#!/usr/bin/env python3
"""Generate App Store promotional screenshots for YouTube Shorts Blocker."""

from PIL import Image, ImageDraw, ImageFont

W, H = 2880, 1800

# Colors
BG = "#0d0d0d"
CARD = "#1a1a1a"
BORDER = "#2a2a2a"
RED = "#E53935"
WHITE = "#ffffff"
MUTED = "#888888"
MUTED_DIM = "#555555"
YT_RED = "#FF0000"
DARK_RED = "#3a0a0a"
GREEN = "#4CAF50"

FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    if r < 1:
        draw.rectangle(xy, fill=fill, outline=outline, width=width)
        return
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.arc([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


def text_center(draw, text, y, fnt, fill=WHITE):
    """Draw horizontally centered text."""
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=fnt, fill=fill)


def text_center_in(draw, text, x, w, y, fnt, fill=WHITE):
    """Draw text centered within a given horizontal region."""
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text((x + (w - tw) // 2, y), text, font=fnt, fill=fill)


def draw_video_thumb(draw, x, y, w, h, color="#333333"):
    """Draw a simplified video thumbnail card."""
    rounded_rect(draw, (x, y, x + w, y + int(h * 0.58)), 10, fill=color)
    # Play triangle
    cx, cy = x + w // 2, y + int(h * 0.29)
    sz = 16
    draw.polygon([(cx - sz, cy - sz), (cx - sz, cy + sz), (cx + sz, cy)], fill="#ffffff50")
    # Title lines
    ty = y + int(h * 0.65)
    draw.rectangle([x + 4, ty, x + w - 20, ty + 10], fill="#444444")
    draw.rectangle([x + 4, ty + 20, x + int(w * 0.55), ty + 30], fill="#333333")


def draw_shorts_card(draw, x, y, w, h):
    """Draw a Shorts-style vertical card (red tinted)."""
    rounded_rect(draw, (x, y, x + w, y + h), 10, fill=DARK_RED, outline=YT_RED, width=2)
    cx, cy = x + w // 2, y + h // 2 - 10
    draw.polygon([(cx - 12, cy - 16), (cx - 12, cy + 16), (cx + 14, cy)], fill=YT_RED)
    f = font(20)
    bbox = draw.textbbox((0, 0), "Short", font=f)
    tw = bbox[2] - bbox[0]
    draw.text((x + (w - tw) // 2, y + h - 40), "Short", font=f, fill=YT_RED)


# =============================================================================
# Screenshot 1: Before & After Homepage
# =============================================================================

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Title
text_center(d, "Clean YouTube Homepage", 80, font(80), WHITE)
text_center(d, "Shorts shelves removed automatically", 180, font(38), MUTED)

# Two browser window panels side by side
panel_gap = 80
panel_w = (W - panel_gap - 200) // 2  # ~1300 each
panel_h = 1200
left_x = 100
right_x = left_x + panel_w + panel_gap

panel_top = 300

# -- Draw browser window frames --
for px, label, label_color in [(left_x, "BEFORE", RED), (right_x, "AFTER", GREEN)]:
    # Browser frame
    rounded_rect(d, (px, panel_top, px + panel_w, panel_top + panel_h), 16, fill=CARD, outline=BORDER, width=2)
    # Title bar
    d.rectangle([px + 1, panel_top + 1, px + panel_w - 1, panel_top + 44], fill="#222222")
    # Traffic lights
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        d.ellipse([px + 18 + i * 28, panel_top + 14, px + 32 + i * 28, panel_top + 28], fill=c)
    # Address bar
    ab_x = px + 110
    ab_w = panel_w - 160
    rounded_rect(d, (ab_x, panel_top + 8, ab_x + ab_w, panel_top + 36), 8, fill="#111111")
    d.text((ab_x + 12, panel_top + 10), "youtube.com", font=font(18), fill=MUTED_DIM)

    # Label badge above the window
    bf = font(36)
    bbox = d.textbbox((0, 0), label, font=bf)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    lx = px + (panel_w - tw) // 2
    pill_pad_x = 28
    pill_pad_y = 12
    pill_top = panel_top - th - pill_pad_y * 2 - 16
    pill_bot = panel_top - 16
    rounded_rect(d, (lx - pill_pad_x, pill_top, lx + tw + pill_pad_x, pill_bot), 14,
                 fill=label_color, outline=None, width=0)
    d.text((lx, pill_top + pill_pad_y - 2), label, font=bf, fill=WHITE)

# -- Left panel (Before) content --
content_x = left_x + 20
content_y = panel_top + 56
cw = panel_w - 40

# Sidebar
sidebar_w = 140
for i in range(8):
    sy = content_y + 10 + i * 50
    d.rectangle([content_x + 8, sy, content_x + 28, sy + 20], fill="#444444")
    d.rectangle([content_x + 36, sy, content_x + sidebar_w - 10, sy + 12], fill="#333333")

# Video grid area
vx = content_x + sidebar_w + 16
vw = cw - sidebar_w - 16
thumb_w = (vw - 30) // 3
thumb_h = 110

# Row 1: regular videos
for i in range(3):
    tx = vx + i * (thumb_w + 15)
    draw_video_thumb(d, tx, content_y + 10, thumb_w, thumb_h, "#2a2a2a")

# Shorts shelf row (highlighted)
shorts_y = content_y + thumb_h + 30
d.text((vx, shorts_y), "Shorts", font=font(24), fill=YT_RED)
shelf_top = shorts_y + 36
shelf_h = 200
# Red glow border around shelf
rounded_rect(d, (vx - 6, shelf_top - 4, vx + vw + 6, shelf_top + shelf_h + 4), 14,
             fill=None, outline=YT_RED, width=3)
# Shorts cards
card_count = 5
card_gap = 10
card_w = (vw - card_gap * (card_count - 1)) // card_count
for i in range(card_count):
    cx = vx + i * (card_w + card_gap)
    draw_shorts_card(d, cx, shelf_top + 6, card_w, shelf_h - 12)

# Big red X over the shelf
d.line([(vx - 6, shelf_top - 4), (vx + vw + 6, shelf_top + shelf_h + 4)], fill=RED, width=6)
d.line([(vx + vw + 6, shelf_top - 4), (vx - 6, shelf_top + shelf_h + 4)], fill=RED, width=6)

# Row 3 & 4: more videos below
for row in range(3):
    ry = shelf_top + shelf_h + 24 + row * (thumb_h + 16)
    for i in range(3):
        tx = vx + i * (thumb_w + 15)
        draw_video_thumb(d, tx, ry, thumb_w, thumb_h, "#2a2a2a")

# -- Right panel (After) content --
content_x = right_x + 20
cw = panel_w - 40

sidebar_w = 140
for i in range(8):
    sy = content_y + 10 + i * 50
    d.rectangle([content_x + 8, sy, content_x + 28, sy + 20], fill="#444444")
    d.rectangle([content_x + 36, sy, content_x + sidebar_w - 10, sy + 12], fill="#333333")

vx = content_x + sidebar_w + 16
vw = cw - sidebar_w - 16
thumb_w = (vw - 30) // 3

# All clean video rows - no Shorts!
for row in range(7):
    ry = content_y + 10 + row * (thumb_h + 16)
    for i in range(3):
        tx = vx + i * (thumb_w + 15)
        draw_video_thumb(d, tx, ry, thumb_w, thumb_h, "#2a2a2a")

# Bottom tagline
text_center(d, "YouTube Shorts Blocker  --  Safari Extension", H - 60, font(28), MUTED)

img.save("/Users/cristian/Development/Prodius/fun/No YouTube Shorts/screenshots/screenshot-1.png")
print("Screenshot 1 saved.")


# =============================================================================
# Screenshot 2: URL Redirect
# =============================================================================

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

text_center(d, "Shorts Links? No Problem.", 140, font(84), WHITE)
text_center(d, "Automatically redirected to the standard player", 250, font(40), MUTED)

# Central card
card_w = 1800
card_h = 900
card_x = (W - card_w) // 2
card_y = 380
rounded_rect(d, (card_x, card_y, card_x + card_w, card_y + card_h), 28, fill=CARD, outline=BORDER, width=2)

# -- Top section: Shorts URL (crossed out) --
section_y = card_y + 60

# Label
d.text((card_x + 80, section_y), "Shorts URL", font=font(28), fill=RED)

# URL bar
bar_x = card_x + 80
bar_w = card_w - 160
bar_h = 70
bar_y = section_y + 50
rounded_rect(d, (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), 14, fill="#111111", outline=RED, width=2)

# Lock icon + URL text
url_text = "youtube.com/shorts/dQw4w9WgXcQ"
uf = font(34)
url_bbox = d.textbbox((0, 0), url_text, font=uf)
url_tw = url_bbox[2] - url_bbox[0]
url_x = bar_x + (bar_w - url_tw) // 2
url_y = bar_y + (bar_h - 34) // 2
d.text((url_x, url_y), url_text, font=uf, fill="#cc5555")
# Strikethrough
strike_y = url_y + 20
d.line([(url_x - 8, strike_y), (url_x + url_tw + 8, strike_y)], fill=RED, width=4)

# -- Arrow down --
arrow_cx = W // 2
arrow_top = bar_y + bar_h + 50
arrow_bot = arrow_top + 120
# Shaft
d.rectangle([arrow_cx - 4, arrow_top, arrow_cx + 4, arrow_bot - 20], fill=GREEN)
# Arrowhead
d.polygon([
    (arrow_cx - 30, arrow_bot - 30),
    (arrow_cx + 30, arrow_bot - 30),
    (arrow_cx, arrow_bot + 10)
], fill=GREEN)

# -- Bottom section: Watch URL --
section2_y = arrow_bot + 30
d.text((card_x + 80, section2_y), "Standard Player", font=font(28), fill=GREEN)

bar2_y = section2_y + 50
rounded_rect(d, (bar_x, bar2_y, bar_x + bar_w, bar2_y + bar_h), 14, fill="#111111", outline=GREEN, width=2)

url2_text = "youtube.com/watch?v=dQw4w9WgXcQ"
url2_bbox = d.textbbox((0, 0), url2_text, font=uf)
url2_tw = url2_bbox[2] - url2_bbox[0]
url2_x = bar_x + (bar_w - url2_tw) // 2
url2_y = bar2_y + (bar_h - 34) // 2
d.text((url2_x, url2_y), url2_text, font=uf, fill=GREEN)

# Checkmark after URL
d.text((url2_x + url2_tw + 20, url2_y - 2), "✓", font=font(34), fill=GREEN)

# -- Video player mockup --
player_x = card_x + 140
player_w = card_w - 280
player_y = bar2_y + bar_h + 40
player_h = card_y + card_h - player_y - 40
rounded_rect(d, (player_x, player_y, player_x + player_w, player_y + player_h), 12, fill="#222222")

# Play button
pcx = player_x + player_w // 2
pcy = player_y + player_h // 2
psz = 34
d.polygon([(pcx - psz, pcy - int(psz * 1.2)), (pcx - psz, pcy + int(psz * 1.2)), (pcx + int(psz * 1.1), pcy)], fill="#ffffff80")

# Progress bar
prog_y = player_y + player_h - 16
d.rectangle([player_x + 16, prog_y, player_x + player_w - 16, prog_y + 6], fill="#444444")
d.rectangle([player_x + 16, prog_y, player_x + int(player_w * 0.3), prog_y + 6], fill=RED)

# "Horizontal player" label
text_center(d, "Full horizontal player  --  no vertical Shorts view", card_y + card_h + 30, font(26), MUTED_DIM)

# Bottom tagline
text_center(d, "YouTube Shorts Blocker  --  Safari Extension", H - 60, font(28), MUTED)

img.save("/Users/cristian/Development/Prodius/fun/No YouTube Shorts/screenshots/screenshot-2.png")
print("Screenshot 2 saved.")


# =============================================================================
# Screenshot 3: One-Click Control
# =============================================================================

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

text_center(d, "Toggle Anytime", 100, font(84), WHITE)
text_center(d, "One click to pause or resume blocking", 210, font(40), MUTED)

# Layout: two popup mockups side by side, each with a Safari toolbar above
# Active (ON) on the left-center, Paused (OFF) on the right-center

popup_w = 560
popup_h = 680
gap = 200
total = popup_w * 2 + gap
start_x = (W - total) // 2

# ── Active popup (left) ──
on_x = start_x
on_top = 360

# Safari toolbar above
tb_w = popup_w + 60
tb_h = 50
tb_x = on_x - 30
tb_y = on_top
rounded_rect(d, (tb_x, tb_y, tb_x + tb_w, tb_y + tb_h), 10, fill="#1c1c1c", outline=BORDER, width=2)
for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
    d.ellipse([tb_x + 16 + i * 24, tb_y + 15, tb_x + 30 + i * 24, tb_y + 29], fill=c)
# Address bar
ab_x2 = tb_x + 100
ab_w2 = tb_w - 200
rounded_rect(d, (ab_x2, tb_y + 10, ab_x2 + ab_w2, tb_y + tb_h - 10), 6, fill="#111111")
d.text((ab_x2 + 12, tb_y + 14), "youtube.com", font=font(18), fill=MUTED_DIM)
# Extension icon
ext_x = tb_x + tb_w - 60
rounded_rect(d, (ext_x, tb_y + 10, ext_x + 30, tb_y + 40), 6, fill=RED)
d.text((ext_x + 6, tb_y + 12), "S", font=font(18), fill=WHITE)

# Triangle connector
tri_cx = on_x + popup_w // 2
tri_y = tb_y + tb_h
d.polygon([(tri_cx - 14, tri_y + 16), (tri_cx + 14, tri_y + 16), (tri_cx, tri_y + 2)], fill=CARD)

# Popup card
popup_y = tri_y + 16
rounded_rect(d, (on_x, popup_y, on_x + popup_w, popup_y + popup_h), 24,
             fill=CARD, outline=GREEN, width=2)

# "Active" label above
text_center_in(d, "Active", on_x, popup_w, on_top - 50, font(30), GREEN)

# App icon
ai_sz = 80
ai_x = on_x + (popup_w - ai_sz) // 2
ai_y = popup_y + 40
d.ellipse([ai_x, ai_y, ai_x + ai_sz, ai_y + ai_sz], fill=RED)
d.text((ai_x + 22, ai_y + 16), "S", font=font(44), fill=WHITE)
d.line([(ai_x + 14, ai_y + ai_sz - 14), (ai_x + ai_sz - 14, ai_y + 14)], fill=WHITE, width=4)

# Title
text_center_in(d, "YouTube Shorts Blocker", on_x, popup_w, ai_y + ai_sz + 24, font(32), WHITE)

# Status: Blocking Shorts
status_y = ai_y + ai_sz + 76
sf = font(26)
status_text = "Blocking Shorts"
sbbox = d.textbbox((0, 0), status_text, font=sf)
stw = sbbox[2] - sbbox[0]
dot_x = on_x + (popup_w - stw - 24) // 2
d.ellipse([dot_x, status_y + 6, dot_x + 16, status_y + 22], fill=GREEN)
d.text((dot_x + 24, status_y), status_text, font=sf, fill=GREEN)

# Toggle (ON)
toggle_w = 100
toggle_h = 52
toggle_x = on_x + (popup_w - toggle_w) // 2
toggle_y = status_y + 56
rounded_rect(d, (toggle_x, toggle_y, toggle_x + toggle_w, toggle_y + toggle_h), toggle_h // 2, fill=GREEN)
knob_r = 21
knob_cx = toggle_x + toggle_w - knob_r - 6
knob_cy = toggle_y + toggle_h // 2
d.ellipse([knob_cx - knob_r, knob_cy - knob_r, knob_cx + knob_r, knob_cy + knob_r], fill=WHITE)

# Divider
div_y = toggle_y + toggle_h + 36
d.line([(on_x + 40, div_y), (on_x + popup_w - 40, div_y)], fill=BORDER, width=1)

# Feature list
features = [
    ("Hide Shorts Shelves", True),
    ("Redirect Shorts URLs", True),
    ("Hide Shorts Tab", True),
]
fy = div_y + 28
feat_f = font(26)
for label, enabled in features:
    fx = on_x + 60
    d.ellipse([fx, fy + 3, fx + 26, fy + 29], fill=GREEN)
    d.text((fx + 5, fy + 3), "✓", font=font(18), fill=WHITE)
    d.text((fx + 40, fy), label, font=feat_f, fill=WHITE)
    fy += 52

# ── Paused popup (right) ──
off_x = start_x + popup_w + gap
off_popup_h = popup_h

# Safari toolbar
tb2_x = off_x - 30
tb2_w = popup_w + 60
rounded_rect(d, (tb2_x, tb_y, tb2_x + tb2_w, tb_y + tb_h), 10, fill="#1c1c1c", outline=BORDER, width=2)
for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
    d.ellipse([tb2_x + 16 + i * 24, tb_y + 15, tb2_x + 30 + i * 24, tb_y + 29], fill=c)
ab2_x = tb2_x + 100
ab2_w = tb2_w - 200
rounded_rect(d, (ab2_x, tb_y + 10, ab2_x + ab2_w, tb_y + tb_h - 10), 6, fill="#111111")
d.text((ab2_x + 12, tb_y + 14), "youtube.com", font=font(18), fill=MUTED_DIM)
ext2_x = tb2_x + tb2_w - 60
rounded_rect(d, (ext2_x, tb_y + 10, ext2_x + 30, tb_y + 40), 6, fill=MUTED_DIM)
d.text((ext2_x + 6, tb_y + 12), "S", font=font(18), fill=MUTED)

# "Paused" label above
text_center_in(d, "Paused", off_x, popup_w, on_top - 50, font(30), MUTED)

# Triangle
tri2_cx = off_x + popup_w // 2
d.polygon([(tri2_cx - 14, tri_y + 16), (tri2_cx + 14, tri_y + 16), (tri2_cx, tri_y + 2)], fill="#141414")

# Popup card (dimmer)
rounded_rect(d, (off_x, popup_y, off_x + popup_w, popup_y + off_popup_h), 24,
             fill="#141414", outline="#333333", width=2)

# App icon (greyed out)
ai2_x = off_x + (popup_w - ai_sz) // 2
d.ellipse([ai2_x, ai_y, ai2_x + ai_sz, ai_y + ai_sz], fill=MUTED_DIM)
d.text((ai2_x + 22, ai_y + 16), "S", font=font(44), fill=MUTED)
d.line([(ai2_x + 14, ai_y + ai_sz - 14), (ai2_x + ai_sz - 14, ai_y + 14)], fill=MUTED, width=4)

# Title
text_center_in(d, "YouTube Shorts Blocker", off_x, popup_w, ai_y + ai_sz + 24, font(32), MUTED)

# Status: Shorts Allowed
off_status = "Shorts Allowed"
osbbox = d.textbbox((0, 0), off_status, font=sf)
ostw = osbbox[2] - osbbox[0]
odot_x = off_x + (popup_w - ostw - 24) // 2
d.ellipse([odot_x, status_y + 6, odot_x + 16, status_y + 22], fill=MUTED)
d.text((odot_x + 24, status_y), off_status, font=sf, fill=MUTED)

# Toggle (OFF)
otx = off_x + (popup_w - toggle_w) // 2
rounded_rect(d, (otx, toggle_y, otx + toggle_w, toggle_y + toggle_h), toggle_h // 2, fill="#444444")
oknob_cx = otx + knob_r + 6
oknob_cy = toggle_y + toggle_h // 2
d.ellipse([oknob_cx - knob_r, oknob_cy - knob_r, oknob_cx + knob_r, oknob_cy + knob_r], fill=MUTED)

# Divider
d.line([(off_x + 40, div_y), (off_x + popup_w - 40, div_y)], fill="#333333", width=1)

# Feature list (all dimmed)
fy = div_y + 28
for label, _ in features:
    fx = off_x + 60
    rounded_rect(d, (fx, fy + 3, fx + 26, fy + 29), 6, fill=None, outline=MUTED_DIM, width=2)
    d.text((fx + 40, fy), label, font=feat_f, fill=MUTED_DIM)
    fy += 52

# ── Arrows between popups ──
arr_y = popup_y + popup_h // 2 - 10
arr_lx = on_x + popup_w + 20
arr_rx = off_x - 20

# Right arrow
d.line([(arr_lx, arr_y), (arr_rx, arr_y)], fill=MUTED, width=3)
d.polygon([(arr_rx - 14, arr_y - 10), (arr_rx - 14, arr_y + 10), (arr_rx + 2, arr_y)], fill=MUTED)
# Left arrow below
d.line([(arr_rx, arr_y + 30), (arr_lx, arr_y + 30)], fill=MUTED, width=3)
d.polygon([(arr_lx + 14, arr_y + 20), (arr_lx + 14, arr_y + 40), (arr_lx - 2, arr_y + 30)], fill=MUTED)

# "1 click" label between arrows
text_center(d, "1 click", arr_y - 36, font(22), MUTED)

# Bottom tagline
text_center(d, "YouTube Shorts Blocker  --  Safari Extension", H - 60, font(28), MUTED)

img.save("/Users/cristian/Development/Prodius/fun/No YouTube Shorts/screenshots/screenshot-3.png")
print("Screenshot 3 saved.")

print("\nAll done!")
