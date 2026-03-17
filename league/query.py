import sqlite3
from collections import defaultdict

DB_PATH = "strat.db"
OUT_FILE = "roster.txt"

def build_roster_output():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Load player_list lookup keyed by player_id
    cursor.execute("SELECT player_id, player_name, MainPos FROM player_list")
    player_list = {row["player_id"]: dict(row) for row in cursor.fetchall()}

    # Load batting and pitching lookup dicts keyed by player-additional
    cursor.execute('''SELECT "Player-additional", Age, Team, G, AB, R, H,
                      "2B", "3B", HR, RBI, SB, CS, BB, SO, BA, OBP, SLG, OPS, Pos
                      FROM Batting_2025''')
    batting = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    cursor.execute('''SELECT "Player-additional", Age, Team, W, L, ERA, G, GS, GF,
                      SV, IP, H, R, ER, HR, BB, SO, FIP, WHIP, H9, HR9, BB9, SO9
                      FROM Pitching_2025''')
    pitching = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    # Group roster by team
    cursor.execute("SELECT full_name, flb_team_init, player_id FROM roster ORDER BY flb_team_init, player_id")
    teams = defaultdict(list)
    for row in cursor.fetchall():
        teams[row["flb_team_init"]].append((row["full_name"], row["player_id"]))

    conn.close()

    BAT_HDR  = f"  {'Name':<28} {'Pos':<5} {'Age':>3} {'Tm':<5} {'G':>3} {'AB':>4} {'R':>3} {'H':>3} {'2B':>3} {'3B':>3} {'HR':>3} {'RBI':>4} {'SB':>3} {'CS':>3} {'BB':>4} {'SO':>4} {'BA':>5} {'OBP':>5} {'SLG':>5} {'OPS':>5} {'Pos'}\n"
    BAT_SEP  = "  " + "-" * (len(BAT_HDR) - 3) + "\n"
    PITCH_HDR= f"  {'Name':<28} {'Pos':<5} {'Age':>3} {'Tm':<5} {'W':>3} {'L':>3} {'ERA':>5} {'G':>3} {'GS':>3} {'GF':>3} {'SV':>3} {'IP':>6} {'H':>4} {'R':>4} {'ER':>4} {'HR':>3} {'BB':>4} {'SO':>4} {'FIP':>5} {'WHIP':>6} {'H9':>5} {'HR9':>5} {'BB9':>5} {'SO9':>5}\n"
    PITCH_SEP= "  " + "-" * (len(PITCH_HDR) - 3) + "\n"

    with open(OUT_FILE, "w") as f:
        for team in sorted(teams.keys()):
            f.write(f"=== {team} ===\n")
            players = teams[team]

            # Batters first
            batters = [(fn, pid) for fn, pid in players if pid in batting]
            if batters:
                f.write("\n  -- Batters --\n")
                f.write(BAT_HDR)
                f.write(BAT_SEP)
                for full_name, player_id in batters:
                    b = batting[player_id]
                    pl = player_list.get(player_id, {})
                    name = pl.get("player_name", full_name)
                    main_pos = pl.get("MainPos", "")
                    f.write(f"  {name:<28} {main_pos:<5} {str(b['Age']):>3} {str(b['Team']):<5} "
                            f"{str(b['G']):>3} {str(b['AB']):>4} {str(b['R']):>3} {str(b['H']):>3} "
                            f"{str(b['2B']):>3} {str(b['3B']):>3} {str(b['HR']):>3} {str(b['RBI']):>4} "
                            f"{str(b['SB']):>3} {str(b['CS']):>3} {str(b['BB']):>4} {str(b['SO']):>4} "
                            f"{str(b['BA']):>5} {str(b['OBP']):>5} {str(b['SLG']):>5} {str(b['OPS']):>5} "
                            f"{b['Pos']}\n")

            # Pitchers next
            pitchers = [(fn, pid) for fn, pid in players if pid in pitching]
            if pitchers:
                f.write("\n  -- Pitchers --\n")
                f.write(PITCH_HDR)
                f.write(PITCH_SEP)
                for full_name, player_id in pitchers:
                    p = pitching[player_id]
                    pl = player_list.get(player_id, {})
                    name = pl.get("player_name", full_name)
                    main_pos = pl.get("MainPos", "")
                    f.write(f"  {name:<28} {main_pos:<5} {str(p['Age']):>3} {str(p['Team']):<5} "
                            f"{str(p['W']):>3} {str(p['L']):>3} {str(p['ERA']):>5} {str(p['G']):>3} "
                            f"{str(p['GS']):>3} {str(p['GF']):>3} {str(p['SV']):>3} {str(p['IP']):>6} "
                            f"{str(p['H']):>4} {str(p['R']):>4} {str(p['ER']):>4} {str(p['HR']):>3} "
                            f"{str(p['BB']):>4} {str(p['SO']):>4} {str(p['FIP']):>5} {str(p['WHIP']):>6} "
                            f"{str(p['H9']):>5} {str(p['HR9']):>5} {str(p['BB9']):>5} {str(p['SO9']):>5}\n")

            # DNP last
            dnp = [(fn, pid) for fn, pid in players if pid not in batting and pid not in pitching]
            if dnp:
                f.write("\n  -- Did Not Play --\n")
                for full_name, player_id in dnp:
                    pl = player_list.get(player_id, {})
                    name = pl.get("player_name", full_name)
                    main_pos = pl.get("MainPos", "")
                    f.write(f"  {name:<28} {main_pos:<5}  DNP\n")

            f.write("\n")

    print(f"Written to {OUT_FILE}")

if __name__ == "__main__":
    build_roster_output()
