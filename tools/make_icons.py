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
BG = "#ffffff"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Excavator icon: SVG Repo #503877 "Excavator" (Transportation Stylized Duotone Icons), Public Domain licence —
# https://www.svgrepo.com/svg/503877/excavator  (source kept in tools/excavator-source.svg)
import re as _re
_SRC = (Path(__file__).resolve().parent / "excavator-source.svg").read_text(encoding="utf-8")
INNER = _re.search(r"<svg[^>]*>(.*)</svg>", _SRC, _re.S).group(1).strip()
BX, BY, BW, BH = 208.56, 250.29, 637.24, 522.81   # drawing bounding box (measured with getBBox)


def mark(fill=0.80):
    s = 64 * fill / BW
    tx, ty = (64 - BW * s) / 2 - BX * s, (64 - BH * s) / 2 - BY * s
    return f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.5f})">{INNER}</g>'


def favicon_svg():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="{BG}"/>{mark()}</svg>\n'


def maskable_svg():   # full-bleed background, mark inside the 80% safe zone
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="{BG}"/>{mark(0.62)}</svg>\n'


def logo_svg():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 64"><rect width="64" height="64" rx="15" fill="{BG}"/>{mark()}'
            f'<text x="78" y="42" font-family="Manrope, Inter, Arial, sans-serif" font-weight="800" font-size="30" fill="#0b2545">Eqskavatori<tspan fill="#1f87dd">.ge</tspan></text></svg>\n')


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
        f'  "background_color": "#ffffff",\n  "theme_color": "#09090b",\n  "icons": [\n'
        '    {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},\n'
        '    {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},\n'
        '    {"src": "/assets/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}\n  ]\n}\n', encoding="utf-8")
    print("icons ok")


if __name__ == "__main__":
    main()
