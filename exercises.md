# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng placeholder bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Kim Mạnh Hùng  Mã học viên: 2A202601679

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Nếu ta để mặc định `"changeme"`, ứng dụng vẫn khởi động bình thường trên môi trường Cloud khi chúng ta quên cấu hình biến `AGENT_API_KEY`. Lúc này, hệ thống sẽ chạy với API key mặc định, dẫn đến lỗ hổng bảo mật nghiêm trọng (bất kỳ ai cũng có thể dò ra hoặc sử dụng khóa mặc định `"changeme"` để gọi API) và khiến chúng ta mất tiền oan cho nhà cung cấp LLM mà không phát hiện kịp thời. Việc "chết sớm" (fail fast) giúp phát hiện lỗi thiếu cấu hình ngay lập tức trong quá trình deploy/khởi chạy giúp ngăn chặn rủi ro bảo mật này từ đầu.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Dòng log JSON thu được:
> `{"event": "ask_completed", "level": "info", "timestamp": "2026-08-10T02:46:52.684112+00:00", "user_id": "sv-test", "tokens_in": 43, "tokens_out": 47, "cost_usd": 3.465e-05}`
> Hai việc làm được:
> 1. Phân tích, tổng hợp và lọc dữ liệu tự động theo thời gian thực (ví dụ dùng Logstash, Datadog hoặc cloud logs để tính toán tổng chi phí `cost_usd` của từng user trong ngày/tháng).
> 2. Cài đặt hệ thống cảnh báo tự động (alerting) khi tỷ lệ lỗi tăng cao hoặc chi phí đột biến nhờ vào cấu trúc JSON chuẩn hóa giúp máy dễ parse và trích xuất trường.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.05 GB |
| Multi-stage | 148 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Phần dung lượng chênh lệch chính là các công cụ biên dịch (compilers), build tools, caches của pip, các file không cần thiết cho quá trình runtime và base image đầy đủ của Python (bản đầy đủ chứa nhiều thư viện hệ thống cồng kềnh) so với bản slim chỉ chứa runtime tối giản cần thiết để chạy ứng dụng.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> - Với Dockerfile hiện tại, các layer từ base image, cấu hình WORKDIR, COPY requirements.txt và RUN pip install đều được dùng lại từ cache vì file `requirements.txt` không đổi. Chỉ có layer COPY source code (`COPY app ./app`, `COPY utils ./utils`) và các layer sau đó là phải chạy lại.
> - Nếu đặt `COPY . .` trước `RUN pip install`, bất kỳ thay đổi nào trong source code (dù chỉ là 1 ký tự trong `app/main.py`) cũng sẽ làm mất cache ở layer `COPY`, buộc Docker phải chạy lại lệnh `RUN pip install` ở bước tiếp theo, làm chậm quá trình build đáng kể.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> - Chuỗi sự kiện: Kẻ tấn công khai thác một lỗ hổng thực thi mã từ xa (RCE) trong code Python -> Do container chạy bằng user `root`, kẻ tấn công có toàn quyền root bên trong container -> Kẻ tấn công sử dụng các kỹ thuật container breakout (khai thác kernel, mount socket docker, v.v.) để truy cập trực tiếp vào hệ điều hành host -> Do tiến trình container chạy dưới quyền root trên host, kẻ tấn công chiếm luôn quyền root của máy host.
> - Lệnh `USER appuser` cắt đứt chuỗi này ngay ở bước 2: khi kẻ tấn công thực thi mã trong container, họ chỉ có đặc quyền hạn chế của user thường (`appuser`), không thể thực hiện các thao tác can thiệp hệ thống hoặc container breakout thành công.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Tối đa 20 request. Người dùng gửi 10 request vào giây 59 của phút thứ nhất, sau đó gửi tiếp 10 request vào giây 01 của phút thứ hai. Vì hệ thống reset số đếm lúc giây 00, cả hai lượt gửi đều hợp lệ về mặt kỹ thuật, nhưng người dùng đã gửi tổng cộng 20 request chỉ trong 2 giây.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> - Rate limit giới hạn số lượng request trong một khoảng thời gian ngắn (tần suất). Cost guard giới hạn tổng số tiền (chi phí LLM token) đã chi tiêu trong cả tháng.
> - Tình huống Rate limit cho qua nhưng Cost guard chặn: User chỉ gửi 1 request trong phút (đạt yêu cầu rate limit), nhưng câu hỏi hoặc câu trả lời có dung lượng cực lớn (ví dụ 100k tokens), tiêu hết ngân sách tháng. Cost guard sẽ chặn request này.
> - Tình huống ngược lại: User gửi 20 request trong 10 giây, mỗi request cực ngắn chỉ tiêu tốn 1 token (tổng chi phí rất nhỏ và chưa vượt budget tháng). Cost guard cho qua, nhưng Rate limit sẽ chặn lại do vượt tần suất cho phép.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> 1. Redis mất kết nối.
> 2. Endpoint liveness probe (/health) của cả 3 container đồng loạt trả về lỗi 503 do gộp kiểm tra Redis.
> 3. Orchestrator coi cả 3 container đã chết (unhealthy) và tự động restart cả 3 container cùng lúc.
> 4. Khi các container khởi động lại, chúng lại tiếp tục gọi liveness probe và tiếp tục fail vì Redis vẫn chưa kết nối lại được, dẫn đến việc container bị khởi động lại liên tục trong vòng lặp vô hạn. Khi Redis kết nối lại, hệ thống không còn container nào sẵn sàng phục vụ ngay.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Nếu lưu trong dict Python (in-memory state), `history_length` sẽ thay đổi hỗn loạn hoặc tăng ngẫu nhiên, không đồng đều vì mỗi request được load balancer đẩy đến một trong ba container khác nhau. Mỗi container có một dict riêng nên lịch sử bị phân mảnh, lúc trả về độ dài 1, lúc 2, lúc lại 1.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Lỗi gặp phải: Lỗi `/ready` endpoint trả về 503 khi deploy lên cloud.
> Cách tìm ra nguyên nhân: Kiểm tra log của container ứng dụng thông qua terminal/dashboard, thấy thông báo lỗi ConnectionError không kết nối được tới `redis://localhost:6379/0`.
> Cách sửa: Thay đổi biến môi trường `REDIS_URL` trên dashboard của cloud platform để trỏ đúng tới địa chỉ Redis instance được cấp phát (ví dụ do Redis add-on sinh ra tự động) thay vì dùng localhost.
