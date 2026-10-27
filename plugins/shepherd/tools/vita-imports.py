#!/usr/bin/env python3
"""vita-imports.py -- list and check what a PS Vita ELF imports, before it reaches a device.

Reads the unstripped ELF that the vitasdk linker writes (the input of vita-elf-create, e.g. build/myapp.elf), not eboot.bin.
Imports are the stub sections the linker creates: .vitalink.fstubs.<Library> (functions) and .vitalink.vstubs.<Library> (variables).
Pure Python 3 standard library; no vitasdk needed to run it.

Checks (each optional; any violation -> exit 1):
  --module-load-libs FILE   every imported library must be on this list (one per line, # comments). Use it for a MODULE loaded with
                            sceKernelLoadStartModule: such a module may import only libraries already loaded in the process, or the
                            load fails with 0x8002D003 (MODULEMGR_NO_LIB). An eboot does not have this limit. (knowledge base GT-001)
  --allow-libs FILE         every imported library must be on this list (a general allow-list, e.g. a network-free app)
  --forbid PRESET           network | kernel | jit | hooks (repeatable; see PRESETS below)
  --allow-func NAME         exempt one function from --forbid (repeatable), e.g. a JIT app's own ForVM calls
  --allow-newlib-net        exempt the three SceNet imports vitasdk's newlib adds to every program (sceNetRecv, sceNetSend,
                            sceNetSocketClose) from --forbid network (not from --module-load-libs: a module still can't import them)
Output: a table by library (default), --funcs to list every function, --json for machine-readable output.
Exit codes: 0 ok, 1 a check failed, 2 the file could not be read as a 32-bit ARM ELF with vitasdk stubs.

usage: vita-imports.py ELF [--funcs] [--json] [--module-load-libs FILE] [--allow-libs FILE] [--forbid PRESET]... [--allow-func NAME]...
"""
import argparse, json, struct, sys

FSTUBS, VSTUBS = ".vitalink.fstubs.", ".vitalink.vstubs."

# Library -> note. Only facts verified on a device (see the knowledge base); other libraries are just listed.
NOTES = {
    "SceShaccCg": "libshacccg.suprx: users extract it themselves (GT-006); it is loaded late (e.g. by the shader-compiler wrapper), "
                  "so a module loaded with sceKernelLoadStartModule may not import it -- bind it at first use (GT-001)",
    "SceNet": "loaded only after sceSysmoduleLoadModule(SCE_SYSMODULE_NET); a module may not import it before that (GT-001). "
              "vitasdk's newlib imports sceNetRecv / sceNetSend (libc syscalls.o) and sceNetSocketClose (libc io.o) in EVERY program, "
              "for socket-aware read / write / close, even with no networking (GT-014): harmless in an eboot, fatal in a module",
    "SceNgs": "loaded at run time with sceSysmoduleLoadModule(SCE_SYSMODULE_NGS); not available to a module before that",
    "kubridge": "needs the kubridge kernel plugin installed on the user's Vita",
}

NEWLIB_NET = {"sceNetRecv", "sceNetSend", "sceNetSocketClose"}   # vitasdk newlib, every program (GT-014)

PRESETS = {
    "network": ("libraries for networking (an offline app should import none)",
                lambda lib, fn: lib.startswith(("SceNet", "SceHttp", "SceSsl", "SceNp", "SceLibSsl"))),
    "kernel": ("kernel-only libraries (*ForDriver / *ForKernel): a user app cannot import them",
               lambda lib, fn: lib.endswith(("ForDriver", "ForKernel"))),
    "jit": ("run-time code memory (ForVM / VM domains): only a JIT should import these (knowledge base VH-008)",
            lambda lib, fn: fn is not None and ("ForVM" in fn or "VMDomain" in fn)),
    "hooks": ("hooking frameworks (taiHEN, kubridge): they tie the app to the user's plugin setup",
              lambda lib, fn: lib in ("taihen", "kubridge")),
}


class ElfError(Exception):
    pass


def read_imports(path):
    """-> {library: set(function or variable names)}; variables are listed under '<lib> (variables)'."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"\x7fELF":
        raise ElfError("not an ELF file (did you pass eboot.bin? use the linker's .elf, before vita-elf-create)")
    if data[4] != 1 or data[5] != 1:
        raise ElfError("not a 32-bit little-endian ELF")
    (e_shoff,) = struct.unpack_from("<I", data, 0x20)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x2E)
    if not e_shoff or not e_shnum:
        raise ElfError("no section headers (stripped?)")
    secs = []
    for i in range(e_shnum):
        secs.append(struct.unpack_from("<IIIIIIIIII", data, e_shoff + i * e_shentsize))
    def sec_data(s):
        return data[s[4]:s[4] + s[5]]
    shstr = sec_data(secs[e_shstrndx])
    def cstr(tab, off):
        end = tab.find(b"\0", off)
        return tab[off:end if end >= 0 else len(tab)].decode("utf-8", "replace")
    names = [cstr(shstr, s[0]) for s in secs]
    imports = {}
    for name in names:   # libraries whose stubs section exists, even if no symbol is named (rare)
        if name.startswith(FSTUBS):
            imports.setdefault(name[len(FSTUBS):], set())
        elif name.startswith(VSTUBS):
            imports.setdefault(name[len(VSTUBS):] + " (variables)", set())
    symtabs = [s for s in secs if s[1] == 2]   # SHT_SYMTAB
    if not symtabs:
        if not imports:
            raise ElfError("no symbol table and no .vitalink stub sections: is this the linker's ELF from a vitasdk build?")
        return imports
    st = symtabs[0]
    strtab = sec_data(secs[st[6]])   # sh_link -> string table
    entsize = st[9] or 16
    blob = sec_data(st)
    for off in range(0, len(blob) - entsize + 1, entsize):
        st_name, st_value, st_size, st_info, st_other, st_shndx = struct.unpack_from("<IIIBBH", blob, off)
        if st_shndx == 0 or st_shndx >= len(names):
            continue
        sym = cstr(strtab, st_name)
        if not sym or sym.startswith("$"):   # $a / $t / $d mapping symbols
            continue
        sec = names[st_shndx]
        typ = st_info & 0xF   # 0 NOTYPE, 1 OBJECT, 2 FUNC
        if sec.startswith(FSTUBS) and typ in (0, 2):
            imports.setdefault(sec[len(FSTUBS):], set()).add(sym)
        elif sec.startswith(VSTUBS):
            imports.setdefault(sec[len(VSTUBS):] + " (variables)", set()).add(sym)
    if not imports:
        raise ElfError("no .vitalink stub sections: is this the linker's ELF from a vitasdk build?")
    return imports


def read_list(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line)
    return out


def base_lib(lib):
    return lib[:-len(" (variables)")] if lib.endswith(" (variables)") else lib


def main(argv=None):
    ap = argparse.ArgumentParser(description="List and check a PS Vita ELF's imports (vitasdk stub sections).")
    ap.add_argument("elf")
    ap.add_argument("--funcs", action="store_true", help="list every imported function / variable")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--module-load-libs", metavar="FILE", help="libraries loaded when this module is loaded (GT-001)")
    ap.add_argument("--allow-libs", metavar="FILE", help="general allow-list of libraries")
    ap.add_argument("--forbid", action="append", default=[], choices=sorted(PRESETS), help="forbidden preset (repeatable)")
    ap.add_argument("--allow-func", action="append", default=[], metavar="NAME", help="exempt a function from --forbid")
    ap.add_argument("--allow-newlib-net", action="store_true", help="exempt newlib's three SceNet imports from --forbid network")
    a = ap.parse_args(argv)

    try:
        imports = read_imports(a.elf)
    except (OSError, ElfError, struct.error) as e:
        print(f"vita-imports: {a.elf}: {e}", file=sys.stderr)
        return 2

    problems = []
    if a.module_load_libs:
        loaded = set(read_list(a.module_load_libs))
        for lib in sorted(imports):
            if base_lib(lib) not in loaded:
                problems.append({"check": "module-load-libs", "library": base_lib(lib),
                                 "why": "not loaded when the module loads: sceKernelLoadStartModule would fail with 0x8002D003 "
                                        "(MODULEMGR_NO_LIB); bind it at first use (taiGetModuleExportFunc) or load it first (GT-001)",
                                 "functions": sorted(imports[lib])})
    if a.allow_libs:
        allowed = set(read_list(a.allow_libs))
        for lib in sorted(imports):
            if base_lib(lib) not in allowed:
                problems.append({"check": "allow-libs", "library": base_lib(lib), "why": "not on the allow-list",
                                 "functions": sorted(imports[lib])})
    exempt = set(a.allow_func)
    for p in a.forbid:
        desc, rule = PRESETS[p]
        ex = exempt | (NEWLIB_NET if p == "network" and a.allow_newlib_net else set())
        for lib in sorted(imports):
            bl = base_lib(lib)
            fns = sorted(imports[lib] - ex)
            if rule(bl, None):   # a library-level rule: every (non-exempt) import of the library
                hits = fns if imports[lib] else ["(library)"]
            else:
                hits = [fn for fn in fns if rule(bl, fn)]
            if hits:
                problems.append({"check": f"forbid {p}", "library": bl, "why": desc, "functions": hits})

    notes = {base_lib(l): NOTES[base_lib(l)] for l in imports if base_lib(l) in NOTES}
    if a.json:
        print(json.dumps({"elf": a.elf, "imports": {k: sorted(v) for k, v in sorted(imports.items())},
                          "notes": notes, "problems": problems, "ok": not problems}, indent=2))
        return 1 if problems else 0

    width = max(len(k) for k in imports)
    print(f"{a.elf}: {len(imports)} libraries, {sum(len(v) for v in imports.values())} imports")
    for lib in sorted(imports, key=str.lower):
        print(f"  {lib:<{width}}  {len(imports[lib]):4d}")
        if a.funcs:
            for fn in sorted(imports[lib]):
                print(f"      {fn}")
    for lib, note in sorted(notes.items()):
        print(f"note {lib}: {note}")
    for p in problems:
        shown = ", ".join(p["functions"][:6]) + (" ..." if len(p["functions"]) > 6 else "")
        print(f"FAIL [{p['check']}] {p['library']}: {p['why']}  ({shown})")
    print("imports: " + ("FAIL" if problems else "ok"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
