"""Regenerate blog SVGs with non-overlapping layout."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "public" / "blog" / "glider-orchestration"
OUT.mkdir(parents=True, exist_ok=True)

MARKER = """
<defs>
  <marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="#334155"/>
  </marker>
  <marker id="af" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="#c2410c"/>
  </marker>
</defs>
"""


def svg(name: str, w: int, h: int, body: str) -> None:
    (OUT / name).write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  {MARKER}
  {body}
</svg>
""",
        encoding="utf-8",
    )


def box(x, y, w, h, fill, label, fs=14):
    # multi-line label via tspans if | present
    lines = label.split("|")
    texts = []
    start_y = y + h / 2 - (len(lines) - 1) * 9
    for i, line in enumerate(lines):
        texts.append(
            f'<text x="{x + w / 2}" y="{start_y + i * 18}" text-anchor="middle" '
            f'font-family="IBM Plex Sans, system-ui, sans-serif" font-size="{fs}" fill="#1e3a5f">{line}</text>'
        )
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
        f'stroke="#1e3a5f" stroke-width="2"/>' + "".join(texts)
    )


def title(x, y, t, size=22):
    return (
        f'<text x="{x}" y="{y}" font-family="Fraunces, Georgia, serif" '
        f'font-size="{size}" fill="#0f172a">{t}</text>'
    )


def arrow(x1, y1, x2, y2, *, dashed=False, color="#334155", mid=None, mid_dx=8, mid_dy=0, mid_anchor="start"):
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    mk = "af" if dashed else "a"
    out = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="2"{dash} marker-end="url(#{mk})"/>'
    )
    if mid:
        out += (
            f'<text x="{(x1 + x2) / 2 + mid_dx}" y="{(y1 + y2) / 2 + mid_dy}" '
            f'text-anchor="{mid_anchor}" '
            f'font-family="IBM Plex Sans, system-ui, sans-serif" font-size="12" '
            f'fill="{color}">{mid}</text>'
        )
    return out


def vstack(cx, top, items, gap=28, bw=280, bh=56):
    """items: list of (fill, label). Returns (body, centers[(x,y,w,h),...])."""
    body = ""
    boxes = []
    y = top
    for fill, label in items:
        x = cx - bw / 2
        body += box(x, y, bw, bh, fill, label)
        boxes.append((x, y, bw, bh))
        y += bh + gap
    for i in range(len(boxes) - 1):
        _, y1, _, h1 = boxes[i]
        _, y2, _, _ = boxes[i + 1]
        body += arrow(cx, y1 + h1, cx, y2)
    return body, boxes


def main() -> None:
    # 01 — vertical stack with clear gaps
    b = title(40, 40, "Glider orchestration stack")
    layers = [
        (80, 70, 520, 64, "#bae6fd", "Dashboard :8081  ·  Gateway :8080  ·  MITM :8082"),
        (80, 170, 520, 64, "#fde68a", "Router  →  Transform  →  Orchestrator"),
        (80, 270, 240, 72, "#bbf7d0", "Loop Manager|(hoops / stages)"),
        (360, 270, 240, 72, "#fbcfe8", "Swarm Runner|(templates / waves)"),
        (80, 380, 520, 64, "#fed7aa", "Tools registry  +  runs/&lt;id&gt;/{work,out}"),
        (80, 480, 520, 64, "#e2e8f0", "Backends: Ollama / vLLM / BYOK cloud"),
    ]
    for L in layers:
        b += box(*L)
    b += arrow(340, 134, 340, 170)
    b += arrow(340, 234, 200, 270)
    b += arrow(340, 234, 480, 270)
    b += arrow(340, 342, 340, 380)
    b += arrow(340, 444, 340, 480)
    svg("01-orchestration-stack.svg", 680, 580, b)

    # 02 — hoop cycle: clean vertical main path + side loop
    b = title(40, 36, "Hoop cycle (Loop Engineering)")
    b += (
        '<text x="40" y="62" font-family="IBM Plex Sans, system-ui, sans-serif" '
        'font-size="13" fill="#64748b">Main path ↓ · optional pause on the right · next round loops up</text>'
    )
    main = [
        ("#bae6fd", "1  workspace|scratch + output folders for this run"),
        ("#c7d2fe", "2  planner|decide what to do (text plan)"),
        ("#bbf7d0", "3  actor|do the work (tools / writes)"),
        ("#fde68a", "4  critic|score the result (SCORE:)"),
        ("#fbcfe8", "5  memory|save what happened"),
    ]
    col, boxes = vstack(260, 90, main, gap=36, bw=320, bh=58)
    b += col
    # human_gate beside critic
    b += box(520, 90 + 3 * (58 + 36), 260, 58, "#fecaca", "human_gate|pause for a person")
    # critic → human_gate (right)
    cy = boxes[3][1] + boxes[3][3] / 2
    b += arrow(
        boxes[3][0] + boxes[3][2],
        cy,
        520,
        cy,
        mid="if review needed",
        mid_dx=0,
        mid_dy=-14,
        mid_anchor="middle",
    )
    # human_gate → memory (down-left into path) — or back into path before memory
    b += arrow(650, boxes[3][1] + boxes[3][3], 650, boxes[4][1] + 20)
    b += arrow(650, boxes[4][1] + 29, boxes[4][0] + boxes[4][2], boxes[4][1] + 29)
    # next iteration: memory → workspace (left rail)
    b += arrow(
        boxes[4][0],
        boxes[4][1] + boxes[4][3] / 2,
        70,
        boxes[4][1] + boxes[4][3] / 2,
        dashed=True,
        color="#c2410c",
    )
    b += arrow(
        70,
        boxes[4][1] + boxes[4][3] / 2,
        70,
        boxes[0][1] + boxes[0][3] / 2,
        dashed=True,
        color="#c2410c",
        mid="next round",
        mid_dx=-10,
        mid_dy=0,
        mid_anchor="end",
    )
    b += arrow(
        70,
        boxes[0][1] + boxes[0][3] / 2,
        boxes[0][0],
        boxes[0][1] + boxes[0][3] / 2,
        dashed=True,
        color="#c2410c",
    )
    b += box(
        120,
        90 + 5 * (58 + 36) + 20,
        560,
        48,
        "#e2e8f0",
        "feeds (optional): one step’s summary is pasted into a later step’s prompt",
        fs=13,
    )
    svg("02-hoop-cycle.svg", 820, 660, b)

    # 03 — fanout vs swarm side by side, no overlap
    b = title(40, 40, "Parallel: fanout vs nested swarm")
    # left column
    b += box(40, 80, 340, 56, "#bbf7d0", "Actor  parallel_mode = fanout")
    workers = [
        (40, 180, 100, 56, "#bae6fd", "w0|quality"),
        (160, 180, 100, 56, "#bae6fd", "w1|security"),
        (280, 180, 100, 56, "#bae6fd", "w2|secrets"),
    ]
    for w in workers:
        b += box(*w)
    b += box(40, 280, 340, 56, "#fde68a", "CritiqueMerge → one stage result")
    b += arrow(210, 136, 90, 180)
    b += arrow(210, 136, 210, 180)
    b += arrow(210, 136, 330, 180)
    b += arrow(210, 236, 210, 280)

    # right column
    b += box(440, 80, 360, 56, "#fbcfe8", "Actor  parallel_mode = swarm")
    b += box(440, 180, 360, 56, "#c7d2fe", "swarm.Runner.Run / RunWaves")
    b += box(440, 280, 170, 56, "#bae6fd", "roles")
    b += box(630, 280, 170, 56, "#bae6fd", "weave")
    b += box(440, 380, 360, 56, "#fde68a", "Merged summary → hoop cycle")
    b += arrow(620, 136, 620, 180)
    b += arrow(620, 236, 525, 280)
    b += arrow(620, 236, 715, 280)
    b += arrow(620, 336, 620, 380)
    svg("03-fanout-vs-swarm.svg", 840, 480, b)

    # 04 — workspace
    b = title(40, 40, "Per-run workspace binding")
    b += box(200, 80, 400, 56, "#c7d2fe", "Hoop / Swarm / /cloud turn")
    b += box(40, 200, 300, 64, "#bbf7d0", "mode = run|(fresh runs/&lt;id&gt;/…)")
    b += box(460, 200, 340, 64, "#fde68a", "mode = existing|(reuse sandbox path)")
    b += box(40, 320, 300, 64, "#fed7aa", "work/|(action · clones · scratch)")
    b += box(460, 320, 340, 64, "#bae6fd", "out/|(reports · packs · finals)")
    b += box(80, 440, 680, 56, "#e2e8f0", "~/.glider/workspace sandbox  ·  ScopeRel + artifact_write")
    b += arrow(400, 136, 190, 200)
    b += arrow(400, 136, 630, 200)
    b += arrow(190, 264, 190, 320)
    b += arrow(630, 264, 630, 320)
    b += arrow(400, 384, 400, 440)
    svg("04-workspace-binding.svg", 860, 540, b)

    # 05 — audit hoop: single vertical spine (readable)
    b = title(40, 36, "Repo security audit hoop — happy path")
    b += (
        '<text x="40" y="62" font-family="IBM Plex Sans, system-ui, sans-serif" '
        'font-size="13" fill="#64748b">Read top → bottom. Orange dashed = try again / ask a human again.</text>'
    )
    audit = [
        ("#bbf7d0", "1  memory — load notes from last time (if any)"),
        ("#c7d2fe", "2  router — prefer local model for this job"),
        ("#bae6fd", "3  planner — short checklist only (no clone yet)"),
        ("#bbf7d0", "4  actor — clone the repo into work/audit-target"),
        ("#bbf7d0", "5  actor — verify the clone folder is really there"),
        ("#a5f3fc", "6  context — write shared “clone lives here” facts"),
        ("#bbf7d0", "7  actor — parallel quality + security helpers"),
        ("#fecaca", "8  human_gate — person reviews findings"),
        ("#fde68a", "9  critic — SCORE: is the audit usable?"),
        ("#fbcfe8", "10 memory — save this cycle’s result"),
    ]
    col, boxes = vstack(300, 88, audit, gap=22, bw=420, bh=48)
    b += col
    # feedback rail: critic → planner
    b += arrow(
        boxes[8][0] + boxes[8][2],
        boxes[8][1] + boxes[8][3] / 2,
        620,
        boxes[8][1] + boxes[8][3] / 2,
        dashed=True,
        color="#c2410c",
    )
    b += arrow(
        620,
        boxes[8][1] + boxes[8][3] / 2,
        620,
        boxes[2][1] + boxes[2][3] / 2,
        dashed=True,
        color="#c2410c",
        mid="replan",
        mid_dx=10,
        mid_dy=0,
        mid_anchor="start",
    )
    b += arrow(
        620,
        boxes[2][1] + boxes[2][3] / 2,
        boxes[2][0] + boxes[2][2],
        boxes[2][1] + boxes[2][3] / 2,
        dashed=True,
        color="#c2410c",
    )
    # on_fail critic → human_gate (shorter rail)
    b += arrow(
        boxes[8][0] + boxes[8][2],
        boxes[8][1] + boxes[8][3] / 2 + 10,
        560,
        boxes[8][1] + boxes[8][3] / 2 + 10,
        dashed=True,
        color="#c2410c",
    )
    b += arrow(
        560,
        boxes[8][1] + boxes[8][3] / 2 + 10,
        560,
        boxes[7][1] + boxes[7][3] / 2,
        dashed=True,
        color="#c2410c",
        mid="ask human",
        mid_dx=10,
        mid_dy=0,
        mid_anchor="start",
    )
    b += arrow(
        560,
        boxes[7][1] + boxes[7][3] / 2,
        boxes[7][0] + boxes[7][2],
        boxes[7][1] + boxes[7][3] / 2,
        dashed=True,
        color="#c2410c",
    )
    svg("05-audit-hoop-flow.svg", 760, 880, b)

    print("wrote", sorted(p.name for p in OUT.iterdir() if p.suffix == ".svg"))


if __name__ == "__main__":
    main()
