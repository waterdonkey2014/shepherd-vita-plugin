# Idea catalog: power, clocks and platform (PWR)

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| PWR-001 | Default to 500 MHz where a plugin profile allows it; show the measured clock; fall back to 444 quietly | EXPERIMENTAL | yes | apps can't request 500 themselves (FA-004); plugins export no user API |
| PWR-002 | Keep one measurement app at a fixed clock for history | VERIFIED (method) | -- | |
| PWR-003 | Performance / Battery-saver modes (locked rates, clocks, preloading budgets; same graphics) | THEORETICAL | yes | battery measured per mode over long runs |
| PWR-004 | Idle power saving: an identical frame + no input -> skip GPU work and step the clock down | THEORETICAL | yes | |
| PWR-005 | Freeze drawing when the system dims the screen; logic, audio, animation events keep running | THEORETICAL | yes | needs the dim signal -- a 5 s power tick that blocks dimming must be revisited |
| PWR-006 | Suspend detection by RTC minus process time; re-raise clocks after standby | EXPERIMENTAL | yes | GT-004 |
| PWR-007 | Use the 4th core when unlocked, three otherwise | VERIFIED | yes | VH-002 |
| PWR-008 | Real model / firmware detection through SceVshBridge | VERIFIED | -- | VH-011 |
| PWR-009 | Save backups with read-back verification and a restore option | VERIFIED | yes | TR-011 |
| PWR-010 | Rear touch corners as L2 / R2 / L3 / R3 | VERIFIED | -- | TR-011 |
| PWR-011 | Player-side: a reputable A1 / A2 microSD on an SD2Vita adapter | THEORETICAL | yes | the card slot caps speed well below a PC's; the adapter's quality matters; measure with a read test |
| PWR-012 | Player-side: format the microSD with large clusters | THEORETICAL | yes | fewer lookups for big files |
| PWR-013 | Player-side A/B: Wi-Fi off / suspended apps closed during play | THEORETICAL | yes | they may take CPU time and memory from the borrowed 4th core |
| PWR-014 | Player-side: a PS TV for TV play and up to four pads | THEORETICAL | yes | local co-op route |
