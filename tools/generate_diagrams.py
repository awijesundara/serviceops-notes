"""Renders the manual's architecture and workflow diagrams as branded PNGs.

These are plain box-and-arrow diagrams drawn with Pillow (already a
documentation dependency for screenshot post-processing) rather than a new
diagramming library or a hosted rendering service, matching this project's
existing "no extra dependency for docs tooling" posture. Output lands in
docs/diagrams/ and is embedded into OPERATIONS_MANUAL.md the same way a
screenshot is: a plain ``![alt](diagrams/x.png)`` line that
generate_operations_manual.py already knows how to place and caption.

Run directly (no running application required, unlike capture_screenshots.py):

    python3 tools/generate_diagrams.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "diagrams"

SCALE = 3  # supersample, then the PDF embedder scales down for crisp text
TEAL = (0, 62, 76)
DARK = (0, 47, 58)
AMBER = (249, 170, 60)
INK = (19, 37, 43)
MUTED = (99, 118, 125)
LINE = (216, 225, 228)
PANEL = (240, 245, 245)
WHITE = (255, 255, 255)

FONT_CANDIDATES_BOLD = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
FONT_CANDIDATES_REGULAR = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _font(candidates, size):
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def bold(size):
    return _font(FONT_CANDIDATES_BOLD, size * SCALE)


def regular(size):
    return _font(FONT_CANDIDATES_REGULAR, size * SCALE)


class Diagram:
    """A fixed-size canvas with a handful of primitives sized in logical
    (unscaled) points; every call multiplies by SCALE so the saved PNG is
    supersampled for crisp text once the PDF embedder scales it back down."""

    def __init__(self, width, height, bg=WHITE):
        self.w, self.h = width, height
        self.img = Image.new("RGB", (width * SCALE, height * SCALE), bg)
        self.draw = ImageDraw.Draw(self.img)

    def _s(self, *vals):
        return tuple(v * SCALE for v in vals)

    def box(self, x, y, w, h, label, fill=PANEL, outline=TEAL, text_color=INK,
            font_size=13, sublabel=None, sub_color=MUTED, sub_size=10.5):
        self.draw.rounded_rectangle(self._s(x, y, x + w, y + h), radius=8 * SCALE,
                                     fill=fill, outline=outline, width=2 * SCALE)
        f = bold(font_size)
        lines = label.split("\n")
        line_h = font_size * 1.25
        total_h = line_h * len(lines) + (sub_size * 1.3 if sublabel else 0)
        cy = y + h / 2 - total_h / 2
        for line in lines:
            bbox = self.draw.textbbox((0, 0), line, font=f)
            tw = (bbox[2] - bbox[0]) / SCALE
            self.draw.text(self._s(x + w / 2 - tw / 2, cy), line, font=f, fill=text_color)
            cy += line_h
        if sublabel:
            sf = regular(sub_size)
            for line in sublabel.split("\n"):
                bbox = self.draw.textbbox((0, 0), line, font=sf)
                tw = (bbox[2] - bbox[0]) / SCALE
                self.draw.text(self._s(x + w / 2 - tw / 2, cy + 2), line, font=sf, fill=sub_color)
                cy += sub_size * 1.3

    def text(self, x, y, label, size=11, color=INK, bold_font=False, center=False, max_width=None):
        f = bold(size) if bold_font else regular(size)
        for i, line in enumerate(label.split("\n")):
            lx = x
            if center:
                bbox = self.draw.textbbox((0, 0), line, font=f)
                tw = (bbox[2] - bbox[0]) / SCALE
                lx = x - tw / 2
            self.draw.text(self._s(lx, y + i * size * 1.3), line, font=f, fill=color)

    def arrow(self, x1, y1, x2, y2, color=MUTED, width=1.6, dashed=False, label=None):
        if dashed:
            self._dashed_line(x1, y1, x2, y2, color, width)
        else:
            self.draw.line(self._s(x1, y1, x2, y2), fill=color, width=int(width * SCALE))
        # arrowhead
        import math
        ang = math.atan2((y2 - y1), (x2 - x1))
        size = 6
        for da in (0.5, -0.5):
            hx = x2 - size * math.cos(ang - da)
            hy = y2 - size * math.sin(ang - da)
            self.draw.line(self._s(x2, y2, hx, hy), fill=color, width=int(width * SCALE))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            f = regular(9.5)
            bbox = self.draw.textbbox((0, 0), label, font=f)
            tw = (bbox[2] - bbox[0]) / SCALE
            th = (bbox[3] - bbox[1]) / SCALE
            pad = 3
            self.draw.rectangle(self._s(mx - tw / 2 - pad, my - th / 2 - pad,
                                         mx + tw / 2 + pad, my + th / 2 + pad), fill=WHITE)
            self.draw.text(self._s(mx - tw / 2, my - th / 2), label, font=f, fill=MUTED)

    def _dashed_line(self, x1, y1, x2, y2, color, width, dash=5, gap=4):
        import math
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            return
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length:
            seg_end = min(pos + dash, length)
            self.draw.line(self._s(x1 + ux * pos, y1 + uy * pos,
                                    x1 + ux * seg_end, y1 + uy * seg_end),
                            fill=color, width=int(width * SCALE))
            pos += dash + gap

    def group_label(self, x, y, w, label, color=MUTED, size=9.5):
        f = bold(size)
        bbox = self.draw.textbbox((0, 0), label, font=f)
        tw = (bbox[2] - bbox[0]) / SCALE
        self.draw.text(self._s(x + w / 2 - tw / 2, y), label.upper(), font=f, fill=color)

    def save(self, name):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / name
        self.img.save(path, "PNG")
        print(path)


def architecture():
    d = Diagram(760, 340)
    d.box(20, 130, 140, 60, "Browser\nPWA / iOS", fill=WHITE, outline=MUTED, text_color=INK)
    d.box(220, 110, 180, 100, "ServiceOps app\n(Flask, stateless)", fill=TEAL, outline=DARK,
          text_color=WHITE, sublabel="web replicas 1..N", sub_color=(220, 230, 232))
    d.box(480, 30, 170, 60, "PostgreSQL", fill=PANEL, outline=TEAL)
    d.box(480, 110, 170, 60, "Uploads\n(volume / RWX / S3)", fill=PANEL, outline=TEAL, font_size=11.5)
    d.box(480, 190, 170, 60, "Worker\n(SLA · workflows · outbox)", fill=PANEL, outline=TEAL, font_size=11)
    d.box(220, 250, 180, 60, "AD / LDAP\nKeycloak (optional)", fill=WHITE, outline=MUTED, font_size=11)
    d.box(480, 270, 170, 55, "SMTP · Webhooks\nChat / Teams (optional)", fill=WHITE, outline=MUTED, font_size=10.5)

    d.arrow(160, 158, 218, 150, label="HTTPS")
    d.arrow(400, 145, 478, 60, label="SQL")
    d.arrow(400, 155, 478, 140, label="read/write")
    d.arrow(400, 175, 478, 210)
    d.arrow(660, 220, 660, 190, dashed=True, label="events, schedules")
    d.arrow(660, 250, 660, 270, label="deliver")
    d.arrow(310, 210, 310, 250, dashed=True, label="verify / sync")
    d.text(20, 30, "System architecture", size=16, bold_font=True, color=DARK)
    d.text(20, 55, "One PostgreSQL database and one worker process serve every application replica.",
           size=10, color=MUTED)
    d.save("architecture.png")


def deployment_topology():
    d = Diagram(780, 300)
    d.text(20, 20, "Deployment topologies", size=16, bold_font=True, color=DARK)
    cols = [
        (20, "Single server", ["ServiceOps app", "Bundled PostgreSQL", "Docker volume"],
         "Evaluation / one-server production"),
        (280, "Single server, external DB", ["ServiceOps app", "External PostgreSQL", "Docker volume + backups"],
         "Separate backup ownership"),
        (540, "Kubernetes", ["ServiceOps app × 3+", "External HA PostgreSQL", "RWX / S3 storage"],
         "High availability, horizontal scale"),
    ]
    for x, title, boxes, caption in cols:
        d.group_label(x, 60, 210, title, color=TEAL, size=10.5)
        y = 85
        for i, label in enumerate(boxes):
            fill = TEAL if i == 0 else PANEL
            text_color = WHITE if i == 0 else INK
            d.box(x, y, 210, 46, label, fill=fill, outline=DARK if i == 0 else TEAL,
                  text_color=text_color, font_size=10.5)
            if i < len(boxes) - 1:
                d.arrow(x + 105, y + 46, x + 105, y + 58)
            y += 58
        d.text(x, y + 8, caption, size=9, color=MUTED, max_width=210)
    d.save("deployment_topology.png")


def change_governance():
    d = Diagram(780, 220)
    d.text(20, 15, "Normal change governance flow", size=16, bold_font=True, color=DARK)
    steps = ["Draft", "Team / manager\napproval", "CCB\napproval", "Approved", "Implementation\n(change tasks)", "Post-\nimplementation\nreview"]
    x = 20
    w = 115
    gap = 8
    for i, label in enumerate(steps):
        fill = AMBER if label == "Approved" else PANEL
        d.box(x, 70, w, 60, label, fill=fill, outline=TEAL, font_size=9.5)
        if i < len(steps) - 1:
            d.arrow(x + w, 100, x + w + gap, 100)
        x += w + gap
    d.arrow(x - w - gap - w / 2, 130, 135, 165, color=(160, 60, 40), dashed=True,
            label="material change → invalidates approvals, restarts at Draft")
    d.text(20, 175, "Scope, plan, risk, affected CIs, schedule, or assignment-group changes after approval",
           size=9, color=MUTED)
    d.text(20, 190, "reopen the record at the pre-approval gate and start a new approval cycle.",
           size=9, color=MUTED)
    d.save("change_governance.png")


def identity_flow():
    d = Diagram(780, 300)
    d.text(20, 15, "Identity: sign-in and directory reconciliation", size=16, bold_font=True, color=DARK)
    d.box(20, 60, 160, 55, "Local\nadministrator", fill=WHITE, outline=MUTED, font_size=10.5)
    d.box(20, 130, 160, 55, "AD / LDAP\nbind + search", fill=WHITE, outline=MUTED, font_size=10.5)
    d.box(20, 200, 160, 55, "Keycloak\nOIDC code flow", fill=WHITE, outline=MUTED, font_size=10.5)
    d.box(250, 120, 170, 75, "Authenticated\nsession", fill=TEAL, outline=DARK, text_color=WHITE, font_size=11.5)
    d.arrow(180, 87, 248, 140)
    d.arrow(180, 157, 248, 155)
    d.arrow(180, 227, 248, 172)
    d.box(500, 40, 250, 70, "Just-in-time provisioning", fill=PANEL, outline=TEAL, font_size=10.5,
          sublabel="new account created on first\nsuccessful LDAP/Keycloak login", sub_size=9)
    d.box(500, 130, 250, 90, "Scheduled reconciliation\n(per tenant)", fill=PANEL, outline=TEAL, font_size=10.5,
          sublabel="worker loop, ≥15 min cadence\nrefreshes profile + manager chain\nnever bulk-imports the directory", sub_size=9)
    d.arrow(420, 155, 498, 75, label="first login")
    d.arrow(420, 165, 498, 170, dashed=True, label="every cycle")
    d.text(500, 235, "No “sync all LDAP users” action exists by design — accounts", size=9, color=MUTED)
    d.text(500, 249, "are created by authentication, not by a bulk directory import.", size=9, color=MUTED)
    d.save("identity_flow.png")


def backup_upgrade_flow():
    d = Diagram(820, 300)
    d.text(20, 15, "Backup, upgrade, and rollback safety flow", size=16, bold_font=True, color=DARK)
    steps = [
        ("serviceops\nbackup", PANEL),
        ("rehearse-recovery /\nrehearse-upgrade", PANEL),
        ("deploy or\nserviceops update", TEAL),
        ("verify health,\nlogin, workflows", PANEL),
    ]
    x = 20
    w = 175
    gap = 22
    boxes_xy = []
    for label, fill in steps:
        text_color = WHITE if fill == TEAL else INK
        d.box(x, 70, w, 65, label, fill=fill, outline=DARK, text_color=text_color, font_size=10.5)
        boxes_xy.append(x)
        x += w + gap
    for bx in boxes_xy[:-1]:
        d.arrow(bx + w, 102, bx + w + gap, 102)
    last_x = boxes_xy[-1]
    d.arrow(last_x + w / 2, 135, last_x + w / 2, 175, color=(160, 60, 40))
    d.box(20, 175, last_x + w - 20, 75,
          "Failed?  Atomic rollback restores the prior release.\nDatabase migrations are never auto-reversed —\nrestore from the verified backup instead.",
          fill=WHITE, outline=(160, 60, 40), text_color=(120, 40, 25), font_size=9.5)
    d.text(20, 265, "A pre-upgrade backup reference is mandatory; the updater refuses to proceed without one.",
           size=9, color=MUTED)
    d.save("backup_upgrade_flow.png")


if __name__ == "__main__":
    architecture()
    deployment_topology()
    change_governance()
    identity_flow()
    backup_upgrade_flow()
