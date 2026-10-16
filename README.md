# K4A-Day28-Eviaura — VBot Production Capstone

## Tổng quan

Phần chuẩn bị của Trường Bảo: [thiết kế bảo mật/sandbox, HA/vận hành, sizing/chi phí và nội dung slide 8–10](./bao/README.md). Đây là bản đề xuất chờ nhóm xác nhận cloud, tải và bằng chứng giá.

Bài capstone yêu cầu thiết kế **VBot Workplace** — trợ lý AI văn phòng nội bộ chạy trên cloud, kết nối Google Workspace, Microsoft 365/Outlook, Notion, Jira và Confluence.

Mục tiêu là xây dựng kiến trúc production cho **2.000 người dùng hoạt động mỗi ngày (DAU)**, giữ chất lượng và các yêu cầu vận hành/bảo mật, đồng thời đạt **hóa đơn hạ tầng hàng tháng thấp nhất** trong các nhóm hợp lệ.

Đề bài và công cụ kiểm tra báo giá nằm trong [vbot-capstone.html](./vbot-capstone.html). Trang HTML có checklist, mẫu báo giá và validator chạy ngay trên trình duyệt; file XLSX không được tải lên máy chủ.

## Đầu ra cần nộp

### 1. Slide thuyết trình

- Tối đa **15 slide nội dung**, tỷ lệ 16:9, PPTX hoặc PDF, tối đa 10 MB.
- Thời lượng trình bày: **7 phút**, sau đó 3 phút hỏi đáp.
- Tên file: `G03_slide.pdf` hoặc `G03_slide.pptx` — thay `03` bằng mã nhóm.
- Slide phải thể hiện:
  - giả định tải từ 2.000 DAU và công thức sizing;
  - sơ đồ kiến trúc đầy đủ component, có mã component trên từng hộp;
  - luồng một request từ SSO/LB/gateway đến model, connector, sandbox và chiều ngược lại;
  - lựa chọn model, routing, API/self-host/hybrid và lý do chọn công nghệ;
  - connector, phân quyền tài liệu, workspace riêng và sandbox;
  - AI governance, data governance, HA, backup/DR, monitoring và FinOps;
  - tổng chi phí USD/tháng, USD/DAU, các hạng mục lớn nhất và đòn bẩy tiết kiệm;
  - rủi ro chính và tác động khi DAU tăng gấp đôi.

### 2. Báo giá hạ tầng XLSX

- Tên file: `G03_baogia.xlsx`.
- Sheet bắt buộc: `BaoGia`; sheet `BangChung` dùng khi tham chiếu ảnh bằng mã `E01`, `E02`, …
- Sheet `BaoGia` có đúng 5 cột:

| Cột | Nội dung |
|---|---|
| `Component` | Mã component trong danh sách bên dưới; dòng cuối là `TOTAL` |
| `Ý nghĩa` | Hạng mục là gì và dùng để làm gì |
| `Ghi chú` | Dịch vụ/SKU, region, đơn giá × số lượng, sizing, HA, staging; tối thiểu 15 ký tự |
| `Chi phí/tháng (USD)` | Số không âm; dùng dấu chấm cho phần thập phân |
| `Bằng chứng` | URL, ảnh hoặc mã `E01`…; nhiều mục cách nhau bằng dấu `;` |

- Mỗi dòng là một khoản chi phí tháng; một component có thể có nhiều dòng.
- Dòng `TOTAL` phải là dòng cuối và bằng tổng các dòng chi phí.
- Mỗi khoản phải có link trang giá chính thức, calculator/bảng tính đã lưu hoặc ảnh chụp có thể đối chiếu SKU, region và đơn giá.
- Không dùng free tier, trial, promotional/startup credit hoặc giá đàm phán riêng.
- `ops_labor` và `contingency` có thể ghi `NA` ở cột bằng chứng; chi phí `0` chỉ hợp lệ khi ghi rõ đã nằm trong dịch vụ khác.

## Năm cấp tác vụ của sản phẩm

1. **Email và hỏi đáp:** soạn/trả lời/tóm tắt thread, tra cứu tài liệu nội bộ.
2. **Tài liệu và slide:** tạo báo cáo, biên bản, tờ trình; xuất DOCX/XLSX/PPTX.
3. **Dữ liệu và code:** phân tích spreadsheet, viết/sửa/review code trong sandbox.
4. **Agent dự án:** đọc Jira/Confluence/Notion, lập kế hoạch, tạo ticket, cập nhật trang.
5. **Thiết kế:** tạo mockup, sơ đồ và hình minh họa.

Agent phải hành động bằng OAuth ủy nhiệm của người dùng với scope tối thiểu; không dùng service account có quyền đọc toàn bộ tập đoàn. Mỗi nhân viên có workspace riêng, lịch sử chat, bộ nhớ dài hạn và quota lưu trữ 10 GB.

## Giả định sizing bắt buộc

Đề cho sẵn:

- 2.000 DAU, giờ hành chính Thứ 2–Thứ 6, 08:00–18:00 GMT+7.
- 22 ngày làm việc/tháng.
- Production và 1 staging.
- Chạy 24/7 tính 730 giờ/tháng; giờ hành chính tính 220 giờ/tháng.
- Đơn vị tiền tệ: USD, chưa VAT.

Nhóm phải tự ước lượng và ghi công thức cho request/người/ngày, tỷ lệ 5 cấp tác vụ, token input/output, peak RPS/token/số phiên, lượt và thời gian sandbox, ảnh sinh ra, dung lượng knowledge base/workspace/chat/audit, số lượt gọi connector và egress.

## 19 component hạ tầng

Các component bắt buộc trong báo giá/sơ đồ gồm:

`compute`, `llm`, `gateway`, `load_balancer`, `authn`, `authz`, `database`, `vector_db`, `object_storage`, `cache_queue`, `sandbox`, `connectors`, `secrets_kms`, `backup_dr`, `monitoring`, `governance`, `network`, `cicd`, `ops_labor`.

Component tùy chọn: `embedding`, `licenses`, `contingency`, `other`.

## Cổng chất lượng H1–H8

Giá rẻ chỉ có giá trị khi đạt đủ các ràng buộc sau:

- **H1 — Cloud:** chọn một cloud chính, nêu region và lý do; model API bên ngoài phải đi qua private endpoint hoặc kênh cam kết không lưu dữ liệu.
- **H2 — Định danh/phân quyền:** SSO OIDC/SAML, MFA, RBAC/ABAC, ACL tài liệu, OAuth scope tối thiểu và token vault mã hóa.
- **H3 — Cô lập user/sandbox:** workspace, memory và kết quả tìm kiếm tách theo người; sandbox container/microVM, mặc định không egress, giới hạn tài nguyên và hủy sau khi chạy.
- **H4 — AI governance:** guardrail input/output, chống prompt injection, xác nhận người dùng trước hành động ghi ra ngoài và eval gate khi đổi model/prompt.
- **H5 — Data governance:** mã hóa lúc lưu/truyền, DLP/che PII, phân loại dữ liệu, retention, audit log 12 tháng; nhà cung cấp model không huấn luyện trên dữ liệu.
- **H6 — Độ trễ:** p95 time-to-first-token không quá 3 giây giờ cao điểm; agent nền hoàn thành trong 10 phút và có thông báo.
- **H7 — HA/backup/DR:** khả dụng 99,5% giờ hành chính, không single point of failure ở LB/gateway/database, backup có kiểm thử; RTO 4 giờ, RPO 1 giờ.
- **H8 — Chất lượng/chi phí:** mỗi cấp tác vụ đạt tối thiểu 95% điểm model tham chiếu; có quota, cảnh báo ngân sách và cơ chế cắt khi vượt.

Nếu thiếu component bắt buộc hoặc vi phạm H1–H8, điểm chi phí bị giới hạn tối đa 10/20.

## Cách chấm và lỗi thường gặp

Tổng 100 điểm:

- Kiến trúc và độ phủ component: 25
- Báo giá, bằng chứng và sizing: 20
- Hiệu quả chi phí: 20
- Bảo mật, sandbox, governance: 15
- Lý do chọn công nghệ/model: 10
- Trình bày và hỏi đáp: 10

Điểm chi phí: `20 × (TOTAL thấp nhất trong các nhóm hợp lệ / TOTAL của nhóm)`.

Các lỗi bị trừ điểm:

- Báo giá không qua validator: -10 và điểm chi phí bằng 0.
- TOTAL trên slide khác TOTAL trong XLSX: -5.
- Mỗi dòng dùng free tier/trial/credit hoặc bằng chứng không khớp: -5, tối đa -15.
- Nộp trễ: -5 mỗi 5 phút.

## Quy trình làm bài đề xuất

1. Đọc `vbot-capstone.html`, chia nhóm theo 5 vai: kiến trúc trưởng; model serving; data/workspace; sandbox/bảo mật/governance; cloud/HA/vận hành.
2. Chốt giả định tải và hướng LLM: API, tự host hoặc hybrid.
3. Vẽ kiến trúc, chọn dịch vụ/region và lấy bằng chứng giá ngay khi sizing.
4. Hoàn thiện `BaoGia`, `BangChung`, kiểm tra bằng validator trong HTML.
5. Làm slide, bảo đảm tổng chi phí và các giả định khớp XLSX.
6. Chạy lại validator, kiểm checklist slide và đặt đúng tên file trước khi nộp Google Form.

## Kiểm tra nhanh

Mở file HTML bằng trình duyệt:

```text
vbot-capstone.html
```

Trong phần **Báo giá**, chọn hoặc kéo thả file `.xlsx` để kiểm tra định dạng, component bắt buộc, tổng tiền, bằng chứng, free tier/trial, HA và staging. Validator không đọc được nội dung ảnh; giám khảo vẫn kiểm tra thủ công từng bằng chứng.

## Lịch thực hiện trong buổi học

- 00:00–00:15: mở đề và hỏi đáp.
- 00:15–00:25: chia nhóm, phân vai.
- 00:25–01:15: sizing.
- 01:25–02:35: kiến trúc và báo giá.
- 02:35–03:05: tối ưu, đóng gói, chạy validator.
- 03:05: hạn nộp.
- 03:10 trở đi: bảo vệ; mỗi nhóm 7 phút trình bày + 3 phút hỏi đáp.
