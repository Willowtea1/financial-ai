# Upload API Documentation

## Endpoint: `/api/upload`

Upload user documents (images and videos) to R2 storage via Cloudflare Worker.

### Authentication
This endpoint requires authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Request

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): The file to upload (image or video)
- `compress` (optional): Boolean flag to compress videos before upload (default: false)

### Example Usage

#### Using cURL:
```bash
curl -X POST http://localhost:3001/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "compress=false"
```

#### Using JavaScript (Fetch API):
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('compress', 'true');

const response = await fetch('http://localhost:3001/api/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result);
```

#### Using Axios:
```javascript
import axios from 'axios';

const formData = new FormData();
formData.append('file', file);
formData.append('compress', true);

const response = await axios.post('http://localhost:3001/api/upload', formData, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'multipart/form-data'
  }
});

console.log(response.data);
```

### Response

#### Success (200):
```json
{
  "success": true,
  "url": "https://pub-xxxxx.r2.dev/1234567890_abc123_document.pdf",
  "fileName": "1234567890_abc123_document.pdf",
  "originalName": "document.pdf",
  "size": 1048576,
  "compressed": false
}
```

#### Error (400/500):
```json
{
  "detail": {
    "error": "Failed to upload file",
    "message": "Only image and video files are allowed"
  }
}
```

### File Type Support
- **Images:** All image formats (JPEG, PNG, GIF, WebP, etc.)
- **Videos:** All video formats (MP4, MOV, AVI, etc.)

### File Size Limit
Maximum file size: 100MB (configurable in Cloudflare Worker)

### Features
- Automatic file type validation
- Optional video compression
- Secure upload with authentication
- Upload history saved to database
- Direct R2 storage via Cloudflare Worker

### Database Record
Each successful upload creates a record in the `user_uploads` table with:
- `user_id`: ID of the authenticated user
- `file_name`: Generated unique filename
- `original_name`: Original filename
- `file_url`: Public URL to access the file
- `file_size`: File size in bytes
- `file_type`: MIME type
- `compressed`: Whether video was compressed
