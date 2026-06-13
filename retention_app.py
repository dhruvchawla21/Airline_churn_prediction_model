import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Retention Control Tower", page_icon="✈️", layout="wide")

st.markdown("""
<style>
  .stApp { background-color: #f0f4f8; }
  .block-container { padding: 1.2rem 2rem 2rem; max-width: 1400px; }
  .stTabs [data-baseweb="tab"] { font-weight: 500; font-size: 0.95rem; padding: 10px 20px; }
  .stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; }
  hr { border-color: #e2e8f0; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("final_customer_results.csv")
    df["Loyalty Number"] = df["Loyalty Number"].astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("final_customer_results.csv not found. Run Final_pipeline.ipynb first.")
    st.stop()

SEG_COLORS = {
    "VIP at risk":         "#c0392b",
    "At risk":             "#e74c3c",
    "High-value, cooling": "#d35400",
    "Cooling":             "#e67e22",
    "High-value, healthy": "#1e8449",
    "Healthy":             "#27ae60",
}
SEG_ORDER    = list(SEG_COLORS.keys())
RISK_BORDERS = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#27ae60"}

at_risk     = df[df["risk_band"] == "High"]
vip_risk    = df[df["segment"] == "VIP at risk"]
clv_exposed = at_risk["CLV"].sum()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a2e4a 0%,#2c5282 100%);
     border-radius:14px;padding:22px 30px;margin-bottom:1.6rem">
  <div style="display:flex;align-items:center;gap:14px">
    <span style="font-size:2.4rem">✈️</span>
    <div>
      <div style="font-size:1.7rem;font-weight:700;color:white;letter-spacing:-0.3px">
        Retention Control Tower</div>
      <div style="font-size:0.87rem;color:#90b8d4;margin-top:4px">
        Scored end of June 2018 · disengagement risk forecast for H2 2018</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI cards ────────────────────────────────────────────────────────────────
def kpi_card(col, label, value, sub, border_color):
    col.markdown(f"""
<div style="background:white;border-radius:12px;padding:18px 22px;
     box-shadow:0 1px 5px rgba(0,0,0,0.09);border-left:5px solid {border_color}">
  <div style="font-size:0.7rem;color:#718096;font-weight:700;text-transform:uppercase;
       letter-spacing:0.7px">{label}</div>
  <div style="font-size:2.1rem;font-weight:700;color:#1a202c;margin:5px 0 3px;line-height:1">
    {value}</div>
  <div style="font-size:0.76rem;color:#a0aec0">{sub}</div>
</div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "Active members",    f"{len(df):,}",              "in scoring population",             "#2b6cb0")
kpi_card(k2, "Flagged high risk",  f"{len(at_risk):,}",         "~1 in 5 disengage within 6 months", "#e74c3c")
kpi_card(k3, "VIPs at risk",       f"{len(vip_risk):,}",        "top-30% CLV — call these first",    "#d35400")
kpi_card(k4, "CLV exposed",        f"${clv_exposed/1e6:,.1f}M", "lifetime value at high risk",       "#805ad5")

st.markdown("<div style='margin-top:1.4rem'></div>", unsafe_allow_html=True)

tab_list, tab_play, tab_member = st.tabs(
    ["📋  Action list", "🗺️  Segment playbook", "🔎  Member lookup"])

# ── Tab 1: Action list ───────────────────────────────────────────────────────
with tab_list:
    chart_col, filter_col = st.columns([3, 1])

    with filter_col:
        st.markdown("**Filter contacts**")
        seg_pick  = st.multiselect("Segments", SEG_ORDER,
                                   default=["VIP at risk", "At risk"])
        card_pick = st.multiselect("Loyalty card",
                                   sorted(df["loyalty_card"].unique()),
                                   default=sorted(df["loyalty_card"].unique()))
        top_n     = st.slider("Max contacts", 50, 3000, 500, step=50)

    with chart_col:
        sample = df.sample(min(4000, len(df)), random_state=42)
        fig_scatter = px.scatter(
            sample, x="churn_probability", y="CLV",
            color="segment", color_discrete_map=SEG_COLORS,
            opacity=0.6, category_orders={"segment": SEG_ORDER},
            labels={"churn_probability": "Churn probability", "CLV": "Lifetime value ($)"},
            title="Member landscape — where risk meets value",
        )
        fig_scatter.update_traces(marker_size=5)
        fig_scatter.update_layout(
            height=290, margin=dict(l=0, r=0, t=36, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1, font_size=11, title_text=""),
            xaxis=dict(gridcolor="#edf2f7", range=[0, 1]),
            yaxis=dict(gridcolor="#edf2f7"),
            title_font_size=13, font_family="sans-serif",
        )
        st.plotly_chart(fig_scatter, use_container_width=True,
                        config={"displayModeBar": False})

    st.divider()

    view = (df[df["segment"].isin(seg_pick) & df["loyalty_card"].isin(card_pick)]
              .sort_values("churn_probability", ascending=False)
              .head(top_n))

    if len(view) == 0:
        st.info("No members match the current filters.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Members selected",      f"{len(view):,}")
        m2.metric("Expected to disengage",  f"{view['churn_probability'].sum():,.0f}")
        m3.metric("Combined CLV",           f"${view['CLV'].sum():,.0f}")

        show = view[["Loyalty Number", "segment", "churn_probability", "CLV",
                     "loyalty_card", "recency_months", "flights_12m",
                     "zero_streak_now", "recommended_action"]].rename(columns={
            "churn_probability":  "Risk score",
            "segment":            "Segment",
            "loyalty_card":       "Card",
            "recency_months":     "Months since last flight",
            "flights_12m":        "Flights (12m)",
            "zero_streak_now":    "Inactive streak (months)",
            "recommended_action": "Next action"})
        st.dataframe(show, use_container_width=True, hide_index=True, height=380,
            column_config={
                "Risk score": st.column_config.ProgressColumn(
                    "Risk score", min_value=0, max_value=1, format="%.2f"),
                "CLV": st.column_config.NumberColumn(format="$%d")})
        st.download_button("⬇  Download contact list (CSV)",
                           show.to_csv(index=False).encode(),
                           file_name="retention_contact_list.csv", mime="text/csv")

# ── Tab 2: Segment playbook ──────────────────────────────────────────────────
with tab_play:
    stats = (df.groupby("segment").agg(
                 n=("Loyalty Number", "size"),
                 churn_rate=("churned", "mean"),
                 clv=("CLV", "mean"),
                 action=("recommended_action", "first"))
               .reindex(SEG_ORDER))

    cards_col, charts_col = st.columns([2, 3])

    with cards_col:
        st.markdown("**Six segments — one play each**")
        for seg in SEG_ORDER:
            if seg not in stats.index:
                continue
            r  = stats.loc[seg]
            bc = ("#e74c3c" if "at risk" in seg.lower()
                  else "#e67e22" if "cooling" in seg.lower() else "#27ae60")
            st.markdown(f"""
<div style="background:white;border-radius:10px;padding:14px 18px;margin-bottom:10px;
     box-shadow:0 1px 4px rgba(0,0,0,0.07);border-left:5px solid {bc}">
  <div style="font-weight:600;font-size:0.93rem;color:#1a202c">{seg}</div>
  <div style="font-size:0.77rem;color:#718096;margin:3px 0 6px">
    {int(r['n']):,} members &nbsp;·&nbsp; {r['churn_rate']*100:.0f}% churn
    &nbsp;·&nbsp; avg CLV ${r['clv']:,.0f}
  </div>
  <div style="font-size:0.83rem;color:#2d3748"><b>Play:</b> {r['action']}</div>
</div>""", unsafe_allow_html=True)

    with charts_col:
        seg_clv = (df.groupby("segment")["CLV"].sum()
                     .reindex(SEG_ORDER).reset_index())
        seg_clv.columns = ["Segment", "CLV"]
        seg_clv["CLV_M"] = seg_clv["CLV"] / 1e6

        fig_bar = go.Figure(go.Bar(
            x=seg_clv["CLV_M"], y=seg_clv["Segment"], orientation="h",
            marker_color=[SEG_COLORS[s] for s in seg_clv["Segment"]],
            text=seg_clv["CLV_M"].map("${:.1f}M".format), textposition="outside",
        ))
        fig_bar.update_layout(
            title="Total lifetime value by segment",
            height=310, margin=dict(l=0, r=70, t=36, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#edf2f7", title="Total CLV ($M)"),
            yaxis=dict(autorange="reversed"),
            title_font_size=13, font_family="sans-serif", font_size=12,
        )
        st.plotly_chart(fig_bar, use_container_width=True,
                        config={"displayModeBar": False})

        risk_counts = df["risk_band"].value_counts().reindex(["High", "Medium", "Low"])
        fig_risk = go.Figure(go.Bar(
            x=risk_counts.values, y=risk_counts.index, orientation="h",
            marker_color=["#e74c3c", "#e67e22", "#27ae60"],
            text=[f"{v:,}" for v in risk_counts.values], textposition="outside",
        ))
        fig_risk.update_layout(
            title="Members by risk band",
            height=210, margin=dict(l=0, r=60, t=36, b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#edf2f7", title="Members"),
            title_font_size=13, font_family="sans-serif", font_size=12,
        )
        st.plotly_chart(fig_risk, use_container_width=True,
                        config={"displayModeBar": False})

# ── Tab 3: Member lookup ─────────────────────────────────────────────────────
with tab_member:
    q = st.text_input("Loyalty number", placeholder="e.g. 100018", max_chars=10)

    if not q:
        st.caption("Enter a loyalty number to see the full risk profile for that member.")
    else:
        try:
            row = df[df["Loyalty Number"] == int(q)]
        except ValueError:
            row = df.iloc[0:0]

        if len(row) == 0:
            st.warning("Member not found. Members with no flights in the last 12 months "
                       "are outside the scored population.")
        else:
            r  = row.iloc[0]
            bc = RISK_BORDERS[r["risk_band"]]

            left, right = st.columns([1, 2])

            with left:
                st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 22px;
     box-shadow:0 1px 5px rgba(0,0,0,0.09);border-left:6px solid {bc}">
  <div style="font-size:0.7rem;color:#718096;font-weight:700;text-transform:uppercase;
       letter-spacing:0.7px">Loyalty #{int(r['Loyalty Number'])}</div>
  <div style="font-size:1.5rem;font-weight:700;color:#1a202c;margin:6px 0 4px">
    {r['segment']}</div>
  <div style="font-size:1.15rem;font-weight:600;color:{bc}">
    Risk score: {r['churn_probability']:.2f}</div>
  <hr style="border-color:#edf2f7;margin:12px 0">
  <div style="font-size:0.84rem;color:#4a5568;line-height:2">
    <b>Card:</b> {r['loyalty_card']}<br>
    <b>Lifetime value:</b> ${r['CLV']:,.0f}<br>
    <b>Tenure:</b> {int(r['tenure_months'])} months<br>
    <b>Flights (12m):</b> {int(r['flights_12m'])}<br>
    <b>Last flight:</b> {int(r['recency_months'])} months ago<br>
    <b>Inactive streak:</b> {int(r['zero_streak_now'])} months
  </div>
</div>""", unsafe_allow_html=True)
                st.markdown(f"""
<div style="background:#fffbeb;border:1px solid #f6e05e;border-radius:10px;
     padding:14px 18px;margin-top:12px;font-size:0.85rem;color:#744210">
  <div style="font-weight:600;margin-bottom:4px">Recommended action</div>
  {r['recommended_action']}
</div>""", unsafe_allow_html=True)

            with right:
                seg_avg = df[df["segment"] == r["segment"]].mean(numeric_only=True)

                labels = ["Flights (12m)", "Months since last flight",
                          "Inactive streak (months)", "Points earned (12m)"]
                member_vals = [r["flights_12m"], r["recency_months"],
                               r["zero_streak_now"], r["points_acc_12m"]]
                avg_vals    = [seg_avg["flights_12m"], seg_avg["recency_months"],
                               seg_avg["zero_streak_now"], seg_avg["points_acc_12m"]]

                fig_member = go.Figure()
                fig_member.add_trace(go.Bar(
                    name="This member", x=labels, y=member_vals,
                    marker_color=bc, opacity=0.9,
                    text=[f"{v:.0f}" for v in member_vals], textposition="outside"))
                fig_member.add_trace(go.Bar(
                    name="Segment avg", x=labels, y=avg_vals,
                    marker_color="#94a3b8", opacity=0.7,
                    text=[f"{v:.0f}" for v in avg_vals], textposition="outside"))
                fig_member.update_layout(
                    barmode="group", height=320,
                    margin=dict(l=0, r=0, t=36, b=0),
                    plot_bgcolor="white", paper_bgcolor="white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                xanchor="right", x=1, font_size=12),
                    title=f"Member vs '{r['segment']}' average",
                    title_font_size=13, font_family="sans-serif",
                    yaxis=dict(gridcolor="#edf2f7"),
                )
                st.plotly_chart(fig_member, use_container_width=True,
                                config={"displayModeBar": False})

                all_avg = df.mean(numeric_only=True)
                d1, d2, d3 = st.columns(3)
                d1.metric("Flights vs avg",
                          f"{r['flights_12m']:.0f}",
                          f"{r['flights_12m'] - all_avg['flights_12m']:+.1f}")
                d2.metric("Recency vs avg",
                          f"{r['recency_months']:.0f} mo",
                          f"{r['recency_months'] - all_avg['recency_months']:+.1f} mo")
                d3.metric("Points vs avg",
                          f"{r['points_acc_12m']:,.0f}",
                          f"{r['points_acc_12m'] - all_avg['points_acc_12m']:+,.0f}")
