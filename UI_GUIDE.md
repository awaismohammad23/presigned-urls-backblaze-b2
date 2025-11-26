# UI Interaction Guide

## Getting Started

1. **Start the Server**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5001`

2. **Open in Browser**
   Navigate to: `http://localhost:5001`

## Using the Application

The application has three main tabs:

### 📥 Tab 1: Download URL

**Purpose:** Generate a pre-signed URL to download an existing file from your B2 bucket.

**Steps:**
1. Click on the **"Download URL"** tab (it's selected by default)
2. Enter the **file name** of the file you want to download (e.g., `image.png`, `document.pdf`)
   - ⚠️ **Important:** The file must already exist in your B2 bucket
3. (Optional) Set the **expiration time** in seconds (default is 3600 = 1 hour)
   - Maximum: 604800 seconds (7 days)
4. Click **"Generate Download URL"**
5. The generated URL will appear below with:
   - The full pre-signed URL
   - Expiration details
   - A clickable link to test the download

**Example:**
- File Name: `my-photo.jpg`
- Expiration: `3600` (1 hour)
- Result: A URL that allows downloading `my-photo.jpg` for 1 hour

---

### ⬆️ Tab 2: Upload URL

**Purpose:** Generate a pre-signed URL to upload a new file to your B2 bucket.

**Steps:**
1. Click on the **"Upload URL"** tab
2. Enter the **file name** for the file you want to upload (e.g., `new-document.pdf`)
   - This will be the name of the file in your B2 bucket
3. (Optional) Set the **expiration time** in seconds (default is 3600 = 1 hour)
4. Click **"Generate Upload URL"**
5. After generating the URL, a **"Test Upload"** section will appear
6. Click **"Choose File"** and select a file from your computer
7. Click **"Upload File"** to test the upload
8. You'll see a success message if the upload works

**Example:**
- File Name: `report-2024.pdf`
- Expiration: `7200` (2 hours)
- Result: A URL that allows uploading a file named `report-2024.pdf` for 2 hours

---

### 📁 Tab 3: List Files

**Purpose:** View all files currently in your B2 bucket.

**Steps:**
1. Click on the **"List Files"** tab
2. The application will automatically load all files from your bucket
3. For each file, you'll see:
   - **File name**
   - **File size** (formatted in KB, MB, GB)
   - **Last modified date**
   - A **"Generate Download URL"** button
4. Click **"Generate Download URL"** on any file to:
   - Automatically switch to the Download URL tab
   - Pre-fill the file name
   - Generate a download URL for that file
5. Click **"Refresh"** to reload the file list

**Use Cases:**
- Browse what files are in your bucket
- Quickly generate download URLs for existing files
- Verify that uploads were successful

---

## Common Workflows

### Workflow 1: Download an Existing File
1. Go to **"List Files"** tab
2. Find the file you want
3. Click **"Generate Download URL"**
4. Click the generated link to download

### Workflow 2: Upload a New File
1. Go to **"Upload URL"** tab
2. Enter a file name (e.g., `my-document.pdf`)
3. Click **"Generate Upload URL"**
4. Select your file and click **"Upload File"**
5. Go to **"List Files"** tab to verify the upload

### Workflow 3: Share a File Temporarily
1. Go to **"Download URL"** tab
2. Enter the file name
3. Set expiration (e.g., 3600 for 1 hour)
4. Copy the generated URL
5. Share the URL with others (it will expire after the set time)

---

## Understanding the Results

### Success Messages (Green)
- ✅ Shows the generated URL
- Displays expiration information
- Provides clickable links to test

### Error Messages (Red)
- ❌ Shows what went wrong
- Common errors:
  - **"file_name is required"** - You forgot to enter a file name
  - **"File not found"** - The file doesn't exist in your bucket (for downloads)
  - **"Access denied"** - Check your B2 credentials in `.env`
  - **"Connection error"** - Check your B2 endpoint URL

---

## Tips

1. **File Names:** Use the exact file name as it appears in your B2 bucket (case-sensitive)
2. **Expiration:** Shorter expiration times are more secure for sensitive files
3. **Testing:** Always test your URLs before sharing them
4. **Refresh:** Use the refresh button in "List Files" after uploading to see new files
5. **Browser:** The UI works best in modern browsers (Chrome, Firefox, Safari, Edge)

---

## Troubleshooting

### CSS/JS Not Loading
- Make sure the server is running
- Check the browser console for errors
- Try refreshing the page (Ctrl+R or Cmd+R)

### API Errors
- Check your `.env` file has correct B2 credentials
- Verify your bucket name is correct
- Ensure your B2 endpoint URL is correct

### Upload Not Working
- Make sure you generated an upload URL first
- Check the file size (very large files may timeout)
- Verify the file name doesn't contain special characters

---

## Need Help?

Check the main `README.md` for setup instructions and API documentation.

