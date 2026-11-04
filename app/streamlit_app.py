"""Streamlit app: Is memory loss only about age? (CDC BRFSS 2023 + 2024, people 45+)

Uses only the summary tables in tableau/ (group totals with survey weights, small groups hidden),
so it is safe to run online. No data about single people.

Run locally:  streamlit run app/streamlit_app.py
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "tableau"
YOUNG, OLD, MUTED = "#2A5C8A", "#B4532A", "#6B7280"
GROUPS = ["Younger (45-64)", "Older (65+)"]
GROUP_COLORS = alt.Scale(domain=GROUPS, range=[YOUNG, OLD])

st.set_page_config(page_title="Is memory loss only about age?", page_icon="🧠", layout="wide")


@st.cache_data
def load(name):
    return pd.read_csv(DATA / name)


groups = load("dash_groups.csv").set_index("group")   # people and weighted % per age group
by_age = load("dash_age.csv")                          # 5-year age groups
by_inc = load("dash_income.csv")                       # age group x income
by_edu = load("dash_education.csv")                    # age group x education
by_health = load("dash_health.csv")                    # factor x age group
model = load("dash_model.csv")                         # permutation importance from the ML model
odds = load("odds_ratios.csv")                         # weighted logistic regression, models A and B
odds = odds[odds["model"] == "B"]                      # model B: with depression


def side_by_side(d, category, order, x_title, height=380):
    """Bars for younger and older people next to each other, per category."""
    return alt.Chart(d).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X(f"{category}:N", sort=order, title=x_title, axis=alt.Axis(labelAngle=0, labelLimit=120)),
        xOffset=alt.XOffset("group:N", sort=GROUPS),
        y=alt.Y("memory_loss_pct:Q", title="% with memory loss"),
        color=alt.Color("group:N", title="Age group", scale=GROUP_COLORS),
        tooltip=[alt.Tooltip("group:N", title="Age group"), alt.Tooltip(f"{category}:N"),
                 alt.Tooltip("people:Q", title="People", format=","),
                 alt.Tooltip("memory_loss_pct:Q", title="% with memory loss", format=".1f")],
    ).properties(height=height)


# ---- Look and feel: same style as the Tableau dashboard (white, grey tiles, dark buttons) ----
st.markdown("""
<style>
div.stButton > button {
    background-color: #2B2B2B; color: #FFFFFF; border: none; border-radius: 4px;
    font-weight: 700; padding: 0.9rem 0.5rem; width: 100%;
}
div.stButton > button:hover { background-color: #2A5C8A; color: #FFFFFF; }
div.stButton > button:focus:not(:active) { color: #FFFFFF; }
.kpi { text-align: center; padding: 0.4rem 0; }
.kpi .num { font-size: 2.3rem; font-weight: 300; color: #3A3A3A; line-height: 1.1; }
.kpi .lbl { font-size: 0.95rem; color: #6B7280; }
.subtitle { color: #6B7280; margin-top: -0.8rem; }
</style>
""", unsafe_allow_html=True)

PAGES = ["Home", "Age", "Income", "Education", "Health", "What predicts memory loss", "Risk checker"]
if "page" not in st.session_state:
    st.session_state.page = "Home"


def go(target):
    """Button callback: open another page (runs before the page is drawn again)."""
    st.session_state.page = target


def home_button():
    """Title row helper: a '← Home' button at the top right of every topic page."""
    _, right = st.columns([5, 1])
    right.button("← Home", on_click=go, args=("Home",), key="home_btn", width="stretch")


# ---- Sidebar: choose a topic (stays in sync with the buttons) ----
st.sidebar.title("🧠 Memory loss in people 45+")
page = st.sidebar.radio("Choose a topic", PAGES, key="page")
st.sidebar.markdown("---")
st.sidebar.caption("Data: CDC Behavioral Risk Factor Surveillance System (BRFSS) 2023 and 2024, "
                   "Cognitive Decline module (37 US states). Percentages use the survey weights. "
                   "Group totals only.")
st.sidebar.caption("Memory loss = \"confusion or memory loss that is happening more often or getting worse\" "
                   "in the past 12 months. Self-reported, not a diagnosis.")
st.sidebar.caption("Source: CDC BRFSS 2023-2024, free on cdc.gov. Student project, not endorsed by CDC.")

# ---- Home ----
if page == "Home":
    st.title("Is memory loss only about age?")
    st.markdown('<p class="subtitle">CDC BRFSS 2023 + 2024 &nbsp;|&nbsp; people aged 45+ in 37 US states '
                '&nbsp;|&nbsp; weighted survey results</p>', unsafe_allow_html=True)

    # KPI tiles: 2 x 2, so the numbers are not cut off on small screens
    everyone, young, old = groups.loc["Everyone (45+)"], groups.loc["Younger (45-64)"], groups.loc["Older (65+)"]
    kpis = [(f"{everyone['people']:,}", "people aged 45+"),
            (f"{everyone['with_memory_loss']:,}", "report memory loss getting worse"),
            (f"{young['memory_loss_pct']:.1f}%", "of younger people (45-64)"),
            (f"{old['memory_loss_pct']:.1f}%", "of older people (65+)")]
    for row in (kpis[:2], kpis[2:]):
        for col, (num, lbl) in zip(st.columns(2), row):
            with col.container(border=True):
                st.markdown(f'<div class="kpi"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>',
                            unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Groups")
        table = groups.reset_index()[["group", "people", "with_memory_loss", "memory_loss_pct"]].rename(columns={
            "group": "Group", "people": "People", "with_memory_loss": "With memory loss",
            "memory_loss_pct": "% (weighted)"})
        st.dataframe(table, hide_index=True, column_config={
            "People": st.column_config.NumberColumn(format="localized"),
            "With memory loss": st.column_config.NumberColumn(format="localized"),
            "% (weighted)": st.column_config.NumberColumn(format="%.1f%%")})
    with right:
        st.subheader("Main finding")
        low, high = by_inc[by_inc["group"] == GROUPS[0]]["memory_loss_pct"].iloc[[0, -1]]
        st.write(f"Memory loss is almost as common at 45-64 ({young['memory_loss_pct']:.1f}%) as at 65+ "
                 f"({old['memory_loss_pct']:.1f}%). For younger people, **money, depression and hearing** "
                 f"matter more than age. Lowest income: **{low:.1f}%** have memory loss. Highest income: "
                 f"**{high:.1f}%**.")

    st.write("**Click a topic to explore:**")
    topics = [("Age", "Age"), ("Income", "Income"), ("Education", "Education"), ("Health", "Health"),
              ("What predicts it?", "What predicts memory loss")]
    for col, (label, target) in zip(st.columns(len(topics)), topics):
        col.button(label, on_click=go, args=(target,), key=f"btn_{target}", width="stretch")
    st.button("Risk checker: which factors matter for a person like this?", on_click=go,
              args=("Risk checker",), key="btn_risk", width="stretch")

    st.caption('Memory loss here is self-reported ("confusion or memory loss happening more often or getting '
               'worse"), not a diagnosis. The charts show links, not causes. Percentages use the BRFSS survey '
               'weights. Only group totals are shown.')

# ---- Age ----
elif page == "Age":
    home_button()
    st.header("Memory loss is almost flat from 45 to 74")
    st.write("It only goes up clearly after age 75.")
    chart = alt.Chart(by_age).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("age_group:N", title="Age group", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("memory_loss_pct:Q", title="% with memory loss"),
        color=alt.condition(alt.datum.age_group < "65", alt.value(YOUNG), alt.value(OLD)),
        tooltip=[alt.Tooltip("age_group:N", title="Age group"), alt.Tooltip("people:Q", title="People", format=","),
                 alt.Tooltip("memory_loss_pct:Q", title="% with memory loss", format=".1f")],
    ).properties(height=380)
    labels = chart.mark_text(dy=-8, color=MUTED).encode(text=alt.Text("memory_loss_pct:Q", format=".1f"))
    st.altair_chart(chart + labels, width="stretch")
    st.caption("Blue = younger (45-64), orange = older (65+).")
    with st.expander("See the numbers"):
        st.dataframe(by_age[["age_group", "people", "with_memory_loss", "memory_loss_pct"]], hide_index=True)

# ---- Income ----
elif page == "Income":
    home_button()
    st.header("Low income goes with much more memory loss, especially for younger people")
    d = by_inc.copy()
    d["income"] = d["income"].str[2:]
    order = d["income"].drop_duplicates().tolist()
    st.altair_chart(side_by_side(d, "income", order, "Household income per year"), width="stretch")
    young = d[d["group"] == GROUPS[0]].set_index("income")["memory_loss_pct"]
    old = d[d["group"] == GROUPS[1]].set_index("income")["memory_loss_pct"]
    c1, c2 = st.columns(2)
    c1.metric("Younger: lowest vs highest income", f"{young.iloc[0]:.1f}% vs {young.iloc[-1]:.1f}%")
    c2.metric("Older: lowest vs highest income", f"{old.iloc[0]:.1f}% vs {old.iloc[-1]:.1f}%")
    with st.expander("See the numbers"):
        st.dataframe(d.pivot(index="income", columns="group", values="memory_loss_pct").loc[order, GROUPS])

# ---- Education ----
elif page == "Education":
    home_button()
    st.header("Less education goes with more memory loss")
    d = by_edu.copy()
    d["education"] = d["education"].str[2:]
    order = d["education"].drop_duplicates().tolist()
    st.altair_chart(side_by_side(d, "education", order, "Education"), width="stretch")
    st.caption("When income and health are in the same model, education matters much less "
               "(see the Risk checker).")
    with st.expander("See the numbers"):
        st.dataframe(d.pivot(index="education", columns="group", values="memory_loss_pct").loc[order, GROUPS])

# ---- Health ----
elif page == "Health":
    home_button()
    st.header("Health problems: how common is memory loss with each one?")
    group = st.radio("Age group", GROUPS, horizontal=True)
    d = by_health[by_health["group"] == group].copy()
    base = float(d.loc[d["factor"] == "None of these", "memory_loss_pct"].iloc[0])
    d["is_base"] = d["factor"] == "None of these"
    chart = alt.Chart(d).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("memory_loss_pct:Q", title="% with memory loss"),
        y=alt.Y("factor:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        color=alt.condition(alt.datum.is_base, alt.value(MUTED), alt.value(YOUNG if group == GROUPS[0] else OLD)),
        tooltip=[alt.Tooltip("factor:N", title="Factor"), alt.Tooltip("people:Q", title="People", format=","),
                 alt.Tooltip("memory_loss_pct:Q", title="% with memory loss", format=".1f")],
    ).properties(height=380)
    labels = chart.mark_text(align="left", dx=4, color=MUTED).encode(text=alt.Text("memory_loss_pct:Q", format=".1f"))
    st.altair_chart(chart + labels, width="stretch")
    st.caption(f"Grey bar: people with none of these health problems ({base:.1f}%). "
               "Simple comparisons; people can have several problems at the same time.")

# ---- What predicts memory loss ----
elif page == "What predicts memory loss":
    home_button()
    st.header("Which factors does a machine learning model need most?")
    st.write("A gradient boosting model learned who reports memory loss from the other survey answers "
             "(208,171 people). Bigger bar = the model needs this factor more.")
    group = st.radio("Age group", GROUPS, horizontal=True)
    d = model[model["Group"] == group]
    chart = alt.Chart(d).mark_bar(cornerRadiusEnd=4, color=YOUNG if group == GROUPS[0] else OLD).encode(
        x=alt.X("Importance:Q", title="Drop in model score when the factor is shuffled"),
        y=alt.Y("Factor:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=["Factor", alt.Tooltip("Importance:Q", format=".4f")]).properties(height=380)
    st.altair_chart(chart, width="stretch")
    if group == GROUPS[0]:
        st.success("For younger people, **depression, income and hearing** matter most. Age is almost not needed.")
    else:
        st.success("For older people, **age** is one of the top 3 factors, after depression and hearing.")
    st.caption("Model score (ROC AUC): 0.71 overall, 0.74 for younger and 0.68 for older people. "
               "Memory loss here is self-reported, so it is hard to predict. For learning, not for diagnosing.")

# ---- Risk checker (explains factors, does not diagnose) ----
else:
    home_button()
    st.header("Which factors matter for a person like this?")
    st.warning("**This is not a diagnosis and not medical advice.** It shows what the statistics found for "
               "groups of people in the USA. These are links, not causes. Worried about memory? Talk to a doctor.")

    col1, col2 = st.columns(2)
    group = col1.radio("Age group", GROUPS, horizontal=True)
    sex = col2.radio("Sex", ["Male", "Female"], horizontal=True)
    incomes = ["Under $15k", "$15-25k", "$25-35k", "$35-50k", "$50-100k", "$100-200k", "$200k+"]
    income = col1.select_slider("Household income per year", incomes, value="$200k+")
    edus = {"College graduate": None, "Some college": "Some college (vs college)",
            "High school": "High school (vs college)", "Less than high school": "Less than high school (vs college)"}
    edu = col2.selectbox("Education", list(edus))
    health = st.multiselect("Health", ["Depression", "Deaf / serious hearing problem", "Stroke", "COPD",
                                       "Heart disease", "Diabetes", "No exercise", "Current smoker", "Obese"])

    g = odds[odds["group"] == group].set_index("factor")
    rows = []
    if income != "$200k+":
        r = g.loc[f"Income {income.replace('Under', 'under')} (vs $200k+)"]
        rows.append((f"Income {income}", r["OR"], r["p"]))
    if edus[edu]:
        r = g.loc[edus[edu]]
        rows.append((edu, r["OR"], r["p"]))
    if sex == "Female":
        r = g.loc["Female"]
        rows.append(("Female", r["OR"], r["p"]))
    for h in health:
        r = g.loc[h]
        rows.append((h, r["OR"], r["p"]))

    if not rows:
        st.info("This is the comparison person: same age group, male, income $200k+, a college degree and "
                "none of the health problems. Change the choices above to see how each factor changes the odds.")
    else:
        d = pd.DataFrame(rows, columns=["Factor", "Times the odds", "p"])
        d["Times the odds"] = d["Times the odds"].round(2)
        d["Proven?"] = d["p"].map(lambda p: "Yes" if p < 0.05 else "Not proven")
        d["Effect"] = d["Times the odds"].map(lambda v: "Higher odds" if v > 1 else "Lower odds")
        chart = alt.Chart(d).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Times the odds:Q", title="Times the odds (1 = no difference)"),
            y=alt.Y("Factor:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
            color=alt.Color("Effect:N", scale=alt.Scale(domain=["Higher odds", "Lower odds"], range=[OLD, YOUNG]),
                            legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["Factor", "Times the odds", "Proven?"]).properties(height=max(160, 64 * len(d)))
        rule = alt.Chart(pd.DataFrame({"x": [1]})).mark_rule(color=MUTED, strokeDash=[4, 4]).encode(x="x:Q")
        st.altair_chart(chart + rule, width="stretch")
        total = float(d["Times the odds"].prod())
        st.metric("All chosen factors together", f"about {total:.1f}× the odds",
                  help="The odds ratios multiplied, as the logistic regression model does.")
        st.write(f"Compared with a person of the **same age group ({group})** who is male, has an income of "
                 "$200k+, a college degree and none of the health problems.")
        st.info("A big number does **not** mean this person has memory loss. Odds are not percentages, and "
                "multiplying many factors makes the number grow fast. In the data, about 16 in 100 people "
                "aged 45+ report memory loss getting worse.")
        st.dataframe(d[["Factor", "Times the odds", "Proven?"]], hide_index=True)

    st.caption("Odds ratios from a weighted logistic regression on BRFSS 2023 + 2024 (all factors together, "
               "plus state and year; standard errors clustered by survey PSU). The odds ratio compares odds, "
               "not percentages. Depression and memory complaints go together in both directions.")
