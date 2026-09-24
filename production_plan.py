# Includes ramp schedule and sensitivity test range
# A320-family production ramp scenarios
# Values represent nominal aircraft produced per month


RAMPS = {
    "slow": {
        2026: 52,
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

    "base": {
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

    "fast": {
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
}


RATE_SENSITIVITY = list(range(55, 100))


def get_production_ramp(case="base"):
    if case not in RAMPS:
        raise ValueError(
            "Ramp case must be 'slow', 'base', or 'fast'"
        )

    return RAMPS[case].copy()


def get_rate_sensitivity():
    return RATE_SENSITIVITY.copy()
