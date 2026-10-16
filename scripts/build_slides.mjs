import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation, PresentationFile, FileBlob} from '../.tools/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';

const root=path.resolve('.');
const skill='C:/Users/ASUS/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
const runtime='C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const build=path.join(root,'.tools/slides');
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.join(root,'deliverables'),{recursive:true});
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const m=JSON.parse(await fs.readFile('deliverables/cost-model.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#103548',ink:'#17364A',teal:'#087F83',light:'#F4F8FA',muted:'#587080',line:'#D1DEE5',amber:'#A76014',pale:'#E8F4F3',white:'#FFFFFF'};
const fmt=(n)=>n.toLocaleString('vi-VN',{minimumFractionDigits:2,maximumFractionDigits:2});
const byComp=(c)=>m.rows.filter(r=>r[0]===c).reduce((a,r)=>a+r[3],0);
const saving=(100*(1-m.summary.total/m.summary.all_reference_total)).toLocaleString('vi-VN',{minimumFractionDigits:2,maximumFractionDigits:2});
let serial=0;
const durations=[15,30,25,40,35,35,30,30,25,30,25,30,25,25,20];
const sourceNotes='Nguồn nội bộ: docs/ARCHITECTURE.md, docs/DEPLOYMENT.md, deliverables/cost-model.json, deliverables/VALIDATION.md. Ngày thiết kế 16/10/2026. Số liệu là dự toán, không phải hóa đơn hoặc benchmark production.';
function rect(s,x,y,w,h,fill=C.white,stroke='none',name='shape'){
 return s.shapes.add({name:`${name}-${++serial}`,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1,style:'solid'}});
}
function text(s,content,x,y,w,h,size=24,color=C.ink,bold=false,align='left'){
 const q=rect(s,x,y,w,h,'none','none','text');q.text=content;
 q.text.style={typeface:'Arial',fontSize:size,bold,color,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0};
 return q;
}
function line(s,x,y,w,h=2,color=C.line){return rect(s,x,y,w,h,color);}
function arrow(s,a,b,from='right',to='left',color=C.teal){
 return s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:color,width:2,style:'solid'},head:{type:'triangle',width:'sm',length:'sm'}});
}
function slide(title,notes,sources=[],dark=false){
 const s=p.slides.add();s.background.fill=dark?C.navy:C.white;
 const n=p.slides.items.length;
 if(!dark){line(s,56,45,44,5,C.teal);text(s,title,56,69,1168,74,36,C.ink,true);}
 line(s,56,670,1168,1,dark?'#365565':C.line);
 text(s,'G03  /  Eviaura',56,684,500,20,13,dark?'#BED5DF':C.muted);
 text(s,String(n).padStart(2,'0'),1160,682,64,22,14,dark?'#BED5DF':C.muted,false,'right');
 s.speakerNotes.text=`Thời lượng gợi ý: ${durations[n-1]} giây.\n\n${notes}\n\n${sourceNotes}\n${sources.map(x=>'Nguồn: '+x).join('\n')}`;
 return s;
}
function block(s,label,body,x,y,w,h=125){
 line(s,x,y,4,h,C.teal);text(s,label,x+20,y,w-20,34,24,C.ink,true);text(s,body,x+20,y+45,w-24,h-40,22,C.muted);
}
function band(s,body,y=610,color=C.pale){rect(s,56,y,1168,42,color);text(s,body,70,y+10,1140,27,18,C.ink);}
function table(s,values,x,y,w,h,widths,size=21){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.styleOptions={headerRow:false,bandedRows:false};
 t.borders.assign({fill:C.line,width:.6,style:'solid'});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
  const cell=t.getCell(r,c);cell.fill=r===0?C.navy:(r%2?C.light:C.white);
  cell.text.style={typeface:'Arial',fontSize:size,bold:r===0,color:r===0?C.white:C.ink,verticalAlignment:'middle',insets:9};
 }
 return t;
}
function node(s,code,label,x,y,w=220,h=78){
 const q=rect(s,x,y,w,h,C.light,C.line,'component-'+code);
 text(s,code,x+12,y+10,w-24,24,17,C.teal,true);
 text(s,label,x+12,y+36,w-24,h-38,19,C.ink);
 return q;
}

// 01
{
 const s=slide('VBot Workplace','Giới thiệu phương án AWS cho 2.000 DAU. Mục tiêu là giảm tổng chi phí trong khi vẫn giữ các điều kiện H1 đến H8. Đây là gói thiết kế trước triển khai, chưa có kết quả production.',[],true);
 text(s,'VBOT WORKPLACE',56,64,1040,42,24,'#B8DBE4',true);
 text(s,'Kiến trúc AWS\ncho 2.000 DAU',56,157,1100,170,62,C.white,true);
 line(s,56,369,125,6,'#24B5AC');
 text(s,'Serverless và model trả theo sử dụng',56,411,1100,55,32,C.white);
 text(s,fmt(m.summary.total)+' USD/tháng',56,500,1100,66,48,'#70D7CD',true);
 text(s,'Production + staging + vận hành + dự phòng, chưa VAT',56,584,1120,35,22,'#C5DBE3');
}
// 02
{
 const s=slide('352.000 tác vụ mỗi tháng là cơ sở sizing','Chốt giả định 8 tác vụ mỗi nhân viên mỗi ngày và 22 ngày làm việc. Với 220 giờ hành chính, tải bình quân khoảng 0,44 tác vụ trên giây. Hệ số đỉnh 6 tạo mức 2,67 RPS. Tính theo thời gian request trung bình 20 giây, khoảng 54 phiên đồng thời ở đỉnh. Đây là giả định cần đo, không phải load test.');
 text(s,'2.000 × 8 × 22 = 352.000',56,168,1168,72,49,C.teal,true);
 text(s,'DAU × tác vụ/người/ngày × ngày làm việc',58,249,1160,38,25,C.muted);
 table(s,[['Chỉ số','Công thức','Kết quả'],['RPS trung bình','352.000 / (220 × 3.600)','0,44 RPS'],['RPS đỉnh','RPS trung bình × 6','2,67 RPS'],['Phiên đồng thời đỉnh','2,67 × 20 giây','≈ 54 phiên'],['Tokens/tháng','Tổng qua các lượt model và tool','1.207,36M in / 252,384M out']],56,316,1168,245,[290,500,378],22);
 band(s,'Production chạy 24/7 (730 giờ). Warm capacity theo giờ hành chính (220 giờ), GMT+7.');
}
// 03
{
 const s=slide('Dung lượng và tác vụ nặng được tính riêng','Giá chính tính đủ quota 10 GB cho 2.000 nhân viên, không giả định mỗi người mới dùng vài MB. Chỉ một phần tài liệu được index theo nhu cầu và quyền nguồn. Sandbox và ảnh cũng có volume riêng. Staging dùng khoảng 5% lượt model và compute, có dữ liệu riêng.',[m.sources.s3,m.sources.agentcore]);
 table(s,[['Hạng mục','Giả định tháng'],['Workspace và KB','20.000 GB quota + 200 GB KB + 100 GB staging'],['Vector và embedding','1 triệu chunk, 1.024 chiều, 120M token embedding'],['Sandbox','35.200 session × 120 giây, 1 active vCPU + 4 GB'],['Sinh ảnh','3.520 ảnh, 1.024 × 1.024 standard'],['Connector và egress','1 triệu call, 300 GB internet outbound'],['Dữ liệu và audit','50 GB state, 20 GB audit mới/tháng, giữ 12 tháng']],56,163,1168,379,[340,828],23);
 text(s,'Staging riêng',56,574,300,36,26,C.teal,true);
 text(s,'5% model/compute, 100 MAU, không warm capacity',365,574,850,58,25,C.muted);
}
// 04
{
 const s=slide('Kiến trúc bao phủ đủ 19 component','Đi theo đường xử lý trên cùng: SSO, managed load distribution, gateway, compute và model. Compute truy cập các thành phần dữ liệu theo quyền người dùng. Connector và sandbox được tách khỏi luồng chat. Hàng dưới là các năng lực vận hành xuyên suốt. Chọn us-east-1 và US inference boundary, cần duyệt residency và đo độ trễ từ Việt Nam trước release.',[
 'https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html',
 'https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html']);
 const xs=[56,292,528,764,1000];
 const a=[['authn','SSO + Cognito'],['load_balancer','REST regional TLS'],['gateway','Auth, quota, router'],['compute','Lambda ARM'],['llm','Bedrock APIs']].map(([c,l],i)=>node(s,c,l,xs[i],166));
 for(let i=0;i<4;i++)arrow(s,a[i],a[i+1]);
 const b=[['authz','RBAC / ABAC + ACL'],['database','DynamoDB + PITR'],['vector_db','S3 Vectors'],['object_storage','Private user files'],['cache_queue','SQS / TTL cache']].map(([c,l],i)=>node(s,c,l,xs[i],292));
 line(s,166,268,944,2,C.teal);line(s,874,244,2,24,C.teal);
 for(let i=0;i<5;i++)line(s,xs[i]+109,268,2,24,C.teal);
 [['connectors','OAuth delegated'],['secrets_kms','Token vault + KMS'],['sandbox','Code Interpreter'],['network','VPC isolated / 2 AZ']].forEach(([c,l],i)=>node(s,c,l,56+i*296,418,280));
 [['backup_dr','PITR / versions'],['monitoring','Metrics / audit'],['governance','DLP / approvals'],['cicd','IaC / staging'],['ops_labor','Shared operations']].forEach(([c,l],i)=>node(s,c,l,xs[i],544));
 text(s,'Primary Singapore. Nova: APAC, Sonnet: Global, ảnh: Oregon. LB nằm trong API Gateway.',56,638,1168,26,16,C.muted);
}
// 05
{
 const s=slide('Một request đi qua kiểm tra quyền và ngân sách','Người dùng đăng nhập SSO. Backend lấy tenant và user từ danh tính đã xác thực, không lấy từ body. Trước mỗi call, hệ thống giữ chỗ ngân sách tối đa. Retrieval kiểm tra ACL trước khi đưa text vào prompt. Kết quả đi qua kiểm tra output rồi mới stream về. Với tác vụ nền, trả job ID và thông báo khi hoàn thành. Hành động ghi luôn chờ xác nhận payload.',[
 'https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html']);
 const labels=[['1. SSO + MFA','Access token, scope'],['2. LB / gateway','Xác thực và throttle'],['3. Admission','Quyền và cost reserve'],['4. Retrieval','ACL tại nguồn'],['5. Model / tools','Route hoặc background'],['6. Output check','DLP trước phát chunk'],['7. Phản hồi','SSE hoặc trạng thái job']];
 const nodes=[];
 labels.forEach(([h,b],i)=>{
  const x=i<4?56+i*296:56+(i-4)*396; const y=i<4?190:390; const w=i<4?280:376;
  const q=rect(s,x,y,w,118,C.light,C.line);text(s,h,x+16,y+15,w-32,36,25,C.teal,true);text(s,b,x+16,y+62,w-32,45,22,C.ink);nodes.push(q);
 });
 for(let i=0;i<3;i++)arrow(s,nodes[i],nodes[i+1]);
 for(let i=4;i<6;i++)arrow(s,nodes[i],nodes[i+1]);
 text(s,'Kết quả retrieval đã kiểm quyền trở thành context cho bước 5',56,332,1168,32,23,C.muted);
 band(s,'Gửi mail, sửa ticket/page hoặc xóa file: proposal có digest, user xác nhận, worker kiểm tra lại.');
}
// 06
{
 const s=slide('Model nhỏ chỉ thay baseline sau khi đạt chất lượng','Dùng Nova Lite cho email, tài liệu thông thường và prompt hỗ trợ thiết kế. Code và agent phức tạp dùng Sonnet 4.5. Tỷ lệ chuyển từ Lite lên Sonnet 10% là giả định trong cost model, cả hai lượt đều tính phí. Baseline text là Sonnet 4.5, baseline ảnh là Stable Image Core cùng cấu hình. Canvas được thay do EOL. Nova Lite gọi APAC, Sonnet gọi Global, ảnh gọi us-west-2. Cần từng cấp đạt 95% baseline.',[m.sources.nova,m.sources.sonnet,'https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-stability-ai-stable-image-core-1-0.html']);
 table(s,[['Cấp tác vụ','Tỷ lệ','Input / output','Model dự kiến'],['L1  Email / hỏi đáp','60%','2.000 / 400','Nova Lite'],['L2  Tài liệu / slide','20%','4.000 / 900','Nova Lite'],['L3  Dữ liệu / code','10%','6.000 / 1.500','Sonnet 4.5'],['L4  Agent dự án','9%','9.000 / 1.600','Sonnet 4.5'],['L5  Thiết kế / ảnh','1%','2.000 / 300','Lite + Image Core']],56,164,1168,330,[360,120,270,418],22);
 text(s,'API thay vì tự host GPU',56,532,550,34,27,C.teal,true);
 text(s,'Giảm chi phí nhàn rỗi và công vận hành ở tải này',56,577,590,64,23,C.muted);
 text(s,'Escalation 10% + retry 5%',690,532,534,34,26,C.teal,true);
 text(s,'Đã tính phí cả call rẻ trước khi fallback',690,577,534,64,23,C.muted);
}
// 07
{
 const s=slide('Connector hành động bằng quyền của người dùng','Tích hợp đủ Google Workspace, M365, Notion, Jira và Confluence. Quyền delegated và scope theo chức năng, tách đọc với ghi. Refresh token lưu ciphertext trong DynamoDB vault với KMS, client secrets ở Secrets Manager. ACL stale, quyền bị thu hồi hay nguồn không xác minh được đều fail closed. Không có tài khoản đọc toàn doanh nghiệp.');
 table(s,[['Nguồn','Phạm vi tích hợp'],['Google Workspace','Mail, tài liệu và lịch theo OAuth user'],['Microsoft 365 / Outlook','Mail, lịch và file theo delegated token'],['Notion','Đọc và cập nhật page đã được user cấp quyền'],['Jira / Confluence','Issue, project và page trong quyền người dùng']],56,171,710,315,[300,410],23);
 text(s,'Cùng một nguyên tắc',810,177,414,45,27,C.teal,true);
 text(s,'Scope thấp nhất\n\nACL gốc được kiểm tra lại\n\nGhi ra ngoài cần xác nhận',810,239,414,250,24,C.ink);
 band(s,'Refresh token: KMS envelope encryption. Client secret: Secrets Manager. Retry 429 hữu hạn.');
}
// 08
{
 const s=slide('Workspace riêng và sandbox không có đường ra ngoài','Tách dữ liệu theo tenant/user trong trusted controller. S3 prefix chỉ là namespace, không tự tạo isolation. Sandbox là session mới mỗi job, VPC mode với subnet không có IGW, NAT, endpoints hay DNS, không đưa credential vào môi trường thực thi. Controller chỉ trao file đã kiểm quyền. Dừng session trong finally và watchdog xử lý session mồ côi.',[
 'https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html']);
 rect(s,56,170,552,368,C.light,C.line);rect(s,656,170,568,368,C.pale,C.line);
 text(s,'Trusted controller',76,191,510,40,28,C.teal,true);
 text(s,'Identity từ token đã xác thực\n\nS3 workspace tối đa 10 GB/user\n\nMemory và search lọc theo quyền\n\nURL ký ngắn hạn, quota byte atomic',76,255,510,260,23,C.ink);
 text(s,'Untrusted code session',678,191,520,40,28,C.teal,true);
 text(s,'AgentCore Code Interpreter VPC\n\nSubnet cô lập, DNS disabled\n\nKhông OAuth token hoặc data role\n\nDeadline ≤ 600 giây, hủy sau job',678,255,520,260,23,C.ink);
 text(s,'Controller trao file qua tool API sau kiểm tra owner',56,565,1168,35,25,C.ink,true);
 text(s,'Chế độ SANDBOX vẫn có thể truy cập S3. Thiết kế chọn VPC và phải test cả DNS/IPv6/HTTP.',56,617,1168,40,20,C.amber);
}
// 09
{
 const s=slide('Governance chặn dữ liệu và hành động vượt quyền','Áp dụng governance ở input, output và tool calls. Email và tài liệu là nguồn không tin cậy, không có quyền ra lệnh. Proposal ghi có target, payload digest, nonce và expiry. Audit chỉ chứa metadata đã che thông tin, có Object Lock ít nhất 12 tháng. Model và prompt mới phải qua eval trước khi phát hành.',[
 'https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html']);
 block(s,'Input và retrieval','Phân loại dữ liệu, che PII/secrets.\nEmail và tài liệu không trở thành chỉ thị hệ thống.',56,177,554,158);
 block(s,'Output và tool calls','Kiểm tra chunk trước stream.\nApproval ràng buộc target, payload digest và expiry.',670,177,554,158);
 block(s,'Data retention','TLS/SSE, vault dùng KMS.\nHot logs 30 ngày, audit immutable ≥ 12 tháng.',56,393,554,158);
 block(s,'Model và prompt change','Eval theo từng cấp, tối thiểu 50 ca/cấp.\nDeny release nếu thiếu dữ liệu hoặc <95% baseline.',670,393,554,158);
 band(s,'Không log raw prompt, nội dung tài liệu hoặc OAuth token. Chính sách model phải được duyệt trước release.');
}
// 10
{
 const s=slide('HA đa AZ, DR cùng region cần diễn tập khôi phục','Đường đồng bộ dùng API Gateway, Lambda và DynamoDB managed multi-AZ, tránh một máy gateway hay database đơn lẻ. PITR và S3 versioning phục vụ khôi phục mất dữ liệu logic trong region. RTO 4 giờ và RPO 1 giờ là mục tiêu cần diễn tập. Phương án giá chính chưa có failover cả region. Nếu H7 yêu cầu regional disaster, phải thêm replication và báo giá lại.');
 table(s,[['Chỉ tiêu','Mục tiêu thiết kế','Cơ chế'],['Availability','99,5% giờ hành chính','Managed multi-AZ API / compute / state'],['RTO','≤ 4 giờ','Restore table/bucket mới, kiểm tra ACL'],['RPO','≤ 1 giờ','DynamoDB PITR, S3 versions'],['Backup test','Diễn tập mỗi tháng','Checksum, dữ liệu cuối, thời gian restore']],56,171,1168,300,[270,300,598],22);
 text(s,'Phạm vi DR hiện tại',56,514,1168,38,28,C.teal,true);
 text(s,'Khôi phục trong cùng region. Chưa có bằng chứng đạt RTO/RPO và chưa có regional failover.',56,564,1168,66,26,C.amber);
}
// 11
{
 const s=slide('Độ trễ và cost được đo trên cùng một request','Mục tiêu TTFT p95 là token model đầu tiên, không tính heartbeat hoặc thông báo đang xử lý. Warm 10 slots giờ hành chính chỉ giảm cold start cho một phần tải, peak 54 phiên vẫn có overflow. Quota model và TPM phải tính retry, escalation và headroom. Monitoring tách các giai đoạn để biết lỗi do retrieval, model hay connector.');
 text(s,'≤ 3 giây',56,175,490,80,60,C.teal,true);
 text(s,'p95 time-to-first-model-token',56,266,530,40,27,C.ink,true);
 text(s,'Mục tiêu giờ cao điểm, đo từ Việt Nam.\nChưa có benchmark xác nhận.',56,330,535,97,25,C.muted);
 text(s,'Các tín hiệu cần theo dõi',690,177,534,45,28,C.teal,true);
 text(s,'SSO, retrieval, model TTFT, end-to-end\n\nTokens và USD theo user / đơn vị\n\n429, lỗi tool, queue age, DLQ\n\nSession sandbox mồ côi, ACL deny',690,245,534,275,24,C.ink);
 band(s,'Nền ≤ 10 phút, trả job ID và trạng thái. Bedrock quota phải có headroom trước mở production.');
}
// 12
{
 const s=slide('Tổng dự toán là '+fmt(m.summary.total)+' USD mỗi tháng','Con số trên slide khớp TOTAL trong báo giá XLSX Singapore. AWS định kỳ '+fmt(m.summary.aws_recurring)+' USD, cộng 200 USD vận hành và 10% dự phòng. Model là phần lớn nhất. Các billable rate đã đối chiếu SKU công khai AWS ngày 16/10/2026. Giá chưa VAT. Workload, labor và eval allowance vẫn là giả định. Dự toán không khấu trừ ưu đãi.',[m.sources.bedrock,m.sources.lambda,m.sources.s3]);
 text(s,fmt(m.summary.total)+' USD',56,165,1168,78,60,C.teal,true);
 text(s,fmt(m.summary.per_dau)+' USD/DAU/tháng',58,253,1166,39,28,C.muted);
 const t=table(s,[['Khoản','USD/tháng'],['AWS định kỳ',fmt(m.summary.aws_recurring)],['Nhân sự vận hành',fmt(m.summary.labor)],['Dự phòng',fmt(m.summary.contingency)],['TOTAL',fmt(m.summary.total)]],56,320,540,285,[350,190],24);
 text(s,'Các khoản lớn nhất',680,326,540,40,28,C.ink,true);
 text(s,fmt(byComp('llm'))+'    LLM\n\n'+fmt(byComp('object_storage'))+'       Object storage\n\n'+fmt(byComp('compute'))+'       Compute\n\n'+fmt(byComp('sandbox'))+'       Sandbox',680,384,544,230,25,C.muted);
 text(s,'USD, chưa VAT. Có staging và full workspace quota. Không khấu trừ ưu đãi.',56,633,1168,25,18,C.muted);
}
// 13
{
 const s=slide('Routing là đòn bẩy tiết kiệm lớn nhất','So sánh cùng workload cho thấy routing có thể giảm khoảng 44,84% so với toàn bộ text dùng Sonnet. Đây là chênh lệch dự toán, không phải savings đo được. Sử dụng thấp hơn của workspace chỉ là sensitivity, báo giá chính vẫn tính đủ 20 TB. Khi 4.000 DAU, envelope khoảng 12.563 USD nhưng phải resize quota và đo lại độ trễ.');
 table(s,[['Kịch bản','USD/tháng','Điều kiện'],['Toàn bộ text dùng Sonnet',fmt(m.summary.all_reference_total),'Cùng workload và baseline'],['Routing Lite / Sonnet',fmt(m.summary.total),'Mỗi cấp đạt ≥95% baseline'],['Workspace 1 GB/người',fmt(m.summary.sparse_workspace_total),'Sensitivity, backup allowance giữ nguyên'],['4.000 DAU',fmt(m.summary.double_dau_total),'Envelope tuyến tính, sizing lại']],56,168,1168,300,[440,220,508],22);
 text(s,saving+'%',56,516,280,75,54,C.teal,true);
 text(s,'Chênh lệch dự toán routing so với toàn Sonnet',350,525,860,73,29,C.ink,true);
 text(s,'Ưu tiên giảm context, eval model nhỏ, index theo nhu cầu. Chưa tính tiết kiệm cache khi chưa đo hit rate.',56,620,1168,35,20,C.muted);
}
// 14
{
 const s=slide('Quota cắt ở admission, release qua staging và eval','Budgets có độ trễ nên không phải hard cap. Hard cap được thực thi bằng transaction reserve trước từng model hoặc tool call, sau đó reconcile chi phí thật và xử lý idempotency. CI xây artifact, kiểm tra hạ tầng và chạy eval. Staging data riêng, không warm. Hiện 42 resource schema đã pass và 6 rule bảo mật pass, nhưng runtime app và kiểm thử live còn thiếu.');
 block(s,'FinOps theo từng call','Atomic reserve theo user, đơn vị và tổng.\nKhông đủ budget thì deny trước model/tool call.\nRetry giữ idempotency, reconcile usage thực.',56,180,554,190);
 block(s,'CI/CD và staging','Build artifact có digest, version và rollback.\nIaC check, security check, per-level eval gate.\nStack staging và data tách riêng.',670,180,554,190);
 text(s,'Đã kiểm tra cục bộ',56,430,1168,40,29,C.teal,true);
 text(s,'IaC tham chiếu US: 42 resources, 0 findings\n6/6 security rules, 5 tests gate. Chưa validate deploy Singapore.',56,490,1168,91,27,C.ink);
 band(s,'Budget cảnh báo ở 80% và 100%. Chưa có application ZIP hoặc deployment AWS thực tế.');
}
// 15
{
 const s=slide('H1–H8 là điều kiện nghiệm thu trước production','Chốt lại kiến trúc có đủ thành phần và báo giá, nhưng chưa được tuyên bố đạt production. Phải có bằng chứng residency và model terms, SSO/OAuth/ACL, sandbox isolation, governance, latency, restore và chất lượng từng cấp. Mục tiêu là giá thấp nhất trong các phương án đã vượt các cổng, không dùng kết quả validator định dạng để thay cho các cổng này.');
 const left=[['H1  Cloud','Duyệt inference APAC / Global / Oregon'],['H2  Identity / ACL','Test MFA, revoked ACL và OAuth scope'],['H3  Isolation','Test cross-user, DNS/egress và cleanup'],['H4  AI governance','Test injection và xác nhận trước ghi']];
 const right=[['H5  Data governance','Kiểm tra DLP, retention và audit'],['H6  Latency','Đo p95 ≤3 giây ở peak từ Việt Nam'],['H7  HA / DR','Diễn tập RTO/RPO, chốt regional DR'],['H8  Quality / cost','≥95% baseline mỗi cấp, quota race test']];
 for(const [col,items] of [[56,left],[670,right]])items.forEach(([h,b],i)=>{text(s,h,col,172+i*100,554,32,24,C.teal,true);text(s,b,col,213+i*100,554,52,22,C.ink);});
 band(s,'Thiết kế và dự toán đã có. SKU, ứng dụng và các bằng chứng live cần hoàn thiện trước triển khai.');
}

if(p.slides.items.length!==15)throw Error('Expected exactly 15 total slides');
const sum=durations.reduce((a,b)=>a+b,0);
await fs.writeFile(path.join(build,'timing.json'),JSON.stringify({seconds:sum,slides:durations},null,2));
// All tables and architecture components remain editable in the PowerPoint file.
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
const finalPath=path.join(root,'deliverables/G03_slide.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,3,6,7,10,12,13].flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:15,requiredNativeTableOwnerSlides:[2,3,6,7,10,12,13],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({slides:15,seconds:sum,finalPath,result}));
// Render final package, not just the in-memory authoring model.
const finalDeck=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(let i=0;i<finalDeck.slides.items.length;i++){
 const image=await finalDeck.export({slide:finalDeck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await image.arrayBuffer()));
}
console.log('Rendered all final slides.');
