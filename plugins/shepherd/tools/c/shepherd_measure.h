/* shepherd_measure.h -- honest measurement lines for PS Vita apps (part of the Shepherd plugin, MIT licence).
 *
 * Writes one greppable "SM ..." line per measurement, the format tools/vita-runlog.py reads:
 *   SM BEGIN app=<name> build=<text>
 *   SM CLK when=<text> reported=<MHz> measured=<MHz> step=<MHz>     the ARM clock MEASURED, not only reported (knowledge base VH-001)
 *   SM MEM tag=<text> user_kib=<n> cdram_kib=<n> phycont_kib=<n> [largest_kib=<n>]
 *   SM BOOT tag=<text> ms=<ms since process start>
 *   SM FRAME n=<frame> ms=<ms> render_ms=<ms> gc_ms=<ms>             optional, one per frame (costs a card write each)
 *   SM FRAMES window=<text> n=.. mean_ms=.. p50_ms=.. p95_ms=.. p99_ms=.. max_ms=.. fps=..
 *   SM GC pause_ms=<ms>
 *   SM SUSP lost_ms=<ms>                                              time spent suspended (GT-004)
 *   SM END result=<PASS|FAIL> reason="<text>"
 *
 * Use: in ONE .c file
 *     #define SHEPHERD_MEASURE_IMPLEMENTATION
 *     #include "shepherd_measure.h"
 * and include it plainly elsewhere. Link: -lSceRtc_stub -lScePower_stub (plus the default vitasdk libraries).
 *
 *     sm_init("myport", "v0.3", "ux0:data/myport/measure.txt");
 *     sm_log_clock("start");  sm_log_mem("start", -1);
 *     ... sm_log_boot("first_picture"); ...
 *     per frame: sm_frame_begin(); ...; sm_frame_end(render_us, gc_us, 0); sm_suspend_check();
 *     every few seconds or at the end of a test window: sm_log_frames("menu-idle"); sm_frames_reset();
 *     sm_log_clock("end"); sm_end(1, "done");
 *
 * Notes
 *  - Each line is written to the file with its own sceIoWrite, so a crash keeps every line before it. Per-frame lines cost a card
 *    write each: use the FRAMES summary for long runs.
 *  - The measured clock: 64 dependent adds per loop pass run at one add per cycle on the Cortex-A9, so cycles / microseconds = MHz
 *    (best of 4 short runs, ~1-2 % low from the loop's branch). It sees a clock a plugin set outside scePower, which
 *    scePowerGetArmClockFrequency can miss (GT-011). Under an emulator the figure means nothing.
 *  - Not thread-safe by default: call from one thread, or define SM_LOCK() / SM_UNLOCK() before the implementation.
 *  - Redirect output: define SM_WRITE(line, len) before the implementation (default: the log file + optional sceClibPrintf with
 *    SM_ALSO_PRINTF).
 *  - Off the Vita (host tests), the system calls are declared here and must be provided by the test. */
#ifndef SHEPHERD_MEASURE_H
#define SHEPHERD_MEASURE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifndef SM_FRAME_RING
#define SM_FRAME_RING 512                 /* frames kept for the FRAMES summary */
#endif
#ifndef SM_SUSP_MIN_US
#define SM_SUSP_MIN_US 500000             /* a gap between RTC and process time above this counts as a suspension */
#endif

void     sm_init (const char *app, const char *build, const char *log_path);   /* log_path NULL: no file */
void     sm_line (const char *line);                                          /* write one raw line (adds the newline) */
int      sm_clock_measured_mhz (void);
int      sm_clock_step (int mhz);                                             /* the Vita clock step it is, or 0 */
void     sm_log_clock (const char *when);
void     sm_log_mem (const char *tag, long largest_kib);                      /* largest_kib < 0: not known */
void     sm_log_boot (const char *tag);
void     sm_frame_begin (void);
void     sm_frame_end (uint32_t render_us, uint32_t gc_us, int log_each);
void     sm_log_frames (const char *window);
void     sm_frames_reset (void);
long     sm_suspend_check (void);                                             /* ms lost to a suspension since the last call */
void     sm_log_gc (uint32_t pause_us);
void     sm_end (int pass, const char *reason);
uint64_t sm_ms_since_start (void);

#ifdef __cplusplus
}
#endif
#endif /* SHEPHERD_MEASURE_H */

/* ------------------------------------------------------------------------------------------------------------------------------- */
#ifdef SHEPHERD_MEASURE_IMPLEMENTATION
#ifndef SHEPHERD_MEASURE_IMPLEMENTED
#define SHEPHERD_MEASURE_IMPLEMENTED

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__vita__)
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/sysmem.h>
#include <psp2/kernel/clib.h>
#include <psp2/io/fcntl.h>
#include <psp2/power.h>
#include <psp2/rtc.h>
#else   /* host tests: the same calls, provided by the test */
typedef int SceUID;
typedef struct SceKernelFreeMemorySizeInfo { int size, size_user, size_cdram, size_phycont; } SceKernelFreeMemorySizeInfo;
typedef struct SceRtcTick { uint64_t tick; } SceRtcTick;
uint64_t sceKernelGetProcessTimeWide (void);
int sceKernelGetFreeMemorySize (SceKernelFreeMemorySizeInfo *info);
int scePowerGetArmClockFrequency (void);
int sceRtcGetCurrentTick (SceRtcTick *tick);
SceUID sceIoOpen (const char *file, int flags, int mode);
int sceIoWrite (SceUID fd, const void *data, unsigned size);
int sceIoClose (SceUID fd);
int sceClibPrintf (const char *fmt, ...);
#define SCE_O_WRONLY 0x0002
#define SCE_O_CREAT 0x0200
#define SCE_O_TRUNC 0x0400
#endif

#ifndef SM_LOCK
#define SM_LOCK() ((void) 0)
#define SM_UNLOCK() ((void) 0)
#endif

static SceUID   sm__fd = -1;
static uint64_t sm__rtc_prev, sm__proc_prev, sm__frame_t0;
static uint32_t sm__ring [SM_FRAME_RING], sm__sorted [SM_FRAME_RING];
static uint32_t sm__n, sm__frame_no;
static uint64_t sm__render_sum, sm__gc_sum;

static void sm__write (const char *line, unsigned len)
{
#ifdef SM_WRITE
	SM_WRITE (line, len);
#else
	if (sm__fd >= 0)
		sceIoWrite (sm__fd, line, len);
#ifdef SM_ALSO_PRINTF
	sceClibPrintf ("%s", line);
#endif
#endif
}

void sm_line (const char *line)
{
	char buf [320];
	int n = snprintf (buf, sizeof buf, "%s\n", line);
	if (n < 0)
		return;
	if (n >= (int) sizeof buf) {   /* keep the newline on a cut line */
		n = sizeof buf - 1;
		buf [n - 1] = '\n';
	}
	SM_LOCK ();
	sm__write (buf, (unsigned) n);
	SM_UNLOCK ();
}

/* a value safe for "key=value" parsing: whitespace and quotes become '_' */
static const char *sm__clean (char *out, size_t cap, const char *in)
{
	size_t i = 0;
	if (!in || !*in)
		in = "-";
	for (; in [i] && i + 1 < cap; i++)
		out [i] = (in [i] == ' ' || in [i] == '\t' || in [i] == '\n' || in [i] == '\r' || in [i] == '"') ? '_' : in [i];
	out [i] = 0;
	return out;
}

/* "12.34" from microseconds, without floating-point printf */
static const char *sm__ms (char *out, size_t cap, uint64_t us)
{
	snprintf (out, cap, "%lu.%02lu", (unsigned long) (us / 1000), (unsigned long) ((us % 1000) / 10));
	return out;
}

static uint64_t sm__rtc_us (void)
{
	SceRtcTick t;
	if (sceRtcGetCurrentTick (&t) < 0)
		return 0;
	return t.tick;   /* microseconds */
}

uint64_t sm_ms_since_start (void)
{
	return sceKernelGetProcessTimeWide () / 1000;   /* process time starts at the process start */
}

void sm_init (const char *app, const char *build, const char *log_path)
{
	char line [256], a [64], b [64];
	if (log_path)
		sm__fd = sceIoOpen (log_path, SCE_O_WRONLY | SCE_O_CREAT | SCE_O_TRUNC, 0666);
	sm__rtc_prev = sm__rtc_us ();
	sm__proc_prev = sceKernelGetProcessTimeWide ();
	snprintf (line, sizeof line, "SM BEGIN app=%s build=%s", sm__clean (a, sizeof a, app), sm__clean (b, sizeof b, build));
	sm_line (line);
}

static unsigned __attribute__ ((noinline)) sm__spin (unsigned n)
{
#if defined(__arm__)
	unsigned x = 0;
	__asm__ volatile ("1:\n\t"
			  ".rept 64\n\t"
			  "adds %0, %0, #1\n\t"
			  ".endr\n\t"
			  "subs %1, %1, #1\n\t"
			  "bne 1b\n\t"
			  : "+l" (x), "+l" (n) : : "cc");
	return x;
#else
	volatile unsigned x = 0;
	while (n--)
		for (int i = 0; i < 64; i++)
			x++;
	return x;
#endif
}

int sm_clock_measured_mhz (void)
{
	const unsigned n = 4096;            /* 4096 x 64 = 262,144 cycles: ~0.6 ms at 444 MHz */
	uint64_t best = ~(uint64_t) 0;
	for (int r = 0; r < 4; r++) {       /* an interrupt or a preemption only ever adds time: keep the best */
		uint64_t t0 = sceKernelGetProcessTimeWide ();
		sm__spin (n);
		uint64_t dt = sceKernelGetProcessTimeWide () - t0;
		if (dt && dt < best)
			best = dt;
	}
	return best == ~(uint64_t) 0 ? 0 : (int) ((64ull * n + best / 2) / best);
}

int sm_clock_step (int mhz)
{
	static const int steps [] = { 41, 83, 111, 166, 222, 333, 444, 500 };
	for (unsigned i = 0; i < sizeof steps / sizeof steps [0]; i++)
		if (mhz * 100 >= steps [i] * 92 && mhz * 100 <= steps [i] * 106)   /* -8 % .. +6 % */
			return steps [i];
	return 0;
}

void sm_log_clock (const char *when)
{
	char line [160], w [48];
	int m = sm_clock_measured_mhz ();
	snprintf (line, sizeof line, "SM CLK when=%s reported=%d measured=%d step=%d", sm__clean (w, sizeof w, when),
		  scePowerGetArmClockFrequency (), m, sm_clock_step (m));
	sm_line (line);
}

void sm_log_mem (const char *tag, long largest_kib)
{
	char line [200], extra [40] = "", t [64];
	SceKernelFreeMemorySizeInfo info;
	memset (&info, 0, sizeof info);
	info.size = sizeof info;
	if (sceKernelGetFreeMemorySize (&info) < 0)
		return;
	if (largest_kib >= 0)
		snprintf (extra, sizeof extra, " largest_kib=%ld", largest_kib);
	snprintf (line, sizeof line, "SM MEM tag=%s user_kib=%d cdram_kib=%d phycont_kib=%d%s", sm__clean (t, sizeof t, tag),
		  info.size_user / 1024, info.size_cdram / 1024, info.size_phycont / 1024, extra);
	sm_line (line);
}

void sm_log_boot (const char *tag)
{
	char line [128], t [64];
	snprintf (line, sizeof line, "SM BOOT tag=%s ms=%lu", sm__clean (t, sizeof t, tag), (unsigned long) sm_ms_since_start ());
	sm_line (line);
}

void sm_frame_begin (void)
{
	sm__frame_t0 = sceKernelGetProcessTimeWide ();
}

void sm_frame_end (uint32_t render_us, uint32_t gc_us, int log_each)
{
	uint64_t dt = sceKernelGetProcessTimeWide () - sm__frame_t0;
	uint32_t us = dt > 0xFFFFFFFFu ? 0xFFFFFFFFu : (uint32_t) dt;
	sm__ring [sm__n % SM_FRAME_RING] = us;
	sm__n++;
	sm__frame_no++;
	sm__render_sum += render_us;
	sm__gc_sum += gc_us;
	if (log_each) {
		char line [160], a [24], b [24], c [24];
		snprintf (line, sizeof line, "SM FRAME n=%lu ms=%s render_ms=%s gc_ms=%s", (unsigned long) sm__frame_no,
			  sm__ms (a, sizeof a, us), sm__ms (b, sizeof b, render_us), sm__ms (c, sizeof c, gc_us));
		sm_line (line);
	}
}

static int sm__cmp (const void *x, const void *y)
{
	uint32_t a = *(const uint32_t *) x, b = *(const uint32_t *) y;
	return a < b ? -1 : a > b;
}

void sm_log_frames (const char *window)
{
	uint32_t k = sm__n < SM_FRAME_RING ? sm__n : SM_FRAME_RING;
	char line [256], mean [24], p50 [24], p95 [24], p99 [24], mx [24], w [64];
	if (!k)
		return;
	uint64_t sum = 0;
	for (uint32_t i = 0; i < k; i++) {
		sm__sorted [i] = sm__ring [i];
		sum += sm__ring [i];
	}
	qsort (sm__sorted, k, sizeof sm__sorted [0], sm__cmp);
	uint64_t avg = sum / k;
	uint64_t fps10 = avg ? (10000000ull + avg / 2) / avg : 0;   /* frames per second x 10 */
	snprintf (line, sizeof line, "SM FRAMES window=%s n=%lu mean_ms=%s p50_ms=%s p95_ms=%s p99_ms=%s max_ms=%s fps=%lu.%lu",
		  sm__clean (w, sizeof w, window), (unsigned long) k, sm__ms (mean, sizeof mean, avg),
		  sm__ms (p50, sizeof p50, sm__sorted [(50 * (k - 1) + 50) / 100]),
		  sm__ms (p95, sizeof p95, sm__sorted [(95 * (k - 1) + 50) / 100]),
		  sm__ms (p99, sizeof p99, sm__sorted [(99 * (k - 1) + 50) / 100]),
		  sm__ms (mx, sizeof mx, sm__sorted [k - 1]), (unsigned long) (fps10 / 10), (unsigned long) (fps10 % 10));
	sm_line (line);
}

void sm_frames_reset (void)
{
	sm__n = 0;
	sm__render_sum = sm__gc_sum = 0;
}

long sm_suspend_check (void)
{
	uint64_t rtc = sm__rtc_us (), proc = sceKernelGetProcessTimeWide ();
	long lost_ms = 0;
	if (rtc && sm__rtc_prev) {
		uint64_t wall = rtc - sm__rtc_prev, run = proc - sm__proc_prev;
		if (wall > run && wall - run > SM_SUSP_MIN_US) {   /* process time stops while suspended; the RTC does not (GT-004) */
			char line [96];
			lost_ms = (long) ((wall - run) / 1000);
			snprintf (line, sizeof line, "SM SUSP lost_ms=%ld", lost_ms);
			sm_line (line);
		}
	}
	sm__rtc_prev = rtc;
	sm__proc_prev = proc;
	return lost_ms;
}

void sm_log_gc (uint32_t pause_us)
{
	char line [64], a [24];
	snprintf (line, sizeof line, "SM GC pause_ms=%s", sm__ms (a, sizeof a, pause_us));
	sm_line (line);
}

void sm_end (int pass, const char *reason)
{
	char line [256], r [160];
	size_t i = 0;
	for (; reason && reason [i] && i + 1 < sizeof r; i++)
		r [i] = (reason [i] == '"') ? '\'' : (reason [i] == '\n' || reason [i] == '\r') ? ' ' : reason [i];
	r [i] = 0;
	snprintf (line, sizeof line, "SM END result=%s reason=\"%s\"", pass ? "PASS" : "FAIL", r);
	sm_line (line);
	if (sm__fd >= 0) {
		sceIoClose (sm__fd);
		sm__fd = -1;
	}
}

#endif /* SHEPHERD_MEASURE_IMPLEMENTED */
#endif /* SHEPHERD_MEASURE_IMPLEMENTATION */
