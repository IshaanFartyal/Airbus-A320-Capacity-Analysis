# A320-family production ramp scenarios and the rates used for the
# rate sensitivity.
#
# Values are nominal aircraft produced per month, averaged over the
# year. A scenario that shows 75 in 2028 therefore has 2028 as its
# first full year at rate 75.
#
# Every scenario starts from the same 2026 rate and differs from 2027.
# No ramp runs below the base no-investment baseline rate of 55,
# which is set in data/airbus_assumptions.csv


# The scenario all headline results are based on
TARGET_CASE = "target"

RAMPS = {
    # Airbus's stated target: a rate of 70 to 75 by the end of 2027,
    # stabilising at 75 thereafter. This is what Airbus is aiming
    # for, so it assumes the ramp goes to plan.
    "target": {
        2026: 58,
        2027: 68,
        2028: 75,
        2029: 75,
        2030: 75,
        2031: 75,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },

    # A deliberately slower ramp with steps of about 6 a month per
    # year, just above the comfortable step. First full year at
    # rate 75 is 2029.
    "moderate": {
        2026: 58,
        2027: 64,
        2028: 70,
        2029: 75,
        2030: 75,
        2031: 75,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },

    # A gradual ramp with no rate increase above the comfortable
    # annual step, so it pays no expedite cost. First full year at
    # rate 75 is 2030.
    "gradual": {
        2026: 58,
        2027: 62,
        2028: 66,
        2029: 71,
        2030: 75,
        2031: 75,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },

    # The slowest ramp, also with no expedite cost. First full year
    # at rate 75 is 2031.
    "slow": {
        2026: 58,
        2027: 61,
        2028: 65,
        2029: 68,
        2030: 72,
        2031: 75,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },
}

# Display names, in the order the scenarios are reported
RAMP_LABELS = {
    "target": "Airbus target",
    "moderate": "Moderate ramp",
    "gradual": "Gradual ramp",
    "slow": "Slow ramp",
}

# Delays of the Airbus target case, in years
DELAY_YEARS = [1, 2, 3, 4, 5]


RATE_SENSITIVITY = list(range(55, 100))


def get_production_ramp(case=TARGET_CASE):
    if case not in RAMPS:
        raise ValueError(
            "Ramp case must be 'target', 'moderate', 'gradual', or 'slow'"
        )

    return RAMPS[case].copy()


def get_delayed_ramp(delay_years):
    """The Airbus target case with its rate increases pushed back.

    The first year's rate is held for the length of the delay, after
    which the rate follows the same steps as the target case.
    """
    target = get_production_ramp(TARGET_CASE)

    years = list(target.keys())
    rates = list(target.values())

    delayed_rates = [rates[0]] * delay_years + rates

    return dict(zip(years, delayed_rates[:len(years)]))


def first_full_year_at_rate(ramp, monthly_rate):
    """First year in which a ramp runs at the given rate, or None."""
    for year, rate in ramp.items():
        if rate >= monthly_rate:
            return year

    return None


def get_rate_sensitivity():
    return RATE_SENSITIVITY.copy()
