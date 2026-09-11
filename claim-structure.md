# Cấu trúc tuyên bố, khai TRƯỚC khi chạy lại

Bài **kỹ thuật** (đường B), tách ra từ TNSESITD-2026-06-2033 đã reject. Ngày khai: 11/09/2026.
⛔ Chưa chạy thí nghiệm mới nào tại thời điểm khai. Mã kế thừa: `haodpsut/qi-gnn-dynamic-wireless`.

CLAIM: Trên đồ thị liên kết liên vệ tinh của chòm LEO, thứ hạng giữa ba toán tử lan truyền
cùng Laplacian (GCN cục bộ, nhiệt exp(-tL), unitary exp(-itL)) PHỤ THUỘC VÀO QUY MÔ CHÒM: ở
quy mô nhỏ toán tử nhiệt ngang hoặc hơn, và ở quy mô lớn (đường kính đồ thị dài) toán tử
unitary vượt lên, với khoảng cách vượt qua phương sai theo seed. Cơ chế (tầm với ~t so với ~√t)
KHÔNG phải của bài này: nó đã được chứng minh tổng quát ở arXiv:2608.20738 (CTQW-GNN). Đóng
góp của bài này là ĐO hiện tượng đó trong một bối cảnh chưa ai đo, theo một giao thức
param-matched, đa seed, đa quy mô.

MEASUREMENT: (1) Bốn quy mô Walker-delta / Starlink: 264 · 1584 · 3168 · 4408 vệ tinh, cùng
+Grid, cùng polar cutoff. (2) Ba toán tử, cùng mạng, cùng số tham số, cùng ngân sách huấn luyện.
(3) ≥10 seed mỗi ô, báo trung bình ± độ lệch chuẩn và SỐ SEED THẮNG. (4) Hai tác vụ: trường
khoảng cách hop (tác vụ cũ, tổng hợp) VÀ một tác vụ gần vận hành hơn: trường độ trễ lan truyền
end-to-end tới đích (dùng trọng số trễ W đã có trong constellation.py). (5) Thước: MAE toàn cục
và AURC nút xa. (6) Mọi phép đo chạy trên MỘT máy (VPS), một lần chạy, mọi bảng sinh từ một
bộ kết quả.

⛔ NGƯỠNG HỢP LỆ, khai trước (lớp lỗi 24):
  - Một lần chạy chỉ được tính khi MAE huấn luyện giảm đơn điệu trong 3 khoảng và MAE cuối
    < 0,5 (dự đoán hằng số cho ~0,5 trên tác vụ chuẩn hoá). Vi phạm ⇒ ghi PHÂN KỲ, không ghi số.
  - "Thắng" ở một quy mô = trung bình thấp hơn VÀ thắng ≥ 7/10 seed. Không đủ cả hai ⇒ HOÀ.
  - Trend "phụ thuộc quy mô" chỉ được tuyên bố nếu thứ hạng ở quy mô nhỏ nhất và lớn nhất KHÁC
    nhau theo định nghĩa trên. Nếu không ⇒ kết quả là "thứ hạng bất biến theo quy mô".

IF NULL: Nếu unitary không vượt lên ở quy mô lớn với 10 seed (kết quả 3 seed cũ là nhiễu), bài
còn: (a) phép đo param-matched, đa seed, đa quy mô về toán tử lan truyền trên đồ thị LEO, chưa
ai công bố, hữu ích dù chiều nào; (b) kết luận "toàn cục thắng cục bộ ở mọi quy mô, unitary và
nhiệt không phân biệt được" là kết quả âm sạch cho những ai định thay heat kernel bằng quantum
walk; (c) tác vụ trễ lan truyền cho biết kết luận có đổi khi rời tác vụ tổng hợp không. Nhưng
phải nói thẳng: bài IF NULL YẾU ở TNSE, vì venue có tiền lệ cho phương pháp, không cho kết quả
âm. Nếu null ⇒ cân nhắc venue khác (Computer Networks đã đăng kết quả âm) thay vì cố nộp TNSE.

SURVIVES: yes, nhưng đổi venue.

CONTRIBUTIONS:
  - [independent] Bộ đo mở: bốn chòm, hai tác vụ, ba toán tử, ≥10 seed, một lần chạy, sinh lại được.
  - [independent] Giao thức param-matched + ngưỡng hợp lệ khai trước, áp lên so sánh toán tử.
  - [dependent] Thứ hạng toán tử đổi theo quy mô chòm. Chỉ đúng nếu (3) và ngưỡng ở trên thoả.
  - [dependent] Kết luận giữ nguyên khi đổi từ tác vụ tổng hợp sang tác vụ trễ. Chỉ đúng nếu đo được.

## Ràng buộc bài nhà, khai thẳng
- **TNSM-2026-11591 đang phản biện** (GNN cho định tuyến LEO dưới tải, reality-check). Bài này
  KHÔNG dùng chung mã, dữ liệu, kết quả hay hình nào với TNSM. Khác câu hỏi: TNSM hỏi mô hình
  học có thắng ECMP mù dưới tải không; bài này hỏi toán tử lan truyền nào và thứ hạng có đổi
  theo quy mô không. Trong bài chỉ trích TNSM như "under review" nếu được nhận trước, không
  dựa vào kết quả của nó.
- Không dùng chữ "quantum-inspired" trong tiêu đề. Không dùng "honest" ở bất kỳ đâu.

## ⛔ SỬA ĐỔI 11/09/2026, TRƯỚC khi chạy thí nghiệm thật, sau lần khói trên Mac

Lần khói (1 seed, s264, 200 epoch, KHÔNG dùng làm số báo cáo) lộ ra ba điều, và cả ba đổi thiết kế:

**1. Ngưỡng hợp lệ "MAE < 0,5" là ĐOÁN và SAI.** Đo bộ dự đoán hằng số: MAE ≈ 0,19 (hops), 0,17
(delay). Ngưỡng cũ cho qua cả mô hình không học gì. ⇒ Hợp lệ nay chỉ xét BỆNH LÝ HUẤN LUYỆN
(NaN, loss không giảm đơn điệu theo ba phần, giảm < 10%). "Có thắng hằng số không" là KẾT QUẢ,
in thành cột riêng, không bao giờ dùng để bỏ hàng.

**2. Mã cũ dùng `relu(t)`: t học được đi ÂM ở lớp 2-3** (heat [2.72, −0.15, −0.16], qw [0.87,
−0.04, −0.04]) ⇒ propagator = đơn vị, gradient chết, hai mô hình phổ chỉ lan truyền ở MỘT lớp.
⇒ Thêm tham số hoá `softplus(θ)`; giữ `relu` làm nhánh đối chứng.

**3. Thứ hạng toán tử ĐẢO theo cách tham số hoá và điểm khởi tạo t**, cùng seed cùng dữ liệu:

| nhánh | heat | qw |
|---|---|---|
| relu, t0=0,5 (mã cũ) | **0,104** | 0,163 |
| relu, t0=2,0 | 0,138 | **0,113** |
| softplus, t0=0,5 | 0,160 | **0,081** |
| softplus, t0=2,0 | 0,185 | 0,177 |

⇒ CLAIM được BỔ SUNG một mệnh đề, khai trước: *"Thứ hạng giữa heat và unitary trên đồ thị LEO
phụ thuộc vào tham số hoá và khởi tạo thời gian lan truyền t; bài đo cả bốn nhánh và chỉ tuyên
bố một thứ hạng ở quy mô nào nếu nó ĐỨNG VỮNG qua cả bốn nhánh (≥7/10 seed ở mỗi nhánh)."* Nếu
không nhánh nào cho thứ hạng ổn định thì phát hiện chính của bài là chính điều đó: **so sánh toán
tử phổ trên đồ thị LEO không xác định được nếu không kiểm soát t**, và kết quả 3-seed của bản
TNSE cũ là một ca cụ thể của hiện tượng ấy.

**Lưới đo cuối, khai trước:** 4 shell (264 · 1584 · 3168 · 4400) × 2 tác vụ (hops · delay) × 3
toán tử × 10 seed × 4 nhánh t = **960 ô**, mỗi ô n_train=8, n_eval=6, hidden=16, 3 lớp, 200
epoch. Chạy trên VPS, một lần, `OMP_NUM_THREADS=1`, song song theo ô. Mọi hàng giữ nguyên trong
CSV kể cả hàng không hợp lệ; số hàng không hợp lệ in cạnh mọi số headline.

**Một lệch mã/văn của bài cũ, sửa và khai:** mã chạy `seam=False` trong khi văn bản nói "seam cut".
Bài mới chạy `seam=True` và nói rõ. Shell 3168 và 4400 là **scale-up tổng hợp** của hình học
shell-1, không phải chòm thật; bài phải nói vậy.

## ⛔ BỔ SUNG 11/09/2026 14:40, sau 117/960 ô (chỉ s4400 xong), TRƯỚC khi có hàng s3168 nào

Ở s4400 cả ba toán tử nằm trong **0,001** của nhau và cách hằng số **0,0005** (hops: 0,1864 đến
0,1871 so với 0,187). Quy tắc "thắng = ≥7/10 seed" vẫn cho "heat thắng 9/10" bằng 0,0007 MAE.
Đó là hiện tượng SÀN: với 200 epoch, ở 4400 không toán tử nào học được gì.

⇒ Bổ sung **cách báo cáo**, không đổi giao thức chạy: một ô chỉ **xếp hạng được** khi toán tử tốt
nhất cải thiện ≥ **5%** so với hằng số (`FLOOR_GAIN`). Dưới đó in **FLOOR**, không tính là thắng.

⇒ Hệ quả đã thấy trước: nếu s3168 cũng FLOOR thì lưới 200 epoch chỉ xếp hạng được ở 264 và 1584,
và kết luận "phụ thuộc quy mô" KHÔNG rút ra được từ lưới này. Khi đó đề xuất một **nhánh epoch**
(600) cho s3168 và s4400, khai riêng trước khi chạy, KHÔNG chèn vào lưới đang chạy.

## ⛔ BỔ SUNG 11/09/2026 16:20, sau 480/960 ô lưới 1 (rộng 16, 3 lớp), TRƯỚC khi chạy lưới 2

**Phát hiện về hiện vật đã nộp của bản TNSE.** `exp_e_shell1.csv` đã nộp ghi `params=3301`, tức
mạng **rộng 32, 4 lớp** (2·32+32 + 3·(32·32+32) + 33 + 4 = 3301), khớp văn bản bài ("width 32").
Nhưng mã phát hành mặc định **rộng 16, 3 lớp** (`params=612`), và **không tồn tại script nào sinh
Exp E** trong repo, dù CSV của nó có. ⇒ Thí nghiệm headline "edge emerges at scale" của bản cũ
**không tái tạo được từ hiện vật phát hành**. Lưới 1 của bài này chạy cấu hình *phát hành*, nên
không tái tạo 0,148 ở 1584 là điều phải xảy ra chứ không phải mâu thuẫn.

**Kết quả lưới 1 (hai nhánh t0=0,5, 480 ô, 0 không hợp lệ):** chỉ **s264 xếp hạng được**
(cải thiện 18-29% so với hằng số); **từ s1584 trở lên là SÀN** (0,1-2,9%) ở cả hai tác vụ. Ở s264:
relu → hoà (heat 6/10), softplus → qw thắng 7-8/10, phương sai seed ±0,04.

⇒ **Lưới 2, khai trước:** giống lưới 1 nhưng **rộng 32, 4 lớp** (cấu hình bài cũ, 3301 tham số),
đủ 4 nhánh t, 960 ô, tệp riêng `results/scale_h32l4_<arm>.csv`. Mục đích: (a) kiểm xem 0,148 ở
1584 có tái tạo được ở đúng cấu hình không; (b) tách **dung lượng** khỏi **toán tử**: nếu lưới 2
học được ở 1584 còn lưới 1 không, thì sàn của lưới 1 là sàn dung lượng, đúng Pitfall 4 của bài cũ.
Ngân sách 200 epoch giữ nguyên để so được với bài cũ. Nhánh epoch (600) vẫn để sau, khai riêng.
