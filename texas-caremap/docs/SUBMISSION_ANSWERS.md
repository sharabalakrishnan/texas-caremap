# Congressional App Challenge 2026: Submission Answers

Draft answers for the submission form. Text in **[brackets]** needs the student's own details. Read every answer aloud once: judges may ask about anything written here.

**Deadline: Monday, October 26, 2026 at 12:00 PM Eastern = 11:00 AM in Austin.** Aim to submit Sunday, October 25.

---

## App title
Texas CareMap

## One-line description
Texas CareMap helps uninsured Texans find the nearest low-cost community health center, see which coverage programs may fit their family, and shows where in Texas people live farthest from care.

## Platform and languages
- Platform: Web app (works on phones, tablets, and computers)
- Language: Python
- Libraries: Streamlit (interface), pandas and NumPy (data analysis), Plotly (maps and charts), pytest (testing)

## Links
- Live app: **[Streamlit Community Cloud URL]**
- Source code: **[GitHub repository URL]**
- Demo video: **[YouTube or Vimeo URL, unlisted]**

---

## What problem does your app solve?

Texas has the highest uninsured rate of any state: 16.7% of Texans had no health insurance in 2024, according to the U.S. Census Bureau. Two things make this worse than it needs to be. First, many people don't know that federally funded community health centers see everyone, with or without insurance, and charge reduced fees based on income. Second, the coverage rules are confusing. Texas did not expand Medicaid, so the rules depend heavily on age, pregnancy, and whether you have children, and many families don't realize their kids may qualify for free or low-cost coverage even when the parents don't.

Texas CareMap answers two questions in under a minute: "Where can I get care near me?" and "What coverage should I apply for?" It also gives decision-makers a county-by-county picture of where uninsured Texans live far from a health center.

**[Optional, one or two sentences in your own words: why this matters to you, or a moment that made you notice the problem.]**

---

## How does your app work?

The app has three main screens.

**1. Find a clinic.** The user enters a ZIP code and how far they can travel. The app converts the ZIP code to a map location, then uses the haversine formula to measure the distance to every health center site in Texas (about 700 sites from the federal Health Resources and Services Administration). Results appear on a map and as cards with distance, hours, and a directions link. In rural areas where nothing is close, the app still shows the closest sites instead of an empty page.

**2. Coverage guide.** The user enters age, household size, and income. The app converts income into a percentage of the 2026 federal poverty level and runs it through a rules engine for Texas programs: Children's Medicaid (whose limit changes with age), CHIP, Medicaid for Pregnant Women, Healthy Texas Women, Medicaid for parents, Marketplace tax credits, and Medicare. Programs are sorted into "worth applying," "close to the limit, apply and let them decide," and "probably not." The app identifies people who fall into Texas's coverage gap and points them to community health centers. It always says it is a guide, not an eligibility decision.

**3. Texas access gaps.** For all 254 counties, the app combines Census uninsured estimates with the health center data and calculates an original Access Gap Score. It averages three percentile ranks: the uninsured rate, the typical distance from homes to the nearest site, and the number of sites per 10,000 uninsured people. The results appear on a color-coded county map, a ranked chart, and a downloadable table that shows each estimate's 90% confidence interval and flags counties where the estimate is less certain. A table also counts health center sites in each congressional district.

**Privacy:** there are no accounts, nothing is saved, and all data is downloaded ahead of time, so a user's ZIP code and income are never sent to any other service.

---

## What technical difficulty did you face, and how did you solve it?

**1. Making the county map work everywhere.** The first version of the county map came up blank on a restricted network. The cause was the charting library: its built-in map type quietly downloads a world outline from the internet every time it loads, and some networks, like many school networks, block that. The fix was to draw each of Texas's 254 county boundaries directly as filled shapes from the Census boundary file. That meant grouping counties into color classes with equal numbers of counties, adding invisible points at each county's center so hovering still shows details, and correcting for the fact that a degree of longitude is shorter than a degree of latitude at Texas's latitude, so the state doesn't look stretched. The map now needs nothing from the internet.

**2. Turning eligibility rules into code without overpromising.** Program rules interact in ways that are easy to get wrong. For example, Healthy Texas Women covers women 15 to 44, but not anyone already on Medicaid or CHIP. An early version suggested it to a 16-year-old who already qualified for Children's Medicaid; testing caught it, and the rule was fixed and given its own test. The rules engine is checked by more than 20 automated tests, including incomes right at each limit, and it has a "close to the limit" category because programs measure income differently (monthly instead of yearly, with deductions). All limits are stored in one file with their sources, so they can be updated each year without changing code.

**3. Measuring distance to care fairly.** Counting clinics per county is misleading in a state where a county can be bigger than some states. The app measures the distance from every residential ZIP code to its nearest site (about 2,500 ZIP codes times 700 sites) using vectorized NumPy math in chunks, so it runs in under a second. The measures are combined with percentile ranks so that miles (which can be in the hundreds) don't outweigh percentages, and Census margins of error are shown so small, uncertain counties aren't over-interpreted.

---

## What did you learn?

**[Write this in your own words. Some prompts: What surprised you in the data? What did you learn about Texas health coverage? What would you do differently? What was hardest to debug? A judge will be able to tell if this section is real.]**

---

## Future plans

- Spanish version
- Driving and public transit times instead of straight-line distance
- Filters for specific services, such as dental, behavioral health, or pharmacy
- Share the county findings with community health organizations
- **[Your own ideas]**

---

## AI use disclosure
**[To be completed by you.]**
