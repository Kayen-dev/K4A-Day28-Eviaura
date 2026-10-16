# Bàn giao của Tuấn Kiệt — model serving VBot

Theo [đề bài](../vbot-capstone.html) và checkpoint K1–K6 trong [TEAMMATE_PLAN.md](../TEAMMATE_PLAN.md). Đây chỉ là phần chi phí của Kiệt để Dũng ghép vào báo giá toàn hệ thống, **không phải tổng dự án**.

## Quyết định và giả định

- Cloud chính: **AWS `ap-southeast-1` (Singapore)**. Hạ tầng ứng dụng, dữ liệu lưu trữ và API đặt ở Singapore. Region này hợp lý về địa lý cho người dùng Việt Nam, nhưng không đồng nghĩa mọi suy luận đều ở Singapore.
- Text: Bedrock Runtime với **Nova Micro** (`apac.amazon.nova-micro-v1:0`) cho việc nhẹ và **Nova Pro** (`apac.amazon.nova-pro-v1:0`) cho việc khó. Đây là **Geo Cross-Region Inference APAC**: request từ Singapore có thể được xử lý ở region APAC khác. Nhóm phải duyệt chính sách lưu trú dữ liệu và kiểm tra p95 trước khi khóa. [AWS công bố hỗ trợ APAC](https://aws.amazon.com/about-aws/whats-new/2025/02/amazon-nova-understanding-models-europe-asia-pacific/), [bảng region/model](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html).
- Embedding: Cohere Embed Multilingual v3 (`cohere.embed-multilingual-v3`) chạy **in-region Singapore** cho RAG tiếng Việt/Anh. Model còn active theo [model card AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-cohere-embed-multilingual.html). Phong xác nhận dimension, cách chunk/index và corpus.
- Cấp 5: mặc định dùng Nova để xuất HTML/SVG/mockup chỉnh sửa được. Dự phòng ảnh bitmap qua Stable Image Core 1.0 ở **`us-west-2`**, vì model này không có endpoint Singapore. Đây là **ngoại lệ đưa prompt ảnh ra ngoài APAC**, chỉ bật sau khi nhóm/đơn vị chấp thuận; nếu không, khóa tính năng bitmap hoặc chọn nhà cung cấp khác và báo giá lại. [Model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-stability-ai-stable-image-core-1-0.html). Không dùng Nova Canvas/Titan Image Generator đời cũ đã EOL.
- Đầu bài đã chốt **2.000 người dùng hoạt động mỗi ngày**, **10 GB quota/người**, **T2–T6 08:00–18:00 GMT+7**, **22 ngày/tháng**. Vậy cửa sổ tải là **220 giờ/tháng**; 10 GB/người là giới hạn logic tối đa **20.000 GB (20 TB)**, không phải lượng lưu trữ đã sử dụng. Storage thực dùng, bản sao, backup do Phong/Bảo báo giá.
- **Chưa chốt số request/người/ngày.** Để tính minh họa, Kiệt dùng **10 request/DAU/ngày**, tương ứng **440.000 request/tháng**. Dũng cần duyệt hoặc thay bằng số khác; tất cả chi phí text/ảnh/embedding/gateway phải tính lại tỷ lệ thuận khi số request đổi.

## K1–K2: 5 cấp và sizing

| Cấp | Tác vụ | Tỷ lệ | Request/tháng | Input/output token mỗi request | Micro/Pro | Input/output triệu token/tháng |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Email, hỏi đáp/RAG ngắn | 50% | 220.000 | 1.000/250 | 90%/10% | 220/55 |
| 2 | Báo cáo, DOCX/XLSX/PPTX | 25% | 110.000 | 2.400/800 | 50%/50% | 264/88 |
| 3 | Phân tích bảng tính, script/code | 12% | 52.800 | 4.200/1.200 | 0%/100% | 221,76/63,36 |
| 4 | Agent dự án nhiều bước | 8% | 35.200 | 9.000/2.400 | 0%/100% | 316,8/84,48 |
| 5 | Mockup, sơ đồ, minh họa | 5% | 22.000 | 1.500/500 | 60%/40% | 33/11 |

Tổng text: **1.055,56M input / 301,84M output token/tháng**. Micro nhận **349,8M/100,1M**, Pro nhận **705,76M/201,74M**; lần lượt **266.200 / 173.800 request/tháng**. Token là giả định có tính system prompt, RAG, lịch sử ngắn và các bước agent; chưa đo log. Giả định 20% request cấp 5 yêu cầu bitmap = **4.400 ảnh/tháng**, chỉ tính chi phí nếu ngoại lệ ngoài APAC được duyệt.

Trung bình trong giờ hành chính: `440.000/(220×3.600)=0,556 request/s`. Giả định peak **4×**: **2,22 request/s**, khoảng **5.331 input token/s và 1.524 output token/s** toàn pool. Đây là nhu cầu quota, **không phải quota AWS đã cấp**. Báo cho Bảo kiểm tra RPM/TPM của từng inference profile, throttling và giới hạn tài khoản.

Sandbox cho Bảo: giả định 80% cấp 3 và 50% cấp 4 chạy tool/code, nên **59.840 lượt/tháng**. Nếu một lượt giữ sandbox 1 phút, peak 4× ≈ **18,1 sandbox đồng thời**. Bảo quyết định CPU/RAM, queue, timeout và dòng giá `sandbox`.

Embedding cho Phong: 440.000 query × 200 token = **88M token/tháng**; giả định corpus 10M token, cập nhật 2% × 22 ngày = 4,4M; phân bổ index đầu 10M/12 = 0,833M. Tổng **93,233M embedding token/tháng**. Phong xác nhận corpus và tránh tính trùng nếu search service đã thu phí embedding.

## K3–K5: giá tham khảo, routing và cổng chất lượng

AWS [Price List API Singapore](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/ap-southeast-1/index.json) ghi Standard On-Demand theo SKU: Nova Micro **$0,047/M input + $0,188/M output** (`4KEEE3KE8SAX8673`, `8ZARPNED4P2CRQ3C`); Nova Pro **$1,08/M input + $4,32/M output** (`XPEGXF3HSTPDCWRN`, `42JMX7GP83AUXPWJ`). Giá tại source region Singapore cho APAC cross-region, không cộng phụ phí định tuyến theo [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html). Cần lưu snapshot giá/SKU vào sheet `BangChung` khi nộp vì giá có thể đổi.

| Dòng `BaoGia` | Công thức | USD/tháng |
| --- | --- | ---: |
| `llm` Nova Micro | `349,8×0,047 + 100,1×0,188` | **35,26** |
| `llm` Nova Pro | `705,76×1,08 + 201,74×4,32` | **1.633,74** |
| `llm` Stable Image Core, **chỉ khi duyệt ngoại lệ** | `4.400×$0,04/ảnh` | **176,00** |
| `embedding` Cohere Embed Multilingual v3 | `93,233×$0,10/M token` | **9,32** |
| `gateway` API Gateway REST, **đơn giá tạm** | `0,44M×$3,50/M request` | **1,54** |
| **Cộng phần Kiệt nếu bật bitmap** | Tổng dòng đã làm tròn | **1.855,86** |
| **Cộng phần Kiệt nếu không bật bitmap** | Không gồm $176 bitmap | **1.679,86** |

Giá ảnh $0,04/ảnh dựa trên [AWS Samples](https://github.com/aws-samples/genai-sticker-printing); giá Cohere $0,10/M lấy từ [ví dụ AWS Bedrock](https://aws.amazon.com/bedrock/pricing/). Dòng API Gateway $3,50/M là **ước lượng chưa xác nhận SKU Singapore** từ [trang giá AWS](https://aws.amazon.com/api-gateway/pricing/), cần đối soát AWS Calculator trước khi khóa. REST API cần cho [response streaming](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-transfer-mode.html); HTTP API không hỗ trợ tính năng này. Mọi giá là USD/tháng trước VAT, không trừ free tier, không gồm traffic truyền dữ liệu, VPC/PrivateLink, guardrails, storage, compute, staging hoặc sandbox.

**So sánh:** nếu toàn bộ text dùng Nova Pro thì `(1.055,56×1,08)+(301,84×4,32)=**$2.443,95/tháng**`; routing Micro/Pro = **$1.669,00/tháng** (tổng hai dòng làm tròn), tiết kiệm **$774,95/tháng**, *chỉ nếu Micro vượt eval*. Tự host không được ghi là rẻ hơn khi chưa có benchmark GPU/tốc độ ở Singapore và dự toán 2 AZ, EBS, vận hành; chọn managed API làm phương án A. Với giả định tối thiểu **2 GPU node × 730 giờ**, giá compute hòa vốn lý thuyết phải **≤ $1,143/node-giờ** (`1.669/1.460`) *trước* EBS, mạng, staging và nhân công; thực tế ngưỡng phải thấp hơn. Đây là ngưỡng, **không phải báo giá GPU**. Hybrid chỉ hợp lý khi có workload ổn định đủ lớn và benchmark throughput, không tự nhận đã tối ưu.

Gateway app trên compute của Bảo định tuyến theo độ khó, gắn ACL trước RAG/tool, ghi `user_id`, đơn vị, model, token, giá, latency; quota theo user/đơn vị và cảnh báo 70/90% ngân sách. Cache chỉ cho nội dung công khai hoặc key có `tenant_id` + ACL version + prompt/model version + TTL; **giả định cache hit 0% trong báo giá** để không kê tiết kiệm chưa đo. Khi gần trần, giảm context/ảnh tùy chọn rồi mới route sang Micro **cho cấp đã qua eval**; không hạ cấp code/agent chỉ để tiết kiệm. Fallback khi Micro lỗi/throttle là Pro nếu còn quota, sau đó trả lỗi có thể thử lại; agent/tool ghi phải retry có giới hạn và idempotency.

**Eval chưa chạy:** tối thiểu 100 case/cấp bằng tiếng Việt/Anh, gồm ACL, prompt injection, sự thật, định dạng; hai người chấm độc lập thang 0–5. Pro là reference cho text; Micro chỉ nhận một cấp nếu điểm trung bình `Micro/Pro ≥95%` và **0 lỗi rò rỉ dữ liệu/hành động sai quyền**. Cấp 3 cần unit test trong sandbox; cấp 4 cần tool trace và human approval; bitmap cần benchmark riêng. Đây là tiêu chí đề xuất, chưa phải kết quả đo. Nếu Nova Pro không đạt chất lượng tham chiếu, thay model và tính lại giá.

**H6/H8 chưa chứng minh:** TTFT p95 ≤3 giây là mục tiêu; budget thiết kế 0,20s gateway + 0,55s RAG + 0,15s routing + 1,80s model + 0,20s mạng = **2,90s**, không phải đo thực tế. Chạy 30 phút peak 2,22 RPS với mix thật, ghi p50/p95/p99, timeout, throttling, queue; agent cấp 4 hoàn thành ≤10 phút gồm chờ queue/tool/sandbox. Geo routing có thể ảnh hưởng latency. Chỉ tuyên bố đạt H6/H8 sau đo và có log/bằng chứng.

## Checkpoint còn mở

| Mục | Trạng thái | Cần làm trước khi nộp |
| --- | --- | --- |
| K1 | Đã thiết kế model/routing/eval | Chạy eval nội bộ, xác nhận Micro và Pro đạt chất lượng |
| K2 | Đã tính sizing theo giả định | Dũng chốt request/DAU/ngày; Phong chốt corpus; Bảo xác nhận RPM/TPM/sandbox và 10 GB quota |
| K3 | Đã chọn API, có phương án B | Benchmark/Calculator nếu nhóm muốn kết luận chi phí self-host |
| K4 | Đã định nghĩa phép đo H6/H8 | Chạy load test trên tài khoản thật trong giờ hành chính |
| K5 | Đã chuẩn bị slide và dòng Excel | Dũng đối soát giá Singapore; nhóm phê duyệt/loại ngoại lệ bitmap ngoài APAC |
| K6 | Chưa thể khóa | Cần deck/XLSX master của Dũng để kiểm tra số cuối |

Đầu ra: [nội dung slide 4–5](./KIET_SLIDES_04_05.md), [dòng Excel dạng TSV](./KIET_BAOGIA.tsv). Không cộng dòng `TOTAL` của Kiệt vào `BaoGia`; Dũng lập `TOTAL` chung.
