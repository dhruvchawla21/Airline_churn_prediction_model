# ============================================================================
# RETENTION CONTROL TOWER — Streamlit prototype
# ----------------------------------------------------------------------------
# Run with:   streamlit run retention_app.py
# Reads:      final_customer_results.csv  (produced by churn_pipeline.py,
#             must sit in the same folder as this file)
#
# Audience: a non-technical marketing manager. The app answers, on open:
#   1) Who needs attention right now?       (Action list tab)
#   2) How big is the problem?              (header KPIs)
#   3) What exactly do we do about it?      (Playbook tab, per segment)
#   4) Tell me about one specific member.   (Member lookup tab)
# ============================================================================

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Retention Control Tower",
                   page_icon="🛫", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
  .block-container {padding-top: 2.2rem;}
  h1 {font-weight: 800; letter-spacing: -0.5px;}
  [data-testid="stMetricValue"] {font-size: 1.9rem;}
  .seg-card {border: 1px solid #d9d9d9; border-left: 6px solid #888;
             border-radius: 8px; padding: 14px 18px; margin-bottom: 12px;
             background: #fafafa;}
  .seg-card h4 {margin: 0 0 4px 0;}
  .seg-card .meta {color: #666; font-size: 0.85rem; margin-bottom: 6px;}
  .risk-high {border-left-color: #c62828;}
  .risk-med  {border-left-color: #ef6c00;}
  .risk-low  {border-left-color: #2e7d32;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ data
@st.cache_data
def load_data():
    df = pd.read_csv("final_customer_results.csv")
    df["Loyalty Number"] = df["Loyalty Number"].astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("final_customer_results.csv not found. Run churn_pipeline.py "
             "first, then place the CSV next to this app.")
    st.stop()

SEG_RISK = {"VIP at risk": "risk-high", "At risk": "risk-high",
            "High-value, cooling": "risk-med", "Cooling": "risk-med",
            "High-value, healthy": "risk-low", "Healthy": "risk-low"}
SEG_ORDER = list(SEG_RISK.keys())

# ------------------------------------------------------------------ header
st.title("Retention Control Tower")
st.caption("Scored at the end of June 2018 · predicts disengagement risk for "
           "July–December 2018 · refresh by re-running the scoring pipeline")

at_risk = df[df["risk_band"] == "High"]
vip_risk = df[df["segment"] == "VIP at risk"]
clv_exposed = at_risk["CLV"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active members", f"{len(df):,}")
c2.metric("Flagged high risk", f"{len(at_risk):,}",
          help="Members above the model's high-risk threshold. "
               "Historically ~1 in 5 of these disengage within 6 months, "
               "vs ~1 in 30 overall.")
c3.metric("VIPs at risk", f"{len(vip_risk):,}",
          help="High risk AND top-30% lifetime value. Call these first.")
c4.metric("CLV exposed", f"${clv_exposed/1e6:,.1f}M",
          help="Combined lifetime value of all high-risk members.")

st.divider()

tab_list, tab_play, tab_member = st.tabs(
    ["📋 Action list", "🗺️ Segment playbook", "🔎 Member lookup"])

# ------------------------------------------------------------------ tab 1
with tab_list:
    st.subheader("Who needs attention first")
    st.caption("Sorted by risk. Filter, review, download — the CSV download "
               "is ready to hand to the campaign/ops team.")

    f1, f2, f3 = st.columns([2, 2, 3])
    seg_pick = f1.multiselect("Segments", SEG_ORDER,
                              default=["VIP at risk", "At risk"])
    card_pick = f2.multiselect("Loyalty card",
                               sorted(df["loyalty_card"].unique()),
                               default=sorted(df["loyalty_card"].unique()))
    top_n = f3.slider("How many members can the team contact?",
                      50, 3000, 500, step=50)

    view = df[df["segment"].isin(seg_pick) &
              df["loyalty_card"].isin(card_pick)] \
             .sort_values("churn_probability", ascending=False).head(top_n)

    if len(view) == 0:
        st.info("No members match these filters. Widen the segment or "
                "card selection above.")
    else:
        exp_churn = view["churn_probability"].sum()
        st.markdown(f"**{len(view):,} members selected** · the model expects "
                    f"roughly **{exp_churn:,.0f}** of them to disengage if "
                    f"nothing is done · combined CLV "
                    f"**${view['CLV'].sum():,.0f}**")

        show = view[["Loyalty Number", "segment", "churn_probability",
                     "CLV", "loyalty_card", "recency_months", "flights_12m",
                     "zero_streak_now", "recommended_action"]].rename(columns={
            "churn_probability": "Risk score",
            "segment": "Segment", "loyalty_card": "Card",
            "recency_months": "Months since last flight",
            "flights_12m": "Flights (12m)",
            "zero_streak_now": "Inactive streak (months)",
            "recommended_action": "Next action"})
        st.dataframe(
            show, use_container_width = True, hide_index=True, height=430,
            column_config={"Risk score": st.column_config.ProgressColumn(
                "Risk score", min_value=0, max_value=1, format="%.2f"),
                "CLV": st.column_config.NumberColumn(format="$%d")})

        st.download_button(
            "Download this contact list (CSV)",
            show.to_csv(index=False).encode(),
            file_name="retention_contact_list.csv", mime="text/csv")

# ------------------------------------------------------------------ tab 2
with tab_play:
    st.subheader("One play per segment")
    st.caption("Six segments from two questions: how likely is the member to "
               "disengage (model risk) and how valuable are they (lifetime "
               "value, top 30% = high). Each card is the standing instruction "
               "for that group.")

    stats = df.groupby("segment").agg(
        n=("Loyalty Number", "size"),
        avg_risk=("churn_probability", "mean"),
        churn_rate=("churned", "mean"),
        clv=("CLV", "mean"),
        action=("recommended_action", "first"))

    left, right = st.columns(2)
    for i, seg in enumerate(SEG_ORDER):
        if seg not in stats.index:
            continue
        r = stats.loc[seg]
        target = left if i % 2 == 0 else right
        target.markdown(f"""
<div class="seg-card {SEG_RISK[seg]}">
  <h4>{seg}</h4>
  <div class="meta">{int(r['n']):,} members · observed disengagement
  {r['churn_rate']*100:.0f}% · avg lifetime value ${r['clv']:,.0f}</div>
  <div><b>Play:</b> {r['action']}</div>
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("**Where the value sits**")
    pivot = df.pivot_table(index="risk_band", columns=df["CLV"] >=
                           df["CLV"].quantile(0.70),
                           values="CLV", aggfunc="sum").rename(
        columns={False: "Standard value", True: "High value (top 30%)"})
    pivot = pivot.reindex(["High", "Medium", "Low"]) / 1e6
    st.bar_chart(pivot, height=260, use_container_width= True)
    st.caption("Total lifetime value ($M) by risk band. The red bars to "
               "watch: high-value dollars sitting in High/Medium risk.")

# ------------------------------------------------------------------ tab 3
with tab_member:
    st.subheader("Look up one member")
    q = st.text_input("Loyalty number", placeholder="e.g. 100018")
    if q:
        try:
            row = df[df["Loyalty Number"] == int(q)]
        except ValueError:
            row = df.iloc[0:0]
        if len(row) == 0:
            st.warning("No member with that loyalty number is in the scored "
                       "population (members with no flights in the last 12 "
                       "months are out of scope).")
        else:
            r = row.iloc[0]
            a, b, c, d = st.columns(4)
            a.metric("Risk score", f"{r['churn_probability']:.2f}")
            b.metric("Segment", r["segment"])
            c.metric("Lifetime value", f"${r['CLV']:,.0f}")
            d.metric("Card", r["loyalty_card"])
            e, f, g, h = st.columns(4)
            e.metric("Flights, last 12m", int(r["flights_12m"]))
            f.metric("Months since last flight", int(r["recency_months"]))
            g.metric("Inactive streak now", f"{int(r['zero_streak_now'])} mo")
            h.metric("Tenure", f"{int(r['tenure_months'])} mo")
            st.markdown(f"**Recommended next action:** "
                        f"{r['recommended_action']}")
