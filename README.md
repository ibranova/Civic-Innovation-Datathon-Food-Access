# Beyond the Pantry
- NYC Food Coverage Predictor (Neighborhood Tabulation Area (NTA)-level)
- Identifying where the Emergency Food Assistance Program (EFAP) supply does not scale with structural vulnerability across NYC neighborhoods.

## Key Takeaway
- In 2024, EFAP site coverage is not evenly aligned with structural vulnerability across NYC Neighborhood Tabulation Areas (NTAs). Among high-priority NTAs (top 25% by structural vulnerability), 56% fall below the city median coverage, and 16% have zero EFAP sites. Statistical testing also shows that coverage differs meaningfully between high-priority and other NTAs (p = 0.001167), supporting the conclusion that misalignment is real rather than noise.


## Critical Research Question
- To what extent does Emergency Food Assistance Program (EFAP) site distribution align with structural vulnerability across NYC Neighborhood Tabulation Areas (NTAs), and can neighborhood structural and service characteristics predict low coverage areas to support targeted resource planning?


### Why this matters
- Food insecurity is not just about hunger. It is shaped by structural conditions like unemployment, household vulnerability, and where families are already under pressure. EFAP is one of NYC’s emergency food supports, so if EFAP supply does not scale with vulnerability, the neighborhoods with the highest need can be systematically underserved.

### Data sources (2024 focus)
- This project integrates multiple NYC civic datasets at the NTA level.
  - NYC Neighborhood Prioritization/vulnerability indicators (structural vulnerability inputs)
  - EFAP site locations and service attributes (food supply)
  - Shelter context indicators (used as added context and in the model as an “extended feature”)
  - NTA geography (for mapping and joins)
- Sources include NYC Open Data and NYC Council published datasets (plus related city documentation).

### Key terminology 
- **Neighborhood Tabulation Area (NTA):** A NYC-defined neighborhood geography used for reporting and planning. Each record in our analysis represents one NTA.
- **Structural vulnerability:** refers to the underlying socioeconomic conditions that make a neighborhood more likely to experience hardship, including food insecurity. In this project, it is measured by the Weighted Score, which combines food insecurity rates with broader risk factors like unemployment and family-related pressures to reflect overall systemic disadvantage.
  - Higher structural vulnerability means a neighborhood faces deeper, more persistent barriers to stable food access.
- **Weighted Score (Structural Vulnerability):** Weighted Score is a composite measure of structural vulnerability, combining food insecurity and broader socioeconomic risk factors (as defined in our project data dictionary).
  - Higher _Weighted Score_ means the neighborhood ranks as more structurally vulnerable.
- **High-Priority NTA:** the top 25% of neighborhoods ranked by Weighted Score.
  - This is a ranking-based definition, not a label we assign manually.
- **Coverage Ratio**: our “supply relative to pressure” metric:
  - Coverage Ratio = Total EFAP Sites ÷ Food Insecurity Percentage
  - It is not a perfect measure of service capacity, but it is a consistent way to compare whether EFAP site presence scales with food insecurity pressure.
- Why we use medians (and quadrant logic)
  - We use median thresholds to divide neighborhoods into clear visual zones without letting a few extreme values dominate the story. Medians allow a clean “above typical vs below typical” comparison across NTAs, which is why we use them in the alignment scatterplot and in the under-served “action” view (Referring to the Dashboard)


#### Analytical approach
- We answer the CRQ in two parts:
  - _Alignment analysis_ (dashboard): Compare structural vulnerability (Weighted Score) vs EFAP coverage (Coverage Ratio) and identify mismatch zones.
  - _Predictive modeling_ (Model): Predict whether an NTA is likely to be a low coverage area using structural + service context features.

#### Dashboard (Tableau) story
🔗 Tableau Public Dashboard (CID Food Access – Dashboard): [https://public.tableau.com/views/CID-foodaccess/Dashboard2](https://public.tableau.com/app/profile/ibrahima.diallo4653/viz/FoodInsecurityAnalysisinNYC/Dashboard3)
- The dashboard is designed as a narrative:
  1. Pressure (structural vulnerability context)
     - The map shows how food insecurity pressure varies across NTAs.
  2. Supply distribution (EFAP presence)
     - The bar chart shows how EFAP sites are distributed across NTAs.
     - With a borough filter, it shows where EFAP supply is concentrated within that borough.
  3. Alignment vs misalignment (4-zone view)
     - We split the city into four zones using medians of:
       - `X-axis`: structural vulnerability (Weighted Score or priority score used for need)
       - `Y-axis`: Coverage Ratio
       - Zones:
         - **Aligned**: higher vulnerability + higher coverage
         - **Under-Served**: higher vulnerability + lower coverage
         - **Over-Served**: lower vulnerability + higher coverage
         - **Lower Priority**: lower vulnerability + lower coverage
  4. Action view (zoom into the underserved zone)
     - A ranked list of high-priority NTAs ordered by Coverage Ratio from lowest to highest.
     - This is meant to answer: “Where should decision makers act first?”
     - _Why there are 0s in the action chart_: A 0% coverage value means an NTA has zero EFAP sites in the EFAP dataset, so the Coverage Ratio becomes zero. Those NTAs represent the most severe supply gaps because there is no EFAP presence at all.

#### KPI definitions 
- **KPI 1: “% of high-priority NTAs under-served”**
  - This tells us: Out of the neighborhoods that are most structurally vulnerable, how many have below-typical EFAP coverage?
  - In our results, 56% of high-priority NTAs are below the city median coverage.
 
- **KPI 2: “Average coverage in high-priority NTAs”**
  - This tells us: On average, what does coverage look like across high-priority NTAs?
  - This can feel like it “contradicts” KPI 1 because averages can be pulled up by a smaller number of better-covered neighborhoods, while KPI 1 is counting how many fall below a typical benchmark (the median). Both can be true at once:
    - The average might look OK, while most high-priority areas are still below the median, meaning coverage is unevenly distributed inside the high-priority group.

- **KPI 3: “% of high-priority NTAs with zero EFAP sites”**
  - This tells us: How many of the most vulnerable neighborhoods have no EFAP sites at all?
  - In our results, 16% of high-priority NTAs have zero EFAP sites.
  - City median coverage matters in this context because the median is the “middle neighborhood” benchmark. Half of NTAs are above it, and half are below it. We use it to avoid extreme outliers and to make the “under-served vs not under-served” classification clear and defensible.



#### Statistical analysis (what we tested and what we found)
- **Hypothesis**:
  - H0 (null): EFAP coverage is the same for high-priority and non-high-priority NTAs.
  - H1 (alternative): EFAP coverage differs between high-priority and non-high-priority NTAs.
- **Variables**
  - Grouping: High Priority vs Not High Priority
  - Outcome: Coverage Ratio

##### Why we used Welch’s t-test**
- We checked assumptions and found: Coverage Ratio is not normally distributed, and group variances are not equal. So we used Welch’s t-test, which is designed for unequal variances. The Welch’s t-test p-value = `0.001167`
  - This is statistically significant, meaning the observed difference is unlikely to be random.
  - Effect size: Cohen’s d = `0.3526`
    - This suggests a small-to-moderate practical difference. The effect is not just “statistically significant”; it is meaningful enough to care about in planning decisions.

###### Interpretation
- Coverage gaps are not evenly spread. High-priority neighborhoods are more likely to have worse coverage patterns, supporting the dashboard story that supply does not reliably scale with vulnerability.







----

## Overview

This project examines food insecurity among children living in New York City family homeless shelters by comparing neighborhood food insecurity prioritization, shelter population concentration, and the availability of emergency food assistance sites.
The goal is to identify whether neighborhoods with the highest shelter-related need are adequately supported with emergency food resources and to provide data-informed recommendations for equitable food access planning.

---

## Critical Research Question

How does the availability of emergency food assistance sites across Neighborhood Tabulation Areas (NTAs) compare for neighborhoods located within community districts with higher shelter population concentrations and higher food insecurity prioritization?

---

## Key Actionable Recommendations

### Policy

Adopt equity-based funding that prioritizes High Priority NTAs (top 25% most structurally vulnerable) so emergency food infrastructure scales proportionally with neighborhood need.

### Resource Allocation

Increase and strategically place EFAP sites in neighborhoods with low coverage ratios to better align food supply with food insecurity intensity.

### Data & Technology

Implement a real-time dashboard using coverage_ratio and weighted_score to monitor whether emergency food infrastructure is proportionally meeting neighborhood vulnerability.

---

## Stakeholders

NYC Department of Homeless Services
Mayor’s Office of Food Policy
Children and families living in NYC shelters

---

## Data Sources

DHS Shelter Census & community district shelter datasets – provide shelter population trends and geographic concentration.
Emergency Food Assistance Program (EFAP) – provides locations and characteristics of emergency food sites.
Neighborhood Food Insecurity Prioritization dataset – measures neighborhood-level food insecurity and vulnerability.

---

## Methodology

### Geographic aggregation at the Neighborhood Tabulation Area (NTA) level

All spatial analyses are conducted at the NTA level to ensure consistency across datasets and to enable neighborhood-level comparisons of food access and shelter-related needs.

### Construction of a coverage ratio to quantify food access relative to need

A coverage ratio is calculated using counts of individuals in shelter systems as a proxy for food insecurity needs, allowing food assistance availability to be evaluated relative to population demand.

### Statistical testing of differences across priority and non-priority areas

Mean difference tests and proportional comparisons are used to assess whether food coverage differs significantly between high-need and lower-need neighborhoods before modeling.

### Logistic regression for neighborhood-level classification

Coverage ratio is binned into categorical outcomes (for example, high vs low coverage), and logistic regression is used to identify neighborhood characteristics associated with inadequate food access.

### Exploratory time-series analysis using ARIMAX

ARIMAX models are explored to examine trends in shelter population demand over time, with results interpreted cautiously and model assumptions explicitly tested and documented.

---

## Tech Stack

Python: Pandas, Scikit-learn, Streamlit
SQL: SQLite
Visualization: Tableau

---

## Key Findings

Food assistance resources are unevenly distributed relative to neighborhoods with the highest concentration of family shelters.

Children in shelter-dense neighborhoods face compounded barriers such as distance, limited hours, and transportation challenges when accessing food.

Data integration and predictive analysis reveal priority zones where targeted investment would most effectively reduce food insecurity risk.

---

## Ethics & Equity

This project centers on children and families experiencing homelessness, recognizing that institutional datasets often reflect system-level perspectives rather than lived experience.
Findings are framed to avoid harm, prevent misinterpretation, and support equitable policy decisions rather than surveillance or deficit narratives.
Since shelter data are not available at the individual shelter-site or exact neighborhood location level, we cannot make causal claims about how specific food programs affect shelter residents.

---

## Links to Final Deliverables

Interactive Tableau Dashboard: [WIP]

Local Streamlit Application: [WIP]

Technical Report (PDF):
[Link to deliverables/Deliverable_Report.pdf]

---

## Repository Navigation

sql/data_processing.sql — Star Schema construction and ETL

python/notebooks/eda.ipynb — Visual EDA and statistical analysis

python/src/model_training.py — Final model code and evaluation

ai_process.md — Documentation on ethical AI usage

---

## Data Source Attribution

I acknowledge and appreciate the work of the New York City Open Data program and associated municipal agencies in making these datasets publicly available for civic research and analysis.

---

## APA References

Coalition for the Homeless. (n.d.). Why are so many people homeless?
Davis, A. Y. (2003). Are prisons obsolete? Seven Stories Press.
Feeding America. (n.d.). What is food insecurity?
Gundersen, C., & Ziliak, J. P. (2018). Food insecurity research in the United States: Where we have been and where we need to go. *Applied Economic Perspectives and Policy, 40*(1), 119–135.
Institute for Children, Poverty, and Homelessness. (n.d.-a). Federal SNAP changes threaten stability for NYC families in shelters.
Institute for Children, Poverty, and Homelessness. (n.d.-b). Family homelessness 101: New York City – Impact on children.
Mayor’s Office of Food Policy. (n.d.-a). About the Mayor’s Office of Food Policy.
Mayor’s Office of Food Policy. (n.d.-b). Food Forward NYC.
New York State Office of the Comptroller. (2023). Federal actions threaten to exacerbate rising food insecurity.
NY1. (2024, May 29). Child hunger rates continue to rise in New York City.
U.S. Department of Agriculture Economic Research Service. (n.d.). Definitions of food security.

---


