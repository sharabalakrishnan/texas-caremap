"""Page 2: coverage guide - which programs may fit this person."""

import html

import streamlit as st

from caremap import coverage
from views.style import page_header, section

STATUS_HEADINGS = {
    coverage.LIKELY: ("Worth applying", "Your answers fit these programs' published rules."),
    coverage.CHECK: ("Close to the limit",
                     "Programs count income in their own ways, so these could go either way."),
}


def render():
    config = coverage.load_programs()
    g = config["poverty_guidelines"]

    page_header("Coverage guide", "See what may fit your family.",
                "Answer a few questions. We compare your answers with each program's published rules.")
    st.info(
        "**This is a guide, not an eligibility decision.** Only the program itself can tell you "
        "if you qualify. Your answers stay on this page and aren't saved.",
        icon="🧭",
    )

    with st.form("coverage"):
        st.markdown("**About the person who needs coverage**")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=0, max_value=120, value=16, step=1)
        female = c2.radio("Sex", ["Female", "Male"], horizontal=True,
                          help="Some programs, like Healthy Texas Women, are only for women.") == "Female"
        pregnant = st.checkbox("Currently pregnant")
        parent = st.checkbox("Is a parent or relative caring for a child under 19 at home",
                             help="Only used for adults 19 to 64.")
        job = st.checkbox("Is offered health insurance through a job (theirs or a family member's)")

        st.markdown("**About the household**")
        c3, c4, c5 = st.columns([1, 1, 1])
        size = c3.number_input("People in the household", min_value=1, max_value=15, value=4, step=1,
                               help="Count the people you live with who share income, plus anyone you claim on taxes. "
                                    "A pregnant woman counts as herself plus the number of babies expected.")
        period = c4.radio("Income is", ["Per year", "Per month"], horizontal=True)
        income = c5.number_input("Total household income before taxes ($)", min_value=0, value=40000,
                                 step=500, format="%d")
        submitted = st.form_submit_button("Show my options", type="primary")

    if not submitted:
        st.caption(f"Uses the {g['year']} federal poverty guidelines. Program rules last checked "
                   f"{config['last_reviewed']}.")
        return

    yearly = income * 12 if period == "Per month" else income
    household = coverage.Household(
        age=int(age), household_size=int(size), yearly_income=float(yearly), pregnant=pregnant,
        female=female, parent_or_caretaker=parent, has_job_coverage=job,
    )
    result = coverage.guide(household, config)

    poverty_line = coverage.poverty_line(int(size), g)
    section("Your results")
    m1, m2 = st.columns(2)
    m1.metric("Household income", f"${yearly:,.0f} a year")
    m2.metric("Compared with the poverty level", f"{result.fpl_percent:.0f}%",
              help=f"The {g['year']} federal poverty level for {int(size)} "
                   f"{'person' if size == 1 else 'people'} is ${poverty_line:,.0f} a year. "
                   "Most programs set their income limits as a percentage of this number.")

    if result.coverage_gap:
        st.warning(
            "**You may fall in Texas's coverage gap.** Texas Medicaid covers very few adults "
            "without children, and Marketplace tax credits start at 100% of the poverty level. "
            "Community health centers are the best option: they charge reduced fees based on income. "
            "Use **Find a clinic** to see the closest ones.",
            icon="⚠️",
        )

    for status in (coverage.LIKELY, coverage.CHECK):
        items = result.by_status(status)
        if not items:
            continue
        heading, sub = STATUS_HEADINGS[status]
        section(heading)
        st.caption(sub)
        for s in items:
            program_card(s, config, int(size))

    unlikely = result.by_status(coverage.UNLIKELY)
    if unlikely:
        with st.expander(f"Programs that probably don't fit ({len(unlikely)})"):
            for s in unlikely:
                program_card(s, config, int(size))

    for note in result.notes:
        st.caption(note)

    mp = config["programs"]["marketplace"]
    st.caption(f"Marketplace open enrollment: {mp['open_enrollment']}. Medicaid and CHIP accept "
               "applications all year.")
    st.caption(f"Income limits use the {g['year']} federal poverty guidelines. Medicaid and CHIP "
               "usually look at monthly income, so a change this month can matter.")


def program_card(s: coverage.Suggestion, config: dict, size: int):
    p = config["programs"][s.key]
    with st.container(border=True):
        st.markdown(f'<div class="tc-card tc-card-name">{html.escape(s.name)}</div>', unsafe_allow_html=True)
        st.write(s.reason)
        lines = []
        if p.get("who"):
            lines.append(f"Who it's for: {p['who']}")
        people = f"{size} {'person' if size == 1 else 'people'}"
        if s.limit_income and s.key == "marketplace":
            mp = config["programs"]["marketplace"]
            low = coverage.income_at_percent(mp["subsidy_min"], size, config["poverty_guidelines"])
            lines.append(f"Tax credits for {people}: incomes from about \\${low:,.0f} to \\${s.limit_income:,.0f} a year")
        elif s.limit_income:
            lines.append(f"Income limit for {people}: about \\${s.limit_income:,.0f} a year "
                         f"(\\${s.limit_income / 12:,.0f} a month)")
        if s.cost:
            lines.append(f"Cost: {s.cost}")
        st.caption("  \n".join(lines))
        buttons = [(label, url) for label, url in (("How to apply", s.apply_url), ("Learn more", s.info_url)) if url]
        cols = st.columns([1, 1, 2])
        for col, (label, url) in zip(cols, buttons):
            col.link_button(label, url, use_container_width=True)
