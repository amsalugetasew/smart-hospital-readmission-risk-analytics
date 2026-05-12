# 🧭 Navigation Structure

## Two-Level Navigation System

The application now features a **hierarchical two-level navigation** system with a main menu and context-specific submenus.

---

## 📊 Navigation Hierarchy

```
🏥 Hospital Readmission Risk Analytics
│
├── 📋 MAIN MENU (Top Level)
│   │
│   ├── 🎯 Prediction
│   │   │
│   │   └── Prediction Submenu:
│   │       ├── 💓 Readmission Prediction
│   │       │   ├── Single Patient Form
│   │       │   └── Batch Prediction (CSV/Excel Upload)
│   │       │
│   │       └── 📈 Analytics Dashboard
│   │           ├── KPIs
│   │           ├── Readmission Overview (Cards)
│   │           ├── Clinical Analysis (Cards)
│   │           ├── Demographics & Stay Duration (Cards)
│   │           ├── Geographic & Seasonal Patterns (Cards)
│   │           ├── Insurance & Historical Patterns (Cards)
│   │           ├── Risk Factors Analysis (Cards)
│   │           └── Summary Statistics
│   │
│   └── 🔬 Model Training
│       │
│       └── Model Training Submenu:
│           ├── ☁️ Dataset Upload
│           │   ├── Upload Custom Dataset
│           │   ├── Dataset Overview
│           │   └── Switch Dataset
│           │
│           ├── 📊 EDA (Exploratory Data Analysis)
│           │   ├── Feature Distributions
│           │   ├── Correlation Heatmap
│           │   ├── Missing Values Analysis
│           │   └── Target Distribution
│           │
│           ├── ⚙️ Preprocessing
│           │   ├── View Raw Data
│           │   ├── Preprocessing Pipeline
│           │   ├── Feature Scaling
│           │   └── One-Hot Encoding
│           │
│           ├── 🤖 Model Training
│           │   ├── Select Algorithm
│           │   ├── Configure Hyperparameters
│           │   ├── Train/Test Split
│           │   ├── Train Model
│           │   └── View Metrics
│           │
│           └── ⚡ Model Performance
│               ├── Performance Metrics
│               ├── Confusion Matrix
│               ├── Feature Importance
│               └── Classification Report
```

---

## 🎨 Visual Design

### Main Menu (Top Level)
- **Location**: Sidebar, below backend status
- **Style**: Large buttons with bold text
- **Colors**: 
  - Prediction: Green theme (#00A86B)
  - Model Training: Blue theme (#0066CC)
- **Icons**: 
  - Prediction: 🎯 (activity)
  - Model Training: 🔬 (cpu)

### Submenus (Second Level)
- **Location**: Sidebar, below main menu
- **Style**: Smaller buttons, indented appearance
- **Dynamic**: Changes based on main menu selection
- **Colors**: Match parent menu theme

---

## 🔄 Navigation Flow

### User Journey 1: Making Predictions
1. User opens app → Lands on **Prediction** menu (default)
2. Sees two options:
   - **Readmission Prediction** (default selected)
   - **Analytics Dashboard**
3. Can switch between prediction modes without leaving Prediction menu

### User Journey 2: Training Models
1. User clicks **Model Training** in main menu
2. Sidebar updates to show 5 training-related pages:
   - **Dataset Upload** (default selected)
   - **EDA**
   - **Preprocessing**
   - **Model Training**
   - **Model Performance**
3. Can navigate through entire ML pipeline sequentially

---

## 💡 Key Features

### ✅ Benefits of Two-Level Navigation

1. **Better Organization**
   - Clear separation between prediction and training workflows
   - Reduced cognitive load (fewer options visible at once)
   - Logical grouping of related features

2. **Improved User Experience**
   - Intuitive navigation structure
   - Context-aware submenus
   - Faster access to frequently used features

3. **Scalability**
   - Easy to add new features under existing categories
   - Can add more main menu items if needed
   - Maintains clean sidebar even with many pages

4. **Visual Clarity**
   - Color-coded menus (Green for Prediction, Blue for Training)
   - Clear visual hierarchy
   - Consistent styling throughout

---

## 🎯 Menu Mapping

### Old Navigation → New Navigation

| Old Single-Level Menu | New Main Menu | New Submenu |
|----------------------|---------------|-------------|
| Dataset Upload | Model Training | Dataset Upload |
| EDA | Model Training | EDA |
| Preprocessing | Model Training | Preprocessing |
| Model Training | Model Training | Model Training |
| Readmission Prediction | **Prediction** | **Readmission Prediction** |
| Analytics Dashboard | **Prediction** | **Analytics Dashboard** |
| Model Performance | Model Training | Model Performance |

---

## 🔧 Technical Implementation

### Session State Management
```python
# Main menu state
st.session_state['main_menu'] = "Prediction"  # or "Model Training"
```

### Conditional Submenu Rendering
```python
if main_menu == "Prediction":
    # Show prediction submenu
    page = option_menu(options=["Readmission Prediction", "Analytics Dashboard"])
else:
    # Show model training submenu
    page = option_menu(options=["Dataset Upload", "EDA", "Preprocessing", ...])
```

### Styling
- Main menu: Larger font (18px), bold (600-700 weight)
- Submenu: Standard font (16px), normal weight
- Color themes: Green (#00A86B) for Prediction, Blue (#0066CC) for Training

---

## 📱 Responsive Design

The navigation system is fully responsive and works on:
- ✅ Desktop (full sidebar)
- ✅ Tablet (collapsible sidebar)
- ✅ Mobile (hamburger menu)

---

## 🚀 Usage Instructions

### For End Users

1. **To Make Predictions:**
   - Ensure "Prediction" is selected in main menu (default)
   - Choose between:
     - "Readmission Prediction" for single/batch predictions
     - "Analytics Dashboard" for data visualization

2. **To Train Models:**
   - Click "Model Training" in main menu
   - Follow the workflow:
     1. Dataset Upload → Upload your data
     2. EDA → Explore your data
     3. Preprocessing → Prepare data
     4. Model Training → Train model
     5. Model Performance → Evaluate results

### For Developers

The navigation structure is defined in `frontend/app.py` starting around line 340.

**To add a new page:**
1. Decide which main menu it belongs to
2. Add to the appropriate submenu options list
3. Add corresponding page logic with `if page == "Your Page Name":`

**To add a new main menu:**
1. Add to main menu options list
2. Create new submenu section with `if main_menu == "Your Menu":`
3. Define submenu pages

---

## 📝 Notes

- All existing functionality is preserved
- No changes to page content or features
- Only navigation structure has been reorganized
- Backend connectivity and dataset management unchanged
- All pages work exactly as before

---

**Last Updated**: May 12, 2026
**Version**: 2.0 (Two-Level Navigation)
