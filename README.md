# SmartGrid Pulse

**Autonomous Energy Demand Prediction and Power Distribution Engine** is a Chennai-based academic demonstration built with Flask, HTML, CSS, JavaScript, scikit-learn and Plotly. It is an educational simulation—not a live electricity utility control system.

## Three project modules

1. **Intelligent Agent Architecture and Search Planning** — Chennai-region map, illustrative grid graph, A*, Greedy Best-First and Uniform Cost Search, edge-cost explanations, measured grid-size experiments and constraint-based power allocation.
2. **Knowledge Representation and Logical Reasoning** — propositional/FOL-style ground facts, unification, ten rules, forward chaining, backward chaining and ten inference scenarios.
3. **Machine Learning, Real-Time Integration and Scalability** — chronological train/validation/test Decision Tree/MLP evaluation, forecast, CSV validation and upload, safe priority-aware allocation, 1×/10×/100× workload tests and PDF report.

## Geographic and data accuracy

The map labels Basin Bridge Gas Turbine Power Station in Chennai and North Chennai TPS I/II in Athipattu, Thiruvallur district. Map points are approximate display coordinates. Representative substations, demand nodes, line links, capacities and feeder paths are explicitly illustrative/simulated; actual feeder topology is not asserted. Ennore Thermal Power Station is not presented as an active facility. The sample CSV is synthetic Chennai-style teaching data, not utility telemetry. No live TANGEDCO/TANTRANSCO integration or control is implemented.

Official reference pages supplied for the project:
- Basin Bridge GTPS: https://www.tnpgcl.org/en/generation/generation/gas-turbine-power-stations/bbgtps/
- North Chennai TPS I: https://www.tnpgcl.org/en/generation/generation/thermal-power-stations/nctps1/
- North Chennai TPS II: https://www.tnpgcl.org/en/generation/generation/thermal-power-stations/nctps2/
- TANTRANSCO network: https://www.tantransco.org/en/tantransco/infrastructure/nework/
- TANGEDCO GIS: https://tapps.tneb.in/gisapp/weblink.html

## Windows / VS Code setup

1. Install Python 3.10 or newer and VS Code.
2. Extract `SmartGrid_Pulse.zip` and open the `SmartGrid_Pulse` folder in VS Code.
3. Open Terminal → New Terminal (PowerShell), then run:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation for the current terminal, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again. Or use Command Prompt: `venv\Scripts\activate.bat`.

4. Open http://127.0.0.1:5000 in your browser. Stop the server with Ctrl+C.

## CSV upload

Use the CSV upload in Module 3. Required fields: `timestamp`, `demand_kw`, `generation_kw`. Accepted aliases include `date`/`datetime`, `demand`/`load_kw` and `generation`/`supply_kw`. Optional fields include `region`, `temperature`, `renewable_kw` and `priority`. The file needs at least 20 valid rows. Required values must be parseable and non-negative. Invalid uploads show a helpful message and do not replace the active dataset. Download the bundled sample from the page or `sample_data/chennai_energy_sample.csv`.

## PDF report

Run the desired experiments first, then select **Generate & download PDF report** in Module 3. The report uses the active dataset and results computed in the current server session. Sections without a run are clearly marked as not yet run.

## Tests

```powershell
pytest -q
```

## Faculty demonstration walkthrough

1. Open Module 1; identify the three facility markers and explain the simulated lines/nodes. Run a Basin Bridge → example hospital route comparison; expand the edge-cost table.
2. Run the four grid-size search experiments and explain that timings are machine-dependent.
3. Run CSP with a limited supply and show how critical services are prioritized while demand, supply and connection limits are respected.
4. Open Module 2; show the facts/rules, forward-chained facts, test cases, then prove `unsafe(line_1)` using backward chaining.
5. Open Module 3; train both models, compare held-out MAE/RMSE, generate the next-24-hour forecast, run the allocation and 1×/10×/100× benchmark.
6. Download the PDF report. Mention clearly that sample observations, feeder topology and distribution capacities are simulated.

## Technical notes

- Search edge cost = distance component + congestion penalty + safety-risk penalty. Values are normalized educational cost units, not currency or real grid tariffs.
- A* uses a conservative scaled straight-line heuristic for this toy graph. Greedy Best-First is not guaranteed to return the minimum-cost route. UCS orders by accumulated path cost.
- Runtime, memory, ML metrics and scalability measurements are computed on the running machine and can vary.
- The MLP may emit a convergence warning on some machines; metrics are still calculated from the fitted estimator.
- The interactive map requires an internet connection for OpenStreetMap tiles and the Leaflet CDN. Charts use Plotly CDN.
