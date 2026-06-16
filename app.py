import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Intelligence | Telecom",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0D1117;
    color: #E6EDF3;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161B22;
    border-right: 1px solid #21262D;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #8B949E;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}

/* Main background */
.main .block-container {
    background: #0D1117;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Page title */
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.page-subtitle {
    color: #8B949E;
    font-size: 0.9rem;
    margin-top: 2px;
    margin-bottom: 1.5rem;
}

/* KPI Cards */
.kpi-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.red::before   { background: linear-gradient(90deg, #FF6B6B, #FF8E53); }
.kpi-card.amber::before { background: linear-gradient(90deg, #F6C90E, #FF8E53); }
.kpi-card.green::before { background: linear-gradient(90deg, #3FB950, #56CFE1); }
.kpi-card.blue::before  { background: linear-gradient(90deg, #58A6FF, #7C3AED); }

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8B949E;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #E6EDF3;
    line-height: 1;
}
.kpi-sub {
    font-size: 12px;
    color: #8B949E;
    margin-top: 5px;
}

/* Section headers */
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #E6EDF3;
    border-left: 3px solid #58A6FF;
    padding-left: 10px;
    margin: 1.5rem 0 1rem 0;
}

/* Risk badge */
.risk-high   { background:#FF6B6B22; color:#FF6B6B; border:1px solid #FF6B6B55; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.risk-medium { background:#F6C90E22; color:#F6C90E; border:1px solid #F6C90E55; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.risk-low    { background:#3FB95022; color:#3FB950; border:1px solid #3FB95055; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:600; }

/* Simulator result card */
.sim-card {
    background: linear-gradient(135deg, #161B22, #1C2333);
    border: 1px solid #30363D;
    border-radius: 14px;
    padding: 24px;
    margin-top: 12px;
}
.sim-big {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #3FB950;
    line-height: 1;
}

/* Divider */
hr { border-color: #21262D; margin: 1.5rem 0; }

/* Plotly chart background fix */
.js-plotly-plot { border-radius: 12px; }

/* Streamlit element overrides */
div[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 14px 18px;
}
.stSelectbox label, .stSlider label, .stMultiSelect label {
    color: #8B949E !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.stSlider .stMarkdown { color: #8B949E; }
</style>
""", unsafe_allow_html=True)


# ── Data loading & feature engineering ───────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
    df = pd.read_csv(url)

    # Clean TotalCharges
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"])

    # Binary churn
    df["Churned"] = (df["Churn"] == "Yes").astype(int)

    # Risk scoring (SQL-style rule-based)
    def risk_score(row):
        score = 0
        if row["Contract"] == "Month-to-month": score += 3
        elif row["Contract"] == "One year":     score += 1
        if row["tenure"] <= 12:                 score += 2
        elif row["tenure"] <= 24:               score += 1
        if row["MonthlyCharges"] >= 65:         score += 2
        elif row["MonthlyCharges"] >= 45:       score += 1
        if row["InternetService"] == "Fiber optic": score += 1
        if row["TechSupport"] == "No":          score += 1
        if row["PaymentMethod"] == "Electronic check": score += 1
        return score

    df["RiskScore"] = df.apply(risk_score, axis=1)
    df["RiskTier"] = pd.cut(
        df["RiskScore"],
        bins=[-1, 3, 6, 10],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    )

    return df

df = load_data()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 CHURN INTELLIGENCE")
    st.markdown("IBM Telco Dataset · 7,032 customers")
    st.markdown("---")

    st.markdown("**NAVIGATION**")
    page = st.radio(
        "", ["📊 Risk Dashboard", "💰 Revenue Simulator"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**FILTERS**")

    contract_filter = st.multiselect(
        "Contract Type",
        options=df["Contract"].unique().tolist(),
        default=df["Contract"].unique().tolist()
    )

    internet_filter = st.multiselect(
        "Internet Service",
        options=df["InternetService"].unique().tolist(),
        default=df["InternetService"].unique().tolist()
    )

    tenure_range = st.slider(
        "Tenure (months)",
        min_value=int(df["tenure"].min()),
        max_value=int(df["tenure"].max()),
        value=(0, 72)
    )

    charges_range = st.slider(
        "Monthly Charges ($)",
        min_value=float(df["MonthlyCharges"].min()),
        max_value=float(df["MonthlyCharges"].max()),
        value=(18.0, 120.0)
    )

    st.markdown("---")
    st.markdown("**RISK TIER**")
    risk_filter = st.multiselect(
        "Show tiers",
        options=["High Risk", "Medium Risk", "Low Risk"],
        default=["High Risk", "Medium Risk", "Low Risk"]
    )

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df[
    (df["Contract"].isin(contract_filter)) &
    (df["InternetService"].isin(internet_filter)) &
    (df["tenure"].between(*tenure_range)) &
    (df["MonthlyCharges"].between(*charges_range)) &
    (df["RiskTier"].isin(risk_filter))
].copy()

# ── Computed metrics ──────────────────────────────────────────────────────────
total_customers   = len(filtered)
churned           = filtered["Churned"].sum()
churn_rate        = churned / total_customers * 100 if total_customers else 0
monthly_rev_lost  = filtered[filtered["Churned"] == 1]["MonthlyCharges"].sum()
annual_rev_lost   = monthly_rev_lost * 12
high_risk_count   = (filtered["RiskTier"] == "High Risk").sum()
high_risk_active  = filtered[(filtered["RiskTier"] == "High Risk") & (filtered["Churned"] == 0)]
recoverable_rev   = high_risk_active["MonthlyCharges"].sum()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: RISK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Risk Dashboard":

    st.markdown('<div class="page-title">Customer Churn Risk Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Real-time risk scoring across 7,032 IBM Telco customers · Adjust filters to explore segments</div>', unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card red">
            <div class="kpi-label">Churn Rate</div>
            <div class="kpi-value">{churn_rate:.1f}%</div>
            <div class="kpi-sub">{churned:,} of {total_customers:,} customers lost</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card amber">
            <div class="kpi-label">Annual Revenue Lost</div>
            <div class="kpi-value">${annual_rev_lost:,.0f}</div>
            <div class="kpi-sub">From churned customers</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-label">High Risk Customers</div>
            <div class="kpi-value">{high_risk_count:,}</div>
            <div class="kpi-sub">{high_risk_count/total_customers*100:.1f}% of filtered segment</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-label">Recoverable / Month</div>
            <div class="kpi-value">${recoverable_rev:,.0f}</div>
            <div class="kpi-sub">Active high-risk customers</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 2: Risk distribution + Churn by contract ─────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Risk Tier Distribution</div>', unsafe_allow_html=True)
        tier_counts = filtered["RiskTier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Count"]
        color_map = {"High Risk": "#FF6B6B", "Medium Risk": "#F6C90E", "Low Risk": "#3FB950"}
        fig_donut = go.Figure(go.Pie(
            labels=tier_counts["Tier"],
            values=tier_counts["Count"],
            hole=0.65,
            marker_colors=[color_map.get(t, "#8B949E") for t in tier_counts["Tier"]],
            textinfo="label+percent",
            textfont=dict(color="#E6EDF3", size=12),
            hovertemplate="<b>%{label}</b><br>%{value:,} customers<br>%{percent}<extra></extra>"
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_customers:,}</b><br><span style='font-size:11px'>customers</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#E6EDF3"),
            align="center"
        )
        fig_donut.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Churn Rate by Contract Type</div>', unsafe_allow_html=True)
        contract_churn = filtered.groupby("Contract")["Churned"].agg(["sum", "count"]).reset_index()
        contract_churn.columns = ["Contract", "Churned", "Total"]
        contract_churn["Rate"] = contract_churn["Churned"] / contract_churn["Total"] * 100
        fig_bar = go.Figure(go.Bar(
            x=contract_churn["Contract"],
            y=contract_churn["Rate"],
            marker_color=["#FF6B6B", "#F6C90E", "#3FB950"],
            text=contract_churn["Rate"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color="#E6EDF3", size=12),
            hovertemplate="<b>%{x}</b><br>Churn Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_bar.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            yaxis=dict(gridcolor="#21262D", title="Churn Rate (%)", color="#8B949E"),
            xaxis=dict(color="#8B949E"),
            margin=dict(t=30, b=10, l=10, r=10),
            height=300,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Row 3: Churn by tenure + Monthly charges ──────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-header">Churn Rate by Tenure Band</div>', unsafe_allow_html=True)
        filtered["TenureBand"] = pd.cut(
            filtered["tenure"],
            bins=[0, 12, 24, 36, 48, 60, 72],
            labels=["0–12m", "13–24m", "25–36m", "37–48m", "49–60m", "61–72m"]
        )
        tenure_churn = filtered.groupby("TenureBand", observed=True)["Churned"].agg(["sum","count"]).reset_index()
        tenure_churn["Rate"] = tenure_churn["sum"] / tenure_churn["count"] * 100
        fig_line = go.Figure(go.Scatter(
            x=tenure_churn["TenureBand"].astype(str),
            y=tenure_churn["Rate"],
            mode="lines+markers",
            line=dict(color="#58A6FF", width=2.5),
            marker=dict(size=8, color="#58A6FF", line=dict(color="#0D1117", width=2)),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.08)",
            hovertemplate="<b>%{x}</b><br>Churn Rate: %{y:.1f}%<extra></extra>"
        ))
        fig_line.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            yaxis=dict(gridcolor="#21262D", title="Churn Rate (%)", color="#8B949E"),
            xaxis=dict(color="#8B949E"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header">Monthly Charges: Churned vs Retained</div>', unsafe_allow_html=True)
        fig_box = go.Figure()
        for label, color in [("Yes", "#FF6B6B"), ("No", "#3FB950")]:
            sub = filtered[filtered["Churn"] == label]["MonthlyCharges"]
            fig_box.add_trace(go.Box(
                y=sub, name="Churned" if label == "Yes" else "Retained",
                marker_color=color,
                line_color=color,
                fillcolor=f"rgba({','.join(str(int(color.lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.2)",
                hovertemplate=f"<b>{'Churned' if label=='Yes' else 'Retained'}</b><br>$%{{y:.0f}}<extra></extra>"
            ))
        fig_box.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            yaxis=dict(gridcolor="#21262D", title="Monthly Charges ($)", color="#8B949E"),
            xaxis=dict(color="#8B949E"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True,
            legend=dict(bgcolor="#161B22", bordercolor="#21262D")
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Row 4: High-risk customer table ──────────────────────────────────────
    st.markdown('<div class="section-header">High-Risk Active Customers (Top 50 by Revenue at Stake)</div>', unsafe_allow_html=True)

    display_cols = ["customerID", "Contract", "tenure", "MonthlyCharges", "InternetService", "TechSupport", "PaymentMethod", "RiskScore", "RiskTier"]
    hr_table = high_risk_active[display_cols].sort_values("MonthlyCharges", ascending=False).head(50).copy()
    hr_table.columns = ["Customer ID", "Contract", "Tenure (m)", "Monthly $", "Internet", "Tech Support", "Payment", "Risk Score", "Tier"]

    def style_tier(val):
        if val == "High Risk":   return "color: #FF6B6B; font-weight: 600;"
        if val == "Medium Risk": return "color: #F6C90E; font-weight: 600;"
        return "color: #3FB950; font-weight: 600;"

    styled = hr_table.style\
        .applymap(style_tier, subset=["Tier"])\
        .format({"Monthly $": "${:.0f}", "Risk Score": "{:.0f}"})\
        .set_properties(**{
            "background-color": "#161B22",
            "color": "#E6EDF3",
            "border-color": "#21262D",
            "font-size": "13px"
        })

    st.dataframe(styled, use_container_width=True, height=320)

    # ── Row 5: Churn drivers heatmap ─────────────────────────────────────────
    st.markdown('<div class="section-header">What Drives Churn? — Service Feature Analysis</div>', unsafe_allow_html=True)

    if filtered.empty:
        st.info("No data available for the selected filters to generate Feature Analysis.")
    else:
        features = ["PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
                    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]

        churn_rates = []
        for feat in features:
            rate = filtered.groupby(feat)["Churned"].mean() * 100
            for val, r in rate.items():
                churn_rates.append({"Feature": feat, "Value": val, "Churn Rate": r})

        cr_df = pd.DataFrame(churn_rates)
        
        if not cr_df.empty:
            pivot = cr_df.pivot(index="Feature", columns="Value", values="Churn Rate")

            fig_heat = go.Figure(go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale=[[0,"#0D1117"],[0.5,"#7C3AED"],[1,"#FF6B6B"]],
                text=[[f"{v:.1f}%" if pd.notna(v) else "" for v in row] for row in pivot.values],
                texttemplate="%{text}",
                textfont=dict(size=11, color="#E6EDF3"),
                hovertemplate="<b>%{y}</b> → %{x}<br>Churn Rate: %{z:.1f}%<extra></extra>",
                showscale=True,
                colorbar=dict(
                    title=dict(text="Churn %", font=dict(color="#8B949E")),
                    tickfont=dict(color="#8B949E")
                )
            ))
            fig_heat.update_layout(
                paper_bgcolor="#161B22", plot_bgcolor="#161B22",
                font_color="#E6EDF3",
                xaxis=dict(color="#8B949E"),
                yaxis=dict(color="#8B949E"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=340,
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("No data available for the selected filters to generate Feature Analysis.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: REVENUE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="page-title">Revenue Impact Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Model the financial return of retention interventions · Adjust assumptions to see ROI in real time</div>', unsafe_allow_html=True)

    # ── Current state snapshot ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Current State — Revenue at Risk</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="kpi-card red">
            <div class="kpi-label">Annual Revenue Lost</div>
            <div class="kpi-value">${annual_rev_lost:,.0f}</div>
            <div class="kpi-sub">From {churned:,} churned customers</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        avg_monthly = filtered[filtered["Churned"]==1]["MonthlyCharges"].mean()
        avg_ltv = avg_monthly * 24
        st.markdown(f"""<div class="kpi-card amber">
            <div class="kpi-label">Avg Lost LTV (24m)</div>
            <div class="kpi-value">${avg_ltv:,.0f}</div>
            <div class="kpi-sub">Per churned customer</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="kpi-card blue">
            <div class="kpi-label">High-Risk Active</div>
            <div class="kpi-value">{len(high_risk_active):,}</div>
            <div class="kpi-sub">${recoverable_rev:,.0f}/mo at stake</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        high_risk_churn_rate = filtered[filtered["RiskTier"]=="High Risk"]["Churned"].mean()*100
        st.markdown(f"""<div class="kpi-card red">
            <div class="kpi-label">High-Risk Churn Rate</div>
            <div class="kpi-value">{high_risk_churn_rate:.1f}%</div>
            <div class="kpi-sub">Validated against actual churn</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Simulator controls ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Intervention Parameters</div>', unsafe_allow_html=True)

    sim_c1, sim_c2, sim_c3 = st.columns(3)

    with sim_c1:
        target_tier = st.selectbox(
            "Target Segment",
            ["High Risk only", "High + Medium Risk", "All customers"],
        )
        if target_tier == "High Risk only":
            pool = filtered[(filtered["RiskTier"]=="High Risk") & (filtered["Churned"]==0)]
        elif target_tier == "High + Medium Risk":
            pool = filtered[(filtered["RiskTier"].isin(["High Risk","Medium Risk"])) & (filtered["Churned"]==0)]
        else:
            pool = filtered[filtered["Churned"]==0]

    with sim_c2:
        retention_rate = st.slider(
            "Retention Success Rate (%)",
            min_value=5, max_value=80, value=30, step=5,
            help="What % of targeted customers can you successfully retain?"
        )

    with sim_c3:
        cost_per_customer = st.slider(
            "Cost per Customer ($)",
            min_value=0, max_value=100, value=10, step=5,
            help="Discount, offer, or outreach cost per customer contacted"
        )

    ltv_months = st.slider(
        "LTV Horizon (months)",
        min_value=6, max_value=48, value=24, step=6,
        help="How many months of retained revenue to count as the win?"
    )

    # ── Simulation calculations ───────────────────────────────────────────────
    n_targeted        = len(pool)
    n_retained        = int(n_targeted * retention_rate / 100)
    avg_monthly_pool  = pool["MonthlyCharges"].mean() if len(pool) else 0
    revenue_saved     = n_retained * avg_monthly_pool * ltv_months
    total_cost        = n_targeted * cost_per_customer
    net_benefit       = revenue_saved - total_cost
    roi_pct           = (net_benefit / total_cost * 100) if total_cost > 0 else float("inf")
    monthly_saved     = n_retained * avg_monthly_pool

    # ── Results ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Simulation Results</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"""<div class="kpi-card green">
            <div class="kpi-label">Customers Retained</div>
            <div class="kpi-value">{n_retained:,}</div>
            <div class="kpi-sub">of {n_targeted:,} targeted</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""<div class="kpi-card green">
            <div class="kpi-label">Revenue Saved ({ltv_months}m)</div>
            <div class="kpi-value">${revenue_saved:,.0f}</div>
            <div class="kpi-sub">${monthly_saved:,.0f} / month</div>
        </div>""", unsafe_allow_html=True)
    with r3:
        st.markdown(f"""<div class="kpi-card amber">
            <div class="kpi-label">Intervention Cost</div>
            <div class="kpi-value">${total_cost:,.0f}</div>
            <div class="kpi-sub">${cost_per_customer} × {n_targeted:,} customers</div>
        </div>""", unsafe_allow_html=True)
    with r4:
        roi_color = "green" if roi_pct > 0 else "red"
        st.markdown(f"""<div class="kpi-card {roi_color}">
            <div class="kpi-label">ROI</div>
            <div class="kpi-value">{"∞" if total_cost==0 else f"{roi_pct:.0f}%"}</div>
            <div class="kpi-sub">Net: ${net_benefit:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    # ── ROI Sensitivity chart ─────────────────────────────────────────────────
    st.markdown("---")
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown('<div class="section-header">ROI vs Retention Rate</div>', unsafe_allow_html=True)
        rates = list(range(5, 85, 5))
        rois  = []
        for r in rates:
            nr  = int(n_targeted * r / 100)
            rev = nr * avg_monthly_pool * ltv_months
            roi = (rev - total_cost) / total_cost * 100 if total_cost > 0 else rev
            rois.append(roi)

        fig_roi = go.Figure()
        fig_roi.add_hline(y=0, line_color="#FF6B6B", line_dash="dot", line_width=1.5, annotation_text="Break-even", annotation_font_color="#FF6B6B")
        fig_roi.add_trace(go.Scatter(
            x=rates, y=rois,
            mode="lines+markers",
            line=dict(color="#3FB950", width=2.5),
            marker=dict(size=6, color="#3FB950"),
            fill="tozeroy",
            fillcolor="rgba(63,185,80,0.08)",
            hovertemplate="<b>Retention: %{x}%</b><br>ROI: %{y:.0f}%<extra></extra>"
        ))
        fig_roi.add_trace(go.Scatter(
            x=[retention_rate], y=[roi_pct],
            mode="markers",
            marker=dict(size=13, color="#58A6FF", symbol="circle", line=dict(color="#0D1117", width=2)),
            name="Current setting",
            hovertemplate=f"<b>Your setting: {retention_rate}%</b><br>ROI: {roi_pct:.0f}%<extra></extra>"
        ))
        fig_roi.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            xaxis=dict(title="Retention Rate (%)", gridcolor="#21262D", color="#8B949E"),
            yaxis=dict(title="ROI (%)", gridcolor="#21262D", color="#8B949E"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    with col_f:
        st.markdown('<div class="section-header">Revenue Saved by LTV Horizon</div>', unsafe_allow_html=True)
        horizons   = [6, 12, 18, 24, 30, 36, 42, 48]
        rev_values = [n_retained * avg_monthly_pool * h for h in horizons]
        cost_line  = [total_cost] * len(horizons)

        fig_ltv = go.Figure()
        fig_ltv.add_trace(go.Bar(
            x=horizons, y=rev_values,
            marker_color="#58A6FF",
            name="Revenue Saved",
            hovertemplate="<b>%{x} months</b><br>$%{y:,.0f}<extra></extra>"
        ))
        fig_ltv.add_trace(go.Scatter(
            x=horizons, y=cost_line,
            mode="lines",
            line=dict(color="#FF6B6B", dash="dot", width=2),
            name="Intervention Cost",
            hovertemplate=f"Intervention cost: ${total_cost:,.0f}<extra></extra>"
        ))
        fig_ltv.update_layout(
            paper_bgcolor="#161B22", plot_bgcolor="#161B22",
            font_color="#E6EDF3",
            xaxis=dict(title="LTV Horizon (months)", gridcolor="#21262D", color="#8B949E"),
            yaxis=dict(title="Revenue ($)", gridcolor="#21262D", color="#8B949E"),
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            legend=dict(bgcolor="#161B22", bordercolor="#21262D", font=dict(color="#8B949E"))
        )
        st.plotly_chart(fig_ltv, use_container_width=True)

    # ── Cost sweep table ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Cost Sensitivity Table — ROI at Different Cost per Customer</div>', unsafe_allow_html=True)

    costs       = [0, 5, 10, 15, 20, 30, 50, 75, 100]
    ret_rates   = [10, 20, 30, 40, 50]
    table_rows  = []
    for c in costs:
        row = {"Cost/Customer ($)": f"${c}"}
        for rr in ret_rates:
            nr  = int(n_targeted * rr / 100)
            rev = nr * avg_monthly_pool * ltv_months
            tc  = n_targeted * c
            roi = (rev - tc) / tc * 100 if tc > 0 else float("inf")
            row[f"{rr}% retained"] = f"{roi:.0f}%" if tc > 0 else "∞"
        table_rows.append(row)

    sens_df = pd.DataFrame(table_rows)

    def color_roi(val):
        try:
            v = float(val.replace("%","").replace("∞","9999"))
            if v > 200:  return "color: #3FB950; font-weight:600"
            if v > 0:    return "color: #F6C90E"
            return "color: #FF6B6B"
        except:
            return ""

    styled_sens = sens_df.style.applymap(
        color_roi, subset=[c for c in sens_df.columns if "retained" in c]
    ).set_properties(**{
        "background-color": "#161B22",
        "color": "#E6EDF3",
        "border-color": "#21262D",
        "font-size": "13px"
    })
    st.dataframe(styled_sens, use_container_width=True, height=340)

    # ── Business recommendation ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Business Recommendation</div>', unsafe_allow_html=True)

    if roi_pct > 300:
        rec_color = "#3FB950"; rec_icon = "✅"; rec_label = "STRONG BUY"
        rec_text = f"At a {retention_rate}% success rate with ${cost_per_customer}/customer spend, this intervention yields a <b>{roi_pct:.0f}% ROI</b> over {ltv_months} months. Recommend immediate deployment targeting {n_targeted:,} customers in the {target_tier} segment."
    elif roi_pct > 100:
        rec_color = "#58A6FF"; rec_icon = "👍"; rec_label = "RECOMMENDED"
        rec_text = f"Positive ROI of <b>{roi_pct:.0f}%</b> over {ltv_months} months. Feasible — refine targeting or test at smaller scale to validate retention rate assumption before full rollout."
    elif roi_pct > 0:
        rec_color = "#F6C90E"; rec_icon = "⚠️"; rec_label = "MARGINAL"
        rec_text = f"ROI of <b>{roi_pct:.0f}%</b> is positive but slim. Consider reducing intervention cost below ${cost_per_customer} or improving the retention offer to increase success rate before committing."
    else:
        rec_color = "#FF6B6B"; rec_icon = "❌"; rec_label = "NOT VIABLE"
        rec_text = f"Negative ROI at current parameters. Reduce cost per customer or target only the highest-value segment to find a viable configuration."

    st.markdown(f"""
    <div style="background:#161B22; border:1px solid {rec_color}44; border-left:4px solid {rec_color};
                border-radius:10px; padding:20px 24px; margin-top:8px;">
        <div style="color:{rec_color}; font-weight:700; font-size:13px; letter-spacing:1px; margin-bottom:8px;">
            {rec_icon} {rec_label}
        </div>
        <div style="color:#E6EDF3; font-size:14px; line-height:1.7;">{rec_text}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="text-align:center; color:#484F58; font-size:12px; padding: 8px 0;">
    Churn Intelligence Dashboard · IBM Telco Dataset · Built with Streamlit + Plotly
    · <a href="https://github.com/Sasikumar-19/Customer_Churn_Analysis_Revnue_Impact_Simulator"
        style="color:#58A6FF; text-decoration:none;">GitHub →</a>
</div>
""", unsafe_allow_html=True)
