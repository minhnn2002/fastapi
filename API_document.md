
# 📚 SMS API Documentation

## 📑 Table of Contents

- [API 1: GET /content/](#api-1-get-content)
  - [Description](#description)
  - [Query Parameters](#query-parameters)
  - [Response Example](#response-example)
  - [SMSGroupedData Format](#smsgroupeddata-format)
  - [Possible Errors](#possible-errors)
- [API 2: PUT /content/](#api-1-get-content)
  - [Description](#description)
  - [Query Parameters](#query-parameters)
  - [Response Example](#response-example)
- [API 3: GET /frequency/](#api-2-get-frequency)
  - [Description](#description-1)
  - [Query Parameters](#query-parameters-1)
  - [Response Example](#response-example-1)
  - [FrequencyData Format](#frequencydata-format)
  - [Possible Errors](#possible-errors-1)
- [API 4: PUT /frequency/](#api-2-get-frequency)
  - [Description](#description-1)
  - [Query Parameters](#query-parameters-1)
  - [Response Example](#response-example-1)

---

## 📘 API 1: GET /content/

### Description
This API filters and groups SMS messages based on time, content keyword, and phone number. It returns statistics like frequency and groups of similar messages.

### Query Parameters
- If `from_datetime` or `to_datetime` is not provided, the system will use the min and max timestamps from the database.  
- If `from_datetime` is earlier than the min timestamp, it will be auto-adjusted.  
- If `to_datetime` is later than the max timestamp, it will also be auto-adjusted.

| Name           | Type      | Required | Description                                                                 |
|----------------|-----------|----------|-----------------------------------------------------------------------------|
| from_datetime  | datetime  | No       | Start time in `YYYY-MM-DD HH:MM:SS` format.|
| to_datetime    | datetime  | No       | End time in `YYYY-MM-DD HH:MM:SS` format.  |
| page           | int       | No       | Page number to fetch (default is `0`). Must be ≥ 0.                         |
| page_size      | int       | No       | Number of records per page. Allowed values: `10`, `50`, `100`.             |
| text_keyword   | string    | No       | Filter messages that contain this keyword (case-insensitive).              |
| phone_num      | string    | No       | Filter senders whose phone numbers match this pattern (case-insensitive).  |

### Response Example

```json
{
  "status_code": 200,
  "message": "Success",
  "data": [...],
  "error": false,
  "error_message": "",
  "page": 0,
  "limit": 10,
  "total": 100
}
```

### Response Fields

| Field           | Type                           | Description |
|------------------|--------------------------------|-------------|
| `status_code`    | `int`                          | HTTP status code (e.g. 200, 400, 404) |
| `message`        | `str or null`                  | Response message |
| `data`           | `list[SMSGroupedData] or null` | Main data result |
| `error`          | `bool`                         | Whether an error occurred |
| `error_message`  | `str or null`                  | Error description if any |
| `page`           | `int`                          | Current page number |
| `limit`          | `int`                          | Number of records per page |
| `total`          | `int`                          | Total number of matched records |

### SMSGroupedData Format Example

```json
{
  "stt": 1,
  "sdt_in": "0123456789",
  "frequency": 3,
  "ts": "2022-09-06T17:26:20",
  "message_groups": [
    {
      "group_id": "group_abc",
      "messages": [
        {
          "text_sms": "Example content",
          "count": 2
        }
      ]
    }
  ]
}
```

| Field            | Type                     | Description |
|------------------|--------------------------|-------------|
| `stt`            | int                      | Row number |
| `sdt_in`         | str                      | Phone number |
| `frequency`      | int                      | Number of SMS messages |
| `ts`             | string (ISO datetime)    | First message timestamp |
| `message_groups` | list of grouped messages | Grouped by message content |
|`group_id`        | str                      | ID of the group|
|`message`         | str                      | The message in group `group_id`|
|`count`           | int                      | Total number of message count|
### Possible Errors

- **400 Bad Request**
  - `"Invalid time range: 'to_datetime' is earlier than 'from_datetime'."`
  - `"Page X exceeds total pages (Y)"`

---
## 📘 API 2: PUT /content/

### Description
This API is used to send client feedback, so that they can evaluate whether a phone number is spam or not based on the text message.

If any message is marked as spam, then all the messages belong to the same group will be marked as spam

### Query Parameters
| Name           | Type      | Required | Description                                                                 |
|----------------|-----------|----------|-----------------------------------------------------------------------------|
| sdt_in  | str  | No       | The phone number client wants to give the feedback|
| text_sms    | str  | No       | The message that phone number send |
| feedback           | bool       | No       |  Feedback of client whether True(Spam) or False(Not Spam).          |


### Response Example

```json
"Message": "Updated {number} records",
```
{number} is the total number of records have been updated in the database.


---

## 📘 API 3: GET /frequency/

### Description
This API filters SMS messages by time, keyword, and phone number, and **returns only the frequency and first timestamp per phone number** (no message grouping).

### Query Parameters

Same as `/content/`:

| Name            | Type     | Description |
|-----------------|----------|-------------|
| `from_datetime` | datetime | Start timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `to_datetime`   | datetime | End timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `page`          | int      | Page index (starting from 0) |
| `page_size`     | int      | Records per page (10, 50, 100) |
| `text_keyword`  | str      | Filter SMS content by keyword |
| `phone_num`     | str      | Filter phone number pattern |

### Response Example

```json
{
  "status_code": 200,
  "message": "Success",
  "data": [...],
  "error": false,
  "error_message": "",
  "page": 0,
  "limit": 10,
  "total": 100
}
```

### Response Fields

| Field           | Type                           | Description |
|------------------|--------------------------------|-------------|
| `status_code`    | `int`                          | HTTP status code (e.g. 200, 400, 404) |
| `message`        | `str or null`                  | Response message |
| `data`           | `list[SMSGroupedData] or null` | Main data result |
| `error`          | `bool`                         | Whether an error occurred |
| `error_message`  | `str or null`                  | Error description if any |
| `page`           | `int`                          | Current page number |
| `limit`          | `int`                          | Number of records per page |
| `total`          | `int`                          | Total number of matched records |

### FrequencyData Format Example

```json
{
  "stt": 1,
  "sdt_in": "0123456789",
  "frequency": 3,
  "ts": "2022-09-06T17:26:20"
}
```

| Field        | Type                  | Description |
|--------------|------------------------|-------------|
| `stt`        | int                    | Row number |
| `sdt_in`     | str                    | Phone number |
| `frequency`  | int                    | Number of matched messages |
| `ts_first`   | string (ISO datetime)  | Timestamp of first message |

### Possible Errors

- **400 Bad Request**
  - `"Invalid time range: 'to_datetime' is earlier than 'from_datetime'."`
  - `"Page X exceeds total pages (Y)"`

## 📘 API 4: PUT /frequency/

### Description
This API is used to send client feedback, so that they can evaluate whether a phone number is spam or not based on the frequency message.

If any record is marked as spam, then all the records belong to that phone number will be marked as spam

### Query Parameters
| Name           | Type      | Required | Description                                                                 |
|----------------|-----------|----------|-----------------------------------------------------------------------------|
| sdt_in  | str  | No       | The phone number client wants to give the feedback|
| feedback           | bool       | No       |  Feedback of client whether True(Spam) or False(Not Spam).          |


### Response Example

```json
"Message": "Updated {number} records",
```
{number} is the total number of records have been updated in the database.


