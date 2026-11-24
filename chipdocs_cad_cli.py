#!/usr/bin/env python3
"""
ChipDocs.org Universal Multi-EDA & 3D MCAD Downloader CLI
Download verified CAD files for 24 ECAD & 3D MCAD tools from https://chipdocs.org with 1 command.

Usage:
  python3 chipdocs_cad_cli.py STM32F103C8T6 --format fusion_lbr
  python3 chipdocs_cad_cli.py ESP32-S3-WROOM-1 --format altium_lia --out ./libs
  python3 chipdocs_cad_cli.py RP2040 --format kicad_zip,step_3d,orcad_edif,allegro_scr,pads_asc
"""

import argparse
import json
import os
import re
import urllib.parse
import urllib.request

BASE = "https://chipdocs.org"

FORMATS = {
    "kicad_zip": ("kicad.zip", ".zip"),
    "kicad_mod": ("footprint.kicad_mod", ".kicad_mod"),
    "kicad_sym": ("symbol.kicad_sym", ".kicad_sym"),
    "fusion_lbr": ("library.lbr", ".lbr"),
    "altium_lia": ("library.lia", ".lia"),
    "altium_pas": ("altium_creator.pas", ".pas"),
    "orcad_edif": ("symbol.edf", ".edf"),
    "allegro_scr": ("footprint.scr", ".scr"),
    "pads_asc": ("library.pads.asc", ".pads.asc"),
    "diptrace_asc": ("library.diptrace.asc", ".diptrace.asc"),
    "cadstar_cpa": ("library.cpa", ".cpa"),
    "designspark_eil": ("library.eil", ".eil"),
    "geda_fp": ("footprint.fp", ".fp"),
    "fritzing_fzp": ("part.fzp", ".fzp"),
    "jlc_eda_json": ("library.eda.json", ".eda.json"),
    "ipc2581_xml": ("package.ipc2581.xml", ".ipc2581.xml"),
    "step_3d": ("model.step", ".step"),
    "glb_3d": ("model.glb", ".glb"),
    "autocad_dxf": ("drawing.dxf", ".dxf"),
    "mesh_stl": ("model.stl", ".stl"),
    "openscad_scad": ("parametric.scad", ".scad"),
    "freecad_macro": ("freecad_model.FCMacro", ".FCMacro"),
}


def main():
    p = argparse.ArgumentParser(description="Download verified CAD libraries from chipdocs.org")
    p.add_argument("query", help="MPN or LCSC code (e.g. STM32F103C8T6, ESP32-S3, NRF52840)")
    p.add_argument("--format", "-f", default="kicad_zip,fusion_lbr,altium_lia,step_3d",
                   help=f"Comma-separated formats from: {', '.join(FORMATS.keys())}")
    p.add_argument("--out", "-o", default="./chipdocs_downloads", help="Output directory")
    args = p.parse_args()

    req = urllib.request.Request(
        f"{BASE}/api/v1/components/search?q={urllib.parse.quote(args.query)}&limit=1",
        headers={"User-Agent": "ChipDocs-CLI/1.0"},
    )
    data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
    comp = (data.get("components") or [None])[0]
    if not comp:
        raise SystemExit(f"Component '{args.query}' not found on chipdocs.org")

    mpn = comp["mpn"]
    pid = urllib.parse.quote(comp["lcsc_part"])
    safe = re.sub(r"[^A-Za-z0-9_.\-]+", "_", mpn).strip("_")
    os.makedirs(args.out, exist_ok=True)
    print(f"Resolved: {mpn} ({comp['lcsc_part']}) — {comp.get('canonical_manufacturer')} [{comp.get('package')}]")

    for fk in [x.strip() for x in args.format.split(",") if x.strip()]:
        if fk not in FORMATS:
            print(f"  ! Unknown format: {fk}")
            continue
        vname, ext = FORMATS[fk]
        dl_url = f"{BASE}/api/v1/assets/{pid}/cleanroom/{vname}"
        dest = os.path.join(args.out, f"{safe}{ext}")
        raw = urllib.request.urlopen(urllib.request.Request(dl_url, headers={"User-Agent": "ChipDocs-CLI/1.0"}), timeout=20).read()
        with open(dest, "wb") as f:
            f.write(raw)
        print(f"  ✓ Saved {dest} ({len(raw):,} bytes)")


if __name__ == "__main__":
    main()
