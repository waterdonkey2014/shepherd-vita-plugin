/* Host test for tools/c/shepherd_measure.h: stand-ins for the Vita calls with a controlled clock, so the output is known exactly.
 * Built and run by tests/test_tools.py (cc host_test.c -o host_test && ./host_test > out.txt). */
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define SM_WRITE(line, len) fwrite ((line), 1, (len), stdout)
#define SHEPHERD_MEASURE_IMPLEMENTATION
#include "../../plugins/shepherd/tools/c/shepherd_measure.h"

static uint64_t g_proc_us, g_rtc_us = 1000000000ull, g_auto_step;

uint64_t sceKernelGetProcessTimeWide (void) { g_proc_us += g_auto_step; return g_proc_us; }
int sceKernelGetFreeMemorySize (SceKernelFreeMemorySizeInfo *info)
{
	info->size_user = 200 * 1024 * 1024;
	info->size_cdram = 40 * 1024 * 1024 + 512 * 1024;
	info->size_phycont = 26 * 1024 * 1024;
	return 0;
}
int scePowerGetArmClockFrequency (void) { return 444; }
int sceRtcGetCurrentTick (SceRtcTick *t) { t->tick = g_rtc_us; return 0; }
SceUID sceIoOpen (const char *f, int fl, int m) { (void) f; (void) fl; (void) m; return -1; }
int sceIoWrite (SceUID fd, const void *d, unsigned n) { (void) fd; (void) d; return (int) n; }
int sceIoClose (SceUID fd) { (void) fd; return 0; }
int sceClibPrintf (const char *fmt, ...) { va_list ap; va_start (ap, fmt); int r = vprintf (fmt, ap); va_end (ap); return r; }

static void advance (uint64_t proc_us, uint64_t rtc_us) { g_proc_us += proc_us; g_rtc_us += rtc_us; }

int main (void)
{
	sm_init ("host test", "t\"1", NULL);              /* the space and the quote must be cleaned */
	g_auto_step = 590;                                /* each time read advances 590 us: 262,144 cycles / 590 us = 444 MHz */
	sm_log_clock ("start");
	g_auto_step = 0;
	sm_log_mem ("start", 4096);
	advance (1234000, 1234000);
	sm_log_boot ("first_picture");
	sm_suspend_check ();
	/* 100 frames: 98 x 16.666 ms, one 50 ms, one 100 ms */
	for (int i = 0; i < 100; i++) {
		sm_frame_begin ();
		uint64_t us = i == 40 ? 50000 : i == 70 ? 100000 : 16666;
		advance (us, us);
		sm_frame_end (8000, i == 70 ? 30000 : 0, i < 2);
	}
	sm_log_frames ("idle window");
	advance (1000, 2501000);                          /* 2.5 s suspended: RTC moves, process time doesn't (GT-004) */
	sm_suspend_check ();
	sm_log_gc (12345);
	sm_end (1, "all \"good\"\nnext");
	return 0;
}
