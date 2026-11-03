#!/usr/bin/env python3
"""Tests for plugins/shepherd/tools -- run: python3 tests/test_tools.py  (Python 3.8+, standard library only).

Every check has a negative control: a tool that never fails proves nothing (the vita-check-the-checker skill). Fixtures are built
here (a synthetic ELF with vitasdk stub sections, param.sfo, VPK zips, logs, a fake memory card), so no binaries live in the repo.
Optional parts run when their tools exist: the C header's host test (cc) and a real vitasdk build of the example (arm-vita-eabi-gcc).
"""
import hashlib, json, os, shutil, struct, subprocess, sys, tempfile, unittest, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "plugins", "shepherd", "tools")
PY = sys.executable


def run(*args, cwd=None):
    p = subprocess.run(list(args), capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def tool(name, *args):
    return run(PY, os.path.join(TOOLS, name), *args)


def make_elf(path, libs):
    """A minimal ELF32 LE with .vitalink.fstubs.<lib> sections and one FUNC symbol per import; libs = {lib: [funcs]}.
    A name starting with 'var:' goes into .vitalink.vstubs.<lib> as an OBJECT."""
    sec_names = ["", ".shstrtab", ".strtab", ".symtab"]
    stub_secs = []
    for lib, fns in libs.items():
        if any(not f.startswith("var:") for f in fns):
            stub_secs.append((".vitalink.fstubs." + lib, [f for f in fns if not f.startswith("var:")], 2))
        if any(f.startswith("var:") for f in fns):
            stub_secs.append((".vitalink.vstubs." + lib, [f[4:] for f in fns if f.startswith("var:")], 1))
    sec_names += [n for n, _, _ in stub_secs]
    shstr = b"\0" + b"".join(n.encode() + b"\0" for n in sec_names[1:])
    name_off = {}
    off = 1
    for n in sec_names[1:]:
        name_off[n] = off
        off += len(n) + 1
    strtab, syms = b"\0", [struct.pack("<IIIBBH", 0, 0, 0, 0, 0, 0)]
    for idx, (sname, fns, typ) in enumerate(stub_secs):
        shndx = 4 + idx
        syms.append(struct.pack("<IIIBBH", len(strtab), 0, 0, 0, 0, shndx))   # a "$t" mapping symbol: must be ignored
        strtab += b"$t\0"
        for fn in fns:
            syms.append(struct.pack("<IIIBBH", len(strtab), 0x81000000, 16, (1 << 4) | typ, 0, shndx))
            strtab += fn.encode() + b"\0"
    symtab = b"".join(syms)
    stub_blob = b"\0" * 16
    body, offsets = b"", {}
    def add(name, blob):
        nonlocal body
        offsets[name] = 52 + len(body)
        body += blob
    add(".shstrtab", shstr); add(".strtab", strtab); add(".symtab", symtab)
    for n, _, _ in stub_secs:
        add(n, stub_blob)
    shoff = 52 + len(body)
    shdrs = [struct.pack("<IIIIIIIIII", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
    shdrs.append(struct.pack("<IIIIIIIIII", name_off[".shstrtab"], 3, 0, 0, offsets[".shstrtab"], len(shstr), 0, 0, 1, 0))
    shdrs.append(struct.pack("<IIIIIIIIII", name_off[".strtab"], 3, 0, 0, offsets[".strtab"], len(strtab), 0, 0, 1, 0))
    shdrs.append(struct.pack("<IIIIIIIIII", name_off[".symtab"], 2, 0, 0, offsets[".symtab"], len(symtab), 2, 1, 4, 16))
    for n, _, _ in stub_secs:
        shdrs.append(struct.pack("<IIIIIIIIII", name_off[n], 1, 6, 0x81000000, offsets[n], len(stub_blob), 0, 0, 4, 0))
    hdr = b"\x7fELF" + bytes([1, 1, 1, 0]) + b"\0" * 8
    hdr += struct.pack("<HHIIIIIHHHHHH", 2, 40, 1, 0, 0, shoff, 0, 52, 0, 0, 40, len(shdrs), 1)
    with open(path, "wb") as f:
        f.write(hdr + body + b"".join(shdrs))


def make_sfo(fields):
    """param.sfo from {key: str | int}."""
    keys = sorted(fields)
    key_tab, data_tab, index = b"", b"", b""
    for k in keys:
        v = fields[k]
        if isinstance(v, int):
            raw, fmt, ln, mx = struct.pack("<I", v), 0x0404, 4, 4
        else:
            b = v.encode() + b"\0"
            mx = (len(b) + 3) // 4 * 4
            raw, fmt, ln = b.ljust(mx, b"\0"), 0x0204, len(b)
        index += struct.pack("<HHIII", len(key_tab), fmt, ln, mx, len(data_tab))
        key_tab += k.encode() + b"\0"
        data_tab += raw
    key_tab = key_tab.ljust((len(key_tab) + 3) // 4 * 4, b"\0")
    key_start = 20 + len(index)
    data_start = key_start + len(key_tab)
    return b"\0PSF" + struct.pack("<IIII", 0x0101, key_start, data_start, len(keys)) + index + key_tab + data_tab


class Imports(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.elf = os.path.join(self.d, "app.elf")
        make_elf(self.elf, {"SceLibKernel": ["sceKernelExitProcess", "sceClibPrintf"], "SceNet": ["sceNetSend", "sceNetRecv",
                 "sceNetSocketClose"], "SceShaccCg": ["sceShaccCgCompileProgram"], "SceSysmem": ["sceKernelAllocMemBlockForVM"],
                 "taihen": ["taiGetModuleExportFunc"], "SceLibc": ["var:__stack_chk_guard"]})
        self.lst = os.path.join(self.d, "loaded.txt")
        with open(self.lst, "w") as f:
            f.write("# comment\nSceLibKernel\nSceSysmem\ntaihen\nSceLibc\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_lists_libraries_and_ignores_mapping_symbols(self):
        rc, out = tool("vita-imports.py", self.elf, "--json")
        self.assertEqual(rc, 0, out)
        j = json.loads(out)
        self.assertEqual(j["imports"]["SceNet"], ["sceNetRecv", "sceNetSend", "sceNetSocketClose"])
        self.assertEqual(j["imports"]["SceLibc (variables)"], ["__stack_chk_guard"])
        self.assertNotIn("$t", json.dumps(j["imports"]))

    def test_module_load_list_fails_late_libraries(self):
        rc, out = tool("vita-imports.py", self.elf, "--module-load-libs", self.lst)
        self.assertEqual(rc, 1)
        self.assertIn("FAIL [module-load-libs] SceNet", out)
        self.assertIn("FAIL [module-load-libs] SceShaccCg", out)
        self.assertNotIn("FAIL [module-load-libs] SceLibKernel", out)
        self.assertNotIn("FAIL [module-load-libs] SceLibc", out)   # variables count under their library (on the list)

    def test_module_load_list_passes_when_complete(self):   # the negative control of the test above
        with open(self.lst, "a") as f:
            f.write("SceNet\nSceShaccCg\n")
        rc, out = tool("vita-imports.py", self.elf, "--module-load-libs", self.lst)
        self.assertEqual(rc, 0, out)

    def test_forbid_presets_and_exemptions(self):
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "network")
        self.assertEqual(rc, 1); self.assertIn("FAIL [forbid network] SceNet", out)
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "network", "--allow-newlib-net")
        self.assertEqual(rc, 0, out)
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "jit")
        self.assertEqual(rc, 1); self.assertIn("sceKernelAllocMemBlockForVM", out)
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "jit", "--allow-func", "sceKernelAllocMemBlockForVM")
        self.assertEqual(rc, 0, out)
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "hooks")
        self.assertEqual(rc, 1); self.assertIn("taihen", out)
        rc, out = tool("vita-imports.py", self.elf, "--forbid", "kernel")
        self.assertEqual(rc, 0, out)

    def test_kernel_preset_catches_fordriver(self):
        elf = os.path.join(self.d, "k.elf")
        make_elf(elf, {"SceSysmemForDriver": ["ksceKernelAllocMemBlock"]})
        rc, out = tool("vita-imports.py", elf, "--forbid", "kernel")
        self.assertEqual(rc, 1, out)

    def test_not_an_elf(self):
        rc, out = tool("vita-imports.py", self.lst)
        self.assertEqual(rc, 2); self.assertIn("not an ELF", out)


class Vpk(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def vpk(self, name, sfo, extra=None, skip=()):
        p = os.path.join(self.d, name)
        with zipfile.ZipFile(p, "w") as z:
            files = {"eboot.bin": b"SCE\0", "sce_sys/param.sfo": make_sfo(sfo), "sce_sys/icon0.png": b"\x89PNG"}
            files.update(extra or {})
            for n, b in files.items():
                if n not in skip:
                    z.writestr(n, b)
        return p

    def test_good_vpk(self):
        p = self.vpk("ok.vpk", {"TITLE_ID": "ABCD00001", "TITLE": "Test", "ATTRIBUTE2": 12})
        rc, out = tool("vita-vpk-check.py", p, "--expect-title-id", "ABCD00001", "--expect-attribute2", "12")
        self.assertEqual(rc, 0, out); self.assertIn("ATTRIBUTE2", out)

    def test_bad_vpks(self):
        rc, out = tool("vita-vpk-check.py", self.vpk("a.vpk", {"TITLE_ID": "abc1", "ATTRIBUTE2": 0}), "--expect-attribute2", "12")
        self.assertEqual(rc, 1); self.assertIn("4 capital letters", out); self.assertIn("ATTRIBUTE2 is 0", out)
        rc, out = tool("vita-vpk-check.py", self.vpk("b.vpk", {"TITLE_ID": "ABCD00001"}, skip=("eboot.bin",)))
        self.assertEqual(rc, 1); self.assertIn("missing eboot.bin", out)
        rc, out = tool("vita-vpk-check.py", self.vpk("c.vpk", {"TITLE_ID": "ABCD00001"}, {"data/game.assets": b"x"}),
                       "--forbid-ext", ".assets")
        self.assertEqual(rc, 1); self.assertIn("forbidden file type", out)
        rc, out = tool("vita-vpk-check.py", self.vpk("d.vpk", {"TITLE_ID": "ABCD00001"}), "--expect-title-id", "ABCD00002")
        self.assertEqual(rc, 1)

    def test_macos_leftovers_warn_only(self):
        p = self.vpk("e.vpk", {"TITLE_ID": "ABCD00001"}, {"._eboot.bin": b"x", "data/.DS_Store": b"x"})
        rc, out = tool("vita-vpk-check.py", p)
        self.assertEqual(rc, 0, out); self.assertEqual(out.count("macOS leftover"), 2)

    def test_missing_icon_warns_only(self):
        p = self.vpk("f.vpk", {"TITLE_ID": "ABCD00001"}, skip=("sce_sys/icon0.png",))
        rc, out = tool("vita-vpk-check.py", p)
        self.assertEqual(rc, 0, out); self.assertIn("no sce_sys/icon0.png", out)

    def test_loose_sfo_and_garbage(self):
        sfo = os.path.join(self.d, "param.sfo")
        with open(sfo, "wb") as f:
            f.write(make_sfo({"TITLE_ID": "ABCD00001", "APP_VER": "01.00"}))
        rc, out = tool("vita-vpk-check.py", "--sfo", sfo, "--json")
        self.assertEqual(rc, 0, out); self.assertEqual(json.loads(out)["param_sfo"]["APP_VER"], "01.00")
        with open(sfo, "wb") as f:
            f.write(b"nope")
        rc, out = tool("vita-vpk-check.py", "--sfo", sfo)
        self.assertEqual(rc, 2)


LOG_444 = """noise before
12:00:01 SM BEGIN app=demo build=1
SM CLK when=start reported=444 measured=441 step=444
SM MEM tag=start user_kib=200000 cdram_kib=100000 phycont_kib=26000
SM BOOT tag=first_picture ms=900
SM FRAME n=1 ms=40.00
SM FRAME n=2 ms=20.00
SM FRAME n=3 ms=20.00
SM FRAME n=4 ms=120.00
SM MEM tag=menu user_kib=150000 cdram_kib=90000 phycont_kib=6000
SM END result=PASS reason="done"
"""


class Runlog(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.h = os.path.join(self.d, "hist.tsv")

    def tearDown(self):
        shutil.rmtree(self.d)

    def log(self, name, text):
        p = os.path.join(self.d, name)
        with open(p, "w") as f:
            f.write(text)
        return p

    def test_stats_numbers(self):
        rc, out = tool("vita-runlog.py", "stats", self.log("a.txt", LOG_444), "--json")
        self.assertEqual(rc, 0, out)
        s = json.loads(out)
        self.assertEqual(s["frames"], 4)
        self.assertAlmostEqual(s["mean_ms"], 50.0)
        self.assertEqual(s["max_ms"], 120.0)
        self.assertEqual(s["clock_measured"], 444)
        self.assertEqual(s["user_free_min_kib"], 150000)
        self.assertEqual(s["phycont_free_min_kib_at"], "menu")
        self.assertEqual(s["result"], "PASS")
        self.assertEqual(s["warnings"], [])

    def test_warnings(self):
        txt = "SM CLK when=start reported=444 measured=497 step=500\nSM FRAME n=1 ms=10\n"
        rc, out = tool("vita-runlog.py", "stats", self.log("b.txt", txt))
        self.assertIn("DIFFER", out); self.assertIn("no END line", out)
        rc, out = tool("vita-runlog.py", "stats", self.log("c.txt", "hello\n"))
        self.assertIn("no SM lines", out)
        built = self.log("built.vpk", "x")
        old = self.log("old.txt", LOG_444)
        os.utime(old, (1, 1))
        rc, out = tool("vita-runlog.py", "stats", old, "--built", built)
        self.assertIn("STALE", out)

    def test_history_dedupe_and_clock_honesty(self):
        a = self.log("run1.txt", LOG_444)
        b = self.log("run2.txt", LOG_444.replace("ms=120.00", "ms=60.00"))
        c = self.log("run3.txt", LOG_444.replace("measured=441 step=444", "measured=497 step=500").replace("reported=444", "reported=500"))
        for p, label in ((a, "v1"), (b, "v2"), (a, "v1-again"), (c, "v3")):
            rc, out = tool("vita-runlog.py", "add", p, "--history", self.h, "--label", label)
            self.assertEqual(rc, 0, out)
        with open(self.h) as f:
            self.assertEqual(len(f.read().strip().splitlines()), 4)   # header + 3 runs: the repeated log was skipped
        rc, out = tool("vita-runlog.py", "compare", "--history", self.h, "--a", "v1", "--b", "v2")
        self.assertIn("%", out); self.assertIn("better", out); self.assertNotIn("NO PERCENTAGES", out)
        rc, out = tool("vita-runlog.py", "compare", "--history", self.h, "--a", "v2", "--b", "v3")
        self.assertIn("NO PERCENTAGES", out); self.assertNotIn("%", out.split("NO PERCENTAGES")[1].split("\n", 1)[1])
        rc, out = tool("vita-runlog.py", "show", "--history", self.h)
        self.assertEqual(rc, 0); self.assertIn("v3", out)

    def test_spec_maps_other_formats(self):
        spec = self.log("spec.json", json.dumps({"rules": [
            {"match": r"^CPU (?P<reported>\d+)MHz timed (?P<measured>\d+)", "kind": "CLK"},
            {"match": r"^frame (?P<n>\d+) took (?P<ms>[\d.]+)ms", "kind": "FRAME"},
            {"match": r"^(?P<result>OK|ERR)$", "kind": "END"}]}))
        txt = "CPU 444MHz timed 443\nframe 1 took 30.0ms\nframe 2 took 10.0ms\nOK\n"
        rc, out = tool("vita-runlog.py", "stats", self.log("o.txt", txt), "--spec", spec, "--json")
        s = json.loads(out)
        self.assertEqual(s["frames"], 2); self.assertAlmostEqual(s["mean_ms"], 20.0); self.assertEqual(s["result"], "OK")
        self.assertEqual(s["clock_measured"], 443)


class PullLogs(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.card = os.path.join(self.d, "card")
        for sub in ("VitaShell", "app", "data/my port/logs/menu"):
            os.makedirs(os.path.join(self.card, sub))
        for rel, body in (("data/my port/measure.txt", LOG_444), ("data/my port/logs/menu/engine.log", "x"),
                          ("data/my port/._measure.txt", "junk"), ("data/my port/cache.bin", "\0" * 64),
                          ("data/psp2core-1.psp2dmp", "dump")):
            with open(os.path.join(self.card, rel), "w") as f:
                f.write(body)

    def tearDown(self):
        shutil.rmtree(self.d)

    def snapshot(self):
        out = []
        for root, dirs, files in sorted(os.walk(self.card)):
            dirs.sort()
            for n in sorted(files):
                p = os.path.join(root, n)
                with open(p, "rb") as f:
                    out.append((os.path.relpath(p, self.card), hashlib.sha256(f.read()).hexdigest()))
            out.append((os.path.relpath(root, self.card), "dir"))
        return out

    def test_copies_logs_and_never_touches_the_card(self):
        before = self.snapshot()
        dest = os.path.join(self.d, "out")
        rc, out = run("sh", os.path.join(TOOLS, "vita-pull-logs.sh"), "--card", self.card, "--data-dir", "ux0:data/my port", "--dest", dest)
        self.assertEqual(rc, 0, out)
        got = sorted(os.path.relpath(os.path.join(r, n), dest) for r, _, fs in os.walk(dest) for n in fs)
        self.assertEqual(got, ["card-manifest.txt", "coredumps/psp2core-1.psp2dmp", "logs/menu/engine.log", "measure.txt"])
        self.assertEqual(self.snapshot(), before)

    def test_refusals_leave_the_card_alone(self):
        before = self.snapshot()
        rc, out = run("sh", os.path.join(TOOLS, "vita-pull-logs.sh"), "--card", self.card, "--data-dir", "data/my port",
                      "--dest", os.path.join(self.card, "data", "out", "deeper"))
        self.assertEqual(rc, 1); self.assertIn("on the card", out)
        os.makedirs(os.path.join(self.d, "cart", "app")); os.makedirs(os.path.join(self.d, "cart", "gc"))
        os.makedirs(os.path.join(self.d, "cart", "data"))
        rc, out = run("sh", os.path.join(TOOLS, "vita-pull-logs.sh"), "--card", os.path.join(self.d, "cart"), "--data-dir", "data/x")
        self.assertEqual(rc, 1); self.assertIn("does not look like", out)
        self.assertEqual(self.snapshot(), before)


class MeasureHeader(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc"), "no C compiler")
    def test_host_run_matches_known_numbers(self):
        d = tempfile.mkdtemp()
        try:
            exe = os.path.join(d, "host_test")
            rc, out = run("cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-O1", os.path.join(ROOT, "tests", "c", "host_test.c"), "-o", exe)
            self.assertEqual(rc, 0, out)
            rc, out = run(exe)
            self.assertEqual(rc, 0, out)
            log = os.path.join(d, "out.txt")
            with open(log, "w") as f:
                f.write(out)
            self.assertIn("SM BEGIN app=host_test build=t_1", out)          # space and quote cleaned
            self.assertIn('reason="all \'good\' next"', out)
            rc, js = tool("vita-runlog.py", "stats", log, "--json")
            s = json.loads(js)
            self.assertEqual(s["clock_measured"], 444)
            self.assertEqual(s["frames"], 100)
            self.assertAlmostEqual(s["mean_ms"], 17.83)
            self.assertAlmostEqual(s["p99_ms"], 50.0)
            self.assertAlmostEqual(s["max_ms"], 100.0)
            self.assertEqual(s["susp_ms"], 2500)
            self.assertEqual(s["largest_min_kib"], 4096)
            self.assertEqual(s["boot"], "first_picture=1238")
        finally:
            shutil.rmtree(d)

    @unittest.skipUnless(shutil.which("arm-vita-eabi-gcc"), "no vitasdk")
    def test_vitasdk_build_of_the_example(self):
        d = tempfile.mkdtemp()
        try:
            elf = os.path.join(d, "ex.elf")
            rc, out = run("arm-vita-eabi-gcc", "-O2", "-Wall", "-Wextra", "-Werror", "-Wl,-q",
                          os.path.join(TOOLS, "c", "measure_example.c"), "-o", elf, "-lSceRtc_stub", "-lScePower_stub")
            self.assertEqual(rc, 0, out)
            rc, out = tool("vita-imports.py", elf, "--json")
            imp = json.loads(out)["imports"]
            for lib in ("SceRtcUser", "ScePower", "SceSysmem", "SceLibKernel"):
                self.assertIn(lib, imp)
            # vitasdk's newlib brings SceNet into every program (GT-014): fine for an eboot, refused for a module
            self.assertEqual(sorted(imp.get("SceNet", [])), ["sceNetRecv", "sceNetSend", "sceNetSocketClose"])
            rc, _ = tool("vita-imports.py", elf, "--module-load-libs", os.path.join(TOOLS, "module-load-libs.example.txt"))
            self.assertEqual(rc, 1)
            rc, out = tool("vita-imports.py", elf, "--forbid", "network", "--allow-newlib-net", "--forbid", "kernel")
            self.assertEqual(rc, 0, out)
        finally:
            shutil.rmtree(d)


class ScrubLog(unittest.TestCase):
    SAMPLE = ("boot 97.9 s idle 36.97 ms clk arm 444 bus 222 gpu 222 MHz err 0x8002D003 v1.2.3.4\n"
              "log dir /" + "Users/someone/vita/logs/run.txt on /" + "Volumes/Big Drive/x\n"
              "C:\\Users\\someone\\AppData\\x  /home/someone/y\n"
              "mail me@" + "example.org from 10.0.0.42 and 8.8.8.8 doc 192.0.2.7 local 127.0.0.1\n"
              "mac 00:1A:2B:3C:4D:5E psid 0123456789abcdef0123456789ABCDEF steam 76561198000000001\n"
              "account: lambfan99 user=foo\n")

    def test_scrubs_private_and_keeps_numbers(self):
        d = tempfile.mkdtemp()
        try:
            src = os.path.join(d, "run.txt")
            with open(src, "w") as f:
                f.write(self.SAMPLE)
            rc, out = tool("vita-scrub-log.py", src)
            self.assertEqual(rc, 0, out)
            t = open(os.path.join(d, "run.scrubbed.txt")).read()
            for gone in ("someone", "Big Drive", "example.org", "10.0.0.42", "8.8.8.8", "00:1A:2B", "0123456789abcdef",
                         "76561198000000001", "lambfan99", "foo"):
                self.assertNotIn(gone, t, gone)
            for kept in ("97.9 s", "36.97 ms", "444", "0x8002D003", "v1.2.3.4", "192.0.2.7", "127.0.0.1"):
                self.assertIn(kept, t, kept)
            self.assertEqual(open(src).read(), self.SAMPLE)         # the input is never changed
            rc, out = tool("vita-scrub-log.py", "--check", os.path.join(d, "run.scrubbed.txt"))
            self.assertEqual(rc, 0, out)
        finally:
            shutil.rmtree(d)

    def test_check_fails_on_unscrubbed(self):                       # negative control: --check must catch the raw file
        d = tempfile.mkdtemp()
        try:
            src = os.path.join(d, "run.txt")
            with open(src, "w") as f:
                f.write(self.SAMPLE)
            rc, out = tool("vita-scrub-log.py", "--check", src)
            self.assertEqual(rc, 1, out)
            rc, out = tool("vita-scrub-log.py", src, src)            # refuses to overwrite its input
            self.assertEqual(rc, 2, out)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
