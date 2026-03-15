import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mortgage Projection",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --ink:       #0f1117;
    --paper:     #faf8f4;
    --cream:     #f2ede4;
    --rust:      #c84b31;
    --gold:      #d4a853;
    --sage:      #4a7c59;
    --slate:     #4a5568;
    --rule:      rgba(15,17,23,0.12);
}

/* ── Global resets ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

.main .block-container {
    background: var(--paper);
    padding-top: 2rem;
    max-width: 1280px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--cream) !important;
    border-right: 1px solid var(--rule);
}
[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}
[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: var(--rust) !important;
}
[data-testid="stSidebar"] label { opacity: 0.7; font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--ink) !important;
    font-family: 'DM Serif Display', serif !important;
}
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox select {
    background: #ffffff !important;
    border: 1px solid var(--rule) !important;
    color: var(--ink) !important;
    border-radius: 4px;
}

/* ── Headers ── */
h1 { font-family: 'DM Serif Display', serif !important; font-size: 2.8rem !important; letter-spacing: -0.02em; }
h2 { font-family: 'DM Serif Display', serif !important; font-size: 1.6rem !important; }
h3 { font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.85rem !important; letter-spacing: 0.06em; text-transform: uppercase; color: var(--slate) !important; }

/* ── Metric cards ── */
.metric-card {
    background: var(--cream);
    border: 1px solid var(--rule);
    border-radius: 2px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--rust);
}
.metric-card.green::before { background: var(--sage); }
.metric-card.gold::before  { background: var(--gold); }

.metric-label {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.4rem;
    font-family: 'DM Mono', monospace;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--ink);
    line-height: 1.1;
}
.metric-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--slate);
    margin-top: 0.3rem;
}

/* ── Section dividers ── */
.section-rule {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 2rem 0;
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--slate);
    margin-bottom: 0.5rem;
}

/* ── Tab strip ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--rule);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    color: var(--slate);
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.6rem 1.4rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: var(--rust) !important;
    border-bottom: 2px solid var(--rust) !important;
    background: transparent !important;
}

/* ── Dataframe ── */
.stDataFrame { border: 1px solid var(--rule); border-radius: 2px; }

/* ── Buttons ── */
.stButton > button {
    background: var(--rust);
    color: white;
    border: none;
    border-radius: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.5rem 1.4rem;
}
.stButton > button:hover { background: #a83c25; }

/* ── Hero strip ── */
.hero {
    background: var(--ink);
    color: var(--paper);
    padding: 2.5rem 2.8rem;
    margin-bottom: 2.5rem;
    border-radius: 2px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.hero-title { font-family: 'DM Serif Display', serif; font-size: 3rem; line-height: 1; }
.hero-sub { font-family: 'DM Mono', monospace; font-size: 0.8rem; color: rgba(250,248,244,0.5); letter-spacing: 0.1em; text-transform: uppercase; margin-top: 0.5rem; }
.hero-badge { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--rust); letter-spacing: 0.1em; text-transform: uppercase; text-align: right; }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────
def build_amortization(principal, annual_rate, months, extra_monthly=0.0, lump_sums=None, start_date=None):
    """Returns a DataFrame with the full amortization schedule."""
    if lump_sums is None:
        lump_sums = {}
    monthly_rate = annual_rate / 100 / 12
    if monthly_rate == 0:
        base_payment = principal / months
    else:
        base_payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)

    rows = []
    balance = principal
    total_interest = 0.0
    if start_date is None:
        start_date = date.today().replace(day=1)

    for i in range(1, months + 1):
        if balance <= 0:
            break
        pmt_date = start_date + relativedelta(months=i - 1)
        interest = balance * monthly_rate
        principal_portion = min(base_payment - interest, balance)
        extra = min(extra_monthly + lump_sums.get(i, 0.0), balance - principal_portion)
        extra = max(extra, 0)
        total_pmt = base_payment + extra
        balance -= (principal_portion + extra)
        balance = max(balance, 0)
        total_interest += interest
        rows.append({
            "Month": i,
            "Date": pmt_date,
            "Payment": round(total_pmt, 2),
            "Principal": round(principal_portion + extra, 2),
            "Interest": round(interest, 2),
            "Extra": round(extra, 2),
            "Balance": round(balance, 2),
            "Cumulative Interest": round(total_interest, 2),
        })
        if balance == 0:
            break

    return pd.DataFrame(rows), round(base_payment, 2)


def fmt_currency(val):
    return f"£{val:,.0f}"

def fmt_months(m):
    y, mo = divmod(int(m), 12)
    parts = []
    if y: parts.append(f"{y}y")
    if mo: parts.append(f"{mo}m")
    return " ".join(parts) if parts else "0m"


# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 Loan Setup")
    st.markdown("---")

    principal = st.number_input("Loan Amount (£)", min_value=10_000, max_value=5_000_000,
                                 value=100_000, step=5_000, format="%d")
    annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.1, max_value=20.0,
                                   value=6.5, step=0.05, format="%.2f")
    loan_years = st.selectbox("Loan Term (years)", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35], index=29)
    start_date = st.date_input("Loan Start Date", value=date.today().replace(day=1))

    st.markdown("---")
    st.markdown("## ⚡ Accelerate Repayment")
    extra_monthly = st.number_input("Extra Monthly Payment (£)", min_value=0,
                                     max_value=50_000, value=0, step=50)
    lump_month = st.number_input("Lump Sum — Month #", min_value=1,
                                  max_value=loan_years * 12, value=12, step=1)
    lump_amount = st.number_input("Lump Sum — Amount (£)", min_value=0,
                                   max_value=500_000, value=0, step=1_000)

    st.markdown("---")
    st.markdown("## 🔁 Refinance Compare")
    refi_rate = st.number_input("New Rate (%)", min_value=0.1, max_value=20.0,
                                 value=5.5, step=0.05, format="%.2f")
    refi_costs = st.number_input("Refinance Costs (£)", min_value=0,
                                  max_value=50_000, value=1_000, step=500)


# ── Compute schedules ─────────────────────────────────────────────────────────
months = loan_years * 12
lump_sums = {int(lump_month): float(lump_amount)} if lump_amount > 0 else {}

df_base, base_pmt = build_amortization(principal, annual_rate, months,
                                        extra_monthly=0, lump_sums={},
                                        start_date=start_date)
df_accel, accel_pmt = build_amortization(principal, annual_rate, months,
                                          extra_monthly=extra_monthly,
                                          lump_sums=lump_sums,
                                          start_date=start_date)
df_refi, refi_pmt = build_amortization(principal, refi_rate, months,
                                        extra_monthly=extra_monthly,
                                        lump_sums=lump_sums,
                                        start_date=start_date)

# Convert date columns to proper datetime for full Plotly compatibility
for _df in [df_base, df_accel, df_refi]:
    _df["Date"] = pd.to_datetime(_df["Date"])

base_total_interest  = df_base["Interest"].sum()
accel_total_interest = df_accel["Interest"].sum()
refi_total_interest  = df_refi["Interest"].sum()
interest_saved       = base_total_interest - accel_total_interest
months_saved         = len(df_base) - len(df_accel)
payoff_date          = df_accel["Date"].iloc[-1]


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">Mortgage<br>Projection</div>
    <div class="hero-sub">Loan tracking · Repayment analysis · Refinance impact</div>
  </div>
  <div class="hero-badge">
    {fmt_currency(principal)} loan<br>
    {annual_rate}% · {loan_years} years<br>
    Payoff {payoff_date.strftime("%b %Y")}
  </div>
</div>
""", unsafe_allow_html=True)


# ── KPI row ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

cards = [
    (c1, "Base Monthly Payment", fmt_currency(base_pmt), f"+{fmt_currency(extra_monthly)} extra" if extra_monthly else "No extra payments", ""),
    (c2, "Total Interest (Base)", fmt_currency(base_total_interest), f"{base_total_interest/principal*100:.1f}% of principal", ""),
    (c3, "Interest Saved", fmt_currency(interest_saved), f"{fmt_months(months_saved)} earlier payoff", "green"),
    (c4, "Projected Payoff", payoff_date.strftime("%b %Y"), f"Month {len(df_accel)} of {months}", "gold"),
    (c5, "Total Cost (Accel.)", fmt_currency(principal + accel_total_interest), f"Principal + interest", ""),
]

for col, label, val, sub, variant in cards:
    with col:
        st.markdown(f"""
        <div class="metric-card {variant}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{val}</div>
          <div class="metric-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="section-rule">', unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Balance Over Time",
    "🥧  Payment Breakdown",
    "⚡  Extra Payment Impact",
    "🔁  Refinance Analysis",
    "📋  Full Schedule",
])


# ── TAB 1 · Balance over time ─────────────────────────────────────────────────
with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_base["Date"], y=df_base["Balance"],
        name="Standard schedule",
        line=dict(color="#4a5568", width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(74,85,104,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=df_accel["Date"], y=df_accel["Balance"],
        name="Accelerated schedule",
        line=dict(color="#c84b31", width=2.5),
        fill="tozeroy", fillcolor="rgba(200,75,49,0.08)",
    ))
    # Payoff marker - use add_shape to avoid Plotly datetime add_vline bug
    fig.add_shape(type="line", xref="x", yref="paper",
                  x0=payoff_date, x1=payoff_date, y0=0, y1=1,
                  line=dict(color="#4a7c59", width=1.5, dash="dash"))
    fig.add_annotation(x=payoff_date, y=1, yref="paper", yanchor="bottom",
                       text=f"Payoff {payoff_date.strftime('%b %Y')}",
                       font=dict(color="#4a7c59", size=11), showarrow=False)

    fig.update_layout(
        title=dict(text="Outstanding Balance Projection", font=dict(family="DM Serif Display", size=20)),
        xaxis_title="", yaxis_title="Balance (£)",
        yaxis_tickprefix="£", yaxis_tickformat=",.0f",
        plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
        font=dict(family="DM Sans", color="#0f1117"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified", height=420,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Cumulative interest side-by-side
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_base["Date"], y=df_base["Cumulative Interest"],
        name="Standard", line=dict(color="#4a5568", width=2, dash="dot"),
    ))
    fig2.add_trace(go.Scatter(
        x=df_accel["Date"], y=df_accel["Cumulative Interest"],
        name="Accelerated", line=dict(color="#d4a853", width=2.5),
        fill="tonexty", fillcolor="rgba(74,124,89,0.12)",
    ))
    fig2.update_layout(
        title=dict(text="Cumulative Interest Paid", font=dict(family="DM Serif Display", size=20)),
        xaxis_title="", yaxis_title="Interest (£)",
        yaxis_tickprefix="£", yaxis_tickformat=",.0f",
        plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
        font=dict(family="DM Sans", color="#0f1117"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified", height=360,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ── TAB 2 · Payment breakdown ─────────────────────────────────────────────────
with tab2:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # Donut: total cost composition
        labels = ["Principal", "Interest (Accel.)", "Interest Saved"]
        values = [principal, accel_total_interest, interest_saved]
        colours = ["#0f1117", "#c84b31", "#4a7c59"]
        fig_donut = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.62,
            marker=dict(colors=colours, line=dict(color="#faf8f4", width=2)),
            textinfo="label+percent",
            textfont=dict(family="DM Mono", size=11),
        ))
        fig_donut.update_layout(
            title=dict(text="Total Cost Composition", font=dict(family="DM Serif Display", size=20)),
            plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
            showlegend=False, height=380,
            margin=dict(l=10, r=10, t=60, b=10),
            annotations=[dict(text=f"<b>{fmt_currency(principal + accel_total_interest)}</b><br>total cost",
                              x=0.5, y=0.5, font_size=13, showarrow=False,
                              font=dict(family="DM Mono"))]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_right:
        # Stacked bar: principal vs interest per year
        df_accel["Year"] = df_accel["Date"].apply(lambda d: d.year)
        yearly = df_accel.groupby("Year").agg(
            Principal=("Principal", "sum"),
            Interest=("Interest", "sum"),
        ).reset_index()

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=yearly["Year"], y=yearly["Principal"],
                                  name="Principal", marker_color="#0f1117"))
        fig_bar.add_trace(go.Bar(x=yearly["Year"], y=yearly["Interest"],
                                  name="Interest", marker_color="#c84b31"))
        fig_bar.update_layout(
            barmode="stack",
            title=dict(text="Annual Principal vs Interest", font=dict(family="DM Serif Display", size=20)),
            xaxis_title="Year", yaxis_title="(£)",
            yaxis_tickprefix="£", yaxis_tickformat=",.0f",
            plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
            font=dict(family="DM Sans", color="#0f1117"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            height=380, margin=dict(l=10, r=10, t=60, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Early months breakdown table
    st.markdown('<div class="section-label">First 12 months — payment split</div>', unsafe_allow_html=True)
    display_cols = ["Month", "Date", "Payment", "Principal", "Interest", "Extra", "Balance"]
    df_show = df_accel[display_cols].head(12).copy()
    df_show["Date"] = df_show["Date"].apply(lambda d: d.strftime("%b %Y"))
    for col in ["Payment", "Principal", "Interest", "Extra", "Balance"]:
        df_show[col] = df_show[col].apply(lambda v: f"£{v:,.0f}")
    st.dataframe(df_show, use_container_width=True, hide_index=True)


# ── TAB 3 · Extra payment impact ─────────────────────────────────────────────
with tab3:
    st.markdown("#### Sensitivity — Extra Monthly Payment")
    extras = [0, 100, 200, 500, 1000, 1500, 2000, 3000]
    sensitivity_rows = []
    for e in extras:
        df_s, _ = build_amortization(principal, annual_rate, months,
                                      extra_monthly=e, lump_sums={}, start_date=start_date)
        sensitivity_rows.append({
            "Extra / Month": f"£{e:,}",
            "Payoff (months)": len(df_s),
            "Payoff Date": df_s["Date"].iloc[-1].strftime("%b %Y"),
            "Total Interest": df_s["Interest"].sum(),
            "Interest Saved": base_total_interest - df_s["Interest"].sum(),
            "Months Saved": len(df_base) - len(df_s),
        })
    df_sens = pd.DataFrame(sensitivity_rows)

    fig_sens = make_subplots(rows=1, cols=2,
                              subplot_titles=["Months to Payoff", "Total Interest Paid"])
    fig_sens.add_trace(go.Bar(
        x=df_sens["Extra / Month"], y=df_sens["Payoff (months)"],
        marker_color="#c84b31", name="Months"), row=1, col=1)
    fig_sens.add_trace(go.Bar(
        x=df_sens["Extra / Month"], y=df_sens["Total Interest"],
        marker_color="#4a7c59", name="Interest"), row=1, col=2)
    fig_sens.update_layout(
        plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
        font=dict(family="DM Sans", color="#0f1117"),
        showlegend=False, height=380,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig_sens.update_yaxes(tickprefix="£", tickformat=",.0f", row=1, col=2)
    st.plotly_chart(fig_sens, use_container_width=True)

    # Table
    df_display_sens = df_sens.copy()
    df_display_sens["Total Interest"] = df_display_sens["Total Interest"].apply(fmt_currency)
    df_display_sens["Interest Saved"] = df_display_sens["Interest Saved"].apply(fmt_currency)
    st.dataframe(df_display_sens, use_container_width=True, hide_index=True)

    # Lump sum what-if
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    st.markdown("#### Lump Sum Impact Across Timing")
    lump_months_test = [6, 12, 24, 36, 60, 120]
    if lump_amount > 0:
        lump_rows = []
        for lm in lump_months_test:
            if lm <= months:
                df_l, _ = build_amortization(principal, annual_rate, months,
                                              extra_monthly=0, lump_sums={lm: lump_amount},
                                              start_date=start_date)
                lump_rows.append({
                    "Paid at month": lm,
                    "Months saved": len(df_base) - len(df_l),
                    "Interest saved": base_total_interest - df_l["Interest"].sum(),
                })
        df_lump = pd.DataFrame(lump_rows)
        fig_lump = go.Figure(go.Bar(
            x=df_lump["Paid at month"].astype(str),
            y=df_lump["Interest saved"],
            marker_color="#d4a853",
            text=df_lump["Interest saved"].apply(fmt_currency),
            textposition="outside",
            name="Interest Saved",
        ))
        fig_lump.update_layout(
            title=dict(text=f"Interest Saved by Paying {fmt_currency(lump_amount)} at Different Months",
                       font=dict(family="DM Serif Display", size=18)),
            xaxis_title="Month of lump sum payment",
            yaxis_title="Interest Saved (£)",
            yaxis_tickprefix="£", yaxis_tickformat=",.0f",
            plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
            font=dict(family="DM Sans", color="#0f1117"),
            height=360, margin=dict(l=10, r=10, t=60, b=30),
        )
        st.plotly_chart(fig_lump, use_container_width=True)
    else:
        st.info("Set a Lump Sum Amount in the sidebar to see timing analysis.")


# ── TAB 4 · Refinance ─────────────────────────────────────────────────────────
with tab4:
    refi_interest_saved = accel_total_interest - refi_total_interest
    refi_net_saved = refi_interest_saved - refi_costs

    col_a, col_b, col_c = st.columns(3)
    for col, label, val, sub, variant in [
        (col_a, "Interest Saved by Refi", fmt_currency(refi_interest_saved), f"Gross saving", "green"),
        (col_b, "Refi Costs", fmt_currency(refi_costs), "Upfront fees", ""),
        (col_c, "Net Saving", fmt_currency(refi_net_saved), "After costs", "gold" if refi_net_saved > 0 else ""),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card {variant}">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    # Break-even
    if refi_net_saved > 0 and refi_costs > 0:
        monthly_saving = (accel_total_interest - refi_total_interest) / len(df_accel)
        if monthly_saving > 0:
            breakeven_months = int(refi_costs / (monthly_saving))
            st.markdown(f"""
            <div style="margin-top:1.5rem; padding: 1rem 1.4rem; background: var(--cream);
                        border-left: 3px solid var(--gold); font-family: 'DM Mono', monospace; font-size: 0.85rem;">
              Break-even point: <strong>{breakeven_months} months</strong>
              ({breakeven_months//12}y {breakeven_months%12}m) after refinancing
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # Side-by-side balance comparison
    fig_refi = go.Figure()
    fig_refi.add_trace(go.Scatter(
        x=df_accel["Date"], y=df_accel["Balance"],
        name=f"Current ({annual_rate}%)",
        line=dict(color="#c84b31", width=2.5),
    ))
    fig_refi.add_trace(go.Scatter(
        x=df_refi["Date"], y=df_refi["Balance"],
        name=f"Refinanced ({refi_rate}%)",
        line=dict(color="#4a7c59", width=2.5, dash="dash"),
    ))
    fig_refi.update_layout(
        title=dict(text="Balance Trajectory: Current vs Refinanced", font=dict(family="DM Serif Display", size=20)),
        xaxis_title="", yaxis_title="Balance (£)",
        yaxis_tickprefix="£", yaxis_tickformat=",.0f",
        plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
        font=dict(family="DM Sans", color="#0f1117"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified", height=400,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig_refi, use_container_width=True)

    # Rate sensitivity sweep
    rates = np.arange(max(1.0, annual_rate - 3), annual_rate + 0.1, 0.25)
    rate_rows = []
    for r in rates:
        df_r, p = build_amortization(principal, r, months, start_date=start_date)
        rate_rows.append({"Rate": round(r, 2), "Monthly Payment": p,
                          "Total Interest": df_r["Interest"].sum()})
    df_rates = pd.DataFrame(rate_rows)

    fig_rates = make_subplots(rows=1, cols=2,
                               subplot_titles=["Monthly Payment by Rate", "Total Interest by Rate"])
    fig_rates.add_trace(go.Scatter(x=df_rates["Rate"], y=df_rates["Monthly Payment"],
                                    mode="lines+markers", line=dict(color="#c84b31", width=2),
                                    name="Payment"), row=1, col=1)
    fig_rates.add_trace(go.Scatter(x=df_rates["Rate"], y=df_rates["Total Interest"],
                                    mode="lines+markers", line=dict(color="#0f1117", width=2),
                                    name="Total Interest"), row=1, col=2)
    fig_rates.add_shape(type="line", xref="x1", yref="paper",
                        x0=annual_rate, x1=annual_rate, y0=0, y1=1,
                        line=dict(color="#4a7c59", width=1.5, dash="dash"))
    fig_rates.add_shape(type="line", xref="x2", yref="paper",
                        x0=annual_rate, x1=annual_rate, y0=0, y1=1,
                        line=dict(color="#4a7c59", width=1.5, dash="dash"))
    fig_rates.add_annotation(x=annual_rate, y=1, xref="x1", yref="paper", yanchor="bottom",
                              text="Current rate", font=dict(color="#4a7c59", size=10), showarrow=False)
    fig_rates.update_layout(
        plot_bgcolor="#faf8f4", paper_bgcolor="#faf8f4",
        font=dict(family="DM Sans", color="#0f1117"),
        showlegend=False, height=360,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig_rates.update_yaxes(tickprefix="£", tickformat=",.0f")
    fig_rates.update_xaxes(ticksuffix="%")
    st.plotly_chart(fig_rates, use_container_width=True)


# ── TAB 5 · Full schedule ─────────────────────────────────────────────────────
with tab5:
    st.markdown(f"**{len(df_accel)} payments** in accelerated schedule &nbsp;·&nbsp; "
                f"**{len(df_base)} payments** in standard schedule")

    view_option = st.radio("View", ["Accelerated schedule", "Standard schedule"], horizontal=True)
    df_view = df_accel.copy() if "Accel" in view_option else df_base.copy()
    df_view["Date"] = df_view["Date"].apply(lambda d: d.strftime("%b %Y"))

    # Highlight milestones
    highlight_pct = st.slider("Highlight balance below (% remaining)", 0, 100, 50)
    threshold = principal * highlight_pct / 100

    display_full = df_view[["Month", "Date", "Payment", "Principal", "Interest", "Extra", "Balance", "Cumulative Interest"]].copy()
    for col in ["Payment", "Principal", "Interest", "Extra", "Balance", "Cumulative Interest"]:
        display_full[col] = display_full[col].apply(lambda v: f"£{v:,.0f}")

    st.dataframe(display_full, use_container_width=True, hide_index=True, height=500)

    # CSV download
    csv = df_view.to_csv(index=False)
    st.download_button(
        label="⬇ Download Schedule CSV",
        data=csv,
        file_name="mortgage_schedule.csv",
        mime="text/csv",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid rgba(15,17,23,0.12);
            font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #9ba3af; text-align: center;">
  Mortgage Intelligence · for illustrative purposes only · not financial advice
</div>
""", unsafe_allow_html=True)
