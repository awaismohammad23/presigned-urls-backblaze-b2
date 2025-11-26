# Backblaze B2 Pre-Signed URLs Application

A full-stack web application for generating and testing pre-signed URLs with Backblaze B2 storage.

## Features

- 🔗 Generate pre-signed URLs for downloading files
- ⬆️ Generate pre-signed URLs for uploading files
- 📁 List all files in your B2 bucket
- 🧪 Test upload functionality directly from the UI
- ⏱️ Customizable expiration times for URLs

## Setup

### 1. Install Dependencies

Make sure you have Python 3.8+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

Or if you're using a virtual environment (recommended):

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with your Backblaze B2 credentials:

```env
B2_APPLICATION_KEY_ID=your_key_id_here
B2_APPLICATION_KEY=your_application_key_here
B2_ENDPOINT_URL=https://s3.us-west-000.backblazeb2.com
B2_BUCKET_NAME=your_bucket_name
```

**Note:** 
- Replace `us-west-000` with your actual B2 region
- You can find your endpoint URL in your Backblaze B2 dashboard
- The endpoint format is: `https://s3.<region>.backblazeb2.com`
- You can write the endpoint URL with or without `https://` - it will be added automatically if missing
  - Example: `B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com` (works)
  - Example: `B2_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com` (also works)

### 3. Run the Application

Start the Flask server:

```bash
python app.py
```

The application will be available at `http://localhost:5001`

**Note:** 
- The default port is 5001 (to avoid conflicts with macOS AirPlay on port 5000)
- If port 5001 is also in use, you can set a custom port in your `.env` file:
  ```env
  PORT=8080
  ```
- The frontend automatically detects the port, so no manual configuration is needed

## Usage

### Generate Download URL

1. Navigate to the "Download URL" tab
2. Enter the file name you want to download
3. Set the expiration time (in seconds, default is 3600 = 1 hour)
4. Click "Generate Download URL"
5. Use the generated URL to download the file

### Generate Upload URL

1. Navigate to the "Upload URL" tab
2. Enter the file name for the file you want to upload
3. Set the expiration time
4. Click "Generate Upload URL"
5. Select a file and click "Upload File" to test the upload

### List Files

1. Navigate to the "List Files" tab
2. View all files in your bucket
3. Click "Generate Download URL" on any file to quickly generate a download URL
4. Click "Refresh" to reload the file list

## API Endpoints

### POST `/api/generate-download-url`

Generate a pre-signed URL for downloading a file.

**Request Body:**
```json
{
  "file_name": "example.pdf",
  "expiration": 3600
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://...",
  "file_name": "example.pdf",
  "expiration_seconds": 3600,
  "expires_at": 1234567890.123
}
```

### POST `/api/generate-upload-url`

Generate a pre-signed URL for uploading a file.

**Request Body:**
```json
{
  "file_name": "example.pdf",
  "expiration": 3600
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://...",
  "file_name": "example.pdf",
  "expiration_seconds": 3600,
  "expires_at": 1234567890.123
}
```

### GET `/api/list-files`

List all files in the bucket.

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "name": "example.pdf",
      "size": 1024,
      "last_modified": "2024-01-01T00:00:00"
    }
  ]
}
```

## Project Structure

```
.
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in git)
├── static/
│   ├── index.html        # Frontend HTML
│   ├── styles.css        # Frontend styles
│   └── script.js         # Frontend JavaScript
└── README.md             # This file
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Make sure your B2 endpoint URL is correct and includes the region
2. **Access Denied**: Verify your B2 credentials are correct in the `.env` file
3. **File Not Found**: Ensure the file exists in your bucket before generating a download URL
4. **CORS Errors**: The Flask app includes CORS support, but make sure you're accessing it from `localhost:5000`

## Security Notes

- Never commit your `.env` file to version control
- Pre-signed URLs expire after the specified time
- Keep your B2 credentials secure
- Consider using environment-specific configurations for production

## License

MIT

