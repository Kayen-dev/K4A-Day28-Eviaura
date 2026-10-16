"""Rebuild the AWS target infrastructure and transparent monthly estimate; no AWS calls."""
import json
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)
money = lambda n: float(Decimal(str(n)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
P = 'https://aws.amazon.com/'
sources = {
 'bedrock': P+'bedrock/pricing/', 'nova': P+'nova/pricing/',
 'lambda': P+'lambda/pricing/', 'api': P+'api-gateway/pricing/',
 's3': P+'s3/pricing/', 'ddb': P+'dynamodb/pricing/on-demand/',
 'cognito': P+'cognito/pricing/', 'agentcore': P+'bedrock/agentcore/pricing/',
 'sqs': P+'sqs/pricing/', 'kms': P+'kms/pricing/',
 'secrets': P+'secrets-manager/pricing/', 'cw': P+'cloudwatch/pricing/',
 'waf': P+'waf/pricing/', 'transfer': P+'ec2/pricing/on-demand/#Data_Transfer',
 'build': P+'codebuild/pricing/', 'budgets': P+'aws-cost-management/aws-budgets/pricing/',
 'sonnet': 'https://www-cdn.anthropic.com/files/4zrzovbb/website/3684c2faafb97418665782cea0001f439f74b1d2.pdf'
}
# Prices are planning inputs. Capture/SKU/account verification remains a release gate.
inputs = dict(dau=2000, requests_per_user_day=8, workdays=22, hours_month=730,
              business_hours=220, peak_factor=6, staging_ratio=.05,
              escalation_ratio=.10, workspace_gb_per_user=10,
              retry_ratio=.05, sonnet_input_million=3.30, sonnet_output_million=16.50,
              nova_input_million=.06, nova_output_million=.24)
tasks = [
 # tokens are cumulative per user task, including tool turns and retrieved context
 dict(level='L1', share=.60, input=2000, output=400, model='Nova Lite'),
 dict(level='L2', share=.20, input=4000, output=900, model='Nova Lite'),
 dict(level='L3', share=.10, input=6000, output=1500, model='Claude Sonnet 4.5'),
 dict(level='L4', share=.09, input=9000, output=1600, model='Claude Sonnet 4.5'),
 dict(level='L5', share=.01, input=2000, output=300, model='Nova Lite + Nova Canvas'),
]
N = inputs['dau']*inputs['requests_per_user_day']*inputs['workdays']
nova=sonnet=all_sonnet=total_in=total_out=0
for t in tasks:
    t['requests']=N*t['share']
    a=t['requests']*t['input']/1e6; b=t['requests']*t['output']/1e6
    total_in+=a; total_out+=b
    s=a*inputs['sonnet_input_million']+b*inputs['sonnet_output_million']
    all_sonnet+=s
    if t['model'].startswith('Nova'):
        # First cheap call still billed on escalations; no fictional cache savings.
        nova+=a*.06+b*.24
        sonnet+=s*inputs['escalation_ratio']
    else: sonnet+=s
factor=(1+inputs['retry_ratio'])*(1+inputs['staging_ratio'])
rows=[]
def add(c, name, note, value, source):
    rows.append([c,name,'us-east-1; '+note,money(value), sources.get(source,source)])
add('compute','Chat streaming Lambda ARM','512 MB × 20 s × 352000 × 1.05 staging × 0.0000133334 USD/GB-s + 0.20 USD/M invocation', .5*20*N*1.05*.0000133334+N*1.05/1e6*.2,'lambda')
add('compute','Background worker và chờ sandbox','19% tasks × 352000 × 120 s × 1 GB × 1.05 staging × 0.0000133334 USD/GB-s + invocation; separate trusted worker remains billable while waiting',N*.19*120*1.05*.0000133334+N*.19*1.05/1e6*.2,'lambda')
add('compute','Provisioned concurrency giờ hành chính','10 warm slots × 0.5 GB × 220 h × 3600 × 0.0000033334; execution conservatively billed at on-demand above',10*.5*220*3600*.0000033334,'lambda')
add('llm','Nova Lite: L1/L2/L5','Cumulative task tokens; 0.06 input / 0.24 output USD per M; 5% retries and 5% staging; no cache discount',nova*factor,'nova')
add('llm','Sonnet 4.5: L3/L4 và escalation','US geographic inference; 3.30 input / 16.50 output USD per M; 10% escalation of cheap tasks + 5% retry + 5% staging',sonnet*factor,'sonnet')
add('llm','Nova Canvas: ảnh 1024 standard','3520 images × 0.04 USD × 1.05 retries × 1.05 staging',3520*.04*factor,'nova')
add('gateway','API Gateway REST + router','1000000 API calls × 3.50 USD/M; regional multi-AZ; quota in DynamoDB included in database',3.5,'api')
add('load_balancer','Managed regional request distribution','Đã nằm trong API Gateway REST, TLS và multi-AZ routing; không thêm ALB',0,'api')
add('authn','Cognito enterprise federation','2000 prod + 100 staging federated MAU × 0.015 USD; MFA at corporate IdP; no allowance deducted',2100*.015,'cognito')
add('authz','RBAC/ABAC và ACL kiểm tra lại','Đã nằm trong compute/database: server derives tenant/user, per-document ACL, deny stale ACL',0,'ddb')
add('database','DynamoDB Standard on-demand','50 GB × 0.25 + 8M WRU × 0.625/M + 20M RRU × 0.125/M; includes transactional quota/approvals/token vault ciphertext and staging',50*.25+8*.625+20*.125,'ddb')
add('vector_db','S3 Vectors storage and ingestion','1000000 × (4096+1024+1024+128) bytes / GiB × 0.06 + 20% monthly PUT × 0.20/GB; prod+staging',1e6*6272/2**30*(.06+.2*.2)*1.05,'s3')
# Query scans 1M-vector index before ACL filtering. Do not assume filtering reduces charged scan.
q=300000; scan=100000*5248/2**40*.004+900000*5248/2**40*.002
add('vector_db','S3 Vectors queries','300000 queries × (2.50 USD/M + scan 1M vectors, 5248 bytes/vector, tiers 0.004/0.002 USD/TiB); top20 IDs below included return threshold',q/1e6*2.5+q*scan,'s3')
add('object_storage','Workspace quota đầy đủ + KB + staging','2000 × 10 GB + 200 GB KB + 100 GB staging = 20300 GB × 0.023 USD/GB-month',20300*.023,'s3')
add('object_storage','S3 object requests','2000000 PUT/LIST × 0.005/1000 + 10000000 GET × 0.0004/1000',2e6*.005/1000+10e6*.0004/1000,'s3')
add('cache_queue','SQS + TTL cache','3000000 queue API units × 0.40/M; cache in DynamoDB already in database; encrypted queues + DLQ',3*.4,'sqs')
add('sandbox','AgentCore Code Interpreter VPC','35200 sessions × 120 s × (1 active vCPU × 0.0895/h + 4 GB × 0.00945/h); no assumed idle CPU discount; 5% staging',35200*120/3600*(.0895+4*.00945)*1.05,'agentcore')
add('connectors','Delegated OAuth Lambda workers','1000000 calls × 1 GB × 2 s × 0.0000133334 + 0.20/M; connector overhead separately budgeted beyond worker job duration; no full-tenant service account',1e6*2*.0000133334+.2,'lambda')
add('secrets_kms','KMS và OAuth app secrets','2 customer keys × 1 USD + 1M requests × 0.03/10000 + 10 app secrets × 0.40 + 100000 API × 0.05/10000; user refresh tokens envelope-encrypted in DynamoDB',2+3+4+.5,'kms')
add('backup_dr','PITR + object versions + restore drill','50 GB DynamoDB PITR × 0.20 + 4000 GB previous S3 versions × 0.023 + 50 GB monthly backup × 0.10 + 10 GB restore × 0.15; same-region recovery',50*.2+4000*.023+50*.1+10*.15,'ddb')
add('monitoring','CloudWatch + S3 audit 12 tháng','20 GB ingest × 0.50 + 20 GB logs × 0.03 + 20 metrics × 0.30 + 10 alarms × 0.10 + 240 GB audit S3 × 0.023; audit writes included object requests',20*.5+20*.03+20*.3+10*.1+240*.023,'cw')
add('governance','DLP/guardrail và eval allowance','DLP, injection rules and approvals nằm trong compute; 30 USD monthly reference-model eval/review allowance; fail-closed quality gate; not measured quality evidence',30,'bedrock')
add('network','Internet egress + regional WAF','300 GB internet egress × 0.09 + 5 USD web ACL + 3 rules × 1 + 1M requests × 0.60; isolated sandbox VPC; no NAT or paid interface endpoints',300*.09+5+3+.6,'waf')
add('cicd','CodeBuild và staging','1000 Linux small build minutes × 0.005; IaC/S3 artifacts included object_storage; staging compute/model/db explicitly in respective lines',1000*.005,'build')
add('embedding','Titan Text Embeddings V2','100M monthly ingestion tokens + 20M query tokens × 0.02 USD/M; first index 500M tokens extra 10 USD one-time',120*.02,'bedrock')
add('ops_labor','Vận hành và trực giờ hành chính','0.10 FTE × 2000 USD/FTE-month; 16 h/month; shared business-hours on-call, not dedicated 24/7',.1*2000,'NA')
cloud=money(sum(r[3] for r in rows if r[0]!='ops_labor'))
base=money(sum(r[3] for r in rows))
add('contingency','Dự phòng biến động tải và đơn giá','10% of AWS recurring estimate; not a spending cap; exact SKU evidence still needs capture',cloud*.10,'NA')
total=money(sum(r[3] for r in rows))
summary=dict(monthly_requests=N, input_tokens_million=total_in, output_tokens_million=total_out,
 peak_rps=N/(220*3600)*6, peak_concurrency=N/(220*3600)*6*20,
 peak_input_tpm=total_in*1e6/(220*3600)*6*60,
 peak_output_tpm=total_out*1e6/(220*3600)*6*60,
 aws_recurring=cloud, labor=200, contingency=rows[-1][3], total=total, per_dau=money(total/2000),
 all_reference_total=money(total+(all_sonnet-nova-sonnet)*factor*1.1),
 sparse_workspace_total=money(total-18000*.023*1.1),
 double_dau_total=money((cloud*2)*1.1+300),
 note='Planning estimate; no AWS resources created, no production quality or latency result. Rate inputs need SKU snapshots before submission.')
(OUT/'cost-model.json').write_text(json.dumps(dict(as_of='2026-10-16',region='us-east-1',inputs=inputs,tasks=tasks,rows=rows,summary=summary,sources=sources),ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Báo giá AWS dự kiến — VBot Eviaura','', 'USD/tháng, chưa VAT; 2.000 DAU; production + staging. Không khấu trừ ưu đãi. Đơn giá là đầu vào lập kế hoạch, cần chốt SKU và ảnh bảng giá trước khi nộp.', '', '| Component | Hạng mục | USD/tháng |','|---|---|---:|']
md += [f'| {r[0]} | {r[1]} | {r[3]:,.2f} |' for r in rows]
md += [f'| TOTAL | Có công vận hành và dự phòng | **{total:,.2f}** |','',f'AWS định kỳ: **{cloud:,.2f}**; công vận hành: **200.00**; dự phòng: **{rows[-1][3]:,.2f}**; tổng/DAU: **{total/2000:.2f}**.', '',f'Tất cả text request dùng Sonnet tham chiếu: **{summary["all_reference_total"]:,.2f}**. Workspace chỉ dùng 1 GB/người: **{summary["sparse_workspace_total"]:,.2f}**. 4.000 DAU: envelope tuyến tính **{summary["double_dau_total"]:,.2f}**, cần sizing và quota lại.', '', 'Chi tiết công thức và nguồn: `Eviaura_baogia.xlsx` và `cost-model.json`. Giá rẻ của model chỉ áp dụng sau eval đạt H8; hiện chưa có dữ liệu chứng minh.']
(OUT/'BAOGIA.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
