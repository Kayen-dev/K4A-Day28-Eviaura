# Nội dung đề xuất cho slide 8–10

Đây là nội dung để Dũng ghép vào deck chung, chưa phải file PPTX/PDF. Các trường `[CHỜ ...]` phải được thay trước khi nộp; không đưa nguyên bảng chi tiết của tài liệu kỹ thuật lên slide. Tổng thời lượng nói đề xuất khoảng 90 giây trong 7 phút của nhóm.

## Slide 8 — Cloud và sandbox cô lập theo user

**Thông điệp:** Code agent chạy trong môi trường tạm, chỉ thấy input đã được cấp quyền.

- Cloud/region: **[CHỜ Dũng + Bảo]**; prod hai AZ, gateway/orchestrator phân tán; staging tách biệt.
- Sandbox: **[CHỜ chốt runtime; ứng viên gVisor]**, pool riêng; non-root, không đặc quyền, không cloud/OAuth credential.
- Mặc định chặn mạng ngoài/nội bộ/metadata; giới hạn CPU/RAM/PID/disk/thời gian; hủy sau chạy.
- Runner stage input đúng user, kiểm output rồi publish về workspace; code không tự gọi connector.

Sơ đồ gợi ý: `load_balancer → gateway → authz → compute → cache_queue → sandbox`; cạnh sandbox ghi “stage/publish qua runner”; vẽ hai AZ cho phần dịch vụ luôn chạy, workspace đặt ngoài sandbox và ghi mã `object_storage`. Bổ sung `network` ở ranh giới. Dũng ghép các mã còn lại trong sơ đồ tổng.

**Lời nói (~30 giây):** “Bảo phụ trách ranh giới cloud và môi trường chạy code. Gateway và orchestrator được phân tán qua hai AZ. Code agent chạy trong sandbox riêng, không mang token OAuth, không được tự truy cập mạng hay metadata cloud. Runner chỉ đưa vào dữ liệu user được phép đọc, kiểm kết quả rồi lưu về đúng workspace. CPU, RAM và thời gian sẽ lấy từ bảng sizing chung.”

## Slide 9 — Quyền và governance trước mọi hành động

**Thông điệp:** Model đề xuất; hệ thống kiểm quyền và người dùng duyệt hành động ghi.

- `authn`: SSO + MFA; `authz`: RBAC/ABAC và ACL gốc, áp dụng cho RAG/cache/workspace.
- `secrets_kms`: OAuth ủy nhiệm scope tối thiểu; vault mã hóa; model/sandbox không nhận token.
- `governance`: guardrail + DLP input/output; nội dung connector là dữ liệu không tin cậy.
- Ghi ra ngoài: kiểm policy → xem trước → approval gắn đúng payload → kiểm lại quyền → thực thi và audit.
- Audit 12 tháng; model không huấn luyện trên dữ liệu, API ngoài đáp ứng kênh H1; đổi model/prompt phải qua eval gate.

Sơ đồ gợi ý: `Đề xuất → Quyền/DLP → User duyệt → Connector → Audit`; nhánh deny kết thúc, nhánh payload đổi quay lại duyệt. Nêu “ACL thu hồi: vô hiệu cache/kiểm lại nguồn”.

**Lời nói (~30 giây):** “Quyền của user được kiểm ở backend và giữ nguyên qua truy xuất tài liệu, bộ nhớ và connector. Token được cất trong vault mã hóa, không đi vào prompt hoặc sandbox. Một email chứa lệnh ẩn không được tự cấp quyền cho agent. Gửi email, tạo ticket hay xóa file đều cần user xem đúng nội dung và xác nhận; thay nội dung sau duyệt phải xin duyệt lại.”

## Slide 10 — HA, phục hồi và kiểm soát chi phí

**Thông điệp:** Có mục tiêu và cách kiểm chứng; chưa tuyên bố đạt khi chưa có bằng chứng.

- H7: availability **99,5% giờ hành chính**; không điểm lỗi đơn ở LB/gateway/database; dự phòng tải khi mất một AZ.
- Backup/PITR **[CHỜ dịch vụ Phong/Bảo]**; mục tiêu **RTO 4 giờ / RPO 1 giờ**, diễn tập restore và kiểm ACL.
- Theo dõi p95 TTFT **≤3 giây**, job nền **≤10 phút** kèm thông báo; log/metric/trace và tuổi backup.
- Quota/user, dự trù chi phí job đang chạy; cảnh báo và hard cap. CI/CD qua staging, eval, duyệt release và rollback.
- **[CHỜ]** SKU/số replica, chi phí 11 component, nguồn giá và kết quả kiểm khả thi. H6/H8 phối hợp Kiệt; database phối hợp Phong.

Sơ đồ gợi ý: `AZ-A ↔ AZ-B → backup tách quyền`; cạnh backup ghi RPO/RTO, phía dưới ghi metric/alert. Không vẽ một bản sao ngoài region nếu chưa chọn và tính tiền.

**Lời nói (~30 giây):** “Nhóm thiết kế failover khi mất một AZ và backup cho cả tình huống xóa nhầm hoặc hỏng dữ liệu. Mục tiêu là phục hồi trong bốn giờ, mất dữ liệu tối đa một giờ; phải chứng minh bằng cơ chế backup và kế hoạch restore. Monitoring theo dõi độ trễ, queue, bảo mật và chi phí. Hạn mức được kiểm trước khi cấp tài nguyên, đồng thời dành ngân sách cho job đang chạy.”

## Câu hỏi Bảo nên chuẩn bị

1. **A có đọc được dữ liệu B?** Kiểm owner từ phiên xác thực, ACL ở truy xuất và đọc file, cache theo quyền, runner mount đúng input; chứng minh bằng T03/T04.
2. **Sandbox gọi metadata/thoát ra node?** Không credentials, runtime isolation, không đặc quyền/host mount, network policy và chặn ở hạ tầng; kiểm T06/T07. Không cam kết tuyệt đối không có lỗ hổng runtime.
3. **Prompt injection gửi hợp đồng ra ngoài?** Nội dung không cấp quyền, policy/DLP và approval gắn payload; kiểm T08/T09.
4. **Một AZ mất lúc 10h?** Health check và failover, năng lực AZ còn lại, retry có kiểm soát và xử lý job in-flight; cần topology/sizing chốt để nói thời gian cụ thể.
5. **Backup nào đáp ứng RPO 1h?** Nêu PITR/log và bản sao object thực tế; backup mỗi ngày riêng lẻ không đáp ứng.
6. **Giá rẻ có bỏ phí bảo mật?** Đối chiếu đủ 11 component, phần bao gồm ở dòng khác, audit 12 tháng, staging, egress và restore drill; chỉ trích số đã có bằng chứng.
