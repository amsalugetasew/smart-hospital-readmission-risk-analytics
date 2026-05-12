# Requirements Document

## Introduction

This feature adds an LLM-powered Medical Advisor to the existing Smart Hospital Readmission Risk Analytics platform. The advisor is accessible via a dedicated icon/link in the existing Streamlit navigation sidebar and opens as a new page within the app — it does not replace any existing functionality.

The Medical Advisor accepts three inputs: free-text clinical notes, an uploaded patient history document, and an uploaded lab results document. A quantized, medically-focused LLM processes these inputs and generates a structured clinical recommendation covering admission decision, admission level, and suggested follow-up tasks. All processing runs locally (no external API calls) using a small quantized model suitable for deployment on Railway.

---

## Glossary

- **LLM_Advisor**: The LLM-based medical advisor component, including its FastAPI endpoint and Streamlit page.
- **Quantized_Model**: A compressed, reduced-precision language model optimized for CPU inference (e.g., GGUF format via llama-cpp-python or a HuggingFace model with 4-bit quantization).
- **Clinical_Notes**: Free-text input provided by a clinician describing the patient's current condition, symptoms, and observations.
- **Patient_History**: A structured or semi-structured document (PDF or plain text) uploaded by the user containing the patient's medical history.
- **Lab_Results**: A structured or semi-structured document (PDF or plain text) uploaded by the user containing laboratory test results.
- **Admission_Recommendation**: The LLM_Advisor's output classifying the patient into one of three admission levels: home treatment, outpatient, or inpatient.
- **Recommended_Tasks**: A list of follow-up actions suggested by the LLM_Advisor (e.g., schedule specialist visit, repeat lab test, prescribe medication review).
- **Admit_Decision**: A binary recommendation (Admit / Do Not Admit) produced by the LLM_Advisor.
- **Streamlit_App**: The existing frontend application located at `frontend/app.py`.
- **FastAPI_Backend**: The existing backend application located at `backend/main.py`.
- **Navigation_Sidebar**: The existing Streamlit sidebar containing the two-level navigation menu.

---

## Requirements

### Requirement 1: Navigation Entry Point

**User Story:** As a clinician, I want to see an LLM Medical Advisor icon/link in the existing navigation sidebar, so that I can access the advisor without disrupting my current workflow.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display an "🤖 LLM Medical Advisor" navigation entry in the Navigation_Sidebar alongside the existing "Prediction" and "Model Training" main menu items.
2. WHEN the user selects "🤖 LLM Medical Advisor" from the Navigation_Sidebar, THE Streamlit_App SHALL render the LLM Medical Advisor page as the main content area.
3. WHEN the user navigates away from the LLM Medical Advisor page, THE Streamlit_App SHALL restore the previously selected page without data loss to the existing prediction or training workflows.
4. THE Streamlit_App SHALL preserve all existing navigation items, styles, and session state when the LLM Medical Advisor entry is added.

---

### Requirement 2: Clinical Input Collection

**User Story:** As a clinician, I want to provide doctor's notes, patient history, and lab results as inputs, so that the LLM can analyze the full clinical picture.

#### Acceptance Criteria

1. THE LLM_Advisor page SHALL provide a multi-line text area for entering Clinical_Notes with a minimum capacity of 5,000 characters.
2. THE LLM_Advisor page SHALL provide a file upload widget that accepts Patient_History documents in PDF and plain-text (.txt) formats.
3. THE LLM_Advisor page SHALL provide a file upload widget that accepts Lab_Results documents in PDF and plain-text (.txt) formats.
4. IF a user submits the form without providing Clinical_Notes, THEN THE LLM_Advisor page SHALL display a validation error message and SHALL NOT invoke the LLM_Advisor backend endpoint.
5. WHERE Patient_History or Lab_Results files are not uploaded, THE LLM_Advisor SHALL proceed with only the available inputs and SHALL indicate in the output which inputs were used.
6. WHEN an uploaded file exceeds 10 MB, THE LLM_Advisor page SHALL display an error message stating the file size limit and SHALL NOT process the file.
7. WHEN an uploaded file is not in an accepted format, THE LLM_Advisor page SHALL display an error message listing the accepted formats and SHALL NOT process the file.

---

### Requirement 3: Document Parsing

**User Story:** As a developer, I want the system to extract text from uploaded documents, so that the LLM can process their content.

#### Acceptance Criteria

1. WHEN a PDF file is uploaded as Patient_History or Lab_Results, THE LLM_Advisor SHALL extract all readable text from the PDF using a PDF parsing library.
2. WHEN a plain-text file is uploaded as Patient_History or Lab_Results, THE LLM_Advisor SHALL read the file content as UTF-8 encoded text.
3. IF a PDF file is encrypted or unreadable, THEN THE LLM_Advisor SHALL return a descriptive error message identifying the file and the reason for failure.
4. THE LLM_Advisor SHALL truncate extracted document text to 3,000 tokens per document before passing it to the Quantized_Model, and SHALL indicate in the output when truncation has occurred.
5. THE Document_Parser SHALL format extracted text from Patient_History and Lab_Results back into a plain-text representation suitable for inclusion in a prompt.
6. FOR ALL valid plain-text documents, parsing then formatting then parsing SHALL produce text content equivalent to the original (round-trip property).

---

### Requirement 4: LLM Inference Endpoint

**User Story:** As a developer, I want a dedicated FastAPI endpoint that runs LLM inference, so that the frontend can request recommendations without blocking the UI.

#### Acceptance Criteria

1. THE FastAPI_Backend SHALL expose a POST endpoint at `/llm-advisor/analyze` that accepts Clinical_Notes, optional Patient_History text, and optional Lab_Results text as request body fields.
2. WHEN a valid request is received at `/llm-advisor/analyze`, THE FastAPI_Backend SHALL invoke the Quantized_Model and return a structured JSON response containing Admit_Decision, Admission_Recommendation, and Recommended_Tasks.
3. THE FastAPI_Backend SHALL load the Quantized_Model once at startup and SHALL reuse the loaded instance for all subsequent inference requests.
4. WHEN the Quantized_Model is not loaded or fails to initialize, THE FastAPI_Backend SHALL return an HTTP 503 response with a descriptive error message.
5. IF the inference request exceeds 60 seconds, THEN THE FastAPI_Backend SHALL return an HTTP 504 response with a timeout error message.
6. THE FastAPI_Backend SHALL validate that the Clinical_Notes field is non-empty and SHALL return an HTTP 422 response if it is missing or blank.

---

### Requirement 5: LLM Model Selection and Loading

**User Story:** As a developer, I want to use a small quantized medical LLM, so that the advisor runs efficiently on Railway's CPU-based deployment without requiring a GPU.

#### Acceptance Criteria

1. THE LLM_Advisor SHALL use a quantized language model with a parameter count no greater than 7 billion parameters in GGUF or 4-bit quantized HuggingFace format.
2. THE LLM_Advisor SHALL use a model that has been fine-tuned or instruction-tuned on medical or clinical text (e.g., MedAlpaca, BioMistral, or equivalent).
3. THE LLM_Advisor SHALL load the Quantized_Model from a local file path configured via an environment variable `LLM_MODEL_PATH`.
4. IF the file at `LLM_MODEL_PATH` does not exist at startup, THEN THE FastAPI_Backend SHALL log a warning and SHALL continue to start, returning HTTP 503 for any inference requests until the model is available.
5. THE Quantized_Model SHALL run inference using CPU-only execution to ensure compatibility with Railway's deployment environment.
6. WHEN the Quantized_Model is loaded successfully, THE FastAPI_Backend SHALL log the model name, file size, and load time.

---

### Requirement 6: Prompt Construction

**User Story:** As a developer, I want the system to construct a structured clinical prompt, so that the LLM produces consistent and clinically relevant output.

#### Acceptance Criteria

1. THE LLM_Advisor SHALL construct a prompt that includes a system instruction defining the LLM's role as a clinical decision support assistant.
2. THE LLM_Advisor SHALL include Clinical_Notes, available Patient_History text, and available Lab_Results text as clearly labeled sections within the prompt.
3. THE LLM_Advisor SHALL instruct the Quantized_Model to respond in a structured format containing exactly three sections: Admit Decision, Admission Level, and Recommended Tasks.
4. THE LLM_Advisor SHALL limit the total prompt length to the context window of the selected Quantized_Model (minimum 2,048 tokens supported).
5. WHEN Patient_History or Lab_Results text is not available, THE LLM_Advisor SHALL include a placeholder note in the corresponding prompt section stating the input was not provided.

---

### Requirement 7: Recommendation Output Display

**User Story:** As a clinician, I want to see a clear, structured recommendation from the LLM, so that I can make an informed admission decision quickly.

#### Acceptance Criteria

1. WHEN the LLM_Advisor returns a successful response, THE Streamlit_App SHALL display the Admit_Decision prominently using a color-coded indicator: green for "Do Not Admit" and red for "Admit".
2. THE Streamlit_App SHALL display the Admission_Recommendation as one of three labeled options: "Home Treatment", "Outpatient Care", or "Inpatient Admission".
3. THE Streamlit_App SHALL display the Recommended_Tasks as a numbered list with each task on a separate line.
4. THE Streamlit_App SHALL display a disclaimer stating that the LLM output is for clinical decision support only and does not replace professional medical judgment.
5. WHEN the LLM_Advisor returns an error response, THE Streamlit_App SHALL display a user-friendly error message and SHALL provide a "Retry" button.
6. WHILE the LLM_Advisor is processing a request, THE Streamlit_App SHALL display a loading spinner with the message "Analyzing clinical data…".

---

### Requirement 8: Response Parsing and Validation

**User Story:** As a developer, I want the system to reliably parse the LLM's text output into structured fields, so that the frontend always receives a consistent data structure.

#### Acceptance Criteria

1. THE LLM_Advisor SHALL parse the Quantized_Model's text output to extract Admit_Decision, Admission_Recommendation, and Recommended_Tasks into separate fields.
2. IF the Quantized_Model output does not contain a recognizable Admit_Decision, THEN THE LLM_Advisor SHALL set Admit_Decision to "Undetermined" and SHALL include the raw model output in the response for review.
3. IF the Quantized_Model output does not contain a recognizable Admission_Recommendation, THEN THE LLM_Advisor SHALL set Admission_Recommendation to "Undetermined" and SHALL include the raw model output in the response for review.
4. THE Response_Parser SHALL normalize Admit_Decision values to one of: "Admit", "Do Not Admit", or "Undetermined".
5. THE Response_Parser SHALL normalize Admission_Recommendation values to one of: "Home Treatment", "Outpatient Care", "Inpatient Admission", or "Undetermined".
6. FOR ALL valid structured LLM outputs, parsing then formatting then parsing SHALL produce an equivalent structured result (round-trip property).

---

### Requirement 9: Deployment Compatibility

**User Story:** As a developer, I want the LLM advisor to deploy on Railway without breaking the existing deployment, so that both the existing app and the new feature are available in production.

#### Acceptance Criteria

1. THE LLM_Advisor SHALL not introduce any Python dependency that conflicts with the versions specified in `requirements.txt`.
2. THE FastAPI_Backend SHALL expose the `/llm-advisor/analyze` endpoint on the same port and process as the existing FastAPI application, requiring no additional Railway service.
3. WHEN `LLM_MODEL_PATH` is not set or the model file is absent, THE FastAPI_Backend SHALL start successfully and the existing `/predict` and `/analytics` endpoints SHALL remain fully operational.
4. THE LLM_Advisor SHALL document the minimum RAM requirement for loading the Quantized_Model in the project README.
5. WHERE the Railway deployment plan does not provide sufficient RAM for the Quantized_Model, THE LLM_Advisor page SHALL display a configuration notice instructing the operator to set `LLM_MODEL_PATH` and upgrade the deployment plan.

---

### Requirement 10: Session and State Management

**User Story:** As a clinician, I want my inputs to persist within a session so that I can review and resubmit without re-entering data.

#### Acceptance Criteria

1. THE Streamlit_App SHALL store Clinical_Notes, the names of uploaded files, and the last LLM response in Streamlit session state for the duration of the browser session.
2. WHEN the user navigates away from the LLM Medical Advisor page and returns within the same session, THE Streamlit_App SHALL restore the previously entered Clinical_Notes and display the last LLM response if available.
3. THE Streamlit_App SHALL provide a "Clear" button that resets Clinical_Notes, uploaded file references, and the displayed LLM response from session state.
4. WHEN the "Clear" button is activated, THE Streamlit_App SHALL reset all LLM_Advisor session state fields and SHALL re-render the input form in its initial empty state.
