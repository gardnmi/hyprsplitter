#!/usr/bin/env python3
"""Build and record independent fixed grids, stopping at the first failed stage."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--counts',type=int,nargs='+',required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--fps',type=int,default=35)
p.add_argument('--prestart-record',action='store_true')
a=p.parse_args();a.output=a.output.resolve()
a.output.mkdir(parents=True,exist_ok=False)
results=[]
for count in a.counts:
    output=a.output/str(count)
    command=[sys.executable,str(ROOT/'preview_progressive.py'),'--static-grid',
        '--levels','7','--max-terminals',str(count),'--hold','10','--timeout','7200',
        '--allow-slow','--defer-texture','--skip-unchanged-rules','--combined-geometry',
        '--fast-floating','--host-size','1280x800','--host-workspace','5',
        '--focus-for-capture','--record','--output',str(output)]
    command.extend(['--fps',str(a.fps)])
    if a.prestart_record:command.append('--prestart-record')
    print(f'STAGE START: {count} terminals on workspace 5',flush=True)
    started=time.monotonic()
    result=subprocess.run(command)
    row=dict(terminals=count,returncode=result.returncode,seconds=time.monotonic()-started,output=str(output))
    results.append(row)
    (a.output/'stages.json').write_text(json.dumps(results,indent=2)+'\n')
    print('STAGE END: '+json.dumps(row),flush=True)
    if result.returncode:
        sys.exit(result.returncode)
