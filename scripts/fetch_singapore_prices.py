"""Download public AWS Price List files only. No credentials or account APIs."""
import concurrent.futures, json, urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'.tools/pricing-sg'
OUT.mkdir(parents=True,exist_ok=True)
base='https://pricing.us-east-1.amazonaws.com'
def get(url):
    with urllib.request.urlopen(url,timeout=90) as r:return json.load(r)
index=get(base+'/offers/v1.0/aws/index.json')
services=['AmazonBedrockFoundationModels','AmazonBedrockService']
print('Related codes:',[k for k in index['offers'] if any(x in k.lower() for x in ['bedrock','codebuild','cognito','secret','kms','queue','cloudwatch','waf'])],flush=True)
def fetch(service):
    if service not in index['offers']:return service,'not in index'
    try:
        regions=get(base+index['offers'][service]['currentRegionIndexUrl'])['regions']
        target='us-west-2'
        r=regions.get(target) or regions.get('any')
        if not r:return service,'no SG/any regional catalog'
        url=base+r['currentVersionUrl']; d=get(url)
        (OUT/(service+'-'+target+'.json')).write_text(json.dumps(d),encoding='utf-8')
        (OUT/(service+'-'+target+'.url')).write_text(url,encoding='utf-8')
        return service,dict(products=len(d['products']),publicationDate=d.get('publicationDate'),url=url)
    except Exception as e:return service,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for result in ex.map(fetch,services):print(json.dumps(result),flush=True)
