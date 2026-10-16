"""Read the actual XLSX cached values; run the lab's unmodified validator and static infrastructure guard."""
import json, sys, subprocess, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/guard'))
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(ROOT/'deliverables/Eviaura_baogia.xlsx') as z:
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
    rows=[]
    for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:sheetData/s:row',ns):
        cells=['']*5
        for cell in row.findall('s:c',ns):
            col=''.join(filter(str.isalpha,cell.attrib['r'])); idx=0
            for c in col:idx=idx*26+ord(c)-64
            if idx>5:raise AssertionError('Extra column in BaoGia')
            v=cell.find('s:v',ns); typ=cell.attrib.get('t','n')
            if typ=='s':value=strings[int(v.text)]
            elif typ=='inlineStr':value=''.join(cell.find('s:is',ns).itertext())
            elif v is None:value=''
            elif typ=='n':value=float(v.text)
            else:value=v.text or ''
            cells[idx-1]=value
        rows.append({'line':int(row.attrib['r']),'cells':cells})
tmp=ROOT/'deliverables/quote-cached-values.json'
tmp.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
subprocess.run(['node','scripts/check_quote.mjs',str(tmp)],cwd=ROOT,check=True)
import guardpycfn
template=(ROOT/'infra/vbot.template.json').read_text(encoding='utf-8')
rules=(ROOT/'infra/security.guard').read_text(encoding='utf-8')
result=guardpycfn.validate_with_guard(template,rules,True)
if isinstance(result,str): result=json.loads(result)
(ROOT/'deliverables/guard-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
status=result['result']['container']['FileCheck']['status']
rule_results=[c['container']['RuleCheck'] for c in result['result']['children'] if 'RuleCheck' in c.get('container',{})]
print('Guard:',json.dumps({'file_status':status,'rules':rule_results}))
# Nonmatching resource filters appear as FAIL in verbose traversal, even in a passing rule.
if not result.get('success') or status!='PASS' or any(r['status']!='PASS' for r in rule_results):
    raise SystemExit('Guard found rule failures')
print('Actual XLSX cached values and project guard rules verified.')
