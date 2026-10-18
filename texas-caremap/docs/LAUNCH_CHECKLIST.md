# Launch Checklist: from this folder to a submitted app

**Hard deadline: Monday, Oct 26, 2026 at 12:00 PM Eastern = 11:00 AM Central (Austin).**
Target: submitted by **Sunday, Oct 25**.

---

## Step 1 · Confirm eligibility (10 minutes, do first)
- [ ] Find the congressional district for home **and** school address (house.gov "Find Your Representative").
- [ ] Check that district's office is hosting the 2026 challenge (congressionalappchallenge.us lists participating districts).
- [ ] Register on the student portal: congressionalappchallenge.us → Students → Register.
- [ ] Note what the portal asks for (video length limit, fields, file types). Adjust the docs if it differs.

## Step 2 · Build the real data (15 minutes)
On a home computer with normal internet:
```bash
cd texas-caremap
python -m pip install -r requirements.txt
python scripts/build_data.py
```
- [ ] It prints about 700 Texas sites and 254 counties with no errors.
- [ ] `data/processed/` now has `clinics_tx.csv` and `county_uninsured_tx.csv`.
- [ ] If the Census step fails with "layout changed," the message lists the columns found; the parser in `parse_sahie()` needs those names. Clinics can still be built alone with `--only clinics`.

## Step 3 · Run the tests and the app (15 minutes)
```bash
python -m pytest -q          # expect: 67 passed
streamlit run app.py
```
- [ ] The red "Sample data" banner is **gone**.

## Step 4 · Hands-on testing (45 minutes; ask 2-3 people to try it too)

**Find a clinic**
| Try | Expect |
|---|---|
| 78701 (Austin), 25 mi | Many sites, map with blue dots, cards sorted by distance |
| `77002-1234` (Houston, ZIP+4) | Accepts it and searches 77002 |
| 79848 (Sanderson), 25 mi | "No sites within 25 miles… closest ones anyway" |
| 79901 (El Paso), 78520 (Brownsville) | Results; spot-check one address on Google Maps |
| 10001 (New York) | "doesn't look like a Texas ZIP code" |
| 123 | "Please enter a 5-digit ZIP code" |
| "Only 40+ hours" filter | Fewer results |

- [ ] **The clinic map shows a street map zoomed to the area, with blue dots.** (It could not be checked in the build environment, which had no graphics; check on a laptop **and** a phone.)
- [ ] Click **Directions** on two cards: Google Maps opens to the right address.
- [ ] Click **Phone & hours** on two cards: Google Maps opens that clinic's listing with its phone number.

**Coverage guide**
| Person | Expect |
|---|---|
| Age 8, household 4, $50,000/year | CHIP: worth applying. Children's Medicaid: probably not |
| Age 8, household 4, $25,000/year | Children's Medicaid: worth applying |
| Age 0 (baby), household 3, $45,000/year | Children's Medicaid (higher infant limit) |
| Age 30, household 1, $12,000/year | Coverage-gap warning; health centers |
| Age 30, household 1, $30,000/year | Marketplace: worth applying |
| Age 25, female, pregnant, household 2, $30,000 | Medicaid for Pregnant Women |
| Age 25, female, household 2, $30,000 | Healthy Texas Women |
| Age 70 | Medicare |
| Monthly income $2,500 | Shows $30,000 a year |

- [ ] Click **every** "How to apply" and "Learn more" button; each opens a working official page. If a Texas HHS page has moved, update its URL in `data/programs.json`.

**Texas access gaps**
- [ ] Map shows all of Texas in blue shades; hover works; all four "Color the map by" options work.
- [ ] Top-counties chart and table load; CSV download opens in Excel/Sheets.
- [ ] District table looks right (Texas has 38 districts).
- [ ] Write down 1-2 real findings for the video (e.g., which region has the darkest counties).

**General**
- [ ] Everything readable on a phone; sidebar menu opens from the top-left arrow.
- [ ] About page shows the data download date and SAHIE year.

## Step 5 · Put the code on GitHub (20 minutes)
- [ ] Create a **public** repository named `texas-caremap` on the student's GitHub account.
- [ ] Upload the whole folder **including** `data/processed/` (the live app needs it).
```bash
git init
git add .
git commit -m "Texas CareMap"
git branch -M main
git remote add origin https://github.com/<username>/texas-caremap.git
git push -u origin main
```

## Step 6 · Deploy the live app (15 minutes, free)
- [ ] Go to share.streamlit.io, sign in with GitHub.
- [ ] Create app → repository `texas-caremap`, branch `main`, main file `app.py`.
- [ ] Optional: set a custom subdomain like `texas-caremap`.
- [ ] Open the live link on a phone and repeat a few tests from Step 4.
- [ ] Note: free apps go to sleep after a few days without visitors. **Open the link the morning of judging** and again before submitting so it's awake. The demo video is the backup.

## Step 7 · Screenshots (10 minutes)
- [ ] Find a clinic with results, Coverage guide with results, Texas access gaps map. Save as PNGs (for the README and portal if requested).

## Step 8 · Record the demo video (1-2 hours with practice)
- [ ] Follow `DEMO_VIDEO_SCRIPT.md`. Keep it within the portal's time limit.
- [ ] Upload to YouTube as **Unlisted**. Check the link in a private/incognito window.

## Step 9 · Fill in the submission (30 minutes)
- [ ] Copy answers from `SUBMISSION_ANSWERS.md`; fill every **[bracket]**.
- [ ] Write the "What did you learn?" answer personally.
- [ ] Complete the AI disclosure.
- [ ] Paste the live app, GitHub, and video links; click each from the form preview.
- [ ] Submit by **Sunday, Oct 25**. Screenshot the confirmation page/email.

## Before judging (Nov–Dec)
- [ ] Be ready to explain: the haversine formula, how the Access Gap Score is calculated, why percentile ranks, what a 90% confidence interval means, why Texas has a coverage gap.
- [ ] Every January: update `poverty_guidelines` in `data/programs.json` and rerun `scripts/build_data.py`.
