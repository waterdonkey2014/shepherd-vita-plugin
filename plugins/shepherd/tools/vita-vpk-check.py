#!/usr/bin/env python3
"""vita-vpk-check.py -- read a VPK's param.sfo and check its contents before it goes to the card.

A VPK is a zip: eboot.bin, sce_sys/param.sfo, sce_sys/icon0.png, plus the app's files. This tool prints the param.sfo fields and the
file list with sizes, and checks (any failure -> exit 1):
  - eboot.bin and sce_sys/param.sfo are present (sce_sys/icon0.png: a warning if missing); param.sfo parses;
  - TITLE_ID is 4 capital letters + 5 digits (e.g. ABCD00001);
  - --expect-title-id ID     the TITLE_ID is exactly this (catches a build packed with the wrong id)
  - --expect-attribute2 N    ATTRIBUTE2 is N; 12 asks for the extended main-memory budget (knowledge base VH-003)
  - --forbid-ext .ext        no file with this extension (repeatable), e.g. game data that must not be redistributed
  - --max-mib N              the VPK is at most N MiB
and warns (no failure) on macOS leftovers (._* AppleDouble files, .DS_Store: GT-012) and on duplicate names.
--sfo FILE reads a loose param.sfo instead of a VPK. --json for machine-readable output.
Exit codes: 0 ok, 1 a check failed, 2 the file could not be read.

usage: vita-vpk-check.py APP.vpk [--expect-title-id ID] [--expect-attribute2 N] [--forbid-ext .ext]... [--max-mib N] [--json]
       vita-vpk-check.py --sfo param.sfo [--json]
"""
import argparse, json, os, re, struct, sys, zipfile

FMT_UTF8S, FMT_UTF8, FMT_INT32 = 0x0004, 0x0204, 0x0404


class SfoError(Exception):
    pass


def parse_sfo(blob):
    """param.sfo (PSF) -> {key: str | int}."""
    if len(blob) < 20 or blob[:4] != b"\0PSF":
        raise SfoError("not a param.sfo (no \\0PSF magic)")
    _ver, key_start, data_start, count = struct.unpack_from("<IIII", blob, 4)
    if 20 + 16 * count > len(blob) or key_start > len(blob) or data_start > len(blob):
        raise SfoError("param.sfo header points outside the file")
    out = {}
    for i in range(count):
        key_off, fmt, length, _max_len, data_off = struct.unpack_from("<HHIII", blob, 20 + 16 * i)
        k0 = key_start + key_off
        key = blob[k0:blob.index(b"\0", k0)].decode("utf-8", "replace")
        d0 = data_start + data_off
        raw = blob[d0:d0 + length]
        if fmt == FMT_INT32:
            out[key] = struct.unpack_from("<I", raw)[0] if len(raw) >= 4 else None
        elif fmt in (FMT_UTF8, FMT_UTF8S):
            out[key] = raw.split(b"\0", 1)[0].decode("utf-8", "replace")
        else:
            out[key] = raw.hex()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a PS Vita VPK (or a loose param.sfo).")
    ap.add_argument("vpk", nargs="?")
    ap.add_argument("--sfo", metavar="FILE", help="read a loose param.sfo instead of a VPK")
    ap.add_argument("--expect-title-id")
    ap.add_argument("--expect-attribute2", type=int)
    ap.add_argument("--forbid-ext", action="append", default=[])
    ap.add_argument("--max-mib", type=float)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if bool(a.vpk) == bool(a.sfo):
        ap.error("give a VPK or --sfo FILE")

    fails, warns, files = [], [], []
    try:
        if a.sfo:
            with open(a.sfo, "rb") as f:
                sfo = parse_sfo(f.read())
        else:
            with zipfile.ZipFile(a.vpk) as z:
                infos = z.infolist()
                files = [(i.filename, i.file_size) for i in infos if not i.is_dir()]
                names = [n for n, _ in files]
                for req in ("eboot.bin", "sce_sys/param.sfo"):
                    if req not in names:
                        fails.append(f"missing {req}")
                if "sce_sys/icon0.png" not in names:
                    warns.append("no sce_sys/icon0.png (the home-screen icon, 128x128 PNG)")
                sfo = parse_sfo(z.read("sce_sys/param.sfo")) if "sce_sys/param.sfo" in names else {}
    except (OSError, zipfile.BadZipFile, SfoError, struct.error, ValueError) as e:
        print(f"vita-vpk-check: {a.sfo or a.vpk}: {e}", file=sys.stderr)
        return 2

    tid = sfo.get("TITLE_ID")
    if sfo:
        if not isinstance(tid, str) or not re.fullmatch(r"[A-Z]{4}\d{5}", tid):
            fails.append(f"TITLE_ID {tid!r} is not 4 capital letters + 5 digits")
        if a.expect_title_id and tid != a.expect_title_id:
            fails.append(f"TITLE_ID is {tid}, expected {a.expect_title_id}")
        if a.expect_attribute2 is not None and sfo.get("ATTRIBUTE2") != a.expect_attribute2:
            fails.append(f"ATTRIBUTE2 is {sfo.get('ATTRIBUTE2')}, expected {a.expect_attribute2}")
    for name, _size in files:
        base = os.path.basename(name)
        if base.startswith("._") or base == ".DS_Store":
            warns.append(f"macOS leftover {name} (GT-012)")
        for ext in a.forbid_ext:
            if name.lower().endswith(ext.lower()):
                fails.append(f"forbidden file type {ext}: {name}")
    seen = set()
    for name, _size in files:
        if name in seen:
            warns.append(f"duplicate entry {name}")
        seen.add(name)
    total = sum(s for _, s in files)
    if a.max_mib is not None and a.vpk and os.path.getsize(a.vpk) > a.max_mib * 1048576:
        fails.append(f"VPK is {os.path.getsize(a.vpk) / 1048576:.1f} MiB, over {a.max_mib} MiB")

    if a.json:
        print(json.dumps({"file": a.sfo or a.vpk, "param_sfo": sfo, "files": [{"name": n, "size": s} for n, s in files],
                          "uncompressed_bytes": total, "warnings": warns, "failures": fails, "ok": not fails}, indent=2))
        return 1 if fails else 0

    print(f"{a.sfo or a.vpk}")
    for k in sorted(sfo):
        note = "  (12 = extended main-memory budget, VH-003)" if k == "ATTRIBUTE2" else ""
        print(f"  {k:<20} {sfo[k]}{note}")
    if files:
        print(f"  {len(files)} files, {total / 1048576:.2f} MiB uncompressed" + (f", {os.path.getsize(a.vpk) / 1048576:.2f} MiB packed" if a.vpk else ""))
        for name, size in sorted(files, key=lambda x: -x[1])[:15]:
            print(f"    {size / 1024:10.1f} KiB  {name}")
        if len(files) > 15:
            print(f"    ... {len(files) - 15} more")
    for w in warns:
        print(f"warn: {w}")
    for f_ in fails:
        print(f"FAIL: {f_}")
    print("vpk: " + ("FAIL" if fails else "ok"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
