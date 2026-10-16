# D1–D2 — giả định chung và sizing

Trạng thái: **bản làm việc của Dũng**, để nhóm dùng cùng một mẫu tính; giá trị ngoài đề là giả định cần chủ mảng xác nhận. Dũng chọn AWS `ap-southeast-1` làm region làm việc, Bảo chốt SKU/topology. Nguồn: [đề bài](../vbot-capstone.html), [Kiệt](../kiet/KIET_MODEL_SERVING.md), [Bảo](../bao/SIZING_AND_COST.md).

| Ký hiệu | Giá trị | Căn cứ / người xác nhận |
| --- | ---: | --- |
| `U` | 2.000 DAU | Đề bài |
| `D` | 22 ngày/tháng | Đề bài |
| `H_work` | 220 giờ/tháng, T2–T6 08:00–18:00 GMT+7 | Đề bài |
| `H_full` | 730 giờ/tháng cho thành phần 24/7 | Đề bài |
| Môi trường | Production HA hai AZ + một staging tách dữ liệu/quyền | Đề bài và thiết kế Bảo; Bảo chốt SKU/giờ staging |
| `r` | **10 request/DAU/ngày** | Dũng dùng giả định Kiệt để thống nhất bản nháp; Kiệt xác nhận trước khi khóa giá |
| `k_peak` | **4×** trung bình trong giờ hành chính | Giả định Kiệt; load test để chứng minh |
| `t_session` | **30 giây/request** cho phiên tương tác đang hoạt động | Giả định Dũng để quy hoạch kết nối; phải đo, không gồm agent nền |
| Quota workspace | 10 GB/user; trần 20.000 GB với 2.000 user | Đề bài; không dùng trần làm dung lượng tính tiền |

## Từ DAU đến tải

`N_req = U × D × r = 2.000 × 22 × 10 = 440.000 request/tháng`.

| Cấp | Tỷ lệ | Request/tháng | Input/output token/request | Input/output triệu token/tháng |
| --- | ---: | ---: | ---: | ---: |
| 1 — email, hỏi đáp | 50% | 220.000 | 1.000 / 250 | 220 / 55 |
| 2 — tài liệu, slide | 25% | 110.000 | 2.400 / 800 | 264 / 88 |
| 3 — dữ liệu, code | 12% | 52.800 | 4.200 / 1.200 | 221,76 / 63,36 |
| 4 — agent dự án | 8% | 35.200 | 9.000 / 2.400 | 316,8 / 84,48 |
| 5 — thiết kế | 5% | 22.000 | 1.500 / 500 | 33 / 11 |
| **Tổng** | **100%** | **440.000** | | **1.055,56 / 301,84** |

Routing theo Kiệt: Micro **349,8M input / 100,1M output**, Pro **705,76M / 201,74M**. Giờ hành chính bình quân `440.000 ÷ (220 × 3.600) = 0,556 request/s`; peak thiết kế `×4 = 2,22 request/s`. Peak pool ≈ **5.331 input token/s + 1.524 output token/s**. Đây là nhu cầu để kiểm quota/latency, chưa phải quota AWS được cấp.

Phiên tương tác đồng thời ước lượng `ceil(2,22 request/s × 30 giây) = 67 phiên` tại peak; agent nền và sandbox là pool riêng. Giả định 30 giây chỉ để sizing connection/gateway, không chứng minh TTFT p95.

Thiết kế cấp 5 có **22.000 request/tháng** xuất SVG/HTML trong baseline, **0 ảnh bitmap**. Nếu nhóm duyệt ngoại lệ bitmap ngoài APAC, giả định 20% cấp 5 thành **4.400 ảnh/tháng** và cộng lại dòng giá/egress; không cộng khoản này vào baseline.

Sandbox: `440.000 × (12% × 80% + 8% × 50%) = 59.840 run/tháng`. Với **60 giây/run** (chưa tính overhead/đơn vị làm tròn hóa đơn), peak `59.840 ÷ (220 × 3.600) × 4 × 60 ≈ 18,1 phiên đồng thời`. Bảo chốt CPU/RAM, startup/cleanup, headroom và khả năng chịu mất AZ trước khi tính giá.

Embedding: `440.000 × 200 token/query = 88M token`; index đầu `10M/12 = 0,833M`; cập nhật `10M × 2% × 22 = 4,4M`; tổng **93,233M token/tháng**. Corpus 10M token và churn 2%/ngày do Kiệt giả định, Phong cần xác nhận; không tính trùng với vector service.

## Dung lượng, connector và egress — giả định quy hoạch Dũng

Các số dưới đây cho phép kiểm tra phép tính trước khi Phong thay bằng sizing dữ liệu thực. Dùng GB thập phân (`1 GB = 10^9 byte`); **không coi là giá hoặc số đo production**.

| Hạng mục | Giả định và công thức | Kết quả quy hoạch |
| --- | --- | ---: |
| Knowledge base được index | Corpus Kiệt 10M token × 4 byte/token; chỉ là text đã trích, chưa gồm file gốc/index | 0,04 GB text |
| Workspace thực dùng | 2.000 user × 1 GB/user; tăng 0,1 GB/user/tháng; quota vẫn là 10 GB/user | 2.000 GB ban đầu, +200 GB/tháng |
| Chat/history | Trần bảo thủ: `(1.055,56M + 301,84M) token × 4 byte`; giữ 90 ngày theo đề xuất Bảo | 5,43 GB/tháng, 16,29 GB/90 ngày |
| Audit | 10 sự kiện/request × 440.000 request × 1 KB/sự kiện × 12 tháng | 4,4 GB/tháng, 52,8 GB/12 tháng trước index/replica |
| Connector đọc | Cấp 1: 1 call/request; cấp 2: 1; cấp 4: 3 | 435.600 call/tháng |
| Connector ghi | Cấp 4: 1 call/request, chỉ sau user approval | 35.200 call/tháng |
| Connector tổng | `(435.600 + 35.200) × 1,2` cho phân trang/retry đọc | 564.960 call/tháng, peak khoảng 2,85 call/s |
| Egress SaaS | 564.960 call × 2 KB request/call | 1,13 GB/tháng |
| Egress về user | 301,84M output token × 4 byte + 5% request xuất artifact × 1 MB | 23,21 GB/tháng |
| **Egress cộng sơ bộ** | SaaS + user; chưa gồm cross-AZ/region, backup và staging | **24,34 GB/tháng** |

Connector response giả định 50 KB/call ⇒ **28,25 GB/tháng ingress**; nếu đi qua NAT cùng request, khoảng **29,38 GB/tháng NAT processed**. Tỷ lệ request phải gọi connector, kích thước file/artifact, dữ liệu nguồn, index overhead và traffic qua từng AZ **chờ Phong/Bảo xác nhận**. Corpus 10M token chỉ là phần chọn lọc rất nhỏ cho RAG, chưa chứng minh đủ độ phủ tìm kiếm toàn tập đoàn; nếu Phong tăng corpus, phải tính lại embedding/vector/storage. Không nhân đôi corpus khi chỉ tăng DAU; chỉ query embedding tăng theo request.

## Cần Phong/Bảo điền để khóa chi phí

| Đầu vào | Công thức/đơn vị cần trả | Chủ |
| --- | --- | --- |
| Tài khoản cấp phép/MAU, IdP hiện có | User/license/tháng; phạm vi SSO/MFA đã mua | Phong + Bảo |
| Workspace thực dùng, tài liệu, vector, DB, audit | GB, vector, request/IOPS; 12 tháng audit, version/replica/backup | Phong |
| Connector | Call/tháng/provider, độ tươi, rate limit, bytes/call và chiều egress | Phong |
| Sandbox | vCPU/RAM/giây và billing minimum/run; idle pool, hai AZ | Bảo + Kiệt |
| Compute/LB/network/DR/monitoring/CI | SKU, số node/AZ, giờ prod/staging, GB truyền/log/backup, đơn giá Singapore | Bảo; Dũng hỗ trợ rà giá |
| H1/H6/H8 | Bedrock private endpoint và điều khoản dữ liệu; quota RPM/TPM; kết quả eval và p95 | Kiệt + Bảo |

**Quy tắc thay đổi:** nếu `r`, mix hoặc region đổi, tính lại chuỗi request → token/sandbox/storage/network → XLSX `TOTAL` → slide. Không lấy 2.000 DAU làm MAU/license khi số tài khoản chưa được xác nhận.
