import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from auth import login_page, logout, is_authenticated, get_user_info


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not is_authenticated():
    login_page()
    st.stop()

# ── Chart layout helper ───────────────────────────────────────────────────────
def chart_layout():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="#1e293b", showgrid=True),
        yaxis=dict(gridcolor="#1e293b", showgrid=True),
    )

# ── KPI card helper ───────────────────────────────────────────────────────────
def kpi(label, value, delta, prefix="", suffix=""):
    arrow = "▲" if delta >= 0 else "▼"
    color = "#22c55e" if delta >= 0 else "#ef4444"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{prefix}{value:,}{suffix}</div>
        <div class="kpi-delta" style="color:{color}">{arrow} {abs(delta):.1f}%</div>
    </div>"""

# ── Data generation ───────────────────────────────────────────────────────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    months = pd.date_range("2024-01-01", periods=12, freq="MS")
    mrr        = [4200,4800,5300,6100,6800,7500,8200,8900,9600,10400,11200,12100]
    users      = [320,380,450,530,610,700,795,890,990,1100,1215,1340]
    churn      = [3.8,3.5,3.2,3.0,2.8,2.6,2.5,2.4,2.3,2.2,2.1,2.0]
    new_users  = [45,72,85,95,102,112,118,125,132,140,148,158]
    dau        = [180,210,250,295,340,390,445,498,555,615,680,750]
    df_monthly = pd.DataFrame({
        "Month": months, "MRR": mrr, "Users": users,
        "Churn %": churn, "New Users": new_users, "DAU": dau,
        "ARR": [m*12 for m in mrr],
        "ARPU": [round(m/u,2) for m,u in zip(mrr,users)],
    })
    df_plans = pd.DataFrame({
        "Plan":  ["Starter","Pro","Business","Enterprise"],
        "Users": [480,520,240,100],
        "MRR":   [2400,7800,7200,9500],
    })
    features = ["Dashboard","Reports","API","Integrations","Exports","Alerts"]
    cohorts  = ["Jan","Feb","Mar","Apr","May","Jun"]
    df_heat  = pd.DataFrame(
        np.random.randint(30,100,size=(len(cohorts),len(features))),
        index=cohorts, columns=features
    )
    days     = pd.date_range(end=datetime.today(), periods=30, freq="D")
    signups  = np.random.poisson(lam=5, size=30) + np.linspace(3,7,30).astype(int)
    df_daily = pd.DataFrame({"Date": days, "Signups": signups})
    return df_monthly, df_plans, df_heat, df_daily

df_monthly, df_plans, df_heat, df_daily = generate_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
user = get_user_info()
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-profile">
        <img src="{user.get('picture','https://ui-avatars.com/api/?name=User')}"
             class="avatar" alt="avatar">
        <div class="sidebar-name">{user.get('name','User')}</div>
        <div class="sidebar-email">{user.get('email','')}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", ["📊 Overview","💰 Revenue","👥 Users","📉 Churn","🔥 Engagement"])
    st.markdown("---")
    date_range = st.select_slider("Date Range", options=["3M","6M","12M"], value="12M")
    n  = {"3M":3,"6M":6,"12M":12}[date_range]
    df = df_monthly.tail(n)
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.markdown('<h1 class="page-title">📊 SaaS Overview</h1>', unsafe_allow_html=True)
    cards = "".join([
        kpi("Monthly Recurring Revenue", df["MRR"].iloc[-1],  8.5, "$"),
        kpi("Total Users",               df["Users"].iloc[-1], 10.3),
        kpi("Annual Recurring Revenue",  df["ARR"].iloc[-1],  8.5, "$"),
        kpi("Avg Revenue Per User",      df["ARPU"].iloc[-1], -1.2, "$"),
    ])
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(df, x="Month", y="MRR", title="MRR Growth",
                      color_discrete_sequence=["#6366f1"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(df, x="Month", y="New Users", title="New Signups / Month",
                     color_discrete_sequence=["#22c55e"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        fig = px.pie(df_plans, names="Plan", values="MRR", title="Revenue by Plan",
                     color_discrete_sequence=["#6366f1","#8b5cf6","#a78bfa","#c4b5fd"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.line(df, x="Month", y=["MRR","ARR"], title="MRR vs ARR",
                      color_discrete_sequence=["#6366f1","#f59e0b"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)

# ── REVENUE ───────────────────────────────────────────────────────────────────
elif page == "💰 Revenue":
    st.markdown('<h1 class="page-title">💰 Revenue Analytics</h1>', unsafe_allow_html=True)
    cards = "".join([
        kpi("Current MRR", df["MRR"].iloc[-1],  8.5, "$"),
        kpi("Current ARR", df["ARR"].iloc[-1],  8.5, "$"),
        kpi("ARPU",        df["ARPU"].iloc[-1], -1.2, "$"),
        kpi("Peak MRR",    df["MRR"].max(),      0.0, "$"),
    ])
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    fig = px.bar(df_plans, x="Plan", y="MRR", text="MRR", title="MRR by Plan",
                 color="Plan", color_discrete_sequence=["#6366f1","#8b5cf6","#a78bfa","#c4b5fd"])
    fig.update_traces(texttemplate="$%{text:,}", textposition="outside")
    fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.area(df, x="Month", y="ARR", title="ARR Trend",
                      color_discrete_sequence=["#f59e0b"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(df, x="Month", y="ARPU", title="ARPU Trend", markers=True,
                      color_discrete_sequence=["#ec4899"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)

# ── USERS ─────────────────────────────────────────────────────────────────────
elif page == "👥 Users":
    st.markdown('<h1 class="page-title">👥 User Analytics</h1>', unsafe_allow_html=True)
    dau_val = df["DAU"].iloc[-1]; mau_val = df["Users"].iloc[-1]
    cards = "".join([
        kpi("Total Users",    mau_val, 10.3),
        kpi("New This Month", df["New Users"].iloc[-1], 5.4),
        kpi("DAU",            dau_val, 3.2),
        kpi("DAU/MAU Ratio",  round(dau_val/mau_val*100,1), 1.1, "", "%"),
    ])
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="Month", y="Users", title="Total Users Growth",
                      markers=True, color_discrete_sequence=["#6366f1"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(df_daily, x="Date", y="Signups", title="Daily Signups (Last 30 days)",
                     color_discrete_sequence=["#22c55e"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    fig = px.bar(df_plans, x="Plan", y="Users", text="Users", title="Users by Plan",
                 color="Plan", color_discrete_sequence=["#6366f1","#8b5cf6","#a78bfa","#c4b5fd"])
    fig.update_traces(textposition="outside")
    fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)

# ── CHURN ─────────────────────────────────────────────────────────────────────
elif page == "📉 Churn":
    st.markdown('<h1 class="page-title">📉 Churn Analysis</h1>', unsafe_allow_html=True)
    cc = df["Churn %"].iloc[-1]; pc = df["Churn %"].iloc[-2]
    lost = round(df["Users"].iloc[-1] * cc / 100)
    ltv  = round(df["ARPU"].iloc[-1] / (cc / 100))
    cards = "".join([
        kpi("Churn Rate",     cc,               -(pc-cc), "", "%"),
        kpi("Lost Users/Mo",  lost,             -(pc-cc)),
        kpi("Customer LTV",   ltv,               5.2, "$"),
        kpi("Retention Rate", round(100-cc, 1), (pc-cc),  "", "%"),
    ])
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="Month", y="Churn %", title="Monthly Churn Rate (%)",
                      markers=True, color_discrete_sequence=["#ef4444"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c2:
        cbp = pd.DataFrame({"Plan":["Starter","Pro","Business","Enterprise"],
                            "Churn":[4.5,2.1,1.8,0.9]})
        fig = px.bar(cbp, x="Plan", y="Churn", title="Churn Rate by Plan (%)",
                     color="Plan",
                     color_discrete_sequence=["#ef4444","#f97316","#f59e0b","#22c55e"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Cohort Retention (%)")
    cohort_data = {}
    for i in range(6):
        ml = (datetime.today()-timedelta(days=30*i)).strftime("%b %Y")
        ret = [100]+sorted(np.random.randint(60,99,size=5).tolist(),reverse=True)
        cohort_data[ml] = ret[:6-i]+["-"]*i
    st.dataframe(pd.DataFrame(cohort_data,
                 index=["M0","M1","M2","M3","M4","M5"]).T,
                 use_container_width=True)

# ── ENGAGEMENT ────────────────────────────────────────────────────────────────
elif page == "🔥 Engagement":
    st.markdown('<h1 class="page-title">🔥 Engagement & Usage</h1>', unsafe_allow_html=True)
    dau_v = df["DAU"].iloc[-1]; mau_v = df["Users"].iloc[-1]
    wau_v = round(dau_v * 4.2)
    cards = "".join([
        kpi("DAU",        dau_v, 3.2),
        kpi("WAU",        wau_v, 2.8),
        kpi("MAU",        mau_v, 10.3),
        kpi("Stickiness", round(dau_v/mau_v*100,1), 1.5, "", "%"),
    ])
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="Month", y="DAU", title="Daily Active Users Trend",
                      markers=True, color_discrete_sequence=["#f59e0b"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    with c2:
        sd = pd.DataFrame({"Duration":["<1 min","1-5 min","5-15 min","15-30 min",">30 min"],
                           "Users":[80,210,380,290,140]})
        fig = px.bar(sd, x="Duration", y="Users",
                     title="Session Duration Distribution",
                     color_discrete_sequence=["#8b5cf6"])
        fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Feature Adoption Heatmap (%)")
    fig = px.imshow(df_heat, text_auto=True, color_continuous_scale="Purples",
                    title="Feature Usage by Cohort (%)")
    fig.update_layout(**chart_layout()); st.plotly_chart(fig, use_container_width=True)
