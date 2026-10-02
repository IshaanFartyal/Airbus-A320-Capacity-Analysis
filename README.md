# Airbus A320 Capacity Expansion Strategy

A portfolio project combining industrial strategy, finance, capacity planning, scenario analysis, and Python using public Airbus operating and financial disclosures.

## Business Question

> Is an A320 Family production ramp toward 70–75 aircraft per month economically attractive, and how sensitive is that value to production rate, ramp timing, incremental margin, investment cost, supply-chain performance, customer delivery demand, backlog, and inventory accumulation?

## Important Methodology Note

This project deliberately separates three types of inputs:

- **Reported data**: values publicly disclosed by Airbus.
- **Derived data**: calculations made directly from reported Airbus figures.
- **Assumptions**: illustrative modeling inputs that are not claimed to represent Airbus internal data.

This distinction is essential because Airbus does not publicly disclose the detailed aircraft-level cost, margin, investment, demand, and cash-flow information required to calculate the true NPV of the A320 Family production ramp.

The project should therefore be interpreted as a **scenario-based strategic investment model**, not as a forecast of Airbus internal financial performance.

---

## Project Structure

```text
airbus_capacity_analysis/

├── data/
│   ├── airbus_inputs.csv
│   ├── airbus_assumptions.csv
│   ├── a320_deliveries_history.csv
│   └── a320_quarterly_deliveries_history.csv
│
├── outputs/
│   └── generated plots
│
├── model.py
├── financial_analysis.py
├── production_plan.py
├── demand.py
├── scenarios.py
├── plots.py
├── fixed_plots.py
├── plot_style.py
├── main.py
├── requirements.txt
└── README.md
```

### File Roles

**`model.py`**

Contains the core physical and economic relationships used by the analysis, including:

- annual production
- delivery and inventory flows
- backlog evolution
- incremental profit
- inventory holding costs
- capacity-dependent investment

**`financial_analysis.py`**

Contains financial calculations including:

- net present value (NPV)
- simple payback period

**`production_plan.py`**

Contains editable production assumptions including:

- slow, base, and fast production ramps
- production-rate values used for sensitivity analysis

**`demand.py`**

Contains the assumed yearly A320 Family:

- customer delivery demand
- new orders

These values are model assumptions and are kept separate from reported Airbus data.

**`scenarios.py`**

Combines the operating model, financial model, production plans, and demand assumptions to evaluate:

- constant production-rate cases
- rate sensitivity
- alternative production ramps
- NPV
- inventory
- backlog
- investment requirements

**`main.py`**

Prints the headline base case. The headline is the base production ramp, with a comparison of the slow, base, and fast ramps and a constant-rate-75 reference case.

**`plots.py`**

Generates model-dependent plots that may change when assumptions or scenarios are changed.

**`fixed_plots.py`**

Generates plots based only on historical reported or derived Airbus data.

**`plot_style.py`**

Contains the shared figure style, colors, and helper functions used by both plotting scripts, so that all report figures look consistent.

---

## Setup

Create and activate a virtual environment:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

## Run the Analysis

Print the headline base case:

```powershell
python main.py
```

Run scenario analysis:

```powershell
python scenarios.py
```

Generate model-dependent plots:

```powershell
python plots.py
```

Generate historical fixed-data plots:

```powershell
python fixed_plots.py
```

The analysis and model-based plots can also be run sequentially in PowerShell:

```powershell
python scenarios.py && python plots.py
```

---

# Model Logic

## 1. Production Capacity

Annual production capacity is calculated from the planned monthly production rate:

```text
monthly production rate
× 12
× supply-chain availability
=
annual production capacity
```

Actual production is capped at what can be delivered in that year:

```text
annual production
=
minimum of:

annual production capacity
deliverable orders - beginning inventory
```

where deliverable orders are the smaller of customer delivery demand and outstanding orders.

Capacity above deliverable demand therefore stays idle rather than building aircraft that customers cannot take. Idle capacity still costs its capacity investment.

Supply-chain availability is interpreted as the **share of the planned production ramp that key suppliers can support**.

For example:

```text
75 aircraft/month
× 12
× 95% supply-chain availability
=
855 aircraft/year
```

It does not mean that 95% of suppliers are available. It represents how well key suppliers, such as engine manufacturers, scale their output with Airbus's expansion plans.

It acts as a ceiling on deliveries both with and without the investment. If suppliers cannot support more aircraft than the existing factories can already build, the investment adds no deliveries while its cost is still paid. The value of the capacity investment therefore depends on suppliers' ability to scale.

This is a simplification: the supply ceiling is tied to the planned rate, which assumes suppliers deliver a fixed share of whatever Airbus plans.

---

## 2. Backlog

Backlog represents aircraft already ordered by customers but not yet delivered.

Backlog is not physical inventory.

The model evolves backlog as:

```text
beginning backlog
+ new orders
- deliveries
=
ending backlog
```

The A320 Family backlog is modeled separately from Airbus's total Commercial Aircraft backlog because this project focuses specifically on the A320 Family.

---

## 3. Customer Delivery Demand

The model uses a yearly demand plan rather than assuming that every aircraft produced can automatically be delivered.

The demand plan represents the number of aircraft customers are assumed to be ready to accept during each year.

This is separate from backlog:

```text
backlog
=
total outstanding contracted orders

delivery demand
=
aircraft customers are assumed ready to receive during a specific year
```

The yearly demand and new-order values in `demand.py` are illustrative assumptions.

The base demand plan rises to 900 aircraft per year. This level is supported by three reference points:

- it is Airbus's own stated stabilisation rate of 75 aircraft per month;
- it corresponds to about 53% of Airbus's Global Market Forecast for single-aisle aircraft, in line with the A320 Family's historical share of deliveries and orders;
- it sits somewhat above the historical A320neo-family net order rate, with the difference covered by the order backlog.

`demand.py` also defines a low demand level of 760 aircraft per year (roughly the long-run net order rate) and a high level of 1,000 aircraft per year. These are used only for the demand sensitivity figure. All other results use the base demand plan.

---

## 4. Deliveries

The number of aircraft delivered in each year is constrained by:

```text
aircraft physically available
customer delivery demand
outstanding orders
```

Conceptually:

```text
deliveries
=
minimum of:

beginning inventory + production
delivery demand
beginning backlog + new orders
```

This prevents the model from assuming Airbus can deliver more aircraft than:

- it can physically produce,
- customers are ready to accept,
- or have actually been ordered.

---

## 5. Inventory

Physical inventory is modeled separately from backlog.

Inventory evolves as:

```text
beginning inventory
+ production
- deliveries
=
ending inventory
```

Because production is capped at deliverable demand, inventory normally stays at zero. The inventory logic is kept so that the model remains correct if a different production policy is introduced.

The model assigns a holding cost to this inventory to approximate costs associated with:

- storage
- maintenance and preservation
- handling
- insurance
- working capital
- other costs associated with undelivered aircraft

Inventory-cost assumptions are illustrative and are not reported Airbus aircraft-level costs.

---

## 6. Incremental Deliveries

Incremental deliveries are measured relative to a no-investment baseline:

```text
annual deliveries
- baseline deliveries
=
incremental deliveries
```

The baseline is what the existing industrial system delivers with no further investment. It faces the same supply ceiling and delivery demand as the ramp:

```text
baseline deliveries
=
minimum of:

baseline monthly rate × 12
supply ceiling
delivery demand
```

The base assumption is 55 aircraft per month, or 660 deliveries per year when suppliers are not the limit.

This is anchored on Airbus's highest annual A320 Family deliveries: 642 aircraft in 2019, or 53.5 per month, the last year before the pandemic and the engine shortage. Airbus has expanded its production capability since then, so the base assumption is set about 3% above that level.

Airbus does not publish the capacity of its existing A320 Family production system. The baseline is therefore a model assumption, not reported Airbus data, and it is tested in the sensitivity analysis between 53.5 per month (the 2019 record) and 60 per month (the rate Airbus announced for 2019).

No production ramp runs below the base baseline rate.

---

## 7. Incremental Profit

Annual incremental operating benefit is modeled as:

```text
incremental deliveries
× assumed incremental margin per aircraft
=
incremental profit
```

The incremental margin is a model assumption.

The current model assumes a constant contribution margin unless additional production-cost effects are explicitly introduced.

---

## 8. Inventory-Adjusted Cash Flow

Annual operating cash flow is calculated as:

```text
incremental profit
- inventory holding cost
- production cost of aircraft added to inventory
=
annual operating cash flow
```

The incremental margin is only earned when an aircraft is delivered. An aircraft that is built but not delivered therefore costs its full assumed production cost in the year it is built, and that cash is released again if the aircraft is delivered from inventory in a later year.

With production capped at deliverable demand, this term is normally zero. It ensures that any production policy that builds ahead of demand is charged for it.

---

## 9. Capacity-Dependent Investment

The model does not assume that expanding to every production rate costs the same amount.

Instead, required capacity investment scales with the size of the production expansion.

The investment model uses:

- no-investment baseline rate
- target production rate
- a reference investment assumption
- a capacity-scaling exponent

Investment is measured from the no-investment baseline, so the reference investment covers the step from the baseline rate to the 75-aircraft-per-month reference target.

This means that a hypothetical expansion to 90 or 100 aircraft per month requires more investment than an expansion toward Airbus's stated 70–75 aircraft-per-month production objective.

The exact investment relationship remains an illustrative modeling assumption.

### Investment timing in the ramp scenarios

In the constant-rate sensitivity, the full investment is paid at time zero.

In the ramp scenarios, investment is phased over the ramp:

```text
investment for capacity coming online in a year
=
total investment
× capacity added that year / total capacity added
```

Capacity that comes online in a given year is paid for at the end of the previous year. The first year's capacity is paid at time zero.

### Expedite cost

A faster ramp is not free. Year-on-year increases in the monthly rate above an assumed comfortable step incur an expedite cost:

```text
expedite cost
=
(annual rate increase - comfortable annual rate step)
× expedite cost per rate point
```

This represents overtime, supplier premiums, and other costs of ramping quickly. Both parameters are illustrative assumptions.

---

## 10. Net Present Value

NPV is calculated as:

```text
NPV
=
-initial capacity investment
+ discounted future annual cash flows
```

In the ramp scenarios, the phased investment and expedite costs of later years are deducted from the annual cash flows before discounting.

Future cash flows are discounted using the assumed project discount rate.

A positive NPV indicates that the modeled discounted operating benefits exceed the assumed investment cost.

---

# Production Ramp Scenarios

The project evaluates multiple yearly production paths.

For example:

```text
Slow ramp
2026 → lower rate
2027 → gradual increase
...
→ eventually reaches target production

Base ramp
→ reaches target more quickly

Fast ramp
→ reaches target earlier
```

The exact schedules are stored in:

```text
production_plan.py
```

This allows production assumptions to be changed without modifying the scenario-analysis logic.

Each ramp generates a different sequence of:

- annual production
- deliveries
- inventory
- backlog
- incremental profit
- cash flow
- NPV

---

# Production-Rate Sensitivity

The model also evaluates hypothetical constant monthly production rates.

This analysis asks:

> What happens to project value if the production rate changes while the other base-case assumptions remain fixed?

For every tested production rate, the model recalculates:

- production
- deliveries
- inventory
- inventory cost
- production cost tied up in undelivered aircraft
- required capacity investment
- backlog
- NPV

This allows the model to identify where additional production capacity may stop creating economic value because the extra capacity can no longer be delivered against demand while its investment cost continues to rise.

Any production rate identified as value-maximizing is a **model result under the selected assumptions**, not a claim about Airbus's actual optimal production rate.

---

# Current Reported Inputs

The dataset includes reported or directly derived values for:

- A320 Family annual deliveries
- A320 Family quarterly delivery history
- 2025 A320 Family deliveries
- 2025 average monthly A320 Family deliveries
- Airbus A320 Family production-rate guidance
- A320 Family backlog
- total Commercial Aircraft backlog
- Commercial Aircraft revenue
- Commercial Aircraft adjusted EBIT
- Commercial Aircraft capital expenditure

Reported values and guidance may change over time and should be re-checked against Airbus disclosures when the analysis is updated.

---

# Historical Delivery Data

The project contains two historical datasets.

### Annual A320 Family Deliveries

```text
data/a320_deliveries_history.csv
```

This dataset is used to show the long-term development of A320 Family deliveries.

### Quarterly A320 Family Deliveries

```text
data/a320_quarterly_deliveries_history.csv
```

Quarterly data provide more detail on short-term delivery patterns.

Some quarterly values are directly reported by Airbus while others are derived from cumulative Airbus disclosures.

For example:

```text
Q2 deliveries
=
H1 cumulative deliveries
- Q1 deliveries
```

and:

```text
Q4 deliveries
=
full-year deliveries
- 9M cumulative deliveries
```

The CSV contains a `source_type` and `source_or_derivation` field to make this distinction explicit.

---

# Data Sources

The Airbus data used in this project comes from public company disclosures and investor-relations materials.

### Aircraft Deliveries and Backlog

Airbus reported 793 total commercial aircraft deliveries in 2025, including 607 A320 Family aircraft.

Airbus also reported a year-end Commercial Aircraft backlog of 8,754 aircraft.

Source:

[Airbus — 793 commercial aircraft deliveries in 2025](https://www.airbus.com/en/newsroom/press-releases/2026-01-airbus-reports-793-commercial-aircraft-deliveries-in-2025)

---

### A320 Family Backlog

The model uses the A320 Family backlog rather than total Commercial Aircraft backlog when modeling A320-specific order flows.

The year-end 2025 A320 Family backlog was approximately 7,163 aircraft.

The total Commercial Aircraft backlog is retained as contextual Airbus-wide information.

---

### Commercial Aircraft Revenue and EBIT

Airbus reported approximately:

```text
Commercial Aircraft revenue: €52.6 billion
Commercial Aircraft EBIT Adjusted: €5.470 billion
```

for 2025.

Source:

[Airbus — Full-Year 2025 Results](https://www.airbus.com/en/newsroom/press-releases/2026-02-airbus-reports-full-year-fy-2025-results)

---

### Capital Expenditure

Airbus FY2025 financial statements report approximately €3.037 billion of capital expenditure for the Airbus Commercial Aircraft segment.

Total Airbus Group capital expenditure was approximately €3.964 billion.

The model does **not** assume that all Commercial Aircraft capex relates to the A320 production ramp.

Instead, A320 ramp investment is treated as a separate modeling assumption.

Source:

[Airbus FY2025 Financial Statements](https://www.airbus.com/sites/g/files/jlcbta136/files/2026-02/airbus_fy_2025_financial_statements_1.pdf)

---

### A320 Family Production Rate

Airbus has stated that it expects A320 Family production to reach approximately:

```text
70–75 aircraft per month by the end of 2027
```

and to stabilise around:

```text
75 aircraft per month thereafter
```

This guidance is used as an important industrial reference point in the model.

It is **not assumed to represent Airbus's mathematically optimal or profit-maximizing production rate**.

Source:

[Airbus — Full-Year 2025 Results](https://www.airbus.com/en/newsroom/press-releases/2026-02-airbus-reports-full-year-fy-2025-results)

---

### Supply-Chain Constraints

Airbus has identified engine availability and other supplier constraints as important factors affecting the A320 Family production ramp.

This provides the basis for including a supply-chain production-realization factor in the model.

Source:

[Airbus — Full-Year 2025 Results](https://www.airbus.com/en/newsroom/press-releases/2026-02-airbus-reports-full-year-fy-2025-results)

---

### Industrial Capacity Expansion

Airbus has expanded A320 Family industrial capacity across multiple production locations, including Toulouse, Mobile, and Tianjin.

These investments support Airbus's planned A320 Family production ramp.

Source:

[Airbus — A320 Family industrial ramp-up](https://www.airbus.com/en/newsroom/stories/2025-10-ramping-up-a320-family-production)

---

# Model Assumptions

The following inputs are illustrative assumptions and are **not reported Airbus internal values**:

- no-investment baseline production rate
- incremental contribution margin per additional aircraft
- A320-specific ramp investment
- discount rate
- project life
- supply-chain realization rate
- yearly customer delivery demand
- yearly new orders
- inventory holding cost per aircraft
- production cost per aircraft
- capacity-investment scaling exponent
- comfortable annual rate step
- expedite cost per rate point

These assumptions are deliberately stored separately from reported data.

---

# Interpretation of Results

The purpose of the model is not to determine Airbus's true internal optimal production rate.

Instead, it demonstrates how the economic value of a capacity expansion changes when considering:

```text
production capacity
+
supply-chain constraints
+
customer demand
+
backlog
+
inventory accumulation
+
inventory holding costs
+
capacity investment
+
aircraft contribution margin
+
discounted cash flows
```

For example, very high production rates may initially increase deliveries but can eventually create:

- idle excess capacity
- higher capacity investment
- lower project NPV

The point at which this occurs depends on the model assumptions.

---

# Current Outputs

The project generates the following model-based plots:

- production rate over time for the slow, base, and fast ramps
- base-ramp cumulative cash flow, with the low point and payback year marked
- NPV vs monthly production rate, with the Airbus target rate and the value-maximizing rate marked
- NPV vs monthly production rate for low, base, and high delivery demand
- tornado chart of NPV sensitivity to the main assumptions
- NPV by ramp scenario and supply-chain availability, with the base case and the break-even availability marked
- NPV comparison across ramp scenarios
- base-ramp delivery demand, production capacity, and deliveries

Each figure has a headline stating its conclusion, which is generated from the model results, and a source note. Values are shown in € billion.

Historical fixed-data plots include:

- long-term A320 Family annual deliveries
- quarterly A320 Family deliveries

---

# Limitations

This model intentionally simplifies Airbus's real industrial and financial system.

- assumed aircraft-level incremental margins
- assumed A320-specific capacity investment
- assumed customer delivery-demand schedule
- assumed future order intake
- simplified supply-chain representation
- simplified inventory costs
- no aircraft-model mix within the A320 Family
- no customer-specific pricing
- no financing or pre-delivery payment modeling
- no tax effects
- no working-capital model beyond inventory holding costs
- no detailed factory or supplier network optimization
- no stochastic simulation of demand or supplier disruptions

Results should therefore be interpreted as **scenario-analysis outputs**, not forecasts of Airbus's actual economics.

---

# Future Improvements

- [ ] Introduce downside, base, and upside demand scenarios.
- [ ] Add separate engine and major-supplier capacity constraints.
- [ ] Add uncertainty to future order intake.
- [x] Model production-ramp investment over multiple years rather than entirely at time zero.
- [ ] Add Monte Carlo simulation.
- [ ] Add a more detailed working-capital model.
- [ ] Introduce production-rate-dependent variable costs.
- [x] Compare alternative ramp strategies under identical demand assumptions.
- [ ] Add sensitivity to inventory holding cost and investment scaling.

---
