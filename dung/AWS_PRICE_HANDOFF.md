# Giá cần Bảo chốt — AWS Singapore

Dũng hỗ trợ tìm nguồn cho sáu component vận hành; **chưa phải dòng tiền để ghép XLSX** vì chưa có SKU, quy mô và bản tính Singapore. Dùng [AWS Pricing Calculator](https://calculator.aws/#/) để khóa region `ap-southeast-1`, xuất hoặc chia sẻ estimate theo [hướng dẫn AWS](https://docs.aws.amazon.com/pricing-calculator/latest/userguide/save-share-estimate.html), rồi lưu SKU/đơn giá/số lượng/ngày lấy giá. Không trừ free tier, trial hay credit.

| Component | Meter phải tính | Nguồn AWS chính thức | Bảo xác nhận |
| --- | --- | --- | --- |
| `compute` | Prod: node × 730h × USD/node-h, tối thiểu hai AZ; staging: node × giờ thực; disk riêng nếu có | [EC2 On-Demand](https://aws.amazon.com/ec2/pricing/on-demand/) | Loại instance, số node/AZ, khả năng giữ peak sau mất AZ, staging |
| `load_balancer` | ALB-hour + LCU-hour, traffic/connection/rule; WAF nếu dùng tính riêng | [Elastic Load Balancing](https://aws.amazon.com/elasticloadbalancing/pricing/) | Số ALB, LCU, WAF, tính HA managed |
| `network` | VPC link V2 cho API Gateway REST → ALB, NAT-hour + GB processed, VPC endpoint-hour/GB, public IPv4, Internet/cross-AZ/cross-region egress | [VPC](https://aws.amazon.com/vpc/pricing/), [AWS PrivateLink](https://aws.amazon.com/privatelink/pricing/), [private integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/private-integration.html) | Đường gọi Bedrock/connector, AZ, endpoint nào; không tính cùng GB hai lần |
| `backup_dr` | GB-month lưu backup, bản sao, restore test và transfer; phân biệt replica HA ở `database` | [AWS Backup](https://aws.amazon.com/backup/pricing/) | RPO ≤1h, RTO ≤4h, retention 35 ngày đề xuất, drill |
| `monitoring` | Log ingest/storage 12 tháng audit, hot 30 ngày vận hành, metric/trace/alarm/query | [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) | GB log, retention, số custom metric/alarm; archive ở đâu |
| `cicd` | Build-minute theo compute type, artifact/registry, scan nếu tính phí | [CodeBuild](https://aws.amazon.com/codebuild/pricing/) | Build/tháng × phút/build; staging runtime ở `compute`/data, không cộng lại |

**Điểm cần xem trước khi khóa:** ALB có hai meter giờ và LCU; NAT và endpoint có phí cố định/GB; Backup tính theo tài nguyên và restore; CloudWatch có giá theo region; CodeBuild làm tròn thời lượng build theo chính sách dịch vụ. Trang giá là nguồn meter, nhưng bằng chứng cuối phải cho thấy **Singapore + SKU + đơn giá** của cấu hình nhóm chọn.
