#!/usr/bin/env python3
"""vita-runlog.py -- numbers from PS Vita device logs, and a run-by-run history you can compare honestly.

It reads "SM" measure lines (written by c/shepherd_measure.h, or by your own code in the same format; anything else in the log is
ignored, and a line may carry a prefix such as a timestamp):
  SM BEGIN app=<name> build=<text>
  SM CLK when=<start|end|...> reported=<MHz> measured=<MHz> step=<MHz, 0 = not a clock step>
  SM MEM tag=<checkpoint> user_kib=<n> cdram_kib=<n> phycont_kib=<n> [largest_kib=<n>]
  SM BOOT tag=<milestone> ms=<ms since start>
  SM FRAME n=<frame> ms=<ms> [render_ms=<ms>] [gc_ms=<ms>]
  SM FRAMES window=<label> n=<count> mean_ms=.. p50_ms=.. p95_ms=.. p99_ms=.. max_ms=.. fps=..
  SM GC pause_ms=<ms>
  SM SUSP lost_ms=<ms>
  SM END result=<PASS|FAIL> [reason="..."]
Another log format can be mapped with --spec FILE.json: {"rules": [{"match": "<regex with named groups>", "kind": "CLK",
"set": {"when": "start"}}]} -- each match becomes an event of that kind whose fields are the named groups (+ "set").

Commands:
  stats LOG [--frames A:B] [--hitch-ms 50] [--built FILE]   one log: clock, result, frame times, memory, boot, GC, suspends
  add LOG... --history FILE --label VERSION [--app NAME]     append one row per log (the same log is never added twice)
  show --history FILE [--app NAME] [--last N]                the history as a table
  compare --history FILE [--app NAME] [--a LABEL] [--b LABEL]   two runs side by side (default: the last two of the app)
Honesty rules built in (from device runs that went wrong): the MEASURED clock wins over the reported one; no percentage across two
different clocks or for a run whose clock changed; a log older than --built is flagged STALE; a log with no END line is flagged.
"""
import argparse, csv, datetime, hashlib, json, os, re, statistics, sys

LINE = re.compile(r'(?:^|\s)SM ([A-Z]+)((?:\s+[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\S+))*)\s*$')
FIELD = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|\S+)')
COLS = ["label", "added", "app", "build", "log", "log_sha", "clock_reported", "clock_measured", "clock_note", "result", "frames",
        "mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms", "fps", "render_ms", "gc_worst_ms", "gc_total_ms", "user_free_min_kib",
        "cdram_free_min_kib", "phycont_free_min_kib", "largest_min_kib", "boot", "susp_ms"]
LOWER_BETTER = {"mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms", "render_ms", "gc_worst_ms", "gc_total_ms", "susp_ms"}
HIGHER_BETTER = {"fps", "user_free_min_kib", "cdram_free_min_kib", "phycont_free_min_kib", "largest_min_kib"}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_events(path, spec=None):
    rules = []
    if spec:
        with open(spec, encoding="utf-8") as f:
            for r in json.load(f).get("rules", []):
                rules.append((re.compile(r["match"]), r["kind"], r.get("set", {})))
    events = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = LINE.search(line)
            if m:
                ev = {k: v.strip('"') for k, v in FIELD.findall(m.group(2))}
                ev["kind"] = m.group(1)
                events.append(ev)
                continue
            for rx, kind, const in rules:
                m = rx.search(line)
                if m:
                    ev = {k: v for k, v in m.groupdict().items() if v is not None}
                    ev.update(const)
                    ev["kind"] = kind
                    events.append(ev)
                    break
    return events


def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, int(round(p / 100.0 * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def summarize(path, events, frames_range=None, hitch_ms=50.0):
    s = {"log": path, "warnings": []}
    begin = next((e for e in events if e["kind"] == "BEGIN"), {})
    s["app"], s["build"] = begin.get("app", ""), begin.get("build", "")
    # clock: the measured clock step wins; note a difference from the report or a change during the run
    clk = [e for e in events if e["kind"] == "CLK"]
    reported = [int(num(e["reported"])) for e in clk if num(e.get("reported")) is not None]
    steps = [int(num(e.get("step")) or 0) or int(num(e.get("measured")) or 0) for e in clk if num(e.get("measured")) is not None]
    s["clock_reported"] = reported[-1] if reported else None
    s["clock_measured"] = steps[-1] if steps else None
    notes = []
    if steps and len(set(steps)) > 1:
        notes.append("changed " + ">".join(str(x) for x in dict.fromkeys(steps)))
    if steps and reported and steps[-1] != reported[-1]:
        notes.append("DIFFER (measured %d, reported %d: a plugin set the clock outside scePower?)" % (steps[-1], reported[-1]))
    if not steps:
        s["warnings"].append("no measured clock (SM CLK measured=...): the reported clock can be wrong with plugins (GT-011)")
    s["clock_note"] = "; ".join(notes)
    end = [e for e in events if e["kind"] == "END"]
    s["result"] = end[-1].get("result", "") if end else ""
    if not end:
        s["warnings"].append("no END line: the app crashed, was closed, or is still running -- look for a psp2core dump")
    elif end[-1].get("reason"):
        s["result_reason"] = end[-1]["reason"]
    # frames
    fr = [e for e in events if e["kind"] == "FRAME" and num(e.get("ms")) is not None]
    if frames_range:
        a, b = frames_range
        fr = [e for e in fr if a <= (num(e.get("n")) or -1) <= b]
    summ = [e for e in events if e["kind"] == "FRAMES"]
    if summ and not frames_range and int(num(summ[-1].get("n")) or 0) > len(fr):
        fr_used = []   # the summary covers more frames than the per-frame lines (often only a few are logged): use it
    else:
        fr_used = fr
    if fr_used:
        fr = fr_used
        ms = [num(e["ms"]) for e in fr]
        srt = sorted(ms)
        s["frames"] = len(ms)
        s["mean_ms"] = statistics.fmean(ms) if hasattr(statistics, "fmean") else sum(ms) / len(ms)
        s["p50_ms"], s["p95_ms"], s["p99_ms"], s["max_ms"] = pct(srt, 50), pct(srt, 95), pct(srt, 99), srt[-1]
        s["fps"] = 1000.0 / s["mean_ms"] if s["mean_ms"] else None
        rend = [num(e["render_ms"]) for e in fr if num(e.get("render_ms")) is not None]
        s["render_ms"] = sum(rend) / len(rend) if rend else None
        s["hitches"] = sorted(((num(e["ms"]), e.get("n", "?")) for e in fr if num(e["ms"]) > hitch_ms), reverse=True)
    else:
        summ = [e for e in events if e["kind"] == "FRAMES"]
        if summ:
            last = summ[-1]
            s["frames"] = int(num(last.get("n")) or 0)
            for k in ("mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms", "fps"):
                s[k] = num(last.get(k))
            s["frames_window"] = last.get("window", "")
    s["frame_windows"] = [e for e in events if e["kind"] == "FRAMES"]
    # GC: explicit GC lines, else the per-frame gc_ms
    gc = [num(e["pause_ms"]) for e in events if e["kind"] == "GC" and num(e.get("pause_ms")) is not None]
    if not gc:
        gc = [num(e["gc_ms"]) for e in fr if num(e.get("gc_ms"))]
    s["gc_worst_ms"] = max(gc) if gc else None
    s["gc_total_ms"] = sum(gc) if gc else None
    s["gc_count"] = len(gc)
    # memory: the lowest free value of each pool, with the checkpoint it happened at
    mem = [e for e in events if e["kind"] == "MEM"]
    for key, col in (("user_kib", "user_free_min_kib"), ("cdram_kib", "cdram_free_min_kib"), ("phycont_kib", "phycont_free_min_kib"),
                     ("largest_kib", "largest_min_kib")):
        vals = [(num(e[key]), e.get("tag", "?")) for e in mem if num(e.get(key)) is not None]
        if vals:
            v, tag = min(vals)
            s[col], s[col + "_at"] = int(v), tag
        else:
            s[col] = None
    s["mem_checkpoints"] = mem
    s["boot"] = ";".join("%s=%s" % (e.get("tag", "?"), e.get("ms", "?")) for e in events if e["kind"] == "BOOT")
    susp = [num(e["lost_ms"]) for e in events if e["kind"] == "SUSP" and num(e.get("lost_ms")) is not None]
    s["susp_ms"] = sum(susp) if susp else None
    return s


def fmt(v, nd=2):
    if v is None or v == "":
        return "-"
    if isinstance(v, float):
        return ("%." + str(nd) + "f") % v
    return str(v)


def cmd_stats(a):
    rng = None
    if a.frames:
        x, y = a.frames.split(":")
        rng = (float(x or 0), float(y or 1e18))
    events = parse_events(a.log, a.spec)
    s = summarize(a.log, events, rng, a.hitch_ms)
    if a.built and os.path.exists(a.built) and os.path.getmtime(a.log) < os.path.getmtime(a.built):
        s["warnings"].append("STALE: this log is older than %s -- it is not from this build" % a.built)
    if not events:
        s["warnings"].append("no SM lines found (wrong file, or a different log format: see --spec)")
    if a.json:
        print(json.dumps(s, indent=2, default=str))
        return 0
    print("%s  app=%s build=%s" % (a.log, s["app"] or "-", s["build"] or "-"))
    print("  clock     measured %s MHz, reported %s MHz %s" % (fmt(s["clock_measured"]), fmt(s["clock_reported"]),
                                                           ("(" + s["clock_note"] + ")") if s["clock_note"] else ""))
    print("  result    %s%s" % (s["result"] or "-", (" -- " + s["result_reason"]) if s.get("result_reason") else ""))
    if s.get("frames"):
        print("  frames    n=%s mean %s ms (%s fps)  p50 %s  p95 %s  p99 %s  max %s%s" % (
            s["frames"], fmt(s.get("mean_ms")), fmt(s.get("fps"), 1), fmt(s.get("p50_ms")), fmt(s.get("p95_ms")),
            fmt(s.get("p99_ms")), fmt(s.get("max_ms")), ("  render %s ms" % fmt(s["render_ms"])) if s.get("render_ms") else ""))
        if s.get("hitches"):
            top = ", ".join("%s ms @%s" % (fmt(v, 1), n) for v, n in s["hitches"][:5])
            print("  hitches   %d frames over %s ms: %s" % (len(s["hitches"]), fmt(a.hitch_ms, 0), top))
    for w in s["frame_windows"]:
        print("  window    %s: n=%s mean %s ms p95 %s max %s fps %s" % (w.get("window", "?"), w.get("n", "?"), w.get("mean_ms", "?"),
                                                                       w.get("p95_ms", "?"), w.get("max_ms", "?"), w.get("fps", "?")))
    if s.get("gc_count"):
        print("  gc        %d pauses, worst %s ms, total %s ms" % (s["gc_count"], fmt(s["gc_worst_ms"]), fmt(s["gc_total_ms"])))
    for col, name in (("user_free_min_kib", "user"), ("cdram_free_min_kib", "cdram"), ("phycont_free_min_kib", "phycont"),
                      ("largest_min_kib", "largest block")):
        if s.get(col) is not None:
            print("  memory    lowest free %s: %d KiB (at %s)" % (name, s[col], s[col + "_at"]))
    if s["boot"]:
        print("  boot      " + s["boot"].replace(";", "  "))
    if s.get("susp_ms"):
        print("  suspended %s ms (left out of process time: GT-004)" % fmt(s["susp_ms"], 0))
    for w in s["warnings"]:
        print("  WARN      " + w)
    return 0


def read_history(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def cmd_add(a):
    rows = read_history(a.history)
    seen = {r.get("log_sha") for r in rows}
    new = []
    for log in a.logs:
        with open(log, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()[:16]
        if sha in seen:
            print("skip %s: already in the history" % log)
            continue
        events = parse_events(log, a.spec)
        if not events:
            print("skip %s: no SM lines (see --spec)" % log)
            continue
        s = summarize(log, events)
        row = {c: "" for c in COLS}
        for c in COLS:
            if c in s and s[c] is not None:
                row[c] = fmt(s[c]) if isinstance(s[c], float) else str(s[c])
        row.update(label=a.label, added=datetime.date.today().isoformat(), log=os.path.basename(log), log_sha=sha)
        if a.app:
            row["app"] = a.app
        elif not row["app"]:
            row["app"] = os.path.splitext(os.path.basename(log))[0]
        new.append(row)
        seen.add(sha)
        print("added %s: app=%s clock=%s result=%s mean=%s ms" % (log, row["app"], row["clock_measured"] or row["clock_reported"] or "-",
                                                                  row["result"] or "-", row["mean_ms"] or "-"))
    if new:
        exists = os.path.exists(a.history)
        with open(a.history, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", extrasaction="ignore")
            if not exists:
                w.writeheader()
            w.writerows(new)
    return 0


def eff_clock(r):
    return r.get("clock_measured") or r.get("clock_reported") or ""


def cmd_show(a):
    rows = [r for r in read_history(a.history) if not a.app or r.get("app") == a.app]
    rows = rows[-a.last:] if a.last else rows
    if not rows:
        print("no runs")
        return 0
    cols = ["label", "app", "clock", "result", "frames", "mean_ms", "p95_ms", "max_ms", "fps", "user_free_min_kib", "boot"]
    table = [cols] + [[eff_clock(r) + ("*" if r.get("clock_note") else "") if c == "clock" else r.get(c, "") for c in cols] for r in rows]
    widths = [max(len(str(row[i])) for row in table) for i in range(len(cols))]
    for row in table:
        print("  ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))
    if any(r.get("clock_note") for r in rows):
        print("* clock changed during the run or differs from the reported clock (see clock_note)")
    return 0


def cmd_compare(a):
    rows = [r for r in read_history(a.history) if not a.app or r.get("app") == a.app]
    def pick(label):
        m = [r for r in rows if r.get("label") == label]
        if not m:
            raise SystemExit("no run labelled %r%s" % (label, (" for app " + a.app) if a.app else ""))
        return m[-1]
    if a.a and a.b:
        ra, rb = pick(a.a), pick(a.b)
    elif len(rows) >= 2:
        ra, rb = (pick(a.a), rows[-1]) if a.a else (rows[-2], rows[-1])
    else:
        print("need two runs to compare")
        return 1
    ca, cb = eff_clock(ra), eff_clock(rb)
    pct_ok = ca and ca == cb and not ra.get("clock_note") and not rb.get("clock_note")
    print("A = %s (%s, clock %s)   B = %s (%s, clock %s)" % (ra["label"], ra.get("app", ""), ca or "?", rb["label"], rb.get("app", ""), cb or "?"))
    if not pct_ok:
        why = "different clocks" if ca != cb else "a clock changed during a run or is unknown"
        print("NO PERCENTAGES: %s -- compare runs at the same measured clock" % why)
        same = [r for r in rows if r is not rb and eff_clock(r) == cb and not r.get("clock_note")]
        if same:
            print("  closest earlier run at clock %s: %s (%s)" % (cb, same[-1]["label"], same[-1].get("log", "")))
    if ra.get("app") != rb.get("app"):
        print("NOTE: different apps")
    for c in ["result", "frames", "mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms", "fps", "render_ms", "gc_worst_ms", "gc_total_ms",
              "user_free_min_kib", "cdram_free_min_kib", "phycont_free_min_kib", "largest_min_kib", "susp_ms"]:
        va, vb = ra.get(c, ""), rb.get(c, "")
        if not va and not vb:
            continue
        line = "  %-22s %12s %12s" % (c, va or "-", vb or "-")
        x, y = num(va), num(vb)
        if x is not None and y is not None and c in LOWER_BETTER | HIGHER_BETTER:
            d = y - x
            better = (d < 0) if c in LOWER_BETTER else (d > 0)
            line += "  %+10.2f" % d
            if pct_ok and x:
                line += "  %+7.1f%%" % (100.0 * d / x)
            if d:
                line += "  " + ("better" if better else "worse")
        print(line)
    if ra.get("boot") or rb.get("boot"):
        print("  boot  A: %s\n        B: %s" % (ra.get("boot") or "-", rb.get("boot") or "-"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="PS Vita device-log numbers and run history.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stats"); p.add_argument("log"); p.add_argument("--frames", metavar="A:B")
    p.add_argument("--hitch-ms", type=float, default=50.0); p.add_argument("--built", metavar="FILE")
    p.add_argument("--spec"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("add"); p.add_argument("logs", nargs="+"); p.add_argument("--history", required=True)
    p.add_argument("--label", required=True); p.add_argument("--app"); p.add_argument("--spec")
    p = sub.add_parser("show"); p.add_argument("--history", required=True); p.add_argument("--app"); p.add_argument("--last", type=int)
    p = sub.add_parser("compare"); p.add_argument("--history", required=True); p.add_argument("--app")
    p.add_argument("--a"); p.add_argument("--b")
    a = ap.parse_args(argv)
    try:
        return {"stats": cmd_stats, "add": cmd_add, "show": cmd_show, "compare": cmd_compare}[a.cmd](a)
    except OSError as e:
        print("vita-runlog: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
