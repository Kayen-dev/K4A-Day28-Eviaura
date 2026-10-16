import json,re,sys
from pathlib import Path
folder=Path('.tools/pricing-sg')
for spec in sys.argv[1:]:
    service,_,pattern=spec.partition(':')
    data=json.loads((folder/(service+'.json')).read_text(encoding='utf-8'))
    print('\n'+service)
    for sku,p in data['products'].items():
        if pattern and not re.search(pattern,p['attributes'].get('usagetype',''),re.I):continue
        attrs=p['attributes']
        terms=[]
        for term in data.get('terms',{}).get('OnDemand',{}).get(sku,{}).values():
            for dim in term['priceDimensions'].values():
                terms.append({k:dim.get(k) for k in ['unit','beginRange','endRange','pricePerUnit','description']})
        print(json.dumps({'sku':sku,'usage':attrs.get('usagetype'),'model':attrs.get('model'), 'group':attrs.get('group'),'operation':attrs.get('operation'),'prices':terms},ensure_ascii=False))
