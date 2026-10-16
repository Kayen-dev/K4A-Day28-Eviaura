"""Download public AWS Price List files only. No credentials or account APIs."""
import concurrent.futures, json, urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'.tools/pricing-sg'
OUT.mkdir(parents=True,exist_ok=True)
base='https://pricing.us-east-1.amazonaws.com'
def get(url):
    with urllib.request.urlopen(url,timeout=90) as r:return json.load(r)
index=get(base+'/offers/v1.0/aws/index.json')
services=['AWSLambda','AmazonS3','AmazonDynamoDB','AmazonApiGateway','AmazonCognito','AWSQueueService','awskms','AWSSecretsManager','AmazonCloudWatch','awswaf','CodeBuild','AmazonBedrock','AmazonBedrockAgentCore','AmazonBedrockFoundationModels','AWSDataTransfer']
tasks=[(s,'ap-southeast-1') for s in services]+[('AmazonBedrockFoundationModels','us-west-2')]
def fetch(task):
    service,target=task
    if service not in index['offers']:return service,'not in index'
    try:
        regions=get(base+index['offers'][service]['currentRegionIndexUrl'])['regions']
        r=regions.get(target) or regions.get('any')
        if not r:return service,'no catalog for '+target
        url=base+r['currentVersionUrl']; d=get(url)
        name=service if target=='ap-southeast-1' else service+'-'+target
        (OUT/(name+'.json')).write_text(json.dumps(d),encoding='utf-8')
        (OUT/(name+'.url')).write_text(url,encoding='utf-8')
        return service,dict(products=len(d['products']),publicationDate=d.get('publicationDate'),url=url)
    except Exception as e:return service,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for result in ex.map(fetch,tasks):print(json.dumps(result),flush=True)
