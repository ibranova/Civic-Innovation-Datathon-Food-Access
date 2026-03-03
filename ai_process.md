
# AI Process Documentation
---

## Overview

This document outlines how AI tools were used throughout this project, including prompting strategies, iteration process, validation methods, and human decision-making. Each section reflects individual contributions and responsible AI usage.

---

# Angel – AI Usage Process

## 1. Purpose of AI Use

I mainly used AI during the EDA process. I ran into a lot of coding errors while cleaning, merging, and analyzing my datasets, so I used AI to help me figure out what was going wrong and how to fix it. I also used it for some template guidance when organizing parts of the project documentation. For finding datasets, I used Perplexity.ai to help narrow my search and find more focused, relevant data that aligned with my research question.

---

## 2. Example Prompts Used

* “Why am I getting a ValueError about indices not being aligned in my logistic regression model?”

* “How do I fix a singular matrix error?”

* “Can you help me clean and merge datasets without overlapping columns?”

* “Can you give me a simple template for documenting AI usage?”

* “What datasets are available related to NYC food insecurity and shelter populations?” (used with Perplexity.ai to find more specific data sources)

---

## 3. Final Impact on Project

### Efficiency

Using AI saved me a lot of time. Instead of being stuck on errors for hours, I could troubleshoot faster and keep moving forward with the analysis. It also helped speed up the process of finding useful datasets.

### Clarity

AI helped break down confusing error messages and statistical issues into explanations that made more sense. That made it easier for me to understand what I was doing rather than just copying a fix.

### Technical Debugging

AI was most helpful when I kept running into technical issues during EDA. It helped me work through regression errors, indexing problems, and messy merges so I could clean the data properly.

### Insight Generation

AI didn’t create my research idea, but it helped me explore the data more smoothly. Using Perplexity.ai also helped me discover datasets that strengthened my project and made my analysis more focused.

---

# Ayema – AI Usage Process

## 1. Purpose of AI Use


---

## 2. Example Prompts Used


---


## 3. Contribution to Final Deliverable

Explain how AI supported:

* Visualizations
* Data cleaning
* Interpretation
* Presentation writing

---

# Ibrahima – AI Usage Process

# 1. AI Tools Used

| Tool | Provider | Version | Primary Use |
|------|----------|---------|-------------|
| **Claude** | Anthropic | Claude (Sonnet/Opus) | Code generation, interpretation, documentation |


**Why Claude Was Chosen:**
- Strong capabilities in code generation and explanation
- Clear explanations suitable for non-technical stakeholders

---

# 2. AI Use by Technical Category

## A. SQL Schema Design

### Why AI Was Used
We needed to design an efficient relational database structure (star schema) to integrate four different datasets: Emergency Food Sites, Neighborhood Prioritization, Shelter Census, and NTA Crosswalk. AI helped us think through the relationships and normalization.

### Example Prompt Used
```
I have 4 datasets for NYC food insecurity analysis:
1. Emergency Food Sites (site locations, types, hours)
2. Neighborhood Prioritization (food insecurity rates, unemployment)
3. Shelter Census (families with children by community district)
4. NTA Crosswalk (geographic mappings)

Help me design a star schema database to efficiently store and query this data. 
What should be the fact table and dimension tables?
```

### What AI Suggested
Claude suggested a star schema with:
- **Fact Table:** `fact_food_coverage` containing coverage ratios, site counts, and need indicators per neighborhood
- **Dimension Tables:** `dim_neighborhood`, `dim_food_site`, `dim_time`, `dim_shelter`
- Recommended using NTA (Neighborhood Tabulation Area) as the primary geographic grain
- Suggested creating a crosswalk table to map between CDTA and NTA geographies

### How We Validated
- **Manually reviewed** the schema against our data files to ensure all fields were captured
- **Tested with sample queries** to confirm joins worked correctly
- **Cross-referenced** with NYC Open Data documentation for geographic hierarchy accuracy
- **Modified** the schema to add additional calculated fields (coverage_ratio, is_high_priority) based on the features we engineered.

### What Was Modified
- Added `has_kitchen` and `has_weekend` binary flags (AI didn't initially suggest these)
- Changed the grain from CDTA to NTA after discovering data granularity issues
- Removed suggested time dimension (our analysis was cross-sectional, not time-series initially)

---

## B. Exploratory Data Analysis (EDA)

### Why AI Was Used
AI accelerated the EDA process by generating boilerplate code for visualizations and suggesting appropriate statistical tests based on data characteristics. This allowed us to focus on interpreting results rather than syntax.

### Example Prompts Used

**Prompt 1: Code Generation**
```
I have a pandas DataFrame called 'unified' with columns: food_insecure_percentage, 
unemployment_rate, coverage_ratio, and coverage_category (binary: 0=Low, 1=High).

Write Python code to:
1. Create a correlation heatmap
2. Generate box plots comparing coverage_ratio by coverage_category
3. Check for normality using Shapiro-Wilk test
```

**Prompt 2: Statistical Test Selection**
```
I want to compare coverage ratios between high-priority and low-priority neighborhoods.
- High-priority group: n=50
- Low-priority group: n=147
- Data is NOT normally distributed (Shapiro-Wilk p < 0.001)
- Variances are unequal (Levene's p = 0.005)

What statistical test should I use and why?
```

### What AI Suggested

**For Code Generation:**
- Provided matplotlib/seaborn code for heatmaps and box plots
- Suggested using `scipy.stats.shapiro` for normality testing
- Recommended checking VIF (Variance Inflation Factor) for multicollinearity

**For Statistical Tests:**
- Recommended **Mann-Whitney U test** (non-parametric) over t-test due to non-normality
- Explained that Welch's t-test could be used as a parametric alternative but Mann-Whitney is more appropriate
- Suggested calculating effect size (rank-biserial correlation) alongside p-value

### How We Validated
- **Ran both tests** (Mann-Whitney and Welch's t-test) to compare results
- **Verified assumptions** independently using our own calculations
- **Cross-checked** statistical test selection 
- **Reviewed visualizations** to ensure they accurately represented the data
- **Manually inspected** outliers identified by AI-generated code

### What Was Modified
- Modified color schemes in visualizations to be colorblind-friendly
- Added additional context labels that AI omitted
- Rejected AI's initial suggestion to remove outliers (we kept them as they were valid data points)
- Added confidence intervals that weren't in the original AI-generated code

---

## C. Modeling

### Why AI Was Used
AI helped clarify interpretations of model outputs, explain complex statistical concepts in plain language, and troubleshoot model performance issues. This was particularly valuable for communicating results to non-technical stakeholders.

### Example Prompts Used

**Prompt 1: Model Interpretation**
```
We ran a logistic regression predicting whether a neighborhood is classified as 
low or high coverage area. Here are the coefficients and p-values:

| Feature | Coefficient | P-value |
|---------|-------------|---------|
| food_insecure_percentage | -0.74 | 0.0002 |
| unemployment_rate | +0.81 | <0.0001 |
| is_high_priority | -0.25 | 0.201 |
| vulnerable_population_pct | +0.07 | 0.699 |

Please interpret these results and help explain them clearly to non-technical people.
```

**Prompt 2: Model Comparison**
```
I built 4 time series models to forecast shelter population:
- Baseline (naive): RMSE = 2,047
- AR Model (p=3): RMSE = 838
- ARIMA-style: RMSE = 2,589
- Trend+Seasonal: RMSE = 4,625

Why did the AR model perform best? Why did the others fail?
Explain in simple terms.
```

### What AI Suggested

**For Model Interpretation:**
- Explained that coefficients represent effect of 1 standard deviation increase (since features were scaled)
- Converted coefficients to odds ratios: e^(-0.74) = 0.48, meaning 52% decrease in odds
- Identified which predictors were statistically significant (p < 0.05)
- Created plain-English scenario explanations for each coefficient

**For Model Comparison:**
- Explained that AR model worked best because shelter population is "sticky" (77% persistence)
- Identified that ARIMA failed because differencing removed useful level information when the trend reversed
- Noted that Trend+Seasonal assumed 2023's growth would continue, but 2024 declined


### How We Validated
- **Manually calculated** odds ratios to verify AI's math
- **Ran the code** and verified outputs matched expectations
- **Compared** AI's plain-English explanations with examples
- **Tested** residual diagnostics to confirm residuals were white noise
- **Consulted instructor** to verify interpretation approach was correct

### What Was Modified
- Corrected the direction of one coefficient interpretation (AI initially got the sign wrong for high_shelter_flag)
- Added more context to the "scenario" explanations based on domain knowledge
- Modified confidence interval calculation method based on instructor feedback
- Rejected AI's suggestion to use a more complex model when simpler was more interpretable

---

## D. Summarizing Insights and Findings

### Why AI Was Used
AI helped synthesize complex analytical findings into clear, actionable summaries for different audiences (technical reports, stakeholder presentations, quick updates).

### Example Prompts Used

**Prompt 1: Executive Summary**
```
Based on our analysis:
- Mann-Whitney U test p=0.147 (not significant)
- But high-priority neighborhoods have 40% lower mean coverage ratio
- Logistic regression shows food insecurity predicts LOW coverage (coef=-0.74, p=0.0002)
- Time series forecasts ~31,500 families/month with 97.7% accuracy

Write an executive summary connecting these findings to our research question:
"Do high-need neighborhoods have adequate food assistance coverage?"
```

### What AI Suggested

**For Executive Summary:**
- Structured the findings around the research question
- Noted that "practical significance" exists even without statistical significance
- Connected model outputs to policy recommendations
- Suggested specific action items for policymakers

### How We Validated
- **Fact-checked** all statistics against our actual analysis outputs
- **Reviewed** for accuracy of interpretations
- **Edited** tone to match our voice and style
- **Practiced** presentation to ensure timing was accurate
- **Got feedback** from our instructormbefore finalizing

### What Was Modified
- Simplified some technical language that was still too complex
- Added NYC-specific context that AI didn't know
- Added acknowledgment of limitations that AI omitted

---

# 3. Validation Framework

For all AI outputs, we followed this validation process:

| Step | Description | Applied? |
|------|-------------|----------|
| **1. Sanity Check** | Does the output make logical sense? | Always |
| **2. Code Testing** | Run the code and verify it works | For all code |
| **3. Manual Calculation** | Verify key numbers independently | For statistics |
| **5. Peer Review** | Have team member review output | For final deliverables |
| **6. Instructor Check** | Implement feedback from instructor | For methodology |

---

# 4. What Was Rejected or Significantly Modified

| AI Suggestion | Reason for Rejection/Modification |
|---------------|----------------------------------|
| Remove outliers automatically | Outliers were valid data (wealthy neighborhoods with low food insecurity) |
| Use complex model | Simpler logistic regression was more interpretable for stakeholders |
| Include all 30+ features | Reduced to 5 most meaningful features based on domain knowledge |
| Automated feature selection | Manual selection based on research question alignment |
| Generic visualization colors | Changed to NYC-themed green/accessible colors |
| Technical jargon in summaries | Rewrote in plain English for stakeholder audience |

---

# 5. Risks, Limitations, and Ethical Considerations

## Risks of AI Use in This Project

| Risk | Mitigation |
|------|------------|
| **Incorrect code** | All code was tested before use |
| **Misinterpretation of statistics** | Cross-referenced with textbooks and instructor |
| **Hallucinated facts** | Verified all claims |
| **Over-reliance on AI** | Maintained human decision-making for key choices (Human in the loop) |
| **Reproducibility issues** | Documented all prompts and modifications |

## Limitations

1. **AI doesn't know our specific context** - We had to provide NYC-specific domain knowledge
2. **AI can be confidently wrong** - Required manual verification of all outputs
3. **AI suggestions aren't always optimal** - Sometimes simpler approaches were better
4. **AI can't replace domain expertise** - Human judgment was essential for interpretation

## Ethical Considerations

1. **Transparency** - This document provides full disclosure of AI use
2. **Academic Integrity** - AI was used as a tool, not to replace our own understanding
3. **Bias Awareness** - We checked that AI suggestions didn't introduce or amplify biases
4. **Attribution** - AI assistance is acknowledged; final work represents our analysis

---

# 6. Summary of AI Contribution

| Category | AI Contribution Level | Human Contribution Level |
|----------|----------------------|-------------------------|
| SQL Schema Design | 40% (initial structure) | 60% (refinement, validation) |
| EDA Code | 60% (boilerplate code) | 40% (customization, interpretation) |
| Statistical Tests | 30% (suggestions) | 70% (selection, validation) |
| Model Building | 20% (troubleshooting) | 80% (design, tuning, evaluation) |
| Interpretation | 50% (initial drafts) | 50% (verification, context) |
| Documentation | 60% (drafting) | 40% (editing, accuracy) |
| Final Decisions | 0% | 100% (all decisions were human-made) |

---

# 7. Lessons Learned

1. **AI is a tool and is best to accelerate our process, not replacement** - It speeds up coding but doesn't replace our understanding
2. **Always verify AI outputs** - Even confident-sounding AI can be wrong
3. **Prompts matter** - More specific prompts yield better results
4. **Domain knowledge is essential** - AI needed human context to be useful
5. **Document everything** - This documentation itself was valuable for reflection
