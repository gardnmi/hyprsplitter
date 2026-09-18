#!/usr/bin/env python3
"""Join verified recorded stages at normal speed with factual count captions."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--seconds',type=float,default=8)
p.add_argument('stages',type=Path,nargs='+')
a=p.parse_args();items=[]
for directory in a.stages:
    result=json.loads((directory/'progression.json').read_text())
    if result['status']!='complete':raise ValueError(f'Incomplete stage: {directory}')
    stage=result['stages'][-1]
    if stage['geometry_mismatches'] or not stage['sampled_presentations']:
        raise ValueError(f'Unverified playback: {directory}')
    source=directory/'progressive.mp4'
    capture=json.loads((directory/'capture.json').read_text()) if (directory/'capture.json').exists() else {}
    offset=1+capture.get('playback_offset',0)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(source)]))
    if duration<a.seconds+offset:raise ValueError(f'Clip too short: {source}')
    items.append((stage['terminals'],source,offset))
items.sort()
a.output.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='pd-edit-') as tmp:
    parts=[]
    for i,(count,source,offset) in enumerate(items):
        part=Path(tmp)/f'{i}.mp4';parts.append(part)
        caption=f'{count:,} terminals'
        filters=("scale=1280:800,setsar=1,fps=30,"
            "drawbox=x=0:y=0:w=iw:h=100:color=black:t=fill,"
            f"drawtext=text='{caption}':x=160:y=68:fontsize=22:fontcolor=white")
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(offset),'-i',str(source),
            '-t',str(a.seconds),'-vf',filters,'-an','-c:v','libx264','-preset','fast','-crf','18',
            '-threads','2','-filter_threads','1','-pix_fmt','yuv420p',str(part)],check=True)
    listing=Path(tmp)/'parts.txt';listing.write_text(''.join(f"file '{part}'\n" for part in parts))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0',
        '-i',str(listing),'-c','copy','-movflags','+faststart',str(a.output)],check=True)
a.output.with_suffix('.json').write_text(json.dumps(dict(seconds_per_stage=a.seconds,
    counts=[count for count,_,_ in items],sources=[str(source.resolve()) for _,source,_ in items],
    speed='normal elapsed time; no interpolation',count_caption='postproduction caption from verified stage metadata'),indent=2)+'\n')
print(a.output)
