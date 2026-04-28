"""
TSIS 2 – Paint Application (Extended)
Adds to Practice 10/11:
  • Pencil (freehand)            – existing, improved
  • Straight line tool           – NEW (live preview)
  • Rectangle, Circle, Eraser   – existing
  • Square, Right triangle, Equilateral triangle, Rhombus – from P11
  • Three brush sizes (S/M/L)   – NEW (keyboard 1/2/3 + buttons)
  • Flood-fill tool              – NEW
  • Text tool                    – NEW (click → type → Enter to confirm)
  • Ctrl+S → timestamped PNG     – NEW
"""

import pygame
import sys
import math
import collections
from datetime import datetime

pygame.init()

# ── Layout ───────────────────────────────────────────────────────────────────
SCREEN_W   = 1000
SCREEN_H   = 680
TOOLBAR_H  = 80
CANVAS_TOP = TOOLBAR_H
CANVAS_H   = SCREEN_H - TOOLBAR_H
CANVAS_RECT = pygame.Rect(0, CANVAS_TOP, SCREEN_W, CANVAS_H)

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
LT_GRAY = (235, 237, 240)
MID_GRY = (170, 172, 176)
DK_GRAY = ( 70,  72,  76)
ACCENT  = ( 66, 133, 244)   # highlight for active tool / size

PALETTE = [
    (  0,   0,   0), (255, 255, 255), (220,  30,  30), ( 30, 180,  30),
    ( 30,  80, 220), (255, 220,   0), (255, 130,   0), (140,   0, 200),
    (  0, 200, 200), (255,   0, 180), (120,  80,  40), (100, 100, 100),
    (255, 160, 180), (  0, 100,  60),
]

# ── Tools ─────────────────────────────────────────────────────────────────────
PENCIL   = "pencil"
LINE     = "line"
RECT     = "rect"
CIRCLE   = "circle"
SQUARE   = "square"
RTRI     = "right_tri"
ETRI     = "eq_tri"
RHOMBUS  = "rhombus"
ERASER   = "eraser"
FILL     = "fill"
TEXT     = "text"

TOOL_ROWS = [
    [(PENCIL,  "✏ Pencil"),  (LINE,    "╱ Line"),   (RECT,   "▭ Rect"),
     (CIRCLE,  "◯ Circle"),  (SQUARE,  "■ Square"), (RTRI,   "◺ RTri")],
    [(ETRI,    "△ ETri"),    (RHOMBUS, "◇ Rhomb"),  (FILL,   "▓ Fill"),
     (TEXT,    "T Text"),    (ERASER,  "⌫ Erase"),  (None,   None)],
]

# ── Brush sizes ───────────────────────────────────────────────────────────────
BRUSH_SIZES = [2, 5, 10]   # small, medium, large
SIZE_LABELS = ["S", "M", "L"]

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_btn  = pygame.font.SysFont("Arial", 13, bold=True)
font_sm   = pygame.font.SysFont("Arial", 12)
font_text = pygame.font.SysFont("Arial", 24)   # canvas text tool

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – TSIS 2")
clock  = pygame.time.Clock()


# ─────────────────────────────────────────────────────────────────────────────
class PaintApp:
    def __init__(self):
        self.canvas = pygame.Surface((SCREEN_W, CANVAS_H))
        self.canvas.fill(WHITE)

        self.color      = BLACK
        self.tool       = PENCIL
        self.size_idx   = 1          # 0=S 1=M 2=L
        self.eraser_r   = 18

        # stroke state
        self.drawing    = False
        self.start_pos  = None
        self.prev_pos   = None

        # text tool state
        self.text_active  = False
        self.text_pos     = None     # canvas coords
        self.text_buf     = ""

        # status bar message
        self._status = "Ready"

    # ── helpers ──────────────────────────────────────────────────────────────
    @property
    def brush(self):
        return BRUSH_SIZES[self.size_idx]

    def _screen_to_canvas(self, pos):
        mx, my = pos
        cx = max(0, min(SCREEN_W - 1, mx))
        cy = max(CANVAS_TOP, min(SCREEN_H - 1, my))
        return cx, cy - CANVAS_TOP

    # ── Event entry point ────────────────────────────────────────────────────
    def handle(self, event):
        # ── keyboard ─────────────────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:
            # Text tool receives all keys while active
            if self.text_active:
                self._text_key(event)
                return

            mods = pygame.key.get_mods()
            if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                self._save_canvas()
            elif event.key == pygame.K_1:
                self.size_idx = 0
            elif event.key == pygame.K_2:
                self.size_idx = 1
            elif event.key == pygame.K_3:
                self.size_idx = 2

        # ── mouse ─────────────────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_press(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.drawing:
            self._on_drag(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._on_release(event.pos)

    # ── Press ────────────────────────────────────────────────────────────────
    def _on_press(self, pos):
        mx, my = pos

        # Click in toolbar → toolbar action, cancel any text
        if my < TOOLBAR_H:
            self._commit_text()
            self._toolbar_click(mx, my)
            return

        # Commit any in-progress text before starting a new action
        if self.text_active and self.tool != TEXT:
            self._commit_text()

        cp = self._screen_to_canvas(pos)

        # Text tool: place cursor
        if self.tool == TEXT:
            self._commit_text()       # commit previous if any
            self.text_active = True
            self.text_pos    = cp
            self.text_buf    = ""
            self._status = "Type text, Enter to confirm, Esc to cancel"
            return

        # Fill tool: immediate action
        if self.tool == FILL:
            target_color = self.canvas.get_at(cp)[:3]
            if target_color != self.color:
                self._flood_fill(cp, target_color, self.color)
            return

        self.drawing   = True
        self.start_pos = cp
        self.prev_pos  = cp

        if self.tool == PENCIL:
            pygame.draw.circle(self.canvas, self.color, cp, self.brush)
        elif self.tool == ERASER:
            pygame.draw.circle(self.canvas, WHITE, cp, self.eraser_r)

    # ── Drag ─────────────────────────────────────────────────────────────────
    def _on_drag(self, pos):
        cp = self._screen_to_canvas(pos)

        if self.tool == PENCIL:
            pygame.draw.line(self.canvas, self.color, self.prev_pos, cp,
                             max(1, self.brush * 2))
            pygame.draw.circle(self.canvas, self.color, cp, self.brush)
            self.prev_pos = cp

        elif self.tool == ERASER:
            pygame.draw.circle(self.canvas, WHITE, cp, self.eraser_r)
            self.prev_pos = cp

        # For shape tools and LINE: preview is handled in draw(); no canvas write here

    # ── Release ──────────────────────────────────────────────────────────────
    def _on_release(self, pos):
        if not self.drawing:
            return
        cp = self._screen_to_canvas(pos)
        shape_tools = {RECT, CIRCLE, SQUARE, RTRI, ETRI, RHOMBUS, LINE}
        if self.tool in shape_tools:
            self._draw_shape(self.start_pos, cp, self.canvas)

        self.drawing   = False
        self.start_pos = None
        self.prev_pos  = None

    # ── Shape helper ─────────────────────────────────────────────────────────
    def _draw_shape(self, p1, p2, surface):
        x1, y1 = p1
        x2, y2 = p2
        w = self.brush

        if self.tool == LINE:
            pygame.draw.line(surface, self.color, p1, p2, w)

        elif self.tool == RECT:
            r = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
            pygame.draw.rect(surface, self.color, r, w)

        elif self.tool == SQUARE:
            side = min(abs(x2-x1), abs(y2-y1))
            sx = x1 if x2 >= x1 else x1 - side
            sy = y1 if y2 >= y1 else y1 - side
            pygame.draw.rect(surface, self.color, (sx, sy, side, side), w)

        elif self.tool == CIRCLE:
            cx = (x1+x2)//2; cy = (y1+y2)//2
            r  = int(math.hypot(x2-x1, y2-y1)/2)
            if r > 0:
                pygame.draw.circle(surface, self.color, (cx, cy), r, w)

        elif self.tool == RTRI:
            pts = [(x1,y2), (x1,y1), (x2,y2)]
            pygame.draw.polygon(surface, self.color, pts, w)

        elif self.tool == ETRI:
            bx = (x1+x2)/2
            pts = [(x1,y2), (x2,y2), (bx,y1)]
            pygame.draw.polygon(surface, self.color, pts, w)

        elif self.tool == RHOMBUS:
            cx = (x1+x2)//2; cy = (y1+y2)//2
            pts = [(cx,y1), (x2,cy), (cx,y2), (x1,cy)]
            pygame.draw.polygon(surface, self.color, pts, w)

    # ── Flood fill (BFS) ─────────────────────────────────────────────────────
    def _flood_fill(self, start, target_col, fill_col):
        sw, sh = self.canvas.get_size()
        visited = [[False]*sh for _ in range(sw)]
        q = collections.deque()
        q.append(start)
        visited[start[0]][start[1]] = True

        while q:
            x, y = q.popleft()
            self.canvas.set_at((x, y), fill_col)
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < sw and 0 <= ny < sh and not visited[nx][ny]:
                    if self.canvas.get_at((nx, ny))[:3] == target_col:
                        visited[nx][ny] = True
                        q.append((nx, ny))

    # ── Text tool ─────────────────────────────────────────────────────────────
    def _text_key(self, event):
        if event.key == pygame.K_RETURN:
            self._commit_text()
        elif event.key == pygame.K_ESCAPE:
            self.text_active = False
            self.text_buf    = ""
            self._status = "Ready"
        elif event.key == pygame.K_BACKSPACE:
            self.text_buf = self.text_buf[:-1]
        else:
            ch = event.unicode
            if ch and ch.isprintable():
                self.text_buf += ch

    def _commit_text(self):
        if self.text_active and self.text_buf:
            rendered = font_text.render(self.text_buf, True, self.color)
            self.canvas.blit(rendered, self.text_pos)
        self.text_active = False
        self.text_buf    = ""
        self._status = "Ready"

    # ── Save canvas ───────────────────────────────────────────────────────────
    def _save_canvas(self):
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"canvas_{ts}.png"
        pygame.image.save(self.canvas, name)
        self._status = f"Saved → {name}"

    # ── Toolbar click ─────────────────────────────────────────────────────────
    def _toolbar_click(self, mx, my):
        # Palette swatches  (row 1, top area)
        for i, col in enumerate(PALETTE):
            sx = 10 + i*36
            if sx <= mx <= sx+30 and 6 <= my <= 30:
                self.color = col
                return

        # Tool buttons (two rows)
        for row_i, row in enumerate(TOOL_ROWS):
            for col_i, (tool, label) in enumerate(row):
                if tool is None:
                    continue
                bx = 10 + col_i * 95
                by = 36 + row_i * 22
                if bx <= mx <= bx+88 and by <= my <= by+18:
                    self.tool = tool
                    if tool != TEXT:
                        self._commit_text()
                    return

        # Brush size buttons (S M L)
        for i in range(3):
            bx = SCREEN_W - 190 + i*36
            if bx <= mx <= bx+30 and 14 <= my <= 38:
                self.size_idx = i
                return

        # Eraser size +/–
        if SCREEN_W-100 <= mx <= SCREEN_W-82 and 46 <= my <= 66:
            self.eraser_r = max(5, self.eraser_r - 3)
        elif SCREEN_W-76 <= mx <= SCREEN_W-58 and 46 <= my <= 66:
            self.eraser_r = min(60, self.eraser_r + 3)

        # Clear button
        if SCREEN_W-52 <= mx <= SCREEN_W-6 and 8 <= my <= 36:
            self.canvas.fill(WHITE)
            self._commit_text()

    # ── Draw everything ───────────────────────────────────────────────────────
    def draw(self, surface):
        # ── Canvas ────────────────────────────────────────────────────────────
        surface.blit(self.canvas, (0, CANVAS_TOP))

        # Live preview for shape tools
        mx, my = pygame.mouse.get_pos()
        if self.drawing and self.start_pos:
            shape_tools = {RECT, CIRCLE, SQUARE, RTRI, ETRI, RHOMBUS, LINE}
            if self.tool in shape_tools:
                cp = self._screen_to_canvas((mx, my))
                preview = pygame.Surface((SCREEN_W, CANVAS_H), pygame.SRCALPHA)
                self._draw_shape(self.start_pos, cp, preview)
                surface.blit(preview, (0, CANVAS_TOP))

        # Text cursor / live typing preview
        if self.text_active and self.text_pos:
            tx, ty = self.text_pos
            rendered = font_text.render(self.text_buf + "|", True, self.color)
            surface.blit(rendered, (tx, ty + CANVAS_TOP))

        # Eraser cursor ring
        if self.tool == ERASER:
            pygame.draw.circle(surface, MID_GRY, (mx, my), self.eraser_r, 2)

        # Fill cursor crosshair
        if self.tool == FILL and my >= CANVAS_TOP:
            pygame.draw.line(surface, DK_GRAY, (mx-8, my), (mx+8, my), 1)
            pygame.draw.line(surface, DK_GRAY, (mx, my-8), (mx, my+8), 1)

        # ── Toolbar ───────────────────────────────────────────────────────────
        pygame.draw.rect(surface, LT_GRAY, (0, 0, SCREEN_W, TOOLBAR_H))
        pygame.draw.line(surface, MID_GRY, (0, TOOLBAR_H), (SCREEN_W, TOOLBAR_H), 2)

        # Palette
        for i, col in enumerate(PALETTE):
            sx = 10 + i*36
            pygame.draw.rect(surface, col, (sx, 6, 30, 24))
            border = ACCENT if col == self.color else DK_GRAY
            thick  = 3 if col == self.color else 1
            pygame.draw.rect(surface, border, (sx, 6, 30, 24), thick)

        # Tool rows
        for row_i, row in enumerate(TOOL_ROWS):
            for col_i, (tool, label) in enumerate(row):
                if tool is None:
                    continue
                bx = 10 + col_i*95
                by = 36 + row_i*22
                active = tool == self.tool
                bg  = ACCENT if active else (200, 202, 206)
                fg  = WHITE  if active else DK_GRAY
                pygame.draw.rect(surface, bg, (bx, by, 88, 18), border_radius=3)
                lbl = font_btn.render(label, True, fg)
                surface.blit(lbl, (bx + 44 - lbl.get_width()//2, by+2))

        # Brush size buttons (S M L)
        size_x_start = SCREEN_W - 190
        for i, lbl_txt in enumerate(SIZE_LABELS):
            bx = size_x_start + i*36
            active = i == self.size_idx
            bg = ACCENT if active else (200, 202, 206)
            fg = WHITE  if active else DK_GRAY
            pygame.draw.rect(surface, bg, (bx, 14, 30, 24), border_radius=4)
            s = font_btn.render(lbl_txt, True, fg)
            surface.blit(s, (bx+15-s.get_width()//2, 19))
        size_hint = font_sm.render(f"Brush ({BRUSH_SIZES[self.size_idx]}px) 1/2/3", True, DK_GRAY)
        surface.blit(size_hint, (size_x_start, 42))

        # Eraser size
        er_x = SCREEN_W - 100
        eraser_hint = font_sm.render(f"Eraser:{self.eraser_r}px", True, DK_GRAY)
        surface.blit(eraser_hint, (er_x, 44))
        pygame.draw.rect(surface, MID_GRY, (er_x, 46, 18, 18), border_radius=3)
        surface.blit(font_btn.render("−", True, BLACK), (er_x+3, 47))
        pygame.draw.rect(surface, MID_GRY, (er_x+24, 46, 18, 18), border_radius=3)
        surface.blit(font_btn.render("+", True, BLACK), (er_x+28, 47))

        # Active colour swatch
        pygame.draw.rect(surface, self.color, (SCREEN_W-52, 44, 22, 22))
        pygame.draw.rect(surface, BLACK,      (SCREEN_W-52, 44, 22, 22), 2)

        # Clear button
        pygame.draw.rect(surface, (200, 50, 50), (SCREEN_W-52, 8, 42, 28), border_radius=4)
        ct = font_btn.render("Clear", True, WHITE)
        surface.blit(ct, (SCREEN_W-52+21-ct.get_width()//2, 13))

        # Status bar at bottom of toolbar
        status_surf = font_sm.render(self._status, True, DK_GRAY)
        surface.blit(status_surf, (10, TOOLBAR_H - 16))

        # Ctrl+S hint
        hint = font_sm.render("Ctrl+S = Save PNG", True, MID_GRY)
        surface.blit(hint, (SCREEN_W//2 - hint.get_width()//2, TOOLBAR_H - 16))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = PaintApp()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            app.handle(event)
        screen.fill(WHITE)
        app.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()