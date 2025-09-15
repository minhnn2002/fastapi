# 📑 Mục lục {#muc-luc}

- [Các API về content](#content)
  - [GET /content/ ](#get-content)
    - [Mô tả](#mo-ta-get-content)
    - [Tham số truy vấn](#tham-so-truy-van-get-content)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-get-content)
    - [Các trường phản hồi](#cac-truong-phan-hoi-get-content)
    - [Định dạng SMSGroupedContent](#dinh-dang-smsgroupedcontent)
  - [GET /content/export](#export-get-content)
    - [Mô tả](#mo-ta-export-get-content)
    - [Tham số truy vấn](#tham-so-truy-van-export-get-content)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-export-get-content)
  - [PUT /content/](#put-content)
    - [Mô tả](#mo-ta-put-content)
    - [Tham số truy vấn](#tham-so-truy-van-put-content)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-put-content)
    - [Các trường phản hồi](#cac-truong-phan-hoi-put-content)
- [Các API về frequency](#frequency)
  - [GET /frequency/ ](#get-frequency)
    - [Mô tả](#mo-ta-get-frequency)
    - [Tham số truy vấn](#tham-so-truy-van-get-frequency)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-get-frequency)
    - [Các trường phản hồi](#cac-truong-phan-hoi-get-frequency)
    - [Định dạng SMSGroupedFrequency](#dinh-dang-smsgroupedfrequency)
  - [GET /frequency/export](#export-get-frequency)
    - [Mô tả](#mo-ta-export-get-frequency)
    - [Tham số truy vấn](#tham-so-truy-van-export-get-frequency)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-export-get-frequency)
  - [PUT /frequency/](#put-frequency)
    - [Mô tả](#mo-ta-put-frequency)
    - [Tham số truy vấn](#tham-so-truy-van-put-frequency)
    - [Ví dụ phản hồi](#vi-du-phan-hoi-put-frequency)
    - [Các trường phản hồi](#cac-truong-phan-hoi-put-frequency)
---

# Các API về content {#content}
## GET /content/ {#get-content}
### Mô tả {#mo-ta-get-content}
API này tiến hành lọc dựa trên thời gian (**giới hạn 1 giờ**), nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id` và `sdt_in`, sau đó tính toán tần suất nhắn tin. Chỉ những (`group_id`, `sdt_in`) có **tần suất lớn hơn 20(SMS/h)** mới được hiển thị.

### Tham số truy vấn {#tham-so-truy-van-get-content}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng ISO format.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng ISO format.          |
| page           | int      | Không    | Số thứ tự của trang (≥ 0).  Mặc định là `0`.                             |
| page_size      | int      | Không    | Số bản ghi trên mỗi trang. Giá trị cho phép: `10`, `50`, `100`. Mặc định là `10`.           |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |
| phone_num      | string   | Không    | Lọc số điện thoại khớp với mẫu này (không phân biệt hoa thường). |

### Lưu ý
- Khoảng thời gian giữa `to_datetime` và `from_datetime` phải nằm trong khoảng 1 giờ đồng hồ đổ lại, nếu không sẽ có thông báo lỗi được trả về.
- Nếu thời gian không được cung cấp, hệ thống sẽ tự động lọc theo 1 giờ đồng hồ gần nhất.
- Nếu `from_datetime` không được cung cấp thì `from_datetime` sẽ được tính bằng `to_datetime - 1h`.
- Nếu `to_datetime` không được cung cấp thì `to_datetime` sẽ được tính bằng `from_datetime + 1h`. 

### Ví dụ phản hồi {#vi-du-phan-hoi-get-content}

```json
{
    "status_code": 200,
    "message": "Success",
    "error": false,
    "error_message": "",
    "data": [
        {
            "stt": 1,
            "group_id": "group_n0U2_1755225977",
            "frequency": 32,
            "ts": "2025-09-04T04:20:46",
            "agg_message": "2GOE Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
            "sdt_in": "9212DEF244091507FB332AAF6E2717E6",
            "messages": [
                {
                    "text_sms": "Z56D Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                {
                    "text_sms": "B92A Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                {
                    "text_sms": "IR9I Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                {
                    "text_sms": "W5X0 Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                {
                    "text_sms": "DHLC Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                {
                    "text_sms": "OFIM Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
                    "count": 1
                },
                ...
            ]
        },
        {
            "stt": 2,
            "group_id": "group_mY5T_1755226210",
            "frequency": 20,
            "ts": "2025-09-04T04:20:46",
            "agg_message": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1167 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
            "sdt_in": "64B1FB8FB33E2183479027EBF2632363",
            "messages": [
                {
                    "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A2957 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
                    "count": 1
                },
                {
                    "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1841 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
                    "count": 1
                },
                {
                    "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A344 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
                    "count": 1
                },
                {
                    "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1901 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
                    "count": 1
                },
                ...
            ]
        },
        ...
    ],
    "page": 0,
    "limit": 10,
    "total": 3062
}
```

### Các trường phản hồi{#cac-truong-phan-hoi-get-content}

| Trường           | Kiểu                           | Mô tả |
|------------------|--------------------------------|-------|
| `status_code`    | `int`                          | Mã trạng thái HTTP (200, 400, 404,...). |
| `message`        | `str`                | Thông báo phản hồi. |
| `data`           | `list[SMSGroupedContent] hoặc null` | Kết quả dữ liệu chính. |
| `error`          | `bool`                         | Có lỗi hay không. |
| `error_message`  | `str hoặc null`                | Mô tả lỗi nếu có. |
| `page`           | `int`                          | Trang hiện tại. |
| `limit`          | `int`                          | Số bản ghi trên mỗi trang. |
| `total`          | `int`                          | Tổng số bản ghi khớp. |

### Định dạng SMSGroupedContent {#dinh-dang-smsgroupedcontent}

```json
"stt": 2,
"group_id": "group_mY5T_1755226210",
"frequency": 20,
"ts": "2025-09-04T04:20:46",
"agg_message": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1167 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
"sdt_in": "64B1FB8FB33E2183479027EBF2632363",
"messages": [
    {
        "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A2957 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
        "count": 1
    },
    {
        "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1841 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
        "count": 1
    },
    {
        "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1197 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
        "count": 1
    },
    {
        "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A1901 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
        "count": 1
    },
    {
        "text_sms": "99Vin LongSG hotline:0362.777.777. GDMuabanMomo/atm100=120k code ( LSG08M09A135 ) NhanQuatai http://irjrwe.site/r/21V2gKZO9t ",
        "count": 1
    },
    ...
```

| Trường           | Kiểu                     | Mô tả |
|------------------|--------------------------|-------|
| `stt`            | `int`                      | Số thứ tự. |
| `group_id`       | `str`                      | ID của nhóm. |
| `sdt_in`         | `str`                      | Số điện thoại đã gửi tin nhắn. |
| `frequency`      | `int`                      | Số lượng tin nhắn mà 1 số điện thoại đã gửi trong nhóm `group_id`. |
| `ts`             | `datetime`    | Thời điểm tin nhắn đầu tiên được gửi trong nhóm bởi số điện thoại `sdt_in`.|
| `agg_message`             | `str`    | Tin nhắn tổng hợp.|
| `messages` | `list` | Danh sách các tin nhắn đã gửi trong nhóm của số điện thoại `sdt_in`. |
| `text_sms`        | `str`                      | Nội dung tin nhắn. |
| `count`          | `int`                      | Tần suất của mỗi `text_sms`. |

---

## GET /content/export {#export-get-content}
### Mô tả {#mo-ta-export-get-content}
API này tiến hành lọc dựa trên thời gian (**giới hạn 1 giờ**), nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id` và `sdt_in`, sau đó tính toán tần suất nhắn tin. Chỉ những (`group_id`, `sdt_in`) có **tần suất lớn hơn 20(SMS/h)** mới được giữ lại và xuất ra dưới dạng file csv để người dùng có thể download.
### Tham số truy vấn {#tham-so-truy-van-export-get-content}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng ISO format.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng ISO format.                      |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |
| phone_num      | string   | Không    | Lọc số điện thoại khớp với mẫu này (không phân biệt hoa thường). |

### Lưu ý
- Khoảng thời gian giữa `to_datetime` và `from_datetime` phải nằm trong khoảng 1 giờ đồng hồ đổ lại, nếu không sẽ có thông báo lỗi được trả về.
- Nếu thời gian không được cung cấp, hệ thống sẽ tự động lọc theo 1 giờ đồng hồ gần nhất.
- Nếu `from_datetime` không được cung cấp thì `from_datetime` sẽ được tính bằng `to_datetime - 1h`.
- Nếu `to_datetime` không được cung cấp thì `to_datetime` sẽ được tính bằng `from_datetime + 1h`. 

### Ví dụ phản hồi {#vi-du-phan-hoi-export-get-content}
Tệp csv chứa nội dung yêu cầu sẽ được tải về máy người dùng.

---

## PUT /content/ {#put-content}

### Mô tả {#mo-ta-put-content}
API này được sử dụng để gửi phản hồi từ người dùng. Dựa trên tần suất nhắn tin và nội dung nhắn tin của (`group_id`, `sdt_in`), người dùng sẽ đánh giá xem (`group_id`, `sdt_in`) có phải spam hay không.


### Tham số truy vấn {#tham-so-truy-van-put-content}

| Tên            | Kiểu     | Bắt buộc | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| feedback       | bool     | Có    | Phản hồi của người dùng: True (Spam) hoặc False (Không phải Spam).         |
| group_id       | str     | Có    | ID của nhóm.         |
| sdt_in         | str      | Có    | Số điện thoại mà người dùng muốn đánh giá.            |




### Ví dụ phản hồi {#vi-du-phan-hoi-4}

```json
{
  "status_code": 200,
  "message": "Updated 4 records",
  "error": false,
  "error_message": null
}
```

### Các trường phản hồi{#cac-truong-phan-hoi-put-content}

| Trường           | Kiểu                           | Mô tả |
|------------------|--------------------------------|-------|
| `status_code`    | `int`                          | Mã trạng thái HTTP (ví dụ: 200, 400, 404). |
| `message`        | `str`                | Thông báo số bản ghi được cập nhật thành công. |
| `error`          | `bool`                         | Có lỗi hay không. |
| `error_message`  | `str hoặc null`                | Mô tả lỗi nếu có. |

---
---
# Các API về frequency {#frequency}
## GET /frequency/ {#get-frequency}
### Mô tả {#mo-ta-get-frequency}
API này tiến hành lọc dựa trên thời gian (**giới hạn 1 giờ**) và nội dung tin nhắn. Sau đó tiến hành nhóm theo `group_id`, sau đó tính toán tần suất nhắn tin. Chỉ những `group_id` có **tần suất lớn hơn 20(SMS/h)** mới được hiển thị.

### Tham số truy vấn {#tham-so-truy-van-get-frequency}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng ISO format. Mặc định là mốc thời gian tối thiểu trong cơ sở dữ liệu.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng ISO format. Mặc định là mốc thời gian tối đa trong cơ sở dữ liệu.                        |
| page           | int      | Không    | Số thứ tự của trang (≥ 0).  Mặc định là `0`.                             |
| page_size      | int      | Không    | Số bản ghi trên mỗi trang. Giá trị cho phép: `10`, `50`, `100`. Mặc định là `10`.           |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |


 

### Ví dụ phản hồi {#vi-du-phan-hoi-get-frequency}

```json
{
  "status_code": 200,
  "message": "Success",
  "error": false,
  "error_message": "",
  "data": [
        {
            "stt": 1,
            "group_id": "group_zs7C_1755500059",
            "frequency": 5973,
            "ts": "2025-09-04T04:20:46",
            "agg_message":"0lq Chuc mung quy höi vien da nhån duoc Çde tri an 899k  truy cap: bit.ly/3BBBjDd t-nghiem TX,sIöt sieu nö,bäÇarät,tlmn..x3 nap lan dau, nap rut 1:1",
            "messages": [
                {
                    "text_sms": "TANG BAN 188K KHI DANGKY TAIKHOAN 88UU KHUYENMAI cuckhung banca,nohu. thuonglon den 15trieu. Lienhe CSKH denhan code: https://nhancode.online/j94e5   MVmUt",
                    "count": 1
                },
                {
                    "text_sms": "560+1260=thu 1820",
                    "count": 1
                },
                {
                    "text_sms": "ԀϪȁOk e, mai anh cho rút ống, khi nào chú em muốn về anh cho về, mổ nộ",
                    "count": 1
                },
                {
                    "text_sms": "WP/F0 0 20220906000903 Lat N 16.57481 deg Lon E 107.89458 deg Alt 7m 13Km/h 2022/09/06 00:09:03 Z",
                    "count": 1
                },
                ...
        },
        {
            "stt": 2,
            "group_id": "group_WKvV_1755226270",
            "frequency": 8446,
            "ts": "2025-09-04T04:20:46",
            "agg_message": "0G2I Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
            "messages": [
                {
                    "text_sms": "BONG90 DK nhan 300k,Napdau 210%.LiveCasino,T.Thao,Daga,Xoso,NoHu Hoantra sieu cao 1.75%. Lixi nguoi choi 3TR dau thang! https://bom.so/BONG90-01  GLoyi",
                    "count": 1
                },
                {
                    "text_sms": "TDTCgamePHOM,XOSO,TAlXlU,XocdiaTLMN,naprut1:1,tagCode: fp2dp3g03jli thuogtoi8888k,chucban trungthu Vve,event nhan88k.tele: thienduongtrochoi2022 .DK: tdtc3.com",
                    "count": 2
                },
                {
                    "text_sms": "Boc Fun Tang ban code ngau nhien tu 10k den 500k , nap km 125% , choi tai xiu lo de bong da, ma là: A1 http://boc2.fun  pfLuU",
                    "count": 1
                },
                {
                    "text_sms": "Ԁ̖؄hấy quán Chay Garden thì số 54 ở cạnh đó) Xe máy đi thẳng vào để dư",
                    "count": 1
                },
                {
                    "text_sms": "Ԁ̼̃ có ác. ",
                    "count": 1
                },
                {
                    "text_sms": "ԀίԂ anh lại một mk khi hong có dợ..hong có dợ òi anh hạnh phúc vs ai ",
                    "count": 1
                },
                {
                    "text_sms": "TANG BAN 188K KHI DANGKY TAIKHOAN 88UU KHUYENMAI cuckhung banca,nohu. thuonglon den 15trieu. Lienhe CSKH denhan code: https://nhancode.online/j94e5   OWSQr",
                    "count": 1
                }
        }

  ],
  "page": 0,
  "limit": 100,
  "total": 750
}
```

### Các trường phản hồi{#cac-truong-phan-hoi-get-frequency}

| Trường           | Kiểu                           | Mô tả |
|------------------|--------------------------------|-------|
| `status_code`    | `int`                          | Mã trạng thái HTTP (200, 400, 404,...). |
| `message`        | `str`                | Thông báo phản hồi. |
| `data`           | `list[SMSGroupedFrequency] hoặc null` | Kết quả dữ liệu chính. |
| `error`          | `bool`                         | Có lỗi hay không. |
| `error_message`  | `str hoặc null`                | Mô tả lỗi nếu có. |
| `page`           | `int`                          | Trang hiện tại. |
| `limit`          | `int`                          | Số bản ghi trên mỗi trang. |
| `total`          | `int`                          | Tổng số bản ghi khớp. |

### Định dạng SMSGroupedFrequency {#dinh-dang-smsgroupedfrequency}

```json
"stt": 2,
"group_id": "group_WKvV_1755226270",
"frequency": 8446,
"ts": "2025-09-04T04:20:46",
"agg_message": "0G2I Çhuc mung quy höi vien da nhån duoc c;;de tri ån 899k truy cåp: bit.ly/3QuRHJM T-nghiem Tai_xiu, S()lt,sieu_NT,baÇarät,tlmn.. x3 nap_lån dåu, nap rut 1:1",
"messages": [
    {
        "text_sms": "BONG90 DK nhan 300k,Napdau 210%.LiveCasino,T.Thao,Daga,Xoso,NoHu Hoantra sieu cao 1.75%. Lixi nguoi choi 3TR dau thang! https://bom.so/BONG90-01  GLoyi",
        "count": 1
    },
    {
        "text_sms": "TDTCgamePHOM,XOSO,TAlXlU,XocdiaTLMN,naprut1:1,tagCode: fp2dp3g03jli thuogtoi8888k,chucban trungthu Vve,event nhan88k.tele: thienduongtrochoi2022 .DK: tdtc3.com",
        "count": 2
    },
    {
        "text_sms": "Boc Fun Tang ban code ngau nhien tu 10k den 500k , nap km 125% , choi tai xiu lo de bong da, ma là: A1 http://boc2.fun  pfLuU",
        "count": 1
    },
    {
        "text_sms": "Ԁ̖؄hấy quán Chay Garden thì số 54 ở cạnh đó) Xe máy đi thẳng vào để dư",
        "count": 1
    },
    {
        "text_sms": "Ԁ̼̃ có ác. ",
        "count": 1
    },
    {
        "text_sms": "ԀίԂ anh lại một mk khi hong có dợ..hong có dợ òi anh hạnh phúc vs ai ",
        "count": 1
    },
    {
        "text_sms": "TANG BAN 188K KHI DANGKY TAIKHOAN 88UU KHUYENMAI cuckhung banca,nohu. thuonglon den 15trieu. Lienhe CSKH denhan code: https://nhancode.online/j94e5   OWSQr",
        "count": 1
    }
```

| Trường           | Kiểu                     | Mô tả |
|------------------|--------------------------|-------|
| `stt`            | `int`                      | Số thứ tự. |
| `group_id`       | `str`                      | ID của nhóm. |
| `frequency`      | `int`                      | Số lượng tin nhắn đã gửi trong nhóm `group_id`. |
| `ts`             | `datetime`    | Thời điểm tin nhắn đầu tiên được gửi trong nhóm.|
| `agg_message`             | `str`    | Tin nhắn tổng hợp.|
| `messages` | `list` | Danh sách các tin nhắn đã gửi trong nhóm. |
| `text_sms`        | `str`                      | Nội dung tin nhắn. |
| `count`          | `int`                      | Tần suất của mỗi `text_sms`. |


### Lưu ý
- Khoảng thời gian giữa `to_datetime` và `from_datetime` phải nằm trong khoảng 1 giờ đồng hồ đổ lại, nếu không sẽ có thông báo lỗi được trả về.
- Nếu thời gian không được cung cấp sẽ tự động lấy 1 giờ đồng hồ gần nhất.
- Nếu `from_datetime` không được cung cấp thi `from_datetime` sẽ được tính bằng `to_datetime - 1h`. 
- Nếu `to_datetime` không được cung cấp thi `to_datetime` sẽ được tính bằng `from_datetime + 1h`. 
---

## GET /frequency/export {#export-get-frequency}
### Mô tả {#mo-ta-export-get-frequency}
API này tiến hành lọc dựa trên thời gian (**giới hạn 1 giờ**) và nội dung tin nhắn. Sau đó tiến hành nhóm theo `group_id`, sau đó tính toán tần suất nhắn tin. Chỉ những `group_id` có **tần suất lớn hơn 20(SMS/h)** mới được giữ lại và xuất ra dưới dạng file csv để người dùng có thể download.

### Tham số truy vấn {#tham-so-truy-van-export-get-frequency}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng ISO format.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng ISO format.                      |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |

### Lưu ý
- Khoảng thời gian giữa `to_datetime` và `from_datetime` phải nằm trong khoảng 1 giờ đồng hồ đổ lại, nếu không sẽ có thông báo lỗi được trả về.
- Nếu thời gian không được cung cấp sẽ tự động lấy 1 giờ đồng hồ gần nhất.
- Nếu `from_datetime` không được cung cấp thi `from_datetime` sẽ được tính bằng `to_datetime - 1h`. 
- Nếu `to_datetime` không được cung cấp thi `to_datetime` sẽ được tính bằng `from_datetime + 1h`. 

### Ví dụ phản hồi {#vi-du-phan-hoi-export-get-frequency}
Tệp csv chứa nội dung yêu cầu sẽ được tải về máy người dùng.

---

## PUT /frequency/ {#put-frequency}

### Mô tả {#mo-ta-put-frequency}
API này được sử dụng để gửi phản hồi từ người dùng, giúp họ đánh giá liệu một nhóm có phải là spam hay không dựa trên nội dung tin nhắn được gửi trong nhóm.

### Tham số truy vấn {#tham-so-truy-van-put-frequency}

| Tên            | Kiểu     | Bắt buộc | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| feedback       | bool     | Có    | Phản hồi của người dùng: True (Spam) hoặc False (Không phải Spam).         |
| group_id       | str     | Có    | ID của nhóm.         |           |




### Ví dụ phản hồi {#vi-du-phan-hoi-put-frequency}

```json
{
  "status_code": 200,
  "message": "Updated 4 records",
  "error": false,
  "error_message": null
}
```

### Các trường phản hồi{#cac-truong-phan-hoi-put-frequency}

| Trường           | Kiểu                           | Mô tả |
|------------------|--------------------------------|-------|
| `status_code`    | `int`                          | Mã trạng thái HTTP (ví dụ: 200, 400, 404). |
| `message`        | `str`                | Thông báo số bản ghi được cập nhật thành công. |
| `error`          | `bool`                         | Có lỗi hay không. |
| `error_message`  | `str hoặc null`                | Mô tả lỗi nếu có. |
