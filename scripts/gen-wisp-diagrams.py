"""Draw the SVG diagrams for the Wisp post (public/blog/wisp/).

    python3 scripts/gen-wisp-diagrams.py

Colours and fonts follow src/styles/global.css. Every label is placed by hand, so
check the rendered output after you change any text.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "public" / "blog" / "wisp"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = "#fbf8f1"
INK = "#12151a"
SOFT = "#5b6472"
LINE = "#d4cec0"
ACCENT = "#0a7c8c"  # site accent (teal)
TEAL_BG = "#d9f2ef"
VIOLET = "#5b3fd1"  # Wisp
VIOLET_BG = "#e7e1fb"
NIGHT = "#21135a"
AMBER = "#b45309"
AMBER_BG = "#fdecc8"
GREY_BG = "#ebe7dd"

SANS = "IBM Plex Sans, system-ui, sans-serif"
MONO = "IBM Plex Mono, ui-monospace, monospace"
SERIF = "Fraunces, Georgia, serif"

DEFS = f"""<defs>
  <marker id="ink" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="{INK}"/></marker>
  <marker id="teal" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="{ACCENT}"/></marker>
  <marker id="violet" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="{VIOLET}"/></marker>
  <marker id="amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="{AMBER}"/></marker>
</defs>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(name, w, h, title_text, body):
    (OUT / name).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title_text)}">\n'
        f'<title>{esc(title_text)}</title>\n'
        f'<rect width="100%" height="100%" rx="14" fill="{PAPER}"/>\n{DEFS}\n{body}\n</svg>\n',
        encoding="utf-8",
    )


def text(x, y, s, size=14, fill=INK, font=SANS, anchor="start", weight="normal", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{st}>{esc(s)}</text>')


def lines(x, y, rows, size=14, fill=INK, font=SANS, anchor="start", gap=None, weight="normal"):
    gap = gap or size + 5
    return "".join(text(x, y + i * gap, r, size, fill, font, anchor, weight) for i, r in enumerate(rows))


def box(x, y, w, h, fill, stroke=INK, rx=10, dash=False, sw=1.6):
    d = ' stroke-dasharray="6 5"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def label_box(x, y, w, h, fill, head, sub=(), stroke=INK, head_size=15, sub_size=12.5):
    rows = [head] + list(sub)
    total = head_size + (len(sub) * (sub_size + 5))
    top = y + h / 2 - total / 2 + head_size - 2
    out = [box(x, y, w, h, fill, stroke)]
    out.append(text(x + w / 2, top, head, head_size, INK, SANS, "middle", "600"))
    for i, s in enumerate(sub):
        out.append(text(x + w / 2, top + (i + 1) * (sub_size + 5) + 2, s, sub_size, SOFT, SANS, "middle"))
    return "".join(out)


def arrow(x1, y1, x2, y2, color=INK, marker="ink", dash=False, sw=1.8):
    d = ' stroke-dasharray="6 5"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"{d}/>')


def path(d, color=INK, marker=None, dash=False, sw=1.8, fill="none"):
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = ' stroke-dasharray="6 5"' if dash else ""
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"{m}{da}/>'


def heading(t, sub=None):
    out = text(36, 42, t, 22, INK, SERIF)
    if sub:
        out += text(36, 66, sub, 13.5, SOFT)
    return out


def cursor(x, y, s=1.0, fill="#ffffff", stroke=INK):
    pts = [(0, 0), (0, 17), (4, 13), (7.2, 20), (10, 18.8), (7, 12), (12.5, 12)]
    p = " ".join("%.1f,%.1f" % (x + a * s, y + b * s) for a, b in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round"/>'


def monitor(x, y, w, h, label, sub, screen=TEAL_BG):
    out = [box(x, y, w, h, screen, INK, 8, sw=2)]
    out.append(f'<rect x="{x + w / 2 - 16}" y="{y + h}" width="32" height="14" fill="{GREY_BG}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<rect x="{x + w / 2 - 46}" y="{y + h + 14}" width="92" height="7" rx="3" fill="{GREY_BG}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(text(x + w / 2, y + 30, label, 15, INK, SANS, "middle", "600"))
    out.append(text(x + w / 2, y + 50, sub, 12.5, SOFT, SANS, "middle"))
    return "".join(out)


# ---------------------------------------------------------------- 1. the big picture
def big_picture():
    b = [heading("The big picture", "The pointer moves from one computer to the other at a screen edge.")]
    # sharing PC
    b.append(monitor(48, 100, 250, 150, "Sharing computer", "has the keyboard & mouse"))
    b.append(box(78, 300, 150, 30, GREY_BG, INK, 6))
    for i in range(9):
        b.append(f'<rect x="{88 + i * 15}" y="308" width="10" height="6" rx="1.5" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    b.append(f'<rect x="108" y="318" width="90" height="6" rx="1.5" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
    b.append(f'<ellipse cx="258" cy="315" rx="15" ry="20" fill="{GREY_BG}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<line x1="258" y1="297" x2="258" y2="308" stroke="{INK}" stroke-width="1.4"/>')
    # receiving Mac
    b.append(monitor(522, 100, 250, 150, "Receiving computer", "no keyboard or mouse of its own"))
    # pointer path
    b.append(path("M150,205 C200,195 250,182 296,176", VIOLET, None, True, 2.2))
    b.append(cursor(146, 196, 1.0))
    b.append(path("M524,176 C560,172 600,188 640,206", VIOLET, "violet", True, 2.2))
    b.append(cursor(640, 200, 1.0, VIOLET_BG, VIOLET))
    b.append(f'<line x1="297" y1="110" x2="297" y2="240" stroke="{VIOLET}" stroke-width="4"/>')
    b.append(f'<line x1="523" y1="110" x2="523" y2="240" stroke="{VIOLET}" stroke-width="4"/>')
    # the link
    b.append(box(330, 150, 160, 60, VIOLET_BG, VIOLET, 30))
    b.append(text(410, 175, "local network", 13.5, NIGHT, SANS, "middle", "600"))
    b.append(text(410, 194, "TCP port 24800", 12.5, NIGHT, MONO, "middle"))
    b.append(arrow(300, 162, 326, 162, VIOLET, "violet"))
    b.append(arrow(494, 162, 518, 162, VIOLET, "violet"))
    b.append(text(410, 238, "your input, one event at a time", 12.5, SOFT, SANS, "middle"))
    # captions
    b.append(lines(48, 372, ["The real keyboard and mouse stay connected here.",
                             "Wisp blocks their events while the pointer",
                             "is on the other computer."], 12.5, SOFT))
    b.append(lines(522, 372, ["Wisp replays each event here, so apps see",
                              "an ordinary keyboard and mouse."], 12.5, SOFT))
    svg("01-big-picture.svg", 820, 440, "Wisp: the sharing computer sends its input to the receiving computer", "".join(b))


# ---------------------------------------------------------------- 2. the pipeline
def pipeline():
    b = [heading("One keystroke, end to end", "Each box is one part of wisp.py. Both computers run the same file.")]
    w, h, gap, x0 = 168, 76, 26, 36
    xs = [x0 + i * (w + gap) for i in range(4)]
    b.append(text(36, 104, "SHARING COMPUTER", 11.5, ACCENT, MONO, weight="600"))
    top = [("Keyboard & mouse", ["the real hardware"]),
           ("Input hook", ["Windows: low-level hook", "Mac: event tap"]),
           ("Here or there?", ["here: pass it to apps", "there: block it, send it"]),
           ("Send queue", ["merges mouse moves", "into one message"])]
    for i, (hd, sub) in enumerate(top):
        b.append(label_box(xs[i], 116, w, h, TEAL_BG if i else GREY_BG, hd, sub))
        if i:
            b.append(arrow(xs[i - 1] + w + 2, 154, xs[i] - 4, 154))
    # network band
    b.append(box(36, 236, 748, 46, VIOLET_BG, VIOLET, 23))
    b.append(text(410, 264, '{"t": "k", "n": "c", "p": true, "q": 17}   one JSON line per event', 13, NIGHT, MONO, "middle"))
    b.append(arrow(xs[3] + w / 2, 194, xs[3] + w / 2, 232, VIOLET, "violet"))
    b.append(arrow(xs[0] + w - 24, 284, xs[0] + w - 24, 322, VIOLET, "violet"))
    b.append(text(36, 314, "RECEIVING COMPUTER", 11.5, VIOLET, MONO, weight="600"))
    bot = [("Read socket", ["one line, one event"]),
           ("Client core", ["tracks pointer, keys,", "screen edges"]),
           ("Injector", ["Windows: SendInput", "Mac: CGEventPost"]),
           ("Apps", ["see a normal", "keyboard & mouse"])]
    for i, (hd, sub) in enumerate(bot):
        b.append(label_box(xs[i], 326, w, h, VIOLET_BG if i < 3 else GREY_BG, hd, sub))
        if i:
            b.append(arrow(xs[i - 1] + w + 2, 364, xs[i] - 4, 364))
    b.append(lines(36, 440, ["When Wisp blocks an event, apps on the sharing computer never see it.",
                             "When the event stays on the sharing computer, Wisp sends nothing."], 12.5, SOFT))
    svg("02-pipeline.svg", 820, 480, "The path of one keystroke through Wisp", "".join(b))


# ---------------------------------------------------------------- 3. the conversation
def conversation():
    b = [heading("What the two computers say to each other",
                 "Newline-delimited JSON over one TCP connection. Real message shapes, shortened.")]
    lx, rx = 150, 670
    b.append(label_box(lx - 90, 88, 180, 40, TEAL_BG, "Sharing computer"))
    b.append(label_box(rx - 90, 88, 180, 40, VIOLET_BG, "Receiving computer"))
    b.append(f'<line x1="{lx}" y1="130" x2="{lx}" y2="600" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 5"/>')
    b.append(f'<line x1="{rx}" y1="130" x2="{rx}" y2="600" stroke="{LINE}" stroke-width="2" stroke-dasharray="4 5"/>')
    rows = [
        ("<", '{"t":"hello","token":"482913","os":"Darwin"}', "receiver connects and gives the code"),
        (">", '{"t":"hello","os":"Windows","name":"DESKTOP-1"}', "code accepted"),
        (">", '{"t":"enter","r":0.42}', "pointer crossed, 42% down the edge"),
        (">", '{"t":"m","dx":5,"dy":-2}', "mouse moved"),
        (">", '{"t":"b","b":"left","p":true}', "left button pressed"),
        (">", '{"t":"k","n":"c","p":true,"q":17}', "key c pressed, 17th key event"),
        (">", '{"t":"ping","held":["ctrl"]}', "every second: keys still held down"),
        ("<", '{"t":"pong"}', "receiver answers, giving the round-trip time"),
        ("<", '{"t":"leave","r":0.61}', "pointer crossed back, control returns to the sharer"),
    ]
    y = 168
    for d, msg, note in rows:
        col, mk = (ACCENT, "teal") if d == ">" else (VIOLET, "violet")
        if d == ">":
            b.append(arrow(lx + 4, y, rx - 8, y, col, mk))
        else:
            b.append(arrow(rx - 4, y, lx + 8, y, col, mk))
        b.append(text((lx + rx) / 2, y - 8, msg, 12.5, INK, MONO, "middle"))
        b.append(text((lx + rx) / 2, y + 17, note, 11.5, SOFT, SANS, "middle", italic=True))
        y += 50
    svg("03-conversation.svg", 820, 630, "The messages Wisp sends between the two computers", "".join(b))


# ---------------------------------------------------------------- 4. edges
def edges():
    b = [heading("Which edges lead to the other computer",
                 "Wisp only crosses at an edge with no screen beyond it, on the side you chose.")]
    # PC: laptop + taller monitor
    b.append(box(40, 132, 170, 104, TEAL_BG, INK, 6, sw=2))
    b.append(text(125, 190, "screen 1", 13, INK, SANS, "middle", "600"))
    b.append(box(210, 108, 220, 150, TEAL_BG, INK, 6, sw=2))
    b.append(text(320, 190, "screen 2", 13, INK, SANS, "middle", "600"))
    b.append(text(235, 290, "SHARING COMPUTER", 11.5, ACCENT, MONO, "middle", "600"))
    # shared edge (between screens) vs free edge (right of screen 2)
    b.append(f'<line x1="210" y1="134" x2="210" y2="234" stroke="{AMBER}" stroke-width="5"/>')
    b.append(f'<line x1="430" y1="110" x2="430" y2="256" stroke="{VIOLET}" stroke-width="5"/>')
    # ratio marker: 42% of the span 108..258
    ry = 108 + 0.42 * 150
    b.append(f'<circle cx="430" cy="{ry}" r="6" fill="{VIOLET}"/>')
    # Mac
    b.append(box(560, 120, 220, 130, VIOLET_BG, INK, 6, sw=2))
    b.append(text(670, 190, "Mac screen", 13, INK, SANS, "middle", "600"))
    b.append(text(670, 290, "RECEIVING COMPUTER", 11.5, VIOLET, MONO, "middle", "600"))
    b.append(f'<line x1="560" y1="122" x2="560" y2="248" stroke="{VIOLET}" stroke-width="5"/>')
    my = 120 + 0.42 * 130
    b.append(f'<circle cx="560" cy="{my}" r="6" fill="{VIOLET}"/>')
    b.append(path(f"M436,{ry} C480,{ry - 26} 512,{my - 26} 552,{my}", VIOLET, "violet", True, 2))
    b.append(text(495, ry - 34, "r = 0.42", 12.5, NIGHT, MONO, "middle"))
    # legend
    b.append(f'<line x1="40" y1="328" x2="70" y2="328" stroke="{AMBER}" stroke-width="5"/>')
    b.append(lines(82, 333, ["Shared edge: another screen on this computer lies beyond it,",
                             "so the pointer moves there as usual."], 13, INK))
    b.append(f'<line x1="40" y1="388" x2="70" y2="388" stroke="{VIOLET}" stroke-width="5"/>')
    b.append(lines(82, 393, ["Free edge on the chosen side: the pointer crosses here. Wisp sends",
                             "how far along the edge it was (0 is the top, 1 is the bottom), and",
                             "the other computer enters at the same fraction of its own edge."], 13, INK))
    svg("04-edges.svg", 820, 470, "Shared and free screen edges, and how the crossing point carries over", "".join(b))


# ---------------------------------------------------------------- 5. discovery
def discovery():
    b = [heading("Finding the other computer",
                 "A broadcast asks who is sharing. The pairing code stays on the sharing computer's screen.")]
    b.append(label_box(40, 96, 200, 64, VIOLET_BG, "Receiving computer", ["presses Find"]))
    for i, (nm, ip) in enumerate((("DESKTOP-1", "192.168.1.50"), ("studio-mac", "192.168.1.77"))):
        y = 96 + i * 104
        b.append(label_box(580, y, 200, 64, TEAL_BG, nm, ["sharing, " + ip]))
    b.append(arrow(244, 118, 574, 118, VIOLET, "violet"))
    b.append(arrow(244, 136, 574, 214, VIOLET, "violet"))
    b.append(text(410, 106, 'broadcast  "KMSHARE?"  to UDP 24801', 12.5, NIGHT, MONO, "middle"))
    b.append(arrow(576, 150, 248, 150, ACCENT, "teal", True))
    b.append(text(420, 172, 'reply  "KMSHARE!" + {"name", "port"}', 12.5, ACCENT, MONO, "middle"))
    b.append(text(420, 190, "(the message name comes from the project's old name)", 11.5, SOFT, SANS, "middle", italic=True))
    b.append(box(40, 300, 740, 92, GREY_BG, LINE, 12))
    b.append(lines(60, 328, ["Then you pick a computer from the list and type the 6-digit code shown on its screen.",
                             "Wisp opens a TCP connection to port 24800 and sends the code in its first message.",
                             "The sharing computer drops the connection if the code is wrong."], 13, INK, gap=22))
    svg("05-discovery.svg", 820, 420, "How Wisp finds sharing computers on the network", "".join(b))


# ---------------------------------------------------------------- 6. bufferbloat
def bufferbloat():
    b = [heading("Why a download makes the mouse lag",
                 "Every packet waits its turn in the router's queue, and small ones get no shortcut.")]
    b.append(label_box(40, 110, 150, 64, TEAL_BG, "Sharing computer"))
    b.append(label_box(630, 110, 150, 64, VIOLET_BG, "Receiving computer"))
    # router queue
    b.append(box(232, 96, 356, 92, GREY_BG, INK, 12))
    b.append(text(410, 90, "Wi-Fi router queue", 13, INK, SANS, "middle", "600"))
    for i in range(7):
        b.append(f'<rect x="{248 + i * 46}" y="112" width="38" height="60" rx="4" fill="#cfc8b8" stroke="{SOFT}" stroke-width="1.2"/>')
    b.append(f'<rect x="572" y="132" width="10" height="20" rx="2" fill="{VIOLET}"/>')
    b.append(arrow(194, 142, 228, 142))
    b.append(arrow(592, 142, 626, 142))
    b.append(text(267, 206, "download data", 12.5, SOFT, SANS, "start"))
    b.append(path("M577,156 L577,214 L520,214", VIOLET, None, False, 1.4))
    b.append(text(512, 219, "a mouse move", 12.5, VIOLET, SANS, "end", "600"))
    b.append(lines(40, 262, ["A mouse move is a few dozen bytes. A large download can keep the queue full,",
                             "so each move waits behind it. On this network that meant 300 ms or more."], 13, INK, gap=21))
    # fix
    b.append(text(40, 332, "WITH A CABLE BETWEEN THE TWO COMPUTERS", 11.5, ACCENT, MONO, weight="600"))
    b.append(label_box(40, 348, 150, 52, TEAL_BG, "Sharing"))
    b.append(label_box(630, 348, 150, 52, VIOLET_BG, "Receiving"))
    b.append(f'<line x1="194" y1="374" x2="626" y2="374" stroke="{ACCENT}" stroke-width="5"/>')
    b.append(f'<rect x="404" y="366" width="10" height="16" rx="2" fill="{VIOLET}"/>')
    b.append(text(410, 400, "a private link with nothing else in the queue: under 1 ms", 12.5, ACCENT, SANS, "middle"))
    svg("06-bufferbloat.svg", 820, 430, "Router queueing delays Wisp's small packets behind a download", "".join(b))


# ---------------------------------------------------------------- 7. scrambled keys
def scrambled():
    b = [heading("The day every key came out wrong",
                 "Pressing d five times reached the Mac as / ] + g z. The log showed where.")]
    b.append(label_box(40, 104, 150, 64, GREY_BG, "Keyboard", ["d d d d d"]))
    b.append(label_box(250, 104, 200, 64, AMBER_BG, "Anti-keylogging", ["Citrix App Protection"], stroke=AMBER))
    b.append(arrow(194, 136, 246, 136))
    b.append(label_box(560, 84, 220, 52, GREY_BG, "The protected window", ["gets the real keys"]))
    b.append(label_box(560, 156, 220, 52, AMBER_BG, "Every input hook", ["Wisp included"], stroke=AMBER))
    b.append(arrow(454, 124, 556, 110))
    b.append(arrow(454, 148, 556, 182, AMBER, "amber"))
    b.append(text(500, 101, "d d d d d", 12.5, INK, MONO, "middle"))
    b.append(text(506, 204, "/ ] + g z", 12.5, AMBER, MONO, "middle", "600"))
    b.append(lines(40, 252, ["Each fake key was a complete, valid key: its key code and scan code matched.",
                             "So Wisp could not tell it apart from a real one. Closing Citrix's main window fixed it."],
                   13, INK, gap=21))
    svg("07-scrambled-keys.svg", 820, 300, "Anti-keylogging software sends random keys to input hooks", "".join(b))


if __name__ == "__main__":
    big_picture()
    pipeline()
    conversation()
    edges()
    discovery()
    bufferbloat()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
