"""Read Omarchy's palette; never modify the desktop theme."""
import os
from pathlib import Path
import tomllib

DEFAULTS={'background':'#1f1f28','dark_background':'#17171e','foreground':'#dcd7ba',
          'accent':'#dcd7ba','muted':'#54546d','red':'#c34043','yellow':'#c0a36e',
          'orange':'#c17158','green':'#76946a','cyan':'#6a9589','blue':'#7e9cd8',
          'brown':'#60382c','bright_yellow':'#e6c384','bright_green':'#98bb6c'}


def load():
    values=dict(DEFAULTS)
    state=Path(os.environ.get('XDG_STATE_HOME',Path.home()/'.local/state'))
    config=Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))
    for root in (state,config):
        try:
            data=tomllib.loads((root/'omarchy/current/theme/colors.toml').read_text())
            for key,value in data.items():
                if isinstance(value,str) and len(value)==7 and value.startswith('#'):
                    int(value[1:],16);values[key]=value
            break
        except (OSError,ValueError,tomllib.TOMLDecodeError):continue
    return {k:tuple(int(v[i:i+2],16)/255 for i in (1,3,5)) for k,v in values.items()}


PALETTE=load()
FONT='monospace'  # Fontconfig resolves the user's Omarchy font.


def rgb(name):return PALETTE[name]
def rgba(name,alpha=1):return (*rgb(name),alpha)
def mix(a,b,amount):return tuple(x*(1-amount)+y*amount for x,y in zip(rgb(a),rgb(b)))
