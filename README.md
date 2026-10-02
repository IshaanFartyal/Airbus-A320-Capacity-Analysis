# Airbus A320 Capacity Expansion Strategy

A Python model that assesses the economic value of Airbus's A320 Family production ramp-up, combining capacity planning, scenario analysis, and NPV using public Airbus data and stated assumptions.

## Business Question

> How dependent is the value of Airbus's A320 Family ramp-up on its suppliers' ability to keep pace?

The main scenario follows Airbus's stated target of ramping production up to 70-75 aircraft per month by the end of 2027 and stabilizing at rate 75 thereafter. The model values that target, then tests how much of the value survives if suppliers are unable to fully support the planned ramp, or if the ramp is delayed. It also compares the target with deliberately slower ramps, and tests the result against delivery demand, margin, investment cost, and the discount rate.

Airbus does not disclose aircraft-level margins, ramp investment, or the capacity of its existing factories. Reported Airbus figures and model assumptions are therefore kept in separate files, and the results should be read as scenario analysis, not as a forecast of Airbus's actual economics.

## Project Structure

```text
airbus_capacity_analysis/
├── data/
│   ├── airbus_inputs.csv              reported and derived Airbus figures
│   ├── airbus_assumptions.csv         model assumptions (base, downside, upside)
│   ├── a320_deliveries_history.csv    annual deliveries, 1988-2025
│   └── a320_quarterly_deliveries.csv  quarterly deliveries, 2021-2025
├── outputs/                           generated figures
├── model.py
├── financial_analysis.py
├── production_plan.py
├── demand.py
├── scenarios.py
├── main.py
├── plots.py
├── fixed_plots.py
├── plot_style.py
├── requirements.txt
└── README.md
```

| File | Role |
|---|---|
| `model.py` | Core relationships: production, deliveries, backlog, baseline, investment |
| `financial_analysis.py` | NPV calculation |
| `production_plan.py` | Ramp schedules (Airbus target and three deliberately slower ramps), delays of the target, and rates used for the rate sensitivity |
| `demand.py` | Yearly delivery demand and new orders; downside, base, and upside demand levels |
| `scenarios.py` | Combines the above to evaluate ramps, delays, constant rates, and assumption cases |
| `main.py` | Prints the headline Airbus target case and the ramp comparison |
| `plots.py` | Generates the model-based figures |
| `fixed_plots.py` | Generates the historical delivery figures |
| `plot_style.py` | Shared figure style |

## Setup

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Analysis

```powershell
python main.py          # headline Airbus target case and ramp comparison
python scenarios.py     # full scenario tables
python plots.py         # model-based figures, saved in outputs/
python fixed_plots.py   # historical delivery figures, saved in outputs/
```

## How the Model Works

Each year, deliveries are the smallest of three limits:

- **Capacity:** the planned monthly rate × 12.
- **Supply:** the share of the planned rate that key suppliers can support (supply-chain availability).
- **Demand:** the aircraft customers are ready to take, limited by the order backlog.

The value of the investment is measured against a **no-investment baseline**: what the existing factories would deliver anyway, under the same supply and demand limits. If suppliers cannot support more than the existing factories already build, the investment adds nothing.

```text
incremental deliveries = deliveries with the ramp - baseline deliveries
annual cash flow       = incremental deliveries × margin per aircraft
                         - capacity investment - expedite cost
NPV                    = discounted annual cash flows, 2026-2035
```

The NPV is also reported with an extended life: the final year's cash flow is assumed to continue for ten further years. This is shown separately because it is an extrapolation. It is more conservative than the terminal value with perpetual growth that Airbus uses for its commercial aircraft business.

Capacity investment is phased over the ramp and paid the year before the capacity comes online. Capacity added faster than a comfortable annual step costs a premium on top of the normal investment cost, so a faster ramp is not free.

## Key Assumptions

| Assumption | Base value | Basis |
|---|---|---|
| No-investment baseline | 55 aircraft/month | 2019 delivery record (53.5/month) plus about 3% for capacity added since |
| Supply-chain availability | 95% | Assumption; Airbus has delivered roughly 92–102% of its annual targets in 2022–2025 |
| Delivery demand | 900 aircraft/year | Airbus's stated stabilzation rate; about 53% of its forecast single-aisle market |
| Margin per additional aircraft | €8m | Assumption |
| Ramp investment to rate 75 | €2.5bn | Assumption |
| Comfortable ramp pace | 5/month per year | Largest annual rise in A320 deliveries since 2000 was 5.7/month |
| Expedite premium | 50% on capacity added faster than that | Assumption, anchored on overtime pay premiums of 25% to 50% |
| Extended life | 10 years after 2035 | Assumption; more conservative than Airbus's perpetual-growth terminal value |
| Discount rate | 12% | Rounded from Airbus's pre-tax WACC of 11.9% for its commercial aircraft business |

All values are in `data/airbus_assumptions.csv` and `demand.py`, each with a downside and an upside value used for the sensitivity analysis.

## Data Sources

- [Airbus: 793 commercial aircraft deliveries in 2025](https://www.airbus.com/en/newsroom/press-releases/2026-01-airbus-reports-793-commercial-aircraft-deliveries-in-2025)
- [Airbus: Full-Year 2025 results](https://www.airbus.com/en/newsroom/press-releases/2026-02-airbus-reports-full-year-fy-2025-results)
- [Airbus: FY2025 financial statements](https://www.airbus.com/sites/g/files/jlcbta136/files/2026-02/airbus_fy_2025_financial_statements_1.pdf)
- [Airbus: A320 Family industrial ramp-up](https://www.airbus.com/en/newsroom/stories/2025-10-ramping-up-a320-family-production)
- [Airbus: Global Market Forecast](https://www.airbus.com/en/products-services/commercial-aircraft/global-market-forecast)

## Limitations

- Margins, ramp investment, expedite costs, and the baseline are assumptions, not Airbus data.
- The ramp is fixed in advance; Airbus cannot slow or stop investment in response to demand.
- Value after 2035 is a simple extension of the final year's cash flow, not a detailed projection.
- No tax, financing, working capital, aircraft mix, or customer-specific pricing.
- Demand and supplier performance are deterministic inputs, not simulated.
