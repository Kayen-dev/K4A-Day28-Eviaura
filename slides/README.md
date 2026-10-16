# Slide VBot — bản nháp PDF

- `VBot_Eviaura_DRAFT.pdf`: bản trình bày 12 slide, 16:9.
- `VBot_Eviaura_DRAFT.pptx`: bản chỉnh sửa được.
- `build_slides.py`: mã nguồn tái tạo deck; chạy `python slides/build_slides.py`, rồi xuất PPTX sang PDF.

Nội dung lấy từ đề gốc và tài liệu trong `dung/`, `kiet/`, `bao/`. Repo chưa có bản bàn giao riêng của Phong và chưa có báo giá đầy đủ của Bảo. Vì vậy slide 7 dùng giả định trong `dung/ASSUMPTIONS.md`; slide 11 **không có TOTAL cuối cùng**. Chưa dùng file này để nộp như bản khóa: cần Phong/Bảo bổ sung giá có bằng chứng, Dũng lập XLSX `BaoGia`, cập nhật TOTAL/top 5/USD mỗi DAU, chốt mã nhóm để đổi tên file, rồi kiểm nội dung với cả bốn người.

Các số request, peak, corpus và tỷ lệ route là giả định; eval, load test, failover và restore drill chưa chạy. Bản PDF cố ý không tuyên bố đã đạt H1–H8.
