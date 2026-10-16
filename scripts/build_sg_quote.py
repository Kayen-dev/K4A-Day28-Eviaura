"""Reprice the exact 27-line workload against Singapore public SKU snapshots."""
from pathlib import Path
import json, shutil
from decimal import Decimal, ROUND_HALF_UP
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'
archive=OUT/'archive/us-east-1'
archive.mkdir(parents=True,exist_ok=True)
for f in ['cost-model.json','Eviaura_baogia.xlsx','BAOGIA.md','VALIDATION.md','quote-validation.json']:
    src=OUT/f; dst=archive/f
    if src.exists() and not dst.exists():shutil.copyfile(src,dst)
base=json.loads((archive/'cost-model.json').read_text(encoding='utf-8'))
catalog=json.loads((OUT/'pricing-ap-southeast-1.json').read_text(encoding='utf-8'))
r=catalog['rates']; ev={e['key']:e for e in catalog['evidence']}
money=lambda n:float(Decimal(str(n)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
rows=[]; formulas=[]; row_evidence=[]
def add(comp,name,note,formula,keys=(),region='ap-southeast-1'):
    val=money(eval(formula,{'__builtins__':{}},{}))
    urls=list(dict.fromkeys(ev[k]['source_url'] for k in keys))
    skus=list(dict.fromkeys(ev[k]['sku'] for k in keys))
    evidence='; '.join(urls) if urls else ('NA' if comp in ['ops_labor','contingency'] else base['sources']['bedrock'])
    rows.append([comp,name,region+'; '+note+(' SKU: '+', '.join(skus) if skus else ''),val,evidence])
    formulas.append('=ROUND('+formula+',2)')
    row_evidence.append(skus)
N=base['summary']['monthly_requests']; f=1.05*1.05
inp=base['inputs'].copy();inp.update(sonnet_input_million=r['sonnet_in_million'],sonnet_output_million=r['sonnet_out_million'],nova_input_million=r['nova_in_1k']*1000,nova_output_million=r['nova_out_1k']*1000)
nova=sonnet=all_sonnet=0
tasks=base['tasks']
for t in tasks:
    a=t['requests']*t['input']/1e6;b=t['requests']*t['output']/1e6
    s=a*r['sonnet_in_million']+b*r['sonnet_out_million'];all_sonnet+=s
    if t['model'].startswith('Nova'):
        nova+=a*inp['nova_input_million']+b*inp['nova_output_million'];sonnet+=s*.1
    else:sonnet+=s
tasks[-1]['model']='Nova Lite + Stable Image Core (us-west-2)'
add('compute','Chat streaming Lambda ARM','512 MB × 20 s × 352000 × 1.05 staging; ARM on-demand execution + requests',f'.5*20*{N}*1.05*{r["lambda_gbs"]}+{N}*1.05*{r["lambda_request"]}',('lambda_gbs','lambda_request'))
add('compute','Background worker và chờ sandbox','19% × 352000 × 120 s × 1 GB × 1.05; worker billed during sandbox wait',f'{N}*.19*120*1.05*{r["lambda_gbs"]}+{N}*.19*1.05*{r["lambda_request"]}',('lambda_gbs','lambda_request'))
add('compute','Provisioned concurrency giờ hành chính','10 slots × 0.5 GB × 220 h × 3600 × 0.0000041593 USD/GB-s',f'10*.5*220*3600*{r["lambda_pc_gbs"]}',('lambda_pc_gbs',))
add('llm','Nova Lite: L1/L2/L5','APAC inference from Singapore; 0.081 input / 0.324 output USD/M tokens; 5% retry + 5% staging, no cache discount',f'{nova}*{f}',('nova_in_1k','nova_out_1k'))
add('llm','Sonnet 4.5: L3/L4 và escalation','Global inference from Singapore; 3 input / 15 output USD/M; 10% escalation + 5% retry + 5% staging; not Singapore-only residency',f'{sonnet}*{f}',('sonnet_in_million','sonnet_out_million'))
add('llm','Stable Image Core: sinh ảnh','3520 images × 0.04 USD × 1.05 retry × 1.05 staging; stability.stable-image-core-v1:1; replaces EOL Nova Canvas',f'3520*{r["image"]}*{f}',('image',),region='Primary ap-southeast-1; image inference us-west-2')
add('gateway','API Gateway REST + router','1M calls × 4.25 USD/M; managed regional multi-AZ; quota in database',f'1000000*{r["api_request"]}',('api_request',))
add('load_balancer','Managed regional request distribution','Đã nằm trong API Gateway REST multi-AZ, TLS and routing; no separate ALB','0',('api_request',))
add('authn','Cognito enterprise federation','2100 federated MAU × 0.015 USD; corporate IdP enforces MFA; no allowance deducted',f'2100*{r["cognito_mau"]}',('cognito_mau',))
add('authz','RBAC/ABAC và ACL kiểm tra lại','Đã nằm trong compute/database; identity-derived tenant/user, source ACL recheck','0',('ddb_gb',))
add('database','DynamoDB Standard on-demand','50 GB × 0.285 + 8M WRU × 0.71/M + 20M RRU × 0.1425/M; prod+staging; managed multi-AZ',f'50*{r["ddb_gb"]}+8000000*{r["ddb_wru"]}+20000000*{r["ddb_rru"]}',('ddb_gb','ddb_wru','ddb_rru'))
gb=1e6*6272/2**30
add('vector_db','S3 Vectors storage and ingestion','1M × 6272 bytes / GiB × (0.066 storage + 20% × 0.219 PUT/GB) × 1.05 staging; batched PUT',f'{gb}*({r["vector_gb"]}+.2*{r["vector_put_gb"]})*1.05',('vector_gb','vector_put_gb'))
scan=(100000*5248*r['vector_scan_gb_t1']+900000*5248*r['vector_scan_gb_t2'])/2**30
add('vector_db','S3 Vectors queries','300000 × (0.0000027/request + index scan: 100K/900K vectors × 5248 bytes, 0.000004278/0.000002139 USD/GB); top20 IDs',f'300000*({r["vector_query"]}+{scan})',('vector_query','vector_scan_gb_t1','vector_scan_gb_t2'))
add('object_storage','Workspace quota đầy đủ + KB + staging','20300 GB × 0.025 USD/GB-month; full 2000 × 10 GB user quota',f'20300*{r["s3_gb"]}',('s3_gb',))
add('object_storage','S3 object requests','2M PUT/LIST × 0.005/1000 + 10M GET × 0.0004/1000',f'2000000*{r["s3_put"]}+10000000*{r["s3_get"]}',('s3_put','s3_get'))
add('cache_queue','SQS + TTL cache','3M standard requests × 0.40/M; TTL cache nằm trong database; encrypted queue + DLQ',f'3000000*{r["sqs_request"]}',('sqs_request',))
add('sandbox','AgentCore Code Interpreter VPC','35200 × 120s / 3600 × (1 active vCPU × 0.0895/h + 4 GB × 0.00945/h) × 1.05 staging; isolated VPC',f'35200*120/3600*({r["sandbox_cpu_h"]}+4*{r["sandbox_gb_h"]})*1.05',('sandbox_cpu_h','sandbox_gb_h'))
add('connectors','Delegated OAuth Lambda workers','1M × 1 GB × 2s × 0.0000133334 + 0.20/M requests; overhead beyond background duration',f'1000000*2*{r["lambda_gbs"]}+1000000*{r["lambda_request"]}',('lambda_gbs','lambda_request'))
add('secrets_kms','KMS và OAuth app secrets','2 keys × 1 + 1M KMS × 0.03/10000 + 10 secrets × 0.40 + 100K API × 0.05/10000',f'2*{r["kms_key"]}+1000000*{r["kms_request"]}+10*{r["secret"]}+100000*{r["secret_request"]}',('kms_key','kms_request','secret','secret_request'))
add('backup_dr','PITR + object versions + restore drill','50 GB PITR × 0.228 + 4000 GB S3 versions × 0.025 + 50 GB backup × 0.114 + 10 GB restore × 0.171; same-region',f'50*{r["ddb_pitr"]}+4000*{r["s3_gb"]}+50*{r["ddb_backup"]}+10*{r["ddb_restore"]}',('ddb_pitr','s3_gb','ddb_backup','ddb_restore'))
add('monitoring','CloudWatch + S3 audit 12 tháng','20 GB ingest × 0.70 + 20 GB logs × 0.03 + 20 metrics × 0.30 + 10 alarms × 0.10 + 240 GB S3 audit × 0.025',f'20*{r["log_ingest_gb"]}+20*{r["log_storage_gb"]}+20*{r["metric"]}+10*{r["alarm"]}+240*{r["s3_gb"]}',('log_ingest_gb','log_storage_gb','metric','alarm','s3_gb'))
add('governance','DLP/guardrail và eval allowance','DLP and approvals nằm trong compute; 30 USD/month model eval allowance, not a separate managed Guardrails SKU','30')
add('network','Internet egress + regional WAF','300 GB × 0.12 + 5 ACL + 3 rules × 1 + 1M requests × 0.60/M; image transfer allowance 1 GB SG→Oregon × 0.09 + 5 GB return × 0.02; no NAT',f'300*{r["egress_gb"]}+{r["waf_acl"]}+3*{r["waf_rule"]}+1000000*{r["waf_request"]}+{r["sg_to_oregon_gb"]}+5*{r["oregon_to_sg_gb"]}',('egress_gb','waf_acl','waf_rule','waf_request','sg_to_oregon_gb','oregon_to_sg_gb'))
add('cicd','CodeBuild và staging','1000 Linux small build minutes × 0.005; artifacts nằm trong object_storage; 5% staging in compute/model rows',f'1000*{r["build_min"]}',('build_min',))
add('embedding','Titan Text Embeddings V2','120M ingestion+query tokens × 0.028 USD/M; first 500M index adds 14 USD one-time',f'120000000/1000*{r["embedding_in_1k"]}',('embedding_in_1k',))
add('ops_labor','Vận hành và trực giờ hành chính','0.10 FTE × 2000 USD/FTE-month; shared business-hours support; 16 h/month','200')
cloud=money(sum(row[3] for row in rows if row[0]!='ops_labor'))
add('contingency','Dự phòng biến động tải và đơn giá','10% of AWS recurring estimate; not a hard spending cap',f'{cloud}*.1')
total=money(sum(row[3] for row in rows))
summary=base['summary'].copy();summary.update(aws_recurring=cloud,contingency=rows[-1][3],total=total,per_dau=money(total/2000),all_reference_total=money(total+(all_sonnet-nova-sonnet)*f*1.1),sparse_workspace_total=money(total-18000*r['s3_gb']*1.1),double_dau_total=money(cloud*2*1.1+300),previous_us_east_1_total=base['summary']['total'],delta_vs_previous=money(total-base['summary']['total']),note='Public AWS Singapore SKU rates checked 2026-10-16; primary Singapore, Sonnet Global/APAC Nova and Oregon image exception. Quality, latency, residency and account access gates remain.')
model=dict(as_of='2026-10-16',region='ap-southeast-1',inputs=inp,tasks=tasks,rows=rows,summary=summary,sources=base['sources'],formulas=formulas,row_skus=row_evidence,inference_scope='Nova Lite APAC; Sonnet Global from Singapore; Stable Image Core us-west-2. Not Singapore-only data residency.')
(OUT/'cost-model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Báo giá Singapore — G03 Eviaura','',f'**{total:,.2f} USD/tháng**, chưa VAT. AWS {cloud:,.2f}, labor 200.00, dự phòng {rows[-1][3]:,.2f}. Cùng workload 2.000 DAU, 8 tác vụ/người/ngày, 22 ngày, full workspace quota và một staging.','', 'Primary region: **ap-southeast-1**. Nova Lite dùng APAC inference, Sonnet 4.5 dùng Global inference, ảnh dùng Stable Image Core tại us-west-2. Không khẳng định toàn bộ dữ liệu model lưu/xử lý tại Singapore. Nova Canvas đã được thay vì EOL.', '', '| Component | Hạng mục | USD/tháng |','|---|---|---:|']
md += [f'| {a} | {b} | {d:,.2f} |' for a,b,c,d,e in rows]
md += [f'| TOTAL | | **{total:,.2f}** |','',f'Bản cũ us-east-1: {base["summary"]["total"]:,.2f}. Chênh lệch {summary["delta_vs_previous"]:,.2f} USD. Đây không phải phép so sánh riêng region: Sonnet đổi US geo sang Global và model ảnh được thay do EOL.', '', 'Đơn giá billable có SKU, publication date và URL versioned AWS catalog trong `pricing-ap-southeast-1.json`. Không khấu trừ ưu đãi. Governance 30 USD là allowance, labor và contingency là giả định. Chưa đo H6/H8/DR hoặc xác minh quyền model trong account.']
(OUT/'BAOGIA.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
