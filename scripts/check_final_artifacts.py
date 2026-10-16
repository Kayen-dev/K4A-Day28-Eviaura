"""Cross-check final submission names, XLSX values and PowerPoint content against cost JSON."""
from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET,re
root=Path(__file__).resolve().parents[1]
out=root/'deliverables'
m=json.loads((out/'cost-model.json').read_text(encoding='utf-8'))
q=json.loads((out/'quote-validation.json').read_text(encoding='utf-8'))
assert m['region']=='ap-southeast-1' and q['ok'] and q['summary']['total']==m['summary']['total']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(out/'G03_baogia.xlsx')==digest(out/'Eviaura_baogia.xlsx')
pptx=out/'G03_slide.pptx'
with zipfile.ZipFile(pptx) as z:
    slides=sorted(n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
    assert len(slides)==15
    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
    texts={n:' '.join(ET.fromstring(z.read(n)).itertext()) for n in slides}
    amount=f'{m["summary"]["total"]:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
    assert amount in texts['ppt/slides/slide1.xml'] and amount in texts['ppt/slides/slide12.xml']
    required=['compute','llm','gateway','load_balancer','authn','authz','database','vector_db','object_storage','cache_queue','sandbox','connectors','secrets_kms','backup_dr','monitoring','governance','network','cicd','ops_labor']
    assert all(c in texts['ppt/slides/slide4.xml'] for c in required)
    assert 'Singapore' in texts['ppt/slides/slide4.xml'] and 'Oregon' in texts['ppt/slides/slide4.xml']
    assert len([n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)])==15
    size=ET.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz',ns)
    assert (int(size.attrib['cx']),int(size.attrib['cy']))==(12192000,6858000)
assert pptx.stat().st_size<10_000_000
report={'region':m['region'],'total_usd':m['summary']['total'],'quote_pass':q['ok'],'selected_rates':len(json.loads((out/'pricing-ap-southeast-1.json').read_text(encoding='utf-8'))['evidence']),'slides':15,'pptx_bytes':pptx.stat().st_size,'xlsx_sha256':digest(out/'G03_baogia.xlsx'),'pptx_sha256':digest(pptx),'note':'Cross-file consistency check; no native Excel/PowerPoint or live AWS validation.'}
(out/'submission-consistency.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
