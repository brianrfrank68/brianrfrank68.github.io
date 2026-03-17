import sqlite3
from collections import defaultdict
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

DB_PATH = "strat.db"
OUT_FILE = "roster.pdf"

FONT      = "Courier"
FONT_BOLD = "Courier-Bold"
FONT_SIZE = 7
LINE_H    = 9
MARGIN    = 0.4 * inch

PAGE_W, PAGE_H = landscape(letter)
CONTENT_W = PAGE_W - 2 * MARGIN

BAT_COLS   = [
    ("Name",    28), ("Pos", 5), ("Age", 3), ("Tm", 5),
    ("G", 3), ("AB", 4), ("R", 3), ("H", 3), ("2B", 3), ("3B", 3),
    ("HR", 3), ("RBI", 4), ("SB", 3), ("CS", 3), ("BB", 4), ("SO", 4),
    ("BA", 5), ("OBP", 5), ("SLG", 5), ("OPS", 5), ("BRPos", 6),
]
PITCH_COLS = [
    ("Name",    28), ("Pos", 5), ("Age", 3), ("Tm", 5),
    ("W", 3), ("L", 3), ("ERA", 5), ("G", 3), ("GS", 3), ("GF", 3),
    ("SV", 3), ("IP", 6), ("H", 4), ("R", 4), ("ER", 4), ("HR", 3),
    ("BB", 4), ("SO", 4), ("FIP", 5), ("WHIP", 6),
    ("H9", 5), ("HR9", 5), ("BB9", 5), ("SO9", 5),
]

CHAR_W = 4.35  # approximate width of one Courier char at size 7


def col_x_positions(cols):
    """Return list of (label, x_start, width_px, right_align) for each column."""
    positions = []
    x = MARGIN
    for i, (label, chars) in enumerate(cols):
        w = chars * CHAR_W
        right_align = i > 0  # name column is left-aligned, stats are right
        positions.append((label, x, w, right_align))
        x += w + 2
    return positions


BAT_POS   = col_x_positions(BAT_COLS)
PITCH_POS = col_x_positions(PITCH_COLS)


class PDFReport:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=landscape(letter))
        self.y = PAGE_H - MARGIN
        self._new_page_needed = False

    def _check_space(self, lines=1):
        if self.y - lines * LINE_H < MARGIN:
            self.c.showPage()
            self.y = PAGE_H - MARGIN

    def text(self, x, y, txt, bold=False, size=FONT_SIZE):
        self.c.setFont(FONT_BOLD if bold else FONT, size)
        self.c.drawString(x, y, txt)

    def row(self, col_positions, values, bold=False):
        self._check_space()
        self.c.setFont(FONT_BOLD if bold else FONT, FONT_SIZE)
        for (label, x, w, right_align), val in zip(col_positions, values):
            val = str(val) if val is not None else ""
            if right_align:
                self.c.drawRightString(x + w, self.y, val)
            else:
                self.c.drawString(x, self.y, val)
        self.y -= LINE_H

    def separator(self, col_positions):
        self._check_space()
        total_w = col_positions[-1][1] + col_positions[-1][2] - MARGIN
        self.c.setLineWidth(0.3)
        self.c.line(MARGIN, self.y + LINE_H - 2, MARGIN + total_w, self.y + LINE_H - 2)
        self.y -= 2

    def section_header(self, label):
        self._check_space(3)
        self.y -= 4
        self.text(MARGIN, self.y, label, bold=True, size=8)
        self.y -= LINE_H

    def team_header(self, team):
        self._check_space(4)
        self.y -= 6
        self.c.setFont(FONT_BOLD, 10)
        self.c.drawString(MARGIN, self.y, f"=== {team} ===")
        self.y -= LINE_H + 2

    def page_break(self):
        self.c.showPage()
        self.y = PAGE_H - MARGIN

    def save(self):
        self.c.save()


def build_roster_output():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT player_id, player_name, MainPos FROM player_list")
    player_list = {row["player_id"]: dict(row) for row in cursor.fetchall()}

    cursor.execute('''SELECT "Player-additional", Age, Team, G, AB, R, H,
                      "2B", "3B", HR, RBI, SB, CS, BB, SO, BA, OBP, SLG, OPS, Pos
                      FROM Batting_2025''')
    batting = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    cursor.execute('''SELECT "Player-additional", Age, Team, W, L, ERA, G, GS, GF,
                      SV, IP, H, R, ER, HR, BB, SO, FIP, WHIP, H9, HR9, BB9, SO9
                      FROM Pitching_2025''')
    pitching = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    cursor.execute("SELECT full_name, flb_team_init, player_id FROM roster ORDER BY flb_team_init, player_id")
    teams = defaultdict(list)
    for row in cursor.fetchall():
        teams[row["flb_team_init"]].append((row["full_name"], row["player_id"]))

    conn.close()

    pdf = PDFReport(OUT_FILE)

    for team in sorted(teams.keys()):
        pdf.team_header(team)
        players = teams[team]

        batters = [(fn, pid) for fn, pid in players if pid in batting]
        if batters:
            pdf.section_header("-- Batters --")
            pdf.row(BAT_POS, [h for h, _ in BAT_COLS], bold=True)
            pdf.separator(BAT_POS)
            for full_name, player_id in batters:
                b = batting[player_id]
                pl = player_list.get(player_id, {})
                name = pl.get("player_name", full_name)
                main_pos = pl.get("MainPos", "")
                pdf.row(BAT_POS, [
                    name, main_pos, b["Age"], b["Team"],
                    b["G"], b["AB"], b["R"], b["H"], b["2B"], b["3B"],
                    b["HR"], b["RBI"], b["SB"], b["CS"], b["BB"], b["SO"],
                    b["BA"], b["OBP"], b["SLG"], b["OPS"], b["Pos"],
                ])

        pitchers = [(fn, pid) for fn, pid in players if pid in pitching]
        if pitchers:
            pdf.section_header("-- Pitchers --")
            pdf.row(PITCH_POS, [h for h, _ in PITCH_COLS], bold=True)
            pdf.separator(PITCH_POS)
            for full_name, player_id in pitchers:
                p = pitching[player_id]
                pl = player_list.get(player_id, {})
                name = pl.get("player_name", full_name)
                main_pos = pl.get("MainPos", "")
                pdf.row(PITCH_POS, [
                    name, main_pos, p["Age"], p["Team"],
                    p["W"], p["L"], p["ERA"], p["G"], p["GS"], p["GF"],
                    p["SV"], p["IP"], p["H"], p["R"], p["ER"], p["HR"],
                    p["BB"], p["SO"], p["FIP"], p["WHIP"],
                    p["H9"], p["HR9"], p["BB9"], p["SO9"],
                ])

        dnp = [(fn, pid) for fn, pid in players if pid not in batting and pid not in pitching]
        if dnp:
            pdf.section_header("-- Did Not Play --")
            for full_name, player_id in dnp:
                pl = player_list.get(player_id, {})
                name = pl.get("player_name", full_name)
                main_pos = pl.get("MainPos", "")
                pdf.row(BAT_POS[:2], [name, main_pos])
                pdf.y += LINE_H
                pdf.text(MARGIN + BAT_POS[1][1] + BAT_POS[1][2] + 4, pdf.y, "DNP")
                pdf.y -= LINE_H

        pdf.page_break()

    pdf.save()
    print(f"Written to {OUT_FILE}")


if __name__ == "__main__":
    build_roster_output()
