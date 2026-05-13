"""
AI Medical Advisor Page
Provides clinical decision support using a local quantized medical LLM.
Accepts doctor's notes, patient history (PDF/TXT), and lab results (PDF/TXT).
"""

import streamlit as st
import requests
import json
from typing import Optional

# ── Session state keys ──────────────────────────────────────────────────────
_NOTES_KEY    = "llm_advisor_clinical_notes"
_HIST_NAME    = "llm_advisor_history_filename"
_LAB_NAME     = "llm_advisor_lab_filename"
_LAST_RESP    = "llm_advisor_last_response"

MAX_FILE_BYTES = 10 * 1024 * 1024   # 10 MB
ACCEPTED_TYPES = ["pdf", "txt"]


def _init_session_state() -> None:
    """Initialise all llm_advisor_* session state keys if absent."""
    defaults = {
        _NOTES_KEY: "",
        _HIST_NAME: None,
        _LAB_NAME:  None,
        _LAST_RESP: None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _validate_file(uploaded_file) -> Optional[str]:
    """Return an error string if the file is invalid, else None."""
    if uploaded_file is None:
        return None
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
    if ext not in ACCEPTED_TYPES:
        return f"❌ **{uploaded_file.name}** — unsupported format. Accepted: PDF, TXT."
    if uploaded_file.size > MAX_FILE_BYTES:
        return f"❌ **{uploaded_file.name}** — file exceeds 10 MB limit ({uploaded_file.size / 1_048_576:.1f} MB)."
    return None


def _render_input_form():
    """Render input widgets. Returns (notes, hist_bytes, hist_name, lab_bytes, lab_name)."""
    # st.markdown("#### 📝 Clinical Notes")
    notes = st.text_area(
        "Enter doctor's notes / clinical observations",
        value=st.session_state.get(_NOTES_KEY, ""),
        height=200,
        max_chars=5000,
        placeholder="Describe the patient's current condition, symptoms, vital signs, and clinical observations...",
        key="llm_advisor_notes_input",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Patient History")
        hist_file = st.file_uploader(
            "Upload patient history (PDF or TXT)",
            type=ACCEPTED_TYPES,
            key="llm_advisor_history_uploader",
            help="Maximum 10 MB. Accepted formats: PDF, TXT",
        )
        hist_err = _validate_file(hist_file)
        if hist_err:
            st.error(hist_err)
            hist_file = None

    with col2:
        st.markdown("#### 🧪 Lab Results")
        lab_file = st.file_uploader(
            "Upload lab results (PDF or TXT)",
            type=ACCEPTED_TYPES,
            key="llm_advisor_lab_uploader",
            help="Maximum 10 MB. Accepted formats: PDF, TXT",
        )
        lab_err = _validate_file(lab_file)
        if lab_err:
            st.error(lab_err)
            lab_file = None

    hist_bytes = hist_file.read() if hist_file else None
    hist_name  = hist_file.name  if hist_file else None
    lab_bytes  = lab_file.read() if lab_file else None
    lab_name   = lab_file.name  if lab_file else None

    return notes, hist_bytes, hist_name, lab_bytes, lab_name


def _call_analyze_endpoint(api_url: str, payload: dict) -> Optional[dict]:
    """POST to /llm-advisor/analyze. Returns parsed JSON or None on error."""
    try:
        response = requests.post(
            f"{api_url}/llm-advisor/analyze",
            json=payload,
            timeout=120,
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            st.error("⚠️ Validation error: Clinical notes are required and must not be blank.")
        elif response.status_code == 503:
            st.error("🔧 **LLM advisor not configured.**")
            st.info(
                "**Quick setup — choose one free API provider:**\n\n"
                "| Provider | Speed | Free Tier | Get Key |\n"
                "|---|---|---|---|\n"
                "| **Groq** ⭐ | Fastest | ✅ Free | https://console.groq.com |\n"
                "| **OpenRouter** | Fast | ✅ Free models | https://openrouter.ai/keys |\n"
                "| **HuggingFace** | Medium | ✅ Free | https://huggingface.co/settings/tokens |\n"
                "| **Gemini** | Fast | ✅ Free | https://aistudio.google.com/app/apikey |\n\n"
                "1. Get a free API key from any provider above\n"
                "2. Paste it into your `.env` file (e.g. `GROQ_API_KEY=your_key_here`)\n"
                "3. Restart the backend"
            )
        elif response.status_code == 504:
            st.error("⏱️ **Inference timed out.** The model took too long to respond. Try shortening the input or retry.")
        else:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"❌ Backend error ({response.status_code}): {detail}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot reach the backend. Make sure the backend server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The model may be busy — please retry.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None


def _render_results(response: dict) -> None:
    """Render structured recommendation output with clinical reasoning."""
    admit = response.get("admit_decision", "Undetermined")
    level = response.get("admission_recommendation", "Undetermined")
    tasks = response.get("recommended_tasks", [])
    key_factors = response.get("key_factors", [])
    risk_indicators = response.get("risk_indicators", [])
    clinical_rationale = response.get("clinical_rationale", "")
    inputs_used = response.get("inputs_used", [])
    truncated = response.get("truncation_occurred", False)
    raw_output = response.get("raw_output")
    error_msg  = response.get("error")

    # st.markdown("---")
    # st.markdown("## 📊 Clinical Recommendation")

    # ── Admit Decision ──────────────────────────────────────────────────────
    if admit == "Admit":
        st.markdown(
            '<div style="background:#fee2e2;border-left:6px solid #dc2626;padding:16px 20px;'
            'border-radius:8px;margin-bottom:12px;">'
            '<span style="font-size:1.4rem;font-weight:700;color:#dc2626;">🔴 READMIT</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    elif admit == "Do Not Admit":
        st.markdown(
            '<div style="background:#dcfce7;border-left:6px solid #16a34a;padding:16px 20px;'
            'border-radius:8px;margin-bottom:12px;">'
            '<span style="font-size:1.4rem;font-weight:700;color:#16a34a;">🟢 DO NOT READMIT</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#f3f4f6;border-left:6px solid #6b7280;padding:16px 20px;'
            'border-radius:8px;margin-bottom:12px;">'
            '<span style="font-size:1.4rem;font-weight:700;color:#6b7280;">⚪ UNDETERMINED</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Admission Level ─────────────────────────────────────────────────────
    level_icons = {
        "Home Treatment":      "🏠",
        "Outpatient Care":     "🏢",
        "Inpatient Admission": "🏥",
        "Undetermined":        "❓",
    }
    icon = level_icons.get(level, "❓")
    st.markdown(f"### {icon} Admission Level: **{level}**")

    # st.markdown("---")

    # ── Clinical Reasoning (3 columns) ──────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 Key Clinical Factors")
        if key_factors:
            for factor in key_factors:
                st.markdown(
                    f'<div style="background:#eff6ff;border-left:4px solid #3b82f6;'
                    f'padding:8px 12px;border-radius:6px;margin-bottom:6px;">'
                    f'<span style="color:#1e40af;font-weight:600;">▶</span> {factor}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No key factors extracted.")

    with col2:
        st.markdown("### ⚠️ Risk Indicators")
        if risk_indicators:
            for risk in risk_indicators:
                st.markdown(
                    f'<div style="background:#fff7ed;border-left:4px solid #f97316;'
                    f'padding:8px 12px;border-radius:6px;margin-bottom:6px;">'
                    f'<span style="color:#c2410c;font-weight:600;">⚡</span> {risk}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No risk indicators extracted.")

    # ── Clinical Rationale ──────────────────────────────────────────────────
    if clinical_rationale:
        st.markdown("### 🧠 Clinical Rationale")
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #86efac;border-left:5px solid #16a34a;'
            f'padding:16px 20px;border-radius:8px;font-size:1.0rem;line-height:1.6;color:#14532d;">'
            f'{clinical_rationale}</div>',
            unsafe_allow_html=True,
        )

    # st.markdown("---")

    # ── Recommended Tasks ───────────────────────────────────────────────────
    st.markdown("### 📋 Recommended Tasks")
    if tasks:
        for i, task in enumerate(tasks, 1):
            st.markdown(
                f'<div style="background:#fafafa;border:1px solid #e5e7eb;border-left:4px solid #008080;'
                f'padding:10px 14px;border-radius:6px;margin-bottom:6px;">'
                f'<span style="color:#008080;font-weight:700;">{i}.</span> {task}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No specific tasks were recommended.")

    # ── Metadata ────────────────────────────────────────────────────────────
    if inputs_used or truncated:
        st.markdown("")
        if inputs_used:
            st.caption(f"**Inputs analysed:** {', '.join(inputs_used)}")
        if truncated:
            st.warning("⚠️ One or more documents were truncated to fit the model's context window.")

    # ── Raw output fallback ─────────────────────────────────────────────────
    if raw_output:
        with st.expander("🔍 Raw model output (review required)", expanded=False):
            st.text(raw_output)

    if error_msg:
        st.warning(f"⚠️ Partial error: {error_msg}")

    # ── Disclaimer ──────────────────────────────────────────────────────────
    # st.markdown("---")
    st.info(
        "⚕️ **Clinical Disclaimer:** This output is generated by an AI model for clinical decision "
        "support purposes only. It does **not** replace professional medical judgment. Always consult "
        "a qualified clinician before making admission decisions."
    )


def render_llm_advisor_page(api_url: str) -> None:
    """Main entry point — renders the full AI Medical Advisor page."""
    _init_session_state()

    st.markdown(
        "Provide clinical notes and optionally upload patient history and lab results. "
    )

    # ── Provider status banner ────────────────────────────────────────────────
    import requests as _req
    try:
        status_resp = _req.get(f"{api_url}/llm-advisor/status", timeout=3)
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            mode = status_data.get("mode", "none")
            model_name = status_data.get("model_name", "")
            if mode != "none":
                provider_labels = {
                    "groq": "☁️ Groq API",
                    "openrouter": "☁️ OpenRouter API",
                    "huggingface": "☁️ HuggingFace API",
                    "gemini": "☁️ Google Gemini API",
                    "local": "💻 Local Model",
                }
                label = provider_labels.get(mode, mode)
                # st.success(f"✅ **Provider:** {label} — `{model_name}`")
            else:
                _show_setup_notice()
    except Exception:
        pass  # Status endpoint optional — don't block the page

    # st.markdown("---")

    # ── Input form ───────────────────────────────────────────────────────────
    notes, hist_bytes, hist_name, lab_bytes, lab_name = _render_input_form()

    col_submit, col_clear = st.columns([2, 1])

    with col_submit:
        analyze_clicked = st.button(
            "🔍 Analyze & Get Recommendation",
            type="primary",
            use_container_width=True,
        )

    with col_clear:
        clear_clicked = st.button(
            "🗑️ Clean Result",
            use_container_width=True,
        )

    # ── Clear handler ────────────────────────────────────────────────────────
    if clear_clicked:
        st.session_state[_NOTES_KEY] = ""
        st.session_state[_HIST_NAME] = None
        st.session_state[_LAB_NAME]  = None
        st.session_state[_LAST_RESP] = None
        st.rerun()

    # ── Analyze handler ──────────────────────────────────────────────────────
    if analyze_clicked:
        # Validate clinical notes
        if not notes or not notes.strip():
            st.error("⚠️ Clinical notes are required. Please enter the doctor's observations before analyzing.")
        else:
            # Persist inputs to session state
            st.session_state[_NOTES_KEY] = notes
            st.session_state[_HIST_NAME] = hist_name
            st.session_state[_LAB_NAME]  = lab_name

            # Build payload — parse file bytes to text on the frontend side
            # (backend also accepts raw text; we decode here for simplicity)
            patient_history_text = None
            lab_results_text     = None

            if hist_bytes:
                try:
                    patient_history_text = _extract_text(hist_bytes, hist_name)
                except Exception as e:
                    st.error(f"❌ Could not read patient history file: {e}")

            if lab_bytes:
                try:
                    lab_results_text = _extract_text(lab_bytes, lab_name)
                except Exception as e:
                    st.error(f"❌ Could not read lab results file: {e}")

            payload = {
                "clinical_notes":        notes.strip(),
                "patient_history_text":  patient_history_text,
                "lab_results_text":      lab_results_text,
            }

            with st.spinner("🔬 Analyzing clinical data…"):
                result = _call_analyze_endpoint(api_url, payload)

            if result:
                st.session_state[_LAST_RESP] = result
                st.rerun()
            else:
                # Show retry button
                if st.button("🔄 Retry"):
                    st.rerun()

    # ── Display last response (persists across navigation) ───────────────────
    last = st.session_state.get(_LAST_RESP)
    if last and not analyze_clicked:
        _render_results(last)


def _show_setup_notice() -> None:
    """Show a friendly setup guide when no LLM provider is configured."""
    st.warning("⚙️ **LLM provider not configured yet.** Choose a free API option below to get started.")
    with st.expander("🚀 Quick Setup Guide (2 minutes)", expanded=True):
        st.markdown("""
**Step 1 — Get a free API key from any of these providers:**

| Provider | Why choose it | Get Key |
|---|---|---|
| ⭐ **Groq** | Fastest (LPU hardware), generous free tier | [console.groq.com](https://console.groq.com) |
| **OpenRouter** | Access many models, free tier available | [openrouter.ai/keys](https://openrouter.ai/keys) |
| **HuggingFace** | Open-source models, free inference API | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| **Google Gemini** | Very generous free tier | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |

**Step 2 — Add your key to the `.env` file in the project root:**
```
# For Groq (recommended):
GROQ_API_KEY=your_key_here

# For OpenRouter:
OPENROUTER_API_KEY=your_key_here

# For HuggingFace:
HF_API_KEY=your_key_here

# For Gemini:
GEMINI_API_KEY=your_key_here
```

**Step 3 — Restart the backend.** The advisor will be ready instantly. No model download needed.
        """)


def _extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if filename else "txt"
    if ext == "pdf":
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except ImportError:
            # pypdf not installed — fall back to raw decode attempt
            return file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise ValueError(f"PDF parse error: {e}")
    else:
        return file_bytes.decode("utf-8", errors="replace")
