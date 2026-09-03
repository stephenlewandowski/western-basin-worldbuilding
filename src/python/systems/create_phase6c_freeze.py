"""Materialize a hash-protected Phase 6C acceptance manifest."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]; R=ROOT/'reports'
def main():
 src=json.loads((R/'ecology_scenario_manifest.json').read_text()); arts=dict(src['artifacts'])
 # Include the validated artifact check and scenario QA report as acceptance evidence.
 for rel in ['reports/ecology_scenario_artifact_check.json','reports/ecology_scenario_qa.md']:
  p=ROOT/rel; arts[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 out={'accepted_phase':'6C','baseline':'Ecological Futures, 2050 / 2075','status':'ACCEPTED / FROZEN','generated':'2026-09-03','counts':src['counts'],'artifacts':{rel:(meta.get('sha256') if isinstance(meta,dict) else meta) for rel,meta in arts.items()}}
 (R/'phase6c_ecological_futures_freeze_manifest.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'artifacts':len(arts),'status':out['status']}))
if __name__=='__main__': main()
