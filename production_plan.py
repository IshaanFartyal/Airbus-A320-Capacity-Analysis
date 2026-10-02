# A320-family production ramp scenarios and the rates used for the
# rate sensitivity.
#
# Values are nominal aircraft produced per month, averaged over the
# year. A scenario that shows 75 in 2028 therefore has 2028 as its
# first full year at rate 75.
#
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

    # Rate 75 is reached one year later than the Airbus target
    "delay": {
        2026: 55,
        2027: 62,
        2028: 70,
        2029: 75,
        2030: 75,
        2031: 75,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },

    # A deliberately gentle ramp with no rate increase above the
    # comfortable annual step, reaching rate 75 in 2032
    "gradual": {
        2026: 55,
        2027: 57,
        2028: 62,
        2029: 67,
        2030: 70,
        2031: 72,
        2032: 75,
        2033: 75,
        2034: 75,
        2035: 75,
    },
}

# Display names, in the order the scenarios are reported
RAMP_LABELS = {
    "target": "Airbus target",
    "delay": "One-year delay",
    "gradual": "Gradual ramp",
}


RATE_SENSITIVITY = list(range(55, 100))


def get_production_ramp(case=TARGET_CASE):
    if case not in RAMPS:
        raise ValueError(
            "Ramp case must be 'target', 'delay', or 'gradual'"
        )

    return RAMPS[case].copy()


def get_rate_sensitivity():
    return RATE_SENSITIVITY.copy()
