# Báo giá Singapore — G03 Eviaura

**6,022.78 USD/tháng**, chưa VAT. AWS 5,293.44, labor 200.00, dự phòng 529.34. Cùng workload 2.000 DAU, 8 tác vụ/người/ngày, 22 ngày, full workspace quota và một staging.

Primary region: **ap-southeast-1**. Nova Lite dùng APAC inference, Sonnet 4.5 dùng Global inference, ảnh dùng Stable Image Core tại us-west-2. Không khẳng định toàn bộ dữ liệu model lưu/xử lý tại Singapore. Nova Canvas đã được thay vì EOL.

| Component | Hạng mục | USD/tháng |
|---|---|---:|
| compute | Chat streaming Lambda ARM | 49.35 |
| compute | Background worker và chờ sandbox | 112.37 |
| compute | Provisioned concurrency giờ hành chính | 16.47 |
| llm | Nova Lite: L1/L2/L5 | 116.68 |
| llm | Sonnet 4.5: L3/L4 và escalation | 3,834.42 |
| llm | Stable Image Core: sinh ảnh | 155.23 |
| gateway | API Gateway REST + router | 4.25 |
| load_balancer | Managed regional request distribution | 0.00 |
| authn | Cognito enterprise federation | 31.50 |
| authz | RBAC/ABAC và ACL kiểm tra lại | 0.00 |
| database | DynamoDB Standard on-demand | 22.78 |
| vector_db | S3 Vectors storage and ingestion | 0.67 |
| vector_db | S3 Vectors queries | 4.26 |
| object_storage | Workspace quota đầy đủ + KB + staging | 507.50 |
| object_storage | S3 object requests | 14.00 |
| cache_queue | SQS + TTL cache | 1.20 |
| sandbox | AgentCore Code Interpreter VPC | 156.83 |
| connectors | Delegated OAuth Lambda workers | 26.87 |
| secrets_kms | KMS và OAuth app secrets | 9.50 |
| backup_dr | PITR + object versions + restore drill | 118.81 |
| monitoring | CloudWatch + S3 audit 12 tháng | 27.60 |
| governance | DLP/guardrail và eval allowance | 30.00 |
| network | Internet egress + regional WAF | 44.79 |
| cicd | CodeBuild và staging | 5.00 |
| embedding | Titan Text Embeddings V2 | 3.36 |
| ops_labor | Vận hành và trực giờ hành chính | 200.00 |
| contingency | Dự phòng biến động tải và đơn giá | 529.34 |
| TOTAL | | **6,022.78** |

Bản cũ us-east-1: 6,331.27. Chênh lệch -308.49 USD. Đây không phải phép so sánh riêng region: Sonnet đổi US geo sang Global và model ảnh được thay do EOL.

Đơn giá billable có SKU, publication date và URL versioned AWS catalog trong `pricing-ap-southeast-1.json`. Không khấu trừ ưu đãi. Governance 30 USD là allowance, labor và contingency là giả định. Chưa đo H6/H8/DR hoặc xác minh quyền model trong account.
