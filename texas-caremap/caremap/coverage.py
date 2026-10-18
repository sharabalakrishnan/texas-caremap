"""Coverage guide: a small rules engine that suggests programs worth checking.

This never decides eligibility. It compares a household's income to each
program's published income limit and sorts programs into three groups:

  likely    - income is clearly under the limit, so it's worth applying
  check     - income is within CLOSE_BAND points of the limit, so apply and let the
              program decide (deductions and monthly income rules can tip it either way)
  unlikely  - income is clearly over the limit, or the person isn't in the group served
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

PROGRAMS_FILE = Path(__file__).resolve().parent.parent / "data" / "programs.json"

# Programs count income in different ways (monthly vs yearly, certain
# deductions), so anything within this many percentage points of a limit is
# treated as "close" rather than a clear yes or no.
CLOSE_BAND = 10.0

LIKELY, CHECK, UNLIKELY = "likely", "check", "unlikely"


def load_programs(path: Path = PROGRAMS_FILE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def poverty_line(household_size: int, guidelines: dict) -> float:
    """Yearly federal poverty guideline (100% FPL) for a household of this size."""
    if household_size < 1:
        raise ValueError("Household size must be at least 1.")
    return guidelines["base"] + guidelines["per_additional_person"] * (household_size - 1)


def fpl_percent(yearly_income: float, household_size: int, guidelines: dict) -> float:
    """Household income as a percentage of the federal poverty level."""
    if yearly_income < 0:
        raise ValueError("Income can't be negative.")
    return 100.0 * yearly_income / poverty_line(household_size, guidelines)


def income_at_percent(percent: float, household_size: int, guidelines: dict) -> float:
    """The yearly income that equals `percent` of FPL for this household size."""
    return poverty_line(household_size, guidelines) * percent / 100.0


def compare_to_limit(fpl: float, limit: float) -> str:
    if fpl <= limit - CLOSE_BAND:
        return LIKELY
    if fpl <= limit + CLOSE_BAND:
        return CHECK
    return UNLIKELY


@dataclass
class Household:
    age: int                      # age of the person who needs coverage
    household_size: int
    yearly_income: float          # total household income before taxes
    pregnant: bool = False
    female: bool = False
    parent_or_caretaker: bool = False   # lives with and cares for a child under 19
    has_job_coverage: bool = False      # offered health insurance through a job


@dataclass
class Suggestion:
    key: str
    name: str
    status: str
    reason: str
    cost: str = ""
    apply_url: str = ""
    info_url: str = ""
    limit_income: float | None = None   # yearly income at this program's limit


@dataclass
class Guidance:
    fpl_percent: float
    suggestions: list[Suggestion] = field(default_factory=list)
    coverage_gap: bool = False
    notes: list[str] = field(default_factory=list)

    def by_status(self, status: str) -> list[Suggestion]:
        return [s for s in self.suggestions if s.status == status]


def _suggest(key: str, programs: dict, status: str, reason: str, limit: float | None,
             household: Household, guidelines: dict) -> Suggestion:
    p = programs[key]
    limit_income = (
        income_at_percent(limit, household.household_size, guidelines) if limit is not None else None
    )
    return Suggestion(
        key=key, name=p["name"], status=status, reason=reason, cost=p.get("cost", ""),
        apply_url=p.get("apply_url", ""), info_url=p.get("info_url", ""), limit_income=limit_income,
    )


def _limit_reason(fpl: float, limit: float, status: str, approximate: bool = False) -> str:
    about = "about " if approximate else ""
    if status == LIKELY:
        return f"Your household income is under this program's limit ({about}{limit:g}% of the poverty level)."
    if status == CHECK:
        return (f"Your household income is close to this program's limit ({about}{limit:g}% of the "
                f"poverty level). Apply and let the program decide.")
    return f"Your household income looks higher than this program's limit ({about}{limit:g}% of the poverty level)."


def child_medicaid_limit(age: int, limits: dict) -> float:
    if age < 1:
        return limits["under_1"]
    if age <= 5:
        return limits["age_1_5"]
    return limits["age_6_18"]


def guide(household: Household, config: dict | None = None) -> Guidance:
    """Suggest coverage programs for one person in a household."""
    config = config or load_programs()
    g = config["poverty_guidelines"]
    programs = config["programs"]
    if household.age < 0 or household.age > 120:
        raise ValueError("Age must be between 0 and 120.")
    if household.household_size < 1:
        raise ValueError("Household size must be at least 1.")

    fpl = fpl_percent(household.yearly_income, household.household_size, g)
    result = Guidance(fpl_percent=fpl)
    add = result.suggestions.append

    def by_income(key: str, limit: float, approximate: bool = False):
        status = compare_to_limit(fpl, limit)
        add(_suggest(key, programs, status, _limit_reason(fpl, limit, status, approximate), limit, household, g))
        return status

    age = household.age

    # Children and teens (under 19): Medicaid first, then CHIP.
    if age < 19:
        med_limit = child_medicaid_limit(age, programs["children_medicaid"]["limits_by_age"])
        med_status = by_income("children_medicaid", med_limit)
        chip_limit = programs["chip"]["limit"]
        if med_status == LIKELY:
            add(_suggest("chip", programs, UNLIKELY,
                         "Children who qualify for Medicaid get Medicaid instead of CHIP.",
                         chip_limit, household, g))
        else:
            by_income("chip", chip_limit)

    # Pregnancy
    if household.pregnant:
        by_income("pregnancy_medicaid", programs["pregnancy_medicaid"]["limit"])

    # Healthy Texas Women (not for people who already get Medicaid or CHIP)
    htw = programs["healthy_texas_women"]
    on_medicaid_or_chip = any(
        s.status == LIKELY and s.key in ("children_medicaid", "chip", "pregnancy_medicaid")
        for s in result.suggestions
    ) or (
        household.parent_or_caretaker and 19 <= age < 65
        and compare_to_limit(fpl, programs["parent_medicaid"]["limit"]) == LIKELY
    )
    if household.female and htw["min_age"] <= age <= htw["max_age"]:
        if on_medicaid_or_chip and not household.pregnant:
            add(_suggest("healthy_texas_women", programs, UNLIKELY,
                         "People who get Medicaid or CHIP can't also get Healthy Texas Women. "
                         "Medicaid and CHIP already cover women's health and family planning.",
                         htw["limit"], household, g))
        elif household.pregnant:
            add(_suggest("healthy_texas_women", programs, UNLIKELY,
                         "This program is for women who are not pregnant. Pregnancy Medicaid covers pregnancy care.",
                         htw["limit"], household, g))
        else:
            by_income("healthy_texas_women", htw["limit"])
            if age < 18:
                result.notes.append("For Healthy Texas Women, a parent or guardian applies for teens ages 15 to 17.")

    # Adults 19 to 64
    if 19 <= age < 65:
        if household.parent_or_caretaker:
            by_income("parent_medicaid", programs["parent_medicaid"]["limit"], approximate=True)

        mp = programs["marketplace"]
        medicaid_likely = any(s.status == LIKELY and s.key in ("pregnancy_medicaid", "parent_medicaid")
                              for s in result.suggestions)
        if medicaid_likely:
            add(_suggest("marketplace", programs, UNLIKELY,
                         "If you qualify for Medicaid, you usually can't get Marketplace tax credits. "
                         "Apply for Medicaid first.", None, household, g))
        elif household.has_job_coverage:
            add(_suggest("marketplace", programs, UNLIKELY,
                         "If a job offers you affordable coverage, you usually can't get Marketplace tax credits. "
                         "Check your job's plan first.", None, household, g))
        elif fpl < mp["subsidy_min"]:
            add(_suggest("marketplace", programs, UNLIKELY,
                         "Marketplace tax credits start at 100% of the poverty level, so income this low usually "
                         "doesn't qualify for help paying premiums.", mp["subsidy_min"], household, g))
        elif fpl <= mp["subsidy_max"]:
            add(_suggest("marketplace", programs, LIKELY,
                         "Your income is in the range where tax credits lower your monthly premium.",
                         mp["subsidy_max"], household, g))
        else:
            add(_suggest("marketplace", programs, CHECK,
                         "You can buy a Marketplace plan, but above 400% of the poverty level you pay full price.",
                         mp["subsidy_max"], household, g))

        # Texas did not expand Medicaid, so many low-income adults fall in a gap.
        parent_ok = household.parent_or_caretaker and fpl <= programs["parent_medicaid"]["limit"] + CLOSE_BAND
        if fpl < 100 and not household.pregnant and not parent_ok and not household.has_job_coverage:
            result.coverage_gap = True

    # Seniors
    if age >= 65:
        add(_suggest("medicare", programs, LIKELY, "Most people 65 and older can get Medicare.",
                     None, household, g))

    # Everyone can use a community health center.
    add(_suggest("health_centers", programs, LIKELY,
                 "Health centers see everyone. If your income is low, you pay a reduced fee.",
                 None, household, g))

    order = {LIKELY: 0, CHECK: 1, UNLIKELY: 2}
    result.suggestions.sort(key=lambda s: (order[s.status], s.key == "health_centers"))
    return result
