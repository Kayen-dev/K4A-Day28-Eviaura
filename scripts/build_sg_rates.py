"""Extract selected billable AWS SKU rates. No API calls; inputs are saved public catalogs."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'.tools/pricing-sg'
rates={}
evidence=[]
def choose(key,service,usage,model=None):
    d=json.loads((SRC/(service+'.json')).read_text(encoding='utf-8'))
    found=[]
    for sku,p in d['products'].items():
        a=p['attributes']
        if a.get('usagetype')!=usage or (model and a.get('model')!=model):continue
        for term in d['terms']['OnDemand'].get(sku,{}).values():
            for dim in term['priceDimensions'].values():
                if float(dim['pricePerUnit']['USD'])>0:found.append((sku,p,dim))
    # First paid tier, without subtracting allowances; volume remains in the first tier.
    found.sort(key=lambda v:float(v[2]['beginRange']))
    if not found:raise ValueError((key,service,usage,model))
    sku,p,dim=found[0]
    rates[key]=float(dim['pricePerUnit']['USD'])
    evidence.append(dict(key=key,service=service,sku=sku,attributes=p['attributes'],unit=dim['unit'],rate=rates[key],range=[dim['beginRange'],dim['endRange']],source_url=(SRC/(service+'.url')).read_text(),publication_date=d.get('publicationDate'),checked_on='2026-10-16'))

choose('lambda_gbs','AWSLambda','APS1-Lambda-GB-Second-ARM')
choose('lambda_request','AWSLambda','APS1-Request-ARM')
choose('lambda_pc_gbs','AWSLambda','APS1-Lambda-Provisioned-Concurrency-ARM')
choose('api_request','AmazonApiGateway','APS1-ApiGatewayRequest')
choose('cognito_mau','AmazonCognito','APS1-CognitoEnterpriseMAU')
for key,usage in [('ddb_gb','APS1-TimedStorage-ByteHrs'),('ddb_wru','APS1-WriteRequestUnits'),('ddb_rru','APS1-ReadRequestUnits'),('ddb_pitr','APS1-TimedPITRStorage-ByteHrs'),('ddb_backup','APS1-TimedBackupStorage-ByteHrs'),('ddb_restore','APS1-RestoreDataSize-Bytes')]:choose(key,'AmazonDynamoDB',usage)
for key,usage in [('s3_gb','APS1-TimedStorage-ByteHrs'),('s3_put','APS1-Requests-Tier1'),('s3_get','APS1-Requests-Tier2'),('vector_gb','APS1-Vectors-TimedStorage-ByteHrs'),('vector_put_gb','APS1-Vectors-Put-Bytes'),('vector_query','APS1-Vectors-Request-Tier3'),('vector_scan_gb_t1','APS1-Vectors-Query-ProcessedBytes-Tier1'),('vector_scan_gb_t2','APS1-Vectors-Query-ProcessedBytes-Tier2')]:choose(key,'AmazonS3',usage)
choose('sqs_request','AWSQueueService','APS1-Requests-Tier1')
choose('sandbox_cpu_h','AmazonBedrockAgentCore','APS1-CodeInterpreter:Consumption-based:vCPU')
choose('sandbox_gb_h','AmazonBedrockAgentCore','APS1-CodeInterpreter:Consumption-based:Memory')
choose('nova_in_1k','AmazonBedrock','APS1-NovaLite-input-tokens')
choose('nova_out_1k','AmazonBedrock','APS1-NovaLite-output-tokens')
choose('embedding_in_1k','AmazonBedrock','APS1-TitanEmbeddingV2-Text-input-tokens')
choose('sonnet_in_million','AmazonBedrockFoundationModels','APS1-MP:APS1_InputTokenCount_Global-Units','Claude Sonnet 4.5')
choose('sonnet_out_million','AmazonBedrockFoundationModels','APS1-MP:APS1_OutputTokenCount_Global-Units','Claude Sonnet 4.5')
choose('image','AmazonBedrockFoundationModels-us-west-2','USW2-MP:USW2_created_image_stable_image_core-Units','SI-Core-V1')
choose('kms_key','awskms','ap-southeast-1-KMS-Keys')
choose('kms_request','awskms','ap-southeast-1-KMS-Requests')
choose('secret','AWSSecretsManager','APS1-AWSSecretsManager-Secret')
choose('secret_request','AWSSecretsManager','APS1-AWSSecretsManagerAPIRequest')
for key,usage in [('log_ingest_gb','APS1-DataProcessing-Bytes'),('log_storage_gb','APS1-TimedStorage-ByteHrs'),('metric','APS1-CW:MetricMonitorUsage'),('alarm','APS1-CW:AlarmMonitorUsage')]:choose(key,'AmazonCloudWatch',usage)
choose('egress_gb','AWSDataTransfer','APS1-DataTransfer-Out-Bytes')
choose('sg_to_oregon_gb','AWSDataTransfer','APS1-USW2-AWS-Out-Bytes')
choose('oregon_to_sg_gb','AWSDataTransfer','USW2-APS1-AWS-Out-Bytes')
for key,usage in [('waf_acl','APS1-WebACLV2'),('waf_rule','APS1-RuleV2'),('waf_request','APS1-RequestV2-Tier1')]:choose(key,'awswaf',usage)
choose('build_min','CodeBuild','APS1-Build-Min:Linux:g1.small')
out=ROOT/'deliverables/pricing-ap-southeast-1.json'
out.write_text(json.dumps(dict(region='ap-southeast-1',checked_on='2026-10-16',rates=rates,evidence=evidence),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rates,indent=2))
