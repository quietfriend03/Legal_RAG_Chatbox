## Thư mục XML:
**Tổng quát**: Bao gồm 209 file `.XML` đã được xử lý từ những file JSON để biểu diễn tốt hơn.

## Thư mục JSON:
**Tổng quát**: Bao gồm 209 file `.JSON`, với mỗi file là dữ liệu đã chunking từ những file trong thư mục DOC dùng để huấn luyện mô hình.  
Dưới đây là cấu trúc của một file JSON:

```json
{
  "luật": {},
  "chương": {},
  "tên_chương": {},
  "điều": {},
  "tên_điều": {},
  "nội_dung": {}
}
```
## Thư mục DOC
**Tổng quát**: Bao gồm 209 file .DOCX các bộ luật hiện hành của Việt Nam kể từ năm 1993.
Nguồn:https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/tu-van-phap-luat/42248/danh-muc-luat-bo-luat-hien-hanh-tai-viet-nam

## File preprocessing: 
**Tổng quát**: Là xử lý dữ liệu từ file .docx để chuyển thành file .json nhằm mục đích để lưu trữ vào cơ sở dữ liệu vector.

## File json_converter: 
**Tổng quát**: Chuyển các file .json thành các file .xml để trình diễn dễ hơn.
