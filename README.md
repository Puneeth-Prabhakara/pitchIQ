# 🔎 ScoutLens — IPL Player Auction Analytics

> Note: this project is branded **ScoutLens** in the app itself, but the GitHub repository is still named `pitchIQ` (kept as-is to avoid breaking existing clone links for the team).

An interactive dashboard for scouting IPL players ahead of auction day. Built on 17+ seasons of ball-by-ball data, ScoutLens turns raw deliveries into auction-ready insight — phase-wise performance, consistency scoring, head-to-head matchups, durability signals, and side-by-side player comparison.

Built for **Sports & Performance Analytics** — group analytics tool assessment.

---

## Features

- **Player Card** — full batting/bowling profile for any player: career stats, phase splits (Powerplay/Middle/Death), consistency (box plots + plain-English verdicts), dismissal breakdown, dot-ball %, finishing rate, durability (age + missed seasons), and head-to-head vs every opponent faced.
- **Compare Players** — put 2–4 players side by side, with recent-form-window adjustable metrics, phase-wise output comparison, and a head-to-head-vs-a-specific-team selector.
- **Shortlist** — flag auction targets from anywhere in the app, see them all in one table with a normalized radar comparison.
- **Auto-generated scouting summaries** — a one-line, coach-readable verdict per player (e.g. *"Death-Overs Finisher, trending up in recent seasons"*), built from the same underlying stats shown on the page.
- **Sample-size warnings** — small-sample stats are flagged with a badge and a plain-language caveat, so a 5-innings sample is never confused with a settled judgment.

## Tech Stack

Python · Streamlit · Pandas · Plotly · NumPy

## Data Source

Ball-by-ball IPL data (2008–2026) via [ritesh-ojha/IPL-DATASET](https://github.com/ritesh-ojha/IPL-DATASET), a GitHub mirror of Cricsheet/official IPL records. Player age data from the same source's 2024 squad-details file (covers ~261 players; shown as unavailable for the rest rather than guessed).

## Setup

```bash
git clone https://github.com/Puneeth-Prabhakara/pitchIQ.git
cd pitchIQ
pip install streamlit pandas plotly numpy
streamlit run app.py
```

All processed CSVs are already included in this repo, so the app runs immediately after install — no pipeline scripts required.

### Regenerating the data (only needed if you change the pipeline logic)

```bash
python3 pipeline.py
python3 pipeline_extended.py
```

Both scripts read from `IPL-DATASET/csv/` (included in this repo) and write their output CSVs to the project root.

## Project Structure

```
pitchIQ/
├── app.py                      # Streamlit dashboard
├── pipeline.py                 # Base stats: season-level batting/bowling, role inference
├── pipeline_extended.py        # Phase splits, consistency, dot-ball%, H2H, durability, keeper stats
├── .streamlit/config.toml      # Light theme configuration
├── IPL-DATASET/                # Raw ball-by-ball data (cloned dataset)
└── *.csv                       # Processed outputs consumed by app.py
```

## Known Data Limitations

Documented deliberately rather than worked around:

- **No pitch-length data** (yorker/good-length/short) — not available in any public IPL dataset; requires proprietary ball-tracking.
- **No nationality/overseas-player field** — skipped rather than guessed from names.
- **Wicket-keeper catches and byes** can't be reliably attributed to "the keeper" specifically vs. any other fielder — only stumpings are included, since those are unambiguous by the rules of cricket.
- **Player age** only covers ~261 players (2024 squad lists); shown as unavailable for everyone else rather than estimated.

## Contributors

Group project — Sports & Performance Analytics module.