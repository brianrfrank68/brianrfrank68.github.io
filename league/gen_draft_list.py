import sqlite3
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

DB_PATH = "strat.db"

FONT      = "Courier"
FONT_BOLD = "Courier-Bold"
FONT_SIZE = 8
LINE_H    = 10
MARGIN    = 0.4 * inch

PAGE_W, PAGE_H = landscape(letter)
CONTENT_W = PAGE_W - 2 * MARGIN

# Positions in draft-board order: DH first, then the rest of the field, then pitchers.
POSITION_ORDER = ["DH", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "SP", "RP"]
PITCHER_POSITIONS = {"SP", "RP"}
POSITION_LABELS = {
    "C": "Catcher", "1B": "First Base", "2B": "Second Base", "3B": "Third Base",
    "SS": "Shortstop", "LF": "Left Field", "CF": "Center Field", "RF": "Right Field",
    "DH": "Designated Hitter", "SP": "Starting Pitcher", "RP": "Relief Pitcher",
}

BAT_COLS   = [
    ("No", 4), ("Name",    28), ("Age", 3), ("Tm", 5),
    ("G", 3), ("AB", 4), ("R", 3), ("H", 3), ("2B", 3), ("3B", 3),
    ("HR", 3), ("RBI", 4), ("SB", 3), ("CS", 3), ("BB", 4), ("SO", 4),
    ("BA", 5), ("OBP", 5), ("SLG", 5), ("OPS", 5), ("BRPos", 11),
]
PITCH_COLS = [
    ("No", 4), ("Name",    28), ("Age", 3), ("Tm", 5),
    ("W", 3), ("L", 3), ("ERA", 5), ("G", 3), ("GS", 3), ("GF", 3),
    ("SV", 3), ("IP", 6), ("H", 4), ("R", 4), ("ER", 4), ("HR", 3),
    ("BB", 4), ("SO", 4), ("FIP", 5), ("WHIP", 6),
    ("H9", 5), ("HR9", 5), ("BB9", 5), ("SO9", 5),
]

CHAR_W = FONT_SIZE * 0.62  # approximate width of one Courier char
SHADE_COLOR = (0.90, 0.90, 0.90)
EXTRA_GAP_BEFORE = {"BRPos": 12}  # breathing room before the trailing position column


def fmt3(v):
    try:
        return f"{float(v):.3f}"
    except (TypeError, ValueError):
        return ""


def fmt2(v):
    try:
        return f"{float(v):.2f}"
    except (TypeError, ValueError):
        return ""


def col_x_positions(cols):
    """Return list of (label, x_start, width_px, right_align) for each column."""
    positions = []
    x = MARGIN
    for i, (label, chars) in enumerate(cols):
        x += EXTRA_GAP_BEFORE.get(label, 0)
        w = chars * CHAR_W
        right_align = i != 1  # name column is left-aligned, No + stats are right
        positions.append((label, x, w, right_align))
        x += w + 2
    return positions


BAT_POS   = col_x_positions(BAT_COLS)
PITCH_POS = col_x_positions(PITCH_COLS)


class PDFReport:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=landscape(letter))
        self.y = PAGE_H - MARGIN

    def _check_space(self, lines=1):
        if self.y - lines * LINE_H < MARGIN:
            self.c.showPage()
            self.y = PAGE_H - MARGIN

    def text(self, x, y, txt, bold=False, size=FONT_SIZE):
        self.c.setFont(FONT_BOLD if bold else FONT, size)
        self.c.drawString(x, y, txt)

    def row(self, col_positions, values, bold=False, shade=False, grid=False):
        self._check_space()
        total_w = col_positions[-1][1] + col_positions[-1][2] - MARGIN
        if shade:
            self.c.setFillColorRGB(*SHADE_COLOR)
            self.c.rect(MARGIN, self.y - 2, total_w, LINE_H, fill=1, stroke=0)
            self.c.setFillColorRGB(0, 0, 0)
        self.c.setFont(FONT_BOLD if bold else FONT, FONT_SIZE)
        for (label, x, w, right_align), val in zip(col_positions, values):
            val = str(val) if val is not None else ""
            if right_align:
                self.c.drawRightString(x + w, self.y, val)
            else:
                self.c.drawString(x, self.y, val)
        self.y -= LINE_H
        if grid:
            self.c.setLineWidth(0.25)
            self.c.setStrokeColorRGB(0.6, 0.6, 0.6)
            self.c.line(MARGIN, self.y + LINE_H - 2, MARGIN + total_w, self.y + LINE_H - 2)
            self.c.setStrokeColorRGB(0, 0, 0)

    def separator(self, col_positions):
        self._check_space()
        total_w = col_positions[-1][1] + col_positions[-1][2] - MARGIN
        self.c.setLineWidth(0.3)
        self.c.line(MARGIN, self.y + LINE_H - 2, MARGIN + total_w, self.y + LINE_H - 2)
        self.y -= 2

    def position_header(self, label):
        self._check_space(4)
        self.y -= 6
        self.c.setFont(FONT_BOLD, 12)
        self.c.drawString(MARGIN, self.y, label)
        self.y -= LINE_H + 2

    def page_break(self):
        self.c.showPage()
        self.y = PAGE_H - MARGIN

    def save(self):
        self.c.save()


def build_draft_list(year=2026, out_file=None):
    out_file = out_file or f"draft_list_{year}.pdf"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT player_id, player_name, MainPos, mlb_team FROM player_list ORDER BY player_id")
    player_list = {row["player_id"]: dict(row) for row in cursor.fetchall()}

    cursor.execute("SELECT DISTINCT player_id FROM roster")
    rostered = {row["player_id"] for row in cursor.fetchall()}

    cursor.execute(f'''SELECT "Player-additional", Age, Team, G, AB, R, H, "2B", "3B",
                      HR, RBI, SB, CS, BB, SO, BA, OBP, SLG, OPS, Pos
                      FROM Batting_{year}''')
    batting = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    cursor.execute(f'''SELECT "Player-additional", Age, Team, W, L, ERA, G, GS, GF,
                      SV, IP, H, R, ER, HR, BB, SO, FIP, WHIP, H9, HR9, BB9, SO9
                      FROM Pitching_{year}''')
    pitching = {row["Player-additional"]: dict(row) for row in cursor.fetchall()}

    conn.close()

    # Players not on any team roster, grouped by their primary position and
    # ordered by player_id (same convention as gen_roster.py, which sorts
    # players alphabetically by last name via the Baseball-Reference id
    # scheme). Only players with current-year stats are draft-relevant
    # (excludes retired / inactive entries that linger in player_list).
    by_position = {pos: [] for pos in POSITION_ORDER}
    for player_id, p in player_list.items():
        if player_id in rostered:
            continue
        pos = p["MainPos"]
        if pos not in by_position:
            continue
        stat = pitching.get(player_id) if pos in PITCHER_POSITIONS else batting.get(player_id)
        if stat is None:
            continue
        by_position[pos].append((p, stat))

    pdf = PDFReport(out_file)
    draft_no = 1  # keeps climbing across every position, not reset per group

    for pos in POSITION_ORDER:
        players = by_position[pos]
        pdf.position_header(f"{POSITION_LABELS[pos]} ({pos}) -- {len(players)} available")

        if not players:
            pdf.text(MARGIN, pdf.y, "(none available)")
            pdf.y -= LINE_H
            pdf.page_break()
            continue

        cols = PITCH_POS if pos in PITCHER_POSITIONS else BAT_POS
        col_defs = PITCH_COLS if pos in PITCHER_POSITIONS else BAT_COLS
        pdf.row(cols, [h for h, _ in col_defs], bold=True)
        pdf.separator(cols)

        for i, (p, stat) in enumerate(players):
            name = p["player_name"]
            shade = i % 2 == 1
            if pos in PITCHER_POSITIONS:
                pdf.row(cols, [
                    draft_no, name, stat["Age"], stat["Team"],
                    stat["W"], stat["L"], fmt2(stat["ERA"]), stat["G"], stat["GS"], stat["GF"],
                    stat["SV"], stat["IP"], stat["H"], stat["R"], stat["ER"], stat["HR"],
                    stat["BB"], stat["SO"], fmt2(stat["FIP"]), fmt2(stat["WHIP"]),
                    stat["H9"], stat["HR9"], stat["BB9"], stat["SO9"],
                ], shade=shade, grid=True)
            else:
                pdf.row(cols, [
                    draft_no, name, stat["Age"], stat["Team"],
                    stat["G"], stat["AB"], stat["R"], stat["H"], stat["2B"], stat["3B"],
                    stat["HR"], stat["RBI"], stat["SB"], stat["CS"], stat["BB"], stat["SO"],
                    fmt3(stat["BA"]), fmt3(stat["OBP"]), fmt3(stat["SLG"]), fmt3(stat["OPS"]), stat["Pos"],
                ], shade=shade, grid=True)
            draft_no += 1

        pdf.page_break()

    pdf.save()
    print(f"Written to {out_file}")


if __name__ == "__main__":
    build_draft_list(2026)
