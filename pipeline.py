"""
IPL Player Auction Analytics — Data Pipeline (Validation Script)
Loads ball-by-ball data, derives season, builds player-level aggregates,
and prints sanity-check outputs before this logic goes into the Streamlit app.
"""

import pandas as pd
import numpy as np

DATA_DIR = "IPL-DATASET/csv"

# ── LOAD ─────────────────────────────────────────────────────────────────────
balls = pd.read_csv(f"{DATA_DIR}/Ball_By_Ball_Match_Data.csv")
matches = pd.read_csv(f"{DATA_DIR}/Match_Info.csv")

print("=" * 70)
print("RAW SHAPES")
print("=" * 70)
print(f"Ball-by-ball: {balls.shape}")
print(f"Match info:   {matches.shape}")

# ── DERIVE SEASON FROM MATCH DATE ────────────────────────────────────────────
matches['match_date'] = pd.to_datetime(matches['match_date'], errors='coerce')

def derive_season(date):
    if pd.isna(date):
        return np.nan
    # IPL season = year of the match, except matches that start in
    # Dec/Jan that belong to following year's season (rare, but be safe)
    return date.year

matches['season'] = matches['match_date'].apply(derive_season)

print("\n" + "=" * 70)
print("SEASONS DETECTED")
print("=" * 70)
print(sorted(matches['season'].dropna().unique().astype(int)))

# ── MERGE SEASON + VENUE INTO BALL DATA ──────────────────────────────────────
match_lookup = matches[['match_number', 'season', 'venue', 'city', 'team1', 'team2']].rename(
    columns={'match_number': 'ID'}
)
balls = balls.merge(match_lookup, on='ID', how='left')

print(f"\nBalls after merge: {balls.shape}")
print(f"Unmatched (no season): {balls['season'].isna().sum()}")

# ── DERIVE BOWLING TEAM (it's missing — only BattingTeam exists) ────────────
# bowling team = whichever of team1/team2 is NOT the batting team
def get_bowling_team(row):
    if row['BattingTeam'] == row['team1']:
        return row['team2']
    elif row['BattingTeam'] == row['team2']:
        return row['team1']
    return np.nan

balls['BowlingTeam'] = balls.apply(get_bowling_team, axis=1)

# ── PHASE TAGGING (powerplay / middle / death) ───────────────────────────────
def tag_phase(over):
    if over < 6:
        return 'Powerplay'
    elif over < 16:
        return 'Middle'
    else:
        return 'Death'

balls['Phase'] = balls['Overs'].apply(tag_phase)

print("\n" + "=" * 70)
print("PHASE DISTRIBUTION (sanity check)")
print("=" * 70)
print(balls['Phase'].value_counts())

# ── LEGAL DELIVERY FLAG (exclude wides/no-balls for balls-faced calcs) ──────
balls['IsLegalBall'] = ~balls['ExtraType'].isin(['wides', 'noballs'])

# ════════════════════════════════════════════════════════════════════════════
# BATTING AGGREGATES
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BATTING KPI PIPELINE — SAMPLE: V Kohli")
print("=" * 70)

bat = balls.copy()
bat_legal = bat[bat['IsLegalBall']]

batting_by_season = bat_legal.groupby(['Batter', 'season']).agg(
    runs=('BatsmanRun', 'sum'),
    balls_faced=('BallNumber', 'count'),
    innings=('ID', 'nunique'),
    fours=('BatsmanRun', lambda x: (x == 4).sum()),
    sixes=('BatsmanRun', lambda x: (x == 6).sum()),
).reset_index()

batting_by_season['strike_rate'] = (batting_by_season['runs'] / batting_by_season['balls_faced'] * 100).round(2)

# dismissals per player per season
dismissals = balls[balls['IsWicketDelivery'] == 1].groupby(['PlayerOut', 'season']).size().reset_index(name='dismissals')
dismissals = dismissals.rename(columns={'PlayerOut': 'Batter'})

batting_by_season = batting_by_season.merge(dismissals, on=['Batter', 'season'], how='left')
batting_by_season['dismissals'] = batting_by_season['dismissals'].fillna(0)
batting_by_season['average'] = np.where(
    batting_by_season['dismissals'] > 0,
    (batting_by_season['runs'] / batting_by_season['dismissals']).round(2),
    np.nan  # not dismissed all season — average undefined, not "= runs"
)

kohli = batting_by_season[batting_by_season['Batter'] == 'V Kohli'].sort_values('season')
print(kohli.to_string(index=False))

# ── STRIKE RATE BY PHASE ──────────────────────────────────────────────────────
print("\n" + "-" * 70)
print("STRIKE RATE BY PHASE — V Kohli (career)")
print("-" * 70)

phase_bat = bat_legal[bat_legal['Batter'] == 'V Kohli'].groupby('Phase').agg(
    runs=('BatsmanRun', 'sum'),
    balls=('BallNumber', 'count')
)
phase_bat['strike_rate'] = (phase_bat['runs'] / phase_bat['balls'] * 100).round(2)
print(phase_bat)

# ════════════════════════════════════════════════════════════════════════════
# BOWLING AGGREGATES
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BOWLING KPI PIPELINE — SAMPLE: JJ Bumrah")
print("=" * 70)

# runs conceded = batsman runs + extras EXCEPT byes/legbyes (those aren't bowler's fault)
balls['BowlerConcededRuns'] = balls['BatsmanRun'] + np.where(
    balls['ExtraType'].isin(['wides', 'noballs']), balls['ExtrasRun'], 0
)

bowl_legal = balls[balls['IsLegalBall']]

bowling_by_season = bowl_legal.groupby(['Bowler', 'season']).agg(
    balls_bowled=('BallNumber', 'count'),
    runs_conceded=('BowlerConcededRuns', 'sum'),
).reset_index()

bowling_by_season['overs'] = (bowling_by_season['balls_bowled'] // 6) + (bowling_by_season['balls_bowled'] % 6) / 6
bowling_by_season['economy'] = (bowling_by_season['runs_conceded'] / bowling_by_season['overs']).round(2)

wickets = balls[(balls['IsWicketDelivery'] == 1) & (~balls['Kind'].isin(['run out', 'retired hurt', 'NA']))]
wickets_by_season = wickets.groupby(['Bowler', 'season']).size().reset_index(name='wickets')

bowling_by_season = bowling_by_season.merge(wickets_by_season, on=['Bowler', 'season'], how='left')
bowling_by_season['wickets'] = bowling_by_season['wickets'].fillna(0).astype(int)
bowling_by_season['bowling_avg'] = np.where(
    bowling_by_season['wickets'] > 0,
    (bowling_by_season['runs_conceded'] / bowling_by_season['wickets']).round(2),
    np.nan
)

bumrah = bowling_by_season[bowling_by_season['Bowler'] == 'JJ Bumrah'].sort_values('season')
print(bumrah.to_string(index=False))

# ── ROLE INFERENCE ────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("ROLE INFERENCE LOGIC CHECK")
print("=" * 70)

total_balls_faced = bat_legal.groupby('Batter')['BallNumber'].count().rename('balls_faced')
total_balls_bowled = bowl_legal.groupby('Bowler')['BallNumber'].count().rename('balls_bowled')

role_df = pd.concat([total_balls_faced, total_balls_bowled], axis=1).fillna(0)

def infer_role(row, min_involvement=150):
    bat = row['balls_faced']
    bowl = row['balls_bowled']
    total = bat + bowl

    if total < min_involvement:
        return 'Insufficient data'

    bat_share = bat / total
    bowl_share = bowl / total

    # Genuine all-rounder: meaningful contribution on both sides (>30% each)
    if bat_share >= 0.30 and bowl_share >= 0.30:
        return 'All-rounder'
    elif bat_share > bowl_share:
        return 'Batter'
    else:
        return 'Bowler'

role_df['role'] = role_df.apply(infer_role, axis=1)

print(role_df.loc[['V Kohli', 'JJ Bumrah', 'HH Pandya', 'R Ashwin', 'MS Dhoni']].to_string()
      if all(p in role_df.index for p in ['V Kohli', 'JJ Bumrah', 'HH Pandya', 'R Ashwin', 'MS Dhoni'])
      else role_df.head(10).to_string())

print("\n" + "=" * 70)
print("ROLE DISTRIBUTION ACROSS ALL PLAYERS")
print("=" * 70)
print(role_df['role'].value_counts())

# ── SAVE PROCESSED OUTPUTS FOR APP USE ────────────────────────────────────────
batting_by_season.to_csv("batting_by_season.csv", index=False)
bowling_by_season.to_csv("bowling_by_season.csv", index=False)
role_df.to_csv("player_roles.csv")

print("\n" + "=" * 70)
print("SAVED: batting_by_season.csv, bowling_by_season.csv, player_roles.csv")
print("=" * 70)