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

# Normalize team-name variants that refer to the same franchise, so a player's
# head-to-head record doesn't get incorrectly split across two labels.
#   - "Rising Pune Supergiant" / "Rising Pune Supergiants" — inconsistent
#     pluralisation in the source data for the same single-season franchise.
#   - "Royal Challengers Bangalore" / "Royal Challengers Bengaluru" — real
#     city rename, same franchise throughout.
# Kings XI Punjab -> Punjab Kings is left as separate, since that's a more
# debatable rename many fans still track as distinct eras.
TEAM_NAME_FIX = {
    'Rising Pune Supergiant': 'Rising Pune Supergiants',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
}

for col in ['BattingTeam']:
    if col in balls.columns:
        balls[col] = balls[col].replace(TEAM_NAME_FIX)
for col in ['team1', 'team2']:
    matches[col] = matches[col].replace(TEAM_NAME_FIX)

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

# ════════════════════════════════════════════════════════════════════════════
# BOWLER DOT-BALL % (career)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BOWLER DOT-BALL %")
print("=" * 70)

bowl_legal_for_dots = balls[balls['IsLegalBall']].copy()
# A dot ball = zero total runs off that delivery (no runs, no extras conceded)
bowl_legal_for_dots['IsDot'] = bowl_legal_for_dots['BowlerConcededRuns'] == 0

bowler_dots = bowl_legal_for_dots.groupby('Bowler').agg(
    balls_bowled=('BallNumber', 'count'),
    dot_balls=('IsDot', 'sum')
).reset_index()
bowler_dots['dot_pct'] = (bowler_dots['dot_balls'] / bowler_dots['balls_bowled'] * 100).round(2)
bowler_dots.to_csv("bowler_dot_ball_pct.csv", index=False)

print(bowler_dots[bowler_dots['Bowler'] == 'JJ Bumrah'].to_string(index=False))
print("\nTop 5 dot-ball bowlers (min 500 balls):")
print(bowler_dots[bowler_dots['balls_bowled'] >= 500].sort_values('dot_pct', ascending=False).head(5).to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# BATTER DOT-BALL %, BALLS PER BOUNDARY, DISMISSAL BREAKDOWN, FINISHING RATE
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("BATTER DOT-BALL %, BOUNDARY RATE, FINISHING RATE")
print("=" * 70)

bat_legal_for_dots = balls[balls['IsLegalBall']].copy()
bat_legal_for_dots['IsDot'] = bat_legal_for_dots['BatsmanRun'] == 0
bat_legal_for_dots['IsBoundary'] = bat_legal_for_dots['BatsmanRun'].isin([4, 6])

batter_dots = bat_legal_for_dots.groupby('Batter').agg(
    balls_faced=('BallNumber', 'count'),
    dot_balls=('IsDot', 'sum'),
    boundaries=('IsBoundary', 'sum')
).reset_index()
batter_dots['dot_pct'] = (batter_dots['dot_balls'] / batter_dots['balls_faced'] * 100).round(2)
batter_dots['balls_per_boundary'] = np.where(
    batter_dots['boundaries'] > 0,
    (batter_dots['balls_faced'] / batter_dots['boundaries']).round(2),
    np.nan
)

# Finishing rate: % of innings where the batter was NOT dismissed (i.e. "finished" the innings)
innings_played = bat_legal_for_dots.groupby(['Batter', 'ID']).size().reset_index(name='balls_in_innings')
total_innings = innings_played.groupby('Batter').size().reset_index(name='total_innings')

dismissed_innings = balls[balls['IsWicketDelivery'] == 1].groupby('PlayerOut')['ID'].nunique().reset_index(name='dismissed_innings')
dismissed_innings = dismissed_innings.rename(columns={'PlayerOut': 'Batter'})

finishing = total_innings.merge(dismissed_innings, on='Batter', how='left')
finishing['dismissed_innings'] = finishing['dismissed_innings'].fillna(0)
finishing['not_out_innings'] = finishing['total_innings'] - finishing['dismissed_innings']
finishing['finishing_rate_pct'] = (finishing['not_out_innings'] / finishing['total_innings'] * 100).round(2)

batter_dots = batter_dots.merge(finishing[['Batter', 'total_innings', 'finishing_rate_pct']], on='Batter', how='left')
batter_dots.to_csv("batter_dot_ball_pct.csv", index=False)

print(batter_dots[batter_dots['Batter'] == 'V Kohli'].to_string(index=False))

# Dismissal type breakdown per batter
batter_dismissals = balls[
    (balls['IsWicketDelivery'] == 1) & (~balls['Kind'].isin(['retired hurt', 'retired out', 'NA']))
].groupby(['PlayerOut', 'Kind']).size().reset_index(name='count')
batter_dismissals = batter_dismissals.rename(columns={'PlayerOut': 'Batter'})
batter_dismissals.to_csv("batter_dismissal_types.csv", index=False)

print("\nSample — V Kohli dismissal types:")
print(batter_dismissals[batter_dismissals['Batter'] == 'V Kohli'].to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# WICKET-KEEPER STUMPINGS
# ════════════════════════════════════════════════════════════════════════════
# Honest scope: Cricsheet only reliably attributes STUMPINGS to a specific
# fielder (always the keeper, by the rules of cricket). Catches and byes can't
# be reliably attributed to "the keeper" specifically vs. any other fielder,
# since there's no role field — so we deliberately do NOT build those.
print("\n" + "=" * 70)
print("WICKET-KEEPER STUMPINGS (career)")
print("=" * 70)

stumpings = balls[balls['Kind'] == 'stumped'].groupby('FieldersInvolved').size().reset_index(name='stumpings')
stumpings = stumpings.rename(columns={'FieldersInvolved': 'Keeper'})
stumpings = stumpings.sort_values('stumpings', ascending=False)
stumpings.to_csv("keeper_stumpings.csv", index=False)

print(stumpings.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("SAVED: bowler_dot_ball_pct.csv, batter_dot_ball_pct.csv,")
print("       batter_dismissal_types.csv, keeper_stumpings.csv")
print("=" * 70)

# ════════════════════════════════════════════════════════════════════════════
# HEAD-TO-HEAD vs SPECIFIC TEAMS
# ════════════════════════════════════════════════════════════════════════════
# Derive bowling team the same way the base pipeline does, since this script
# doesn't already have it.
print("\n" + "=" * 70)
print("HEAD-TO-HEAD vs OPPOSITION TEAMS")
print("=" * 70)

def get_bowling_team(row):
    if row['BattingTeam'] == row['team1']:
        return row['team2']
    elif row['BattingTeam'] == row['team2']:
        return row['team1']
    return np.nan

balls['BowlingTeam'] = balls.apply(get_bowling_team, axis=1)
bat_legal_h2h = balls[balls['IsLegalBall']]

# Batting head-to-head: player's record broken down by which team they faced
batting_h2h = bat_legal_h2h.groupby(['Batter', 'BowlingTeam']).agg(
    runs=('BatsmanRun', 'sum'),
    balls_faced=('BallNumber', 'count'),
    innings=('ID', 'nunique')
).reset_index()
batting_h2h['strike_rate'] = (batting_h2h['runs'] / batting_h2h['balls_faced'] * 100).round(2)
batting_h2h = batting_h2h.rename(columns={'BowlingTeam': 'Opponent'})
batting_h2h.to_csv("batting_head_to_head.csv", index=False)

print("Sample — V Kohli vs opposition teams:")
print(batting_h2h[batting_h2h['Batter'] == 'V Kohli'].sort_values('runs', ascending=False).head(8).to_string(index=False))

# Bowling head-to-head: player's record broken down by which team they bowled against
bowl_legal_h2h = balls[balls['IsLegalBall']]
bowling_h2h = bowl_legal_h2h.groupby(['Bowler', 'BattingTeam']).agg(
    runs_conceded=('BowlerConcededRuns', 'sum'),
    balls_bowled=('BallNumber', 'count')
).reset_index()
bowling_h2h['overs'] = (bowling_h2h['balls_bowled'] // 6) + (bowling_h2h['balls_bowled'] % 6) / 6
bowling_h2h['economy'] = (bowling_h2h['runs_conceded'] / bowling_h2h['overs']).round(2)

wickets_h2h = balls[
    (balls['IsWicketDelivery'] == 1) & (~balls['Kind'].isin(['run out', 'retired hurt', 'retired out', 'NA']))
].groupby(['Bowler', 'BattingTeam']).size().reset_index(name='wickets')

bowling_h2h = bowling_h2h.merge(wickets_h2h, on=['Bowler', 'BattingTeam'], how='left')
bowling_h2h['wickets'] = bowling_h2h['wickets'].fillna(0).astype(int)
bowling_h2h = bowling_h2h.rename(columns={'BattingTeam': 'Opponent'})
bowling_h2h.to_csv("bowling_head_to_head.csv", index=False)

print("\nSample — JJ Bumrah vs opposition teams:")
print(bowling_h2h[bowling_h2h['Bowler'] == 'JJ Bumrah'].sort_values('wickets', ascending=False).head(8).to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# PLAYER AGE (only covers players in 2024_players_details.csv — 261 players)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PLAYER AGE (LIMITED COVERAGE — 261 PLAYERS ONLY)")
print("=" * 70)

try:
    player_details = pd.read_csv(f"{DATA_DIR}/2024_players_details.csv")
    player_details['dob_parsed'] = pd.to_datetime(player_details['dob'], format='%d/%m/%Y', errors='coerce')
    # Age as of mid-2026 (current point in time for this project)
    reference_date = pd.Timestamp('2026-06-01')
    player_details['age'] = ((reference_date - player_details['dob_parsed']).dt.days / 365.25).round(1)

    player_ages = player_details[['Name', 'dob', 'age', 'battingStyles', 'bowlingStyles']].rename(
        columns={'Name': 'Player'}
    )
    player_ages.to_csv("player_ages.csv", index=False)

    print(f"Coverage: {len(player_ages)} players (out of 800+ in the full dataset)")
    print(player_ages[player_ages['Player'] == 'MS Dhoni'].to_string(index=False))
except FileNotFoundError:
    print("2024_players_details.csv not found — skipping age data.")

# ════════════════════════════════════════════════════════════════════════════
# SEASON-GAP DETECTION (durability/availability proxy — works for everyone)
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("SEASON-GAP DETECTION (missed seasons within active career span)")
print("=" * 70)

# A player's "active span" runs from their debut season to their most recent
# season. Any season inside that span where they have zero recorded innings
# (batting or bowling) counts as a missed season — a visible proxy for injury,
# being dropped, or unavailability. This isn't proof of injury specifically,
# just a flag worth a coach's attention.
all_seasons_in_data = sorted(matches['season'].dropna().unique().astype(int))

bat_seasons = bat_legal_h2h.groupby('Batter')['season'].apply(lambda x: set(x.dropna().astype(int))).reset_index()
bat_seasons = bat_seasons.rename(columns={'season': 'seasons_played', 'Batter': 'Player'})

bowl_seasons = bowl_legal_h2h.groupby('Bowler')['season'].apply(lambda x: set(x.dropna().astype(int))).reset_index()
bowl_seasons = bowl_seasons.rename(columns={'season': 'seasons_played', 'Bowler': 'Player'})

# Combine batting + bowling season sets per player (covers all-rounders correctly)
combined_seasons = pd.concat([bat_seasons, bowl_seasons]).groupby('Player')['seasons_played'].apply(
    lambda sets: set().union(*sets)
).reset_index()

def compute_gaps(seasons_played):
    if not seasons_played or len(seasons_played) < 2:
        return 0, []
    span = list(range(min(seasons_played), max(seasons_played) + 1))
    missed = [s for s in span if s not in seasons_played]
    return len(missed), missed

combined_seasons['missed_count'], combined_seasons['missed_seasons'] = zip(
    *combined_seasons['seasons_played'].apply(compute_gaps)
)
combined_seasons['debut_season'] = combined_seasons['seasons_played'].apply(min)
combined_seasons['latest_season'] = combined_seasons['seasons_played'].apply(max)
combined_seasons['missed_seasons'] = combined_seasons['missed_seasons'].apply(lambda x: ','.join(map(str, x)))

season_gaps = combined_seasons[['Player', 'debut_season', 'latest_season', 'missed_count', 'missed_seasons']]
season_gaps.to_csv("player_season_gaps.csv", index=False)

print("Sample — JJ Bumrah season gaps:")
print(season_gaps[season_gaps['Player'] == 'JJ Bumrah'].to_string(index=False))
print("\nPlayers with most missed seasons (min 5 active seasons):")
multi_season = season_gaps[(season_gaps['latest_season'] - season_gaps['debut_season']) >= 5]
print(multi_season.sort_values('missed_count', ascending=False).head(8).to_string(index=False))

print("\n" + "=" * 70)
print("SAVED: batting_head_to_head.csv, bowling_head_to_head.csv,")
print("       player_ages.csv, player_season_gaps.csv")
print("=" * 70)

print("\n" + "=" * 70)
print("SAVED: batting_by_phase.csv, bowling_by_phase.csv,")
print("       batting_innings.csv, bowling_innings.csv, bowler_wicket_types.csv")
print("=" * 70)