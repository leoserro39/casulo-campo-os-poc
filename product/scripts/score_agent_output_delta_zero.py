#!/usr/bin/env python3
import json,argparse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path.cwd()
BAD=["production ready","client validated","validated hallucination reduction","automatic merge","commercial claim"]
SEC=["operational state","evidence used","evidence gaps","gate decision","allowed actions","blocked actions","risk of hallucination","next safe step"]
ap=argparse.ArgumentParser()
ap.add_argument("--output-file",default="product/agent_runs/real_case_001/model_output.md")
ap.add_argument("--out",default="product/agent_runs/real_case_001/delta_zero_score.json")
a=ap.parse_args()
t=(ROOT/a.output_file).read_text(encoding="utf-8") if (ROOT/a.output_file).exists() else ""
low=t.lower()
hits=[x for x in BAD if x in low]
sh=[x for x in SEC if x in low]
structure=len(sh)/len(SEC)
gate=1.0 if not hits else 0.0
oqi=round(.25*(.7 if "evidence" in low else .3)+.25*gate+.2+.15*structure+.15*gate,4)
res={"version":"delta_zero_score.v0.1","generated_at":datetime.now(timezone.utc).isoformat(),"scores":{"forbidden_pattern_hits":hits,"required_section_hits":sh,"oqi":oqi,"ohri":round(1-oqi,4),"zpi":round(.3*structure+.7*gate,4),"ready_for_client_claim":False,"ready_for_production":False}}
out=ROOT/a.out; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(res,indent=2,ensure_ascii=False))
