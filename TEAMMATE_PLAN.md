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
| **Trần Nguyễn Trí Dũng** (`bananayass`) | Kiến trúc sư trưởng | `ops_labor`, `licenses`, `contingency`, dòng `TOTAL` | Giả định tổng, sơ đồ/luồng đầu cuối, ghép slide, ghép báo giá, tối ưu chi phí, điều phối bảo vệ |
| **Kiệt** (`kayendev`) | Model serving | `llm`, `embedding`, `gateway` | Model theo 5 cấp tác vụ, routing, sizing token/GPU/API, so sánh API–tự host–hybrid, chất lượng và giá inference |
| **Phong** (`phong123-ai`) | Data và workspace | `connectors`, `database`, `vector_db`, `object_storage`, `cache_queue` | Kết nối SaaS, RAG lọc theo quyền, workspace riêng, storage, queue agent và giá dữ liệu |
| **Trường Bảo** (`zewolkt3939`) | Vai gộp: sandbox, bảo mật, governance **và** cloud, HA, vận hành | `sandbox`, `authn`, `authz`, `secrets_kms`, `governance`, `compute`, `load_balancer`, `network`, `backup_dr`, `monitoring`, `cicd` | Cloud/region, sandbox, SSO/OAuth, guardrail/DLP/audit, HA/DR, staging, monitoring và giá vận hành |

Theo đề, nhóm 4 người gộp hai vai cuối. Bảo chốt tính đúng của các component thuộc vai gộp; ba người còn lại hỗ trợ chuẩn bị số liệu và bằng chứng theo bảng dưới đây để các phần có thể làm song song.

| Người hỗ trợ | Việc hỗ trợ Bảo | Bảo chốt |
| --- | --- | --- |
| Dũng | Ước lượng số node/giờ chạy, phác sơ đồ HA và tìm giá `compute`, `load_balancer`, `network`, `backup_dr`, `monitoring`, `cicd` | Topology, khả năng đáp ứng H1/H7 và số tiền từng dòng |
| Kiệt | Tính lượt sandbox từ cơ cấu tác vụ cấp 3–4; đề xuất CPU/RAM/thời gian mỗi lượt và tìm giá `sandbox` | Công nghệ cô lập, cấm egress mặc định, chi phí và cách ngăn thoát sandbox |
| Phong | Mô tả ACL gốc của tài liệu, OAuth ủy nhiệm, tenant/user isolation và dữ liệu cần audit cho `authz`, `secrets_kms`, `governance` | Chính sách quyền, token vault, DLP/audit và tính nhất quán với H2–H5 |

## Công việc chi tiết theo người

### Dũng — tích hợp và bảo vệ

- Mở bảng giả định chung: **2.000 DAU**, 22 ngày làm việc/tháng, 08:00–18:00 GMT+7, prod + 1 staging; chỉ dùng một bộ giả định cho slide và XLSX.
- Cùng Kiệt và Phong chốt request/người/ngày, phân bổ 5 cấp tác vụ, token input/output, peak RPS, token/s, phiên đồng thời, số lượt sandbox, dung lượng và egress. Ghi công thức và lý do chọn số.
- Chọn cùng Bảo một cloud chính/region. Tổng hợp các hộp kiến trúc với mã component và vẽ luồng từ SSO → LB → gateway → model/connector/sandbox → dữ liệu → trả kết quả.
- Ghi các dòng `ops_labor`; chỉ dùng `licenses`, `contingency` nếu có chi phí thực tế/giả định được giải thích. Tổng hợp `TOTAL`, tính USD/DAU = `TOTAL / 2.000`, top 5 khoản chi và giá trị USD của từng đòn bẩy tiết kiệm.
- Soát phương án khi 4.000 DAU, trường hợp giá token thay đổi và rủi ro lớn nhất. Ghép deck và điều phối diễn tập 7 phút + 3 phút hỏi đáp.

### Kiệt — AI và model serving

- Chọn model cho từng cấp: email/hỏi đáp; tài liệu/slide; dữ liệu/code; agent dự án; mockup/sơ đồ/hình minh họa. Nêu model tham chiếu và bộ eval để đạt **ít nhất 95% điểm tham chiếu** cho từng cấp.
- Tính token vào/ra theo cấp, kể cả RAG và các bước agent; tính tải giờ cao điểm, giá API hoặc GPU tự host, embedding/rerank và sinh ảnh nếu cần.
- So sánh ít nhất hai hướng lớn (API, tự host, hybrid) bằng USD/tháng, hiệu năng, rủi ro và điểm hòa vốn. Chốt routing model nhỏ/lớn, cache, fallback, quota theo người/đơn vị và budget alert.
- Giải thích khả năng đạt p95 time-to-first-token ≤ 3 giây cho chat/email/tài liệu lúc cao điểm; agent dự án chạy nền và xong trong 10 phút.
- Bàn giao sơ đồ model/gateway, bảng tính token, các dòng `llm`, `embedding` (nếu dùng), `gateway` và bằng chứng giá. Nếu embedding nằm trong khoản khác, ghi rõ quan hệ để tránh tính hai lần.

### Phong — dữ liệu, connector và workspace

- Chốt chiến lược truy cập Google Workspace/Gmail/Drive/Calendar/Docs/Sheets/Slides, Outlook/Microsoft 365/OneDrive/SharePoint/Teams, Notion, Jira, Confluence: gọi trực tiếp hay đồng bộ, tần suất, rate limit và số API call.
- Thiết kế index tài liệu, vector DB và bước lọc ACL theo quyền gốc **trước khi trả kết quả RAG**; không để agent của người này truy cập file người khác.
- Chọn database cho chat/history/metadata; object storage cho file tải lên, file agent tạo và bộ nhớ dài hạn; quota **10 GB/người**; retention và lifecycle. Ước lượng GB, số vector, request đọc/ghi và chi phí.
- Thiết kế cache/queue cho agent nền, retry, timeout, trạng thái và thông báo hoàn thành. Cùng Bảo xác định chỗ lưu OAuth token và log/audit để không tính thiếu.
- Bàn giao data flow và các dòng `connectors`, `database`, `vector_db`, `object_storage`, `cache_queue` cùng bằng chứng giá.

### Bảo — cloud, bảo mật, sandbox và vận hành

- Chọn cloud chính và region, topology prod nhiều AZ và 1 staging; tính `compute`, `load_balancer`, `network` gồm VPC, NAT, egress, WAF và private endpoint/kênh cam kết không lưu dữ liệu đến model API.
- Thiết kế sandbox container/microVM: workspace mount đúng user, giới hạn CPU/RAM/thời gian, chặn metadata, **mặc định không egress**, hủy sau chạy; tính số phiên đồng thời và giá theo dữ liệu Kiệt cung cấp.
- Thiết kế SSO OIDC/SAML + MFA, RBAC/ABAC, ACL tài liệu theo quyền gốc, OAuth ủy nhiệm scope tối thiểu và token vault/KMS có mã hóa.
- Chốt guardrail đầu vào/ra, chống prompt injection từ nội dung connector, người dùng duyệt trước hành động gửi email/tạo ticket/xóa file, DLP/PII, phân loại dữ liệu, retention, audit log 12 tháng và eval gate khi đổi model/prompt.
- Thiết kế HA không có điểm lỗi đơn ở LB/gateway/database; backup có diễn tập khôi phục; availability **99,5% giờ hành chính**, **RTO 4 giờ**, **RPO 1 giờ**.
- Tính monitoring/log/metric/trace/LLM observability, cảnh báo SLO/chi phí, CI/CD, registry, IaC và staging. Bàn giao sơ đồ security/network/HA, ma trận H1–H7, các dòng component được giao và bằng chứng giá.

## Cách ghép sản phẩm

### Báo giá XLSX

Mỗi người tạo dòng cho component mình sở hữu và gửi Dũng theo đúng 5 cột của `BaoGia`. Một component có thể có nhiều dòng, nhưng mã component phải giữ nguyên như bảng trên. Ghi chú mỗi dòng có dịch vụ, SKU, region, **đơn giá × số lượng**, giờ chạy (730 giờ/tháng nếu 24/7; 220 giờ nếu chỉ giờ hành chính), HA/staging và giả định tính. Dùng USD/tháng chưa VAT và giá niêm yết chính thức; cam kết reserved/savings/committed use phải ghi rõ cách quy đổi. Không dùng free tier, trial, credit hay giá đàm phán riêng.

Mỗi dòng có URL hợp lệ hoặc mã ảnh `E01`… trong `BangChung`; ảnh phải cho thấy dịch vụ, SKU, region, đơn giá. Riêng `ops_labor` và `contingency` có thể ghi `NA`. Khoản 0 USD phải ghi rõ **nằm trong** dòng nào và vẫn có bằng chứng khi cần. Dũng cộng tổng, đặt `TOTAL` ở dòng cuối, chạy validator trong HTML đến khi báo **ĐẠT**; cả nhóm tự đối chiếu ảnh vì validator không đọc nội dung ảnh.

### Slide và bảo vệ

| Cụm slide đề xuất | Người chuẩn bị nội dung | Người chốt bản cuối |
| --- | --- | --- |
| Mục tiêu, giả định và sizing; kiến trúc tổng; luồng request | Dũng, nhận số từ cả nhóm | Dũng |
| Model theo 5 cấp, routing, so sánh phương án và eval chất lượng | Kiệt | Dũng |
| Connectors, ACL, workspace, database/index và agent queue | Phong | Dũng |
| Cloud/network, sandbox, SSO, governance, HA/backup/DR, monitoring | Bảo, nhận hỗ trợ theo bảng trên | Dũng |
| Chi phí, USD/DAU, top 5 khoản, tiết kiệm, rủi ro 4.000 DAU | Dũng, nhận giá từ cả nhóm | Dũng |

Không cần một slide cho mỗi dòng bảng; ghép các ý để giữ tối đa 15 slide nội dung. Mỗi hộp trên sơ đồ gắn mã component tương ứng với `BaoGia`. Tổng USD/tháng trên slide phải đúng bằng `TOTAL` XLSX.

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

## Cổng hoàn thành trước khi nộp

- [ ] Đủ **19 component bắt buộc** trong sơ đồ và `BaoGia`; các component tùy chọn chỉ xuất hiện khi phù hợp.
- [ ] Giả định sizing từ 2.000 DAU có công thức và nhất quán trong slide, báo giá và câu trả lời bảo vệ.
- [ ] H1–H8 có cách chứng minh cụ thể: cloud, quyền, sandbox, AI/data governance, độ trễ, HA/DR, chất lượng và ngân sách.
- [ ] Báo giá có bằng chứng cho từng dòng, không tính thiếu egress/staging/backup/log/nhân sự; validator báo **ĐẠT**.
- [ ] `TOTAL` XLSX bằng tổng trên slide; USD/DAU = `TOTAL / 2.000`.
- [ ] Slide đúng định dạng/giới hạn, tên file đúng mã nhóm, nộp trước hạn và cả bốn người sẵn sàng hỏi đáp.
