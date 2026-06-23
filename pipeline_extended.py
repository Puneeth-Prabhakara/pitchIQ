"""
IPL Analytics — Extended Pipeline (Phase Splits + Consistency)
Builds on top of the base pipeline. Produces:
  - batting_by_phase.csv       (player x season x phase -> SR, runs, balls)
  - bowling_by_phase.csv       (player x season x phase -> economy, runs, balls)
  - batting_innings.csv        (player x match -> runs in that innings) [for consistency]
  - bowling_innings.csv        (player x match -> economy in that innings) [for consistency]
"""

import pandas as pd
import numpy as np

DATA_DIR = "IPL-DATASET/csv"

# ── LOAD ─────────────────────────────────────────────────────────────────────
balls = pd.read_csv(f"{DATA_DIR}/Ball_By_Ball_Match_Data.csv")
matches = pd.read_csv(f"{DATA_DIR}/Match_Info.csv")

matches['match_date'] = pd.to_datetime(matches['match_date'], errors='coerce')
matches['season'] = matches['match_date'].apply(lambda d: d.year if pd.notna(d) else np.nan)

match_lookup = matches[['match_number', 'season', 'team1', 'team2']].rename(columns={'match_number': 'ID'})
balls = balls.merge(match_lookup, on='ID', how='left')

def tag_phase(over):
    if over < 6:
        return 'Powerplay'
    elif over < 16:
        return 'Middle'
    else:
        return 'Death'

balls['Phase'] = balls['Overs'].apply(tag_phase)
balls['IsLegalBall'] = ~balls['ExtraType'].isin(['wides', 'noballs'])
balls['BowlerConcededRuns'] = balls['BatsmanRun'] + np.where(
    balls['ExtraType'].isin(['wides', 'noballs']), balls['ExtrasRun'], 0
)

print("=" * 70)
print("EXTENDED PIPELINE — PHASE SPLITS + CONSISTENCY DATA")
print("=" * 70)

# ════════════════════════════════════════════════════════════════════════════
# BATTING BY PHASE (career + per-season) — now with boundary breakdown
# ════════════════════════════════════════════════════════════════════════════
bat_legal = balls[balls['IsLegalBall']]

batting_by_phase = bat_legal.groupby(['Batter', 'season', 'Phase']).agg(
    runs=('BatsmanRun', 'sum'),
    balls_faced=('BallNumber', 'count'),
    fours=('BatsmanRun', lambda x: (x == 4).sum()),
    sixes=('BatsmanRun', lambda x: (x == 6).sum()),
).reset_index()
batting_by_phase['strike_rate'] = (batting_by_phase['runs'] / batting_by_phase['balls_faced'] * 100).round(2)
batting_by_phase['boundary_pct'] = (
    (batting_by_phase['fours'] + batting_by_phase['sixes']) / batting_by_phase['balls_faced'] * 100
).round(2)

# Career-level (all seasons combined) phase split
batting_by_phase_career = bat_legal.groupby(['Batter', 'Phase']).agg(
    runs=('BatsmanRun', 'sum'),
    balls_faced=('BallNumber', 'count'),
    fours=('BatsmanRun', lambda x: (x == 4).sum()),
    sixes=('BatsmanRun', lambda x: (x == 6).sum()),
).reset_index()
batting_by_phase_career['strike_rate'] = (batting_by_phase_career['runs'] / batting_by_phase_career['balls_faced'] * 100).round(2)
batting_by_phase_career['boundary_pct'] = (
    (batting_by_phase_career['fours'] + batting_by_phase_career['sixes']) / batting_by_phase_career['balls_faced'] * 100
).round(2)
batting_by_phase_career['season'] = 'Career'

batting_phase_combined = pd.concat([batting_by_phase, batting_by_phase_career], ignore_index=True)

print("\nSample — V Kohli phase splits (career):")
print(batting_by_phase_career[batting_by_phase_career['Batter'] == 'V Kohli'].to_string(index=False))

print("\nSample — PD Salt phase splits (career):")
print(batting_by_phase_career[batting_by_phase_career['Batter'] == 'PD Salt'].to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# BOWLING BY PHASE (career + per-season)
# ════════════════════════════════════════════════════════════════════════════
bowl_legal = balls[balls['IsLegalBall']]

bowling_by_phase = bowl_legal.groupby(['Bowler', 'season', 'Phase']).agg(
    runs_conceded=('BowlerConcededRuns', 'sum'),
    balls_bowled=('BallNumber', 'count')
).reset_index()
bowling_by_phase['overs'] = (bowling_by_phase['balls_bowled'] // 6) + (bowling_by_phase['balls_bowled'] % 6) / 6
bowling_by_phase['economy'] = (bowling_by_phase['runs_conceded'] / bowling_by_phase['overs']).round(2)

bowling_by_phase_career = bowl_legal.groupby(['Bowler', 'Phase']).agg(
    runs_conceded=('BowlerConcededRuns', 'sum'),
    balls_bowled=('BallNumber', 'count')
).reset_index()
bowling_by_phase_career['overs'] = (bowling_by_phase_career['balls_bowled'] // 6) + (bowling_by_phase_career['balls_bowled'] % 6) / 6
bowling_by_phase_career['economy'] = (bowling_by_phase_career['runs_conceded'] / bowling_by_phase_career['overs']).round(2)
bowling_by_phase_career['season'] = 'Career'

bowling_phase_combined = pd.concat([bowling_by_phase, bowling_by_phase_career], ignore_index=True)

print("\nSample — JJ Bumrah phase splits (career):")
print(bowling_by_phase_career[bowling_by_phase_career['Bowler'] == 'JJ Bumrah'].to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# INNINGS-LEVEL DATA (for consistency / box plots)
# ════════════════════════════════════════════════════════════════════════════
# One row per player per match = one innings. This is the raw spread we need
# for box plots and std-dev consistency scores (season-level aggregates hide variance).

batting_innings = bat_legal.groupby(['Batter', 'ID', 'season']).agg(
    runs=('BatsmanRun', 'sum'),
    balls_faced=('BallNumber', 'count')
).reset_index()
batting_innings['strike_rate'] = np.where(
    batting_innings['balls_faced'] > 0,
    (batting_innings['runs'] / batting_innings['balls_faced'] * 100).round(2),
    0
)

bowling_innings = bowl_legal.groupby(['Bowler', 'ID', 'season']).agg(
    runs_conceded=('BowlerConcededRuns', 'sum'),
    balls_bowled=('BallNumber', 'count')
).reset_index()
bowling_innings['overs'] = (bowling_innings['balls_bowled'] // 6) + (bowling_innings['balls_bowled'] % 6) / 6
bowling_innings['economy'] = np.where(
    bowling_innings['overs'] > 0,
    (bowling_innings['runs_conceded'] / bowling_innings['overs']).round(2),
    np.nan
)
# Only count innings where bowler actually bowled at least 1 over (filters out token appearances)
bowling_innings = bowling_innings[bowling_innings['overs'] >= 1]
# Only count innings where batter faced at least 1 ball
batting_innings = batting_innings[batting_innings['balls_faced'] >= 1]

print("\n" + "-" * 70)
print("CONSISTENCY CHECK — V Kohli innings-level std dev")
print("-" * 70)
kohli_innings = batting_innings[batting_innings['Batter'] == 'V Kohli']
print(f"Innings count: {len(kohli_innings)}")
print(f"Mean runs: {kohli_innings['runs'].mean():.2f}")
print(f"Std dev runs: {kohli_innings['runs'].std():.2f}")
print(f"Mean SR: {kohli_innings['strike_rate'].mean():.2f}")
print(f"Std dev SR: {kohli_innings['strike_rate'].std():.2f}")

print("\n" + "-" * 70)
print("CONSISTENCY CHECK — JJ Bumrah innings-level std dev")
print("-" * 70)
bumrah_innings = bowling_innings[bowling_innings['Bowler'] == 'JJ Bumrah']
print(f"Innings count: {len(bumrah_innings)}")
print(f"Mean economy: {bumrah_innings['economy'].mean():.2f}")
print(f"Std dev economy: {bumrah_innings['economy'].std():.2f}")

# ── SAVE ──────────────────────────────────────────────────────────────────────
batting_phase_combined.to_csv("batting_by_phase.csv", index=False)
bowling_phase_combined.to_csv("bowling_by_phase.csv", index=False)
batting_innings.to_csv("batting_innings.csv", index=False)
bowling_innings.to_csv("bowling_innings.csv", index=False)

# ════════════════════════════════════════════════════════════════════════════
# WICKET TYPES PER BOWLER (excludes run outs — not bowler's wicket)
# ════════════════════════════════════════════════════════════════════════════
bowler_wickets = balls[
    (balls['IsWicketDelivery'] == 1) &
    (~balls['Kind'].isin(['run out', 'retired hurt', 'retired out', 'obstructing the field', 'NA']))
]
wicket_types = bowler_wickets.groupby(['Bowler', 'Kind']).size().reset_index(name='count')
wicket_types.to_csv("bowler_wicket_types.csv", index=False)

print("\nSample — JJ Bumrah wicket types:")
print(wicket_types[wicket_types['Bowler'] == 'JJ Bumrah'].to_string(index=False))

print("\n" + "=" * 70)
print("SAVED: batting_by_phase.csv, bowling_by_phase.csv,")
print("       batting_innings.csv, bowling_innings.csv, bowler_wicket_types.csv")
print("=" * 70)