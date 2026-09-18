"""Small shared passport, ready for other Hyprsplitter minigames."""
import json,os
from pathlib import Path

class Passport:
 def __init__(self,path=None):
  self.path=Path(path) if path else Path(os.environ.get('XDG_STATE_HOME',Path.home()/'.local/state'))/'hyprsplitter/passport.json'
  try:self.data=json.loads(self.path.read_text())
  except (OSError,ValueError):self.data={}
  if not isinstance(self.data,dict):self.data={}
  self.data.setdefault('games',{})
  self.game=self.data['games'].setdefault('quattro-jump',{'best':0,'completed':[],'stamp':False})
 def record(self,score,challenge,complete):
  self.game['best']=max(self.game['best'],score)
  if complete and challenge not in self.game['completed']:self.game['completed'].append(challenge)
  self.game['stamp']=all(i in self.game['completed'] for i in (1,2,3))
  self.path.parent.mkdir(parents=True,exist_ok=True)
  temp=self.path.with_suffix('.tmp');temp.write_text(json.dumps(self.data,indent=2)+'\n');temp.replace(self.path)
