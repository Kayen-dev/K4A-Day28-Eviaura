# HA, vận hành và kế hoạch kiểm chứng

Đây là mục tiêu thiết kế và tiêu chí nghiệm thu. **Chưa có môi trường chạy hay kết quả đo/restore.** Với bài thiết kế, trình bày cách kiểm và lý do khả thi; không ghi các ca dưới đây đã pass.

## 1. Topology đề xuất

- Một cloud chính, một region có ít nhất hai AZ. Cloud/region và SKU chờ Dũng/Bảo chốt theo giá, dịch vụ và điều khoản dữ liệu/model.
- Public edge chỉ có LB/WAF nếu chọn; gateway/orchestrator đặt private, tối thiểu hai replica phân tán AZ. Kiểm LB có HA do dịch vụ cung cấp, không tự đặt một VM proxy làm điểm lỗi đơn.
- Database có primary/standby hoặc cơ chế HA tương đương, failover và endpoint được ứng dụng hỗ trợ. Phong xác nhận replication, connection retry và năng lực sau mất AZ.
- Queue/cache: queue công việc phải bền vững; cache có thể tái tạo, không là nơi duy nhất giữ job/approval. Không để queue, vault hay bộ kiểm quyền thành điểm lỗi đơn của luồng chính.
- Model/API, vector store, KMS, IdP, DNS và đường egress là phụ thuộc phải rà tính sẵn sàng. Không giả định chúng tự HA. Kiệt/Phong chốt fallback vẫn đạt quyền, điều khoản và chất lượng.
- Giữ năng lực tối thiểu sau khi mất một AZ; autoscaling có thể bổ sung nhưng không thay thế phần dự phòng cần để đạt SLO. Sandbox dùng pool riêng để code không chiếm hết gateway.
- Staging tách secrets/identity/storage, không dùng dữ liệu production thô. Được giảm tài nguyên/lịch chạy nếu ghi rõ chi phí và giới hạn; production cần HA không bị tắt theo staging.

## 2. SLO, metric và cảnh báo

| Mục | Mục tiêu / cách đo | Đề xuất phản ứng |
| --- | --- | --- |
| Availability | Theo đề ≥99,5% trong 220 giờ hành chính/tháng; error budget tương ứng 66 phút. Ghi rõ probe/request nào tính thành công và lịch GMT+7 | Dũng/Bảo chốt người trực chính và dự phòng; cảnh báo lỗi tăng và mất health một AZ |
| TTFT | Theo đề p95 ≤3 giây ở peak cho chat/email/tài liệu; đo từ request hợp lệ được nhận đến token hiển thị đầu tiên, gồm queue và mạng; báo riêng cache hit/miss | Kiệt+Bảo rà queue, prefill, model throttling và pool sẵn sàng; không bỏ mẫu chậm khỏi phép đo |
| Agent nền | Theo đề xong ≤10 phút và có thông báo; đo từ nhận job đến trạng thái cuối + gửi thông báo | Đề xuất báo khi tuổi job >8 phút; timeout có trạng thái rõ, không báo thành công giả |
| Sandbox | CPU/RAM/PID, queue time, timeout, blocked egress, cleanup thất bại | Giới hạn đồng thời/user, xử lý job treo, cô lập worker lỗi |
| Data/connector | DB latency/connections, replication lag, queue age, OAuth lỗi, ACL freshness, rate-limit | Fail closed khi không kiểm quyền; retry có backoff cho đọc; ghi phải idempotent/đối soát |
| Security | DLP deny, approval mismatch/replay, access deny chéo user, vault decrypt bất thường | Cảnh báo không kèm raw secret; thu hồi phiên/token liên quan khi xác nhận sự cố |
| Backup | Backup age, trạng thái archive log/PITR, restore drill, khả năng đọc khóa | Cảnh báo trước khi điểm phục hồi mới nhất quá 1 giờ |
| FinOps | Token/model, sandbox seconds, storage/log/egress theo tenant/user/component | Ngưỡng đề xuất 70/90/100% ngân sách: báo → hạn chế tác vụ tùy chọn → chặn phát sinh vượt hard cap |

Quota kiểm trước enqueue/gọi model, dự trù chi phí cho job đang chạy và đối soát sau hoàn tất; hard cap có thể overshoot nếu chỉ dựa vào hóa đơn trễ. Không cắt audit, authz hay backup để tiết kiệm. Ngân sách, ngưỡng quota và người nhận alert cần nhóm duyệt.

## 3. Backup/DR

Mục tiêu đề: **RTO ≤4 giờ, RPO ≤1 giờ**. HA là xử lý lỗi dịch vụ/AZ; backup còn phải xử lý xóa nhầm/corruption, không thay nhau.

- Database: đề xuất full backup hằng ngày + continuous transaction log/PITR, hoặc cơ chế được chọn bảo đảm điểm khôi phục mới nhất không quá một giờ. Phong xác nhận khả năng và giá.
- Object/workspace: versioning + bản sao/backup chống xóa với cửa sổ bảo vệ ≤1 giờ; kiểm cả metadata và quyền. Lịch sao chép ngày không đủ RPO 1 giờ.
- Vector index: hoặc backup đáp ứng RPO, hoặc rebuild từ nguồn ingest bền vững có ACL/version, đo thời gian rebuild trong ngân sách RTO. Không mặc định rebuild 20 TB xong trong bốn giờ.
- Audit/vault: backup cấu hình, dữ liệu, khóa và quyền khôi phục; không lưu khóa giải mã cùng nơi bằng quyền tương đương. Bản backup tách quyền xóa khỏi tài khoản vận hành thường.
- Đề xuất retention backup 35 ngày, restore drill hằng tháng và sau thay đổi lớn. Đây là giả định cần duyệt; audit vẫn giữ đủ 12 tháng.
- Dự phòng mất AZ trong region là baseline. Muốn tuyên bố phục hồi khi mất cả region phải thêm bản sao ngoài region, khóa/registry/IaC sẵn sàng, bằng chứng thời gian và chi phí. Không tuyên bố DR toàn region đã đạt với topology hai AZ đơn thuần.

### Runbook khôi phục dự thảo

1. Phát hiện, ghi mốc bắt đầu gián đoạn/mất dữ liệu; khoanh vùng lỗi và dừng hành động ghi có nguy cơ lặp/corruption.
2. Với mất AZ: health check loại endpoint lỗi, failover DB và chuyển tải sang AZ còn lại; kiểm quyền, queue và công suất.
3. Với cần restore: chọn điểm sạch, dựng môi trường cô lập bằng IaC, khôi phục data/object/vault/index tương thích. Không restore đè bản còn tốt ngay.
4. Kiểm checksum/sample record, tenant/user ACL, token decrypt, truy vấn và action có approval; đối soát job in-flight trước replay.
5. Chuyển traffic, thông báo trạng thái, ghi thời gian phục hồi và khoảng dữ liệu mất; đối chiếu RTO/RPO bằng số đo.
6. Lưu bằng chứng drill, lỗ hổng và việc sửa. Phân bổ thời gian đề xuất: phát hiện 15 phút + dựng 45 + restore 120 + xác minh/chuyển 60 = 240 phút; phải đo để xác nhận.

## 4. Ma trận yêu cầu và ca kiểm chứng

Tất cả ca có trạng thái **CHƯA CHẠY**. Khi chạy ghi ngày, build/config, đầu vào, kết quả, log đã che và người kiểm. Mọi thử nghiệm chỉ trên dữ liệu/môi trường nhóm sở hữu.

| ID / yêu cầu | Kịch bản và tiêu chí đạt | Owner phối hợp / component tính giá |
| --- | --- | --- |
| T01 / H1 | Xác minh cloud/region và đường API model; lưu điều khoản no-training và private endpoint hoặc cam kết no-retention áp dụng đúng gói/endpoint | Dũng, Kiệt / network, llm |
| T02 / H2 | Token hết hạn/sai audience bị từ chối; MFA theo policy; user không tự gán role admin | Phong / authn, authz |
| T03 / H2–H3 | A yêu cầu tài liệu/workspace/memory B bằng ID trực tiếp, RAG và cache: không trả nội dung hay snippet không được phép | Phong / authz, vector_db, object_storage |
| T04 / H2–H3 | Thu hồi quyền ở nguồn rồi truy vấn lại: không dùng ACL/cache cũ vượt cửa sổ nhóm chốt; không xác minh được thì deny | Phong / authz, connectors |
| T05 / H2–H5 | Token connector không xuất hiện trong prompt/log/sandbox; thu hồi connector khiến lần gọi sau bị chặn/reauth | Phong / secrets_kms, connectors |
| T06 / H3 | Code cố gọi Internet, DNS, metadata IPv4/IPv6, API nội bộ: bị chặn; không đọc file user khác/host/socket/credential | Kiệt / sandbox, network |
| T07 / H3 | Vượt CPU/RAM/PID/disk/time bị giới hạn; kill/crash vẫn cleanup; job user B không thấy dữ liệu job A | Kiệt / sandbox, compute |
| T08 / H4 | Email có chỉ dẫn gửi hợp đồng ra ngoài: không tự gọi tool ghi, không lộ secret; nếu tạo đề xuất vẫn qua policy/approval | Kiệt, Phong / governance |
| T09 / H4 | Đổi người nhận/payload sau approval hoặc replay approval: không thực thi; retry cùng job không tạo thao tác ghi trùng | Phong / governance, connectors |
| T10 / H5 | Dữ liệu mẫu PII/secret bị xử lý theo policy; TLS/mã hóa, quyền audit và lifecycle 12 tháng có cấu hình đối chiếu | Phong / governance, secrets_kms, monitoring |
| T11 / H6 | Load test theo peak đã chốt: p95 TTFT ≤3 giây, agent ≤10 phút và thông báo; lưu phân bố latency và tải | Kiệt / gateway, compute, monitoring |
| T12 / H7 | Mất AZ hoặc replica: LB/gateway/DB failover; đo lỗi, latency, queue và năng lực AZ còn lại | Dũng, Phong / compute, load_balancer, database |
| T13 / H7 | Restore dữ liệu mẫu tại điểm sạch: quyền đúng, RTO ≤4h, RPO ≤1h; backup còn dùng được khi mất quyền vận hành thường | Phong / backup_dr, secrets_kms |
| T14 / H8 | Từng cấp đạt ≥95% điểm tham chiếu có tên; đổi model/prompt không qua eval bị chặn phát hành | Kiệt / governance, cicd, llm |
| T15 / H8 | Vượt quota hoặc dự trù ngân sách: job/gọi model bị chặn theo policy, có thông báo; job in-flight được đối soát | Kiệt, Dũng / gateway, monitoring |

## 5. CI/CD và bằng chứng nộp bài

Đề xuất pipeline: review → kiểm secrets/dependency/image/IaC → unit/integration liên quan → eval và security regression → staging → duyệt release → rollout có rollback. Image pin theo digest, registry riêng, quyền deploy tách production/staging; pipeline không chứa token dài hạn nếu nền tảng hỗ trợ workload identity.

Trước bàn giao: ghi nguồn SKU/region/giá, kiểm đủ 11 component của Bảo, staging/HA/log/backup/egress đã tính; kiểm với Phong không trùng DB/replica/storage. Dũng chạy validator XLSX và đối chiếu TOTAL trên slide. Validator đạt không chứng minh H1–H8 đã đáp ứng hay giá trong ảnh là đúng.
