# Tab Structure Diagram

## Complete Navigation Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  SMART HOSPITAL READMISSION ANALYTICS                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  SIDEBAR NAVIGATION                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃  🎯  Prediction  [DEFAULT]                                     ┃  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│       │                                                                 │
│       ├─► 💓 Readmission Prediction [DEFAULT SUB-PAGE]                 │
│       │                                                                 │
│       └─► 📈 Analytics Dashboard                                       │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  🔬  Model Training                                          │      │
│  └──────────────────────────────────────────────────────────────┘      │
│       │                                                                 │
│       ├─► 📁 Dataset Upload                                            │
│       ├─► 🔍 Exploratory Analysis                                      │
│       ├─► ⚙️ Preprocessing                                             │
│       ├─► 🧠 Model Training                                            │
│       └─► 📊 Model Performance                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  MAIN CONTENT AREA - Readmission Prediction Page                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🔮 Readmission Prediction                                              │
│  Predict hospital readmission risk for individual patients or batch    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  TABS (Horizontal Navigation)                                 │     │
│  ├───────────────────────────────────────────────────────────────┤     │
│  │                                                               │     │
│  │  ┏━━━━━━━━━━━━━━━━━━━━━┓  ┌──────────────────┐  ┌─────────┐ │     │
│  │  ┃ 🤖 LLM Medical      ┃  │ 📝 Single Patient│  │ 📊 Batch│ │     │
│  │  ┃    Advisor          ┃  │    Prediction    │  │ Predict │ │     │
│  │  ┗━━━━━━━━━━━━━━━━━━━━━┛  └──────────────────┘  └─────────┘ │     │
│  │   ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔                                     │     │
│  │   [FIRST TAB - Active by default] ⭐                          │     │
│  │                                                               │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │  TAB CONTENT AREA                                             │     │
│  ├───────────────────────────────────────────────────────────────┤     │
│  │                                                               │     │
│  │  Content of the active tab is displayed here:                │     │
│  │                                                               │     │
│  │  • Tab 1: LLM Medical Advisor interface                      │     │
│  │  • Tab 2: Single patient prediction form                     │     │
│  │  • Tab 3: Batch file upload and processing                   │     │
│  │                                                               │     │
│  └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tab Details

### Tab 1: 🤖 LLM Medical Advisor (FIRST - DEFAULT)

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 LLM Medical Advisor                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📝 Clinical Notes                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Enter doctor's notes / clinical observations...     │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📋 Patient History        🧪 Lab Results                   │
│  ┌──────────────────┐     ┌──────────────────┐            │
│  │ Upload PDF/TXT   │     │ Upload PDF/TXT   │            │
│  └──────────────────┘     └──────────────────┘            │
│                                                             │
│  [🔍 Analyze & Get Recommendation]  [🗑️ Clear]            │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  📊 Clinical Recommendation                                 │
│  • Admit Decision                                           │
│  • Admission Level                                          │
│  • Key Clinical Factors                                     │
│  • Risk Indicators                                          │
│  • Clinical Rationale                                       │
│  • Recommended Tasks                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tab 2: 📝 Single Patient Prediction

```
┌─────────────────────────────────────────────────────────────┐
│  📝 Single Patient Prediction                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Enter Patient Details                                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Age: [65]    │  │ Primary Dx   │  │ Treatment    │     │
│  │ Gender: [M]  │  │ [Diabetes]   │  │ [Medical]    │     │
│  │ Region: [N]  │  │ Comorbid: 2  │  │ Meds: 5      │     │
│  │ Season: [F]  │  │ LOS: 5 days  │  │ Follow-up: 3 │     │
│  │ Insurance    │  │ Risk: 0.5    │  │ Prev Read: 1 │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  [🔮 Predict Risk]                                          │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  📊 Prediction Results                                      │
│  • Risk Category: High/Medium/Low                           │
│  • Probability: 0.XX                                        │
│  • Feature Importance (SHAP)                                │
│  • Risk Gauge Visualization                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tab 3: 📊 Batch Prediction

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Batch Prediction (Upload File)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📤 Upload Patient Data File                                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Drag and drop CSV or Excel file here               │   │
│  │  or click to browse                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [📥 Download Sample Template]                              │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│                                                             │
│  📊 Batch Results                                           │
│  • Total Patients Processed                                 │
│  • High Risk Count                                          │
│  • Medium Risk Count                                        │
│  • Low Risk Count                                           │
│  • Detailed Results Table                                   │
│  • Download Results Button                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## User Journey

### First-Time User Flow

```
1. App Launch
   ↓
2. Prediction section opens (default)
   ↓
3. Readmission Prediction page loads (default sub-page)
   ↓
4. Tab 1 (🤖 LLM Medical Advisor) is active by default ⭐
   ↓
5. User sees LLM advisor interface immediately
   ↓
6. User can:
   • Use LLM advisor (current tab)
   • Click Tab 2 for single patient prediction
   • Click Tab 3 for batch prediction
   • Click Analytics Dashboard in sidebar
```

### Switching Between Prediction Methods

```
User is on Readmission Prediction page
    ↓
Tabs are visible at the top:
    ├── [🤖 LLM Medical Advisor] ← Click to use AI advisor
    ├── [📝 Single Patient Prediction] ← Click for single prediction
    └── [📊 Batch Prediction] ← Click for batch processing
    ↓
Content changes instantly (no page reload)
    ↓
User can switch between tabs freely
```

---

## Navigation Levels

```
Level 1: Top-Level Navigation (Sidebar)
├── 🎯 Prediction
└── 🔬 Model Training

Level 2: Sub-Pages (Sidebar under Prediction)
├── 💓 Readmission Prediction ← Opens page with tabs
└── 📈 Analytics Dashboard

Level 3: Tabs (Inside Readmission Prediction page)
├── 🤖 LLM Medical Advisor (Tab 1 - First)
├── 📝 Single Patient Prediction (Tab 2)
└── 📊 Batch Prediction (Tab 3)
```

---

## Interaction Model

### Sidebar Navigation
- Click "🎯 Prediction" → Shows 2 sub-pages
- Click "💓 Readmission Prediction" → Loads page with 3 tabs
- Click "📈 Analytics Dashboard" → Loads analytics page

### Tab Navigation (Inside Readmission Prediction)
- Tabs are always visible at the top
- Click any tab → Content changes instantly
- No page reload, seamless switching
- Tab state persists during session

---

## Benefits of Tab Structure

### 1. **All Prediction Methods in One Place**
```
Before: Navigate between 3 separate pages
After: Switch between 3 tabs on one page ⭐
```

### 2. **Faster Access**
```
Before: Click sidebar → Wait for page load
After: Click tab → Instant content switch ⭐
```

### 3. **Better Context**
```
Before: Lose context when switching pages
After: Stay on same page, maintain context ⭐
```

### 4. **Cleaner Sidebar**
```
Before: 3 sub-pages under Prediction
After: 2 sub-pages under Prediction ⭐
```

---

## Technical Implementation

### Tab Creation
```python
# Define 3 tabs
tab1, tab2, tab3 = st.tabs([
    "🤖 LLM Medical Advisor",      # First tab (default)
    "📝 Single Patient Prediction", # Second tab
    "📊 Batch Prediction (Upload File)" # Third tab
])
```

### Tab Content
```python
# Tab 1: LLM Medical Advisor
with tab1:
    render_llm_advisor_page(API_URL)

# Tab 2: Single Patient Prediction
with tab2:
    # Form and prediction logic
    st.form("prediction_form")
    # ... form fields ...

# Tab 3: Batch Prediction
with tab3:
    # File upload and batch processing
    st.file_uploader("Upload CSV/Excel")
    # ... batch processing logic ...
```

---

## Color Coding

```
🎯 Prediction Section (Green Theme)
   ├── 💓 Readmission Prediction (Green)
   │    ├── Tab 1: 🤖 LLM Medical Advisor (Green)
   │    ├── Tab 2: 📝 Single Patient (Green)
   │    └── Tab 3: 📊 Batch Prediction (Green)
   └── 📈 Analytics Dashboard (Green)

🔬 Model Training Section (Blue Theme)
   ├── 📁 Dataset Upload (Blue)
   ├── 🔍 EDA (Blue)
   ├── ⚙️ Preprocessing (Blue)
   ├── 🧠 Training (Blue)
   └── 📊 Performance (Blue)
```

---

**Legend:**
- ⭐ = New/Changed
- [DEFAULT] = Default selection
- [FIRST] = First position
- ← = Navigation action
- ↓ = Flow direction
