# Sizing, chi phí và đầu vào cần nhận

Chưa chốt cloud/SKU/giá. Các biểu thức dưới đây là khung để điền bằng số nhóm xác nhận, không phải báo giá nộp. Không điền 0 USD cho mục chưa biết; không dùng URL tài liệu kỹ thuật làm bằng chứng giá.

## 1. Đầu vào và người xác nhận

| Biến | Giá trị / đơn vị | Người cung cấp |
| --- | --- | --- |
| U, D, H | 2.000 DAU, 22 ngày/tháng, 220 giờ hành chính/tháng theo đề | Cố định |
| H_full | 730 giờ/tháng theo đề | Cố định |
| r | CHỜ: request/user/ngày | Dũng + Kiệt |
| p_i, s_i, t_i | CHỜ: tỷ trọng cấp i (tổng =1), số lần chạy sandbox/request cấp i, giây/lần | Kiệt |
| lambda_peak | CHỜ: số lần khởi chạy sandbox/giây ở peak, gồm fan-out/retry theo giả định | Kiệt |
| c, m, d_tmp | CHỜ: vCPU, GB RAM, GB scratch mỗi phiên; runtime startup/cleanup | Kiệt + Bảo |
| peak_RPS, sessions | CHỜ: request/giây và số phiên đồng thời | Dũng + Kiệt |
| S_used, growth | CHỜ: GB thực dùng/user, tăng trưởng và số user lưu dữ liệu | Phong |
| DB, vector, audit | CHỜ: GB, read/write/IOPS, vector/index; event/ngày, byte/event và hệ số index/replica | Phong |
| connector/model egress | CHỜ: call/tháng, GB/tháng, rate limit, nơi endpoint và đường mạng | Phong + Kiệt |
| IdP | CHỜ: nhà cung cấp, số user cấp phép/MAU, gói hiện có có áp dụng không | Dũng + Phong |
| Deployment | CHỜ: cloud/region, API/tự host/hybrid, staging giờ chạy, reserve policy | Dũng + Bảo + Kiệt |

DAU không tự cho biết tổng tài khoản/MAU. Không dùng 2.000 làm số license hoặc MAU nếu nhóm chưa giả định số người đăng ký/hoạt động tháng.

## 2. Công thức sizing

- Request/tháng: `N_req = U × D × r`.
- Sandbox run/tháng: `N_sb = N_req × Σ(p_i × s_i)`; tính cả retry nếu số lần chạy chưa chứa retry. Cấp tác vụ không dùng sandbox đặt `s_i=0`.
- Sandbox vCPU-hour: `N_req × Σ(p_i × s_i × c_i × t_bill_i) / 3600`. RAM GB-hour tương tự dùng `m_i`. `t_bill` gồm overhead và billing rounding/minimum của dịch vụ, không chỉ thời gian code.
- Phiên đồng thời quy hoạch: `ceil(lambda_peak × t_plan × headroom)` với `lambda_peak` tính run/giây, `t_plan` tính giây, `headroom ≥1` nhóm chọn. Đây là ước lượng ban đầu, cần load test cho burst/queue; không thay số đo p95.
- Với mỗi phiên c vCPU, m GB, worker khả dụng C vCPU/M GB: `slots_per_node = min(floor(C/c), floor(M/m))`, sau khi trừ tài nguyên OS/runtime. `nodes_needed = ceil(concurrency / slots_per_node)` nếu slots >0.
- Nếu cần giữ đủ tải khi mất một trong hai AZ, mỗi AZ phải có năng lực còn lại đủ hoặc có kịch bản giảm tải hợp lệ. Không chia đôi `nodes_needed` rồi mặc định vẫn chịu nguyên peak khi mất AZ.
- Quota workspace: `2.000 × 10 GB = 20.000 GB` chỉ là trần cho giả định 2.000 user; giá storage dựa dung lượng thực, phiên bản, backup và tổng user nhóm chọn.
- Audit steady state 12 tháng: `events/day × bytes/event × days_in_12_months / 10^9 × storage_overhead`; thêm ingest, index/search, query, replication và retrieval nếu tính riêng. Không lấy 30 ngày rồi gọi là đủ 12 tháng.
- Compute VM: `Σ(node_count × billed_hours × USD/node-hour) + disk + control_plane_if_any`. Service/serverless tính theo meter nhà cung cấp; không cộng thêm VM hosting nếu đã bao gồm.
- Egress: phân loại Internet/model/connector, cross-AZ, cross-region; `Σ(GB_path × unit_price_path)` theo bảng giá/tier được chọn, cộng endpoint/NAT fixed-hour và processing nếu áp dụng. Tránh tính một đường hai lần và không mặc định private endpoint miễn phí.

## 3. Danh mục 11 component Bảo phải giao

Mọi dòng dưới đây: **CHỜ SỐ / CHỜ BẰNG CHỨNG GIÁ**. Khi ghép vào `BaoGia`, dùng đúng 5 cột theo đề, có thể tách nhiều dòng một component. Bảng này không thay file XLSX.

| Component | Ý nghĩa | Cơ sở tính cần điền | Ranh giới / đầu vào |
| --- | --- | --- | --- |
| sandbox | Chạy code cô lập | Run × thời gian tính tiền × CPU/RAM hoặc worker-hour; scratch, idle pool và runtime overhead | Kiệt cho tải; nếu worker đã ở compute thì dòng này nêu nằm trong compute, không cộng hosting lại |
| authn | SSO/MFA/session | User/MAU/license + MFA event nếu có; gói IdP áp dụng | Không mặc định SSO có sẵn = miễn phí; Dũng rà licenses |
| authz | RBAC/ABAC/ACL enforcement | Policy engine hosting/request + ACL sync nếu có | Phong sở hữu connector/data; nếu chạy chung compute ghi rõ số dòng bao gồm |
| secrets_kms | Token vault và khóa | Vault instance/operation + số secret/version + KMS key/request | Phong nêu token count/rotation, thêm khóa backup nếu tính riêng |
| governance | Guardrail/DLP/eval/approval/audit controls | Request/token/scan GB; compute và lưu audit nếu tính ở đây | Kiệt: eval; Phong: storage; không bỏ phí model eval hoặc tính log hai lần |
| compute | Gateway/orchestrator/worker hosting | SKU × số node × giờ; disk/control plane/autoscaling/HA + staging | Tách inference tự host thuộc llm do Kiệt giữ; tách phần worker sandbox rõ ràng |
| load_balancer | Edge/TLS/health check | LB-hour + capacity/request/data processing + WAF nếu chọn | Gateway phần mềm Kiệt giữ; Bảo giữ hosting ở compute theo thỏa thuận |
| network | Kết nối và truyền dữ liệu | NAT/endpoint-hour, processing GB, egress Internet/cross-AZ/cross-region, DNS/IP nếu tính phí | Tính theo đường đi đã chốt và region, không chỉ một số GB tổng |
| backup_dr | Bản sao phục hồi | GB backup/version/log, copy/transfer, restore/drill và standby nếu có | DB HA replica nằm database của Phong; tránh tính lại ở đây |
| monitoring | Metric/log/trace và cảnh báo | Ingest GB, retention hot/archive, query, custom metric, trace sample và alert | Audit 12 tháng ghi rõ nằm đây hay governance/object_storage; không mất phần chi phí |
| cicd | Pipeline/registry/IaC/staging tooling | Build-minute/runner-hour, artifact/image GB, scan/license nếu có | Staging runtime tính compute/data/network một lần; ghi tham chiếu, không cộng đôi |

## 4. Mẫu một dòng để chuyển sang BaoGia

| Component | Ý nghĩa | Ghi chú | Chi phí/tháng (USD) | Bằng chứng |
| --- | --- | --- | --- | --- |
| compute | Hosting orchestrator production và staging | CHỜ: dịch vụ/SKU; cloud/region; N node × 730 giờ × P USD/giờ; topology 2 AZ; staging N_s × H_s × P_s; nêu phần đã bao gồm | CHƯA ĐIỀN | CHỜ URL trang giá/calculator hoặc mã ảnh |

Chỉ đưa vào bản nộp khi cột tiền là số không âm có căn cứ. Khoản 0 USD chỉ dùng khi thực sự nằm trong dòng khác và tham chiếu rõ dòng đó; không ghi 0 để lấp component.

Checklist từng bằng chứng: tên dịch vụ/SKU → region → đơn vị và currency → mức giá/tier/cam kết → ngày lấy giá → số lượng dùng → phép tính tháng → prod/HA/staging → URL/ảnh đối chiếu được. Không dùng free tier/trial/credit. Giá reserved/commitment phải có thời hạn và cách quy đổi, không chỉ dùng giá discount mà bỏ cam kết.

## 5. Công việc có thể làm song song

- Dũng: chọn cùng Bảo cloud/region, điền peak tải và chuẩn bị giá compute/LB/network/backup/monitoring/CI/CD.
- Kiệt: điền `p_i, s_i, t_i, lambda_peak, c, m`, model endpoint/điều khoản và chi phí eval; soát tác động cold start đến H6.
- Phong: điền data size/ACL/OAuth/vault/audit, HA data và cơ chế PITR/backup; đánh dấu chi phí đã bao gồm.
- Bảo: dùng ba nhóm đầu vào để chốt runtime/topology/quyền/DR, rà 11 component và sửa slide.

Khi DAU lên 4.000, không nhân đôi mọi dòng: phần biến đổi theo request/token/run/GB tăng theo giả định tải, phần cố định có thể giữ đến ngưỡng capacity, HA và license có bậc. Tính lại peak/queue/replica/egress và điều kiện chất lượng trước khi đưa số vào slide Dũng.
