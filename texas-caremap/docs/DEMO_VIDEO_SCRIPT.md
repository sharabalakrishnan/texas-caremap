# Demo Video Script (about 3 minutes)

Record with the **real data** loaded (no red "Sample data" banner), on the live deployed app if possible.

**Setup before recording**
- Browser zoomed to 110-125% so text is readable in the video.
- Close other tabs and turn off notifications.
- Have these ready: ZIP **78701** (downtown Austin), ZIP **79848** (Sanderson, a remote West Texas town), and one code file open in an editor: `caremap/gaps.py` or `caremap/coverage.py`.
- Free tools: OBS Studio, or the built-in recorder (Windows: Win+G; Mac: Shift+Cmd+5). Use a headset mic if possible.
- Upload to YouTube as **Unlisted** and test the link in a private window.

---

## 0:00 – 0:25 · The problem
**Show:** the Home page, then click Find a clinic.

> "Texas has the highest uninsured rate in the country: about one in six Texans had no health insurance in 2024. But many people don't know that community health centers see everyone, with or without insurance, at reduced cost. And the coverage rules are confusing, especially in Texas, which didn't expand Medicaid. I built Texas CareMap to answer two questions fast: where can I get care, and what should I apply for?"

## 0:25 – 1:00 · Find a clinic
**Do:** type 78701, keep 25 miles, Search. Hover a dot on the map. Scroll one card. Click Directions briefly.

> "You type a ZIP code and how far you can travel. The app measures the distance to every federally funded health center site in Texas and shows the closest ones, with hours and directions."

**Do:** change the ZIP to 79848, set distance to 25 miles, Search.

> "In rural West Texas, nothing may be within 25 miles. Instead of an empty page, the app shows the closest sites anyway, because that's the person who needs this most."

## 1:00 – 1:45 · Coverage guide
**Do:** enter age 8, household 4, income $50,000 per year. Show results. Point to the percentage of poverty level and the income limit line.

> "Next, coverage. I enter a child's age, household size, and income. The app compares that to each program's published limit. This eight-year-old's family is above Children's Medicaid but under CHIP, so CHIP is worth applying for. It shows the exact income limit for a family of four."

**Do:** change to age 30, household 1, income $12,000. Show the coverage-gap warning.

> "Now a single adult earning twelve thousand a year. Texas Medicaid doesn't cover most adults without kids, and Marketplace help starts at the poverty line, so this person falls into the coverage gap. The app explains that and sends them to a community health center. And it always says it's a guide, not an eligibility decision."

## 1:45 – 2:30 · Texas access gaps
**Do:** open the page. Point at the four numbers. Hover two or three dark counties. Switch the map to Distance to nearest site, then back. Scroll to the top-counties chart and the district table.

> "This page looks at the whole state. For all 254 counties, the app combines Census uninsured estimates with the health center data into an Access Gap Score: the uninsured rate, how far homes are from the nearest site, and how many sites there are per uninsured person. Darker counties have the biggest gaps. [Name one or two real findings you see, e.g. which region stands out.] The table shows Census confidence intervals, so small counties with uncertain estimates are flagged. There's also a count of sites in each congressional district."

## 2:30 – 2:55 · The code and the hard part
**Show:** the code file, then the test run (`python -m pytest -q`, 67 passed).

> "The hardest technical problem: the charting library's built-in map quietly downloads files from the internet, and it showed up blank on a restricted network, like a lot of school Wi-Fi. The app now draws all 254 county boundaries directly from Census data, so it works anywhere. The project has 67 automated tests covering the distance math, every coverage rule, and each screen."

## 2:55 – 3:00 · Close
> "Texas CareMap: find care, find coverage, and find the gaps. Thank you."

---

**Tips**
- Practice once with a timer. If you run long, shorten the access-gaps section first.
- Speak to the judges like you're explaining it to a friend; you don't have to read word for word.
- Replace the bracketed finding with something you actually notice on the real-data map.
