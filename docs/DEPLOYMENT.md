# Mã hạ tầng và trình tự triển khai

> Báo giá mới dùng Singapore. Template và các lệnh US dưới đây là reference ban đầu, cần sửa model profile/destination IAM và validate lại trước deploy. Xem [phạm vi Singapore](REGION_SINGAPORE.md). Không chỉ thay `--region`.

**Chưa deploy AWS.** `infra/vbot.template.json` là target infrastructure; ứng dụng, dữ liệu và identity integrations chưa được xây dựng trong repo đề bài. Không chạy deploy ngay với ZIP giả hoặc handler trả thành công tĩnh.

## Có gì trong template

Managed REST API streaming với Cognito authorizer, SAML federation/PKCE client, WAF rate limit; Lambda chat và worker với IAM riêng, alias/version, warm schedule chỉ cho prod; DynamoDB on-demand với PITR; S3 private/versioning và immutable audit; S3 Vectors; SQS/DLQ; KMS vault; AgentCore Code Interpreter VPC cô lập hai AZ; budget email cảnh báo.

Các service production dùng managed multi-AZ, không cần tạo 2 bản API hoặc table tính tiền trùng. Staging là lần triển khai **stack khác**, bộ dữ liệu/IdP client/vault khác; chỉ prod có warm schedule. Tài nguyên dữ liệu `Retain` và deletion protection làm chúng còn tồn tại/tính phí sau khi xóa stack. Audit Object Lock `COMPLIANCE` khóa ít nhất 366 ngày, không dùng bucket này cho dữ liệu nhạy cảm thô. Chưa có quyền xóa hoặc deploy trong giai đoạn hiện tại.

Những phần cần hoàn thiện tại bước xây dựng ứng dụng:

- Hai artifact Node.js 22 ARM: chat handler `index.handler` dùng `awslambda.streamifyResponse`; worker xử lý SQS và partial batch failures. Dependencies được pin và bundle. Không gửi code/model token hay provider secrets vào environment plaintext.
- Business controls theo `ARCHITECTURE.md`: source ACL, DLP input/output, budget reservation transactions, external write approvals, 10 GB quota, per-job interpreter sessions, durable job state/retry/deadline và thông báo qua job status của client. `RELEASE_ENABLED=false` phải được ứng dụng thực thi như fail-closed.
- OAuth app registration/consent cho từng SaaS; secret ARNs đưa vào `ConnectorSecretArns`. Backend không được chấp nhận ARN/URL/tenant/user tùy ý từ model. Token vault lưu ciphertext, data key encrypted và KMS context gồm tenant/user/provider.
- Backup automation, restore drills, logging metrics/custom dashboards và cảnh báo vận hành. Template đã bật PITR/versioning; **chưa có AWS Backup plan, log archive delivery pipeline hoặc custom metric publisher**. Giá có khoản dự trù cho các thành phần đó; không tuyên bố chúng đang hoạt động.
- CI/CD pipeline, artifact bucket và frontend/client hosting được dùng từ môi trường triển khai; template chưa tạo CodeBuild project, source connection hay web UI. Báo giá đã dành build minutes và artifact storage. Client có thể tích hợp vào portal hiện có; cần thêm hosting nếu chưa có.

Template chưa thay thế toàn bộ một ứng dụng production. Các phần trên được ghi rõ để bước deploy không biến thành ứng dụng “demo” thiếu H2–H8.

## Tái tạo và kiểm tra cục bộ

Python 3.11+ và Node.js có sẵn. Bộ cài kiểm tra nằm trong `.tools/`, không sửa package global. Phiên đã dùng `cfn-lint==1.57.2` và `guardpycfn==0.1.0`; `guardpycfn` cài `--no-deps` riêng để tránh pin cfn-lint cũ. Builder XLSX dùng artifact-tool của runtime đã có sẵn qua junction `.tools/node_modules`.

```powershell
python scripts/build_design.py
python scripts/build_infra.py
node scripts/build_quote.mjs
python scripts/check_design.py
$env:PYTHONPATH = '.tools/lint'
python -c "from cfnlint.runner import main; main()" -t infra/vbot.template.json -r us-east-1 --format json
git diff --check
```

`check_design.py` mở XLSX thật, lấy giá cached của các công thức, chạy đúng JavaScript validator lấy từ `vbot-capstone.html`, rồi dùng CloudFormation Guard với 6 project rules trong `infra/security.guard`. Các quy tắc này kiểm tra một tập cấu hình bắt buộc, không phải toàn bộ AWS compliance/security registry. Nếu XLSX không còn cache số, phải mở/tính lại/export trước khi nộp. `Sizing` là snapshot từ script; sửa đầu vào trong `scripts/build_design.py` rồi rebuild, không giả định sửa Sizing sẽ tự tính lại model.

## Gate trước bất kỳ thao tác AWS nào

1. Chọn account, profile và region được phép; xác thực bằng phiên ngắn hạn. Kiểm tra caller identity, CloudTrail và quyền deploy tối thiểu. Không cần gửi access key vào chat. Giai đoạn hiện tại không gọi tài khoản.
2. Duyệt residency Mỹ và US geographic inference; kiểm tra model lifecycle/availability thực trong account. Sonnet US geo rate trong dự toán là 3,30/16,50 USD/M token, không lấy giá global inference thấp hơn áp vào geo profile. Check provider terms, data retention, use-case forms và quota.
3. Chuẩn bị SAML metadata HTTPS do doanh nghiệp quản lý, stable subject/email mapping, MFA policy, callback HTTPS chính xác và PKCE. Domain prefix template dùng stack name; giữ stack name chữ thường, số và dấu gạch ngang, đủ ngắn cho Cognito.
4. Package/upload ZIP đã review vào S3 cùng region; giữ S3 Versioning, digest và change log. `ChatCodeSha256` là base64 SHA-256 của ZIP. Mỗi code release phải đổi logical ID của `ChatVersion` hoặc dùng build-specific logical ID để tạo version mới; mỗi thay đổi phương thức API phải tạo `Deployment` logical ID mới. Bản generator hiện dùng ID cố định, phù hợp initial deployment, **không tự động publish release mới chỉ bằng đổi S3 key**.
5. Thực thi và review tests H1–H8. Chạy `scripts/eval_gate.py measured-results.json` với số liệu thật theo schema trong code; đầu vào rỗng phải fail. Không dùng dữ liệu synthetic để khẳng định p95/quality/DR đã đạt.
6. Dựng staging trước. Cài quota, cảnh báo và off-hours schedule; xác nhận DNS-disabled VPC vẫn tương thích control plane của interpreter. Dịch vụ tự tạo ENI/service-linked roles cần được account cho phép. Nếu sandbox không hoạt động, không mở NAT/DNS rộng để “fix”; chọn lại isolated backend và tính lại giá.
7. CloudFormation `validate-template`/change set pre-deploy trong account là lớp riêng sau cfn-lint/Guard. Kiểm tra quota REST streaming timeout, model profile/IAM destinations, alias provisioned concurrency permissions và ENI/session limits. Đọc validation findings trước execute. Không dùng `--disable-validation`.

## Lệnh để review sau khi có đủ đầu vào

Lưu danh sách parameter thật vào `infra/parameters.local.json` (chỉ IDs/ARNs/URLs, không secret). Các parameter bắt buộc gồm `Environment`, `BudgetEmail`, `SamlMetadataUrl`, `CallbackUrl`, `CodeBucket`, `ChatCodeKey`, `WorkerCodeKey`, `ChatCodeSha256`, `ConnectorSecretArns`.

```powershell
aws cloudformation validate-template --template-body file://infra/vbot.template.json --region us-east-1 --profile YOUR_PROFILE
aws cloudformation create-change-set --stack-name vbot-eviaura-staging --change-set-name initial-review --change-set-type CREATE --template-body file://infra/vbot.template.json --parameters file://infra/parameters.local.json --capabilities CAPABILITY_IAM --region us-east-1 --profile YOUR_PROFILE
```

Đây là hướng dẫn cho bước sau, **chưa chạy**. Không tự chạy `execute-change-set`, đăng ký OAuth, bật model hoặc gửi email trong giai đoạn thiết kế. `AWS::Budgets::Budget` có email recipient, nên deployment thực phải dùng địa chỉ chủ tài khoản đã duyệt.

Budget tag `Project` phải activate trong Billing và có thể chậm xuất hiện. Budgets chỉ cảnh báo, không hard stop. Hard stop thực là ledger trước từng model/tool call; ngưỡng model 4.500 USD/tháng chỉ nhỉnh hơn dự toán model, cần cơ chế điều hành khi hết quota chứ không âm thầm vượt. Cost ledger giới hạn phần ứng dụng, không chặn phí storage/logs đã phát sinh hoặc tác động của traffic tấn công.

## Hạn chế DR và giá

Giá có PITR, S3 previous versions và allowance backup/restore; chưa có regional failover. Nếu H7 được hiểu là cả region loss, phải thiết kế bổ sung và báo giá lại trước khi coi kiến trúc hợp lệ. Các line item có URL chính thức nhưng chưa có snapshot SKU/calculator account; validator chỉ kiểm tra format, không xác nhận giá đúng. File hiện tên Eviaura vì chưa có mã nhóm; đổi thành `Gxx_baogia.xlsx` khi có mã thật. Chưa tạo slide thuyết trình trong phạm vi yêu cầu kiến trúc/báo giá/mã hạ tầng này.
