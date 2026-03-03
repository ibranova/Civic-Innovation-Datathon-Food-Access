# app.py - Beyond the Pantry: Food Coverage Predictor
# =====================================================
# Updated based on instructor feedback

import streamlit as st
import joblib
import json
import numpy as np
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="🍎 Beyond the Pantry",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Updated with 26pt minimum font for body text
st.markdown("""
<style>
    /* BIG CAPTIVATING HEADER */
    .main-title {
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #1B5E20, #4CAF50, #81C784);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0;
        line-height: 1.1;
    }
    .subtitle {
        font-size: 1.8rem;
        color: #333;
        text-align: center;
        font-weight: 600;
        margin-top: 0;
    }
    .tagline {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E8F5E9;
    }
    
    /* Body text - 26pt minimum */
    .big-text {
        font-size: 26px !important;
        line-height: 1.5;
    }
    .medium-text {
        font-size: 22px !important;
        line-height: 1.4;
    }
    
    /* Prediction result boxes */
    .result-high {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 8px solid #2E7D32;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .result-low {
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        border-left: 8px solid #C62828;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    /* Definition card */
    .definition-card {
        background: #E3F2FD;
        border: 2px solid #1976D2;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Static note card */
    .static-note {
        background: #FFF8E1;
        border: 2px solid #FFA000;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Performance card */
    .performance-card {
        background: #F5F5F5;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #E0E0E0;
    }
    
    /* Scenario explanation boxes */
    .scenario-card {
        background: #F5F5F5;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 6px solid #2196F3;
    }
    .scenario-positive {
        border-left-color: #1565C0;
        background: #E3F2FD;
    }
    .scenario-negative {
        border-left-color: #E65100;
        background: #FFF3E0;
    }
    
    /* Hide anchor links next to headers */
    .stMarkdown a[href^="#"] {
        display: none !important;
    }
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
    
    /* Limitation warning */
    .limitation-box {
        background: #FFF3E0;
        border: 2px solid #FF9800;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# LOAD MODEL AND DATA
# =============================================================================
@st.cache_resource
def load_model():
    return joblib.load("/Users/Marcy_Student/Desktop/Marcy_Projects/CID_Food_Access/deployment/coverage_model.pkl")

@st.cache_resource
def load_scaler():
    return joblib.load("/Users/Marcy_Student/Desktop/Marcy_Projects/CID_Food_Access/deployment/scaler.pkl")

@st.cache_data
def load_metadata():
    with open("/Users/Marcy_Student/Desktop/Marcy_Projects/CID_Food_Access/deployment/model_metadata.json", "r") as f:
        return json.load(f)

try:
    model = load_model()
    scaler = load_scaler()
    meta = load_metadata()
except Exception as e:
    st.error(f"⚠️ Error loading files: {e}")
    st.info("Make sure coverage_model.pkl, scaler.pkl, and model_metadata.json are in the same folder as app.py")
    st.stop()

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.markdown("## Model Performance")
st.sidebar.metric("Recall (low coverage areas)", "92%")

# Class balance information
st.sidebar.markdown("---")
st.sidebar.markdown("### Training Data")
st.sidebar.markdown("""
<p style="font-size: 20SSpx;">
<strong>197 NYC Neighborhoods (NTAs)</strong><br>
• 50.3% High Coverage (99 NTAs)<br>
• 49.7% Low Coverage (98 NTAs)<br>
• The classes are balanced, nearly 50/50.
  This is especially important because it prevents the model from being biased toward the majority class.
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("## Input Neighborhood Details")

# Get feature stats for slider ranges
feat_stats = meta['feature_statistics']

# Input widgets with ranges shown
food_min = feat_stats['food_insecure_percentage']['min']
food_max = feat_stats['food_insecure_percentage']['max']
unemp_min = feat_stats['unemployment_rate']['min']
unemp_max = feat_stats['unemployment_rate']['max']

food_insecure = st.sidebar.slider(
    "Food Insecurity Rate (%)",
    min_value=0.0,
    max_value=40.0,
    value=15.0,
    step=1.0,
    help=f"Training data range: {food_min:.1f}% - {food_max:.1f}%"
)

unemployment = st.sidebar.slider(
    "Unemployment Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=8.0,
    step=0.5,
    help=f"Training data range: {unemp_min:.1f}% - {unemp_max:.1f}%"
)

high_shelter = st.sidebar.checkbox(
    "High Shelter Population",
    value=False,
    help="Above-average shelter population in this area?"
)

has_kitchen = st.sidebar.checkbox(
    "Has Soup Kitchen",
    value=False,
    help="Are there soup kitchens in this neighborhood?"
)

has_weekend = st.sidebar.checkbox(
    "Has Weekend Hours",
    value=False,
    help="Are food sites open on weekends?"
)

st.sidebar.markdown("---")

predict_btn = st.sidebar.button("Predict Coverage", type="primary", use_container_width=True)

# Limitation note
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="limitation-box">
<p style="font-size: 13px; margin: 0;">
<strong>Model Limitation</strong><br><br>
This model can only generalize to neighborhoods <strong>within the training data range</strong>:<br><br>
• Food Insecurity: 2.9% - 36.0%<br>
• Unemployment: 1.4% - 17.0%<br><br>
Predictions for values outside these ranges may be unreliable.
</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN CONTENT - PAGE NAVIGATION
# =============================================================================
page = st.radio("", ["Prediction", "Model Details"], horizontal=True, label_visibility="collapsed")

# =============================================================================
# PAGE 1: PREDICTION
# =============================================================================
if page == "Prediction":
    
    # Header
    st.markdown('<h1 class="main-title">🍎 Beyond the Pantry</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">NYC Food Coverage Predictor</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Identify neighborhoods that need more food assistance resources</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # MODEL PERFORMANCE SUMMARY (STATIC - AT TOP)
    # =========================================================================
    st.markdown("---")
    
    perf_col1, perf_col2 = st.columns([2, 1])
    
    with perf_col1:
        st.markdown("### Model Performance Summary")
        st.markdown("""
        <div class="performance-card">
            <p class="big-text" style="margin-bottom: 1rem;">
                <strong style="font-size: 48px; color: #2E7D32;">92%</strong> Recall
            </p>
            <p class="medium-text">
                Our model catches <strong>92% of underserved neighborhoods</strong> (low coverage areas).
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col2:
        st.markdown("### Why Recall?")
        st.markdown("""
        <div class="definition-card">
            <p style="font-size: 18px; margin: 0;">
                <strong>We prioritize Recall because:</strong><br><br>
                We want to <strong>detect as many underserved neighborhoods as possible</strong>. 
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Static note
    st.markdown("""
    <div class="static-note">
        <p style="font-size: 16px; margin: 0;">
            <strong>Note:</strong> This performance metric is <strong>static</strong> — it reflects how the model performed on test data and does <strong>not change</strong> based on your input below.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # =========================================================================
    # PREDICTION SECTION
    # =========================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Your Neighborhood Profile")
        
        profile_data = pd.DataFrame({
            "Factor": [
                "Food Insecurity Rate",
                "Unemployment Rate", 
                "High Shelter Area",
                "Has Soup Kitchen",
                "Weekend Hours"
            ],
            "Value": [
                f"{food_insecure:.0f}%",
                f"{unemployment:.1f}%",
                "Yes ✓" if high_shelter else "No",
                "Yes ✓" if has_kitchen else "No",
                "Yes ✓" if has_weekend else "No"
            ]
        })
        st.dataframe(profile_data, use_container_width=True, hide_index=True)
        
        # Comparison chart
        st.markdown("#### Inputs vs NYC Average")
        
        comp_data = pd.DataFrame({
            'Metric': ['Food Insecurity', 'Unemployment'],
            'Your Input': [food_insecure, unemployment],
            'NYC Average': [feat_stats['food_insecure_percentage']['mean'], 
                           feat_stats['unemployment_rate']['mean']]
        }).melt(id_vars=['Metric'], var_name='Type', value_name='Rate')
        
        chart = alt.Chart(comp_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X('Metric:N', axis=alt.Axis(labelAngle=0, title='')),
            y=alt.Y('Rate:Q', title='Rate (%)'),
            color=alt.Color('Type:N', scale=alt.Scale(
                domain=['Your Input', 'NYC Average'],
                range=['#78c679', '#BDBDBD']
            )),
            xOffset='Type:N'
        ).properties(height=220).configure_legend(orient='bottom', title=None)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.markdown("### Prediction Result")
        
        # Definition card - ALWAYS VISIBLE
        st.markdown("""
        <div class="definition-card">
            <p style="font-size: 20px; margin: 0;">
                <strong>What is "Coverage"?</strong><br><br>
                <strong>Coverage</strong> refers to whether a neighborhood has <strong>adequate emergency food assistance resources</strong> (food pantries, soup kitchens, etc.) relative to its need level.<br><br>
                <strong>• 1 = High Coverage</strong> — Adequate food assistance<br>
                <strong>• 0 = Low Coverage</strong> — Needs more resources
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if predict_btn:
            # Prepare and scale input
            input_data = np.array([[food_insecure, unemployment, float(high_shelter), 
                                   int(has_kitchen), int(has_weekend)]])
            input_scaled = scaler.transform(input_data)
            
            # Predict
            prediction = model.predict(input_scaled)[0]
            proba = model.predict_proba(input_scaled)[0]
            
            if prediction == 1:
                st.markdown("""
                <div class="result-high">
                    <h2 style="color:#1B5E20; margin:0; font-size: 32px;">HIGH COVERAGE (1)</h2>
                    <p style="font-size: 22px; margin-top: 0.5rem;">This neighborhood likely has adequate food assistance.</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Confidence: {proba[1]*100:.0f}%**")
                st.progress(proba[1])
            else:
                st.markdown("""
                <div class="result-low">
                    <h2 style="color:#B71C1C; margin:0; font-size: 32px;">LOW COVERAGE (0)</h2>
                    <p style="font-size: 22px; margin-top: 0.5rem;">This neighborhood needs more food assistance resources.</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Confidence: {proba[0]*100:.0f}%**")
                st.progress(proba[0])
            
            st.markdown("---")
            st.markdown("### Recommended Actions")
            
            if prediction == 0:
                st.markdown("""
                <p class="big-text">
                • <strong>Add new food sites</strong> in this area<br>
                • <strong>Extend hours</strong> at existing locations<br>
                • <strong>Partner</strong> with local organizations<br>
                • <strong>Prioritize</strong> in next funding cycle
                </p>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <p class="big-text">
                • <strong>Maintain</strong> current service levels<br>
                • <strong>Monitor</strong> for changes in need<br>
                • <strong>Share</strong> best practices with other areas
                </p>
                """, unsafe_allow_html=True)
        else:
            st.info("Enter neighborhood details in the sidebar and click **Predict Coverage**")
            
     

# =============================================================================
# PAGE 2: MODEL DETAILS
# =============================================================================
elif page == "Model Details":
    
    st.markdown("## Model Details")
    st.markdown("### What Affects Food Coverage?")
    st.markdown("""
    <p class="big-text">
    Below are the factors the model uses to predict coverage, <strong>ordered by importance</strong> (strongest effect first).
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # =========================================================================
    # WHAT THE MODEL FOUND (replacing confusion matrix)
    # =========================================================================
    st.markdown("### What the Model Correctly Identified")
    
    found_col1, found_col2 = st.columns(2)
    
    with found_col1:
        st.markdown("""
        <div class="result-low" style="text-align: center;">
            <p style="font-size: 64px; margin: 0; font-weight: bold; color: #B71C1C;">23</p>
            <p style="font-size: 24px; margin: 0;">out of 25</p>
            <p style="font-size: 20px; margin-top: 1rem;"><strong>Low Coverage areas correctly identified</strong></p>
            <p style="font-size: 18px; color: #666;">(92% Recall for Low Coverage)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with found_col2:
        st.markdown("""
        <div class="result-high" style="text-align: center;">
            <p style="font-size: 64px; margin: 0; font-weight: bold; color: #1B5E20;">20</p>
            <p style="font-size: 24px; margin: 0;">out of 25</p>
            <p style="font-size: 20px; margin-top: 1rem;"><strong>High Coverage areas correctly identified</strong></p>
            <p style="font-size: 18px; color: #666;">(80% Recall for High Coverage)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <p class="big-text" style="margin-top: 1.5rem;">
    <strong>Overall:</strong> The model correctly classified <strong>43 out of 50</strong> neighborhoods in testing (86% accuracy).
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # =========================================================================
    # FEATURE IMPORTANCE - ORDERED BY ABSOLUTE COEFFICIENT
    # =========================================================================
    st.markdown("### How Each Factor Affects Coverage")
    st.markdown("""
    <p class="medium-text" style="color: #666;">
    <em>Ordered by importance (strongest effect first):</em>
    </p>
    """, unsafe_allow_html=True)
    
    # 1. Food Insecurity Rate (coefficient: -1.34) - STRONGEST
    st.markdown("""
    <div class="scenario-card scenario-positive">
        <h3 style="margin:0; font-size: 28px;">1. Food Insecurity Rate</h3>
        <p style="font-size: 22px; margin: 0.5rem 0;"><strong>Effect: Makes LOW coverage more likely</strong></p>
        <p style="font-size: 20px; margin: 0;">
        <em>Scenario:</em> Compare two neighborhoods — one with 10% food insecurity and another with 25%. 
        The neighborhood with <strong>higher food insecurity is more likely to have LOW coverage</strong>. 
        This shows that areas with the greatest need often have the fewest resources.
        </p>
        <p style="font-size: 16px; color: ; margin-top: 0.5rem;"><strong>Importance: Highest</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Has Soup Kitchen (coefficient: 1.03)
    st.markdown("""
    <div class="scenario-card scenario-positive">
        <h3 style="margin:0; font-size: 28px;">2. Has Soup Kitchen</h3>
        <p style="font-size: 22px; margin: 0.5rem 0;"><strong>Effect: Makes HIGH coverage more likely</strong></p>
        <p style="font-size: 20px; margin: 0;">
        <em>Scenario:</em> Neighborhoods with soup kitchens are <strong>much more likely to have good coverage</strong>. 
        Soup kitchens are a strong sign that an area has adequate food resources.
        </p>
        <p style="font-size: 16px; color: #666; margin-top: 0.5rem;"><strong>Importance: Very High</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Weekend Hours (coefficient: 0.97)
    st.markdown("""
    <div class="scenario-card scenario-positive">
        <h3 style="margin:0; font-size: 28px;">3. Weekend Hours</h3>
        <p style="font-size: 22px; margin: 0.5rem 0;"><strong>Effect: Makes HIGH coverage more likely</strong></p>
        <p style="font-size: 20px; margin: 0;">
        <em>Scenario:</em> Areas with weekend food services have <strong>better coverage</strong>. 
        Weekend availability matters because many working families can only access services on weekends.
        </p>
        <p style="font-size: 16px; color: #666; margin-top: 0.5rem;"><strong>Importance: High</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 4. High Shelter Population (coefficient: 0.78)
    st.markdown("""
    <div class="scenario-card scenario-positive">
        <h3 style="margin:0; font-size: 28px;">4. High Shelter Population</h3>
        <p style="font-size: 22px; margin: 0.5rem 0;"><strong>Effect: Makes HIGH coverage more likely</strong></p>
        <p style="font-size: 20px; margin: 0;">
        <em>Scenario:</em> Neighborhoods with large shelter populations tend to have <strong>more food resources</strong>. 
        This suggests programs are reaching these vulnerable populations.
        </p>
        <p style="font-size: 16px; color: #666; margin-top: 0.5rem;"><strong>Importance: Moderate</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 5. Unemployment Rate (coefficient: 0.40) - LOWEST
    st.markdown("""
    <div class="scenario-card scenario-positive">
        <h3 style="margin:0; font-size: 28px;">5. Unemployment Rate</h3>
        <p style="font-size: 22px; margin: 0.5rem 0;"><strong>Effect: Makes HIGH coverage more likely</strong></p>
        <p style="font-size: 20px; margin: 0;">
        <em>Scenario:</em> Areas with higher unemployment tend to have <strong>better food coverage</strong>. 
        This is good news — food programs have successfully targeted economically distressed areas!
        </p>
        <p style="font-size: 16px; color: #666; margin-top: 0.5rem;"><strong>Importance: Lower</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
   # Key Insight - Neutral note style
    st.markdown("""
    <div style="background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
        <p style="font-size: 20px; margin: 0;">
        <strong>Key Insight:</strong> Food insecurity is the strongest predictor of LOW coverage — meaning the neighborhoods 
        that need help the most are often getting the least. Meanwhile, soup kitchens and weekend hours are the 
        strongest indicators of GOOD coverage.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<p style="font-size: 18px;">
<strong>Beyond the Pantry</strong> | NYC Food Insecurity Analysis<br>
<em>Helping policymakers identify neighborhoods that need more food assistance.</em>
</p>
""", unsafe_allow_html=True)