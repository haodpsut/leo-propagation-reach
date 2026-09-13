# Vòng đọc ngoài 2 (12/09/2026): Major. Đối chiếu từng yêu cầu với bản sửa

Nguồn: https://justpaste.it/gmulb (bản đọc ngoài của Hảo trên draft 3, 25 trang).
Mọi con số dưới đây sinh từ `figures/make_figures.py`; không số nào gõ tay.

## Kiểm số reviewer nêu (trước khi sửa gì)

| Reviewer nói | Dữ liệu | Kết luận |
|---|---|---|
| |S| của 24 ô = 4,5,6,6,6,7,7,7,8×5,9×5,10×6 | khớp từng ô | đúng |
| 10/24 CI loại 0, 9 heat | 10, 9 heat, 1 walk | đúng |
| 8/8 p thô < 0.05 đều heat | 8, cả 8 heat | đúng |
| Bảng 10 train ≈ test | hop: bằng tới 5 chữ số; delay: lệch ≤ 0.0012 | đúng, và còn hơn: torus đỉnh-bắc-cầu nên hop field là MỘT trường |
| 13/24 ô far-node ở sàn | 13 với hằng số MAE; **0** với hằng số far-node đúng (0.258 vs 0.202) | draft 3 dùng SAI hằng số; sửa `summarise(key="aurc")` |
| SGC 1584 = 0.202 vs const 0.2018, sd 0.088, n=7 | đúng; 3/7 seed nằm ở hằng, 4/7 thoát | bimodality seed, không phải reach |
| 53%/29% hai định nghĩa; 52.2/36.0 | 52.5 / 36.4 theo cột bảng | đúng; chốt MỘT định nghĩa |
| tổng run 2920, không phải 2640 | 1920 + 720 + 160 + 120 = 2920 | đúng |
| baseline reach xa gấp 3–5 lần kernel | **sai chiều**: đo reach kỳ vọng trên s1584: PPR 2.5, SGC 2.8 hop/lớp; heat 6.4, walk 11.7 | baseline NGẮN hơn ~2 lần |

## Hai lỗi reviewer KHÔNG bắt được, tự tìm ra khi kiểm Bảng 10

1. `grid_isl_graph(seam=True)` GIỮ link qua seam. Docstring và bài đọc ngược. Toàn bộ 2920 run là torus 4-đều; cắt cực 70° vô hiệu ở 53°. Bài ghi "seam cut" ở §3.1, caption Bảng 1, §7 đều sai. Sửa: khai thật, thêm nhánh cắt seam thật (`--seam cut`).
2. Vì torus đỉnh-bắc-cầu, hop field từ mọi đích đẳng cấu; mạng đẳng biến; train MAE = test MAE. "Held-out" trên hop field là bản sao. Khai ở §3.3, §5.3.

## Thí nghiệm mới (VPS, GPU, kết quả trong `code/results/rev2/`)

| Nhánh | Run | Kết quả |
|---|---|---|
| Thang baseline: SGC K'∈{2,8,32,64}, PPR chính xác α∈{0.2,0.05,0.02,0.01} | 480 | best rung/ô; kernel ở nhánh t tốt nhất hơn 1.1–16.5%; nhánh tệ nhất thua ở 5/6 ô; SGC K'=64 ở 264 = hằng số (over-smoothing) |
| Cắt seam, softplus t0=0.5 + ppr/sgc | 300 | hop/1584: walk 0.065 vs heat 0.113, 0:8, p=0.008 → hướng sơ bộ TÁI LẬP trên đồ thị có seam |
| Cắt seam, 3 nhánh t còn lại | 540 | đang chạy (13/09) |
| float64 toàn bộ, hop/1584/softplus 0.5 | 30 | MAE từng seed lệch tới 0.155; cùng seed đổi basin; hiệu heat−walk đổi dấu |

## Yêu cầu → thay đổi

### Tiêu chí 2 (phương pháp)
- (a) lực luật 6: Bảng `tab-power` (min p theo |S|, 18/24 không thể bác, 6 cần 10:0, MDE); luật 6 đổi đơn vị sang GỘP theo (task, shell), Holm trên 6, MDE in cạnh mỗi kết quả (`tab-pooled`).
- (b) hướng: §5.3 nêu 10 CI loại 0 (9 heat, 7 ở 264), 8/8 p thô heat; headline mới: heat thắng ở 264 cả hai tác vụ (10:0, Holm 0.012); 1584/3168 không chứng nhận, MDE lớn hơn hiệu quan sát.
- (c) reach: đo thật (`analysis/fields.py reach`, Bảng `tab-reach`); thang baseline; câu "comparable reach" bỏ.
- (d) cột const: thêm vào Bảng 7 (grid3), 11 (fixed), 12 (aurc), ladder, seam; Bảng 13 caption trỏ tới 12.
- (e) precision: chạy lại ô ở float64 (`tab-precision`), thay câu "identical to 16 digits".
- (f) phụ thuộc: nêu trong "Operating characteristics of rule 6"; Holm hợp lệ dưới phụ thuộc bất kỳ.

### Tiêu chí 3 (dữ liệu)
- (a) Bảng 10: viết lại đúng bảng + giải thích đẳng cấu.
- (b)(c) far-node floor: hằng số far-node tính cho mọi ô (`analysis/fields.py const` → `results/const_aurc.json`); 0 ô ở sàn; câu "every cell leaves the floor" giữ, nay đúng cả hai thước.
- (d) gain baseline theo shell + chẩn đoán 1584 (3 seed ở hằng).
- (e) biên: một định nghĩa (kernel thấp hơn trong từng nhánh; best/worst arm).
- (f) 2920 ở abstract, §4.1, Data availability; baseline vào Bảng 4 (above) và 16 (collapse).
- (g) Bảng 15: câu về ≥8/10 → 0/0 và sàn không tác dụng ở lưới 2.
- (h) "both robust verdicts at 264": nêu ở §5.3, abstract, kết luận.

### Tiêu chí 4, 5, 6
- Discussion: absence vs evidence of absence; sàn: hằng số không đủ, ngưỡng phải khai trước; §7 thêm lực luật 6, thang baseline, precision hỗn loạn, cờ seam.
- §2 gap: "reach measured, not asserted".
- Table-first pass: mọi đếm định tính chuyển thành macro (`numLadderWorstBehindCells`, `numSpecBestBeatsLadderCells`, ...).

## Chưa xong (13/09)
- 3 nhánh t cắt seam đang chạy; §5.5, Discussion, Intro, Abstract dùng macro `numSeam*` nên số tự cập nhật, NHƯNG câu chữ về "heat giữ 264 trên cả hai tác vụ ở đồ thị cắt seam" phải kiểm lại khi có đủ 4 nhánh (hiện delay/264 cắt seam: Holm 0.586, chưa chứng nhận).
- Abstract 286 từ, cần về ≤250.
- Đọc ngoài vòng 3.
