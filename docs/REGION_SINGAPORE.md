# Báo giá Singapore thay cho bản Mỹ

Bản hiện tại: `deliverables/G03_baogia.xlsx` và bản tương thích cùng nội dung `deliverables/Eviaura_baogia.xlsx`. Primary region **ap-southeast-1**. TOTAL **6.022,78 USD/tháng** gồm AWS **5.293,44**, vận hành **200,00**, dự phòng **529,34**, chưa VAT. Duy trì 27 dòng và đủ 19 component bắt buộc. Bộ XLSX có công thức tính lại từng dòng và TOTAL.

Giữ nguyên workload 2.000 DAU, 8 tác vụ/người/ngày, 22 ngày, 20 TB workspace quota và một staging. Đơn giá trả phí đã trích từ AWS Price List công khai theo SKU, unit, publication date và versioned URL trong `deliverables/pricing-ap-southeast-1.json`, ngày kiểm tra 16/10/2026. Không dùng allowance/ưu đãi để giảm giá. Labor, governance 30 USD và contingency là giả định, không phải SKU.

| Hạng mục | Rate Singapore |
|---|---|
| S3 Standard, first tier | 0,025 USD/GB-tháng |
| Lambda ARM on-demand | 0,0000133334 USD/GB-s |
| Lambda ARM provisioned concurrency | 0,0000041593 USD/GB-s |
| REST API requests | 4,25 USD/triệu request |
| DynamoDB Standard | 0,285 USD/GB-tháng, 0,71 USD/M WRU, 0,1425 USD/M RRU |
| Nova Lite | 0,081 input / 0,324 output USD/M token |
| Sonnet 4.5 Global | 3 input / 15 output USD/M token |
| Internet outbound | 0,12 USD/GB, first paid tier |
| CloudWatch log ingest | 0,70 USD/GB |

Điểm cần duyệt về inference:

- [Nova Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html) tại Singapore dùng **APAC inference**, không phải in-region.
- [Sonnet 4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html) tại Singapore dùng **Global inference**. Phải duyệt danh sách destination, không cam kết xử lý dữ liệu chỉ ở Singapore.
- [Nova Canvas](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html) có EOL 30/09/2026 và không có Singapore. Thay bằng [Stable Image Core](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-stability-ai-stable-image-core-1-0.html), model ID `stability.stable-image-core-v1:1`, chạy **us-west-2** ở 0,04 USD/ảnh. Chi phí image transfer đã dự trù thêm 1 GB outbound Singapore và 5 GB return từ Oregon. Không gửi dữ liệu thực trong giai đoạn lập báo giá.

Tổng thấp hơn bản cũ 308,49 USD/tháng **không chứng minh Singapore rẻ hơn trên cùng inference boundary**. Sonnet đổi từ US geo rate 3,30/16,50 sang Global 3/15, đồng thời model ảnh được sửa vì EOL. Các dòng S3, DynamoDB, gateway, log và egress Singapore nhìn chung cao hơn đầu vào bản cũ. Bản cũ giữ tại `deliverables/archive/us-east-1/` để đối chiếu, không dùng nộp.

Kiến trúc/IaC trong tài liệu ban đầu vẫn là US reference. Template IAM đang giới hạn inference US; **không chỉ đổi `--region` rồi deploy Singapore**. Cần cấu hình lại model profile/destination IAM, model ảnh, quota/access và validation tài khoản trước khi triển khai. Báo giá Singapore không tự chứng minh H6/H8 hoặc DR đã đạt. Nếu yêu cầu dữ liệu không rời Singapore, cần chọn lại model có in-region support và tính giá mới.

Tái tạo báo giá Singapore:

```powershell
python scripts/build_sg_rates.py
python scripts/build_sg_quote.py
node scripts/update_sg_quote.mjs
python scripts/check_design.py
```

Các catalog công khai đầu vào được cache tại `.tools/pricing-sg/`. `scripts/build_design.py` là builder US ban đầu, không dùng để tái tạo bảng Singapore.
