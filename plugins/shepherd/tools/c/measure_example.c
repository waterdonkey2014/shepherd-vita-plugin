/* measure_example.c -- a minimal PS Vita app that writes the SM measure lines (shepherd_measure.h), for trying the tools.
 *
 * Build with vitasdk (see tools/README.md for the full commands):
 *   arm-vita-eabi-gcc -O2 -Wl,-q measure_example.c -o measure_example.elf -lSceRtc_stub -lScePower_stub
 * Run it on a Vita, copy ux0:data/sm_example/measure.txt to your computer, then:
 *   python3 vita-runlog.py stats measure.txt
 */
#define SHEPHERD_MEASURE_IMPLEMENTATION
#include "shepherd_measure.h"

#include <psp2/io/stat.h>
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/threadmgr.h>

int main (void)
{
	sceIoMkdir ("ux0:data/sm_example", 0777);
	sm_init ("sm_example", "1", "ux0:data/sm_example/measure.txt");
	sm_log_clock ("start");
	sm_log_mem ("start", -1);
	sm_log_boot ("main");

	for (int i = 0; i < 120; i++) {   /* two seconds of 60 Hz "frames": a sleep stands in for the work */
		sm_frame_begin ();
		sceKernelDelayThread (16000);
		sm_frame_end (0, 0, i < 3);   /* the first three frames also as FRAME lines */
		sm_suspend_check ();
	}
	sm_log_frames ("idle-sleep");
	sm_log_mem ("end", -1);
	sm_log_clock ("end");
	sm_end (1, "example finished");
	sceKernelExitProcess (0);
	return 0;
}
