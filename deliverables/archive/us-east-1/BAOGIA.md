# Báo giá AWS dự kiến — VBot Eviaura

USD/tháng, chưa VAT; 2.000 DAU; production + staging. Không khấu trừ ưu đãi. Đơn giá là đầu vào lập kế hoạch, cần chốt SKU và ảnh bảng giá trước khi nộp.

| Component | Hạng mục | USD/tháng |
|---|---|---:|
| compute | Chat streaming Lambda ARM | 49.35 |
| compute | Background worker và chờ sandbox | 112.37 |
| compute | Provisioned concurrency giờ hành chính | 13.20 |
| llm | Nova Lite: L1/L2/L5 | 86.43 |
| llm | Sonnet 4.5: L3/L4 và escalation | 4,217.87 |
| llm | Nova Canvas: ảnh 1024 standard | 155.23 |
| gateway | API Gateway REST + router | 3.50 |
| load_balancer | Managed regional request distribution | 0.00 |
| authn | Cognito enterprise federation | 31.50 |
| authz | RBAC/ABAC và ACL kiểm tra lại | 0.00 |
| database | DynamoDB Standard on-demand | 20.00 |
| vector_db | S3 Vectors storage and ingestion | 0.61 |
| vector_db | S3 Vectors queries | 3.90 |
| object_storage | Workspace quota đầy đủ + KB + staging | 466.90 |
| object_storage | S3 object requests | 14.00 |
| cache_queue | SQS + TTL cache | 1.20 |
| sandbox | AgentCore Code Interpreter VPC | 156.83 |
| connectors | Delegated OAuth Lambda workers | 26.87 |
| secrets_kms | KMS và OAuth app secrets | 9.50 |
| backup_dr | PITR + object versions + restore drill | 108.50 |
| monitoring | CloudWatch + S3 audit 12 tháng | 23.12 |
| governance | DLP/guardrail và eval allowance | 30.00 |
| network | Internet egress + regional WAF | 35.60 |
| cicd | CodeBuild và staging | 5.00 |
| embedding | Titan Text Embeddings V2 | 2.40 |
| ops_labor | Vận hành và trực giờ hành chính | 200.00 |
| contingency | Dự phòng biến động tải và đơn giá | 557.39 |
| TOTAL | Có công vận hành và dự phòng | **6,331.27** |

AWS định kỳ: **5,573.88**; công vận hành: **200.00**; dự phòng: **557.39**; tổng/DAU: **3.17**.

Tất cả text request dùng Sonnet tham chiếu: **11,478.78**. Workspace chỉ dùng 1 GB/người: **5,875.87**. 4.000 DAU: envelope tuyến tính **12,562.54**, cần sizing và quota lại.

Chi tiết công thức và nguồn: `Eviaura_baogia.xlsx` và `cost-model.json`. Giá rẻ của model chỉ áp dụng sau eval đạt H8; hiện chưa có dữ liệu chứng minh.
