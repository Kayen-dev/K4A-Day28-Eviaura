# Nội dung slide 4–5 — Hồ Đình Tuấn Kiệt

Các số sau là **ước lượng**, dựa trên 2.000 DAU, **giả định chưa chốt 10 request/người/ngày**, 22 ngày × 10 giờ hành chính (T2–T6, 08:00–18:00 GMT+7). Chi tiết: [KIET_MODEL_SERVING.md](./KIET_MODEL_SERVING.md).

## Slide 4 — Model serving theo 5 cấp

**Thông điệp:** AWS `ap-southeast-1` cho app/data, Bedrock Nova Micro/Pro theo profile **APAC cross-region**. 440.000 request/tháng giả định: 266.200 Micro, 173.800 Pro; RAG dùng Cohere Embed Multilingual v3 in-region Singapore. Quota 10 GB/người = tối đa logic 20 TB; lưu trữ thực do Phong/Bảo tính.

| Cấp | Tác vụ | Route đề xuất | Request/tháng |
| --- | --- | --- | ---: |
| 1 | Email, hỏi đáp ngắn | 90% Micro / 10% Pro | 220.000 |
| 2 | Báo cáo, DOCX/XLSX/PPTX | 50% Micro / 50% Pro | 110.000 |
| 3 | Bảng tính, script, code | Pro + sandbox | 52.800 |
| 4 | Agent nhiều bước | Pro + queue + duyệt người dùng | 35.200 |
| 5 | Mockup/sơ đồ/ảnh | Micro/Pro cho HTML/SVG; bitmap tùy chọn | 22.000 |

Luồng vẽ: `User → SSO/API Gateway REST → app gateway (ACL/quota/router) → Nova Micro/Pro → guardrail → User`; nhánh RAG gọi Cohere/index, nhánh code gọi sandbox. 20% cấp 5 = 4.400 bitmap/tháng **chỉ khi nhóm duyệt ngoại lệ Stable Image Core ở Oregon**; nếu không, giữ HTML/SVG và bỏ $176 dòng ảnh. Phải công khai APAC cross-region cho text; không hứa mọi suy luận ở Singapore.

**Cổng chất lượng:** 100 case/cấp, hai người chấm, Micro ≥95% điểm Pro và 0 lỗi ACL/PII mới định tuyến theo tỷ lệ trên. **Chưa chạy eval**.

## Slide 5 — Chi phí, độ trễ, quyết định

**Phần Kiệt:** **$1.679,86/tháng** không bitmap; **$1.855,86/tháng** nếu bật 4.400 bitmap ngoài APAC. Trong phương án có ảnh: Micro $35,26; Pro $1.633,74; ảnh $176; embedding $9,32; REST Gateway ước lượng $1,54. Đây chưa phải tổng dự án và chưa gồm compute/storage/network/staging/sandbox/guardrail.

| Phương án text | USD/tháng | Kết luận |
| --- | ---: | --- |
| Micro + Pro theo eval | **1.669,00** | Chọn tạm; tiết kiệm khi Micro qua cổng 95% |
| Toàn bộ Pro | **2.443,95** | Tăng $774,95/tháng, đơn giản hơn |
| Tự host 2 AZ | Chưa định giá | Ngưỡng lý thuyết ≤$1,143/GPU-node-giờ trước chi phí phụ; cần benchmark Singapore |

Peak giả định **2,22 request/s**, **5.331 input token/s**, **1.524 output token/s** trong 220 giờ/tháng. TTFT p95 ≤3s và agent ≤10 phút là **mục tiêu chưa đo**; cần load test ở peak và kiểm tra quota Bedrock. Theo dõi chi phí/latency từng request; cảnh báo ngân sách 70/90%; chỉ hạ cấp model sau eval.

Nguồn cho chân slide: [AWS price list Singapore](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/ap-southeast-1/index.json), [AWS region/model](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html), [AWS API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/). Giá ảnh, embedding và Gateway cần đối soát snapshot khi chốt Excel; ngoại lệ ảnh ngoài APAC cần nhóm phê duyệt.
