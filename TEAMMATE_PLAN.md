# Kế hoạch nhóm Eviaura — VBot Production Capstone

Nguồn yêu cầu: [vbot-capstone.html](./vbot-capstone.html). Thành viên và GitHub username: [TEAMMATES.md](./TEAMMATES.md). Kế hoạch này dành cho **bài thiết kế kiến trúc và báo giá**, với hai file nộp là slide và XLSX; đề không yêu cầu triển khai VBot thành phần mềm chạy thật.

## Kết quả chung cần hoàn thành

1. **Slide hệ thống** (`Gxx_slide.pdf` hoặc `.pptx`): tối đa 15 slide nội dung, 16:9, tối đa 10 MB; trình bày 7 phút. Có sizing từ 2.000 DAU, sơ đồ đủ component, luồng request, lựa chọn model/công nghệ, phân quyền, sandbox, governance, HA/DR, chi phí và rủi ro khi DAU tăng gấp đôi.
2. **Báo giá** (`Gxx_baogia.xlsx`): sheet `BaoGia` đúng 5 cột `Component`, `Ý nghĩa`, `Ghi chú`, `Chi phí/tháng (USD)`, `Bằng chứng`; sheet `BangChung` nếu dùng ảnh mã `E01`… Dòng `TOTAL` ở cuối và khớp số trên slide. Mỗi dòng giá có nguồn chính thức hoặc ảnh/calculator kiểm chứng được.
3. **Bảo vệ**: cả bốn người giải thích được giả định tải, lựa chọn kiến trúc, cách cô lập dữ liệu, nguồn giá và tám ràng buộc H1–H8.

Thay `xx` bằng mã nhóm được giao; không tự mặc định mã nhóm là `03`.

## Phân vai và component sở hữu

| Người | Vai theo đề | Component chịu trách nhiệm cuối | Phần việc phải bàn giao |
| --- | --- | --- | --- |
| **Trần Nguyễn Trí Dũng** (`2A202602784`, `@bananayass`) | Kiến trúc sư trưởng | `ops_labor`, `licenses`, `contingency`, dòng `TOTAL` | Giả định tổng, sơ đồ/luồng đầu cuối, ghép slide, ghép báo giá, tối ưu chi phí, điều phối bảo vệ |
| **Hồ Đình Tuấn Kiệt** (`2A202602785`, `@Kayen-dev`) | Model serving | `llm`, `embedding`, `gateway` | Model theo 5 cấp tác vụ, routing, sizing token/GPU/API, so sánh API–tự host–hybrid, chất lượng và giá inference |
| **Nguyễn Duy Phong** (`2A202602834`, `@DuyPhong123-ai`) | Data và workspace | `connectors`, `database`, `vector_db`, `object_storage`, `cache_queue` | Kết nối SaaS, RAG lọc theo quyền, workspace riêng, storage, queue agent và giá dữ liệu |
| **Nguyễn Trường Bảo** (`2A202602540`, `@zewolkt3939`) | Vai gộp: sandbox, bảo mật, governance **và** cloud, HA, vận hành | `sandbox`, `authn`, `authz`, `secrets_kms`, `governance`, `compute`, `load_balancer`, `network`, `backup_dr`, `monitoring`, `cicd` | Cloud/region, sandbox, SSO/OAuth, guardrail/DLP/audit, HA/DR, staging, monitoring và giá vận hành |

Theo đề, nhóm 4 người gộp hai vai cuối. Bảo chốt tính đúng của các component thuộc vai gộp; ba người còn lại hỗ trợ chuẩn bị số liệu và bằng chứng theo bảng dưới đây để các phần có thể làm song song.

| Người hỗ trợ | Việc hỗ trợ Bảo | Bảo chốt |
| --- | --- | --- |
| Dũng | Ước lượng số node/giờ chạy, phác sơ đồ HA và tìm giá `compute`, `load_balancer`, `network`, `backup_dr`, `monitoring`, `cicd` | Topology, khả năng đáp ứng H1/H7 và số tiền từng dòng |
| Kiệt | Tính lượt sandbox từ cơ cấu tác vụ cấp 3–4; đề xuất CPU/RAM/thời gian mỗi lượt và tìm giá `sandbox` | Công nghệ cô lập, cấm egress mặc định, chi phí và cách ngăn thoát sandbox |
| Phong | Mô tả ACL gốc của tài liệu, OAuth ủy nhiệm, tenant/user isolation và dữ liệu cần audit cho `authz`, `secrets_kms`, `governance` | Chính sách quyền, token vault, DLP/audit và tính nhất quán với H2–H5 |

## Công việc chi tiết theo người

Mỗi dòng dưới đây là một checkpoint riêng. Người phụ trách chỉ đánh dấu xong khi **đầu ra kiểm tra** đã có trong bảng sizing, sơ đồ, slide hoặc XLSX chung và người nhận bàn giao đã xem được. Giờ là thời gian tính từ lúc bắt đầu buổi học.

### Dũng — tích hợp và bảo vệ

| Checkpoint | Đầu việc | Đầu ra kiểm tra được và điều kiện chuyển bước |
| --- | --- | --- |
| **D1 · 00:25** | Mở một bảng giả định chung cho 2.000 DAU, 22 ngày/tháng, 08:00–18:00 GMT+7, prod + staging; ghi ai nhập mỗi nhóm số liệu. | Bảng có nguồn số cố định của đề, ô trống cho số nhóm tự chọn và công thức; Kiệt, Phong, Bảo dùng cùng bảng. |
| **D2 · 01:15** | Chốt cùng Kiệt/Phong request/người/ngày, tỉ lệ 5 cấp, token input/output, peak RPS/token/s/phiên, lượt sandbox, dung lượng và egress. | Slide sizing nháp và bảng giả định có công thức, đơn vị, căn cứ và số khớp nhau; Kiệt, Phong, Bảo xác nhận đầu vào dùng cho phần mình. |
| **D3 · 02:00** | Chốt cloud/region với Bảo; ghép sơ đồ tổng và luồng SSO → LB → gateway → model/connector/sandbox → dữ liệu → trả kết quả. | Sơ đồ gắn mã của đủ **19 component bắt buộc**; từng hộp có chủ sở hữu và một dòng báo giá dự kiến. Bảo kiểm tra cloud, HA và ranh giới bảo mật. |
| **D4 · 02:35** | Ghi `ops_labor` và, nếu áp dụng, `licenses`, `contingency`; gom dòng giá của cả nhóm. | XLSX nháp có đúng 5 cột, bằng chứng của các dòng, `TOTAL` là dòng cuối; các khoản tùy chọn có lý do và không bị tính trùng. |
| **D5 · 02:50** | Tính `TOTAL / 2.000`, top 5 khoản, tiết kiệm USD, chi phí khi 4.000 DAU và kịch bản giá token đổi; ghép slide cuối. | Slide chi phí bằng `TOTAL` trong XLSX, có rủi ro và phương án mở rộng; deck 16:9, tối đa 15 slide nội dung, tối đa 10 MB. |
| **D6 · 03:00** | Chạy validator, kiểm H1–H8 với cả nhóm, rà ảnh giá và diễn tập. | Validator báo **ĐẠT**, không còn dòng mẫu/free tier, ảnh giá được người sở hữu xác nhận; bốn người trả lời được câu hỏi ngoài mảng mình. |
| **D7 · 03:05 và bảo vệ** | Xuất hai file đúng mã nhóm, nộp Google Form, giữ bản cuối và dẫn bảo vệ. | Có xác nhận nộp hai file trước hạn; trình bày 7 phút và hỏi đáp 3 phút, tổng trên lời trình bày khớp file đã nộp. |

### Kiệt — AI và model serving

| Checkpoint | Đầu việc | Đầu ra kiểm tra được và điều kiện chuyển bước |
| --- | --- | --- |
| **K1 · 01:00** | Chọn model cho đủ 5 cấp tác vụ và model tham chiếu; định nghĩa tập eval/chấm điểm. | Bảng 5 hàng: tác vụ, model phục vụ, model tham chiếu, phép đo và ngưỡng ≥ 95%; Dũng đưa vào slide chất lượng. |
| **K2 · 01:15** | Tính input/output token, context RAG, bước agent, ảnh sinh ra, peak token/s; chốt với Dũng hướng API/tự host/hybrid. | Bảng công thức từ 2.000 DAU đến token/tháng và tải peak; Bảo nhận số lượt sandbox, Dũng nhận tổng tải model. |
| **K3 · 02:00** | So sánh ít nhất hai phương án bằng USD/tháng, năng lực, điểm hòa vốn và rủi ro; thiết kế routing/cache/fallback. | Bảng so sánh có kết luận, giả định cache/model nhỏ và số USD tiết kiệm; sơ đồ `gateway` khớp kiến trúc tổng. |
| **K4 · 02:20** | Chứng minh mục tiêu p95 token đầu ≤ 3 giây và agent nền ≤ 10 phút; chốt quota, cảnh báo và cách cắt ngân sách. | Bảng ngân sách độ trễ theo từng chặng và kế hoạch đo p95 giờ cao điểm; Bảo đối chiếu năng lực hạ tầng, Dũng đối chiếu H6/H8. |
| **K5 · 02:35** | Bàn giao giá `llm`, `gateway`, `embedding` hoặc giải thích embedding đã bao gồm; ảnh/model tạo hình nếu có. | Dòng báo giá đủ SKU, region/điều khoản, lượng × đơn giá, USD/tháng và bằng chứng; slide model/routing đã gửi Dũng. |
| **K6 · 03:00** | Rà giá và dữ liệu model trên deck/XLSX, chuẩn bị hỏi đáp. | Giá/tải trong slide bằng giá/tải ở XLSX; Kiệt trả lời được điểm hòa vốn, chất lượng 95%, p95 và ngân sách. |

### Phong — dữ liệu, connector và workspace

| Checkpoint | Đầu việc | Đầu ra kiểm tra được và điều kiện chuyển bước |
| --- | --- | --- |
| **P1 · 01:00** | Liệt kê Google Workspace, Microsoft 365/Outlook, Notion, Jira, Confluence; chọn gọi trực tiếp hoặc đồng bộ, tần suất và rate limit. | Ma trận connector gồm quyền OAuth, loại dữ liệu, số API call/tháng và độ tươi; Dũng/Bảo nhận đầu vào egress và network. |
| **P2 · 01:15** | Ước lượng GB tài liệu, số vector, chat/history, lượt đọc ghi, workspace riêng quota 10 GB/người. | Bảng sizing có công thức theo 2.000 DAU, retention và giả định dùng quota thực tế; Dũng đưa vào slide, Bảo dùng cho backup. |
| **P3 · 02:00** | Thiết kế ingest/index và truy vấn RAG lọc ACL quyền gốc; cô lập workspace/bộ nhớ của từng user. | Data flow và ví dụ người A không xem được tài liệu người B ở connector, index, workspace, sandbox; Bảo xác nhận `authz`/token vault. |
| **P4 · 02:20** | Chốt database, vector DB, object storage, cache/queue, retry/timeout và thông báo agent. | Sơ đồ lưu trữ và hàng đợi có lý do HA, vòng đời dữ liệu, điểm lưu token/audit; Bảo xác nhận RPO/RTO và audit 12 tháng. |
| **P5 · 02:35** | Bàn giao giá 5 component mình sở hữu và nội dung slide data. | Mỗi dòng có SKU, region, quy mô × đơn giá và bằng chứng; Dũng ghép XLSX/deck không phải tự ước đoán lại. |
| **P6 · 03:00** | Rà đối chiếu ACL, quota, chi phí và chuẩn bị hỏi đáp. | Phong giải thích được cách giữ quyền gốc, cô lập user, độ tươi index và hàng đợi agent trong bản nộp cuối. |

### Bảo — cloud, bảo mật, sandbox và vận hành

| Checkpoint | Đầu việc | Đầu ra kiểm tra được và điều kiện chuyển bước |
| --- | --- | --- |
| **B1 · 01:00** | Chọn một cloud/region, topology prod nhiều AZ + staging; quyết định kênh gọi model API. | Sơ đồ cloud/network đầu tiên có vùng, WAF/LB, gateway, private endpoint hoặc cam kết không lưu dữ liệu; Dũng chốt đưa vào kiến trúc tổng. |
| **B2 · 01:15** | Chọn sandbox container/microVM và chính sách cô lập; nhận sizing phiên chạy từ Kiệt. | Bảng CPU/RAM/thời gian/phiên, số phiên peak, mặc định chặn egress và metadata, mount đúng workspace, hủy sau chạy; Dũng nhận giả định chi phí. |
| **B3 · 02:00** | Thiết kế SSO OIDC/SAML + MFA, RBAC/ABAC, ACL, OAuth ủy nhiệm scope tối thiểu và token vault/KMS. | Sơ đồ luồng đăng nhập/truy cập tài liệu/token; Phong xác nhận không lộ dữ liệu giữa user và không dùng service account đọc toàn tập đoàn. |
| **B4 · 02:10** | Chốt guardrail input/output, chặn prompt injection, duyệt hành động ghi, DLP/PII, retention, audit 12 tháng và eval gate. | Ma trận H4/H5: biện pháp, vị trí trên sơ đồ, dữ liệu/log lưu ở đâu, khoản chi phí tương ứng; Kiệt xác nhận eval gate. |
| **B5 · 02:20** | Chốt HA LB/gateway/database, backup và diễn tập restore; kiểm availability 99,5%, RTO 4h, RPO 1h. | Sơ đồ failover, tần suất backup, nơi lưu, mục tiêu phục hồi và chi phí; Dũng/Phong kiểm các replica/backup đã được tính. |
| **B6 · 02:35** | Chốt compute, LB, network/egress, sandbox, authn/authz, vault, governance, backup/DR, monitoring, CI/CD và staging. | Đủ **11 component Bảo sở hữu** trong sơ đồ và XLSX, mỗi dòng có cách tính/bằng chứng; ma trận H1–H7 chỉ đến slide và dòng báo giá liên quan. |
| **B7 · 02:50** | Soát log/metric/trace, cảnh báo SLO, LLM observability, quota/chi phí và kịch bản AZ mất điện. | Slide vận hành cho biết đo gì, ai được cảnh báo, failover ra sao; Dũng kiểm H7/H8 và kịch bản bảo vệ. |
| **B8 · 03:00** | Rà từng bằng chứng giá và trả lời chất vấn an toàn/HA. | Bảo xác nhận SKU/region/đơn giá của các dòng mình sở hữu, sandbox không egress, token mã hóa, kiểm thử khôi phục và 12 tháng audit. |

## Cách ghép sản phẩm

### Ai làm Excel (`Gxx_baogia.xlsx`)

**Dũng tạo và giữ file XLSX chính.** Mỗi người nhập trực tiếp phần mình vào `BaoGia` và `BangChung` nếu nhóm dùng bảng tính chung; nếu làm trên bản riêng, gửi các dòng và ảnh để Dũng ghép trước 02:35. Chỉ Dũng khóa bản cuối để tránh hai file khác nhau cùng được coi là bản nộp.

| Người làm Excel | Dòng `BaoGia` phải nhập | Phần `BangChung` / bằng chứng | Checkpoint |
| --- | --- | --- | --- |
| **Dũng** | `ops_labor`; `licenses`, `contingency` khi áp dụng; dòng cuối `TOTAL` | Bằng chứng giá cho `licenses` nếu có; `ops_labor`/`contingency` có thể ghi `NA`; nhận và đối chiếu ảnh của cả nhóm | D4: 02:35 có XLSX đủ dòng và tổng; D6: 03:00 validator **ĐẠT** |
| **Kiệt** | `llm`, `gateway`, `embedding` nếu tính riêng | URL/ảnh giá model, token, GPU, embedding và gateway tương ứng từng dòng; ghi rõ nếu embedding đã nằm trong dòng khác | K5: 02:35 bàn giao dòng và nguồn giá; K6: 03:00 xác nhận lại số |
| **Phong** | `connectors`, `database`, `vector_db`, `object_storage`, `cache_queue` | URL/ảnh SKU, region, dung lượng, số request và đơn giá dịch vụ data/SaaS tương ứng | P5: 02:35 bàn giao dòng và nguồn giá; P6: 03:00 xác nhận lại số |
| **Bảo** | `sandbox`, `authn`, `authz`, `secrets_kms`, `governance`, `compute`, `load_balancer`, `network`, `backup_dr`, `monitoring`, `cicd` | URL/ảnh cloud calculator/SKU và giá của các dịch vụ bảo mật, mạng, HA, vận hành; Dũng/Kiệt/Phong hỗ trợ tìm theo bảng phân vai | B6: 02:35 bàn giao đủ 11 component; B8: 03:00 xác nhận lại bằng chứng |

Sheet `BaoGia` phải đúng 5 cột `Component`, `Ý nghĩa`, `Ghi chú`, `Chi phí/tháng (USD)`, `Bằng chứng`. Một component có thể có nhiều dòng; ghi chú đủ dịch vụ, SKU, region, **đơn giá × số lượng**, giờ chạy (730 giờ/tháng nếu 24/7; 220 giờ nếu chỉ giờ hành chính), HA/staging và giả định tính. Dùng USD/tháng chưa VAT và giá niêm yết chính thức; cam kết reserved/savings/committed use phải ghi rõ cách quy đổi. Không dùng free tier, trial, credit hay giá đàm phán riêng.

Mỗi dòng cần URL hợp lệ hoặc mã ảnh `E01`… trong `BangChung`; ảnh phải cho thấy dịch vụ, SKU, region, đơn giá. Riêng `ops_labor` và `contingency` có thể ghi `NA`. Khoản 0 USD phải ghi rõ **nằm trong** dòng nào và vẫn có bằng chứng khi cần. Dũng cộng tổng, đặt `TOTAL` ở dòng cuối, chạy validator trong HTML đến khi báo **ĐẠT**; cả nhóm tự đối chiếu ảnh vì validator không đọc nội dung ảnh.

### Ai làm slide (`Gxx_slide.pdf` hoặc `.pptx`)

**Dũng tạo và giữ deck chính.** Kiệt, Phong và Bảo làm các slide của mình trong deck chung hoặc gửi nội dung/ảnh sơ đồ có thể chỉnh sửa để Dũng ghép. Số trang dưới đây là khung 12 slide nội dung; có thể ghép trang nếu trình bày quá 7 phút, nhưng phải giữ đủ nội dung yêu cầu.

| Slide dự kiến | Người làm slide | Nội dung phải có | Checkpoint |
| --- | --- | --- | --- |
| **1–3** | **Dũng** | Mục tiêu + giả định/sizing có công thức; kiến trúc tổng đủ mã component; luồng một request qua SSO, LB, gateway, model, connector, sandbox và dữ liệu | D2: 01:15 có sizing; D3: 02:00 có sơ đồ |
| **4–5** | **Kiệt** | Model/routing theo 5 cấp, model tham chiếu và eval ≥95%; so sánh API/tự host/hybrid có số liệu, p95 ≤3 giây, agent ≤10 phút và cách kiểm ngân sách | K3–K4: 02:20 có bản nháp; K5: 02:35 gửi Dũng |
| **6–7** | **Phong** | Connectors, OAuth/ACL gốc; RAG lọc quyền, workspace riêng, quota 10 GB/user, database, vector, object storage và queue agent | P3–P4: 02:20 có sơ đồ; P5: 02:35 gửi Dũng |
| **8–10** | **Bảo** | Cloud/region/network và sandbox; SSO/MFA, token vault, guardrail/DLP/audit/eval gate; HA/backup/DR, monitoring, staging và FinOps | B3–B5: 02:20 có sơ đồ; B6: 02:35 gửi Dũng |
| **11–12** | **Dũng** | `TOTAL` USD/tháng và USD/DAU, top 5 khoản, đòn bẩy tiết kiệm có USD; rủi ro và chi phí/kịch bản khi 4.000 DAU | D5: 02:50 khóa slide; D6: 03:00 cả nhóm duyệt |

Mỗi người **tự viết nội dung và sơ đồ cho slide được giao**, kiểm số liệu với dòng Excel mình nhập và duyệt lại bản deck cuối. Dũng thống nhất bố cục 16:9, ghép/chỉnh deck, kiểm tối đa 15 slide nội dung và 10 MB, xuất PDF/PPTX để nộp. Mỗi hộp trên sơ đồ gắn mã component tương ứng với `BaoGia`; tổng USD/tháng trên slide phải đúng bằng `TOTAL` XLSX.

## Lịch thực hiện và điểm bàn giao

Các mốc là **thời gian tương đối của buổi học**, theo đề; giảng viên có thể điều chỉnh giờ thực tế.

| Mốc | Việc phải xong | Người chốt |
| --- | --- | --- |
| 00:15–00:25 | Chốt 4 vai, nơi lưu file chung, một người giữ bản `BaoGia` chính | Dũng |
| 00:25–01:15 | Sizing có công thức; chốt hướng LLM, cloud/region và sandbox | Dũng + Kiệt + Bảo, Phong xác nhận tải dữ liệu |
| 01:15 | Checkpoint: mọi người dùng chung một bộ giả định và có phần việc/bằng chứng cần tìm | Cả nhóm |
| 01:25–02:35 | Hoàn thành sơ đồ đủ component, dòng giá và bằng chứng; ghép bản nháp slide/XLSX | Mỗi người với phần mình; Dũng ghép |
| 02:35–03:05 | Soát H1–H8, tối ưu chi phí, kiểm tổng, chạy validator đến ĐẠT, xuất slide và diễn tập ngắn | Cả nhóm; Dũng chốt file |
| 03:05 | Nộp hai file đúng tên qua Google Form | Dũng |
| 03:10 trở đi | Bảo vệ: 7 phút trình bày, 3 phút hỏi đáp; mỗi người nắm phần mình và hiểu luồng tổng | Cả nhóm |

## Luồng hoàn thành từ đầu đến cuối

| Cổng | Đầu vào phải có | Cách kiểm và người nhận bàn giao | Nếu chưa đạt |
| --- | --- | --- | --- |
| **G1 · Khóa giả định (01:15)** | D1–D2, K1–K2, P1–P2, B1–B2 | Dũng đối chiếu số 2.000 DAU → request → token/sandbox/storage/egress; Kiệt, Phong, Bảo xác nhận số đầu vào của mình. | Ghi rõ ô sai và người sửa; không dùng hai bộ số khác nhau để tính giá. |
| **G2 · Khóa kiến trúc (02:00)** | D3, K3, P3, B3–B4 | Dũng rà từng mã component trên sơ đồ với danh sách 19 mã bắt buộc; Bảo kiểm ranh giới quyền, network và sandbox. | Chủ component thêm hộp/luồng thiếu và sửa sizing trước khi chốt SKU. |
| **G3 · Khóa sizing và giá (02:35)** | D4, K4–K5, P4–P5, B5–B6 | Dũng cộng các dòng và kiểm `TOTAL`; chủ từng dòng đọc lại SKU, region, đơn giá, số lượng, HA/staging và bằng chứng. | Trả đúng dòng cho chủ sửa; không chèn số ước đoán không có căn cứ vào XLSX. |
| **G4 · Khóa slide (02:50)** | D5, K6 bản nháp, P6 bản nháp, B7 | Dũng kiểm 12 cụm nội dung đề gợi ý, H1–H8, tổng USD/tháng và USD/DAU; Kiệt/Phong/Bảo duyệt phần của mình. | Sửa slide hoặc XLSX và tính lại `TOTAL` nếu thay đổi kiến trúc/giá. |
| **G5 · Sẵn sàng nộp (03:00)** | D6, K6, P6, B8 | Validator XLSX báo **ĐẠT**; ảnh giá được kiểm tay; deck đúng 16:9/≤15 slide nội dung/≤10 MB; tên hai file đúng mã nhóm. | Sửa lỗi validator và kiểm lại cả slide lẫn tổng trước khi nộp. |
| **G6 · Nộp và bảo vệ (03:05 → hết hỏi đáp)** | D7, hai file đã khóa, bản ghi giả định/nguồn giá | Dũng xác nhận form đã nhận hai file; cả nhóm trình bày 7 phút, trả lời 3 phút và dùng đúng số của bản nộp. | Nếu form/định dạng báo lỗi trước hạn, sửa và nộp lại; sau hạn báo trung thực trạng thái cho giảng viên. |

Một thay đổi sau G1 phải được cập nhật qua chuỗi **bảng giả định → sizing từng mảng → XLSX → `TOTAL` → slide**. Chủ dòng báo giá xác nhận lại bằng chứng khi SKU hoặc region thay đổi. Dũng là người khóa bản cuối; mỗi thành viên chịu trách nhiệm phần mình vẫn đúng trong bản đã nộp.

### Bản đồ H1–H8 để không sót yêu cầu

| Yêu cầu | Người chốt | Checkpoint chứng minh |
| --- | --- | --- |
| H1 · Một cloud chính, region, kênh model API an toàn | Bảo | B1, B6; D3 ghép sơ đồ |
| H2 · SSO/MFA, RBAC/ABAC, ACL, OAuth/token vault | Bảo; Phong kiểm ACL gốc | B3, P3, B6 |
| H3 · Workspace riêng, sandbox cô lập và chặn egress | Bảo; Phong kiểm workspace | B2, P3, B6 |
| H4 · Guardrail, prompt injection, người dùng xác nhận, eval gate | Bảo; Kiệt kiểm eval | B4, K1, B6 |
| H5 · Mã hóa, DLP, retention, audit 12 tháng, không huấn luyện trên dữ liệu | Bảo; Phong kiểm lưu trữ | B4, P4, B6 |
| H6 · p95 token đầu ≤ 3 giây, agent ≤ 10 phút có thông báo | Kiệt; Phong kiểm queue; Bảo kiểm tải hạ tầng | K4, P4, B6 |
| H7 · 99,5% giờ hành chính, HA, backup/restore, RTO 4h/RPO 1h | Bảo; Dũng kiểm giá | B5–B6, D4 |
| H8 · ≥95% chất lượng tham chiếu mỗi cấp, quota và ngân sách | Kiệt; Dũng chốt chi phí | K1, K3–K4, D5 |

## Cổng hoàn thành trước khi nộp

- [ ] Đủ **19 component bắt buộc** trong sơ đồ và `BaoGia`; các component tùy chọn chỉ xuất hiện khi phù hợp.
- [ ] Giả định sizing từ 2.000 DAU có công thức và nhất quán trong slide, báo giá và câu trả lời bảo vệ.
- [ ] H1–H8 có cách chứng minh cụ thể: cloud, quyền, sandbox, AI/data governance, độ trễ, HA/DR, chất lượng và ngân sách.
- [ ] Báo giá có bằng chứng cho từng dòng, không tính thiếu egress/staging/backup/log/nhân sự; validator báo **ĐẠT**.
- [ ] `TOTAL` XLSX bằng tổng trên slide; USD/DAU = `TOTAL / 2.000`.
- [ ] Slide đúng định dạng/giới hạn, tên file đúng mã nhóm, nộp trước hạn và cả bốn người sẵn sàng hỏi đáp.
