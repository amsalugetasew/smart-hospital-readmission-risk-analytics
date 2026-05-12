# Implementation Plan: LLM Medical Advisor

## Overview

Implement the LLM Medical Advisor feature by adding a new FastAPI endpoint backed by a local quantized medical LLM (`llama-cpp-python`), new Pydantic models, a dedicated Streamlit page, and navigation integration — all without disrupting the existing prediction and analytics workflows.

The implementation proceeds in dependency order: dependencies → backend data models → backend inference module → backend wiring → frontend page → frontend navigation → tests → configuration.

## Tasks

- [ ] 1. Add Python dependencies to requirements.txt
  - Add `llama-cpp-python==0.3.9` (CPU-only GGUF inference runtime)
  - Add `pypdf==5.1.0` (PDF text extraction, pure-Python, no system deps)
  - Add `hypothesis==6.131.15` (property-based testing library)
  - Verify no version conflicts with existing pinned packages in `requirements.txt`
  - _Requirements: 3.1, 5.1, 5.5, 9.1_

- [ ] 2. Add LLM Pydantic models to backend/models.py
  - Add `LLMAnalysisRequest` model with `clinical_notes: str` (required, non-empty), `patient_history_text: Optional[str] = None`, `lab_results_text: Optional[str] = None`
  - Add `LLMAnalysisResponse` model with `admit_decision: str`, `admission_recommendation: str`, `recommended_tasks: list[str]`, `inputs_used: list[str]`, `truncation_occurred: bool`, `raw_output: Optional[str] = None`, `error: Optional[str] = None`
  - _Requirements: 4.1, 4.2, 8.1, 8.4, 8.5_

- [ ] 3. Implement backend/llm_advisor.py — core classes and API router
  - [ ] 3.1 Implement `DocumentParser` class
    - Write `_extract_txt(file_bytes: bytes) -> str` using UTF-8 decoding with error replacement
    - Write `_extract_pdf(file_bytes: bytes) -> str` using `pypdf.PdfReader`; raise descriptive error on `PdfReadError` (encrypted/corrupted)
    - Write `_truncate_to_tokens(text: str, max_tokens: int) -> tuple[str, bool]` using whitespace-split word count as token approximation; return `(truncated_text, was_truncated)` flag
    - Write `parse(file_bytes: bytes, filename: str) -> ParseResult` dispatching on `.pdf` / `.txt` extension; enforce `MAX_FILE_BYTES = 10 * 1024 * 1024`; call `_truncate_to_tokens` with `MAX_TOKENS_PER_DOC = 3000`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 3.2 Implement `PromptBuilder` class
    - Define `SYSTEM_INSTRUCTION` constant (clinical decision support role, structured output instruction)
    - Write `build(clinical_notes, patient_history, lab_results, context_window) -> str` that assembles the `[INST] <<SYS>>…<</SYS>>` prompt with labeled sections for each input; substitute `"Not provided."` for absent optional inputs; enforce total token count ≤ `context_window`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 3.3 Implement `ResponseParser` class
    - Define `VALID_ADMIT_DECISIONS = frozenset({"Admit", "Do Not Admit", "Undetermined"})`
    - Define `VALID_RECOMMENDATIONS = frozenset({"Home Treatment", "Outpatient Care", "Inpatient Admission", "Undetermined"})`
    - Write `parse(raw_output: str) -> ParsedResponse` using regex to extract `ADMIT DECISION:`, `ADMISSION LEVEL:`, and numbered list under `RECOMMENDED TASKS:`; fall back to `"Undetermined"` and populate `raw_output` when a field cannot be matched
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 3.4 Implement `LLMAdvisor` class
    - Write `__init__` reading `LLM_MODEL_PATH` from environment; set `model_available = False` initially
    - Write `load_model()` loading the GGUF file via `llama_cpp.Llama(model_path=..., n_gpu_layers=0, n_ctx=4096)`; log model name, file size, and load time on success; catch all exceptions and set `model_available = False` with a warning log
    - Write `analyze(clinical_notes, patient_history_text, lab_results_text) -> AnalysisResult` calling `PromptBuilder.build`, invoking `self.model(prompt, ...)`, and calling `ResponseParser.parse` on the output; wrap inference in `asyncio.wait_for` with 60-second timeout
    - _Requirements: 4.3, 4.4, 4.5, 5.3, 5.4, 5.5, 5.6_

  - [ ] 3.5 Implement the `APIRouter` and `POST /llm-advisor/analyze` endpoint
    - Create `router = APIRouter()` in `backend/llm_advisor.py`
    - Implement `POST /analyze` handler: validate `clinical_notes` is non-empty (raise HTTP 422 if blank); check `llm_advisor.model_available` (raise HTTP 503 if False); call `llm_advisor.analyze(...)`; return `LLMAnalysisResponse`
    - Expose a module-level `llm_advisor = LLMAdvisor()` singleton and a `startup_load_model()` coroutine for use in FastAPI lifespan
    - _Requirements: 4.1, 4.2, 4.4, 4.6_

- [ ] 4. Wire llm_advisor router into backend/main.py
  - Import `router as llm_advisor_router` and `startup_load_model` from `backend.llm_advisor`
  - Add `app.include_router(llm_advisor_router, prefix="/llm-advisor")` after existing router setup
  - Add a FastAPI `lifespan` context manager (or `@app.on_event("startup")`) that calls `startup_load_model()` so the model loads once at process start without blocking existing endpoints
  - Verify `GET /health`, `POST /predict`, and `GET /analytics` still return 200 when `LLM_MODEL_PATH` is unset
  - _Requirements: 4.3, 5.3, 5.4, 9.2, 9.3_

- [ ] 5. Checkpoint — backend unit smoke test
  - Ensure all existing backend tests pass, ask the user if questions arise.

- [ ] 6. Create frontend/llm_advisor_page.py — full Streamlit page
  - [ ] 6.1 Implement `_render_input_form() -> tuple`
    - Render `st.text_area` for Clinical Notes (label, placeholder, height=200, max_chars=5000, key=`llm_advisor_clinical_notes`)
    - Render two `st.file_uploader` widgets for Patient History and Lab Results (accept `["pdf", "txt"]`, key prefixes `llm_advisor_history` / `llm_advisor_lab`)
    - Perform client-side file size validation (> 10 MB → `st.error`) and format validation before returning
    - Return `(notes, hist_bytes, hist_name, lab_bytes, lab_name)`
    - _Requirements: 2.1, 2.2, 2.3, 2.6, 2.7_

  - [ ] 6.2 Implement `_call_analyze_endpoint(api_url, payload) -> Optional[dict]`
    - POST to `{api_url}/llm-advisor/analyze` with JSON payload and 120-second timeout
    - Handle HTTP 422 (validation error), 503 (model unavailable), 504 (timeout), and connection errors with distinct user-facing messages
    - Return parsed JSON dict on success, `None` on any error
    - _Requirements: 4.4, 4.5, 9.5_

  - [ ] 6.3 Implement `_render_results(response: dict) -> None`
    - Display `admit_decision` prominently: green badge for "Do Not Admit", red badge for "Admit", grey for "Undetermined"
    - Display `admission_recommendation` as a labeled option
    - Display `recommended_tasks` as a numbered list
    - Show `inputs_used` and `truncation_occurred` as informational notes
    - Show `raw_output` in a collapsed `st.expander` when present (parse failure fallback)
    - Display the clinical disclaimer (Requirement 7.4)
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 6.4 Implement `render_llm_advisor_page(api_url: str) -> None`
    - Initialize all four `llm_advisor_*` session state keys if absent
    - Call `_render_input_form()` to collect inputs
    - Render "Analyze" submit button; on click: validate non-empty notes (show `st.error` if blank), show `st.spinner("Analyzing clinical data…")`, call `_call_analyze_endpoint`, store response in `st.session_state["llm_advisor_last_response"]`, store file names in session state
    - Render "Clear" button that resets all four `llm_advisor_*` session state keys to `None`/`""` and calls `st.rerun()`
    - If `st.session_state["llm_advisor_last_response"]` is set, call `_render_results`
    - Show retry button on error response
    - _Requirements: 2.4, 2.5, 7.5, 7.6, 10.1, 10.2, 10.3, 10.4_

- [ ] 7. Extend frontend/app.py navigation sidebar to add LLM Medical Advisor
  - Add `"🤖 LLM Medical Advisor"` as a third option in the top-level `option_menu` (and the `st.radio` fallback) alongside `"Prediction"` and `"Model Training"`
  - Add the corresponding `elif main_menu == "🤖 LLM Medical Advisor":` branch that imports and calls `render_llm_advisor_page(API_URL)` from `frontend.llm_advisor_page`
  - Ensure existing `"Prediction"` and `"Model Training"` branches are unchanged
  - Verify the sidebar styles, session state keys, and backend status indicator are unaffected
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 8. Checkpoint — end-to-end manual smoke test
  - Ensure all existing pages still render, the new sidebar entry appears, and the LLM advisor page loads (model unavailable notice expected if `LLM_MODEL_PATH` is unset). Ask the user if questions arise.

- [ ] 9. Write property-based tests using hypothesis
  - [ ] 9.1 Write property test for Property 1: Session State Round-Trip
    - Generate random dicts of `llm_advisor_*` session state values; simulate navigation away and back; assert all keys are restored to original values
    - **Property 1: Session State Round-Trip**
    - **Validates: Requirements 1.3, 10.1, 10.2**

  - [ ]* 9.2 Write property test for Property 2: Clinical Notes Validation Rejects Blank Input
    - Use `hypothesis.strategies.text(alphabet=string.whitespace)` to generate whitespace-only strings; assert endpoint returns HTTP 422 and model is not called
    - **Property 2: Clinical Notes Validation Rejects Blank Input**
    - **Validates: Requirements 2.4, 4.6**

  - [ ]* 9.3 Write property test for Property 3: File Size Validation
    - Generate byte lengths above and below 10,485,760; assert files above limit are rejected before reaching `DocumentParser`
    - **Property 3: File Size Validation**
    - **Validates: Requirements 2.6**

  - [ ]* 9.4 Write property test for Property 4: File Format Validation
    - Generate random file extension strings; assert only `{pdf, txt}` are accepted
    - **Property 4: File Format Validation**
    - **Validates: Requirements 2.7**

  - [ ]* 9.5 Write property test for Property 5: Prompt Completeness
    - Generate random combinations of non-empty clinical notes and optional history/lab texts; assert `PromptBuilder.build()` output contains system instruction, all labeled sections, structured output format, and fits within context window
    - **Property 5: Prompt Completeness**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

  - [ ]* 9.6 Write property test for Property 6: Document Text Round-Trip
    - Generate random printable UTF-8 strings; assert `_extract_txt(encode_utf8(text))` → format → `_extract_txt(encode_utf8(formatted))` produces equivalent content (modulo leading/trailing whitespace)
    - **Property 6: Document Text Round-Trip**
    - **Validates: Requirements 3.2, 3.6**

  - [ ]* 9.7 Write property test for Property 7: Token Truncation Invariant
    - Generate random text strings of varying lengths; assert token count after truncation is ≤ 3000 and `truncated` flag is `True` iff original exceeded 3000 tokens
    - **Property 7: Token Truncation Invariant**
    - **Validates: Requirements 3.4**

  - [ ]* 9.8 Write property test for Property 8: Response Normalization Invariant
    - Generate arbitrary strings as mock LLM output; assert `ResponseParser.parse()` always returns `admit_decision` ∈ `{"Admit", "Do Not Admit", "Undetermined"}` and `admission_recommendation` ∈ `{"Home Treatment", "Outpatient Care", "Inpatient Admission", "Undetermined"}`
    - **Property 8: Response Normalization Invariant**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5**

  - [ ]* 9.9 Write property test for Property 9: Response Parsing Round-Trip
    - Generate valid structured LLM output strings (all three sections present in expected format); assert `parse → format_as_text → parse` produces equivalent result to first parse
    - **Property 9: Response Parsing Round-Trip**
    - **Validates: Requirements 8.6**

  - [ ]* 9.10 Write property test for Property 10: Structured Response Always Contains Required Fields
    - Generate valid `LLMAnalysisRequest` dicts with non-empty clinical notes; mock LLM to return arbitrary strings; assert response always contains `admit_decision`, `admission_recommendation`, and `recommended_tasks`
    - **Property 10: Structured Response Always Contains Required Fields**
    - **Validates: Requirements 4.2**

  - [ ]* 9.11 Write property test for Property 11: Graceful Degradation Preserves Existing Endpoints
    - Simulate absent model (`LLM_MODEL_PATH` unset); assert `GET /health` (with predictor loaded), `POST /predict`, and `GET /analytics` all return HTTP 200
    - **Property 11: Graceful Degradation Preserves Existing Endpoints**
    - **Validates: Requirements 9.3**

  - [ ]* 9.12 Write property test for Property 12: Clear Resets All Session State
    - Generate random non-empty values for all four `llm_advisor_*` session state keys; simulate Clear button activation; assert all four keys are reset to initial empty/None values
    - **Property 12: Clear Resets All Session State**
    - **Validates: Requirements 10.3, 10.4**

- [ ] 10. Write integration tests for /llm-advisor/analyze endpoint
  - [ ] 10.1 Write integration test: valid request returns 200 with correct schema
    - Mock `LLMAdvisor.analyze` to return a fixed `AnalysisResult`; POST valid payload; assert HTTP 200 and response body matches `LLMAnalysisResponse` schema with all required fields present
    - _Requirements: 4.1, 4.2_

  - [ ]* 10.2 Write integration test: blank clinical_notes returns 422
    - POST `{"clinical_notes": "   "}` and `{"clinical_notes": ""}` to `/llm-advisor/analyze`; assert HTTP 422 in both cases
    - _Requirements: 4.6_

  - [ ]* 10.3 Write integration test: model unavailable returns 503
    - Set `llm_advisor.model_available = False`; POST valid payload; assert HTTP 503 with descriptive detail message
    - _Requirements: 4.4, 5.4_

  - [ ]* 10.4 Write integration test: existing endpoints unaffected when model absent
    - With `LLM_MODEL_PATH` unset, assert `GET /health` (predictor loaded), `POST /predict`, and `GET /analytics` all return HTTP 200
    - _Requirements: 9.3_

- [ ] 11. Checkpoint — all tests pass
  - Ensure all property-based tests and integration tests pass. Ask the user if questions arise.

- [ ] 12. Update README with LLM model setup instructions
  - Add a new "LLM Medical Advisor Setup" section documenting:
    - `LLM_MODEL_PATH` environment variable (path to GGUF model file)
    - Model download instructions for BioMistral-7B-GGUF Q4_K_M (~4.4 GB) from HuggingFace
    - Minimum RAM requirement (8 GB; Railway Hobby plan or equivalent)
    - CPU-only inference note (no GPU required)
  - _Requirements: 9.4_

- [ ] 13. Update .env and railway.json with LLM_MODEL_PATH configuration
  - Add `LLM_MODEL_PATH=` (empty placeholder) to `.env` with a comment explaining the expected value
  - Add `LLM_MODEL_PATH` to `railway.json` environment variables section (empty string default) so Railway surfaces it as a configurable variable
  - _Requirements: 5.3, 9.1, 9.2_

- [ ] 14. Final checkpoint — full integration verified
  - Ensure all tests pass, the sidebar entry renders, and the model-unavailable notice displays correctly when `LLM_MODEL_PATH` is unset. Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at each major integration boundary
- Property tests validate universal correctness properties across the full input space
- Unit/integration tests validate specific examples and error conditions
- The LLM model file (~4.4 GB) is never committed to the repository; it is loaded at runtime from `LLM_MODEL_PATH`
