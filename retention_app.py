import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Retention Control Tower",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  /* ── Reset & base ─────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  section[data-testid="stSidebar"] { display: none; }
  footer { display: none; }
  #MainMenu { display: none; }

  /* ── Header ──────────────────────────────────────── */
  .rct-header {
    background: linear-gradient(135deg, #0b1a33 0%, #1a3360 100%);
    color: white;
    padding: 18px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
  }
  .rct-header-left { display: flex; align-items: center; gap: 14px; }
  .rct-icon {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    width: 44px; height: 44px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
  }
  .rct-header h1 {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    margin: 0;
    color: white;
  }
  .rct-header p {
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    margin: 3px 0 0;
    letter-spacing: 0.1px;
  }
  .rct-badge {
    background: rgba(22,163,74,0.15);
    border: 1px solid rgba(22,163,74,0.35);
    color: #4ade80;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 5px 12px;
    border-radius: 20px;
    white-space: nowrap;
  }

  /* ── KPI cards ───────────────────────────────────── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 24px 36px 0;
  }
  .kpi-card {
    background: #ffffff;
    border: 0.5px solid rgba(15,31,61,0.1);
    border-radius: 10px;
    padding: 16px 18px;
    border-top-width: 3px;
  }
  .kpi-card.blue  { border-top-color: #2563eb; }
  .kpi-card.red   { border-top-color: #dc2626; }
  .kpi-card.amber { border-top-color: #d97706; }
  .kpi-card.purple{ border-top-color: #7c3aed; }
  .kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #64748b;
  }
  .kpi-value {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #0f1f3d;
    margin: 6px 0 3px;
    line-height: 1;
  }
  .kpi-sub {
    font-size: 11px;
    color: #94a3b8;
  }

  /* ── Body padding ─────────────────────────────────── */
  .rct-body { padding: 0 36px 36px; }

  /* ── Segment playbook cards ───────────────────────── */
  .seg-card {
    background: #ffffff;
    border: 0.5px solid rgba(15,31,61,0.1);
    border-left: 4px solid #888;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
  }
  .seg-card h4 { font-size: 14px; font-weight: 600; color: #0f1f3d; margin: 0 0 3px; }
  .seg-card .meta { font-size: 12px; color: #64748b; margin-bottom: 6px; }
  .seg-card .play { font-size: 13px; color: #0f1f3d; }
  .seg-card.red    { border-left-color: #dc2626; }
  .seg-card.amber  { border-left-color: #d97706; }
  .seg-card.green  { border-left-color: #16a34a; }

  /* ── General ──────────────────────────────────────── */
  [data-testid="stMetricValue"] { display: none; }
  [data-testid="stMetricLabel"] { display: none; }
  div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid rgba(15,31,61,0.1);
    background: transparent;
  }
  .stTabs [data-baseweb="tab"] {
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
    color: #64748b;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
  }
  .stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom-color: #2563eb !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab-panel"] { padding: 0; }
  h2, h3 { color: #0f1f3d !important; letter-spacing: -0.3px; }
  .summary-bar {
    background: #f1f5f9;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    color: #64748b;
    display: flex;
    gap: 28px;
  }
  .summary-bar strong { color: #0f1f3d; }
</style>
""", unsafe_allow_html=True)


# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df = pd.read_csv("final_customer_results.csv")
    df["Loyalty Number"] = df["Loyalty Number"].astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("**File not found:** `final_customer_results.csv` — run `Final_pipeline.ipynb` first, then place the CSV next to this file.")
    st.stop()

SEG_ORDER = ["VIP at risk", "At risk", "High-value, cooling", "Cooling", "High-value, healthy", "Healthy"]
SEG_COLOR = {
    "VIP at risk": "red", "At risk": "red",
    "High-value, cooling": "amber", "Cooling": "amber",
    "High-value, healthy": "green", "Healthy": "green",
}
RISK_COLORS = {"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"}

at_risk     = df[df["risk_band"] == "High"]
vip_risk    = df[df["segment"] == "VIP at risk"]
clv_exposed = at_risk["CLV"].sum()


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="rct-header">
  <div class="rct-header-left">
    <div class="rct-icon">✈️</div>
    <div>
      <h1>Retention Control Tower</h1>
      <p>Loyalty programme &nbsp;·&nbsp; Scoring period: June 2018 &nbsp;·&nbsp; Forecast: Jul – Dec 2018</p>
    </div>
  </div>
  <span class="rct-badge">● ANALYSIS READY</span>
</div>
""", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-label">Active members</div>
    <div class="kpi-value">{len(df):,}</div>
    <div class="kpi-sub">in scoring population</div>
  </div>
  <div class="kpi-card red">
    <div class="kpi-label">Flagged high risk</div>
    <div class="kpi-value">{len(at_risk):,}</div>
    <div class="kpi-sub">~1 in 5 disengage within 6 months</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-label">VIPs at risk</div>
    <div class="kpi-value">{len(vip_risk):,}</div>
    <div class="kpi-sub">top-30% CLV — prioritise these first</div>
  </div>
  <div class="kpi-card purple">
    <div class="kpi-label">CLV exposed</div>
    <div class="kpi-value">${clv_exposed/1e6:,.1f}M</div>
    <div class="kpi-sub">lifetime value of all high-risk members</div>
  </div>
</div>
<div style="height:24px;"></div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────

with st.container():
    st.markdown('<div class="rct-body">', unsafe_allow_html=True)

    tab_list, tab_play, tab_member = st.tabs(
        ["📋  Action list", "🗺️  Segment playbook", "🔍  Member lookup"]
    )

    # ── Tab 1: Action list ────────────────────────────────────────────────────

    with tab_list:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        st.markdown("#### Who needs attention first")
        st.markdown("<p style='font-size:13px;color:#64748b;margin-top:-8px;margin-bottom:16px'>Sorted by risk score. Filter, review, and download — the CSV is ready to hand to the ops team.</p>", unsafe_allow_html=True)

        f1, f2, f3 = st.columns([2, 2, 3])
        with f1:
            seg_pick = st.multiselect(
                "Segments",
                SEG_ORDER,
                default=["VIP at risk", "At risk"],
            )
        with f2:
            card_pick = st.multiselect(
                "Loyalty card",
                sorted(df["loyalty_card"].unique()),
                default=sorted(df["loyalty_card"].unique()),
            )
        with f3:
            top_n = st.slider("Members the team can contact", 50, 3000, 500, step=50)

        view = (
            df[df["segment"].isin(seg_pick) & df["loyalty_card"].isin(card_pick)]
            .sort_values("churn_probability", ascending=False)
            .head(top_n)
        )

        if len(view) == 0:
            st.info("No members match these filters — try widening the segment or card selection.")
        else:
            exp_churn = view["churn_probability"].sum()
            st.markdown(
                f"""<div class="summary-bar">
                  <span>Members selected: <strong>{len(view):,}</strong></span>
                  <span>Expected to disengage: <strong>{exp_churn:,.0f}</strong></span>
                  <span>Combined CLV: <strong>${view['CLV'].sum():,.0f}</strong></span>
                </div>""",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Scatter: churn prob vs CLV
            scatter_color_map = {
                "VIP at risk": "#dc2626", "At risk": "#ef4444",
                "High-value, cooling": "#f59e0b", "Cooling": "#fbbf24",
                "High-value, healthy": "#16a34a", "Healthy": "#4ade80",
            }
            fig = px.scatter(
                view,
                x="churn_probability",
                y="CLV",
                color="segment",
                color_discrete_map=scatter_color_map,
                hover_data=["Loyalty Number", "loyalty_card", "recency_months"],
                labels={"churn_probability": "Churn probability", "CLV": "Lifetime value ($)", "segment": "Segment"},
                height=320,
            )
            fig.update_traces(marker=dict(size=6, opacity=0.7))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#f8fafc",
                font_family="Inter, sans-serif",
                font_color="#0f1f3d",
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.01,
                    xanchor="left", x=0, font=dict(size=12),
                    title_text="",
                ),
                margin=dict(t=36, b=36, l=0, r=0),
                xaxis=dict(gridcolor="rgba(0,0,0,0.05)", tickformat=".0%"),
                yaxis=dict(gridcolor="rgba(0,0,0,0.05)", tickprefix="$", tickformat=",.0f"),
            )
            st.plotly_chart(fig, use_container_width=True)

            show = view[[
                "Loyalty Number", "segment", "churn_probability",
                "CLV", "loyalty_card", "recency_months", "flights_12m",
                "zero_streak_now", "recommended_action",
            ]].rename(columns={
                "churn_probability":  "Risk score",
                "segment":            "Segment",
                "loyalty_card":       "Card",
                "recency_months":     "Months since last flight",
                "flights_12m":        "Flights (12m)",
                "zero_streak_now":    "Inactive streak (mo)",
                "recommended_action": "Next action",
            })

            st.dataframe(
                show,
                use_container_width=True,
                hide_index=True,
                height=380,
                column_config={
                    "Risk score": st.column_config.ProgressColumn(
                        "Risk score", min_value=0, max_value=1, format="%.2f"
                    ),
                    "CLV": st.column_config.NumberColumn(format="$%d"),
                },
            )

            st.download_button(
                "⬇  Download contact list (CSV)",
                show.to_csv(index=False).encode(),
                file_name="retention_contact_list.csv",
                mime="text/csv",
            )

    # ── Tab 2: Segment playbook ───────────────────────────────────────────────

    with tab_play:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("#### One play per segment")
        st.markdown("<p style='font-size:13px;color:#64748b;margin-top:-8px;margin-bottom:20px'>Six segments from two questions: how likely to disengage (model risk) and how valuable (top-30% CLV = high).</p>", unsafe_allow_html=True)

        stats = df.groupby("segment").agg(
            n=("Loyalty Number", "size"),
            avg_risk=("churn_probability", "mean"),
            churn_rate=("churned", "mean"),
            clv=("CLV", "mean"),
            action=("recommended_action", "first"),
        )

        left, right = st.columns(2)
        for i, seg in enumerate(SEG_ORDER):
            if seg not in stats.index:
                continue
            r = stats.loc[seg]
            css = SEG_COLOR.get(seg, "green")
            card_html = f"""
            <div class="seg-card {css}">
              <h4>{seg}</h4>
              <div class="meta">{int(r['n']):,} members · {r['churn_rate']*100:.0f}% observed disengagement · avg CLV ${r['clv']:,.0f}</div>
              <div class="play"><b>Play:</b> {r['action']}</div>
            </div>"""
            (left if i % 2 == 0 else right).markdown(card_html, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("#### Where the value sits")
        st.markdown("<p style='font-size:13px;color:#64748b;margin-top:-8px;margin-bottom:16px'>Total lifetime value ($M) by risk band — high-value bars in High/Medium = immediate revenue at stake.</p>", unsafe_allow_html=True)

        pivot = df.pivot_table(
            index="risk_band",
            columns=df["CLV"] >= df["CLV"].quantile(0.70),
            values="CLV",
            aggfunc="sum",
        ).rename(columns={False: "Standard value", True: "High value (top 30%)"})
        pivot = pivot.reindex(["High", "Medium", "Low"]) / 1e6

        fig2 = go.Figure()
        bar_colors = {"Standard value": "#93c5fd", "High value (top 30%)": "#1d4ed8"}
        for col in pivot.columns:
            fig2.add_trace(go.Bar(
                name=col,
                x=pivot.index,
                y=pivot[col].round(2),
                marker_color=bar_colors.get(col, "#93c5fd"),
            ))
        fig2.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#f8fafc",
            font_family="Inter, sans-serif",
            font_color="#0f1f3d",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
            margin=dict(t=36, b=36, l=0, r=0),
            height=280,
            xaxis=dict(gridcolor="rgba(0,0,0,0.05)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0.05)", tickprefix="$", ticksuffix="M"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 3: Member lookup ──────────────────────────────────────────────────

    with tab_member:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("#### Look up one member")
        q = st.text_input("Loyalty number", placeholder="e.g. 100018", label_visibility="collapsed")

        if q:
            try:
                row = df[df["Loyalty Number"] == int(q)]
            except ValueError:
                row = df.iloc[0:0]

            if len(row) == 0:
                st.warning("Member not found. Members with no flights in the last 12 months are outside the scored population.")
            else:
                r = row.iloc[0]
                risk_color = RISK_COLORS.get(r.get("risk_band", "Low"), "#16a34a")

                st.markdown(f"""
                <div style="background:#fff;border:0.5px solid rgba(15,31,61,0.1);border-left:4px solid {risk_color};border-radius:10px;padding:20px 24px;margin-bottom:16px">
                  <div style="font-size:13px;color:#64748b;margin-bottom:4px">Loyalty #{int(r['Loyalty Number'])}</div>
                  <div style="font-size:22px;font-weight:700;color:#0f1f3d;margin-bottom:2px">{r['segment']}</div>
                  <div style="font-size:13px;color:#64748b">Card: {r['loyalty_card']}</div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                def mini_kpi(col, label, value, sub=""):
                    col.markdown(f"""
                    <div style="background:#f8fafc;border-radius:8px;padding:12px 14px">
                      <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;color:#64748b">{label}</div>
                      <div style="font-size:22px;font-weight:700;color:#0f1f3d;margin:4px 0 2px">{value}</div>
                      <div style="font-size:11px;color:#94a3b8">{sub}</div>
                    </div>""", unsafe_allow_html=True)

                mini_kpi(c1, "Risk score", f"{r['churn_probability']:.2f}")
                mini_kpi(c2, "Lifetime value", f"${r['CLV']:,.0f}")
                mini_kpi(c3, "Flights (12m)", int(r["flights_12m"]))
                mini_kpi(c4, "Tenure", f"{int(r['tenure_months'])} mo")

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                c5, c6, c7 = st.columns(3)
                mini_kpi(c5, "Months since last flight", int(r["recency_months"]))
                mini_kpi(c6, "Inactive streak", f"{int(r['zero_streak_now'])} mo")
                mini_kpi(c7, "Risk band", r.get("risk_band", "—"))

                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background:#eff6ff;border-radius:8px;padding:14px 18px;font-size:13px;color:#1e3a8a">
                  <span style="font-weight:600;">Recommended next action:</span> {r['recommended_action']}
                </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
