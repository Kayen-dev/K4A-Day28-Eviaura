# Kiểm tra gói thiết kế AWS

Ngày kiểm tra: 16/10/2026. Không deploy stack, không gọi Bedrock và không truy cập tài khoản AWS.

| Kiểm tra | Kết quả |
|---|---|
| XLSX qua validator gốc `vbot-capstone.html` | **PASS**, 27 dòng chi phí, đủ 19 component bắt buộc, TOTAL cuối cùng khớp **6.331,27 USD/tháng** |
| Cảnh báo validator | 1: Sonnet chiếm khoảng 67% tổng; cần bảo vệ giả định token/routing. Không coi đây là lỗi format. |
| Công thức XLSX | Recalculate bằng artifact-tool; không thấy lỗi công thức. Validator đọc **cached values của XLSX thật**, không chỉ dữ liệu JSON nguồn. |
| Visual QA | Đã render và xem ba sheet BaoGia, TinhGia, Sizing ở các vùng đầu; chưa kiểm tra bằng Microsoft Excel native. |
| CloudFormation schema/IAM | **cfn-lint 1.57.2: 0 findings**, region us-east-1; 42 resources; 44.962 bytes, dưới giới hạn inline 51.200 bytes. |
| CloudFormation Guard | **6/6 project rules PASS**, dùng guardpycfn 0.1.0. Không phải chứng nhận tuân thủ toàn bộ AWS rules registry. |
| Eval gate logic | **5 tests PASS**; kiểm tra fail-closed khi thiếu số liệu, dưới 95% ở một cấp, vượt latency/RPO, safety violations và score NaN. Fixture synthetic chỉ kiểm tra code gate. |
| Whitespace | `git diff --check` PASS sau các thay đổi code/tài liệu. |

Giá chính gồm AWS định kỳ **5.573,88 USD**, labor **200,00 USD**, dự phòng **557,39 USD**; chưa VAT. Giả định 2.000 DAU, 8 tác vụ/người/ngày, 22 ngày, dùng đủ quota workspace 20 TB và một staging. Khoản compute đã tính thời gian worker chờ sandbox, không chỉ thời gian chạy code bên trong sandbox.

So sánh cùng workload: toàn bộ text request dùng Sonnet tham chiếu **11.478,78 USD/tháng**; routing dự kiến thấp hơn **44,84%**, chỉ có ý nghĩa nếu eval từng cấp đạt H8. Đây là chênh lệch dự toán, chưa phải savings thực tế. Dự toán workspace 1 GB/người là **5.875,87 USD/tháng**; backup allowance giữ nguyên. Envelope 4.000 DAU **12.562,54 USD/tháng**, chưa phải báo giá SKU đã resize.

Chưa kiểm chứng: đơn giá/SKU bằng snapshot hoặc AWS Calculator; model lifecycle/access/quota trong account; SAML/MFA/OAuth thật; ACL/DLP/budget race; sandbox egress/resource/cleanup; peak p95 TTFT từ Việt Nam; chất lượng ≥95% baseline; availability và restore RTO/RPO. Chưa có application ZIP, pipeline, backup automation hoặc regional failover. Mã hạ tầng và danh sách tích hợp còn cần nằm trong `docs/DEPLOYMENT.md`.

XLSX pass validator chỉ chứng minh định dạng và phép cộng. Không chứng minh H1–H8 đã đạt, đơn giá đã được giám khảo chấp nhận hay hệ thống đã chạy production. Cần mã nhóm thật trước khi đổi tên file nộp thành `Gxx_baogia.xlsx`.

Các lệnh đã chạy:

```powershell
python scripts/build_design.py
python scripts/build_infra.py
python scripts/validate_infra.py
python -m unittest discover -s scripts -p 'test_*.py' -v
node scripts/build_quote.mjs
python scripts/check_design.py
git diff --check
```
