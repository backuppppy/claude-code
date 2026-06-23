#!/usr/bin/env python3
"""
Font Maker - Convert image/PDF drawings to TTF font file
Usage: python font_maker.py [image_or_pdf]
"""

import sys
import os
import math
import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from collections import deque

try:
    from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageDraw
except ImportError:
    print("Missing: pip install Pillow")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("Missing: pip install numpy")
    sys.exit(1)

try:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
except ImportError:
    try:
        from fonttools.fontBuilder import FontBuilder
        from fonttools.pens.ttGlyphPen import TTGlyphPen
    except ImportError:
        print("Missing: pip install fonttools")
        sys.exit(1)

try:
    import fitz
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# ─── Constants ───────────────────────────────────────────────────────────────

UPM = 1000          # Units per em
CANVAS_SIZE = 400   # Drawing canvas size in pixels

CHARSET = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
               '0123456789.,!?;:\'"()-/@ ')

_PUNCT_NAMES = {
    ' ': 'space', '.': 'period', ',': 'comma', '!': 'exclam',
    '?': 'question', ';': 'semicolon', ':': 'colon', "'": 'quotesingle',
    '"': 'quotedbl', '(': 'parenleft', ')': 'parenright', '-': 'hyphen',
    '/': 'slash', '@': 'at',
}

def glyph_name(ch):
    if ch in _PUNCT_NAMES:
        return _PUNCT_NAMES[ch]
    if ch.isalpha():
        return ch if ch.isupper() else ch + '.sc'
    if ch.isdigit():
        return f'uni{ord(ch):04X}'
    return f'uni{ord(ch):04X}'


# ─── Vectorizer ──────────────────────────────────────────────────────────────

def glyph_image_to_contours(pil_img, upm=UPM):
    """
    Convert a PIL grayscale glyph image to font-unit contours.
    Uses horizontal run-length encoding → rectangle outlines.
    Returns (contours, lsb, advance_width).
    """
    work_size = 120
    img = pil_img.convert('L').resize((work_size, work_size), Image.LANCZOS)
    arr = np.array(img)
    binary = arr < 140  # True = ink

    if not binary.any():
        return [], 0, int(upm * 0.5)

    # Bounding box
    rows = np.any(binary, axis=1)
    cols = np.any(binary, axis=0)
    rmin, rmax = int(np.where(rows)[0][0]), int(np.where(rows)[0][-1])
    cmin, cmax = int(np.where(cols)[0][0]), int(np.where(cols)[0][-1])

    gw = cmax - cmin + 1
    gh = rmax - rmin + 1

    target_h = int(upm * 0.68)
    scale = target_h / max(gh, 1)

    baseline   = int(upm * 0.18)
    lbearing   = int(upm * 0.06)

    def to_font(px, py):
        fx = lbearing + int((px - cmin) * scale)
        fy = baseline + target_h - int((py - rmin) * scale)
        return fx, fy

    contours = []

    for y in range(rmin, rmax + 1):
        in_run = False
        rx = None
        for x in range(cmin, cmax + 2):
            ink = (x <= cmax) and binary[y, x]
            if ink and not in_run:
                rx = x
                in_run = True
            elif not ink and in_run:
                x1, y_top = to_font(rx, y)
                x2, y_bot = to_font(x,  y + 1)
                if x2 > x1 and y_top > y_bot:
                    # Clockwise in font coords = filled
                    contours.append([(x1, y_top), (x2, y_top), (x2, y_bot), (x1, y_bot)])
                in_run = False

    advance = lbearing + int(gw * scale) + lbearing
    return contours, 0, max(advance, 80)


# ─── Font Builder ────────────────────────────────────────────────────────────

def build_ttf(glyph_imgs, font_name, save_path):
    """
    glyph_imgs: dict  char → PIL Image
    Saves a .ttf font file at save_path.
    """
    # Process all glyphs
    processed = {}  # glyph_name → (contours, lsb, advance)
    char_map   = {}  # codepoint → glyph_name

    for ch, img in glyph_imgs.items():
        name = glyph_name(ch)
        contours, lsb, adv = glyph_image_to_contours(img)
        processed[name] = (contours, lsb, adv)
        char_map[ord(ch)] = name

    glyph_order = ['.notdef'] + list(dict.fromkeys(
        glyph_name(c) for c in CHARSET
    ))
    # Add any extra glyphs not in standard charset
    for name in processed:
        if name not in glyph_order:
            glyph_order.append(name)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)

    glyphs  = {}
    metrics = {}

    # .notdef: simple box outline
    pen = TTGlyphPen(None)
    for pts in [
        [(60, 700), (440, 700), (440,   0), (60,   0)],
        [(110, 650), (110,  50), (390,  50), (390, 650)],
    ]:
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    glyphs ['.notdef'] = pen.glyph()
    metrics['.notdef'] = (500, 0)

    for name in glyph_order[1:]:
        contours, lsb, adv = processed.get(name, ([], 0, int(UPM * 0.5)))
        pen = TTGlyphPen(None)
        drawn = 0
        for c in contours:
            if len(c) < 3:
                continue
            try:
                pen.moveTo(c[0])
                for pt in c[1:]:
                    pen.lineTo(pt)
                pen.closePath()
                drawn += 1
            except Exception:
                pass

        if drawn == 0:
            pen2 = TTGlyphPen(None)
            glyphs[name] = pen2.glyph()
        else:
            glyphs[name] = pen.glyph()

        metrics[name] = (max(adv, 50), lsb)

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)

    asc  =  int(UPM * 0.80)
    desc = -int(UPM * 0.20)

    fb.setupHorizontalHeader(ascent=asc, descent=desc)
    fb.setupNameTable({'familyName': font_name, 'styleName': 'Regular'})
    fb.setupOS2(
        sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
        usWinAscent=asc, usWinDescent=abs(desc),
        sxHeight=int(UPM * 0.52), sCapHeight=int(UPM * 0.72),
    )
    fb.setupPost()

    fb.font.save(save_path)
    return save_path


# ─── Segmentation Dialog ─────────────────────────────────────────────────────

class SegmentDialog:
    """
    Shows a loaded image and lets the user mark character regions,
    either manually or via auto-grid.
    """
    def __init__(self, parent, pil_img, callback):
        self.orig_img = pil_img.convert('L')
        self.callback = callback   # called with dict {char: PIL Image}
        self.selections = {}       # char → (x1,y1,x2,y2) in original coords
        self.char_idx = 0
        self.scale = 1.0

        self.win = tk.Toplevel(parent)
        self.win.title("Segment Characters from Image")
        self.win.geometry("960x680")
        self.win.grab_set()

        self._build_ui()
        self._show_image()

    def _build_ui(self):
        top = ttk.Frame(self.win)
        top.pack(fill='x', padx=8, pady=4)

        self.info_lbl = ttk.Label(top, text=f"Mark: {CHARSET[0]}",
                                  font=('Arial', 13, 'bold'))
        self.info_lbl.pack(side='left')

        ttk.Button(top, text="Skip char",      command=self._skip).pack(side='left', padx=4)
        ttk.Button(top, text="Auto Grid",      command=self._auto_grid).pack(side='left', padx=4)
        ttk.Button(top, text="Clear All",      command=self._clear_all).pack(side='left', padx=4)
        ttk.Button(top, text="Done →",         command=self._finish).pack(side='right', padx=4)

        cf = ttk.Frame(self.win)
        cf.pack(fill='both', expand=True, padx=8, pady=4)

        self.cv = tk.Canvas(cf, bg='#888', cursor='crosshair')
        vsb = ttk.Scrollbar(cf, orient='vertical',   command=self.cv.yview)
        hsb = ttk.Scrollbar(cf, orient='horizontal', command=self.cv.xview)
        self.cv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.cv.pack(fill='both', expand=True)

        self.cv.bind('<Button-1>',        self._sel_start)
        self.cv.bind('<B1-Motion>',       self._sel_drag)
        self.cv.bind('<ButtonRelease-1>', self._sel_end)

        self._sel_rect  = None
        self._sel_start_xy = None
        self._drawn = {}   # char → canvas rect id

    def _show_image(self):
        MAX = 820
        img = self.orig_img.copy()
        if img.width > MAX or img.height > MAX:
            r = min(MAX / img.width, MAX / img.height)
            img = img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)
            self.scale = r
        self._photo = ImageTk.PhotoImage(img)
        self.cv.create_image(0, 0, anchor='nw', image=self._photo, tags='bg')
        self.cv.configure(scrollregion=(0, 0, img.width, img.height))

    def _skip(self):
        self.char_idx = min(self.char_idx + 1, len(CHARSET) - 1)
        self._update_info()

    def _update_info(self):
        ch = CHARSET[self.char_idx]
        self.info_lbl.config(text=f"Mark: {'SPACE' if ch == ' ' else repr(ch)}")

    def _sel_start(self, ev):
        self._sel_start_xy = (self.cv.canvasx(ev.x), self.cv.canvasy(ev.y))

    def _sel_drag(self, ev):
        if not self._sel_start_xy:
            return
        x, y = self.cv.canvasx(ev.x), self.cv.canvasy(ev.y)
        if self._sel_rect:
            self.cv.delete(self._sel_rect)
        self._sel_rect = self.cv.create_rectangle(
            *self._sel_start_xy, x, y, outline='red', width=2)

    def _sel_end(self, ev):
        if not self._sel_start_xy:
            return
        x2, y2 = self.cv.canvasx(ev.x), self.cv.canvasy(ev.y)
        x1, y1 = self._sel_start_xy
        self._sel_start_xy = None
        if self._sel_rect:
            self.cv.delete(self._sel_rect)
            self._sel_rect = None

        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        if (x2 - x1) < 6 or (y2 - y1) < 6:
            return

        ch = CHARSET[self.char_idx]
        ox1, oy1 = int(x1 / self.scale), int(y1 / self.scale)
        ox2, oy2 = int(x2 / self.scale), int(y2 / self.scale)
        self.selections[ch] = (ox1, oy1, ox2, oy2)

        if ch in self._drawn:
            self.cv.delete(self._drawn[ch])
        r = self.cv.create_rectangle(x1, y1, x2, y2, outline='#00cc44', width=2)
        self.cv.create_text(x1 + 3, y1 + 2, text=('·' if ch == ' ' else ch),
                            fill='#00cc44', anchor='nw', font=('Arial', 10, 'bold'))
        self._drawn[ch] = r

        self._skip()

    def _auto_grid(self):
        cols = simpledialog.askinteger("Columns", "How many columns?",
                                       initialvalue=13, minvalue=1, maxvalue=30,
                                       parent=self.win)
        rows = simpledialog.askinteger("Rows", "How many rows?",
                                       initialvalue=7, minvalue=1, maxvalue=20,
                                       parent=self.win)
        if not cols or not rows:
            return

        iw, ih = self.orig_img.width, self.orig_img.height
        cw, ch_px = iw // cols, ih // rows

        for i, ch in enumerate(CHARSET[: rows * cols]):
            r, c = divmod(i, cols)
            x1, y1 = c * cw,      r * ch_px
            x2, y2 = x1 + cw,     y1 + ch_px
            self.selections[ch] = (x1, y1, x2, y2)

            sx1, sy1 = x1 * self.scale, y1 * self.scale
            sx2, sy2 = x2 * self.scale, y2 * self.scale
            if ch in self._drawn:
                self.cv.delete(self._drawn[ch])
            rid = self.cv.create_rectangle(sx1, sy1, sx2, sy2,
                                           outline='#2196F3', width=1)
            self.cv.create_text(sx1 + 2, sy1 + 1,
                                text=('·' if ch == ' ' else ch),
                                fill='#2196F3', anchor='nw', font=('Arial', 8))
            self._drawn[ch] = rid

        messagebox.showinfo("Auto Grid",
                            f"Mapped {min(len(CHARSET), rows*cols)} characters.",
                            parent=self.win)

    def _clear_all(self):
        self.selections.clear()
        for rid in self._drawn.values():
            self.cv.delete(rid)
        self._drawn.clear()
        self.char_idx = 0
        self._update_info()

    def _finish(self):
        result = {}
        for ch, (x1, y1, x2, y2) in self.selections.items():
            try:
                region = self.orig_img.crop((x1, y1, x2, y2))
                result[ch] = region
            except Exception:
                pass
        self.win.destroy()
        if result:
            self.callback(result)


# ─── Main Application ────────────────────────────────────────────────────────

class FontMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Maker  ✏ → TTF")
        self.root.geometry("1120x720")
        self.root.minsize(900, 600)

        self.glyphs       = {}   # char → PIL Image (grayscale, 400×400)
        self.current_char = 'A'
        self.drawing      = False
        self._last_xy     = None

        self._build_ui()
        self._refresh_grid()
        self._load_current()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Toolbar ──
        bar = ttk.Frame(self.root, padding=4)
        bar.pack(fill='x')

        ttk.Button(bar, text="📂 Load Image", command=self._load_image).pack(side='left', padx=2)
        ttk.Button(bar, text="📄 Load PDF",   command=self._load_pdf,
                   state='normal' if HAS_PDF else 'disabled').pack(side='left', padx=2)
        ttk.Separator(bar, orient='vertical').pack(side='left', padx=6, fill='y')
        ttk.Button(bar, text="🗑 Clear Glyph",command=self._clear_glyph).pack(side='left', padx=2)
        ttk.Button(bar, text="💾 Export TTF", command=self._export).pack(side='left', padx=2)
        ttk.Separator(bar, orient='vertical').pack(side='left', padx=6, fill='y')
        ttk.Label(bar, text="Font name:").pack(side='left')
        self._font_name = tk.StringVar(value="HandwrittenFont")
        ttk.Entry(bar, textvariable=self._font_name, width=18).pack(side='left', padx=2)

        self._status = tk.StringVar(value="Draw each character on the canvas →")
        ttk.Label(bar, textvariable=self._status, foreground='#1565C0').pack(side='right', padx=4)

        # ── Main pane ──
        pane = ttk.PanedWindow(self.root, orient='horizontal')
        pane.pack(fill='both', expand=True, padx=6, pady=4)

        # Left: character palette
        left = ttk.LabelFrame(pane, text="Character Palette  (blue = defined)")
        pane.add(left, weight=0)

        self._grid_cv = tk.Canvas(left, width=310, bg='white')
        self._grid_cv.pack(fill='both', expand=True)
        self._grid_cv.bind('<Button-1>', self._on_grid_click)

        # Right: editor
        right = ttk.Frame(pane)
        pane.add(right, weight=1)

        # Current char + nav
        nav = ttk.Frame(right)
        nav.pack(fill='x', pady=(0, 4))
        ttk.Button(nav, text="◀", width=3, command=self._prev_char).pack(side='left')
        self._char_lbl = ttk.Label(nav, text="A", font=('Arial', 28, 'bold'), width=4)
        self._char_lbl.pack(side='left', padx=4)
        ttk.Button(nav, text="▶", width=3, command=self._next_char).pack(side='left')

        # Brush slider
        bframe = ttk.Frame(nav)
        bframe.pack(side='right', padx=8)
        ttk.Label(bframe, text="Brush:").pack(side='left')
        self._brush = tk.IntVar(value=10)
        ttk.Scale(bframe, from_=2, to=40, variable=self._brush,
                  orient='horizontal', length=130).pack(side='left')

        # Drawing canvas
        self._cv = tk.Canvas(right, width=CANVAS_SIZE, height=CANVAS_SIZE,
                              bg='white', cursor='crosshair',
                              highlightthickness=1, highlightbackground='#999')
        self._cv.pack()

        self._cv.bind('<Button-1>',        self._draw_start)
        self._cv.bind('<B1-Motion>',       self._draw_move)
        self._cv.bind('<ButtonRelease-1>', self._draw_end)

        # Glyph PIL buffer
        self._buf = Image.new('L', (CANVAS_SIZE, CANVAS_SIZE), 255)
        self._buf_draw = ImageDraw.Draw(self._buf)

        self._draw_guides()

        # Hint
        ttk.Label(right,
                  text="Blue line=baseline  Red=cap  Green=x-height  |  Draw, then click next char or Export",
                  foreground='gray', font=('Arial', 9)).pack(pady=2)

    def _draw_guides(self):
        w = h = CANVAS_SIZE
        baseline = int(h * 0.76)
        capline  = int(h * 0.14)
        xheight  = int(h * 0.46)
        for y, color, tag in [(baseline, '#1976D2', 'guide'),
                               (capline,  '#C62828', 'guide'),
                               (xheight,  '#2E7D32', 'guide')]:
            self._cv.create_line(0, y, w, y, fill=color, dash=(5, 4), tags=tag)
        self._baseline_y = baseline

    # ── Grid ─────────────────────────────────────────────────────────────────

    def _refresh_grid(self):
        cv = self._grid_cv
        cv.delete('all')
        cols = 8
        cw = ch = 37
        pad = 3
        for i, c in enumerate(CHARSET):
            col = i % cols
            row = i // cols
            x, y = col * cw + pad, row * ch + pad
            active = (c == self.current_char)
            defined = (c in self.glyphs)
            bg = '#1565C0' if active else ('#42A5F5' if defined else '#F5F5F5')
            fg = 'white' if (active or defined) else '#333'
            cv.create_rectangle(x, y, x + cw - 2, y + ch - 2,
                                 fill=bg, outline='#ccc', tags=f'cell{i}')
            cv.create_text(x + cw // 2, y + ch // 2,
                            text=('·' if c == ' ' else c),
                            fill=fg, font=('Arial', 11, 'bold'), tags=f'cell{i}')

        total_rows = (len(CHARSET) + cols - 1) // cols
        cv.configure(height=total_rows * ch + pad * 2)

    def _on_grid_click(self, ev):
        cols = 8
        cw = ch = 37
        pad = 3
        col = (ev.x - pad) // cw
        row = (ev.y - pad) // ch
        idx = row * cols + col
        if 0 <= idx < len(CHARSET):
            self._save_current()
            self.current_char = CHARSET[idx]
            self._load_current()
            self._refresh_grid()

    # ── Glyph save/load ───────────────────────────────────────────────────────

    def _save_current(self):
        arr = np.array(self._buf)
        if arr.min() < 200:
            self.glyphs[self.current_char] = self._buf.copy()

    def _load_current(self):
        ch = self.current_char
        self._char_lbl.config(text='SPC' if ch == ' ' else ch)
        self._buf = Image.new('L', (CANVAS_SIZE, CANVAS_SIZE), 255)
        self._buf_draw = ImageDraw.Draw(self._buf)
        self._cv.delete('ink')

        if ch in self.glyphs:
            self._buf = self.glyphs[ch].copy().resize(
                (CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
            self._buf_draw = ImageDraw.Draw(self._buf)
            self._render_buf()

    def _render_buf(self):
        self._cv.delete('ink')
        ph = ImageTk.PhotoImage(self._buf)
        self._cv.create_image(0, 0, anchor='nw', image=ph, tags='ink')
        self._cv._ph = ph
        self._cv.tag_lower('ink')
        self._cv.tag_raise('guide')

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_start(self, ev):
        self.drawing = True
        self._last_xy = (ev.x, ev.y)

    def _draw_move(self, ev):
        if not self.drawing:
            return
        x, y = ev.x, ev.y
        b = self._brush.get()
        r = b // 2
        self._buf_draw.ellipse([x - r, y - r, x + r, y + r], fill=0)
        if self._last_xy:
            self._buf_draw.line([*self._last_xy, x, y], fill=0, width=b)
        self._cv.create_oval(x - r, y - r, x + r, y + r,
                              fill='black', outline='', tags='ink')
        self._last_xy = (x, y)

    def _draw_end(self, ev):
        self.drawing = False
        self._last_xy = None

    def _clear_glyph(self):
        self._buf = Image.new('L', (CANVAS_SIZE, CANVAS_SIZE), 255)
        self._buf_draw = ImageDraw.Draw(self._buf)
        self._cv.delete('ink')
        self.glyphs.pop(self.current_char, None)
        self._refresh_grid()

    def _prev_char(self):
        self._save_current()
        idx = CHARSET.index(self.current_char)
        self.current_char = CHARSET[(idx - 1) % len(CHARSET)]
        self._load_current()
        self._refresh_grid()

    def _next_char(self):
        self._save_current()
        idx = CHARSET.index(self.current_char)
        self.current_char = CHARSET[(idx + 1) % len(CHARSET)]
        self._load_current()
        self._refresh_grid()

    # ── Load Image / PDF ──────────────────────────────────────────────────────

    def _load_image(self):
        path = filedialog.askopenfilename(
            title="Open image with characters",
            filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp *.tiff *.webp'),
                       ('All', '*.*')])
        if not path:
            return
        try:
            img = Image.open(path)
            SegmentDialog(self.root, img, self._apply_segmented)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_pdf(self):
        if not HAS_PDF:
            messagebox.showinfo("Info", "pip install PyMuPDF")
            return
        path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[('PDF', '*.pdf'), ('All', '*.*')])
        if not path:
            return
        try:
            doc = fitz.open(path)
            n = len(doc)
            page_num = simpledialog.askinteger(
                "Page", f"Page number (1–{n}):",
                initialvalue=1, minvalue=1, maxvalue=n, parent=self.root)
            if not page_num:
                return
            pix  = doc[page_num - 1].get_pixmap(dpi=200)
            img  = Image.open(io.BytesIO(pix.tobytes('png')))
            SegmentDialog(self.root, img, self._apply_segmented)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _apply_segmented(self, char_images):
        """Called by SegmentDialog with {char: PIL Image}."""
        count = 0
        for ch, img in char_images.items():
            self.glyphs[ch] = img.convert('L').resize(
                (CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
            count += 1
        self._load_current()
        self._refresh_grid()
        self._status.set(f"Loaded {count} glyphs from image.")

    # ── Export ────────────────────────────────────────────────────────────────

    def _export(self):
        self._save_current()
        if not self.glyphs:
            messagebox.showwarning("No glyphs", "Draw at least one character first.")
            return

        name = self._font_name.get().strip() or "HandwrittenFont"
        path = filedialog.asksaveasfilename(
            title="Save TTF font",
            defaultextension='.ttf',
            filetypes=[('TrueType Font', '*.ttf'), ('All', '*.*')],
            initialfile=f"{name}.ttf")
        if not path:
            return

        self._status.set("Building font…")
        self.root.update_idletasks()

        try:
            build_ttf(self.glyphs, name, path)
            self._status.set(f"Saved → {os.path.basename(path)}")
            messagebox.showinfo("Done",
                f"Font saved!\n{path}\n\n"
                f"Contains {len(self.glyphs)} glyph(s).\n"
                "Install the .ttf file to use it in other apps.")
        except Exception as e:
            self._status.set("Export failed.")
            messagebox.showerror("Export Error", str(e))
            import traceback; traceback.print_exc()


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app  = FontMakerApp(root)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        p = sys.argv[1]
        if p.lower().endswith('.pdf') and HAS_PDF:
            root.after(400, app._load_pdf)
        elif any(p.lower().endswith(e) for e in ('.png','.jpg','.jpeg','.bmp','.tiff')):
            root.after(400, app._load_image)

    root.mainloop()


if __name__ == '__main__':
    main()
