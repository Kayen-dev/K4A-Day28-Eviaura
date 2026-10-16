"""Run locally installed schema validator and persist results, without AWS API calls."""
import json, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.tools/lint'))
import cfnlint.api
matches=cfnlint.api.lint((root/'infra/vbot.template.json').read_text(),regions=['us-east-1'])
findings=[{'rule':m.rule.id,'message':m.message,'line':m.linenumber,'column':m.columnnumber} for m in matches]
(root/'deliverables/cfn-lint-validation.json').write_text(json.dumps(findings,indent=2),encoding='utf-8')
print(json.dumps({'validator':'cfn-lint 1.57.2','findings':findings,'bytes':(root/'infra/vbot.template.json').stat().st_size},indent=2))
sys.exit(bool(findings))
