import sqlite3
from collections import namedtuple

def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)

def get_teams():
    cur = con.execute("SELECT distinct flb_team_init FROM roster ORDER BY flb_team_init")
    return cur.fetchall()

def get_team_players(team):
    sql = "SELECT player_name, player_list.mlb_team FROM roster, player_list WHERE flb_team_init = '%s' and roster.player_id = player_list.player_id ORDER BY roster.player_id" % team.flb_team_init
    cur = con.execute(sql)
    return cur.fetchall()

con = sqlite3.connect("strat.db")
con.row_factory = namedtuple_factory

team_rows = get_teams()

for team in team_rows:
    print(team.flb_team_init)
    player_rows = get_team_players(team)
    for player in player_rows:
        print(player.player_name + "," + player.mlb_team)
    print()

# con.row_factory = sqlite3.Row
# res = con.execute("SELECT * from Batting")
# row = res.fetchone()
# print(row.keys())
