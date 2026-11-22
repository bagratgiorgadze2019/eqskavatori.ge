"""Logo + favicons for eqskavatori.ge (blue like the machine, yellow excavator mark).

    python3 tools/make_icons.py      -> assets/favicon.svg, assets/logo.svg, *.png, favicon.ico, site.webmanifest
PNG sizes are rendered with headless Chrome from the SVG.
"""
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "assets"
BLUE, YELLOW, INK = "#1d4ed8", "#facc15", "#0b1220"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 64x64 excavator mark: tracks, body, cab, boom + arm + bucket
MARK = f'''<rect x="5" y="44" width="34" height="11" rx="5.5" fill="{YELLOW}"/>
<circle cx="11" cy="49.5" r="2.4" fill="{BLUE}"/><circle cx="22" cy="49.5" r="2.4" fill="{BLUE}"/><circle cx="33" cy="49.5" r="2.4" fill="{BLUE}"/>
<rect x="8" y="31" width="25" height="11" rx="2.5" fill="{YELLOW}"/>
<path d="M11 31V19.5A2.5 2.5 0 0 1 13.5 17H23l3 6v8z" fill="{YELLOW}"/>
<path d="M15 20.5h6.5l2 4.5H15z" fill="{BLUE}"/>
<path d="M30 33 43.5 15.5 55 27" fill="none" stroke="{YELLOW}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M51 26.5h8.5l-1.6 9.2a2 2 0 0 1-2 1.6H52.5z" fill="{YELLOW}"/>'''


def favicon_svg(bg=True):
    rect = f'<rect width="64" height="64" rx="14" fill="{BLUE}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{rect}{MARK}</svg>\n'


def maskable_svg():   # safe zone: mark scaled to 70% in the centre
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="{BLUE}"/>'
            f'<g transform="translate(9.6 9.6) scale(.7)">{MARK}</g></svg>\n')


def logo_svg():  # horizontal lockup for docs / social (site header uses HTML text + favicon.svg)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 64"><rect width="64" height="64" rx="14" fill="{BLUE}"/>{MARK}'
            f'<text x="78" y="42" font-family="Manrope, Inter, Arial, sans-serif" font-weight="800" font-size="30" fill="#ffffff">Eqskavatori<tspan fill="{YELLOW}">.ge</tspan></text></svg>\n')


def render(svg_path, size, out):
    with tempfile.TemporaryDirectory() as d:
        html = Path(d) / "i.html"
        html.write_text(f'<html><body style="margin:0;background:transparent"><img src="file://{svg_path}" width="{size}" height="{size}"></body></html>')
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1", f"--window-size={size},{size}",
                        f"--screenshot={out}", f"file://{html}"], capture_output=True)


def ico(pngs, out):
    """ICO with embedded PNGs (supported by every modern browser)."""
    data = [Path(p).read_bytes() for p, _ in pngs]
    head = struct.pack("<HHH", 0, 1, len(pngs))
    off = 6 + 16 * len(pngs)
    entries = b""
    for (p, size), blob in zip(pngs, data):
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(blob), off)
        off += len(blob)
    Path(out).write_bytes(head + entries + b"".join(data))


def main():
    (A / "favicon.svg").write_text(favicon_svg(), encoding="utf-8")
    (A / "logo.svg").write_text(logo_svg(), encoding="utf-8")
    (A / "maskable.svg").write_text(maskable_svg(), encoding="utf-8")
    fav = (A / "favicon.svg").resolve()
    for size, name in ((180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png"), (32, "favicon-32.png"), (16, "favicon-16.png")):
        render(fav, size, A / name)
    render((A / "maskable.svg").resolve(), 512, A / "icon-maskable-512.png")
    ico([(A / "favicon-16.png", 16), (A / "favicon-32.png", 32)], ROOT / "favicon.ico")
    (ROOT / "site.webmanifest").write_text(
        '{\n  "name": "Eqskavatori.ge — მინი ექსკავატორის მომსახურება",\n  "short_name": "Eqskavatori",\n  "start_url": "/",\n  "display": "standalone",\n'
        f'  "background_color": "#09090b",\n  "theme_color": "#09090b",\n  "icons": [\n'
        '    {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},\n'
        '    {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},\n'
        '    {"src": "/assets/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}\n  ]\n}\n', encoding="utf-8")
    print("icons ok")


if __name__ == "__main__":
    main()
