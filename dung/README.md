# Phần Dũng — bản làm việc để ghép nhóm

| Tệp | Mục đích |
| --- | --- |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Một bộ giả định và công thức sizing cho D1–D2; ghi rõ số đã chọn và số còn chờ |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Sơ đồ đủ 19 component, luồng request và bảng đối chiếu chủ sở hữu cho D3 |
| [DUNG_SLIDES_01_03_11_12.md](DUNG_SLIDES_01_03_11_12.md) | Nội dung và lời nói cho năm slide Dũng sở hữu |
| [DUNG_BAOGIA.tsv](DUNG_BAOGIA.tsv) | Dòng `ops_labor` để ghép vào `BaoGia` |
| [AWS_PRICE_HANDOFF.md](AWS_PRICE_HANDOFF.md) | Nguồn AWS và meter cho sáu component Dũng hỗ trợ Bảo rà giá |

Region làm việc Dũng chọn: AWS `ap-southeast-1` (Singapore); Bảo còn phải chốt SKU/topology. Mã nhóm chưa biết nên dùng `Gxx` trong bản nháp. Không gọi các tệp này là bản nộp: giá Phong và Bảo chưa có, nên chưa thể tính `TOTAL`, top 5, USD/DAU hoặc chạy validator đạt. Không thêm `licenses`/`contingency` khi chưa có SKU hoặc chính sách cụ thể; IdP nếu tính phí nằm ở `authn` của Bảo, tránh tính hai lần

## Thứ tự ghép khi nhận bàn giao

1. Phong xác nhận storage, connector/egress và năm dòng data; Bảo xác nhận 11 dòng cloud/bảo mật, topology HA/staging và bằng chứng giá. Kiệt xác nhận 10 request/DAU/ngày, model/region và năm dòng TSV hiện có.
2. Ghép từng dòng vào sheet `BaoGia` đúng năm cột; loại dòng bitmap ngoài APAC của Kiệt trừ khi nhóm duyệt ngoại lệ. Đối chiếu region/SKU/đơn giá với nguồn, tránh phí trùng giữa `compute`, `sandbox`, `gateway`, `database`, `backup_dr`, `monitoring` và `network`
3. Đặt một dòng `TOTAL` cuối, bằng tổng số USD/tháng; tính `TOTAL/2.000`, top 5 và kịch bản 4.000 DAU từ các meter của từng dòng. Cập nhật slide 11–12 bằng đúng số trong XLSX.
4. Chạy validator trong `vbot-capstone.html`; kiểm thủ công ảnh/bảng giá và H1–H8. Xuất deck 16:9, tối đa 15 slide nội dung và 10 MB; đặt tên theo mã nhóm thật trước khi nộp

**Còn chờ:** mã nhóm; Phong/Bảo xác nhận số quy hoạch data/network và bàn giao giá; IdP/license, request mix, labor rate/ca trực; eval/load/restore test. Dòng `ops_labor` chỉ là 40 giờ công hoạt động phân bổ; nếu cần phụ cấp trực hoặc đội trực riêng để đáp ứng RTO, phải cộng và báo giá lại. Những phép kiểm thực nghiệm chưa chạy thì không ghi đã đạt
