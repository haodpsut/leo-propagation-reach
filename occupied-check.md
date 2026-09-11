OCCUPIED-CHECK
DATE: 2026-09-11
DIRECTION: do thu hang ba toan tu lan truyen (GCN / heat / unitary) tren do thi LEO theo QUY MO chom, param-matched, >=10 seed, hai tac vu. Sau REFRAME: co che unitary da bi chiem, chi con boi canh + hien tuong theo quy mo
QUERY: arXiv API | all:"quantum walk" AND all:"graph neural" | 4 bai, moi nhat 2608.20738 (08/2026) va 2605.09486 (05/2026) | 2026-09-11
QUERY: arXiv API | all:"quantum walk" AND all:satellite | 0 bai | 2026-09-11
QUERY: arXiv API | all:"graph neural" AND all:satellite AND all:constellation | 8 bai, gan nhat 2601.21921 (DeepLaDu), 2604.27478, 2606.31950 | 2026-09-11
QUERY: OpenAlex | ISSN 2327-4697 (TNSE) + "quantum-inspired" | 13 bai, trong do GraphQWalk 10.1109/tnse.2025.3644803 | 2026-09-11
QUERY: OpenAlex | ISSN 2327-4697 + "LEO constellation routing" | 8 bai, 3 bai 2024 | 2026-09-11
NOTE: OpenAlex tim toan van rat mo (tra ve survey PSO cho "quantum walk GNN"), chi doc duoc theo chieu am. arXiv la nguon chinh xac cho co che.
NEAREST: arXiv:2608.20738 CTQW-GNN | 2026-08 | GNN dung propagator unitary e^{-iHt}, CHUNG MINH: khong tat tan so, nang luong Dirichlet khong suy giam ⇒ chong over-smoothing, tren benchmark heterophilic chuan | ⛔ CHIEM CO CHE. Bai cua toi KHONG duoc nhan co che la dong gop; phai trich no lam nguon co che. Con trong: do thi LEO dong, xu huong theo quy mo, giao thuc param-matched da seed
NEAREST: arXiv:2605.09486 CTQWformer | 2026-05 | CTQW voi Hamiltonian hoc duoc + Transformer, phan lop do thi | khac tac vu (phan lop do thi), khac boi canh; chi can trich
NEAREST: 10.1109/tnse.2025.3644803 GraphQWalk (TNSE) | 2025 | CTQW → structural node embedding khong giam sat | cung cong cu, khac cau hoi; la TIEN LE VENUE, phai trich
NEAREST: arXiv:2601.21921 DeepLaDu | 2026-01 | GNN suy gia tac nghen tung lien ket cho LEO mega-constellation | cung boi canh LEO, khac cau hoi (dinh tuyen duoi tai; do la mien cua TNSM). Bai nay khong dung tai
NEAREST: GraphCON (Rusch, ICML 2022) va PDE-GCN (Eliasof, NeurIPS 2021) | 2021-2022 | GNN theo phuong trinh song, lan xa hon khuech tan | cung y "wave vs heat"; bai cu KHONG trich, bai moi phai trich va so sanh trong related work
OWN: TNSM-2026-11591 | IEEE TNSM | under review (nop lai 28/08) | partial | cung boi canh GNN-LEO, KHAC cau hoi (tai vs lan truyen), KHONG dung chung ma/du lieu/hinh. Khai trong bai. Ban v1 cua TNSM tung la QW-GNN va bao am tren tac vu dinh tuyen: bai nay phai giai thich vi sao khac tac vu
OWN: COMNET-D-26-06613 | Computer Networks | With Editor | none | mien khac (semantic comm)
OWN: TNSESITD-2026-06-2033 | TNSE SI | rejected 2026-09-10 | partial | chinh la bai me; bai moi tai su dung ma va mot phan ket qua, KHONG tai su dung van ban tutorial/survey
VERDICT: GO
