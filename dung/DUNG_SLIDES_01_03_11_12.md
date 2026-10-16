# Nội dung slide Dũng — 1–3, 11–12

**Bố cục:** 16:9, nền sáng, chữ tối, xanh đậm cho kiến trúc, cam cho số tải và rủi ro. Một thông điệp chính/slide, sơ đồ dùng cùng mã component trong `BaoGia`. Đây là nội dung chỉnh sửa được để ghép deck; các ô `CHỜ` không được đưa nguyên vào bản nộp.

## Slide 1 — 2.000 DAU thành tải thực

**Headline:** 440.000 request/tháng; thiết kế cho peak 2,22 request/s.

- `2.000 DAU × 22 ngày × 10 request/người/ngày = 440.000 request/tháng`.
- Tỷ lệ 5 cấp: **50% / 25% / 12% / 8% / 5%**.
- Token text: **1.055,56M input + 301,84M output/tháng**. Peak thiết kế 4×: **5.331 input + 1.524 output token/s**.
- Sandbox: **59.840 run/tháng**, khoảng **18,1 phiên đồng thời** nếu mỗi run 60 giây. Workspace quota **10 GB/user**, trần 20 TB; lưu trữ thực dùng chờ Phong.
- Phiên tương tác peak **67** nếu mỗi request giữ kết nối 30 giây. Cấp 5 có **22.000 request SVG/HTML**, baseline **0 bitmap**; ngoại lệ bitmap nếu được duyệt là 4.400 ảnh/tháng.
- Dữ liệu quy hoạch: **2 TB workspace thực dùng**, **16,29 GB chat/90 ngày**, **52,8 GB audit/12 tháng**; khoảng **565.000 connector call** và **24,34 GB egress/tháng**. Phong/Bảo còn phải xác nhận kích thước và đường truyền.
- 220 giờ hành chính/tháng; thành phần 24/7 tính 730 giờ/tháng; production HA hai AZ + một staging.

**Lời nói (~35 giây):** “DAU chỉ là điểm bắt đầu. Chúng tôi chọn 10 request mỗi người mỗi ngày để suy ra 440 nghìn request/tháng, rồi phân theo năm cấp tác vụ để tính token, sandbox và dữ liệu. Peak 4 lần trung bình là giả định thiết kế, sẽ được đối chiếu bằng load test. Quota 10 GB là giới hạn, không phải dung lượng đã dùng để tính tiền.”

## Slide 2 — kiến trúc AWS Singapore, đủ 19 component

**Hình:** dùng một sơ đồ logic tại [ARCHITECTURE.md](ARCHITECTURE.md), chia thành hàng Edge/Identity → Orchestration/Policy → Model/Data/Tool → Operations. Mỗi hộp giữ nguyên mã component; đánh dấu production hai AZ, staging và Bedrock APAC geo cross-region. Đưa sơ đồ replica chi tiết sang slide HA của Bảo.

**Callout:** LB/gateway/database không có điểm lỗi đơn; workspace và quyền đi theo user; Bedrock đi qua VPC interface endpoint. Cấp 5 mặc định SVG/HTML; không đưa prompt bitmap ra ngoài APAC khi chưa duyệt.

**Lời nói (~35 giây):** “Cloud chính dự kiến là AWS Singapore. API Gateway chuyển request qua VPC link đến load balancer và hai AZ; quyền được kiểm trước và sau truy xuất tài liệu. Model, connector và sandbox là ba nhánh tách biệt, với kiểm soát trước hành động ghi và publish artifact. Bảo đang chốt giá bảo mật, backup và vận hành. APAC cross-region của model cần tổ chức duyệt residency.”

## Slide 3 — request từ SSO đến kết quả

**Luồng lớn:** `authn → gateway (API Gateway REST) → network (VPC link) → load_balancer (ALB) → authz/compute → governance → llm hoặc connector/sandbox đã kiểm → ALB → API Gateway → user`.

1. SSO/MFA, session và quota; ACL lọc RAG theo quyền user.
2. DLP trước model; dữ liệu ngoài được coi là không tin cậy. Model đề xuất, policy quyết định.
3. Sandbox không egress và không token; connector dùng OAuth ủy nhiệm. Hành động ghi cần user duyệt payload/đích trước khi chạy.
4. Trace/audit che dữ liệu; job nền có queue, thông báo, backup/restore. Target TTFT p95 ≤3 giây, agent ≤10 phút; chưa có kết quả đo.

**Lời nói (~35 giây):** “API Gateway nhận request và qua VPC link đến ALB. Backend xác thực phiên và kiểm quyền. Khi RAG lấy tài liệu, quyền gốc được kiểm lại trước khi đưa vào prompt. Code chạy trong sandbox tạm không có mạng và token; artifact được kiểm trước khi lưu. Nếu model muốn cập nhật Jira, user phải xem và xác nhận đúng payload. Kết quả quay về qua ALB và API Gateway.”

## Slide 11 — chi phí và đòn bẩy (điền sau khi nhận đủ giá)

**Headline:** `TOTAL = CHỜ XLSX USD/tháng`; `USD/DAU = TOTAL / 2.000`.

- Top 5: cộng các dòng cùng component rồi lấy **năm component USD lớn nhất** trong `BaoGia`; ghi USD/tháng và tỷ lệ trên `TOTAL`.
- Phần Kiệt hiện có **1.679,86 USD/tháng** cho text + embedding + gateway, **chưa** có hạ tầng/data/sandbox/labor. Dòng bitmap 176 USD ngoài APAC bị loại khỏi baseline.
- Labor Dũng đề xuất **800 USD/tháng** theo 40 giờ × 20 USD, chờ nhóm xác nhận.
- Đòn bẩy đã có công thức: routing Micro/Pro tiết kiệm **774,95 USD/tháng** so với toàn Pro theo giả định Kiệt, chỉ áp dụng khi eval từng cấp ≥95%. Không trừ thêm cache hit chưa đo.

**Lời nói (~30 giây):** “Tổng cuối lấy đúng từ dòng TOTAL của XLSX, không cộng tay trên slide. Năm component lớn nhất sẽ cho thấy nơi cần tối ưu. Routing model tiết kiệm khoảng 775 USD mỗi tháng trên workload giả định, nhưng chỉ khi model nhẹ vượt cổng chất lượng.”

## Slide 12 — rủi ro và 4.000 DAU

**Kịch bản:** giữ 10 request/người/ngày và mix 5 cấp ⇒ **880.000 request/tháng**, peak ≈ **4,44 request/s**, text ≈ **2.111,12M input + 603,68M output token/tháng**, sandbox **119.680 run/tháng**. Đây là tải gấp đôi, **không tự suy ra TOTAL gấp đôi**.

- Với từng dòng báo giá, phân loại meter biến đổi (token/request/run/GB) và công suất cố định theo SKU/replica. Tính lại capacity, AZ failover, quota và tier/license trước khi cộng `TOTAL_4k`.
- Phần Kiệt: text/gateway tăng theo request, nhưng corpus index 10M token giữ nguyên. Theo giả định này, 1.679,86 → **3.359,20 USD/tháng** ở 4.000 DAU nếu giữ đơn giá/model mix; nếu corpus cũng gấp đôi thì tính lại. Labor 800 USD chỉ giữ nguyên nếu ca trực không đổi; cần xác nhận.
- Rủi ro chính: APAC geo inference/residency, eval Micro ≥95% và TTFT p95, ACL stale hoặc token lộ, peak sandbox sau mất AZ, thiếu backup/audit/egress trong giá.
- Cổng xử lý: kiểm điều khoản Bedrock/PrivateLink, eval và load test; deny khi ACL không xác minh; thử mất AZ/restore với RTO 4 giờ, RPO 1 giờ; cảnh báo ngân sách 70/90/100%.

**Lời nói (~35 giây):** “Ở 4.000 DAU, token và sandbox tăng gần gấp đôi theo giả định sử dụng. Giá cuối cần tính lại từng meter và bậc công suất, đặc biệt khi mất một AZ. Trước khi tuyên bố đạt, chúng tôi phải đo chất lượng, p95, failover và khôi phục; rủi ro lớn nhất là quyền dữ liệu và residency của inference.”

## Kiểm trước khi ghép

- Dũng đối chiếu mọi số ở đây với [ASSUMPTIONS.md](ASSUMPTIONS.md), Kiệt và `BaoGia` master.
- Kiệt duyệt số model/routing và điều kiện eval; Phong duyệt data/ACL/storage; Bảo duyệt cloud, HA, sandbox và H1–H7.
- Thay toàn bộ `CHỜ`; tổng slide 11 bằng `TOTAL` XLSX; tên file `Gxx` đổi theo mã nhóm. Chỉ đánh dấu H6/H7/H8 đạt khi có bằng chứng thử tương ứng.
