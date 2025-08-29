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
API này tiến hành lọc dựa trên thời gian, nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id` và sau đó là `sdt_in`.

### Tham số truy vấn {#tham-so-truy-van-get-content}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng `YYYY-MM-DD HH:MM:SS`. Mặc định là mốc thời gian tối thiểu trong cơ sở dữ liệu.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng `YYYY-MM-DD HH:MM:SS`. Mặc định là mốc thời gian tối đa trong cơ sở dữ liệu.                        |
| page           | int      | Không    | Số thứ tự của trang (≥ 0).  Mặc định là `0`.                             |
| page_size      | int      | Không    | Số bản ghi trên mỗi trang. Giá trị cho phép: `10`, `50`, `100`. Mặc định là `10`.           |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |
| phone_num      | string   | Không    | Lọc số điện thoại khớp với mẫu này (không phân biệt hoa thường). |

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
      "group_id": "group_073q_1755225954",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "D15",
      "sdt_in": "58739E9926D3A2B7C1A029B3B1351938",
      "messages": [
        {
          "text_sms": "D15",
          "count": 1
        }
      ]
    },
    {
      "stt": 2,
      "group_id": "group_0DJx_1755226161",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "ԀϨ̂ trả  bớt.   Rồi  cha mượn lại bữa  đóng  Ngân hàng.  Nay vợ  trả",
      "sdt_in": "EF0F86331EC0891F137AB97191333E4E",
      "messages": [
        {
          "text_sms": "ԀϨ̂ trả  bớt.   Rồi  cha mượn lại bữa  đóng  Ngân hàng.  Nay vợ  trả",
          "count": 1
        }
      ]
    },
    {
      "stt": 3,
      "group_id": "group_0DgB_1755226051",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "vậy nha, chúc anh và ny tương phùng và sớm lại có hỷ.",
      "sdt_in": "1761C7B0777D388605E12DC6A2E263B6",
      "messages": [
        {
          "text_sms": "vậy nha, chúc anh và ny tương phùng và sớm lại có hỷ.",
          "count": 1
        }
      ]
    },
    {
      "stt": 4,
      "group_id": "group_0G21_1755226590",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "Dạ, có gì con nhờ ông đó với ạ,",
      "sdt_in": "EC1ACBE0AF94E90ADEB3A6C21BAE816B",
      "messages": [
        {
          "text_sms": "Dạ, có gì con nhờ ông đó với ạ,",
          "count": 1
        }
      ]
    },
    {
      "stt": 5,
      "group_id": "group_0SXC_1755226198",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "có gì đâu a ai cũng có lúc khổ mà",
      "sdt_in": "A1FB46E6022791D98424105D61F609FA",
      "messages": [
        {
          "text_sms": "có gì đâu a ai cũng có lúc khổ mà",
          "count": 1
        }
      ]
    },
    {
      "stt": 6,
      "group_id": "group_0VuH_1755225948",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "Di e a dag o sao nè",
      "sdt_in": "0BE31CBF8C51F328CEE3004E7E0D57B9",
      "messages": [
        {
          "text_sms": "Di e a dag o sao nè",
          "count": 1
        }
      ]
    },
    {
      "stt": 7,
      "group_id": "group_0tGO_1755225931",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "Vâng.",
      "sdt_in": "EF953B119E02C5B3E3DE87CA0F8A0D44",
      "messages": [
        {
          "text_sms": "Vâng.",
          "count": 1
        }
      ]
    },
    {
      "stt": 8,
      "group_id": "group_0xfy_1755226045",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "Vd14912t 0911899663",
      "sdt_in": "BEB241379DE340F36071F4C6F26B7268",
      "messages": [
        {
          "text_sms": "Vd14912t 0911899663",
          "count": 1
        }
      ]
    },
    {
      "stt": 9,
      "group_id": "group_10Pt_1755226051",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "VNN G10 NAP50 SOV98837832",
      "sdt_in": "AB7C4F1CE966368ED0FE70A1EAB1ED8C",
      "messages": [
        {
          "text_sms": "VNN G10 NAP50 SOV98837832",
          "count": 1
        }
      ]
    },
    {
      "stt": 10,
      "group_id": "group_1Be3_1755225960",
      "frequency": 1,
      "ts": "2025-08-14T11:03:27",
      "agg_message": "Ah hôm qua c nhận rồi ah. Thèn cu e kia nó đưa mà ko nói e",
      "sdt_in": "EE38DC83AD7F018300EEC3FC803799B4",
      "messages": [
        {
          "text_sms": "Ah hôm qua c nhận rồi ah. Thèn cu e kia nó đưa mà ko nói e",
          "count": 1
        }
      ]
    }
  ],
  "page": 0,
  "limit": 10,
  "total": 3441
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
{
  "stt": 1,
  "group_id": "group_073q_1755225954",
  "frequency": 1,
  "ts": "2025-08-14T11:03:27",
  "agg_message": "D15",
  "sdt_in": "58739E9926D3A2B7C1A029B3B1351938",
  "messages": [
    {
      "text_sms": "D15",
      "count": 1
    }
  ]
}
```

| Trường           | Kiểu                     | Mô tả |
|------------------|--------------------------|-------|
| `stt`            | `int`                      | Số thứ tự. |
| `group_id`       | `str`                      | ID của nhóm. |
| `sdt_in`         | `str`                      | Số điện thoại đã gửi tin nhắn. |
| `frequency`      | `int`                      | Số lượng tin nhắn mà 1 số điện thoại đã gửi trong nhóm `group_id`. |
| `ts`             | `datetime`    | Thời điểm tin nhắn đầu tiên được gửi trong nhóm bởi số điện thoại `sdt_in`.|
| `messages` | `list` | Danh sách các tin nhắn đã gửi trong nhóm của số điện thoại `sdt_in`. |
| `text_sms`        | `str`                      | Nội dung tin nhắn. |
| `count`          | `int`                      | Tần suất của mỗi `text_sms`. |

---

## GET /content/export {#export-get-content}
### Mô tả {#mo-ta-export-get-content}
API này tiến hành lọc dựa trên thời gian (**giới hạn 1 giờ**), nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id` và sau đó là `sdt_in` rồi xuất ra dưới dạng file csv để người dùng có thể download.

### Tham số truy vấn {#tham-so-truy-van-export-get-content}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng `YYYY-MM-DD HH:MM:SS`.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng `YYYY-MM-DD HH:MM:SS`.                      |
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
API này được sử dụng để gửi phản hồi từ người dùng, giúp họ đánh giá liệu một số điện thoại có phải là spam hay không dựa trên nội dung tin nhắn của từng số điện thoại trong từng nhóm.


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
API này tiến hành lọc các bản ghi dựa trên thời gian, nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id`.

### Tham số truy vấn {#tham-so-truy-van-get-frequency}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng `YYYY-MM-DD HH:MM:SS`. Mặc định là mốc thời gian tối thiểu trong cơ sở dữ liệu.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng `YYYY-MM-DD HH:MM:SS`. Mặc định là mốc thời gian tối đa trong cơ sở dữ liệu.                        |
| page           | int      | Không    | Số thứ tự của trang (≥ 0).  Mặc định là `0`.                             |
| page_size      | int      | Không    | Số bản ghi trên mỗi trang. Giá trị cho phép: `10`, `50`, `100`. Mặc định là `10`.           |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |
| phone_num      | string   | Không    | Lọc số điện thoại khớp với mẫu này (không phân biệt hoa thường). |

 

### Ví dụ phản hồi {#vi-du-phan-hoi-get-frequency}

```json
{
  "status_code": 200,
  "message": "Success",
  "error": false,
  "error_message": "",
  "data": [
    {
      "stt": 11,
      "group_id": "group_wIoD_1755504016",
      "frequency": 1,
      "ts": "2025-08-27T11:30:48",
      "agg_message": "ԀϘԄ,có ý kiến thẳng thắn a nói đúng hay sai,kg phải e ngại gì hết...a ",
      "messages": [
        {
          "text_sms": "ԀϘԄ,có ý kiến thẳng thắn a nói đúng hay sai,kg phải e ngại gì hết...a ",
          "count": 1
        }
      ]
    },
    {
      "stt": 12,
      "group_id": "group_wK7L_1755518406",
      "frequency": 1,
      "ts": "2025-08-27T11:30:48",
      "agg_message": "Ԁ̬ЃC nói con mụ bán thất đức vừa thôi, cái trái nhỏ non, E k nói điêu ",
      "messages": [
        {
          "text_sms": "Ԁ̬ЃC nói con mụ bán thất đức vừa thôi, cái trái nhỏ non, E k nói điêu ",
          "count": 1
        }
      ]
    },
    {
      "stt": 13,
      "group_id": "group_wNLs_1755225954",
      "frequency": 12,
      "ts": "2025-08-27T11:30:12",
      "agg_message": "DATAKM",
      "messages": [
        {
          "text_sms": "DATAKM",
          "count": 11
        },
        {
          "text_sms": " DATAKM ",
          "count": 1
        }
      ]
    },
    {
      "stt": 14,
      "group_id": "group_wQqz_1755516009",
      "frequency": 1,
      "ts": "2025-08-27T11:30:18",
      "agg_message": "từ nay k cần phải đau đầu lên kịch bản và diễn nữa đâu.",
      "messages": [
        {
          "text_sms": "từ nay k cần phải đau đầu lên kịch bản và diễn nữa đâu.",
          "count": 1
        }
      ]
    },
    {
      "stt": 15,
      "group_id": "group_wRfq_1755226130",
      "frequency": 1,
      "ts": "2025-08-27T11:30:13",
      "agg_message": "Chiều e xuống chị đưa ",
      "messages": [
        {
          "text_sms": "Chiều e xuống chị đưa ",
          "count": 1
        }
      ]
    },
    {
      "stt": 16,
      "group_id": "group_wU4G_1755551409",
      "frequency": 1,
      "ts": "2025-08-27T11:30:38",
      "agg_message": "A k ngi như za a nag ni cầu xin e mới chịu gap ",
      "messages": [
        {
          "text_sms": "A k ngi như za a nag ni cầu xin e mới chịu gap ",
          "count": 1
        }
      ]
    },
    {
      "stt": 17,
      "group_id": "group_wX0G_1755587710",
      "frequency": 1,
      "ts": "2025-08-27T11:30:12",
      "agg_message": "DCB:ZCCB2VVHU1SEA9QUIHBR9NVKQVOPQ12RL",
      "messages": [
        {
          "text_sms": "DCB:ZCCB2VVHU1SEA9QUIHBR9NVKQVOPQ12RL",
          "count": 1
        }
      ]
    },
    {
      "stt": 18,
      "group_id": "group_wXES_1755514809",
      "frequency": 1,
      "ts": "2025-08-27T11:30:44",
      "agg_message": "Ԁό́Chào chị. Em bên phòng khám Dr.Nguyễn. Đã tới lịch điều trị tiếp củ",
      "messages": [
        {
          "text_sms": "Ԁό́Chào chị. Em bên phòng khám Dr.Nguyễn. Đã tới lịch điều trị tiếp củ",
          "count": 1
        }
      ]
    },
    {
      "stt": 19,
      "group_id": "group_wYmz_1755226170",
      "frequency": 1,
      "ts": "2025-08-27T11:25:48",
      "agg_message": "Ԁϰ̂ lắm ck nhất nhớ vk lắm r vk tối về dt chửi ck cũng dk nửa tối 9h c",
      "messages": [
        {
          "text_sms": "Ԁϰ̂ lắm ck nhất nhớ vk lắm r vk tối về dt chửi ck cũng dk nửa tối 9h c",
          "count": 1
        }
      ]
    },
    {
      "stt": 20,
      "group_id": "group_wbxl_1755504908",
      "frequency": 2,
      "ts": "2025-08-27T11:30:13",
      "agg_message": "Ԁ̀Ȃ đá 23 một ngàn",
      "messages": [
        {
          "text_sms": "Ԁ̀Ȃ đá 23 một ngàn",
          "count": 2
        }
      ]
    }
  ],
  "page": 1,
  "limit": 10,
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
{
  "stt": 20,
  "group_id": "group_wbxl_1755504908",
  "frequency": 2,
  "ts": "2025-08-27T11:30:13",
  "agg_message": "Ԁ̀Ȃ đá 23 một ngàn",
  "messages": [
    {
      "text_sms": "Ԁ̀Ȃ đá 23 một ngàn",
      "count": 2
    }
  ]
}
```

| Trường           | Kiểu                     | Mô tả |
|------------------|--------------------------|-------|
| `stt`            | `int`                      | Số thứ tự. |
| `group_id`       | `str`                      | ID của nhóm. |
| `frequency`      | `int`                      | Số lượng tin nhắn đã gửi trong nhóm `group_id`. |
| `ts`             | `datetime`    | Thời điểm tin nhắn đầu tiên được gửi trong nhóm.|
| `messages` | `list` | Danh sách các tin nhắn đã gửi trong nhóm. |
| `text_sms`        | `str`                      | Nội dung tin nhắn. |
| `count`          | `int`                      | Tần suất của mỗi `text_sms`. |

---

## GET /frequency/export {#export-get-frequency}
### Mô tả {#mo-ta-export-get-frequency}
API này tiến hành lọc các bản ghi dựa trên thời gian (**giới hạn 1 giờ**), nội dung tin nhắn và số điện thoại. Sau đó tiến hành nhóm theo `group_id` rồi xuất ra dưới dạng file csv để người dùng có thể download.

### Tham số truy vấn {#tham-so-truy-van-export-get-frequency}

| Tên            | Kiểu     | Yêu cầu | Mô tả                                                                      |
|----------------|----------|----------|----------------------------------------------------------------------------|
| from_datetime  | datetime | Không    | Thời gian bắt đầu, định dạng `YYYY-MM-DD HH:MM:SS`.                       |
| to_datetime    | datetime | Không    | Thời gian kết thúc, định dạng `YYYY-MM-DD HH:MM:SS`.                      |
| text_keyword   | string   | Không    | Lọc tin nhắn có chứa từ khóa này (không phân biệt hoa thường).              |
| phone_num      | string   | Không    | Lọc số điện thoại khớp với mẫu này (không phân biệt hoa thường). |

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
API này được sử dụng để gửi phản hồi từ người dùng, giúp họ đánh giá liệu một nhóm có phải là spam hay không dựa trên nội dung tin nhắn được gửi trong nhóm

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
