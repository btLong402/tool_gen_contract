# Contract Automation Desktop App - UI Redesign & Export Directory Feature

## Tóm tắt các thay đổi

### 1. **Thêm chức năng chọn thư mục lưu file**
   - Người dùng có thể tự chọn thư mục lưu các file export (DOCX, PDF)
   - Thư mục được lưu vào file `app_config.json` để nhớ lựa chọn
   - Nút "📁 Change" ở header cho phép thay đổi thư mục bất cứ lúc nào

### 2. **Thiết kế lại giao diện chính (MainWindow)**

#### Header Bar (thanh trên cùng)
- Tiêu đề "📋 Contract Automation" được nổi bậc với màu xanh đậm
- Hiển thị đường dẫn thư mục export hiện tại
- Nút "📁 Change" để chọn thư mục mới

#### Layout cải thiện
- Chia giao diện thành 2 cột rõ ràng:
  - **Cột trái**: Templates Library - quản lý các template
  - **Cột phải**: Draft/Export History - lịch sử xuất file của template được chọn

#### Tổ chức nút lệnh tốt hơn
- **Nút chính (xanh)**: "➕ Add template", "📝 Open dynamic form", "📄 Open selected draft"
- **Nút thứ cấp (xám)**: "🔄 Refresh", "👤 Load partner profile"
- **Nút nguy hiểm (đỏ)**: "🗑 Delete"
- **Nút cảnh báo (cam)**: "💾 Save draft"
- **Nút xuất (xanh lục)**: "✅ Export contract"

### 3. **Thiết kế lại Form Dialog (DynamicFormDialog)**

#### Styling cải thiện
- Màu nền sáng, dễ nhìn (#f5f5f5)
- Form fields có background trắng, border nhẹ
- Focus effect rõ ràng với border xanh lam (#3498db)
- Padding và spacing hợp lý

#### Layout tổ chức
- Tiêu đề template ở đầu
- Form fields cuộn được (scrollable)
- Các nút lệnh ở dưới với kích thước nguyên font hợp lý
- Checkbox "📄 Export PDF after DOCX" tách biệt rõ

### 4. **Color Palette chuyên nghiệp**
```
Header: #2c3e50 (Dark blue-grey)
Primary: #3498db (Fresh blue)
Success: #27ae60 (Green)
Warning: #f39c12 (Orange)
Danger: #e74c3c (Red)
Secondary: #95a5a6 (Grey)
Background: #f5f5f5 (Light grey)
```

### 5. **Cập nhật config.py**

##### Hàm mới:
- `load_exports_dir()`: Load đường dẫn từ app_config.json, fallback về thư mục mặc định
- `save_exports_dir(path)`: Lưu đường dẫn thư mục vào app_config.json

##### File cấu hình:
- `app_config.json`: Lưu tùy chọn của người dùng (vị trí export)

## File được cập nhật

1. **src/contract_automation/config.py**
   - Thêm hệ thống lưu/tải cấu hình
   - Support cho custom export directory

2. **src/contract_automation/ui/main_window.py**
   - Thiết kế lại toàn bộ UI với modern styling
   - Thêm header bar với directory selector
   - Cải thiện tổ chức các nút lệnh
   - Thêm stylesheet với QSS

3. **src/contract_automation/ui/form_dialog.py**
   - Update để nhận export_dir parameter
   - Thiết kế lại form layout
   - Thêm styling toàn bộ form
   - Cải thiện UX của form fields

## Feature mới

### Directory Selection UI
- Header bar hiển thị export directory hiện tại
- Button "Change" mở dialog chọn folder
- Đường dẫn được nhớ lại khi tắt/mở lại ứng dụng

### Improved User Experience
- Emojis cho các nút để dễ nhận biết
- Color-coded buttons cho các loại action khác nhau
- Better visual hierarchy
- Responsive layout
- Consistent styling across dialogs

## Usage

```python
# Thay đổi thư mục export
1. Nhấn nút "📁 Change" ở header
2. Chọn thư mục mới
3. Nhấn "Select" để xác nhận

# File export sẽ được lưu vào thư mục đã chọn
1. Mở form với nút "📝 Open dynamic form"
2. Điền thông tin
3. Nhấn "✅ Export contract"
4. File sẽ được lưu vào thư mục đã chọn
```

## Technical Details

### Configuration System
```
app_config.json
{
  "exports_dir": "/path/to/chosen/directory"
}
```

### Dialog Signatures
```python
# MainWindow now passes export_dir
DynamicFormDialog(
    ...,
    export_dir=self.export_dir,
    parent=self,
)
```

### Styling System
- Sử dụng QSS (Qt Style Sheets)
- ObjectNames cho các widgets:
  - `#header`: Header bar styling
  - `#primaryButton`: Primary action buttons
  - `#dangerButton`: Delete/danger buttons
  - `#formInput`: Form input fields
  
## Testing Checklist

- [ ] Directory selection works
- [ ] Config saves/loads correctly
- [ ] UI renders properly on different screen sizes
- [ ] All buttons respond correctly
- [ ] Form fields accept input
- [ ] Export saves to selected directory
- [ ] Config persists after restart
