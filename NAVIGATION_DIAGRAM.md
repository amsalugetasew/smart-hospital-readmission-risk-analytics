# Navigation Structure Diagram

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART HOSPITAL READMISSION                   │
│                     RISK ANALYTICS PLATFORM                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        MAIN NAVIGATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃  🎯  Prediction  [DEFAULT]                             ┃  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
│       │                                                         │
│       ├─► 🤖 LLM Medical Advisor [FIRST] [DEFAULT] ⭐          │
│       │    • AI-powered clinical decision support              │
│       │    • Clinical notes input                              │
│       │    • Patient history upload (PDF/TXT)                  │
│       │    • Lab results upload (PDF/TXT)                      │
│       │    • Admission recommendations                         │
│       │    • Clinical reasoning & risk indicators              │
│       │                                                         │
│       ├─► 💓 Readmission Prediction (Single Row)               │
│       │    • Individual patient risk assessment                │
│       │    • Feature importance analysis                       │
│       │    • SHAP explanations                                 │
│       │                                                         │
│       └─► 📈 Analytics Dashboard (Batch Prediction)            │
│            • Multiple patient analysis                         │
│            • Hospital-wide metrics                             │
│            • Trend visualization                               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  🔬  Model Training                                    │    │
│  └────────────────────────────────────────────────────────┘    │
│       │                                                         │
│       ├─► 📁 Dataset Upload                                    │
│       │    • Upload custom datasets                            │
│       │    • Dataset validation                                │
│       │                                                         │
│       ├─► 🔍 Exploratory Analysis (EDA)                        │
│       │    • Data visualization                                │
│       │    • Statistical analysis                              │
│       │                                                         │
│       ├─► ⚙️ Preprocessing                                     │
│       │    • Missing value handling                            │
│       │    • Feature scaling                                   │
│       │    • Encoding configuration                            │
│       │                                                         │
│       ├─► 🧠 Model Training                                    │
│       │    • Algorithm selection                               │
│       │    • Hyperparameter tuning                             │
│       │    • Model training                                    │
│       │                                                         │
│       └─► 📊 Model Performance                                 │
│            • Metrics evaluation                                │
│            • Confusion matrix                                  │
│            • ROC curves                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Navigation Flow

### User Journey 1: First-Time User (Default Flow)
```
App Launch
    ↓
🎯 Prediction (opens automatically)
    ↓
🤖 LLM Medical Advisor (DEFAULT SUB-PAGE) ⭐
    ↓
Enter clinical notes
    ↓
Upload patient history (optional)
    ↓
Upload lab results (optional)
    ↓
Get AI recommendation
```

### User Journey 2: Single Patient Prediction
```
App Launch
    ↓
🎯 Prediction
    ↓
Click "💓 Readmission Prediction"
    ↓
Enter patient data
    ↓
Get risk prediction + SHAP analysis
```

### User Journey 3: Batch Analysis
```
App Launch
    ↓
🎯 Prediction
    ↓
Click "📈 Analytics Dashboard"
    ↓
View hospital-wide metrics
    ↓
Analyze trends and patterns
```

### User Journey 4: Model Training
```
App Launch
    ↓
Click "🔬 Model Training"
    ↓
📁 Dataset Upload (default sub-page)
    ↓
Follow training pipeline:
  → 🔍 EDA
  → ⚙️ Preprocessing
  → 🧠 Training
  → 📊 Performance
```

---

## Hierarchy Levels

```
Level 1: Main Navigation (Top-level sections)
├── 🎯 Prediction
└── 🔬 Model Training

Level 2: Sub-navigation (Feature pages)
├── Prediction
│   ├── 🤖 LLM Medical Advisor (FIRST)
│   ├── 💓 Readmission Prediction
│   └── 📈 Analytics Dashboard
└── Model Training
    ├── 📁 Dataset Upload
    ├── 🔍 Exploratory Analysis
    ├── ⚙️ Preprocessing
    ├── 🧠 Model Training
    └── 📊 Model Performance
```

---

## Color-Coded Navigation

```
┌─────────────────────────────────────────┐
│  🎯 Prediction                          │  ← Green Gradient
│     (active-green)                      │     #059669 → #047857
│                                         │
│     ├── 🤖 LLM Medical Advisor          │  ← Green (inherits)
│     ├── 💓 Readmission Prediction       │  ← Green (inherits)
│     └── 📈 Analytics Dashboard          │  ← Green (inherits)
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🔬 Model Training                      │  ← Blue Gradient
│     (active)                            │     #0ea5e9 → #0284c7
│                                         │
│     ├── 📁 Dataset Upload               │  ← Blue (inherits)
│     ├── 🔍 Exploratory Analysis         │  ← Blue (inherits)
│     ├── ⚙️ Preprocessing                │  ← Blue (inherits)
│     ├── 🧠 Model Training               │  ← Blue (inherits)
│     └── 📊 Model Performance            │  ← Blue (inherits)
└─────────────────────────────────────────┘
```

---

## State Management

```
Session State Variables:
├── main_menu: "Prediction" (default)
└── sub_page: "LLM Medical Advisor" (default)

Navigation Logic:
├── If main_menu == "Prediction"
│   ├── Show sub-navigation with 3 options
│   └── page = sub_page (LLM Medical Advisor, Readmission Prediction, or Analytics Dashboard)
│
└── If main_menu == "Model Training"
    ├── Show sub-navigation with 5 options
    └── page = sub_page (Dataset Upload, EDA, Preprocessing, Training, or Performance)
```

---

## Comparison: Before vs After

### BEFORE
```
Top-Level Navigation (3 items):
├── Position 1: 🎯 Prediction (DEFAULT)
│   ├── 💓 Readmission Prediction (default sub-page)
│   └── 📈 Analytics Dashboard
├── Position 2: 🔬 Model Training
│   └── (5 sub-pages)
└── Position 3: 🤖 LLM Medical Advisor (SEPARATE, LAST)
```

### AFTER
```
Top-Level Navigation (2 items): ⭐
├── Position 1: 🎯 Prediction (DEFAULT)
│   ├── 🤖 LLM Medical Advisor (FIRST, default sub-page) ⭐
│   ├── 💓 Readmission Prediction
│   └── 📈 Analytics Dashboard
└── Position 2: 🔬 Model Training
    └── (5 sub-pages)
```

---

## Key Features by Section

### 🎯 Prediction Section (3 Sub-pages)

#### 1. 🤖 LLM Medical Advisor (FIRST - DEFAULT)
- **Purpose**: AI-powered clinical decision support
- **Input**: Clinical notes, patient history, lab results
- **Output**: Admission recommendations with clinical reasoning
- **Technology**: Groq/OpenRouter/HuggingFace/Gemini LLM APIs
- **Position**: First sub-page, default when entering Prediction

#### 2. 💓 Readmission Prediction (Single Row)
- **Purpose**: Individual patient readmission risk assessment
- **Input**: Single patient data (14 features)
- **Output**: Risk scores, feature importance, SHAP values
- **Technology**: Random Forest ML model
- **Position**: Second sub-page

#### 3. 📈 Analytics Dashboard (Batch Prediction)
- **Purpose**: Hospital-wide analytics and batch predictions
- **Input**: Multiple patient records
- **Output**: Aggregate metrics, trends, visualizations
- **Technology**: Random Forest ML model + Plotly charts
- **Position**: Third sub-page

### 🔬 Model Training Section (5 Sub-pages)
- **Purpose**: Custom model development pipeline
- **Features**: Data upload, EDA, preprocessing, training, evaluation
- **Output**: Trained models with performance metrics
- **Technology**: Scikit-learn, XGBoost, SHAP

---

**Legend:**
- ⭐ = New/Changed
- [DEFAULT] = Default landing page/sub-page
- [FIRST] = First position in list
- → = Navigation flow
- ├─► = Sub-page
- └─► = Last sub-page
