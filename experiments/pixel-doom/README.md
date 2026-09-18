# Every pixel is a terminal

## Latest result — 56,000 real terminal windows

A fixed grid of **56,000 Foot terminals** passed all position/size checks and
completed a 10-second DOOM sample. Creation took 30.75 minutes; the minimal
geometry query took 0.335 seconds. A valid 9.77-second recording was saved.
The sampled terminal presented seven updates in that interval, with about
1.96 seconds median latency: playback remains very choppy. This is not whole
image FPS or proof of smooth playback. The 64,000 stage was not reached.

Videos:
* `~/Videos/doom-56000-terminals.mp4`: original recording.
* `~/Videos/doom-terminals-staged-progression.mp4`: approximately 48 seconds,
  eight seconds each at 40, 160, 640, 2,560, 10,240, and 56,000 terminals.
  Normal elapsed speed; count captions come from validated stage metadata.

The 56k run used `--static-grid --prestart-record --fps 10`: place a black grid,
validate it, initialize capture, then start DOOM. Terminal updates are capped
at 10 Hz; DOOM simulation speed is unchanged. Smaller clips used a 35 Hz cap,
so these are demonstrations, not matched playback benchmarks. Everything ran
in the private compositor on workspace 5. All processes are closed and the
PTY limit is restored. Nothing is committed.

`grid_clients()` reads only IDs/positions/sizes through lazy Lua window objects,
avoiding full `j/clients` metadata queries. Static validation runs before DOOM.
Captures wait for workspace visibility; interrupted samples preserve the grid
and retry. The wrapper verifies video existence/duration and kills the whole
private process group during cleanup, even if its dbus parent exited early.
See `output/static-prestarted-large/result-summary.json` for final evidence.

## Latest attempt — 40,960 terminals, screenshot timeout

The recorded attempt with all optimization flags reached **40,960 real Foot
terminal windows**. Window count, source coverage, and actual geometry checks
passed; the following optional `grim` screenshot timed out after 10 seconds and
aborted the launcher. The previous 40,960 run failed geometry instead. Neither
failure establishes a terminal capacity limit. About 11 GiB remained available.

Video: `~/Videos/doom-progressive-fast-64k-attempt.mp4` (~74 minutes).
Results: `output/progressive-fast-64000-attempt/run-summary.json`.
The last frame confirms the count, but shows scattered tile artifacts; smooth,
synchronized playback at this count is not established. Placement requests
sometimes took 3–6 seconds. Reaching 64,000 remains unproven.

Checkpoint screenshots are now nonfatal and validated stage data is saved before
capture. A subprocess regression test covers a hung capture, failed capture,
partial-file removal, and subsequent successful capture. Cleanup now kills any
remaining children in the launcher's private process group after compositor
teardown. The failed run's remaining Foot processes were removed; the temporary
PTY limit was restored to 4096. No further large run has started.

`window_events.py` continuously drains compositor events while placement blocks.
Its >9 MiB flood test passed; this run did not hit the prior event queue overflow.
`--fast-floating` enables the private, nested-only floating layout/fullscreen
lookup optimization. Both flag conditions passed 512-window color/geometry and
fullscreen/maximized/tiled transition checks, followed by a 640-terminal recorded
smoke test. Placement timing varied, so no precise fast-floating speedup is claimed.
Results: `output/resume-floating-off`, `output/resume-floating-on`, and
`output/resume-fast-smoke`.

## Fixed fine-grid layout and combined placement

The 40,960-terminal run failed its geometry checkpoint: a small reproduction
showed Foot enforcing a three-pixel minimum height with our one-pixel font.
`--host-size 1280x800` fixes the disposable host dimensions; integer scaling
produces a 960x600 mosaic with 3x3 windows at the native 320x200 target. Runs
above 10,240 reject smaller hosts and exercise the minimum size before creation.
Failed geometry checks now save expected and actual positions/sizes.

`--combined-geometry` enables the opt-in private
`hyprland-combined-geometry.patch` dispatcher, applying move and resize together.
It accepts only floating, non-X11 pixel-doom windows in the nested-only binary.
Three paired tests on 512 static Foot windows (131,072 placements per trial):
mean placement time 2.305 -> 1.611 s; compositor CPU 2.267 -> 1.583 s,
about 30% lower for both. This is a placement microbenchmark, not FPS or total
startup. All 512 final 3x3 tile colors/positions passed, ordinary windows were
rejected, and a 640-terminal progressive recording passed with both new options.
Results: `output/combined-geometry-benchmark/` and `output/combined-fixed-smoke/`.


## Latest recording and rule-update optimization

The latest large attempt reached 25,504 allocated regions (25,480 last completed
placement; 25,456 last displayed counter). It stopped on a two-second IPC receive
timeout, not a confirmed DOOM crash or memory ceiling. The 30-second edit is
`~/Videos/doom-terminals-25000-30s.mp4`; the original is
`~/Videos/doom-progressive-deferred-64k-attempt.mp4`.

`--allow-slow` now uses a 15-second IPC read timeout, restricted to our disposable
private compositor. It does not retry commands. `test_stress_ipc.py` checks that
a response delayed beyond two seconds succeeds with exactly one command sent.

`--skip-unchanged-rules` enables `hyprland-skip-unchanged-rules.patch` in the
private compositor. When workspace population changes, floating pixel-doom
windows skip appearance recomputation if there are no affected effects or enabled
workspace-dependent rules. Rule removal, dependent rules, and the rule-update
event retain their normal behavior. The flag is off by default.

Three paired lifecycle tests at 1,024 Foot windows, with existing 8 ms batching
enabled in both conditions, produced these means:

| Measurement | Previous | Optimized | Reduction |
| --- | --- | --- | --- |
| Creation wall time | 15.34 s | 14.65 s | 4.5% |
| Compositor CPU time during creation | 5.98 s | 3.25 s | 45.7% |
| Cleanup wall time | 3.65 s | 1.16 s | 68.2% |
| Compositor CPU time during cleanup | 3.30 s | 0.87 s | 73.5% |

Creation wall time was mixed across pairs. These are lifecycle measurements,
not playback FPS or evidence of 64,000-window feasibility. All runs verified
window sizes and floating state, and preserved an ordinary anchor window during
cleanup. Results: `output/rules-comparison-1024.json` and its summary JSON.

Functional validation passed color updates, ordinary rendering and text fallback,
stacking, resizing, close/reveal, population-dependent borders, and rule removal.
Valid optimized playback checks completed at 1,024 and 2,560 terminals, but the
matched baseline had presentation gaps. Other runs hit screenshot timeouts;
those runs were excluded. Intermittent nested presentation/capture stalls remain
unresolved, so no new playback improvement is claimed.


## Deferred GPU uploads (private compositor, opt-in)

`HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE=1`, together with the existing nested-only
and batched-drawing flags, retains the latest opaque 1×1 texture update in CPU
memory. The batched renderer already draws from the committed surface color.
If an ordinary render path binds the texture, the latest saved color is uploaded
first. SHM buffers are still released after copying; Foot windows, PTYs, terminal
parsing, frame callbacks, and presentation feedback remain real.

Patch: `hyprland-defer-texture.patch` (apply after the existing private patches).
Build with `cmake --build /tmp/pixel-doom-hyprland-build --target Hyprland -j2`.
Use `--defer-texture` with `preview_progressive.py` or `benchmark_launcher.py`
(the benchmark also requires `--batch-draw`). It is not enabled by default.

Matched 800×600 disposable host, 35 requested FPS, 15 seconds of playback:

| Terminals | Compositor CPU cores, off → on | Reduction | Median sampled latency, off → on | Sampled presentations, off → on |
| --- | --- | --- | --- | --- |
| 1,024 | 0.3620 → 0.3114 | 14.0% | 24.948 → 24.936 ms | 335 → 345 |
| 2,560 | 0.9339 → 0.8038 | 13.9% | 32.415 → 25.546 ms | 267 → 257 |

CPU averages use playback samples from second five onward. Presentation data
comes from terminal19, not whole-mosaic FPS. These runs establish CPU savings,
not an increased frame rate or 64,000-window feasibility. Startup was effectively
unchanged. Earlier valid pairs at another matched host size also reduced CPU;
repeats with missing feedback or mismatched host sizes were excluded.
Reports: `output/deferred-texture-comparison.json` and `output/defer-fixed-*`.

Validation checks actual screenshot colors before/after updates, ordinary-renderer
fallback after a deferred update, visible text and return to solid colors, stacking,
resize, and close/reveal. The benchmark now fixes the disposable host size and
rejects missing presentation intervals longer than three seconds.

A separate shared-color texture-cache experiment (`hyprland-texture-cache.patch`)
raised CPU about24% at1,024 terminals with no playback gain; leave it disabled.
Its flag and patch are retained only for reproducibility. Never combine it with
the deferred-upload experiment.

## Progressive recording and demo looping

`preview_progressive.py --levels 6 --max-terminals 32000 --hold 5 --timeout 1200 --record --output <fresh-directory>`
starts at 40 real Foot windows and refines the running image toward the requested
count. The counter sits directly above the image. Partial stages mix pixel sizes;
32,000 windows represent two native DOOM pixels per terminal **on average**.
This command is a target, not a claim that 32,000 has passed validation.
For a true 1:1 target, use `--levels 7 --max-terminals 64000`: the final
refinement splits only regions larger than one native pixel.
`python experiments/pixel-doom/test_regions.py` verifies exact coverage,
positive region sizes, partial counts, and 64,000 individual 1×1 regions.
This geometry test opens no windows and does not establish 64,000-window performance.

The progressive engine loops demo1 in one process at normal game speed. A stable
demo-name buffer fixes a dangling stack pointer used when the first demo ended.
`python experiments/pixel-doom/test_demo_loop.py` builds a separate accelerated
test binary and exercises 18,000 ticks, crossing three demo endings without windows.
Test acceleration is not enabled in the recording binary.

## Experimental single-pixel Foot buffers

A private Foot patch sends a **1×1 color buffer** for an empty, opaque terminal
with its cursor hidden. Wayland stretches it to the window size. This avoids
repainting and uploading a full bitmap for each color change. These remain real
Foot windows with real PTYs and normal escape-sequence parsing. Text and other
unsupported content fall back to the normal renderer.

Matched 640-window runs at 15 FPS on this desktop:

| Measurement | Patch disabled | Enabled | Enabled repeat |
| --- | ---: | ---: | ---: |
| Hyprland CPU cores, seconds 10–18 | 0.287 | 0.201 | 0.202 |
| Demo CPU cores, whole 18 seconds | 0.391 | 0.232 | 0.233 |
| Demo summed RSS, MiB | 166.71 | 144.48 | 144.84 |

That is approximately **30% less Hyprland CPU** and **40% less demo CPU**.
All compared compositor samples were visible. The first enabled run captured a
screenshot before the comparison interval; the repeat did not. These are short
runs with one baseline, not a guarantee of larger-scale performance. Summed RSS
can double-count shared pages; GPU use was not measured. Per-window compositor
and PTY overhead remain. The patch has now also completed a 1,280-window comparison (below).
Reports are in `output/single-pixel-comparison.json` and `output/onepixel-*.json`.

The patch is opt-in; installed Foot and default launcher behavior are unchanged.
It requires a viewport, 8-bit buffers, workers=0 and no preapply mode. It falls
back for visible cursors, text, styled backgrounds, selection, search, reverse
video, sixels and URL mode. This is an experimental optimization, not a fully
tested general-purpose Foot replacement. SHM allocation includes stride
alignment: a one-pixel image does not mean a four-byte allocation.

### Step up to 1,280 terminals

The user authorized a modest increase. Two 18-second runs at 40×32, requested
15 FPS, used the same private Foot build, with the SHM optimization off/on.
Color caching and callback omission stayed disabled. Steady compositor averages
use eight visible samples each, from seconds 10–18; demo CPU covers the full run.

| Measurement | Standard rendering | 1×1 SHM buffers |
| --- | ---: | ---: |
| Hyprland CPU cores | 0.496 | 0.436 |
| Demo CPU cores | 0.489 | 0.323 |
| Demo summed RSS, MiB | 274.72 | 249.20 |
| Startup seconds | 33.71 | 32.96 |
| Highest sampled gameplay IPC, ms | 24.67 | 19.97 |

Approximately **12% less Hyprland CPU** and **34% less demo CPU** in this pair.
The compositor benefit is smaller than in the 640-window comparison. These are
single short runs, not proof of larger-scale stability or achieved display FPS.
All geometry matched; both runs cleaned up normally with no remaining demo
windows. Shell CPU settled after startup. No recording or screenshot was taken.
PTY limit stayed 4096; no desktop configuration or installed Foot changes.
Reports: `output/scale-comparison-1280.json` and `output/scale-onepixel-*-1280.json`.
A subsequent optimized 1,920-window run is recorded below.

### Step up to 1,920 terminals

At the user's request, a 48×40 grid ran for 18 seconds with the SHM optimization
and requested 15 FPS. It opened in 51.94 seconds, verified all window dimensions,
and cleaned up normally. All steady samples (seconds 10–18) were visible.

- Hyprland steady CPU: **0.740 cores**, versus 0.436 at 1,280.
- Demo whole-run CPU: **1.011 cores**, versus 0.323 at 1,280.
- Demo summed RSS: **353.18 MiB** across eight processes.
- Highest sampled gameplay control-request latency: **26.49 ms**.
- Shell CPU stayed near idle; no demo windows remained after cleanup.

The sharp demo CPU increase needs investigation before assuming linear scaling.
This is one short run with no matching unoptimized 1,920 baseline; actual display
FPS and GPU use were not measured. Logs confirmed the fast path in all three
Foot servers. No system limit changes or shell restarts were needed.
Reports: `output/scale-onepixel-on-1920.json`, `output/scale-summary-1920.json`.
The patch subsequently completed the 5,120-terminal benchmark below.

### Rebuild the private binary

Run from the repository root. These commands need Git, Meson, Ninja and Foot's
build dependencies; Meson may download fallback dependencies. Use fresh `/tmp`
directories after reboot, or reuse the existing patched build without reapplying.

```bash
git clone https://codeberg.org/dnkl/foot.git /tmp/pixel-doom-foot-src
git -C /tmp/pixel-doom-foot-src checkout 2705e36f0ecf3ef50c13b41165de852f134859d6
git -C /tmp/pixel-doom-foot-src apply "$PWD/experiments/pixel-doom/foot-single-pixel.patch"
meson setup /tmp/pixel-doom-foot-build /tmp/pixel-doom-foot-src \
  -Ddocs=disabled -Dtests=false -Dterminfo=disabled --buildtype=release
ninja -C /tmp/pixel-doom-foot-build -j2 foot

python experiments/pixel-doom/run.py --cols 32 --rows 20 --fps 15 --seconds 18 \
  --foot-binary /tmp/pixel-doom-foot-build/foot --single-pixel-buffers \
  --metrics experiments/pixel-doom/output/onepixel-check-640.json
```

Omit `--single-pixel-buffers` for a baseline with the same build. The flag needs
the patched binary; stock Foot ignores the environment variable. Confirm the
saved `.foot.log` contains `single-pixel background path active`.

`python experiments/pixel-doom/test_single_pixel.py` checks one small window
transitions from a 1×1 buffer to normal text rendering and back. It passed;
`output/single-pixel-text-fallback.png` also visibly showed the expected text.
The 640-window gameplay screenshot is `output/onepixel-640.png`.

### Further experiments: callbacks and color sharing

Two additional switches are available in the private patched build, both off by
default and both requiring `--single-pixel-buffers`:

- `--no-pixel-frame-callback`: omit Wayland frame callback requests for the empty
  solid-color path. The hub already paces output at the requested FPS. Text
  rendering still uses Foot's normal frame callbacks. This removes callback
  requests, notifications and dispatch work, but also removes compositor-driven
  throttling for blank terminals. Use only with the externally paced experiment;
  hidden-window resource behavior and high-load behavior remain unvalidated.
- `--color-buffer-cache`: share immutable single-pixel protocol buffers with
  exactly matching colors through a bounded 4,096-entry cache per Foot server.
  **Not recommended for this workload:** the 640-window test increased Hyprland
  CPU to 0.288 cores and demo summed RSS to 211 MiB. Lower demo CPU alone did not
  offset those costs. It remains opt-in for reproducibility; no colors are
  quantized.

A fresh same-build comparison (640 windows, 15 FPS) found no convincing benefit
from callback omission:

| Mode | Hyprland cores, seconds 10–18 | Demo cores, whole run | Demo summed RSS MiB |
| --- | ---: | ---: | ---: |
| Existing SHM optimization | 0.205 | 0.175 | 145.04 |
| Color cache | 0.288 | 0.177 | 210.68 |
| Omit callbacks | 0.197 | 0.173 | 145.26 |

All eight compositor samples per run were visible. The small callback difference
is within short-run variability; an apparent win against older demo CPU numbers
disappeared with the fresh baseline. Keep **both switches disabled**. One run per
mode is not a statistical benchmark. The callback run captured a screenshot at
8 seconds, outside the compositor comparison interval. That screenshot looked
correct. Reports: `output/further-rendering-comparison.json` and per-run JSON.

The fallback check for the callback experiment is:

```bash
python experiments/pixel-doom/test_single_pixel.py --no-pixel-frame-callback
```

It verifies blank/text/blank transitions and that text restores normal frame
callback requests. All changes remain local and uncommitted.

## Latest desktop optimization

The user's Window Shelf plugin previously filtered `Hyprland.toplevels.values`
for every window-list change. It now reads only the two managed special
workspaces' toplevel lists. Normal terminal creation no longer invalidates that
global scan. The user-owned file changed is
`~/.config/omarchy/plugins/io.github.gardnmi.window-shelf/BarWidget.qml`;
the original is backed up in `output/window-shelf-BarWidget.qml.before`.
No packaged Omarchy files were edited.

A 640-window test with the shell kept running averaged approximately 0.004 CPU
cores for the shell; sampled compositor IPC peaked at 0.38 ms. Previous runs had
shown a persistent full shell core. This is promising, but a matched larger
comparison has not been run, so the persistent spin's exact cause is not proven.

A live 32-window probe showed that `min_size={1,1}` did not prevent the initial
20×20 size in this launch path; all 32 still needed resizing to 19×14. The
ineffective rule was removed. Final dimensions remain correct.

The user subsequently authorized small tests only. Larger stress tests remain
paused while they use the machine. Avoid interrupting their work.

## Experiment

Local, uncommitted experiment. DOOM renders at 320×200, then each averaged
output pixel colors a separate real Foot terminal window using OSC 11.
The default 80×64 grid contains **5,120 pixel terminals**, plus a black terminal
backdrop that hides the desktop wallpaper between pixels. Each group of up to
640 pixels shares a Foot server, font cache, and native renderer. Each terminal's
short-lived helper passes its PTY file descriptor to the renderer and exits;
Foot's hold mode keeps the real terminal window alive. The default grid uses
eight Foot servers and eight renderers, plus DOOM and the launcher. Window dimensions
adapt to preserve DOOM's overall image proportions as the grid grows.
Rendering workers and scrollback are disabled for these solid-color terminals.
Color changes use a short OSC 11 sequence; no redundant screen erase is sent.
Window placement is batched in groups of 16 to reduce compositor IPC overhead.
Windows already at the requested size skip resizing; a 640-window check skipped
all 640 resizes and still verified exact final dimensions. Startup reports now
include placement duration and resize count for each batch.
Foot 1.28 clients use a tested direct socket protocol to avoid launching
`footclient` for every window; other versions use the CLI. `--ipc cli` forces
the CLI, and `--renderer process` restores the original per-terminal helper.
The 5,120-pixel grid needs a pseudo-terminal limit above 5,121 plus any terminals
already open. The launcher checks this before opening windows. On machines with
the usual 4,096 limit, use `--cols 64 --rows 40` for 2,560 pixels, or temporarily
raise `kernel.pty.max` and restore its original value afterward. The launcher
does not change the system limit itself.
The terminals float in a grid on a fresh Hyprland workspace.

## Run on this machine

```bash
python experiments/pixel-doom/run.py
```

This plays DOOM's built-in demo. For an interactive game:

```bash
python experiments/pixel-doom/run.py --play
```

Click any pixel to focus it. **W/S** move, **A/D** turn, **F** fires,
**Space** uses doors, **Q** or **Ctrl+C** closes the entire experiment.
Arrow keys also work. Movement uses a short release timeout because terminal
input does not report ordinary key releases. The prototype is silent.

```bash
# Smaller grid / automatic cleanup
python experiments/pixel-doom/run.py --cols 16 --rows 10 --seconds 30

# Save a screenshot once the grid is showing gameplay
python experiments/pixel-doom/run.py --seconds 30 --capture /tmp/pixel-doom.png

# Save a 20-second video of the actual desktop windows
python experiments/pixel-doom/run.py --seconds 60 --record experiments/pixel-doom/output/doom.mp4

# Native DOOM pixels: 64,000 terminals, plus the backdrop (requires PTY headroom).
# This target has NOT yet been validated at full scale.
python experiments/pixel-doom/run.py --cols 320 --rows 200 --gap 0 --seconds 30

# Probe tiny window dimensions without opening the full grid
python experiments/pixel-doom/run.py --cols 320 --rows 200 --gap 0 --limit-windows 32 --seconds 8
```

Requires the installed `foot`, `footclient`, `gcc`, Python and Lua Hyprland.
Screenshot capture also needs `grim`; video uses `gpu-screen-recorder`.
Uses the existing DOOM sources and
`doom1.wad` at `~/Projects/terminal-doom`; `--source` can override that path.
No downloads are performed. The compiled executable is cached under `/tmp`.

Temporary window rules affect only this launch's unique application ID.
On exit, the launcher shuts down its Foot server and DOOM process, disables
its rule, and restores the previous workspace if you are still on the demo.
Desktop configuration files and the main Hyprsplitter game are unchanged.

The DOOM sources retain their upstream GPL licensing. No engine source,
WAD data, or compiled engine is included in this experiment directory.

## Performance check

A 640-pixel comparison on this machine (12 seconds of the same built-in demo):

| Measurement | Original | Optimized |
| --- | ---: | ---: |
| Startup | 14.14 s | 6.86 s |
| Total threads in demo processes | 3,208 | 644 |
| Demo process CPU time | 9.70 s | 5.66 s |

These are single-run measurements, not a broad benchmark. CPU totals cover the
launcher, DOOM, Foot, and pixel clients; they exclude the compositor and recorder.
Foot's worker count applies per terminal, which explains the original thread
explosion. These measurements predate the shared renderer.

The optimized 5,120-pixel run opened in 102.74 seconds and used 5,131 total
threads across 5,131 processes. Over a 60-second sample it consumed 148.54 CPU
seconds (2.47 cores on average). The resulting 18-second recording decoded
successfully; sampled frames showed gameplay without the earlier dialogs.
The temporary PTY-limit increase was restored after testing.

### Shared renderer

**64,000 terminals remain untested.** A previous larger run caused severe
desktop/input slowdown. Subsequent diagnostics found Quickshell consuming an
entire CPU core even with all demo windows closed; restarting the shell restored
idle CPU use. This is evidence of a separate desktop-shell problem, not proof
that the renderer caused it or that restarting fixes every scaling limit.
Do not treat the native-grid command above as a proven usable configuration.

`--setup-without-shell` is an optional local diagnostic: temporarily stop the
Omarchy shell while creating windows, restart it before gameplay, and do the
same around cleanup. The bar remains visible during gameplay and recording.
The launcher refuses to stop a locked session's shell, and restores the shell
on failure. This option targets this machine's `/usr/share/omarchy/shell` setup;
it does not edit desktop configuration. It tests whether the stream of window
events contributes to the shell backlog.

The new renderer checks all of its pixels once per frame, writes only changed
colors, and uses epoll for terminal input. Nonblocking writes keep a slow terminal
from blocking its neighbors; partial escape sequences finish before a newer
color is sent. This removes one persistent process and polling loop per pixel.
`--fps` sets the renderer's sampling frequency (default 15); the DOOM bridge
produces approximately 15 frames per second at renderer settings up to 15;
higher settings now request a faster bridge cadence, up to 35 FPS.

| Grid | Processes / threads | Startup | Average demo CPU cores |
| --- | ---: | ---: | ---: |
| 640 pixels | 4 | 7.35 s | 0.59 |
| 2,560 pixels | 10 | 32.70 s | 0.89 |

Process reduction is substantial; the 640-pixel run did **not** improve CPU
time or startup against the previous optimized version. The 2,560-pixel run
also recorded video, whose CPU use is excluded from these totals.

A 32-window probe on a 320×200 grid confirmed exact 5×5 logical-pixel window
dimensions on this monitor. At full 320×200, each terminal receives one source
pixel, with no downsampling. This still requires 64,000 PTYs and compositor
surfaces. Neither memory use nor desktop responsiveness at that count is proven.

Startup stops between batches if available RAM drops below 4 GiB or opening
windows takes over 600 seconds. Adjust with `--min-free-gib` and
`--startup-timeout`. These guards cannot prevent a compositor stall inside a
request. Reports and Foot logs are saved alongside `--metrics` output.

Transport checks (after `--build-only`):

```bash
python experiments/pixel-doom/test_transport.py
```

These compare the protocol with the installed Foot client and verify that PTY
rendering and keyboard input survive helper exit.

### Diagnosing desktop overhead

`--metrics` now includes one-second samples of Hyprland and Quickshell CPU
(in CPU cores), plus Hyprland IPC response time. Two consecutive samples over
250ms stop the demo. This is a control-request latency check, not a measurement
of input-to-display latency. GPU load is not measured.

`--freeze-after 8 --seconds 16` compares animation with a frozen frame while
keeping all windows open. The first frozen sample straddles the transition.
`--batch-pause 0.3` lets desktop event queues settle between creation batches.
The defaults now use 64-window batches with a 10ms pause between launches;
adjust with `--batch-size` and `--spawn-delay`. Startup also checks IPC and
aborts if a sampled request takes over 250 ms. Failures save the opened count
and error in the metrics file. A request already blocked inside the compositor
can still take time to recover from.
`--fps 5` reduces update frequency in either renderer.

At 640, the process and shared-renderer comparisons took 7.42 s and 7.29 s to open;
their demo CPU averages were 0.381 and 0.366 cores respectively across an 8-second
animated plus 8-second frozen run. Hyprland CPU fell close to zero after freezing.
At 1,280 windows / 5 FPS, animated Hyprland CPU was approximately 0.28 cores; IPC was typically
0.3 ms. At 2,560 windows / 5 FPS, Hyprland used approximately 0.7–0.8 cores during active gameplay,
with sampled IPC below 27 ms. Quickshell took several seconds to settle after
creation but returned to idle. These are individual runs, not guarantees.

A subsequent 5,120-window retry at 5 FPS failed during window placement after the
last progress message at 3,840, before gameplay started. Cleanup completed and
the desktop recovered. The temporary PTY limit was restored to 4,096. The new
startup pacing has only been tested on a small grid; its benefit at 5,120 is not
yet established. The earlier successful 5,120 recording remains the known-good
large run.

### Latest 5,120-window retry

With paced creation and `--setup-without-shell`, all 5,120 windows opened in
160.44s and played for 28s at a requested 3 FPS. The demo used 18 processes,
1.19 CPU cores on average, and 912 MiB summed RSS. All window dimensions matched.
Startup IPC peaked at 8.05ms; gameplay IPC peaked at 163.64ms. Hyprland and the
shell each used about one CPU core late in playback, excluded from demo totals.
The 19.5s recording `output/doom-5120-paced.mp4` decoded successfully and a
sampled frame showed clean gameplay and the visible desktop bar.

Cleanup still failed to restart the shell promptly; after the compositor
recovered, a manual shell restart succeeded. The terminal limit was restored.
The launcher now waits for three responsive client-list queries with no demo
windows before restoring the shell after cleanup. This change passed a small
test but has not been validated again at 5,120. Counts above 5,120 remain untested.

The 5,120 layout initially opened at20×20 despite requesting19×14, so every
window still required resizing. Skipping redundant resizes helped the640-window
case; it did not account for this5,120-window success.

Use `--metrics output/result.json` to collect a run's measurements. Keep videos
and reports in this directory's ignored `output/` folder so they survive reboot.


### Small rendering comparison

At 640 windows, averages over steady gameplay (seconds 6–12):

| Layout | Requested updates/s | Hyprland CPU cores |
| --- | ---: | ---: |
| 2-pixel gaps | 15 | 0.2965 |
| No gaps | 15 | 0.2995 |

Freezing the image dropped Hyprland CPU to 0–0.0067 cores. Removing gaps did
not materially help at this scale. Each case is one short run, not evidence
about behavior at 64,000 windows. Control-request latency stayed under 8 ms.

A third run at 3 updates/s became hidden when the workspace changed before
steady gameplay. It provides no valid visible FPS comparison and is excluded.
New samples record `demo_visible`; hidden samples must not be used to claim
rendering improvements. GPU use is still unmeasured. Reports are in
`output/small-rendering-comparison.json` and the corresponding `small-gap*.json`.

### Per-process investigation of the 1,920 CPU increase

`--metrics` now records `process_breakdown` (CPU/RSS per Foot server, hub, DOOM,
and launcher), plus per-second `process_cores` alongside workspace visibility.
A repeat at 1,920 showed each Foot server averaging about 0.99 CPU cores; DOOM
used 0.022 and the three hubs together 0.043. This identifies Foot as the heavy
consumer in that repeat, but **the workspace became hidden after two seconds**.
It cannot establish the cause of the earlier visible-run increase or serve as a
rendering benchmark. No further large previews were launched after the switch.
Report: `output/profile-onepixel-1920.json`. Per-second process detail was added
after that run and has only been syntax checked; whole-run detail was exercised.

Foot's per-terminal render-delay timers are a candidate for further profiling,
not a confirmed cause. No timer settings or rendering defaults were changed.

### Ghostty comparison: 64 windows

`compare_terminals.py` compares isolated Ghostty and patched Foot instances. Each
uses one emulator process, 64 real windows sized150×90, and the same small C
helper per window writing changing OSC11 colors at15Hz. Helpers remain alive;
this deliberately avoids differences in hold-after-exit support. Thus this is
a synthetic terminal test, not the shared-hub DOOM workload. User config is
disabled; Ghostty gets a unique application/DBus ID. No installed configs change.

After warm-up, each mode was measured for10s visible and10s hidden:

| Emulator / phase | Emulator CPU cores | Emulator RSS MiB | Emulator threads | Hyprland cores |
| --- | ---: | ---: | ---: | ---: |
| Foot, visible | 0.019 | 34.38 | 1 | 0.057 |
| Ghostty, visible | 0.870 | 755.89 | 205 | 0.088 |
| Foot, hidden | 0.012 | 34.38 | 1 | 0.017 |
| Ghostty, hidden | 0.139 | 756.17 | 198 | 0.017 |

CPU/RSS/thread columns cover the emulator only, excluding the identical64 helper
processes and Hyprland. Helper CPU is recorded separately, subject to per-process
tick rounding. All64 windows shared one emulator PID and matched dimensions in
both runs. Ghostty1.3.1-arch2 used OpenGL; Foot1.28 used the private SHM1×1 patch,
workers0. This tests our specialized configuration, not general terminal speed.

**Keep optimized Foot for this experiment.** Ghostty was much heavier here.
Foot's previously observed hidden-workspace CPU spin did not reproduce in this
small, live-helper workload, so its cause at1,920 remains unresolved. This single
short comparison cannot establish large-scale behavior or GPU memory use.

Run one at a time:

```bash
python experiments/pixel-doom/compare_terminals.py ghostty --count 64 --seconds 10
python experiments/pixel-doom/compare_terminals.py foot --count 64 --seconds 10
```

The runner caps windows at64, measures both phases, and closes only its own
instances. It stops if the visible phase becomes hidden unexpectedly.
Ghostty initially maps windows before their commands run on the hidden workspace;
the runner reveals them and waits before checking helper counts. Initial probes
that stopped before measuring were not used in the comparison.
Reports: `output/terminal-comparison-64.json`, `output/compare-{foot,ghostty}-64.json`.
All comparison windows closed; no commits or system-limit changes.

### Patched Foot: 5,120-terminal benchmark

The authorized retry completed at80×64, requested3FPS for28 seconds, with SHM1×1
enabled. The shell stayed running; cache and callback-removal experiments were
off. All window dimensions matched and all playback samples were visible.

| Measurement | Result |
| --- | ---: |
| Startup | 152.66 s |
| Steady Hyprland CPU | 0.899 cores |
| Steady Foot CPU, all eight servers | 0.133 cores |
| Steady total demo CPU | 0.188 cores |
| Whole-playback demo CPU | 1.015 cores |
| Demo summed RSS | 873.41 MiB |
| Demo processes / threads | 18 / 18 |
| Peak sampled gameplay IPC | 51.23 ms |
| Peak sampled startup IPC | 3.13 ms |

Steady averages use22 visible samples from6seconds onward. Foot consumed about
7.6–8 cores during the first two seconds, dropping to roughly0.13 total after
four seconds. This explains why whole-run CPU can misrepresent steady playback;
it does not prove the cause of earlier runs' spikes. Shell steady CPU was0.003
cores. Actual displayedFPS, GPU use and compositor memory growth were not measured.

**Cleanup caused a prolonged temporary desktop stall.** The launcher exited
about35 seconds after writing its playback report; three responsive client-list
checks and PTY-limit restoration were only confirmed about116 seconds after
that report. All demo windows were gone on recovery. No compositor restart was
performed. The temporary8192 PTY limit was restored to4096.

An initial attempt failed in new profiling instrumentation before playback; the
misplaced sampling block was moved from startup to the playback loop and a
16-window smoke test exercised it successfully before the retry. Failure logs
are retained separately. The successful data is in:

- `output/benchmark-summary-5120.json`
- `output/optimized-5120-3fps-current.json`
- `output/optimized-5120-3fps-current-lifecycle.json`
- `output/optimized-5120-3fps-current.stdout.log`

This is a single run, not a matched optimization comparison. Previous5,120 tests
also differed in shell handling and recording. No count above5,120 was attempted.

### Preparing half-native capture

32,000 windows at320×100 represent two vertically averaged source pixels per
terminal; true1:1 still requires320×200=64,000. This larger run has not launched.
The bridge now accepts `PIXEL_DOOM_OUTPUT_FPS`, supplied by `--fps`, to remove
the old65ms output ceiling for settings above15. Lower settings preserve the
previous bridge cadence for comparison continuity. Capture requests at least
30FPS, or the renderer FPS when higher. These settings do not prove achieved
display throughput. Engine-only tests at320×100 confirmed increased frame-content
changes with35 vs15; unsynchronized buffer reads can include partial frames,
so observed change counts are not a precise FPS measurement.

### 32,000-terminal live attempt: startup failure at6,720

The user authorized320×100 terminals, requested35FPS and live recording. The
64-window recording smoke test produced a valid35FPS H.264 file, then a
temporaryPTYlimit32768 enabled the large attempt.

The large run **failed during window placement after opening6,720 terminals**.
Hyprland did not answer a placement request within the2-second socket timeout.
The last successful64-window batches took roughly2.5seconds total to arrange.
AvailableRAM was still about21.8GiB at the last check. The process did not reach
DOOM playback or start recording; no32,000-terminal video exists. The35FPS
playback target was therefore not tested at this count.

Cleanup released the terminalPTYs and restoredkernel.pty.max4096, but desktop
control requests remained unresponsive after the driver's90-second recovery
check. Additional recovery status is saved in `output/attempt-32000-recovery.json`.
No Hyprland restart was attempted. The launcher took291s through failure and
exit, including about47s after writing the failure report.
Reports: `output/attempt-32000-35fps.json`, `.stdout.log`, and `-lifecycle.json`.
This run points to window creation/placement and destruction as immediate
scaling barriers; it does not measure full-grid rendering performance.

The follow-up checks confirmed recovery: three responsive queries, zero remaining
experiment windows, final latency0.2ms. Approximately218.9s elapsed from the
failure report to confirmed recovery. The system limit remained4096.

### Addressing creation and destruction overhead

The launcher now defaults to `--initial-size-rule`: its temporary application
rule sets initial pixel dimensions explicitly, avoiding Hyprland's20×20 initial
size for these tiny windows. The black backdrop is explicitly resized to its
full-screen size as before. `--no-initial-size-rule` restores the old behavior.
This differs from the previously unsuccessful `min_size` rule experiment.

A640-window probe at320×100 layout (5×10 windows) compared the same five
128-window Foot servers,3FPS,4-second playback:

| Measurement | Previous placement | Initial size rule |
| --- | ---: | ---: |
| Resize operations | 640 | 0 |
| Total placement time | 86.72 ms | 68.31 ms |
| Total startup | 15.314 s | 15.182 s |
| Geometry mismatches | 0 | 0 |

Placement improved21%; paced launch delays still dominate total startup at this
size. This single small pair does not establish32,000-window feasibility.

Cleanup now defaults to `--paced-cleanup`: stop DOOM and PTY writers first, then
terminate one Foot server at a time and wait for its windows to disappear with
a responsive client-list query before proceeding. Each wait is bounded15s so a
stalled compositor cannot prevent termination of all remaining servers forever.
`--server-size N` controls the number of pixels per Foot server (default640,
range1–640); use128 for smaller destruction groups at the cost of extra processes
and memory. `--no-paced-cleanup` restores the former teardown order. Reports
include a `.cleanup.json` file with per-group recovery status.

At640, paced cleanup confirmed all five128-window groups settled and finished in
3.492s; the former cleanup finished in3.478s. Thus pacing is functionally tested,
not a demonstrated speedup or proven cure for the large teardown stall.

Installed Hyprland0.56.2 source inspection identified repeated global work:
`CWindow::onUnmap` calls workspace-wide window/rule updates and
`updateAllWindowsDecorations`, which scans the window list. Address selectors
also scan windows and format addresses. These are plausible scaling contributors,
not sampled CPU-profile attribution. A deeper fix would coalesce repeated
workspace/decoration updates during bulk creation/destruction, with careful tests
for normal window rules and focus behavior. No compositor source was installed
or the running desktop restarted. Increasing socket timeout alone would not
remove this work. Smaller `--placement-batch 4` requests are available for the
next controlled scaling test; the comparison above used16 in both cases.

Artifacts: `output/initial-size-comparison.json`, `output/size-rule-*-640.json`,
and corresponding `.cleanup.json` reports. All small-test windows closed.

### Controlled scaling of placement and paced cleanup

Follow-up tests used partial320×100 grids, exact5×10 windows,128 pixels/server,
placement batches4, initial-size rule enabled, paced cleanup enabled,3FPS and8s
playback. These are layout/lifecycle tests, not full-image FPS benchmarks.

| Windows | Startup | Placement total | Resizes | Cleanup | Groups settled |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1,280 | 28.399 s | 272.62 ms | 0 | 12.143 s | 10/10 |
| 2,560 | 57.195 s | 3209.88 ms | 0 | 45.867 s | 20/20 |

Both had zero geometry mismatches. Maximum group-recovery waits were0.012s and
1.296s respectively (cleanup totals also include process termination). Final
client query took0.13ms with no experiment windows. No system limits changed.
The2,560 run used881.81MiB summed demoRSS due to20 Foot servers and20 hubs.
Its brief playback approached one Hyprland core; this partial layout and grouping
differ from earlier full-image tests and cannot support a rendering-speedup claim.

Pacing was functionally successful, but teardown still grew almost4× when window
count doubled. No matching old-cleanup baseline at these counts was run, so this
does not establish a cleanup performance gain. It supports investigating the
repeated compositor-wide updates before another large count increase.
Reports: `output/paced-native-scaling.json`, `output/paced-native-{1280,2560}.json`
and `.cleanup.json` companions.

## Private Hyprland lifecycle batching experiment

`hyprland-batch-lifecycle.patch` targets Hyprland 0.56.2, commit
`efb50993780079460b0cbed1363e2166a2de1d9f`. It is a separate compositor source
experiment; it is not installed into the desktop session.

With `HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE=1`, floating, non-X11 windows whose
class starts with `pixel-doom-` share deferred workspace updates on a fixed
8 ms deadline. `HYPRLAND_PIXEL_DOOM_BATCH_MS` selects 0–16 ms; 0 uses an
event-loop idle callback instead. The deadline does not slide on every request. Unmapping also batches workspace data updates, decoration
refreshes, and forced size reports to remaining windows. Focus, layout removal,
and individual window teardown still run immediately. Leave the variable unset
to use the original paths. Deferring updates changes their timing and needs
more validation before any normal desktop use.

The same patch adds `HYPRLAND_PIXEL_DOOM_NESTED_ONLY=1`, which selects only the
Wayland backend, preventing this build from attempting DRM display ownership.
The benchmark requires this guard. It uses a private runtime directory,
configuration and D-Bus session, with systemd environment updates disabled.
It opens one nested compositor window on the desktop and creates test terminals
inside it. Installed binaries and desktop configuration remain unchanged.

Build in a separate checkout with its `udis86` and `hyprland-protocols`
submodules initialized, apply the patch, then configure/build:

```bash
cmake -S /tmp/pixel-doom-hyprland-src -B /tmp/pixel-doom-hyprland-build \
  -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DNO_XWAYLAND=ON -DNO_HYPRPM=ON
cmake --build /tmp/pixel-doom-hyprland-build --target Hyprland -j2
python experiments/pixel-doom/benchmark_lifecycle.py --count 128 --repeats 2
```

`benchmark_lifecycle.py` compares batching off/on in the same binary, reverses
order on alternate repeats, checks that all targets are floating, and verifies
an ordinary anchor survives their closure and can subsequently close normally.
It allows at most 1,024 windows and three repeats, with an 8 GiB available-memory
reserve and a 45-second creation deadline. JSON reports and logs go to
`output/lifecycle-*`. The workload is static held terminals, not DOOM playback;
these results cannot establish live frame rate or 32,000-window feasibility.

The initial idle-only 128-window comparison showed no measurable cleanup gain:
about 0.114 seconds in all four trials, with nearly every lifecycle request
still causing a workspace pass. Those reports are preserved as
`output/idle-lifecycle-*`. The revised fixed-deadline trial also includes the
same 25 ms settling period in both modes before recording cleanup completion.

### Fixed 8 ms batching results

All trials used the same private compositor binary in nested-only mode, with
batching disabled/enabled. At 128 windows there were two pairs; at 512, three.
Order reversed on alternate pairs. Values below are medians.

| Windows | Baseline cleanup | Batched cleanup | Baseline compositor CPU time | Batched compositor CPU time |
| --- | ---: | ---: | ---: | ---: |
| 128 | 0.129 s | 0.087 s | 0.055 s | 0.020 s |
| 512 | 1.065 s | 0.526 s | 0.960 s | 0.380 s |

At 512 windows this is **51% less cleanup wall time and 60% less compositor CPU
time during cleanup**. All three pairs improved: baseline wall times ranged
1.047–1.104 seconds; enabled times ranged 0.503–0.550 seconds. Startup did not
show a consistent improvement. The ordinary anchor remained after target
closure and subsequently closed successfully in every trial.

These are small, static nested-compositor tests. Cleanup includes an equal
25 ms settling period and uses 20 ms polling; process CPU accounting has 10 ms
resolution. Some file logs omit buffered trailing entries, so their aggregate
batch counters are lower bounds. No claim of live DOOM frame rate, general
compositor correctness, or 32,000-window capacity follows from these results.
All private compositor processes and experiment windows were gone afterward;
the PTY limit stayed 4096. Nothing was installed, committed or pushed.

Reports: `output/lifecycle-summary.json`,
`output/lifecycle-comparison-{128,512}.json`, and individual `lifecycle-*` logs.

### Follow-up at 1,024 terminals

Two further pairs in the same nested harness confirmed the cleanup benefit:
median cleanup **4.621 → 1.975 seconds** (57% less time), and compositor CPU
**4.500 → 1.685 CPU seconds** (63% less). Individual cleanup pairs were
4.894 → 1.955 seconds and 4.349 → 1.994 seconds. Startup stayed around
13.3 seconds in both modes. Each run preserved the ordinary anchor and closed
all test windows. No PTY-limit or installed desktop changes were needed.

Doubling the window count from 512 still roughly quadruples cleanup time even
with batching. This reduces repeated work but does not remove the scaling
problem. These tests remain static nested windows, not a playback benchmark.
Reports: `output/lifecycle-comparison-1024.json` and
`output/lifecycle-summary-1024.json`.

## Private address-selector optimization

`hyprland-fast-address.patch` is a separate opt-in patch to the same Hyprland
source version. With `HYPRLAND_PIXEL_DOOM_FAST_ADDRESS=1`, address selectors
parse the requested address once and compare integers during the window scan,
instead of formatting each candidate address into a string. It preserves the
existing canonical spelling checks and mapped-window/filter checks. It never
dereferences the supplied numeric address. The scan remains linear; this is
not a constant-time index. Leave the variable unset for the original behavior.

Apply this patch alongside the lifecycle/nested-only patch, rebuild the private
binary, then run:

```bash
python experiments/pixel-doom/benchmark_lifecycle.py --mode address --count 512 --repeats 3
```

In address mode, lifecycle batching stays enabled in both arms. The harness
checks malformed/noncanonical addresses, a title selector, surrounding whitespace,
and a closed target's address. It performs 16 successful queries per target,
then moves every target in four-window request batches and verifies every
position. Address-mode reports use `output/address-*`, separate from lifecycle
reports. Placement timing excludes the verification query; this tests a single
placement pass after creation, not the launcher's interleaved creation/placement
workflow. It cannot establish the entire launcher's startup gain.

### Address lookup and placement results

Three pairs at 512 windows and two at 1,024 passed every selector and geometry
check, with order reversed on alternate repeats. Medians:

| Windows | Lookup count | Original lookups | Numeric lookups | Original placement | Numeric placement |
| --- | ---: | ---: | ---: | ---: | ---: |
| 512 | 8,192 | 145.68 ms | 14.75 ms | 20.16 ms | 9.52 ms |
| 1,024 | 16,384 | 544.51 ms | 38.00 ms | 69.76 ms | 25.07 ms |

At 1,024 windows, isolated lookups were about 14× faster and a placement pass
used **64% less wall time**. Creation remained about 13.1 seconds in both arms;
the 45 ms placement saving does not materially change total startup at this
count. Both arms had lifecycle batching enabled. Their cleanup timings must
not be mixed with the earlier unpositioned lifecycle tests: the placement test
changes window geometry and rendering work.

All nested instances exited and no experiment windows remained on the desktop.
The PTY limit remained 4096. Changes are private source patches only, uncommitted
and uninstalled. Reports: `output/address-summary.json`,
`output/address-comparison-{512,1024}.json`, individual `address-*` reports,
and `output/followup-isolation-cleanup.json`.

## Faster Foot window creation: skip the repeated font diagnostic

Foot 1.28's server clones configuration for per-window titles, app IDs and sizes.
Each clone normally triggers `check_if_font_is_monospaced`, which loads a font
and rasterizes five glyphs to check their widths. The experiment always selects
the same monospace font. `run.py` now passes
`-o tweak.font-monospace-warn=no` to its own Foot servers, avoiding that repeated
diagnostic. It does not change the font or rendering. Use
`--font-monospace-check` to restore the previous behavior. Metrics record the flag.
This uses an existing Foot option and needs no new Foot/compositor patch.

Two paired trials at each count in the nested compositor, reversing order on
the second pair, produced these medians:

| Terminals | Original creation | Diagnostic disabled | Original Foot CPU | Diagnostic disabled Foot CPU |
| --- | ---: | ---: | ---: | ---: |
| 128 | 0.969 s | 0.569 s | 0.780 CPU s | 0.385 CPU s |
| 1,024 | 13.224 s | 9.135 s | 9.020 CPU s | 5.185 CPU s |

At 1,024 this is **31% less creation time and 43% less Foot CPU during creation**.
Both optimized runs completed in 9.11–9.16 seconds, versus 13.21–13.24 seconds
with the diagnostic. All 1,024 target sizes matched 24×24, all were floating,
and the ordinary anchor survived closure of the targets. Each test cleaned up.

These are sequential static held-terminal tests with one Foot server and
lifecycle batching enabled in both arms. The full DOOM launcher also includes
spawn delays, multiple servers, placement and other setup, and was measured separately: two 1,024-terminal pairs reduced startup from
20.096/20.049 seconds to 16.634/16.617 seconds (about 17%). This does not
establish playback FPS.
No installed desktop configuration or binaries were changed; PTY limit 4096.

Reproduce with `python experiments/pixel-doom/benchmark_lifecycle.py --mode font
--count 1024 --repeats 2` (one command). Reports: `output/font-summary.json`,
`output/font-comparison-{128,1024}.json`, individual `font-*` logs, and
`output/font-test-cleanup.json`. The preliminary CPU attribution run is under
`output/creation-profile/`.


### Progressive video intro (optional)

Add `--intro` to the launcher to show four readable Foot terminals with their
actual PTY names and child PIDs. Three close, and the remaining preview becomes
a counter of real mosaic windows as they appear. Preview windows are separate
from the mosaic and excluded from its count. The initial checkerboard makes
new tiles visible; after a short ready card, DOOM starts in the mosaic.

With `--record PATH --intro`, recording includes construction and up to 20 seconds
of gameplay. Construction is recorded at real speed. If sped up in an edit,
label that section as a timelapse. Shared Foot servers manage separate terminal
windows and PTYs; window count does not mean an equal number of Foot processes.
A 128-window nested intro test passed. Identity and population screenshots
were visually checked under `output/intro-visual/`; final video capture is pending.

### Playback diagnostics and current limits

`--presentation-sample INDEX` instruments one cell in the private Foot build.
Feedback measures that cell's nested-compositor presentation, not the entire
mosaic's physical display frame rate. `--cache-pixel-geometry` is experimental,
off by default; functional fallback/resize checks passed, but a 2,048-window
run did not establish a CPU improvement.

At 3,072 windows and 35 requested FPS, the compositor used about 0.975 CPU core.
The sampled cell's median commit-to-presentation latency was 73.8 ms after warmup.
All windows were placed correctly and cleaned up, but these results do not
justify a 32,000-window run yet.

`hyprland-batch-draw.patch` is a separate private, nested-only rendering
experiment, still under validation. It batches drawing of eligible opaque
1×1-buffer windows while retaining their real surface/window objects. It is
not installed on the desktop and must pass color, stacking, resizing, removal,
and text-fallback checks before performance results count.


Batched drawing passed 32-terminal color and color-update checks, overlap,
resize, close/reveal, and normal text fallback, with the active fast path
confirmed in the compositor log. One 3,072-terminal comparison at 35 requested
FPS and 20 seconds of playback showed:

| Measurement | Prior path | Batched drawing |
| --- | ---: | ---: |
| Compositor CPU cores, mean | 0.975 | 0.938 |
| Sampled cell median presentation latency | 73.8 ms | 46.4 ms |
| Sampled cell median interval between presentations | 54.4 ms | 35.1 ms |
| Maximum sampled IPC response | 63.2 ms | 34.0 ms |
| Cleanup | 24.5 s | 23.7 s |

Both runs placed all windows correctly and cleaned up completely. These are
single runs, not a repeated paired benchmark. The sampled cell can remain the
same color across game frames, so its presentation intervals are not a full
mosaic FPS measure. CPU remains close to saturation; this does not establish
32,000-terminal readiness. Reports: `output/scale-3072-35fps/` and
`output/batch-draw-3072-35fps/`. The batch option remains opt-in.


### Presentation validation and startup investigation

Later 3,072-window repeat runs without the intro stalled: their processes stayed
alive and their workspace IDs looked correct, but the sampled terminal produced
no gameplay presentation feedback. Those results are invalid. The harness now
checks sustained presentation feedback and observes the outer window's workspace
visibility. It also records the exact playback start time for profile analysis.

Keeping the workspace visible during construction with `--intro` completed a
3,072-window run with 351 measured presentation feedbacks, zero placement errors,
and clean shutdown. The median sampled presentation latency was 36.8 ms; compositor
CPU averaged 0.936 core. This run used `--monitor-damage`, which sets
`debug.damage_tracking=1` in the private compositor only. Its outer window remained
visible at 2042×1120. The failure to resume a hidden grid is still under investigation;
one successful intro run does not establish a general fix or 32,000-window readiness.

`output/monitor-damage-intro-3072/profile-summary.json` summarizes 1,765 playback
CPU samples with no lost records. The largest buckets include NVIDIA's driver
(9.5%), batch eligibility checks (8.1%), and Wayland server processing (6.9%).
These percentages describe sampled main-thread CPU, not wall-clock frame time.
Use `summarize_profile.py DIRECTORY --symbols SYMBOL_FILE` with symbols from the
exact sampled binary. Invalid stalled runs must not inform optimization claims.


## Progressive clarity video (current presentation)

`preview_progressive.py` runs one continuous DOOM demo, beginning with **40 real
Foot terminal pixels**. Each coarse tile divides into four: its existing terminal
shrinks into the top-left quadrant and three new real terminals fill the others.
The image stays live throughout, becoming clearer at 160, 640, and 2,560 terminals.
A small counter above the image updates after each split. It counts mosaic
terminals; the black backdrop and text counter are additional helper terminals.
There are no identity cards, title sequence, or game restarts.

The engine writes its native 320×200 RGB frame once. Each shared PTY hub averages
the source region assigned to each terminal and sends that color through its real
PTY. Sequence-marked region records let the hub change a terminal's sample region
without replacing its window or restarting DOOM. This changes spatial resolution,
not the engine's gameplay speed. `test_transport.py` verifies full-frame averaging
and region changes on the same PTY, alongside the existing transport tests.

Example (private nested builds must already exist):

```bash
python experiments/pixel-doom/preview_progressive.py \
  --levels 4 --hold 3 --record \
  --output experiments/pixel-doom/output/progressive-video-2560
```

`--levels 3` ends at 640; `--levels 4` ends at 2,560. `--hold` controls the pause
at each completed resolution; actual window creation happens in between while
DOOM keeps running. Counts, geometry checks, elapsed times, and the unchanged
engine PID are saved in `progression.json`. Per-stage screenshots are saved too.
The old `run.py --intro` is a separate identity-preview experiment and is **not**
used by this sequence.

Nested recording uses a private `wf-recorder` build at
`/tmp/pixel-doom-wf-recorder-build/wf-recorder`, H.264 at 35 capture FPS, with two
encoding threads. This avoids capturing unrelated host applications. No system
recorder was installed or replaced. The build source is upstream wf-recorder;
its old `AVCodec.pix_fmts` access was adapted to the installed FFmpeg API locally.
The 640-terminal recorded smoke test passed: 18.03 seconds, 632 encoded frames,
all three stage geometries correct, one engine PID, and complete window cleanup.
Capture frame rate is not a claim that every terminal presents 35 distinct colors
per second. Larger scale readiness remains a separate performance question.


The 2,560-terminal recording also passed all four stages and cleaned up completely.
It is 101.03 seconds long, with 3,537 encoded frames at 35 capture FPS. The final
refinement takes about 80 seconds of real window creation; the footage has not
been sped up. Copies are in `~/Videos/doom-progressive-40-to-640.mp4` and
`~/Videos/doom-progressive-40-to-2560.mp4`. The shorter recording is an 18-second
preview; the longer one demonstrates more final detail.
