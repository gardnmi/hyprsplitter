"""Summarize sampled compositor main-thread IPs during measured playback.

Use symbols from the exact executable sampled, generated with nm -n -C.
Library buckets are modules, not functions; percentages are sampled CPU time.
"""
import argparse
import bisect
from collections import Counter
import json
from pathlib import Path


def summarize(profile, metrics, summary, symbols):
    p=json.loads(profile.read_text())
    m=json.loads(metrics.read_text())
    s=json.loads(summary.read_text())
    play_start=m.get('playback_started_monotonic',s['launcher_started_monotonic']+m['startup_seconds'])
    start=play_start+1
    end=play_start+m['sample_seconds']
    mappings=[]
    for line in p['maps'].splitlines():
        fields=line.split(maxsplit=5)
        lo,hi=(int(v,16) for v in fields[0].split('-'))
        mappings.append((lo,hi,int(fields[2],16),fields[5] if len(fields)>5 else '[anonymous]'))
    entries=[]
    for line in symbols.read_text().splitlines():
        parts=line.split(maxsplit=2)
        if len(parts)==3 and parts[1] in ('t','T','w','W'):
            entries.append((int(parts[0],16),parts[2]))
    entries.sort()
    addresses=[e[0] for e in entries]
    counts=Counter()
    for sample in p['samples']:
        if not start<=sample['time_ns']/1e9<=end:
            continue
        ip=sample['ip'];label='[unmapped]'
        for lo,hi,offset,name in mappings:
            if lo<=ip<hi:
                label=Path(name).name
                if label=='Hyprland':
                    j=bisect.bisect_right(addresses,ip-lo+offset)-1
                    label='Hyprland: '+(entries[j][1] if j>=0 else '[unknown]')
                break
        counts[label]+=1
    total=sum(counts.values())
    return {'samples':total,'lost':p['lost'],'scope':p['scope'],
            'buckets':[{'count':n,'percent':round(100*n/total,2),'name':name}
                       for name,n in counts.most_common(35)]}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--symbols',type=Path,default=Path('/tmp/pixel-doom-hyprland-symbols.txt'))
    args=parser.parse_args()
    profile=next(args.directory.glob('*-profile.json'))
    prefix=str(profile).removesuffix('-profile.json')
    result=summarize(profile,Path(prefix+'.json'),Path(prefix+'-summary.json'),args.symbols)
    print(json.dumps(result,indent=2))
