# Phần bàn giao của Nguyễn Trường Bảo

Ngày soạn: 16/10/2026. Nguồn yêu cầu: [đề gốc](../vbot-capstone.html) và [phân công](../TEAMMATE_PLAN.md).

Đây là **bản thiết kế đề xuất để nhóm ghép và duyệt**, chưa phải hệ thống đã triển khai, kết quả benchmark hay báo giá cuối. Không đánh dấu B1–B8 hoàn thành chỉ vì đã có tài liệu.

| Tài liệu | Dùng vào việc gì |
| --- | --- |
| [Thiết kế bảo mật và sandbox](SECURITY_DESIGN.md) | Luồng request, quyền, token vault, cô lập, guardrail và dữ liệu |
| [HA, vận hành và kiểm chứng](OPERATIONS_AND_ACCEPTANCE.md) | Topology, backup/DR, SLO, ma trận H1–H8 và ca kiểm thử |
| [Sizing, chi phí và đầu vào đồng đội](SIZING_AND_COST.md) | Công thức, đủ 11 component của Bảo, ranh giới tránh tính trùng |
| [Nội dung slide 8–10](SLIDES_8_10.md) | Nội dung ngắn và lời thuyết trình để Dũng ghép deck |

## Trạng thái theo checkpoint

| Checkpoint | Đã chuẩn bị | Còn cần để chốt |
| --- | --- | --- |
| B1 | Topology logic hai AZ, ranh giới mạng và đường model | Cloud/region, dịch vụ/SKU và điều khoản model |
| B2 | Chính sách sandbox, vòng đời, công thức và ca kiểm chứng | Tải từ Kiệt, runtime/hosting tương thích, số CPU/RAM và giá |
| B3 | Luồng SSO/OAuth, phân quyền và vault | IdP của tập đoàn, scope và ACL thực tế từ Phong |
| B4 | Ma trận kiểm soát, approval, DLP, retention đề xuất | Phong xác nhận lưu trữ; Kiệt xác nhận tập eval và model |
| B5 | HA/DR và runbook, tiêu chí kiểm thử | Dịch vụ backup/PITR, topology dữ liệu, sizing và chi phí |
| B6 | Danh mục 11 component và công thức giá | SKU/region/đơn giá/bằng chứng; dòng XLSX được Dũng ghép |
| B7 | Metric, alert, FinOps và kịch bản mất AZ | Năng lực đo thực tế, người trực và ngân sách nhóm duyệt |
| B8 | Checklist giá và bộ câu hỏi bảo vệ | Bằng chứng giá, validator và kiểm chéo bản nộp |

## Thứ tự tích hợp

1. Dũng và Bảo chốt một cloud/region; Kiệt chốt hướng API/tự host/hybrid. Không lấy giá theo nhiều region rồi cộng chung.
2. Dũng/Kiệt/Phong điền đầu vào trong `SIZING_AND_COST.md`. Mọi giả định cần có đơn vị và chủ xác nhận.
3. Bảo cập nhật số tài nguyên, dịch vụ và các phương án trong tài liệu này; thay toàn bộ mục chờ trong slide.
4. Bàn giao các dòng có bằng chứng cho Dũng ghép XLSX; kiểm tổng và chạy validator trong HTML.
5. Cả nhóm duyệt sơ đồ tổng đủ 19 component. Sơ đồ ở đây chỉ là phần Bảo và các điểm giao tiếp.

Chưa thay đổi kế hoạch gốc, chưa tạo số giá giả, chưa gửi thông tin cho đồng đội hay nộp bài.
