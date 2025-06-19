<h1 align="center">🔐 Phishing-URL Detector</h1>

<p align="center">
   Bảo vệ bạn khỏi các website lừa đảo bằng thuận toán XGBoost trên trình duyệt Chrome!  
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/XGBoost-ML_Model-green?logo=scikit-learn" />
  <img src="https://img.shields.io/badge/Chrome%20Extension-Detect%20Phishing-orange?logo=googlechrome" />
  <img src="https://img.shields.io/github/license/lamtanhao12345/phishing-detector" />
</p>

---

## Giới thiệu

**Phishing-URL Detector** chính là giải pháp bạn đang tìm kiếm!  
Đây là một công cụ mạnh mẽ được thiết kế để phân tích và nhận diện các **URL lừa đảo**, giúp người dùng tránh xa những cạm bẫy trực tuyến.

>  Sức mạnh nằm ở mô hình học máy **XGBoost**, được tích hợp trực tiếp vào **trình duyệt Chrome** qua extension.

---

##  Huấn luyện Mô hình XGBoost

- **Bộ dữ liệu**: Sử dụng tập `PhiUSIIL Phishing URL Dataset`, gồm hàng ngàn URL hợp pháp và lừa đảo.
- **Tiền xử lý & Feature Engineering**:
   ✅ Loại bỏ trùng lặp & xử lý thiếu dữ liệu
   ✅ Loại bỏ cột không cần thiết: `FILENAME`, `URL`, `Domain`, `TLD`, `Title`
   ✅ Chuyển đổi kiểu dữ liệu: Boolean → số (0/1)
   ✅ Trích xuất đặc trưng từ URL: độ dài, số ký tự đặc biệt, HTTPS, IP domain, v.v.

---

## Tính năng chính

-  Phát hiện **website lừa đảo** trực tiếp từ URL người dùng truy cập
-  Mô hình **XGBoost** tích hợp với Flask Backend
-  Có sẵn mô hình **CatBoost**, **LightGBM** để so sánh
-  Extension Chrome thân thiện, xuất kết quả ngay khi duyệt web
-  Cung cấp API để tích hợp dễ dàng vào hệ thống khác

---


## 📁 Cấu trúc thư mục

| Thư mục / Tập tin              |               Mô tả                                         |
|--------------------------------|-------------------------------------------------------------|
| `data/`                        | Chứa dữ liệu huấn luyện và test                             |
| `backend_XGBoost/`             | Mô hình XGBoost                                             |
| `backend_CatBoost/`            | Mô hình CatBoost                                            |
| `backend_LightGBM/`            | Mô hình LightGBM                                            |
| `assets/`                      | Ảnh minh họa                                                |
| `extension/`                   | Source code của extension trình duyệt Chrome                |
| ├── `background.js`            | Background script của extension                             |
| ├── `content.js`               | Tương tác với nội dung trang web                            |
| ├── `icons.png`                | Icon cho extension                                          |
| ├── `manifest.json`            | Cấu hình extension Chrome                                   |
| ├── `model.js`                 | Tải mô hình dự đoán vào trình duyệt                         |
| ├── `popup.html / popup.css`   | Giao diện popup khi click icon extension                    |
| └── `popup.js`                 | Logic tương tác với giao diện popup                         |
| `Phishing_Model.ipynb`         | Jupyter Notebook huấn luyện mô hình                         |
| `requirements.txt`             | Thư viện cần thiết                                          |
| `README.md`                    | Tài liệu mô tả dự án                                        |


---

<table>
  <thead>
    <tr>
      <th> <b>Mục tiêu</b></th>
      <th> <b>Mô hình đề xuất</b></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Ưu tiên độ chính xác cao nhất</b></td>
      <td> <b>CatBoost</b></td>
    </tr>
    <tr>
      <td><b>Ưu tiên tốc độ xử lý, triển khai nhanh</b></td>
      <td> <b>LightGBM</b></td>
    </tr>
    <tr>
      <td><b>Cân bằng giữa hiệu suất & tính linh hoạt</b></td>
      <td> <b>XGBoost</b></td>
    </tr>
  </tbody>
</table>

##  Cài đặt & Sử dụng

<h3> Bước 1: Clone project</h3>
<pre><code>git clone https://github.com/lamtanhao12345/phishing-detector.git
cd phishing-detector
</code></pre>

<h3> Bước 2: Cài thư viện Python</h3>
<p><strong>Yêu cầu:</strong> Python 3.9 hoặc cao hơn</p>
<pre><code>pip install -r requirements.txt
</code></pre>

<h3> Bước 3: Thêm Extension vào Chrome</h3>
<ol>
  <li>Mở trình duyệt Chrome và vào <code>chrome://extensions</code></li>
  <li>Bật "Chế độ dành cho nhà phát triển"</li>
  <li>Chọn "Tải tiện ích đã giải nén"</li>
  <li>Chọn thư mục <code>extension/</code> trong dự án</li>
</ol>

<h3> Bước 4: Chạy Server XGBoost</h3>
<pre><code>python Server_XGBoot.py
</code></pre>

<p>Khi chạy thành công, API sẽ hoạt động tại:</p>
<pre><code>http://localhost:80</code></pre>

---
## Giao diện minh họa

<p align="center">
  <img src="https://raw.githubusercontent.com/lamtanhao12345/phishing-detector/main/assets/phishing.png" width="300" />
  <br>
  <em>🔴 Giao diện khi phát hiện URL lừa đảo</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/lamtanhao12345/phishing-detector/main/assets/safe.png" width="300" />
  <br>
  <em>🟢 Giao diện khi phát hiện URL an toàn</em>
</p>
