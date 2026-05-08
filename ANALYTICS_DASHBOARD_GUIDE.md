# Analytics Dashboard Guide

## 🎨 New Features

The Analytics Dashboard has been completely redesigned with:
- **Hospital-themed color palette** (medical blues, greens, reds)
- **10+ different chart types** (pie, gauge, bar, area, violin, scatter, heatmap, funnel, line)
- **Interactive visualizations** with hover details
- **Comprehensive analytics** across 6 major sections

---

## 🏥 Hospital-Themed Color Palette

### Primary Colors:
- **Medical Blue** (#0066CC) - Primary actions, trust
- **Medical Green** (#00A86B) - Success, safe outcomes
- **Medical Orange** (#FF6B35) - Warnings, attention needed
- **Medical Red** (#DC143C) - Danger, high risk
- **Medical Teal** (#20B2AA) - Information, calm
- **Medical Purple** (#9370DB) - Special categories

### Color Meanings:
- **Green** = Not Readmitted, Safe, Low Risk
- **Red** = Readmitted, Danger, High Risk
- **Blue** = Neutral, Information
- **Orange/Yellow** = Warning, Medium Risk

---

## 📊 Dashboard Sections

### 1. Key Performance Indicators (KPIs)
**5 Metric Cards:**
- Total Patients
- Readmission Rate (with delta)
- Average Length of Stay
- High Risk Patients
- Average Age

**Purpose**: Quick overview of hospital performance

---

### 2. Readmission Overview

#### Chart 1: Overall Readmission Distribution (Donut Chart)
- **Type**: Pie chart with hole (donut)
- **Colors**: Green (not readmitted), Red (readmitted)
- **Features**:
  - Shows percentage and count
  - Center displays total patients
  - Interactive hover with details

#### Chart 2: Readmission Rate Gauge
- **Type**: Gauge/speedometer chart
- **Colors**: 
  - Green zone (0-30%): Low risk
  - Orange zone (30-60%): Medium risk
  - Red zone (60-100%): High risk
- **Features**:
  - Shows current rate
  - Delta from 50% benchmark
  - Threshold line at 70%

---

### 3. Clinical Analysis

#### Chart 3: Readmission Rate by Primary Diagnosis (Horizontal Bar)
- **Type**: Horizontal bar chart (sorted)
- **Colors**: Risk gradient (yellow → orange → red)
- **Features**:
  - Sorted by readmission rate
  - Shows patient count on hover
  - Color intensity indicates risk level

#### Chart 4: Treatment Type Distribution (Stacked Bar)
- **Type**: Stacked bar chart
- **Colors**: Green (not readmitted), Red (readmitted)
- **Features**:
  - Shows distribution by treatment type
  - Stacked to show total patients
  - Hover shows exact counts

---

### 4. Patient Demographics & Stay Duration

#### Chart 5: Age Distribution (Area Chart)
- **Type**: Area chart with fill
- **Colors**: Green and Red areas
- **Features**:
  - Shows age groups (10-year bins)
  - Separate areas for readmitted vs not
  - Unified hover mode

#### Chart 6: Length of Stay Distribution (Violin Plot)
- **Type**: Violin plot with box plot
- **Colors**: Green (not readmitted), Red (readmitted)
- **Features**:
  - Shows distribution shape
  - Box plot shows quartiles
  - Outliers displayed as points

---

### 5. Geographic & Seasonal Patterns

#### Chart 7: Readmission by Region (Donut Chart)
- **Type**: Pie chart with hole
- **Colors**: Categorical palette (6 colors)
- **Features**:
  - Shows patient distribution
  - Readmission rates listed below
  - Interactive hover

#### Chart 8: Seasonal Readmission Patterns (Bar Chart)
- **Type**: Vertical bar chart
- **Colors**: Season-specific
  - Winter: Blue
  - Spring: Green
  - Summer: Orange
  - Fall: Red
- **Features**:
  - Ordered by season
  - Shows rate and count
  - Hover with details

#### Chart 9: Insurance Type Distribution (Funnel Chart)
- **Type**: Funnel chart
- **Colors**: Blue gradient
- **Features**:
  - Shows patient flow by insurance
  - Sorted by volume
  - Percentage of initial shown

---

### 6. Risk Factors Analysis

#### Chart 10: Comorbidities vs Medications (Scatter Plot)
- **Type**: Scatter plot with size
- **Colors**: Green (not readmitted), Red (readmitted)
- **Size**: Based on risk score
- **Features**:
  - Shows relationship between factors
  - Bubble size = risk score
  - Hover shows age, LOS, risk score
  - Sample of 1000 patients for performance

#### Chart 11: Risk Factor Correlation (Heatmap)
- **Type**: Correlation heatmap
- **Colors**: Red-Blue diverging scale
- **Features**:
  - Shows correlations between numeric variables
  - -1 (red) to +1 (blue)
  - Interactive hover with values

---

### 7. Impact of Previous Readmissions

#### Chart 12: Previous Readmissions Trend (Line + Bar)
- **Type**: Combination chart (line with area + bar)
- **Colors**: Red (rate line), Teal (count bars)
- **Features**:
  - Dual y-axis (rate and count)
  - Area fill under line
  - Shows clear trend
  - Unified hover mode

---

### 8. Summary Statistics

**4 Columns of Statistics:**
- Age Statistics (min, max, median, std dev)
- Length of Stay (min, max, median, std dev)
- Comorbidities (min, max, median, avg)
- Medications (min, max, median, avg)

---

## 🎯 Interactive Features

### Hover Interactions:
- **All charts** have custom hover templates
- Show relevant details (counts, percentages, rates)
- Formatted for readability

### Click Interactions:
- **Pie charts**: Click legend to hide/show slices
- **Bar charts**: Click legend to filter categories
- **Scatter plots**: Click legend to filter outcomes

### Zoom & Pan:
- **All Plotly charts** support zoom and pan
- Double-click to reset view
- Box select to zoom to area

---

## 🎨 Color Scheme Reference

### Chart-Specific Colors:

**Readmission Status:**
- Not Readmitted: `#00A86B` (Medical Green)
- Readmitted: `#DC143C` (Medical Red)

**Risk Levels:**
- Low (0-30%): `#00A86B` (Green)
- Medium (30-60%): `#FF6B35` (Orange)
- High (60-100%): `#DC143C` (Red)

**Seasons:**
- Winter: `#4A90E2` (Blue)
- Spring: `#7ED321` (Green)
- Summer: `#F5A623` (Orange)
- Fall: `#D0021B` (Red)

**Gradients:**
- Risk Gradient: Yellow → Orange → Red
- Safe Gradient: Light Green → Dark Green
- Blue Gradient: Light Blue → Dark Blue

---

## 📱 Responsive Design

All charts are:
- **Responsive**: Adapt to screen size
- **Container-width**: Use full available width
- **Height-optimized**: Appropriate heights for readability
- **Mobile-friendly**: Work on tablets and phones

---

## 🔧 Customization

### To Change Colors:

Edit the `HOSPITAL_COLORS` dictionary in the code:

```python
HOSPITAL_COLORS = {
    'primary': '#0066CC',      # Change to your primary color
    'success': '#00A86B',      # Change to your success color
    'danger': '#DC143C',       # Change to your danger color
    # ... etc
}
```

### To Add New Charts:

1. Load data: `df = pd.read_csv(DATASET_PATH)`
2. Process data: Group, aggregate, or transform
3. Create figure: Use `px.chart_type()` or `go.Figure()`
4. Update layout: Set colors, labels, titles
5. Display: `st.plotly_chart(fig, use_container_width=True)`

### To Modify Existing Charts:

Find the chart section and modify:
- **Data**: Change groupby, aggregation
- **Colors**: Update `color_discrete_map` or `color_continuous_scale`
- **Layout**: Modify `fig.update_layout()`
- **Traces**: Update `fig.update_traces()`

---

## 📊 Chart Type Guide

### When to Use Each Chart:

**Pie/Donut Chart:**
- Part-to-whole relationships
- Categorical distribution
- 2-6 categories max

**Gauge Chart:**
- Single metric with target
- Performance indicators
- Progress tracking

**Bar Chart:**
- Compare categories
- Show rankings
- Display counts or rates

**Area Chart:**
- Show trends over time/categories
- Emphasize magnitude
- Compare multiple series

**Violin Plot:**
- Show distribution shape
- Compare distributions
- Identify outliers

**Scatter Plot:**
- Show relationships
- Identify patterns
- Display 3+ dimensions (x, y, size, color)

**Heatmap:**
- Show correlations
- Display matrix data
- Identify patterns in 2D data

**Funnel Chart:**
- Show progressive reduction
- Display hierarchical data
- Emphasize volume differences

**Line Chart:**
- Show trends
- Time series data
- Continuous data

---

## 🎯 Best Practices

### Color Usage:
- ✅ Use consistent colors for same categories
- ✅ Use green for positive outcomes
- ✅ Use red for negative outcomes
- ✅ Use gradients for continuous scales
- ❌ Don't use too many colors (max 6-8)
- ❌ Don't use similar colors for different categories

### Chart Selection:
- ✅ Choose appropriate chart for data type
- ✅ Use interactive features
- ✅ Add hover details
- ✅ Label axes clearly
- ❌ Don't overcrowd charts
- ❌ Don't use 3D charts (hard to read)

### Layout:
- ✅ Group related charts
- ✅ Use consistent heights
- ✅ Add section headers
- ✅ Include summary statistics
- ❌ Don't make charts too small
- ❌ Don't put too many charts in one row

---

## 🚀 Performance Tips

### For Large Datasets:

1. **Sample data** for scatter plots:
   ```python
   df_sample = df.sample(min(1000, len(df)))
   ```

2. **Aggregate data** before plotting:
   ```python
   df_agg = df.groupby('category').agg({'value': 'mean'})
   ```

3. **Use appropriate chart types**:
   - Avoid scatter plots with >10k points
   - Use histograms instead of individual points
   - Aggregate time series data

4. **Optimize hover templates**:
   - Show only essential information
   - Format numbers appropriately
   - Use `<extra></extra>` to hide trace name

---

## 📝 Summary

The new Analytics Dashboard provides:
- ✅ **12 interactive charts** across 6 sections
- ✅ **Hospital-themed colors** for medical context
- ✅ **Multiple chart types** (pie, gauge, bar, area, violin, scatter, heatmap, funnel, line)
- ✅ **Comprehensive analytics** covering all aspects
- ✅ **Interactive features** (hover, click, zoom, pan)
- ✅ **Responsive design** for all screen sizes
- ✅ **Professional appearance** suitable for presentations

**Total visualizations**: 12 charts + 5 KPI cards + 4 summary stat columns = 21 visual elements

---

**Enjoy your enhanced Analytics Dashboard!** 🎉
