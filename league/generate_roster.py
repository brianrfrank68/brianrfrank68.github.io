import sqlite3
from collections import namedtuple
from fpdf import FPDF

def namedtuple_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    cls = namedtuple("Row", fields)
    return cls._make(row)

def get_teams():
    cur = con.execute("SELECT distinct flb_team_init FROM roster WHERE flb_team_init = 'BFP' ORDER BY flb_team_init")
    return cur.fetchall()

def get_team_players(team):
    sql = "SELECT full_name, player_id FROM roster WHERE flb_team_init = '%s' ORDER BY player_id" % team.flb_team_init
    cur = con.execute(sql)
    return cur.fetchall()

def get_batter_line(player):
    # ['Rk', 'Name', 'Age', 'Tm', 'Lg', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'OPS+', 'TB', 'GDP', 'HBP', 'SH', 'SF', 'IBB', 'Pos Summary', 'Name-additional']
    sql = "SELECT Name, Age, Tm, G, AB, R, H, [2B] AS Doubles, [3B] AS Triples, HR, RBI, SB, CS, SO, BA, OBP, SLG, OPS, [Pos Summary] AS Positions, [Name-additional] AS player_id FROM Batting WHERE [Name-additional] = '%s' " % player.player_id
    cur = con.execute(sql)
    return cur.fetchone()

con = sqlite3.connect("strat.db")
con.row_factory = namedtuple_factory

team_rows = get_teams()

for team in team_rows:
    batterstr = ""
    pdf = FPDF()
    pdf.add_page(orientation = "L")
    pdf.set_font("Arial", size = 10)
    pdf.cell(0, 10, txt = team.flb_team_init, ln = 1, align = 'L')
    
    print(team.flb_team_init)
    player_rows = get_team_players(team)
    for player in player_rows:
        print(player.full_name + ":" + player.player_id)
        batter = get_batter_line(player)
        if batter != None:
            for ele in batter:
                batterstr += str(ele)
            print(batter)
            pdf.cell(0, 10, txt = batterstr, ln = 1, align = 'L')

    pdf.output("GFG.pdf") 

# con.row_factory = sqlite3.Row
# res = con.execute("SELECT * from Batting")
# row = res.fetchone()
# print(row.keys())
