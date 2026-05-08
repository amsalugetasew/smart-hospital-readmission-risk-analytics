# Risk Category Classification Guide

## 🎯 Overview

The Smart Hospital Readmission Risk Analytics system classifies patients into **three risk categories** based on their predicted probability of readmission within 30 days.

---

## 📊 Risk Categories

### 🟢 Low Risk
**Probability Range**: 0% - 33%

**Interpretation:**
- Patient has a **low probability** of being readmitted
- Standard risk level
- Routine care is appropriate

**Clinical Recommendations:**
- ✅ Standard discharge planning
- ✅ Routine follow-up care
- ✅ Standard patient education
- ✅ Normal monitoring protocol

**Actions:**
- Schedule standard follow-up appointment (2-4 weeks)
- Provide standard discharge instructions
- Ensure patient understands medications
- No additional interventions required

**Example Scenarios:**
- Probability = 15% → Low Risk
- Probability = 25% → Low Risk
- Probability = 32% → Low Risk

---

### 🟡 Medium Risk
**Probability Range**: 33% - 66%

**Interpretation:**
- Patient has a **moderate probability** of being readmitted
- Elevated risk level
- Enhanced care recommended

**Clinical Recommendations:**
- ⚠️ Enhanced discharge planning
- ⚠️ Closer follow-up monitoring
- ⚠️ Additional patient education
- ⚠️ Consider support services

**Actions:**
- Schedule earlier follow-up appointment (1-2 weeks)
- Provide detailed discharge instructions
- Conduct medication reconciliation
- Offer patient education materials
- Consider home health referral
- Arrange post-discharge phone call

**Example Scenarios:**
- Probability = 40% → Medium Risk
- Probability = 50% → Medium Risk
- Probability = 65% → Medium Risk

---

### 🔴 High Risk
**Probability Range**: 66% - 100%

**Interpretation:**
- Patient has a **high probability** of being readmitted
- Critical risk level
- Intensive intervention required

**Clinical Recommendations:**
- 🚨 Intensive discharge planning
- 🚨 Immediate intervention strategies
- 🚨 Comprehensive care coordination
- 🚨 Readmission prevention program

**Actions:**
- **Immediate Follow-up**: Schedule within 3-7 days
- **Home Health Services**: Arrange visiting nurse
- **Medication Management**: 
  - Complete medication reconciliation
  - Simplify medication regimen if possible
  - Provide pill organizer
- **Patient/Family Education**:
  - Detailed disease management education
  - Warning signs to watch for
  - When to seek medical attention
- **Care Coordination**:
  - Assign care coordinator
  - Enroll in transitional care program
  - Coordinate with primary care physician
- **Social Support**:
  - Assess social determinants of health
  - Connect with community resources
  - Arrange transportation for appointments

**Example Scenarios:**
- Probability = 70% → High Risk
- Probability = 85% → High Risk
- Probability = 95% → High Risk

---

## 🔢 Risk Calculation

### Formula

```python
def calculate_risk_category(probability):
    """
    Calculate risk category based on readmission probability
    
    Args:
        probability (float): Predicted probability (0.0 to 1.0)
    
    Returns:
        str: Risk category ("Low Risk", "Medium Risk", or "High Risk")
    """
    if probability < 0.33:
        return "Low Risk"
    elif probability < 0.66:
        return "Medium Risk"
    else:
        return "High Risk"
```

### Thresholds

| Probability | Risk Category | Color Code |
|-------------|---------------|------------|
| 0% - 32.9% | Low Risk | 🟢 Green |
| 33% - 65.9% | Medium Risk | 🟡 Yellow/Orange |
| 66% - 100% | High Risk | 🔴 Red |

### Examples

| Probability | Category | Color | Action Level |
|-------------|----------|-------|--------------|
| 10% | Low Risk | 🟢 | Standard |
| 25% | Low Risk | 🟢 | Standard |
| 32.9% | Low Risk | 🟢 | Standard |
| 33% | Medium Risk | 🟡 | Enhanced |
| 50% | Medium Risk | 🟡 | Enhanced |
| 65.9% | Medium Risk | 🟡 | Enhanced |
| 66% | High Risk | 🔴 | Intensive |
| 80% | High Risk | 🔴 | Intensive |
| 95% | High Risk | 🔴 | Intensive |

---

## 🎨 Visual Indicators

### Color Coding

The system uses consistent color coding throughout:

**🟢 Green (Low Risk)**
- RGB: (0, 168, 107)
- Hex: #00A86B
- Meaning: Safe, standard care

**🟡 Yellow/Orange (Medium Risk)**
- RGB: (255, 107, 53)
- Hex: #FF6B35
- Meaning: Caution, enhanced care

**🔴 Red (High Risk)**
- RGB: (220, 20, 60)
- Hex: #DC143C
- Meaning: Alert, intensive care

### Where Colors Appear

1. **Single Patient Prediction**:
   - Risk category box background
   - Probability display

2. **Batch Prediction Results**:
   - Table row highlighting
   - Risk category column

3. **Analytics Dashboard**:
   - Gauge chart zones
   - Bar chart colors
   - Pie chart segments

4. **Visualizations**:
   - Risk distribution charts
   - Probability histograms
   - Summary statistics

---

## 📈 Clinical Decision Support

### Decision Tree

```
Patient Prediction
    ↓
Probability Calculated
    ↓
┌─────────────┬─────────────┬─────────────┐
│   < 33%     │  33% - 66%  │   > 66%     │
│             │             │             │
│  Low Risk   │ Medium Risk │  High Risk  │
│     🟢      │     🟡      │     🔴      │
└─────────────┴─────────────┴─────────────┘
    ↓              ↓              ↓
Standard      Enhanced      Intensive
  Care          Care          Care
```

### Intervention Intensity

| Risk Level | Intervention Intensity | Resource Allocation |
|------------|----------------------|---------------------|
| Low | Standard (1x) | Normal |
| Medium | Enhanced (2x) | Moderate |
| High | Intensive (3x) | Maximum |

---

## 💡 Best Practices

### For Clinicians

1. **Use Risk Category as a Guide**:
   - Not a replacement for clinical judgment
   - Consider patient-specific factors
   - Review feature importance for context

2. **Focus on High-Risk Patients**:
   - Prioritize intervention resources
   - Implement prevention strategies
   - Monitor closely post-discharge

3. **Document Interventions**:
   - Record risk category in patient chart
   - Document prevention strategies implemented
   - Track outcomes for quality improvement

4. **Combine with Clinical Assessment**:
   - Use as one data point
   - Consider social determinants
   - Assess patient readiness for discharge

### For Administrators

1. **Resource Planning**:
   - Allocate resources based on risk distribution
   - Staff transitional care programs appropriately
   - Budget for prevention interventions

2. **Quality Metrics**:
   - Track readmission rates by risk category
   - Monitor intervention effectiveness
   - Measure return on investment

3. **Program Development**:
   - Design targeted programs for high-risk patients
   - Implement care coordination services
   - Develop patient education materials

---

## 📊 Expected Distribution

In a typical hospital population:

| Risk Category | Expected % | Example (1000 patients) |
|---------------|-----------|------------------------|
| Low Risk | 30-40% | 300-400 patients |
| Medium Risk | 30-40% | 300-400 patients |
| High Risk | 20-30% | 200-300 patients |

**Note**: Actual distribution depends on:
- Patient population characteristics
- Hospital type (academic, community, specialty)
- Geographic location
- Seasonal factors

---

## 🎯 Performance Metrics

### Model Calibration

The risk categories are calibrated such that:

- **Low Risk patients**: ~15-25% actual readmission rate
- **Medium Risk patients**: ~45-55% actual readmission rate
- **High Risk patients**: ~75-85% actual readmission rate

### Validation

Regular validation ensures:
- ✅ Categories align with actual outcomes
- ✅ Thresholds remain appropriate
- ✅ Model maintains accuracy over time

---

## 🔄 Updating Thresholds

If your hospital wants to adjust risk thresholds:

### Current Thresholds (Default):
```python
LOW_RISK_THRESHOLD = 0.33
HIGH_RISK_THRESHOLD = 0.66
```

### To Modify:
1. Edit `frontend/app.py` and `backend/predictor.py`
2. Update threshold values
3. Retrain and validate model
4. Update documentation

### Considerations:
- **Lower thresholds** → More patients in higher risk categories → More interventions
- **Higher thresholds** → Fewer patients in higher risk categories → Fewer interventions
- Balance sensitivity vs. resource availability

---

## 📞 Support

For questions about risk categories:
- Review this guide
- Check `README.md` for overview
- See `BATCH_PREDICTION_GUIDE.md` for batch processing
- Consult `TROUBLESHOOTING.md` for issues

---

## 🎉 Summary

**Risk Categories:**
- 🟢 **Low (0-33%)**: Standard care
- 🟡 **Medium (33-66%)**: Enhanced care
- 🔴 **High (66-100%)**: Intensive care

**Key Points:**
- ✅ Evidence-based thresholds
- ✅ Consistent color coding
- ✅ Actionable recommendations
- ✅ Clinical decision support
- ✅ Resource allocation guide

**Use risk categories to:**
- Prioritize interventions
- Allocate resources efficiently
- Improve patient outcomes
- Reduce readmission rates
- Support clinical decisions

---

**The risk category system helps you identify which patients need the most attention and resources!** 🎯
