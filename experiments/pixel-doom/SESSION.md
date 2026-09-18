## FINISHED — 56,000 validated terminals and saved recording; no active runs

Latest user: "okay it crashed what did we get?" Read saved files, verified video,
finished edit. No new64klaunch: directory/stages.jsonabsent,driverprocessgone.
56k progression.jsonstatuscomplete:10.036s sample;7samplepresentations,1.957s
medianlatency; geometryall56,000 zero mismatches in0.335s. Built1845.223s(30.75min).
Rawvideo9.771433sec1280x8001,189,550bytes; decodedvisualDOOMconfirmed.
Sparse/asynchronous updates; do NOT claim smoothFPS. Cap10Hzterminalcolors,
engineunchangednormalgamespeed. Result-summary.json records evidence/limits.
Overalldriver/stopcause not confirmed; don'tassertDOOMcrashed. No64kstageattempted.

SAVED ~/Videos/doom-56000-terminals.mp4 (originalclip).
SAVED ~/Videos/doom-terminals-staged-progression.mp4 (47.966667s≈48s,
1280x800,1439frames30fps,7,157,854bytes). Six8secondstages:
40,160,640,2560,10240,56000. Normalelapsedspeed, nointerpolation, addedcount
captionsfromverifiedstagecounts. SourcesinadjacentJSON.

Allprivateexperimentalprocessesgone. Helperno longerpresentafterinterruption,
PTYmaxwasstill65536; explicitlyrestored4096 viaauthorizedsudo. PTYnr6.
No commits;gitstatusonly??experiments/. No installeddesktopconfigchanges.
Alltoolrun sessionsended/unknownafterinterruption;edit47518finishedsuccessfully.
Do not start another run unless user requests it. User askedstatus, answered
with56krecordingandprogressionvideo. Futurework: playbackthroughput/sync,
maybeprofileblockedcompositor/Foot at48k; creationandminimalquerynowwork.

## CURRENT ACTIVE driver2960 — prestarted recorder, terminal updates10Hz

48k static-large-validated built+validated: geometry.json48,000 zero mismatches,
minimalgeometryquery0.276s. DOOMholdunrecorded3samplepresents/10sec, recording
phase1present/10sec; recordernevercreatedfile (startupstarved), killedafter10s
finalizationtimeout. No48kvideo! progression.jsonstatuscompleteonlymeansplayback
logicfinished; addedcapture-result.json marksrecordingfailed. Don'tclaim48kFPS.
Driver79624pausedthenkilled558132 topreventautomatic56kaftermissingrecording.
Privatecompositororphan558158 killed. WrapperfixnowSIGKILLentirecompositorgroup
evenifdbus-run-sessionparentexitedearly; alloldprivateprocessesgone.

New --prestart-record startsrecorderbeforeengine, waitsheader, skipbaselinehold.
--fps10 caps terminalhubupdates; DOOMsimulationnormal speed. capture.json records
approxstartupoffset and cap. Passed2560testoutput/static-prestart10-2560:
10.0286s video,84samplepresents/10sec,zero geometrymismatches,cleanexit.
Wrappernowffprobevalidatesrecordingexistence/duration; missingclipfailsstage.

ACTIVE tool2960 record_stages.py --counts56000 64000 --fps10 --prestart-record
--output output/static-prestarted-large. Onworkspace5,focusbeforecapture;
wait/retryonhiddenworkspace,preservegrid. Monitoruntilstop. 8GiBreserve.
PTYhelper53200stillactive,elapsed~4700/10800seconds at13:25CDTSept16;
stopmarker/tmp/pixel-doom-stop-static-series restores4096. About100minleft.
Finaledit8sperstage(usingcapture.jsonoffset) to~/Videos/doom-terminals-staged-progression.mp4.
Validlowerclipslistedbelow;40second draftalreadyassembled. No commits.

## ACTIVE newestdriver79624 — large minimal-query stages

Driver29035 saved40,160,10240 successfully, then48k host failed to appear before
any terminals created. Retried fresh successfully: tool79624, record_stages.py
--counts48000 56000 64000 --output output/static-large-validated.
Current48kbuilding ~10k sofar. Keepmonitoringthroughfinish andrecordfinalization.
Workspace5 allruns; auto-focus oncebeforeplayback, wait/retryifhidden.

Validclips for finaledit (all1280x800, about10s):
output/static-validated-stages/40/progressive.mp4
output/static-validated-stages/160/progressive.mp4
output/static-inner-640/progressive.mp4
output/static-lightquery-2560/progressive.mp4
output/static-validated-stages/10240/progressive.mp4
edit_stages.py joins8s fromeach atnormalelapsedspeed30fps, consistentcountcaption
fromverifiedmetadata. Neededbecause10k liveHUDmissing inrecording. Countsnotfaked.
Draft output/static-small-stages-draft.mp4 (40s) createdsuccessfullytool90451.
Afterlargeclips, finalsave~/Videos/doom-terminals-staged-progression.mp4.
PTYhelper53200 remainsactive65536 (10800sdeadline); stopmarker
/tmp/pixel-doom-stop-static-series restores4096. No commits/installedconfigedits.

## CURRENT ACTIVE driver29035 — minimal geometry query; fixed-grid videos

48k static-staged-ws5 built all48,000 in1242.896s (20.7min), compCPU1208.21s.
First unrecorded hold failed on full j/clients timeout15s; no48k video.
Not a provenplaybackcrash: full metadata query includes perwindowfocusHistory
linear scans. Replaced with minimal O(n) Lua hl.get_windows classfilter reading
onlytitle,position,size via lazyobjects/repl. All static geometry validated
BEFORE playback; holdreads no nested IPC. 2560recordedtestpassed newquery,
clipoutput/static-lightquery-2560,10s. Compared42windowminimal/fullgeometry
exactmatch. Static-inner-640 also validclip. All outerclipsinvalidframing.
Cleanup now signalsclose-nested afterrecordingfinalized/enginestopped and
terminatesallownedservers/hubs upfront, beforewaiting individualprocesses.

Active record_stages.py tool29035 sequence40,160,10240,48000,56000,64000.
Output output/static-validated-stages/<count>. Each10sbaseline+10srecorded.
Workspace5 requiredvisible forplayback; focusonceaftergridready, waitifhidden
withoutdiscardinggrid. Userprefauto/manualquestionpendingnoanswer; default
briefautoswitchannounced. Keepmonitoring! Stoppingatfirstfailure; mustcollect
successfulclipsandedit8seconds each intoVideos finalprogression.
PTYhelper53200 stillactive65536; stopmarker/tmp/pixel-doom-stop-static-series
restores4096. No commits/installedconfigedits. Needfinalcleanupverification.

## NEW ACTIVE driver87548 — preserves grid when workspace5 hidden

Output output/static-staged-ws5, sequence48000,56000,64000,40,160,2560,10240.
Started large build first so can work background. Previousdriver48590 exited
on visibility change at40; no usablevideo. Now CaptureHidden retries hold
without destroying grid, waitsworkspace5. Active recordedclip deleted ifhidden.
Grid ready autofocusonce, then waitsifuserleaves. Need10s visible unrecorded,
then10svisible recorded for each. Parentworkspace5 requestedbyuser.
Helper53200 remainsactive (PTY65536). User questionauto/manualpending noanswer;
statedautomaticbriefswitchesafterwaiting, but userkeepsleavingworkspace5.
Do not repeatedlysteal focus; waitforuserwhenCAPTURE PAUSED appears.
Valid finalvideo source sofar output/static-inner-640/progressive.mp4 ONLY.
Outerclipsdistortedratio; don'tuse. Needfix backgroundcapture or uservisibility
if paused. Keepmonitoring largebuild; don'tabandon. No other run active.

## ACTIVE stage series on workspace5 — user requested workspace5

Interrupted48k unrecorded trial reached35,713 allocated before user said they
accidentally killed it. Cleaned fully; no playback sample from that run.
User then requested workspace5. Host moved there; hidden workspaces pause
nested rendering. Added visibility checks; optional input question offered
manual vs automatic switches, no answer yet; after reasonable wait stated
we use brief automatic switches. --focus-for-capture does that.
Outer desktop capture distorted proportions in workspace5; abandoned for final
clips. Wrong-workspace40 video deleted; outer40/160 clips NOT for final.
Direct nested capture static-inner-640 passed, correct image,1280x800,10sclip.
New record_stages.py sequence40,160,2560,10240,48000,56000,64000 launched.
Output output/static-staged-recordings/<count>; stages.json records completed.
All flags, --static-grid, --host-workspace5 --focus-for-capture --record.
Each stage builds black terminals in32windowbatches then10s unrecorded+10s
recorded playback. Same grid reused; inner screenshots skipped. Guard discards
recording on workspace switch. Visibility must remain5 during20s checks.
Stop-on-first-error driver. Need monitorthroughfinish, edit successfulclips8s
each withcountHUD, saveVideos, restorePTYhelper. Helpertool53200 stillactive,
marker /tmp/pixel-doom-stop-static-series restores4096;10800sautomatic deadline.
No commits. Installed desktopconfigunchanged. Hostprops scoped perwindow.

## ACTIVE fixed-grid experiment and staged recording

User approved static runs followed by 5–10s DOOM clips at increasing splits,
then cutting them into one progression video. New --static-grid creates final
black regions before launching engine, with 32-window placement batches.
--record-parent captures the host using outer compositor; for future clips
host opacity overridden per-window only (no persistent config changes).
640 smoke: output/static-series-640, 2.619s creation,10.0286s video,
zero geometry mismatches, outer capture1600x1000. All processes closed.
Current test: 48,000 static grid WITHOUT recording, main tool50773,
output/static-test-48000, --hold10 --timeout7200 with all optimization flags.
Temporary PTY helper tool53200 /tmp/pixel-doom-pty-static-series.py active;
restore4096 with /tmp/pixel-doom-stop-static-series or automatic10800s.
Keep monitoring! Do not leave large run unattended. No commits.
Plan collect clips40,160,640,2560,10240, then48k/56k/64k as validated feasible.
Honor8GiBreserve. Finalcut5–10s each, actual terminal count visible.

## Latest run FINISHED — 40,960 terminals; optional screenshot timeout

User resumed DOOM with 64,000 target. Monitored through stop and finalization.
Output: output/progressive-fast-64000-attempt; summary in run-summary.json.
All optimization flags enabled; host1280x800, scale3, 960x600 mosaic.
Reached40,960; hold() passed DOOM changing-frame, window count, source coverage,
and all actual window geometry checks BEFORE grim timed out at10seconds.
No stage5 record because old code appended it after screenshot. Do not claim
stage5 CPU/RSS/presentation samples. This is not a proven capacity ceiling.
Available memory ~11GiB near end; swap3GiB stable. Placement requests peaked
around6sec. Screenshot timeout cause beyond compositor load not established.
Video ~/Videos/doom-progressive-fast-64k-attempt.mp4, 4447.542856s (~74min),
751209534bytes. Last frame verified40,960 counter; visible scattered tile
artifacts mean synchronized/smooth playback is NOT established.
Finalizer27995/helper94755 completed; PTYmax4096. Main85202 exited1.
Launcher cleanup also timed out on Foot teardown; 270 remaining run-specific
Foot servers manually SIGKILLed. No private test processes remain.
No commits or installed desktop/config changes. No active large run.

Follow-up fixes: checkpoint_screenshot is nonfatal on timeout/nonzero/OSError,
removes partial files; validated stage persisted BEFORE capture. Test with real
fake-grim subprocess verifies timeout/failure and later recovery. Wrapper now
SIGKILLs its isolated launcher group after compositor cleanup to prevent Foot
orphans. Syntax checks passed. No further large run started.
Pre-run validation passed event flood, geometry benchmarks off/on including
full/max/tiled transitions, and640 recorded smoke with zero geometry mismatches.
Fast-floating microbenchmark timings varied; no precise speedup/FPS claim.

## CURRENT — user explicitly says DO NOT RUN YET

Latest steering: user accidentally killed run; apply more optimizations, but
NO game runs or graphical benchmarks until user ready (closing other programs).
All sessions24180,71799,93512 finished. PTYmax4096/nr5; no experimental processes.
Last output progressive-combined-64000-attempt:22,024allocated; lastcounter22,000;
456.142856sec video ~/Videos/doom-progressive-combined-64k-attempt.mp4 saved.
Log: Socket2 fd58 overflowed event queue, removing. No coredump. User separately
reports accidental termination; don't assert a capacity ceiling/regression.

Applied continuous event reader window_events.py; synthetic >9MiB flood passed
BEFORE no-run steering. No graphical tests since that instruction.
Added opt-in HYPRLAND_PIXEL_DOOM_FAST_FLOATING in private compositor:
1) direct floating fullscreen-handler lookup (same handler either layout choice),
2) early floating update avoids unused tiled workarea/workspace gap calculations.
Preserves client configure, damage and decorations. Private nested pixel windows
only. Saved hyprland-fast-floating.patch. Build -j2 passed, Python syntax passed.
NO runtime validation or performance claims for new fast-floating changes.
Preview --fast-floating option added, off by default.
benchmark_geometry.py now requires fresh --output and supports --fast-floating;
prepared tests add fullscreen/maximized/tiled transitions and combined-geometry
rejection during those states. Must run baseline+optimized after user resumes.
Keep already measured combined placement30% improvement distinct from new work.
Everything uncommitted. No installed desktop/config changes. Older ACTIVE
sections below are obsolete. Wait for user before any next game/GUI run.

## ACTIVE new recorded 64k attempt — fixed host and combined placement

User requested final optimization check, then run. MUST monitor until stop and
verify finalization/cleanup; user disliked ending turn after launch previously.
Wrapper PID3304286, main tool24180. Output output/progressive-combined-64000-attempt.
Args --levels7 --max-terminals64000 --hold5 --timeout7200 --allow-slow
--defer-texture --skip-unchanged-rules --combined-geometry --host-size1280x800
--record. Native pixel scale3, game960x600, host1280x800 fixed floating.
Temporary PTY capacity65536; helper tool93512 restores4096 on marker
/tmp/pixel-doom-stop-record-combined-64k or7500seconds.
Finalizer /tmp/pixel-doom-finalize-combined-64k.py watcheswrapper and saves video
~/Videos/doom-progressive-combined-64k-attempt.mp4 and JSON then signalshelper.
No installed config/binary changes, no commits, builds -j2 only.
Combined patch build passed; saved hyprland-combined-geometry.patch.
Three paired512window placement tests131072ops each: time2.305->1.611s,
CPU2.267->1.583s (~30% both). Tiny512colors exact, ordinaryguard passes.
640 progressive smoke recorded+passed with minimum3x3 preflight.
Docs README updated. This large run not yet validated.

## Follow-up diagnosis — fine-grid minimum height reproduced

Eight-window private probe with same Foot font/config: requested1x1 -> actual1x3,
2x2 ->2x3, 3x3 through8x8 all exact. Results output/fine-geometry-probe/results.json.
Durable probe_fine_geometry.py; no desktop config changes; all probe processes exited.
Foot render_resize enforces >=one text cell; pixelsize1 has actual cell height3.
Recorded layout host1017x556 gave777x485 mosaic: at40960,17,920 regions have
requested height2, below Foot minimum. This is a reproduced bug consistent with
the checkpoint failure; exact failed-run actual geometry was not saved.
1280x800 fixed host yields1168x730 mosaic, minimum3x3 even at64000. This geometry
calculation passes; new large fixed-host run NOT executed or claimed validated.
Current --fixed-host-size option only800x600: do NOT use as-is for fine-grid fix.
Added geometry-mismatches.json on failed checkpoint, preserving expected/actual
size+position and initial monitor/mosaic. No new performance speedup measured.
Next performance candidate: combine move+resize into one floating geometry
update; current dispatchers each call updateTarget. Must benchmark, not assume.
Video edit also complete: ~/Videos/doom-terminals-40960-60s.mp4 (60s,1800frames).

## Latest run FINISHED — 40,960 terminals, geometry validation failure

User asked why monitoring stopped; resumed and monitored through finalization.
Sessions57711,21368,21761 finished. No active experimental processes.
PTYmax4096, nr5. Original unchanged; no commits.
Video ~/Videos/doom-progressive-rules-64k-attempt.mp4:
4200.228567 seconds (~70min),660300936 bytes,1016x556,35FPS metadata.
Counter40,960 verified in extracted /tmp/doom-rules-last-frame.png.
Output output/progressive-rules-64000-attempt includes finalization.json,
progression.json, run-summary.json, compositor and Foot logs.
40,960 window count and source coverage passed; hold(level5) failed actual
window geometry check: first bad indices0..7. Actual/expected geometry not
saved, so don't assert root cause. DOOM stayed running; no confirmed crash.
Last completely validated checkpoint10,240 at176.123seconds vs356.095last run.
Same engine2490947 throughout; recent placement requests up to5.268seconds.
Last available memory~9GiB; reserve8GiB not reached. Timeout15sec not reached.
Next: save detailed geometry mismatch+monitor snapshots; reproduce fine tile
sizes with small test before a new large run. All ACTIVE entries below obsolete.

## ACTIVE recorded attempt with both optimizations

User explicitly requested another large run. Wrapper PID2490621, engine2490947,
tool session57711. Output: output/progressive-rules-64000-attempt.
Command: preview_progressive.py --levels 7 --max-terminals 64000 --hold 5
--timeout 7200 --allow-slow --defer-texture --skip-unchanged-rules --record.
Temporary PTY capacity 65536; privileged helper session21761 restores original4096
on /tmp/pixel-doom-stop-record-rules-64k or after7500seconds.
Finalizer /tmp/pixel-doom-finalize-rules-64k.py copies completed video and JSON to
~/Videos/doom-progressive-rules-64k-attempt.mp4 then signals PTY restoration.
Monitor progress, verify video and cleanup at end. Nothing committed.

## Latest completed work — 30-second video and further optimization

Video: ~/Videos/doom-terminals-25000-30s.mp4
Validated 30 seconds, 900 frames, 30 FPS, 792x532; counter retained.
Large attempt stopped at 25,504 allocated regions on a 2-second IPC timeout;
last completed placement 25,480 and displayed counter 25,456. Not a confirmed
DOOM crash or capacity ceiling. Original video retained in Videos.

Private opt-in --skip-unchanged-rules patch built with -j2 and saved.
Three paired 1,024-window lifecycle runs completed: mean compositor creation
CPU 5.98 -> 3.25 s (45.7% lower), cleanup wall 3.65 -> 1.16 s (68.2% lower),
cleanup CPU 3.30 -> .87 s (73.5% lower). Creation wall 15.34 -> 14.65 s,
mixed across pairs. Raw and summary JSON in output/rules-comparison-1024*.
Functional checks including dependent workspace rules and removal passed.
Playback comparison inconclusive: excluded missing-feedback/capture-timeout
runs. Nested presentation/capture stalls remain unresolved.

--allow-slow now uses a private-compositor-only 15-second IPC read timeout,
without replaying mutations. test_stress_ipc.py passed a 2.2-second response.
Combined smoke with --allow-slow --defer-texture --skip-unchanged-rules passed
40 -> 160 -> 161 real windows, zero geometry mismatches, clean shutdown:
output/rules-combined-smoke. No new large run started.

No active experimental sessions. No commits or installed desktop changes.
Next investigation: nested presentation/capture stalls and remaining Foot creation
cost, before another resource-intensive attempt. All ACTIVE entries below are
historical and superseded by this section.

## ACTIVE latest: video complete; optimizing population rule refresh

User: make30secondvideo THEN continueoptimization. NOnewlargeattemptrequested.
Large session71596 FINISHED at25,504allocated, lastcompletedplacement25,480,
lastHUD25,456; IPC2sectimeout, notDOOMcrash. Original2448.657s (40m49s),408MB
saved ~/Videos/doom-progressive-deferred-64k-attempt.mp4. Allnestedprocessesgone.
Finalizer59980 andhelper31634 FINISHED; PTYmaxrestored4096/nr5. Nocredentialsneeded.
30secondvideo COMPLETE verified900frames/30FPS/792x532/21.5MB:
~/Videos/doom-terminals-25000-30s.mp4. Trimblackmargins,speedramp4sinitial+9snext+
14sgrowth+3snormalend. Previewverified; linkalreadysharedincommentary.

Profileduringcreation~11k: updateDecorationValues10.25%,onWindowUpdate8.77%,
workspaceupdateWindows4.94%,getBoxWithIncludedDecos4.36%,etc.
New opt-in HYPRLAND_PIXEL_DOOM_SKIP_UNCHANGED_RULES inWindowRuleApplicator.cpp:
afterresetProps, ifpixel/nonX11/float+nested+ON_WORKSPACE, noreset effects,
no registeredworkspace-dependentwindowrules andnoexecdependencies, skip
appearanceupdate butkeepupdateRules event. Allothercasesoriginalpath.
Savedhyprland-skip-unchanged-rules.patch; builtprivatebinary-j2.
benchmark_launcher.py --skip-unchanged-rules added (defaultoff).
verify_batch_draw.py extended count-dependentrule:32windowsborder0,closeone=>
workspacew[31]border3,disablerule=>border0; checksnormalrulefallback.
ACTIVE session51705: benchmark1024on, deferredtexturealsoON, output/rules-skip-1024-on-1.
Needcheckfunctionalpass,thenmatchedbaseline1024 and2560on/off, fixed800x600host.
Avoidbigtests/sudonew. No commits/installedconfigchanges. NextsaveREADME/results.

AllolderACTIVEsectionsbelowarehistorical.

## LIVE — user requested recorded progression toward64000

Latest instruction: run it and record, see how far we get. Authorizedlargeattempt.
ACTIVE run tool71596, wrapperPID2137581, enginePID2137963.
At10,240 validstage356.095s,.977compositorcore,3415.7MiBRSS,46samplepresents/5s,
151.5665msmedianlatency,0geometrymismatches. Nowover25,000 (~40min); crossedprevious17,608stop.
Requests occasionally1.2s; --allow-slow keepsgoing. Memoryavailable~13GiB.
Profileanalysis savedgrowth-profile-summary.json withEXACTcompositor-symbols.txt.
Topcreationcosts:updateDecorationValues10.25%,onWindowUpdate8.77%,
workspaceupdateWindows4.94%,getBoxWithIncludedDecos4.36%. No liveedits. At17,608request606ms was
warningonly; continuednormally. Session71596stillactive; keepmonitoring.
Profile savedgrowth-profile.json:2430samples,0lost,duringcreation~11k.
Finalizer tool59980 ACTIVE; profiler90541 finished.
Automatic finalizer /tmp/pixel-doom-finalize-64k.py waits wrapperexit, copies
finalizedMP4+JSON into~/Videos/doom-progressive-deferred-64k-attempt.mp4,
thencreatesPTYrestoremarker. Still verifyhelper31634restore andcleanupafterend.
Command preview_progressive.py --levels7 --max-terminals64000 --hold5
--timeout7200 --allow-slow --defer-texture --record
--output output/progressive-deferred-64000-attempt.
Continueprogression,monitorengine/memory/presentation,savevideoeveniffailure.
No commits. Copyfinalizedvideo to~/Videos. Counteraboveimage, noidentityintro.
PRIVATEhelper session31634 ACTIVE, temporarykernelptymax4096->65536,
autorestores after7500sec. MUST create /tmp/pixel-doom-stop-record-64k afterrun,
poll31634,verifyptymax4096. Script/tmp/pixel-doom-pty-record-64k.py.
No persistentconfigchanges. Credentialalreadyusedsuccessfully; don't storeit.
InitialMemAvailable~23GB, disk1.4TBfree. Memoryreserve8GiB maintained.
No500msabort (--allow-slow); IPC/windowtimeout and2hbound stillcanstoprun.
Distinguish watchdog failure fromactualcrash. Earlierlarge17,608limitwas500ms.

Historical notes below include completedtests, notcurrentinstructions.

## COMPLETE — deferred GPU upload optimization, no active tests

User requested implementation toward64k. Kept tests <=2560. Everything cleaned.
Kernelptymax4096; no privileged changes; no commits or installed config edits.
Private compositor built and patched: HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE opt-in.
Patch experiments/pixel-doom/hyprland-defer-texture.patch (GLTexture.cpp/.hpp).
CPU-copy latest opaque1x1 update; ordinary bind materializes latest GPUtexture;
batched renderer bypasses uploads. Real PTYs/windows/framecallbacks retained.

Final matched FIXED800x600 tests,15splayback requested35FPS,CPUmean samples>=5s:
1024 baseline.3620 ->deferred.3114cores (14.0%less); samplepresentations335->345,
latency24.948->24.936ms. 2560 .9339->.8038cores(13.9%less);267->257presentations,
latency32.415->25.546ms. Startupunchanged. No consistentFPSgain. NOT64kproof.
Data output/deferred-texture-comparison.json and output/defer-fixed-*.
Earlier valid matchedpairs corroborated CPUreduction. Exclude all off/on-2
(stalledpresentation), andoff3/on3 (differenthostdimensions) fromcomparisons.
Harness fixes temporaryhost800x600 and checks first/last/continuousfeedback<=3s.
Functional screenshots verifycolors,updates,ordinaryfallbackAFTERupdates,text,
restorecolors,stacking,resize,close/reveal. Allpass.

Shared-color-cache experiment regressedCPU24%; flag remainsOFF, separatepatch
hyprland-texture-cache.patch retained forreproducibility. Don't combineflags.

Nativegeometry now supports--levels7 --max-terminals64000. regions.py uses
positiveareas/skipsnative1x1cells; test_regions.py covers9caps incl32000/63999/
64000 with exact1x1nativecoverage at64k. No64kwindowsopened.
preview_progressive.py nowhas--defer-texture opt-in; smoke session12081 passed
40->160->161 exactgeometry/sourcecoverage and cleaned nested processes.
Use --levels7 --max-terminals64000 --defer-texture forfuturetarget ONLY after
appropriate temporaryPTYcapacity and stagedperformancechecks. Prior actual
maximum17,608 stoppedby500mswatchdog, notenginecrash. No needcredentialsnow.
README updated. Remaining optimization avenues: cachegeometry/eligibility,
coordinatefreshupdates, profilelargersteadyplayback. Don't claim these done.

All earlier ACTIVE sections below are historical, not running tasks.

## ACTIVE optimization work — latest

User authorized implementation of next improvements. No large tests; cap2560.
Implemented opt-in HYPRLAND_PIXEL_DOOM_DEFER_TEXTURE in private GLTexture.cpp/hpp:
opaque 1x1 updates retain CPU color; normal bind materializes latest pixel on GPU.
Batched draws bypass per-texture binds. Real buffers released after CPU copy;
normal rendering, text fallback, and post-update fallback screenshot tests pass.
Patch experiments/pixel-doom/hyprland-defer-texture.patch. Built with-j2.
Earlier weak shared-color texture cache remains opt-in OFF, regressed1024 CPU24%,
no playback gain. Saved hyprland-texture-cache.patch; don't enable it.
First valid matched results:1024 .2972 ->.2539 compositor core;2560 .9318 ->.7423.
1024 presentationcount360->364/15sec latency24.464->24.8095ms;
2560 count276->278 latency29.079->25.428ms. Need repeats before stronger claims.
Artifacts texture-cache-1024-off-1/texture-cache-2560-off-1 are baseline;
defer-texture-{1024,2560}-on-1 are optimized.
Repeat sessions under24349 INVALID: off1024 had only39presents atlast2sec;
on1024 zero. Known nested startup stall also occurs unoptimized. All cleaned.
Hardened benchmark validation: first/last feedback within3sec and no3secgaps.
ACTIVE session43645 retry baseline1024 output/defer-texture-1024-off-3.
Continue matched repeats sequentially, no concurrentbuilds/benchmarks.
PTY limit unchanged4096, no privilegedhelperactive. Don't use/storecredentials.

Also implemented regions.py positive-area subdivision: levels7 target64000,
max min(64000,40*4**(levels-1)), skip1x1 boxes. test_regions.py passes native
coverage/nooverlap/positivearea at9caps incl32000/63999/64000, exact1x1at64k.
Need small progressive smoke after benchmarks. preview now --defer-texture opt-in.
No commits. Installed compositor/config untouched. Historical notes below stale.

## STOPPED — user requested video edit, no more scale runs

User says we are good here for now; speed up the latest recording.
No tests currently running. PTY max restored4096, PTY nr5. No credential used,
no password changes. Helper94536 completed/restored. Helper74020 never started
because sudo had no password; exited1. test_demo_loop.py passed.

Latest run session14489 stopped by 500ms response watchdog at17,608 allocated
regions, NOT engine/compositor crash. All nested processes cleaned. DOOM loop
fix survived about16minutes and multiple demo endings. Last fullyvalidated
stage10,240: .99core,3438MiB RSS,49 sampled presentations/5s,154.661ms median.
Artifact output/progressive-video-32000-loop-fixed/progression.json.
Original recording saved ~/Videos/doom-progressive-40-to-17608-attempt.mp4
(duration971.857s). HUD lags allocated count during last batch.
Completed ~/Videos/doom-terminals-progressive-30s.mp4: 30.000s,900frames,
1016x668,H264,24.7MB. Verified metadata and sampled frames. Cropped empty margins,
speed ramps preserve early coarse stages and final3sec normal-speed footage.

Uncommitted changes: stable demo-name buffer, regressiontest, optional
--allow-slow limited to disposable nested sessions; slow replies warn instead
of500ms abort. Max runtime now7200. Longer rerun WAS NOT STARTED, per user.

Historical notes below describe finished sessions, NOT active tasks.

## Latest update — demo loop fix and resumed scale test

The first 32,000 attempt FAILED at 6,736 allocated regions because DOOM's
initial defdemoname pointed into D_DoomMain's returned stack frame. This was
an engine demo-transition bug, not a demonstrated terminal-capacity limit.
bridge.c now provides a static demo1 name when looping. An accelerated test
completed 18,000 game ticks in one engine process (three demo endings), exit 0.
The normal production binary retains ordinary game pacing.

ACTIVE tool session 14489: preview_progressive.py --levels 6 --max-terminals 32000
--hold 5 --timeout 1200 --record --output output/progressive-video-32000-loop-fixed.
Engine PID 1808336. Survived three demo endings under load. At 10,240 verified
windows: 331.82s elapsed, 0 geometry mismatches, .99 compositor core,
3438MiB measured RSS, 49 sampled presentations in5s, median154.661ms.
Screenshot shows asynchronous patchwork updates, so NOT smooth playback.
Now above12,000 windows; continuing toward target.
Privileged helper 94536 remains active; restore PTY max by creating
/tmp/pixel-doom-pty-stop-long-20260915 after tests, verify max=4096.
Do not store credentials. No commits.

Older notes below are historical and may describe finished sessions.

# Resume notes

## LIVE attempt — read first

User: keep going until isolated run crashes or succeeds; target32,000 from earlier.
Keep continuous playing DOOM, progressive refinement, counter CLOSE above image.
No identity-card intro. Remain uncommitted.

ACTIVE exec3982: preview_progressive.py --levels6 --max-terminals32000 --hold5
--timeout1200 --record --output output/progressive-video-32000-attempt.
Uses exact-source coverage verification, geometry validation, per-stage CPU/RSS/
real presentation probe on terminal19. Events-based discovery replaces full client
list per batch; 159-terminal smoke passed. Batch8parents. Counter y=oy-32.
Watch progress through tool session and output/progression.json every~60sec.

PRIVILEGED HELPER NOW exec94536 (old53909 restored4096 andfinished):
/tmp/pixel-doom-pty-long-session.py raised4096->65536, auto-restores after3600sec.
MUST touch /tmp/pixel-doom-pty-stop-long-20260915 when testing ends, poll94536 and
verifykernel.pty.max4096. User authenticated twice. No persistent sysctl edits.

5120 COMPLETE in119.262sec,58presentations/5sec probe,72.4075ms medianlatency,
~1834.7MiB measuredRSS, .812core. Saved ~/Videos/doom-progressive-40-to-5120.mp4.
The10240attempt exec56495 was stopped around6,664 because original demo exits
normally after143.6seconds. NOT a compositor crash. Its summary marked stopped.
Fixed bridge.c optional PIXEL_DOOM_LOOP_DEMO: afterCreate singledemo=false,
demosequence=0 before eachtick, native attract advance directly selectsdemo1.
One engineprocess staysalive; recorded gameplay loops atnaturalend. No titlecards.
Progressive setsflag; other launchers unchanged. Nativeengine rebuilt successfully.
32000attempt is first long test of loop; small loop-enabledsmoke passed.
Now check enginealive eachcreationbatch too, not onlyholds.

Disposable nested cleanup: wrapper passesPIXEL_DOOM_DISPOSABLE_SESSION=1;
child finishesrecorder,stopsengine/HUD/hubs,terminatesFootservers, writes close-nested.
Wrapper terminates its compositor's processgroup, killsafter2s ifneeded; all Foot
servers exit. Avoids quadratic window teardown. Small159smoke verified cleanup.
Wrapper rejects reused output dirs withclose-nested marker. Main desktop untouched.
Failure metadata now written on exceptions, includes allocated_regions(lastbatch
maynotallvisible), stages,lastenginePID. Sourcecoverage asserts64k unique pixels.


## ACTIVE scale-up (latest user instructions)

User now requests continuing upward until the isolated run crashes or succeeds.
Keep continuous DOOM, real terminal refinement, live pixel counter. User requested
counter directly above image; fixed HUD y=max(monitor.y+5,oy-32), screenshot verified.
Batched creation: 8 parents/24 new children per clients query and compositor command.
Added exact --max-terminals including final 2/3-way split, --levels up to6,
--timeout up to1200. 161 smoke passed. Source-region complete coverage checked.
3,840 recording SUCCESS in78.5s; CPU.988core, RSS1429.7MiB,98 sampled presentations
in5s,medianlatency56.672ms. Earlier2560 reached45.35s (includes4x5s holds), faster
than old101s run. Artifacts output/progressive-video-3840; counter still old position
in that particular recording; new placement starts subsequent runs.

PRIVILEGED HELPER ACTIVE exec53909: pkexec python /tmp/pixel-doom-pty-session.py
User authenticated. Temporarily set kernel.pty.max from4096 to65536. Will restore
on /tmp/pixel-doom-pty-stop-scale-20260915 being created, or after1800sec (~30min).
MUST create marker when testing ends, poll helper53909 for restore, verify4096.
No persistent sysctl config edits. This is just capacity, not a32kload jump.

COMPLETED TEST exec50736: preview_progressive.py --levels5 --max-terminals5120
--hold5 --timeout300 --record --output output/progressive-video-5120.
5120 SUCCESS:119.262sec, .812core,1834.7MiB RSS,58 presents during5s hold,
medianlatency72.4075ms,zero geometrymismatch. Video copied to
~/Videos/doom-progressive-40-to-5120.mp4. Original paced cleanup completed.
ACTIVE TEST exec56495: --levels5 --max-terminals10240 --hold5 --timeout600 --record,
output/progressive-video-10240. At lastcheck reached2560 at43.728s. This run uses
new disposable nested cleanup: after recorder+engine+hubs stopped, child creates
output/close-nested marker; wrapper terminates its whole private compositor group
and SIGKILL after2s ifneeded. All terminal servers then exit. Avoids expensive
per-window closure. Main desktop never targeted. Wrapper env explicitly opts in.
After success next target32000 (levels6,max32000,timeout1200); don't stop early.
Progressive.py now checkpoints stage results and failure metadata (change landed
AFTER10240process started, so that run still only saves stages/checkpoints). Original 32k confidence not established.
No other test processes active; UI smoke84744 and3840run65164 cleaned up.


## Current presentation — corrected user intent

User clarified: DOOM must play with a few terminals, then become clearer as more
real terminals are added. They explicitly dislike the identity-card opening.
They also requested a terminal counter. Do not use the old run.py --intro for
this video. The performance objective remains unfinished, but latest work is the
progressive clarity sequence.

Implemented progressive.py and private nested wrapper preview_progressive.py.
One 320x200 native DOOM engine remains running. Each coarse terminal splits into
four regions: reuse parent and add three real Foot windows. hub.c optionally
reads sequence-marked 16-byte source-region records and averages native pixels
for each terminal. Counter shows N terminal pixels, excludes backdrop/HUD helpers.
No identity cards, title sequence, or game restarts. Default 40->160->640;
--levels4 adds2560. All nested, no installed desktop changes or commits.

SUCCESS recordings:
- ~/Videos/doom-progressive-40-to-640.mp4 (18.03s, 35captureFPS,632frames)
- ~/Videos/doom-progressive-40-to-2560.mp4 (101.03s,35captureFPS,3537frames)
Detailed artifacts output/progressive-video-{640,2560}/. Both video frames viewed;
640/2560 clarity increases, live counter visible. All stages verified sizes and
positions, one engine PID per run, changing source frames; cleanup empty.
2560 run stages at3.022,7.563,18.22,101.11s. Terminal creation slows considerably
at higher counts; final refinement alone ~80s. No retiming was applied.
Private wf-recorder capture uses nested Wayland screencopy, not host desktop.
/tmp/pixel-doom-wf-recorder-build/wf-recorder, upstream source in/tmp/pixel-doom-wf-recorder-src.
FFmpeg API compatibility patch saved wf-recorder-ffmpeg-compat.patch; no installation.
Original gpu-screen-recorder cannot find nested WAYLAND-1; replaced for this path.
Three test_transport.py tests passed, including real-PTY area averaging and
changing sampled regions without restarting hub. Python compile checks passed.
No active subprocess sessions remain. Next ask for feedback on actual video or
optimize progressive creation; do not resume identity-card presentation.

Performance continuation before clarification:
3072 hidden-startup repeat ON/OFF stalled, zero gameplay presentation feedback;
those summaries marked INVALID. Harness now requires sustained feedback,
records outer host visibility and exact playback monotonic time. Intro-visible
startup succeeds. Two matched visible-startup runs at2042x1120:
monitor-damage-intro-3072 CPU.936core,351feedbacks,latency36.768ms;
detailed-damage-intro-3072 CPU.930core,349feedbacks,latency36.762ms.
Whole-monitor redraw showed no useful gain. Keep optional and off by default.
Actual hidden-grid wakeup failure remains unexplained, not blamed on user.
Valid CPU profile has1765samples,no loss: NVIDIA9.5%,append8.1%,Wayland6.9%.
No32kreadiness claim. summarize_profile.py added for exact-binary symbol summaries.

## Latest checkpoint

Progressive intro implemented and 128-terminal functional smoke passed. User
wants readable real terminals, progressive population, then DOOM. Actual video
not yet captured. README now documents intro and actual-launcher measurements.

Foot geometry smoke fixed and passed (text fallback and resize); 2048 benchmark
output/geometry-2048-35fps did not establish CPU benefit; keep option off.

NEW batch draw compositor experiment: src/render/PixelDoomBatch.hpp and
Compositor surface color caching + Renderer append hook. Built successfully.
First smoke tests fell back: Foot has an unmapped child surface. Gate now rejects
mapped children only. output/batch-draw-smoke-6 confirms active batch drawing,
32 color/stack/resize/close checks passed, text fallback screenshot inspected,
128 DOOM clean. Private patch refreshed. No debug eligibility logs remain.
3072 batch draw test complete: output/batch-draw-3072-35fps. Startup50.653s,
20.012s playback, cleanup23.710s, Hyprmean.93784cores, IPCmax34ms, geometry0,
remaining0. Prior run .9747cores/63.18ms IPC. Presentation sample1056 excluding
first5: median commit-to-presentation latency46.38ms vs73.774ms before;
median interval35.133ms vs54.444ms. IMPORTANT earlier note below incorrectly
called73.774 an interval: it is LATENCY. Singlecomparison, not yet32kready.
Intro visual test complete: output/intro-visual,128cells. Identity and population
screenshots inspected, readable IDs/count/checkerboard correct. New32color
UPDATE verification passed too. No builds or test sessions currently active.
Next work for original scale objective: repeated matched batch off/on benchmarks
and profile remaining compositor hot paths; do not jump32k based on this result.
PTY max remains4096; no privileged change made. Actual intro recording pending.
All test windows cleaned up. No installed desktop changes or commits.


## ACTIVE objective: continue until ready for32,000 terminals (2:1), not ready yet

User explicitly requested keepgoinguntilconfident nextlarge2:1run (=32k). Wants
video progressively showing few readable real terminals, then many, thenDOOM.
Asked whether nestedlauncherischeating; explainedrealFootwindows/PTYs,sharedFoot
servers, isolatedHyprland; not32kprocesses. Useracceptedcontinuing.
ASYNC QUESTION PENDING: oneHyprlandinstance required vs multiplenestedacceptable.
No answer yet; continueoneinstancebydefault, don't silentlyswitcharchitecture.

Actual launcher nestedharness new benchmark_launcher.py. run.py CPU attribution
nowreads ipcinstance hyprland.lock PID (fallbackall recordedexplicitly). Exact
instanceassertedbyharness; don't mixparentCPU. SeparateprivateDBus/runtimeconfig.
128launcher15FPSsmoke passed.1024twopairs full launcherfontdiagnosticON20.096/20.049s
vsOFF16.634/16.617s. Allcleaned. Reports output/launcher-validation/.
2048fullDOOM35requestedFPS15s:startup33.494s,total57.399s,0geometrymismatches,
steadyHypr~.97core, IPCmax~24ms. Pure mainthreaduserspacesamplingvia perf_event_open
worksunprivileged(paranoid2), cpu_sample.py ring64pages100Hz. Profilelost0,1046
playbacksamplesmostlyrendering,NvidiaGLdriver16%,libc10%,surfacetree4%,renderWindow4%.
Reports output/scale-2048-35fps/. No large main-session tests.
3072fullDOOM35requestedFPS20s: startup50.684s,cleanup24.523s,RSS865MiB,
Hyprmean.9747core,IPCmax63.18ms,0geometrymismatch,allcleaned.
Onepixelpresentationfeedback250samples,excludingfirst5 median73.774ms/max147.681ms,
1discard. NOTenoughheadroomfor32k. output/scale-3072-35fps/.

Footrender.c added optin presentationinstrumentation (title match),LOG_WARN PD_PRESENT
becauseINFOsuppressed. --presentation-sample INDEX inrun/harness setsenvtitle forone
Footserver +--presentation-timings. Doesn'tretain terminalpointer acrosscallback.
This samplesrealpixelupdates, notfullmosaicFPS; staticcolorpixelsneedn'tupdate.
Smoke12835fps passed withfeedback. sources rebuiltin/tmp/pixel-doom-foot-build.

Intro implemented intro.py +run.py --intro. Fourreadable genuineFootpreviewwindows
showactualPTY/childPID,then3closeandoneprogresscounterremains. Counterqueriesactual
mosaicclasswindows excludingbackdrop, reflectsactualcount. Initialmosaiccheckerboard
showsindividualtilesbeingadded; realDOOMoverwritesit. Previewterminalsareseparatefrom
mosaiccells, counterexcludesthem. Intro4s +readycard2s thenDOOM. --record withintro
startsBEFOREintroandrecordscreationplus20splayback, noautomatictimelapse. Untested
actualrecording; nested128introfunctionaltestpassed,startup8.264s,cleanexit.
Needinspectvisualpreviewwhenconvenient; userprefersdesktopbarandblackbackground.

CURRENT experiment cacheunchangedFootviewportgeometry: addedwl_windowfields and
normalwayl_win_scale/fallbackinvalidations. EnvFOOT_PIXEL_DOOM_CACHE_GEOMETRY,
run/harness --cache-pixel-geometry defaultOFF. Avoidsscale/destinationmessageswhen
unchanged. Footbuilt-successfully. Modifiedtest_single_pixel.py --cache-pixel-geometry
exercisesblank->text->blankandresize360x200. Firstattemptfailedbecausetestresize
insertionmissed; fixed. ACTIVE exec30230 geometry-smoke-fixed nested128test+launcher.
Needpoll,inspectvalidationimage,thenmatched2048/3072performancebeforeenableanything.
Harnesscurrentlyrunsgeometrypreflightautomaticallywhenflagpresent(7s,BEFOREtimer).
Currentfoot-single-pixel.patch refreshed includespresentation+geometryoptions aswell
asoriginalSHM1x1/cache/noCallback. Needdocumentnewoptionsandresults.
No commits/push,installedconfigsunchanged,PTYlimit4096. No roothelperauthactive.

## Latest complete: Foot creation diagnostic optimization

User requested continuing with creation overhead. Added per-process creation CPU
measurements to benchmark_lifecycle.py. Profile1024 (batchingON) took13.07s,
Foot8.92CPU seconds, compositor4.59CPU seconds. Artifacts output/creation-profile/.
Foot server.c rechecks font monospacing on EVERY cloned per-window config;
config.c check_if_font_is_monospaced loads a font and rasterizes5glyphs eachtime.
Existing supported option tweak.font-monospace-warn=no skips this diagnostic.
New benchmark --mode font keeps compositor batchingON botharms, toggles only
that Footoption.128two pairs:creation~0.969s ->0.569s (~41% less), FootCPU.78->.385.
Font1024two pairs COMPLETE: creationmedian13.224s ->9.135s (~31% less),
FootCPU9.020s ->5.185s (~43% less). Individual optimized9.111/9.159s vs
baseline13.208/13.240s. All1024targetdimensions24x24 andfloatingchecks passed.
Added launcher default -o tweak.font-monospace-warn=no only for its own Footservers.
--font-monospace-check restores previousbehavior; metrics record thisflag.
No fonts/rendering/keybindingschanged. No installeddesktopconfig orbinarychanges.
Python compile andrun.py --help checks passed; README updated. Final verified
zero privatecompositors/ownwindows,responsiveparentIPC,PTY4096. No active sessions.
Artifacts output/font-summary.json,font-comparison-{128,1024}.json,font-test-cleanup.json.
No commits or large main-desktop tests. FullDOOMlauncherstartup gain NOTmeasured;
synthetic testusesoneFootserver,no launcher spawn delays. Next useful step: validate
full launcher in nested compositor and profile remaining mapping costs.

## Latest complete: 1024 lifecycle and address optimization confirmed

User resumed compositor optimization after image/tweet side quest.
Raised nested harness hard cap to1024, with8GiB available-memory guard and
45s creation deadline. Lifecycle1024 two pairs complete: cleanup medians
4.621s ->1.975s (~57% less), HyprCPU4.50s ->1.685s (~63% less).
Startup13.326s ->13.274s essentially unchanged. Stillroughlyquadraticcleanup.
Reports lifecycle-comparison-1024.json, lifecycle-summary-1024.json.

Added separate hyprland-fast-address.patch to private source ViewQuery.cpp.
Opt-in HYPRLAND_PIXEL_DOOM_FAST_ADDRESS parses canonical pointer string once,
then integer comparisons in existing linear window scan. No pointer dereference,
no address index/lifetime changes. Canonical form and existing filters preserved.
Rebuilt successfully, no installed changes. benchmark_lifecycle --mode address
keeps lifecycle batching ON botharms, toggles FAST_ADDRESS only, tests malformed/
noncanonical/closed addresses and title queries,16lookups pertarget, then actual
moves in batches4 with exactpositionchecks. Smoke16 passed. Three512pairs passed:
lookup8192requests median145.7ms ->14.75ms; placement20.16ms ->9.52ms.
Creation unchanged (~4.86s). Allwindows cleaned andanchor preserved.
Address1024 two pairs COMPLETE:16,384lookups544.51ms ->38.00ms (~14× faster),
placement69.76ms ->25.07ms (~64% less), map13.094s ->13.073s unchanged.
All selector checks and geometry checks passed. Addresscleanupnotcomparable
with lifecyclecleanup: placement changeswindowgeometry/renderingwork.
Reports address-summary.json, address-comparison-{512,1024}.json.
Finalcleanup verified no private compositor PIDs, no own desktop windows,
responsive IPC, PTY4096. Report followup-isolation-cleanup.json. Docs updated.
No running test/build sessions. No installed changes or commit/push.
Next bottleneck: creation/mapping cost itself; numericselectorhelpsplacementonly.
Stillno normal-rate largeplayback or32kfeasibilityproof; no countjump onmain desktop.

## Latest: private Hyprland batching built and tested in isolation

Private Hyprland 0.56.2 source commit efb50993780079460b0cbed1363e2166a2de1d9f:
/tmp/pixel-doom-hyprland-src; binary /tmp/pixel-doom-hyprland-build/Hyprland.
Release build succeeded (-j2, NO_XWAYLAND, NO_HYPRPM). All build/test sessions
completed. Saved patch hyprland-batch-lifecycle.patch; benchmark_lifecycle.py.

Opt-in HYPRLAND_PIXEL_DOOM_BATCH_LIFECYCLE=1 batches workspace rules/data,
global decoration updates, forced remaining-window size reports. Only floating
non-X11 pixel-doom-* windows. Default fixed deadline8ms; env
HYPRLAND_PIXEL_DOOM_BATCH_MS=0 restores initial idle-only prototype (no gain).
Fixed deadline doesn't slide with each new request. Experimental timing change.
HYPRLAND_PIXEL_DOOM_NESTED_ONLY=1 forces Wayland backend ONLY, no DRM attempts.
Harness uses isolated runtime/config/DBus, disables systemd env updates; hardcap512.

Initial smoke16 passed; idle-only128 A/B showed no cleanup gain (~0.114s).
Fixed8ms128: two pairs, cleanup median0.1292s ->0.0874s (~32% reduction).
Fixed8ms512: three pairs with reversed order on alternate repeat:
cleanup medians1.0646s ->0.5256s (~51% reduction), compositor cleanup CPU
0.96s ->0.38s (~60% less). Baseline range1.047–1.104s, enabled0.503–0.550s.
Startup inconsistent; don't claim startup improvement. Ordinary anchor survived
all target closures and closed normally. All geometry targets floating.
Wall cleanup includes same25ms settling and20ms polling; CPU tick10ms.
Some buffered file logs miss trailing counters; don't present all counters exact.
Static held-terminal nested tests, NOT liveDOOMFPS or proof32000feasible.
Artifacts output/lifecycle-summary.json, lifecycle-comparison-{128,512}.json,
lifecycle-* logs; idle-only originals saved as idle-lifecycle-*.

Final verified: zero private compositor PIDs, zero experiment/nested windows in
parent session, PTY max4096. No installed binaries/desktop config changes,
no large main-session test, no commits or push. Next useful work: investigate
placement/address lookup costs or cautiously validate larger nested lifecycle
scale; do not treat cleanup benefit as permission to run32000onmain desktop.

## Latest controlled scaling complete:1280 and2560, no furthercountincrease

Userproceed applied to newstartup/cleanupmitigations. Bothpartial320×100,gap0,
exact5×10,server-size128,placement-batch4,initialsize/pacedcleanupON,3FPS8s.
1280:startup28.399s,placement272.62ms,0resizes/mismatches,cleanup12.143s,
10/10groupssettled,maxgroupwait0.012s,RSS466.72MiB.
2560:startup57.195s,placement3209.88ms,0resizes/mismatches,cleanup45.867s,
20/20groupssettled,maxgroupwait1.296s,RSS881.81MiB.
Finalquery0.13ms,zeroownwindows. No PTYchanges,auth,commits.
Pacingworked butcleanup~4× for2×windowcount: deepercost persists. No matched
oldcleanupbaseline1280/2560, so NO proven cleanupgain. Partiallayoutnotvalid
fullimageFPSbenchmark; Hyprland~1core at2560briefplayback.
Reports output/paced-native-scaling.json and paced-native-{1280,2560}*.
Tolduser nextusefulinvestigation compositor repeatedglobalupdates, notcountjump.

## Latest: small-scale startup/cleanup mitigation implemented and tested

User asked how to resolve32k failure. Inspected exactHyprlandsource locally.
Initial20×20 clamp can be bypassed with static SIZE rule (previousMIN_SIZE failed).
run.py nowdefaultinitial-size-rule true; --no-initial-size-rule disables.
64native probe and640native(320×100,gap0,5×10cells) opened withZEROresizes and
zero geometrymismatches. Matched640 baselinehad640resizes. Placement86.72ms ->
68.31ms (~21%); startup15.314 ->15.182s. Bothserver-size128 (5servers),3FPS4s.
New--server-size1–640 (default640), hubcapacityserver_size+1.
Newdefault--paced-cleanup stopswriters/engine first thenservergroups sequentially,
waits up15s/group for noownwindows + responsiveclients before next.
.cleanup.json capturesgroupstatus. Smalltest5groups allsettled,3.492s vsold3.478s;
NO evidence largecleanupstall cured. No large rerun. Docs explicit limits.
Source onUnmap callsworkspace.updateWindows/updateWindowData andglobal all
decorations; repeatedfullwindowlist scans. ViewQuery addressselectorsalsolinear.
Likelydeeperfix coalesceglobalupdatesincompositor,requiresisolatedtests,NOTdone.
No installedHyprlandchanges/restarts/configedits. Defaultsrecommendedforfuture
smalltests; nextscalingtry server-size128,placement-batch4,doNOTjump32k.
Artifacts output/initial-size-comparison.json,size-rule-paced-cleanup-640*,
size-rule-baseline-640*,initial-size-rule-64*. Alltestwindowsclosed. No commits.

## Latest32k attempt: failedat6720; desktop recovered

User authenticated and reconfirmedproceed. Driver43245 completed exit1.
Opened6720/32000; timeoutinsideHyprland windowplacement (h.run socketrecv2s),
notmemoryguard orplayback. Lastcompletedbatch6656 took2556.98ms; previous
batches6528/6592~2.5s too. This shows placement costs beforeDOOM.
No32kvideo; playback/recorder neverstarted. Lastmemorysnapshot~21.8GiBavailable.
All terminalPTYs released; helperrestored4096 (PTYcount7 includesauthuntilclose).
Launcherexit291.058stotal,~47safterfailure report.90sdesktopcheck thenfailed
allrequests withtimeouts/EAGAIN. No compositorrestart.
EXTRA RECOVERY EXECSESSION92705 pollingclients every5s,up300s,needs3fast
emptydemowindowchecks. Check output/attempt-32000-recovery.json.
Desktoprecovery CONFIRMED:3fastchecks,zeroexperimentwindows,final0.2ms.
Approx 218.9s from failure report toconfirmedrecovery. Recoverysession92705
finishedsuccessfully. No furtherlarge launches.
Rawreport output/attempt-32000-35fps.json/stdout.log/lifecycle.json.
No commits. Needfinalexplain attemptfailed6720, no recording, controlwindow
management bottleneck; confirmdesktoprecovery beforeclosing taskifpossible.

## ACTIVE:32,000 real-time attempt queued for authentication

User clarifiedhalf=32,000 then real-time normalDOOMspeed thenexplicitproceed.
Confirmed request35FPS,no video retiming. Small64window native-half recording
smoke passed,ffprobe2560×1440h26435FPS4.14s; output/native-half-recording-smoke*.
Prepared driver output/benchmark-32000-driver.py. EXEC SESSION43245 WAITING AUTH.
VisibleFoot auth EXECSESSION84040. Lease dir/tmp/pixel-doom-32000-lease-o2uidsf8.
Reads output/active-32000-lease.json; temporary32768PTYlimit auto20min orrelease.
Afterauthentication starts320×100,gap0,35FPS,28s,SHM1x1ON,8GiBavailablememory
reserve,default600sstartupguard,IPCguards. No shellstopping. Recordingdelay5s,
20srecording to~/Videos/doom-32000-foot-live.mp4 if startupcompletes.
Metrics output/attempt-32000-35fps.json,stdout.log,lifecycle.json.
Driverfinallytoucheslease/release andverifies4096restored. Recordactualcount
ifguardsstop; neverclaim64k/1:1 orachieved35basedoncontainerFPS.
Authorizedlargeattempt despite known5120cleanupstall~116s. Monitorwithout
restartingHyprland. Authwait300s. Needpoll43245 andstdoutprogress afterauth.
No commits; userconfiguntouched.

## Active request: half-native 32,000 terminals and normal-framerate capture

User requested huge test then clarified HALF:32,000, target320×100, two
vertically averaged DOOMpixels/window (nottrue1:1). Asked async fullvs half and
real-time vs slowed-render smooth-export. Count answeredhalf; recording-method
question remains unanswered. No32k windows launched or elevatedPTYlimit yet.
Current4096limit. Prior5120shutdown stalled~116s, so cannot treat32kfullspeed
as established feasible. Need recording-method choice before expensive setup.
Found fixed65msbridgeframecap. bridge.c now accepts PIXEL_DOOM_OUTPUT_FPS,
allows1–35, preserves65mslegacycadence for<=15, uses1000/fpsms for>15.
run.py passesFPSenv on initialengine and restart, recordermax(30,FPS).
Built successfully; engine-only320×100 tests no windows:4ssampling saw47
framecontentchanges at15 and142 at35. Sharedbuffer reads can tear, so this
validates increasedcadence, NOT exactachievedFPS. output/engine-cadence-check.json.
Pythoncompiled before recorderargminorchange. No commits.

## Latest: 5,120 patched Foot benchmark completed, cleanup stalled then recovered

User explicitly authorized5000+ benchmark and authenticated temporaryPTY8192.
First attempt failed in new per-second profiling block accidentally placed in
startup before counters initialized. Fixed by movingblock to playback sampling;
16-window smoke exercised it successfully. Second authorization succeeded.
Successful5120(80×64),3FPSrequested,28.006s,SHM1x1ON,cache/callback flagsOFF.
Shellkept running. Startup152.657s,allgeometrycorrect,18processes/threads,
demoRSS873.41MiB.22visible steady samples t>=6: Hyprland0.89868cores,
Foot8serverscombined0.13335,totaldemo0.18829,shell0.00273.
Wholeplaybackdemo1.015cores due initialFoot7.6–8cores for2s,6cores at3s,
2cores at4s then~0.13. This identifies transientCPU, not rootcause.
MaxgameplayIPC51.23ms; startupmax3.13ms. Allplaybacksamplesvisible.
Cleanup launcher~35s afterreport; IPC then stalled. Finally3clientchecks
no remainingdemowindows,0.24/0.33/0.19ms. Reporttorecovery+limitrestore~116.4s.
PTY restored4096; helperreleased. No compositor/shell restart. NO furtherlaunch.
Reports output/benchmark-summary-5120.json and optimized-5120-3fps-current*.
Oldfailure logs separately optimized-5120-startup-instrumentation-failure*.
No commits. Next bottleneck is shutdown/window-destruction stall plus startup
Foot transient; playbacksuccess does NOT establish safe highercapacity.

## Latest: Ghostty vs optimized Foot comparison complete

User authorized recommended64-window comparison. New compare_terminals.py
uses1emulator process,64 live C helpers,150×90windows,15Hz syntheticOSC11.
Both10s visible and10s hidden. NOT fullDOOM/sharedhub/hold-mode comparison.
Foot visible:0.019core,34.38MiB,1thread; hidden0.012core.
Ghostty visible:0.8697core,755.89MiB,205threads; hidden0.139core,198threads.
Hyprland visibleFoot0.057/Ghostty0.088cores; hiddenboth0.017.
Same64helper processes excluded from emulator figures. Both singlePID64windows
verified and dimensions matched. Ghostty starts commands afterworkspacevisible;
initialprobes stoppedbeforemeasure until runner accounted for that.
KeepFoot. HiddenCPUspin not reproduced at64livehelpers;1920cause unresolved.
All ownwindowsclosed; ordinaryGhostty unaffected. No config/systemlimit edits.
Reports output/terminal-comparison-64.json and compare-{foot,ghostty}-64.json.
No commits. Next research should isolate sharedhub/hold-mode vs livehelper
behavior inFoot; do not extrapolate synthetic64 into maxcapacity.

## Latest profiling: Foot CPU saturation; workspace became hidden

User said proceed after1920 CPUjump. Added per-process CPU/RSS breakdown and
repeated1920 at15FPS18s. Foot servers each averaged~0.99core; hubs total0.043,
DOOM0.022, launcher0.003. Totaldemo3.038cores. All processes remained alive.
Workspace switched away at~3s: steady samples hidden, INVALID for comparison
with visible priorrun. Do NOT claim priorCPUjump cause proved, or improvement.
No more large tests after switch; all windows cleaned up.
Report output/profile-onepixel-1920.json. run.py now ALSO records per-second
process_cores (added after this run, syntaxchecked only), to separate startup,
visible and hidden intervals in future runs. Existing whole-run breakdown tested.
Source inspection: Foot arms per-terminal lower/upper delayed-render timers on
each PTY input. Disabling batching timers is a candidate only, not implemented
or established as cause. Frame callbacks may stop while hidden. Need controlled
visible/hidden comparison at small scale or eventloop profiling before a fix.
No installedFoot/config changes, no commits or count increases.

## Latest: 1,920 optimized terminals completed

User explicitly requested1920. Ran48×40,15 requestedFPS,18 seconds, SHM1x1 ON;
cache/callback experiments OFF. Startup51.94s; geometry all correct;8 processes.
Visible steady samples10–18s: Hyprland0.74025 cores; whole-run demo1.011 cores;
summed demoRSS353.18MiB; maxsampledIPC26.49ms. Shell stayed near idle.
Demo CPU rose sharply versus1280(0.323); cause not established, do not claim
linear scaling or achieved15 displayFPS. No unoptimized1920 comparison run.
All windows closed normally. Foot logs confirm fastpath active in all3servers.
Reports output/scale-onepixel-on-1920.json and scale-summary-1920.json.
No commits, no larger launches, no PTYlimit or desktop configuration changes.

## Latest: authorized step up to 1,280 completed

User asked to bump the count a bit. Ran 1,280 (40×32) at15FPS for18s per mode,
private Foot with SHM optimization ON then OFF. Both completed and cleaned up.
Steady visible seconds10–18: Hyprland0.4955 OFF ->0.43575 ON (~12% lower);
demo cores0.489 ->0.323 (~34% lower); summedRSS274.72 ->249.20MiB.
Startup33.714 ->32.962s; maxsampledIPC24.67 ->19.97ms; all geometry matched.
No further count increase. Cache/callback experiments stayed OFF.
Single short run per mode; no achieved-FPS measurement. Shell settled after
startup. No remaining demo windows. PTYlimit4096 unchanged; no commits.
Saved output/scale-comparison-1280.json and scale-onepixel-{on,off}-1280.json.
Older640-only scope notes below are historical; latest authorized test was1280.

## Latest follow-up: two experiments, neither a demonstrated win

Updated private Foot patch and run.py with opt-in --color-buffer-cache and
--no-pixel-frame-callback. Both default OFF. Installed Foot unchanged.
Test ceiling remained640; all runs18s at15FPS except160-window8s cache smoke.
Cache shares exact-color immutable protocol buffers, bounded4096/server:
Hyprland0.288 cores vs fresh SHM baseline0.205; demo RSS211 vs145 MiB. Regression.
Omitting callbacks: Hyprland0.197 vs0.205, demo0.173 vs0.175 cores. No convincing
win. Earlier apparent25% demo saving against older baseline was explicitly
corrected to user after fresh baseline. Do not claim it as an improvement.
Keep both flags disabled. Existing SHM1x1 optimization remains best measured.
Callback fallback protocol test PASSED: blank buffers had no frame callbacks;
ordinary text restored them. All demo windows closed after testing.
Reports output/further-rendering-comparison.json, callback-baseline-640.json,
cache-on-640.json, no-callback-640.json. Screenshot no-callback-640.png checked.
No larger tests, no commits, no desktop config edits or PTY-limit changes.

## Latest optimization complete: private Foot 1×1 buffers

Patch: foot-single-pixel.patch, against Foot 1.28.0 revision
2705e36f0ecf3ef50c13b41165de852f134859d6. Source /tmp/pixel-doom-foot-src;
binary /tmp/pixel-doom-foot-build/foot. README includes rebuild instructions.
Installed Foot untouched, opt-in --foot-binary plus --single-pixel-buffers.
No commits. Live tests remain capped at 640 while user uses the machine.

640 windows at 15 FPS, visible compositor samples seconds 10–18:
baseline 0.287 cores; enabled 0.201125; repeat 0.202375 (~30% less).
Demo cores 0.391 -> 0.232 / 0.233; summed RSS 166.71 -> 144.48 / 144.84 MiB.
One baseline and two enabled runs; do not extrapolate proof of 64k feasibility.
Protocol fallback test passed 1×1 -> text bitmap -> 1×1; text screenshot checked.
640 screenshot shows correct DOOM, black backdrop and desktop bar.
Durable reports: output/single-pixel-comparison.json, onepixel-off-640.json,
onepixel-on-640.json, onepixel-on-repeat-640.json. All runs finished normally.
PTY limit remains 4096. No shell restart or privileged changes this turn.

## Latest small-scale tests complete

User authorized small tests only; maximum640 windows. All demos closed, PTY
limit4096 unchanged, no shell restarts or privileged helpers. No commits.
Tiny-size rule probe did NOT bypass20x20 initial size; removed min_size1x1 rule.
Matched640-window comparison at15FPS (mean samples6<=t<12s): gap2 Hyprland
0.2965cores; gap0 0.2995cores. Frozen samples t>=14s:0.0067 and0.0cores.
Thus no meaningful benefit from removing gaps at this scale. MaxIPC<8ms.
3FPS test became hidden at~3s because workspace changed, leaving ZERO valid
visible steady-gameplay samples. Do NOT use it to claim an FPS improvement.
Added demo_visible to future samples and gap to report metadata. No more
previews were launched after detecting the workspace switch. Small tests remain
authorized, but avoid disrupting the user and never force refocus on a benchmark.
Summary: output/small-rendering-comparison.json. Raw reports small-gap2-15fps,
small-gap0-15fps, small-gap0-3fps.json. Scope for next test is a brief visible FPS
comparison when user is ready, or profiling under a separately controlled session.

## Active small-scale rendering tests

User explicitly authorized small-scale tests; cap640 windows, no PTY increase,
no shell restarts. Prior limit on larger stress tests still applies.
32-window80x64 size probe FAILED to avoid initial20x20 clamp with min_size1x1:
all32 still needed resize. Removed ineffective min_size rule. Final sizes correct.
640 windows, gap2,15FPS, freeze12s/end20s: small-gap2-15fps.json. Hyprland average
0.296cores during seconds6–12;0.007cores after14s frozen. Complete and cleaned.
Current session56733: same640 windows, gap0,15FPS, freeze12/end20. Next intended
small test: gap0,3FPS. New samples record demo_visible so workspace switches
can be excluded. No commits.

## CURRENT USER CONSTRAINT: no more desktop stress tests

User is doing other work and said “don't take it too far.” We agreed not to run
more demos or switch workspaces while they work. All test windows are closed;
PTY max4096, no privileged lease active. Continue only lightweight/offline work
unless the user authorizes more desktop testing.

Latest improvement: changed user-owned Window Shelf QML at
~/.config/omarchy/plugins/io.github.gardnmi.window-shelf/BarWidget.qml.
Its minimizedWindows binding scanned ALL Hyprland toplevels on every insertion;
it now concatenates the two managed special workspaces' toplevel lists instead.
Original backup: output/window-shelf-BarWidget.qml.before. Optimized copy:
output/window-shelf-BarWidget.qml.optimized. No package files changed.
Live640-window test completed before user restriction, shell left running:
shelf-fixed-640.json, shell averaged0.004 CPU cores, IPC max0.38ms. Promising
compared to old full-core results, but no matched larger A/B performed.
Do not claim all prior shell spin was definitively caused by this widget.

Added min_size={1,1} to temporary demo rule after inspecting EXACT installed
Hyprland source v0.56.2 (commit efb50993780079460b0cbed1363e2166a2de1d9f).
Default MIN_WINDOW_SIZE20 explains tiny windows opening20x20. minSize rule
should override it, but LIVE PROBE STILL NEEDED when user permits.
Source clones under /tmp/pixel-doom-hyprland-src and /tmp/pixel-doom-quickshell-src
are read-only research, no source patches made. Python syntax check passed.
All experiment changes remain uncommitted. No5120/10240 run this turn.


## Latest result: 5,120 playback succeeded; cleanup recovered

Run88812 reached5,120 windows, exact geometry,18processes, startup160.441s,
28.018s playback at3FPS; demoCPU1.192cores/RSSsum911.7MiB. StartupIPC max8.05ms,
playbackIPC max163.64ms. Hyprland and shell each~1core during late playback.
Recording output/doom-5120-paced.mp4 fully decoded,19.5s; sampled frame shows
clean DOOM and visible bar. Copied to~/Videos/doom-5120-paced.mp4.
IMPORTANT: gameplay succeeded but launcher EXITED1 because shell restart failed
during cleanup. All DOOM windows were gone; compositor remained busy temporarily.
Old shell eventually exited, Hyprland returned to0.085ms IPC. Manual
`omarchy restart shell` then succeeded; fresh shell CPU0.0. Lease28349 exited,
PTY max restored4096, used1. No10,240 launch attempted. No commits.
Added wait_for_desktop before cleanup shell restart: require three timely
client-list reads with no experiment windows (up to90s). Small160-window test
with setup-without-shell and placement-batch4 completed with exit0.
5120 cleanup improvement has NOT been revalidated at full scale.
Initial-size probe: target19x14 actually opens20x20. Therefore all5120 resizes
were still necessary in the successful run. Skip-resize optimization only helped
the640-window case; do not credit it for the5120 recovery. resized_from now logged.

## Current continuation

User said keep going and authenticated the new PTY lease. Lease session28349
sets limit16384, auto-restores after15min; send newline on completion to restore.
Active run session88812: 5120 hub windows,3fps,28s, setup-without-shell option,
recording output/doom-5120-paced.mp4 and metrics paced-5120.json.
New optimization skips resize when Foot already has correct dimensions. Tested
at640: all640 skipped, zero final mismatches. Startup samples add placement_ms,
placed count, resized count. New opt-in --setup-without-shell temporarily stops
Omarchy shell during creation and cleanup and restores it before gameplay and
on failure, while protecting active lock sessions. Small160 test passed.
Paced2560 with shell active passed, but shell stayed at1core during10s playback.
New5120 reached LIVE successfully, pending playback/cleanup/video validation. Added --placement-batch to allow fewer moves per compositor request on the next larger run.

## Active retry, authorized by user

User said “okay lets keep trying” after clarifying that 5,120 previously worked.
New comparison: original and hub at640 perform similarly; hub uses4 processes
versus644. Found Quickshell PID1458 consuming a whole CPU core even with no demo
windows. `omarchy restart shell` succeeded, idle shell CPU dropped to0.0. Cause
of shell spin is not yet established; do not blame the hub or compositor as fact.
New run.py metrics sample Hyprland CPU, shell CPU, compositor IPC latency; stop
a run after two consecutive >250ms pings. Added --freeze-after for static-frame
comparison, and --batch-pause (default0.1s/128windows). Frozen engines receive
SIGCONT before cleanup. Tests passed. 1,280 hub windows at5fps: startup15.4s,
6processes, animated Hyprland CPU about0.28cores, shell settled to0, typicalIPC
0.3ms. At freeze HyprlandCPU drops to0. Test cleaned up normally.
2,560 at 5 FPS completed: startup35.296s,10processes,1.179 demo cores;
Hyprland active gameplay ~0.7–0.8cores, IPC max26.93ms. Shell settles after6s.
After shell restart, pkexec authentication WORKED. Temporarily raised PTY limit
16384 using lease session72448. Retried5,120 hub at5fps with0.3s batch pauses.
This FAILED during placement after the last progress line3840, before LIVE.
Hyprland IPC timed out at2s. Launcher cleaned up; compositor took additional
time to drain work, then recovered to0.09ms IPC. All demo windows verified gone.
Lease exited and restored kernel.pty.max=4096; PTY count1. No auth helper remains.
The known-good earlier5,120 recording still stands; this failure is NOT proof
that5,120 is impossible. No10,240 or64,000 attempt performed.
New pacing: default64-window batches,10ms individual spawn delay; startup probes
abort on >250ms IPC. Failures now persist reports with opened count/error.
--fps now also controls legacy per-process clients. Small paced fallback test passed: 256windows at5fps; startup IPC0.09–0.26ms. Keep everything uncommitted. Do not launch another large run
without evaluating the startup pacing results and user desktop responsiveness.

## Prior session: shared renderer; stopped at user request

User reported severe desktop/input slowdown during the larger tests and asked
to stop. Do not resume launches without a new request. All experiment processes
and the visible authorization terminal were closed. Verified kernel.pty.max=4096,
PTY count=1, and no matching demo or authorization processes remain.
The pkexec request never authenticated and was cancelled. A subsequent visible
sudo terminal was also cancelled. `/tmp/pixel-doom-pty-lease-release` exists to
end the temporary helper if it ever starts; delete/recreate lease paths for any
future explicitly authorized attempt, rather than reusing stale state.

Implemented (still uncommitted): hub.c shared PTY renderer, foot_ipc.py direct
Foot 1.28 client protocol, transport tests, run.py hub default and process-mode
fallback, 320×200 grid support, partial-grid probes, memory/startup guards.
Foot color setting fixed from colors.background to colors-dark.background.
Transport tests passed; 32-window native-grid probe accepted exact 5×5 sizes.
New reports/videos live in ignored output/. hub-3840.json reports 14 processes,
64.421s startup, 1.16 demo CPU cores over30s. hub-2560.json reports 10 processes,
32.701s startup, 0.888 cores. Neither includes compositor/recorder resource use.
User-observed desktop slowdown means low demo CPU is NOT evidence of acceptable
system responsiveness. 64,000 windows were NOT attempted. Investigate compositor
cost and synchronized updates before further scaling. The 3,840 video exists
but has not been visually checked; 2,560 video shows gameplay with the old tiny
config-error text, which was subsequently fixed and verified in a small preview.

## Previous session (before shared renderer)

Current task completed: improve efficiency of the real-terminal DOOM prototype.
Everything remains uncommitted, per user request.

- Latest grid: 80×64 = 5,120 pixel terminals plus one black backdrop terminal.
- Eight Foot servers, up to 640 pixels per server. Single-server versions stall.
- Keep the desktop bar visible in recordings; wallpaper must not show through gaps.
- DOOM sources and shareware WAD: `~/Projects/terminal-doom`.
- The original 5,120-terminal version triggered transient unresponsive dialogs.
  The optimized run finished normally; sampled video frames show clean gameplay.
- Kernel pseudo-terminal limit is 4,096 after reboot. We temporarily raised it to
  8,192 for the last test. No persistent system configuration changed.
- Previous `/tmp` recordings were lost on reboot before they could be copied.
  Save new recordings and measurements in `experiments/pixel-doom/output/`.
- A stuck “Boomux Agent blocked” notification was dismissed through
  `omarchy notification dismiss 'Boomux Agent blocked'`; approval prompts can
  cause it to recur. The old pending pkexec authentication ended with reboot.

Completed optimizations:
- Foot `workers=0`: previously four rendering threads were created PER TERMINAL.
- Disable scrollback for the solid-color terminals.
- Short OSC 11 color update, no redundant clear-screen operation per frame.
- Batch 16 window placements per compositor request.
- Add `--metrics` and create output directories before launching.

640-pixel comparison: startup 14.142 -> 6.858 s; threads 3,208 -> 644;
12-second demo CPU time 9.70 -> 5.66 s (about 42% less).
Optimized 5,120-pixel run: startup 102.737 s; 5,131 threads/processes;
148.54 CPU seconds over 60.081 seconds, or 2.472 average CPU cores.
Measurements exclude compositor and recorder CPU; summed RSS double-counts
shared pages and should not be interpreted as unique physical memory.

Durable artifacts under ignored `output/`:
- `baseline-640.json`, `optimized-640.json`, `optimized-5120.json`
- `doom-5120-optimized.mp4` (2560×1440, ~18 s, verified full decode)
- `optimized-640.png`, `optimized-5120-contact.png`

All demo processes closed. `kernel.pty.max` restored to 4096 and PTY count was 1.
No privileged helper or authentication prompt remains active.
Pixel programs still poll ~15 times/second; eliminating those wakeups would be
a possible next optimization. No work on that is pending or claimed complete.
