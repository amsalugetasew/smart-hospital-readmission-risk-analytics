"""
LLM Medical Advisor — backend module.

Supports two inference modes (auto-detected from environment variables):

  1. API mode (default, recommended):
     - Groq          : set LLM_PROVIDER=groq   + GROQ_API_KEY
     - OpenRouter    : set LLM_PROVIDER=openrouter + OPENROUTER_API_KEY
     - HuggingFace   : set LLM_PROVIDER=huggingface + HF_API_KEY
     - Google Gemini : set LLM_PROVIDER=gemini  + GEMINI_API_KEY
     No model download required. Runs on provider GPU.

  2. Local mode (optional, CPU-only):
     - Set LLM_MODEL_PATH to a local GGUF file.
     - Requires llama-cpp-python installed.

Priority: if any API key is set, API mode is used.
          if LLM_MODEL_PATH is set and no API key, local mode is used.
"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import List, Optional

# Load .env so keys are available when load_model() is called
try:
    from dotenv import load_dotenv as _load_dotenv
    import os as _os
    # Load from project root (parent of backend directory)
    _project_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    _env_path = _os.path.join(_project_root, '.env')
    _load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass

from fastapi import APIRouter, HTTPException
from backend.models import LLMAnalysisRequest, LLMAnalysisResponse

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

MAX_FILE_BYTES     = 10 * 1024 * 1024   # 10 MB
MAX_TOKENS_PER_DOC = 3_000
INFERENCE_TIMEOUT  = 60                 # seconds

# Default models per provider (all free-tier capable)
DEFAULT_MODELS = {
    "groq":         "llama-3.3-70b-versatile",
    "openrouter":   "mistralai/mistral-7b-instruct",
    "huggingface":  "mistralai/Mistral-7B-Instruct-v0.3",
    "gemini":       "gemini-1.5-flash",
}

SYSTEM_INSTRUCTION = (
    "You are a clinical decision support assistant. "
    "Analyse the provided patient information and give a structured admission recommendation. "
    "Respond ONLY in the exact format specified below. "
    "Do not add any text outside the format. "
    "This output is for clinical decision support only and does not replace professional medical judgment."
)

PROMPT_TEMPLATE = """\
## Clinical Notes
{clinical_notes}

## Patient History
{patient_history}

## Lab Results
{lab_results}

Based on the above clinical information, provide your recommendation in EXACTLY this format (no extra text):

ADMIT DECISION: [Admit | Do Not Admit]
ADMISSION LEVEL: [Home Treatment | Outpatient Care | Inpatient Admission]
KEY FACTORS:
- [most important clinical feature driving the decision]
- [second key factor]
- [third key factor]
RISK INDICATORS:
- [specific abnormal finding or risk signal, e.g. Troponin I elevated at 2.4 ng/mL]
- [another risk signal]
CLINICAL RATIONALE: [2-3 sentences explaining why this admission decision was made based on the clinical evidence]
RECOMMENDED TASKS:
1. [task]
2. [task]
3. [task]"""


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ParseResult:
    text: str
    truncated: bool = False
    error: Optional[str] = None


@dataclass
class ParsedResponse:
    admit_decision: str
    admission_recommendation: str
    recommended_tasks: List[str] = field(default_factory=list)
    key_factors: List[str] = field(default_factory=list)
    risk_indicators: List[str] = field(default_factory=list)
    clinical_rationale: str = ""
    raw_output: Optional[str] = None


# ── DocumentParser ────────────────────────────────────────────────────────────

class DocumentParser:
    """Extract and truncate text from uploaded file bytes."""

    @staticmethod
    def _extract_txt(file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="replace")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except ImportError:
            logger.warning("pypdf not installed; falling back to raw UTF-8 decode for PDF.")
            return file_bytes.decode("utf-8", errors="replace")
        except Exception as exc:
            raise ValueError(f"PDF parse error: {exc}") from exc

    @staticmethod
    def _truncate_to_tokens(text: str, max_tokens: int) -> tuple[str, bool]:
        words = text.split()
        if len(words) <= max_tokens:
            return text, False
        return " ".join(words[:max_tokens]), True

    @classmethod
    def parse(cls, file_bytes: bytes, filename: str) -> ParseResult:
        if len(file_bytes) > MAX_FILE_BYTES:
            return ParseResult(
                text="",
                error=f"File '{filename}' exceeds the 10 MB size limit.",
            )
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        try:
            raw = cls._extract_pdf(file_bytes) if ext == "pdf" else cls._extract_txt(file_bytes)
        except ValueError as exc:
            return ParseResult(text="", error=str(exc))
        text, truncated = cls._truncate_to_tokens(raw, MAX_TOKENS_PER_DOC)
        return ParseResult(text=text, truncated=truncated)


# ── PromptBuilder ─────────────────────────────────────────────────────────────

class PromptBuilder:
    @staticmethod
    def build(
        clinical_notes: str,
        patient_history: Optional[str],
        lab_results: Optional[str],
        context_window: int = 4096,
    ) -> str:
        user_content = PROMPT_TEMPLATE.format(
            clinical_notes=clinical_notes.strip(),
            patient_history=patient_history.strip() if patient_history else "Not provided.",
            lab_results=lab_results.strip() if lab_results else "Not provided.",
        )
        words = user_content.split()
        if len(words) > context_window:
            user_content = " ".join(words[:context_window])
        return user_content


# ── ResponseParser ────────────────────────────────────────────────────────────

class ResponseParser:
    _ADMIT_RE      = re.compile(r"ADMIT\s+DECISION\s*:\s*(Admit|Do\s+Not\s+Admit)", re.IGNORECASE)
    _LEVEL_RE      = re.compile(
        r"ADMISSION\s+LEVEL\s*:\s*(Home\s+Treatment|Outpatient\s+Care|Inpatient\s+Admission)",
        re.IGNORECASE,
    )
    _FACTORS_RE    = re.compile(r"KEY\s+FACTORS\s*:\s*\n((?:\s*[-•*]\s*.+\n?)+)", re.IGNORECASE)
    _RISKS_RE      = re.compile(r"RISK\s+INDICATORS\s*:\s*\n((?:\s*[-•*]\s*.+\n?)+)", re.IGNORECASE)
    _RATIONALE_RE  = re.compile(r"CLINICAL\s+RATIONALE\s*:\s*(.+?)(?=\nRECOMMENDED|\nADMIT|\Z)", re.IGNORECASE | re.DOTALL)
    _TASKS_RE      = re.compile(r"RECOMMENDED\s+TASKS\s*:\s*\n((?:\d+\..+\n?)+)", re.IGNORECASE)
    _TASK_LINE_RE  = re.compile(r"^\d+\.\s*(.+)$", re.MULTILINE)
    _BULLET_LINE_RE = re.compile(r"^\s*[-•*]\s*(.+)$", re.MULTILINE)

    @classmethod
    def parse(cls, raw_output: str) -> ParsedResponse:
        needs_raw = False

        # Admit decision
        m = cls._ADMIT_RE.search(raw_output)
        if m:
            admit = "Do Not Admit" if "not" in m.group(1).lower() else "Admit"
        else:
            admit = "Undetermined"
            needs_raw = True

        # Admission level
        m = cls._LEVEL_RE.search(raw_output)
        if m:
            lv = m.group(1).lower()
            if "home" in lv:
                level = "Home Treatment"
            elif "outpatient" in lv:
                level = "Outpatient Care"
            elif "inpatient" in lv:
                level = "Inpatient Admission"
            else:
                level = "Undetermined"
                needs_raw = True
        else:
            level = "Undetermined"
            needs_raw = True

        # Key factors
        key_factors: List[str] = []
        m = cls._FACTORS_RE.search(raw_output)
        if m:
            key_factors = cls._BULLET_LINE_RE.findall(m.group(1))

        # Risk indicators
        risk_indicators: List[str] = []
        m = cls._RISKS_RE.search(raw_output)
        if m:
            risk_indicators = cls._BULLET_LINE_RE.findall(m.group(1))

        # Clinical rationale
        clinical_rationale = ""
        m = cls._RATIONALE_RE.search(raw_output)
        if m:
            clinical_rationale = m.group(1).strip()

        # Recommended tasks
        tasks: List[str] = []
        m = cls._TASKS_RE.search(raw_output)
        if m:
            tasks = cls._TASK_LINE_RE.findall(m.group(1))
        else:
            tasks = cls._TASK_LINE_RE.findall(raw_output)

        return ParsedResponse(
            admit_decision=admit,
            admission_recommendation=level,
            recommended_tasks=tasks,
            key_factors=key_factors,
            risk_indicators=risk_indicators,
            clinical_rationale=clinical_rationale,
            raw_output=raw_output if needs_raw else None,
        )


# ── API-based inference helpers ───────────────────────────────────────────────

def _openai_chat(base_url: str, api_key: str, model: str, system: str, user: str,
                 extra_headers: Optional[dict] = None) -> str:
    """Generic OpenAI-compatible chat completion using the openai SDK."""
    from openai import OpenAI  # type: ignore
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=extra_headers or {},
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        max_tokens=512,
        temperature=0.1,
    )
    return response.choices[0].message.content


def _call_groq(api_key: str, model: str, system: str, user: str) -> str:
    """Call Groq API using openai SDK with Groq base URL."""
    return _openai_chat(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        model=model,
        system=system,
        user=user,
    )


def _call_openrouter(api_key: str, model: str, system: str, user: str) -> str:
    """Call OpenRouter API using openai SDK."""
    return _openai_chat(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model=model,
        system=system,
        user=user,
        extra_headers={"HTTP-Referer": "https://hospital-readmission-app"},
    )


def _call_huggingface(api_key: str, model: str, system: str, user: str) -> str:
    """Call HuggingFace Inference Providers API using openai SDK.
    Token must have 'Make calls to serverless Inference API' permission.
    Go to https://huggingface.co/settings/tokens to create/update token.
    """
    try:
        return _openai_chat(
            base_url="https://router.huggingface.co/hf-inference/v1",
            api_key=api_key,
            model=model,
            system=system,
            user=user,
        )
    except Exception as exc:
        if "403" in str(exc) or "permission" in str(exc).lower():
            raise ValueError(
                "HuggingFace token lacks inference permissions. "
                "Go to https://huggingface.co/settings/tokens, create a new token "
                "and enable 'Make calls to serverless Inference API' permission."
            ) from exc
        raise


def _call_gemini(api_key: str, model: str, system: str, user: str) -> str:
    """Call Google Gemini API using openai SDK compatibility layer."""
    return _openai_chat(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
        model=model,
        system=system,
        user=user,
    )


# ── LLMAdvisor ────────────────────────────────────────────────────────────────

class LLMAdvisor:
    """
    Orchestrates LLM inference.
    Auto-detects mode from environment:
      - API mode  : any of GROQ_API_KEY / OPENROUTER_API_KEY / HF_API_KEY / GEMINI_API_KEY
      - Local mode: LLM_MODEL_PATH pointing to a GGUF file
    """

    def __init__(self) -> None:
        self.model            = None          # local llama-cpp model
        self.model_available  = False
        self.mode             = "none"        # "groq" | "openrouter" | "huggingface" | "gemini" | "local" | "none"
        self.api_key          = ""
        self.llm_model_name   = ""
        self.model_path       = ""
        self.context_window   = 4096

    def load_model(self) -> None:
        """Detect and initialise the inference backend."""
        
        logger.info("load_model() called - checking environment variables...")

        # Read all keys fresh (dotenv already loaded at module import)
        self.model_path = os.getenv("LLM_MODEL_PATH", "")
        provider = os.getenv("LLM_PROVIDER", "").lower().strip()

        # ── Try each API provider ────────────────────────────────────────────
        groq_key  = os.getenv("GROQ_API_KEY", "")
        or_key    = os.getenv("OPENROUTER_API_KEY", "")
        hf_key    = os.getenv("HF_API_KEY", "")
        gem_key   = os.getenv("GEMINI_API_KEY", "")
        
        logger.info(f"Environment check: GROQ_API_KEY={'found' if groq_key else 'not found'}")
        logger.info(f"Environment check: OPENROUTER_API_KEY={'found' if or_key else 'not found'}")
        logger.info(f"Environment check: HF_API_KEY={'found' if hf_key else 'not found'}")
        logger.info(f"Environment check: GEMINI_API_KEY={'found' if gem_key else 'not found'}")

        # Explicit provider override, or auto-detect from available keys
        # Helper: use env override if non-empty, else fall back to default model
        def _model_name(default: str) -> str:
            return os.getenv("LLM_MODEL_NAME", "").strip() or default

        if provider == "groq" or (not provider and groq_key):
            if groq_key:
                self.mode            = "groq"
                self.api_key         = groq_key
                self.llm_model_name  = _model_name(DEFAULT_MODELS["groq"])
                self.model_available = True
                logger.info("LLM Medical Advisor: using Groq API (model=%s)", self.llm_model_name)
                return

        if provider == "openrouter" or (not provider and or_key):
            if or_key:
                self.mode            = "openrouter"
                self.api_key         = or_key
                self.llm_model_name  = _model_name(DEFAULT_MODELS["openrouter"])
                self.model_available = True
                logger.info("LLM Medical Advisor: using OpenRouter API (model=%s)", self.llm_model_name)
                return

        if provider == "huggingface" or (not provider and hf_key):
            if hf_key:
                self.mode            = "huggingface"
                self.api_key         = hf_key
                self.llm_model_name  = _model_name(DEFAULT_MODELS["huggingface"])
                self.model_available = True
                logger.info("LLM Medical Advisor: using HuggingFace API (model=%s)", self.llm_model_name)
                return

        if provider == "gemini" or (not provider and gem_key):
            if gem_key:
                self.mode            = "gemini"
                self.api_key         = gem_key
                self.llm_model_name  = _model_name(DEFAULT_MODELS["gemini"])
                self.model_available = True
                logger.info("LLM Medical Advisor: using Gemini API (model=%s)", self.llm_model_name)
                return

        # ── Fall back to local GGUF model ────────────────────────────────────
        if self.model_path:
            if not os.path.exists(self.model_path):
                logger.warning("LLM model file not found at '%s'.", self.model_path)
                return
            try:
                from llama_cpp import Llama  # type: ignore
                size_mb = os.path.getsize(self.model_path) / 1_048_576
                logger.info("Loading local GGUF model: %s (%.1f MB)…", self.model_path, size_mb)
                t0 = time.time()
                self.model = Llama(
                    model_path=self.model_path,
                    n_gpu_layers=0,
                    n_ctx=self.context_window,
                    verbose=False,
                )
                self.mode           = "local"
                self.model_available = True
                logger.info("Local model loaded in %.1f s", time.time() - t0)
            except ImportError:
                logger.warning("llama-cpp-python not installed. Cannot use local model.")
            except Exception as exc:
                logger.warning("Failed to load local model: %s", exc)
            return

        logger.warning(
            "No LLM provider configured. Set one of: "
            "GROQ_API_KEY, OPENROUTER_API_KEY, HF_API_KEY, GEMINI_API_KEY, or LLM_MODEL_PATH."
        )

    def _call_api(self, user_prompt: str) -> str:
        """Dispatch to the configured API provider."""
        if self.mode == "groq":
            return _call_groq(self.api_key, self.llm_model_name, SYSTEM_INSTRUCTION, user_prompt)
        if self.mode == "openrouter":
            return _call_openrouter(self.api_key, self.llm_model_name, SYSTEM_INSTRUCTION, user_prompt)
        if self.mode == "huggingface":
            return _call_huggingface(self.api_key, self.llm_model_name, SYSTEM_INSTRUCTION, user_prompt)
        if self.mode == "gemini":
            return _call_gemini(self.api_key, self.llm_model_name, SYSTEM_INSTRUCTION, user_prompt)
        raise RuntimeError(f"Unknown mode: {self.mode}")

    def analyze(
        self,
        clinical_notes: str,
        patient_history_text: Optional[str],
        lab_results_text: Optional[str],
    ) -> LLMAnalysisResponse:
        inputs_used = ["clinical_notes"]
        if patient_history_text:
            inputs_used.append("patient_history")
        if lab_results_text:
            inputs_used.append("lab_results")

        user_prompt = PromptBuilder.build(
            clinical_notes=clinical_notes,
            patient_history=patient_history_text,
            lab_results=lab_results_text,
            context_window=self.context_window,
        )

        try:
            if self.mode == "local":
                output = self.model(
                    f"[INST] <<SYS>>\n{SYSTEM_INSTRUCTION}\n<</SYS>>\n\n{user_prompt} [/INST]",
                    max_tokens=512,
                    temperature=0.1,
                    stop=["[INST]", "</s>"],
                )
                raw_text: str = output["choices"][0]["text"]
            else:
                raw_text = self._call_api(user_prompt)
        except Exception as exc:
            logger.error("LLM inference error: %s", exc)
            return LLMAnalysisResponse(
                admit_decision="Undetermined",
                admission_recommendation="Undetermined",
                recommended_tasks=[],
                key_factors=[],
                risk_indicators=[],
                clinical_rationale="",
                inputs_used=inputs_used,
                truncation_occurred=False,
                error=f"Inference error: {exc}",
            )

        parsed = ResponseParser.parse(raw_text)
        return LLMAnalysisResponse(
            admit_decision=parsed.admit_decision,
            admission_recommendation=parsed.admission_recommendation,
            recommended_tasks=parsed.recommended_tasks,
            key_factors=parsed.key_factors,
            risk_indicators=parsed.risk_indicators,
            clinical_rationale=parsed.clinical_rationale,
            inputs_used=inputs_used,
            truncation_occurred=False,
            raw_output=parsed.raw_output,
        )


# Module-level singleton
llm_advisor = LLMAdvisor()


async def startup_load_model() -> None:
    logger.info("=" * 60)
    logger.info("Starting LLM Medical Advisor initialization...")
    logger.info("=" * 60)
    llm_advisor.load_model()
    logger.info(f"LLM Advisor Status: mode={llm_advisor.mode}, available={llm_advisor.model_available}")
    logger.info("=" * 60)


# ── API Router ────────────────────────────────────────────────────────────────

router = APIRouter(tags=["LLM Medical Advisor"])


@router.get("/status")
def status() -> dict:
    """Return the current LLM provider mode and model name."""
    return {
        "mode":         llm_advisor.mode,
        "model_name":   llm_advisor.llm_model_name,
        "available":    llm_advisor.model_available,
    }


@router.post("/analyze", response_model=LLMAnalysisResponse)
def analyze(request: LLMAnalysisRequest) -> LLMAnalysisResponse:
    if not request.clinical_notes or not request.clinical_notes.strip():
        raise HTTPException(status_code=422, detail="clinical_notes is required and must not be blank.")

    if not llm_advisor.model_available:
        raise HTTPException(
            status_code=503,
            detail=(
                f"LLM advisor not configured (mode={llm_advisor.mode}). "
                "Set one of: GROQ_API_KEY, OPENROUTER_API_KEY, HF_API_KEY, GEMINI_API_KEY, or LLM_MODEL_PATH."
            ),
        )

    return llm_advisor.analyze(
        clinical_notes=request.clinical_notes,
        patient_history_text=request.patient_history_text,
        lab_results_text=request.lab_results_text,
    )
