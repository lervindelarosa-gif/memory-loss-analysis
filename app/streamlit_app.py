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
compare = load("dash_compare.csv")                     # BRFSS (people say) vs NHANES (people tested)
BRFSS_LABEL, NHANES_LABEL = "BRFSS: say memory is worse", "NHANES: low memory test score"
DATASET_COLORS = alt.Scale(domain=[BRFSS_LABEL, NHANES_LABEL], range=["#4E79A7", "#F28E2B"])


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

PAGES = ["Home", "Age", "Income", "Education", "Health", "What predicts memory loss", "Memory tests (NHANES)",
         "Try the tests", "Expectations vs data", "Class poll", "Risk checker"]
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
st.sidebar.caption("Memory tests page: CDC NHANES 2011-2014, people 60+ who did memory tests "
                   "(dementia screening tests, not a diagnosis).")
st.sidebar.caption("Source: CDC BRFSS 2023-2024 and NHANES 2011-2014, free on cdc.gov. "
                   "Student project, not endorsed by CDC.")

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
              ("What predicts it?", "What predicts memory loss"), ("Memory tests", "Memory tests (NHANES)")]
    for col, (label, target) in zip(st.columns(len(topics)), topics):
        col.button(label, on_click=go, args=(target,), key=f"btn_{target}", width="stretch")
    c1, c2 = st.columns(2)
    c1.button("Risk checker: which factors matter for a person like this?", on_click=go,
              args=("Risk checker",), key="btn_risk", width="stretch")
    c2.button("Try the NHANES-style memory tests yourself", on_click=go,
              args=("Try the tests",), key="btn_try", width="stretch")
    c3, c4 = st.columns(2)
    c3.button("Expectations vs data: what did you expect?", on_click=go, args=("Expectations vs data",), key="btn_expect",
              width="stretch")
    c4.button("Class poll: is memory loss only about age?", on_click=go, args=("Class poll",), key="btn_poll",
              width="stretch")

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

# ---- Memory tests: BRFSS (people say) vs NHANES (people tested) ----
elif page == "Memory tests (NHANES)":
    home_button()
    st.header("BRFSS asks people about their memory. NHANES tests it.")
    st.write("Using both lets me check whether the answer is the same.")

    nh = compare[(compare["item"] == "1 Everyone") & (compare["measure"] == NHANES_LABEL)].set_index("group")["pct"]
    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("**BRFSS 2023-24** (people say)<br>Phone survey, 208,171 people aged 45+.<br>"
                    "\"Is your memory getting worse?\" Yes or no.", unsafe_allow_html=True)
    with c2.container(border=True):
        st.markdown("**NHANES 2011-14** (people tested)<br>Health exam, 2,934 people aged 60+.<br>"
                    "Word list, animal naming, symbol matching.", unsafe_allow_html=True)
    with c3.container(border=True):
        st.markdown(f'<div class="kpi"><div class="num">{nh["1 Younger"]:.1f}% vs {nh["2 Older"]:.1f}%</div>'
                    '<div class="lbl">low test score at 60-69 vs 70+</div></div>', unsafe_allow_html=True)

    d = compare.copy()
    d["item"] = d["item"].str[2:]
    order = d["item"].drop_duplicates().tolist()
    cols = st.columns(2)
    for col, (grp, title) in zip(cols, [("1 Younger", "Younger (BRFSS 45-64, NHANES 60-69)"),
                                        ("2 Older", "Older (BRFSS 65+, NHANES 70+)")]):
        g = d[d["group"] == grp]
        bars = alt.Chart(g).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("pct:Q", title="%", scale=alt.Scale(domain=[0, 70])),
            y=alt.Y("item:N", sort=order, title=None, axis=alt.Axis(labelLimit=200)),
            yOffset=alt.YOffset("measure:N", sort=[BRFSS_LABEL, NHANES_LABEL]),
            color=alt.Color("measure:N", title=None, scale=DATASET_COLORS, legend=alt.Legend(orient="bottom", direction="vertical", labelLimit=400)),
            tooltip=[alt.Tooltip("item:N", title="Group"), alt.Tooltip("measure:N", title="Dataset"),
                     alt.Tooltip("pct:Q", title="%", format=".1f"),
                     alt.Tooltip("people:Q", title="People", format=",")],
        ).properties(height=460, title=title)
        labels = bars.mark_text(align="left", dx=3, color=MUTED, fontSize=11).encode(
            text=alt.Text("pct:Q", format=".1f"))
        col.altair_chart(bars + labels, width="stretch")

    st.success("**Both agree:** low income, depression, stroke and no exercise go with worse memory. "
               "**The twist:** age matters much more when memory is tested (NHANES) than when people judge "
               "their own memory (BRFSS).")
    st.caption("Blue = BRFSS: people say their memory is getting worse. Orange = NHANES: bottom 25% on dementia "
               "screening tests (not a diagnosis). Different people, different years and different age groups, "
               "so compare the patterns, not the exact numbers. Lowest income = under \\$15k (BRFSS) and under "
               "\\$25k (NHANES); highest = \\$200k+ and \\$100k+.")

# ---- Try the tests: own demo versions of the 3 NHANES tests (nothing is saved) ----
elif page == "Try the tests":
    import random
    import time

    home_button()
    st.header("Try the NHANES-style memory tests")
    st.warning("**Short versions of the 3 NHANES tests, to show how they work. Not a real test and not a diagnosis.** These are my own "
               "simple versions (own words and symbols), not the official NHANES test forms. "
               "Nothing you type is saved.")
    ss = st.session_state

    def timer_text(start_key, limit):
        left = limit - (time.time() - ss[start_key])
        return f"⏱️ **{max(0, int(left))} seconds left**" if left > 0 else "⏱️ **Time is up!**"

    tab1, tab2, tab3 = st.tabs(["1. Word recall (memory)", "2. Animal naming (language)",
                                "3. Symbol matching (speed)"])

    # -- 1. Word recall: like the CERAD word list (learn 10 words, recall them later) --
    with tab1:
        WORDS = ["apple", "river", "chair", "candle", "garden", "window", "tiger", "button", "cloud", "ticket"]
        step = ss.setdefault("wr_step", "start")
        if step == "start":
            st.write("You will see **10 words**. Read them, then answer two easy questions. "
                     "After that, type all the words you remember.")
            if st.button("Start", key="wr_start"):
                ss.wr_step = "show"
                st.rerun()
        elif step == "show":
            st.subheader("Remember these words")
            cols = st.columns(5)
            for i, w in enumerate(WORDS):
                cols[i % 5].markdown(f"<div class='kpi'><div class='num' style='font-size:1.6rem'>{w}</div></div>",
                                     unsafe_allow_html=True)
            if st.button("I have read them", key="wr_read"):
                ss.wr_step = "distract"
                st.rerun()
        elif step == "distract":
            st.subheader("Two quick questions first")
            a = st.number_input("What is 7 + 8?", step=1, value=None, key="wr_q1")
            b = st.number_input("What is 20 - 6?", step=1, value=None, key="wr_q2")
            if st.button("Next", key="wr_next", disabled=a is None or b is None):
                ss.wr_step = "recall"
                st.rerun()
        elif step == "recall":
            st.subheader("Now type the words you remember")
            typed = st.text_area("Words (separate them with spaces or commas)", key="wr_typed")
            if st.button("Check my answer", key="wr_check"):
                got = {w.strip(" .,;").lower() for w in typed.replace(",", " ").split()} & set(WORDS)
                ss.wr_score = len(got)
                ss.wr_step = "result"
                st.rerun()
        else:
            st.metric("Words remembered", f"{ss.wr_score} out of 10")
            st.info("**The real test:** NHANES used the CERAD word list. People learn 10 words over 3 tries and "
                    "recall them a few minutes later. It measures **memory**, which is often the first thing to "
                    "change in Alzheimer's disease.")
            if st.button("Try again", key="wr_again"):
                ss.wr_step = "start"
                st.rerun()

    # -- 2. Animal naming: like the animal fluency test (as many animals as possible in 60 seconds) --
    with tab2:
        if "an_start" not in ss:
            st.write("Name **as many different animals as you can in 60 seconds**. Type them with spaces or commas.")
            if st.button("Start the 60 seconds", key="an_go"):
                ss.an_start = time.time()
                st.rerun()
        elif "an_score" not in ss:
            @st.fragment(run_every=1)
            def an_timer():
                st.markdown(timer_text("an_start", 60))
            an_timer()
            typed = st.text_area("Animals", key="an_typed", height=150)
            if st.button("Done", key="an_done"):
                used = time.time() - ss.an_start
                ss.an_score = len({w.strip(" .,;").lower() for w in typed.replace(",", " ").split() if w.strip(" .,;")})
                ss.an_late = used > 65
                st.rerun()
        else:
            st.metric("Different words typed", ss.an_score)
            if ss.an_late:
                st.caption("You went over 60 seconds, so this is just for fun.")
            st.info("**The real test:** in NHANES a tester says \"name as many animals as you can\" and counts the "
                    "different animals in 1 minute. It measures **language and thinking speed**. "
                    "(This demo counts every different word, it does not check that they are animals.)")
            if st.button("Try again", key="an_again"):
                for k in ["an_start", "an_score", "an_late", "an_typed"]:
                    ss.pop(k, None)
                st.rerun()

    # -- 3. Symbol matching: like the DSST (match numbers to symbols as fast as possible) --
    with tab3:
        KEY = {1: "▲", 2: "●", 3: "■", 4: "★", 5: "◆", 6: "✚", 7: "♥", 8: "▼", 9: "◯"}
        LIMIT = 60
        st.write("Each number has its own symbol. Click the right symbol for each number, "
                 f"as many as you can in **{LIMIT} seconds**.")
        st.markdown(" &nbsp; &nbsp; ".join(f"**{n}** = {s}" for n, s in KEY.items()))
        if "sy_start" not in ss:
            if st.button("Start", key="sy_go"):
                ss.sy_start, ss.sy_right, ss.sy_wrong = time.time(), 0, 0
                ss.sy_num = random.randint(1, 9)
                st.rerun()
        else:
            over = time.time() - ss.sy_start > LIMIT

            @st.fragment(run_every=1)
            def sy_timer():
                st.markdown(timer_text("sy_start", LIMIT))
                if time.time() - ss.sy_start > LIMIT and not ss.get("sy_done"):
                    ss.sy_done = True  # time is up: redraw the whole page once to show the score
                    st.rerun(scope="app")
            if not over:
                sy_timer()

            if not over:
                st.markdown(f"<div class='kpi'><div class='num'>{ss.sy_num}</div>"
                            "<div class='lbl'>Which symbol?</div></div>", unsafe_allow_html=True)

                def answer(sym):
                    if time.time() - ss.sy_start > LIMIT:
                        return
                    if KEY[ss.sy_num] == sym:
                        ss.sy_right += 1
                    else:
                        ss.sy_wrong += 1
                    ss.sy_num = random.randint(1, 9)

                for col, sym in zip(st.columns(9), KEY.values()):
                    col.button(sym, key=f"sy_{sym}", on_click=answer, args=(sym,), width="stretch")
                st.caption(f"Right so far: {ss.sy_right}")
            else:
                c1, c2 = st.columns(2)
                c1.metric("Right", ss.sy_right)
                c2.metric("Wrong", ss.sy_wrong)
                st.info("**The real test:** NHANES used the Digit Symbol Substitution Test (DSST). People copy "
                        "symbols under numbers for 2 minutes. It measures **attention and speed**, which slow "
                        "down with age and with problems like stroke.")
                if st.button("Try again", key="sy_again"):
                    for k in ["sy_start", "sy_right", "sy_wrong", "sy_num", "sy_done"]:
                        ss.pop(k, None)
                    st.rerun()

    st.caption("In NHANES 2011-2014, people aged 60+ did these three tests. In this project, a low test score "
               "means the bottom 25% of the combined score. See the Memory tests page.")

# ---- Expectations vs data: write down what you expect, then compare with the results ----
elif page == "Expectations vs data":
    home_button()
    st.header("What did you expect? Compare it with the data")
    st.write("Four questions about the results. Choose what you expect, then click **Show the data**.")
    ss = st.session_state
    young_pct, old_pct = groups.loc["Younger (45-64)", "memory_loss_pct"], groups.loc["Older (65+)", "memory_loss_pct"]
    inc_young = by_inc[by_inc["group"] == GROUPS[0]]["memory_loss_pct"]
    low_inc, high_inc = inc_young.iloc[0], inc_young.iloc[-1]
    nh = compare[(compare["item"] == "1 Everyone") & (compare["measure"] == NHANES_LABEL)].set_index("group")["pct"]
    dep_or = odds[(odds["group"] == GROUPS[0]) & (odds["factor"] == "Depression")]["OR"].iloc[0]

    def question(n, text, guess_widget, answer_md):
        with st.container(border=True):
            st.subheader(f"Question {n}")
            st.write(text)
            guess = guess_widget()
            if st.button("Show the data", key=f"q{n}_show"):
                ss[f"q{n}_open"] = True
            if ss.get(f"q{n}_open"):
                st.success(answer_md(guess))

    question(1, "Out of 100 people aged **45-64**, how many say their memory is getting worse?",
             lambda: st.slider("What you expect", 0, 60, 5, key="q1"),
             lambda g: f"You expected **{g}**. The data says **{young_pct:.0f}** ({young_pct:.1f}%). "
                       f"That is almost the same as people aged 65+ ({old_pct:.1f}%). "
                       "So memory loss is **not only an old-age problem**.")

    question(2, "Among people aged 45-64 with the **lowest income** (under \\$15k), how many out of 100 say "
                "their memory is getting worse?",
             lambda: st.slider("What you expect", 0, 60, 15, key="q2"),
             lambda g: f"You expected **{g}**. The data says **{low_inc:.0f}** ({low_inc:.1f}%). With the highest "
                       f"income (\\$200k+) it is only **{high_inc:.1f}%**, almost 4 times less.")

    q3_opts = ["When people judge their own memory (BRFSS)", "When memory is tested (NHANES)", "Both the same"]
    question(3, "When does **age** make a bigger difference?",
             lambda: st.radio("What you expect", q3_opts, index=None, key="q3"),
             lambda g: ("✅ As you expected. " if g == q3_opts[1] else "") +
                       f"**When memory is tested.** Low test scores: {nh['1 Younger']:.1f}% at 60-69 vs "
                       f"{nh['2 Older']:.1f}% at 70+. What people say: {young_pct:.1f}% at 45-64 vs "
                       f"{old_pct:.1f}% at 65+.")

    q4_opts = ["Age", "Depression", "Smoking", "Being overweight"]
    question(4, "For people aged 45-64, which of these goes with memory loss the **most**?",
             lambda: st.radio("What you expect", q4_opts, index=None, key="q4"),
             lambda g: ("✅ As you expected. " if g == q4_opts[1] else "") +
                       f"**Depression**: about **{dep_or:.1f} times the odds**, after taking income, health and "
                       "the other factors into account. Within 45-64, age itself hardly matters, and smoking "
                       "and being overweight showed no clear link.")

    st.caption("Answers come from the BRFSS 2023-2024 and NHANES 2011-2014 results in this app. Links, not causes.")

# ---- Class poll: live votes shared by everyone who opens the app ----
elif page == "Class poll":
    import threading

    @st.cache_resource
    def poll_store():
        """One shared vote counter for all visitors (in memory, no names, gone when the app restarts)."""
        return {"lock": threading.Lock(),
                "votes": {"Start": {"Yes": 0, "No": 0}, "End": {"Yes": 0, "No": 0}}}

    store = poll_store()
    ss = st.session_state
    home_button()
    st.header("Class poll: is memory loss only about age?")
    st.write("Vote once at the **start** of the talk and once at the **end**. Did anyone change their mind?")

    def vote(rnd, answer):
        if ss.get(f"voted_{rnd}"):
            return
        with store["lock"]:
            store["votes"][rnd][answer] += 1
        ss[f"voted_{rnd}"] = answer

    c1, c2 = st.columns(2)
    for col, rnd, title in [(c1, "Start", "Before the talk"), (c2, "End", "After the talk")]:
        with col.container(border=True):
            st.subheader(title)
            if ss.get(f"voted_{rnd}"):
                st.write(f"Thanks! You voted **{ss[f'voted_{rnd}']}**.")
            else:
                b1, b2 = st.columns(2)
                b1.button("Yes, only age", key=f"poll_{rnd}_yes", on_click=vote, args=(rnd, "Yes"),
                          width="stretch")
                b2.button("No, other things too", key=f"poll_{rnd}_no", on_click=vote, args=(rnd, "No"),
                          width="stretch")

    @st.fragment(run_every=2)
    def poll_results():
        with store["lock"]:
            v = {r: dict(a) for r, a in store["votes"].items()}
        st.subheader("Live results")
        cols = st.columns(2)
        for col, rnd, title in [(cols[0], "Start", "Before the talk"), (cols[1], "End", "After the talk")]:
            total = sum(v[rnd].values())
            no_pct = round(100 * v[rnd]["No"] / total) if total else 0
            with col.container(border=True):
                st.markdown(f"**{title}** ({total} vote{'' if total == 1 else 's'})")
                st.markdown(f'<div class="kpi"><div class="num">{no_pct}%</div>'
                            '<div class="lbl">say <b>no, other things too</b></div></div>', unsafe_allow_html=True)
                st.progress(no_pct / 100)
                st.caption(f"Yes, only age: {v[rnd]['Yes']} · No, other things too: {v[rnd]['No']}")
        st.caption(f"Before: {sum(v['Start'].values())} votes · After: {sum(v['End'].values())} votes. "
                   "Updates every 2 seconds.")

    poll_results()
    with st.expander("For the presenter"):
        st.write("Clear all votes before the talk. Votes are only counted (no names) and are lost "
                 "when the app restarts.")
        if st.button("Reset all votes", key="poll_reset"):
            with store["lock"]:
                store["votes"] = {"Start": {"Yes": 0, "No": 0}, "End": {"Yes": 0, "No": 0}}
            for k in ["voted_Start", "voted_End"]:
                ss.pop(k, None)
            st.rerun()

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
