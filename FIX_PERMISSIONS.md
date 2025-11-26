# Fix "UnauthorizedAccess" Error

## The Problem

You're getting this error when trying to use a pre-signed download URL:

```
<Error>
<Code>UnauthorizedAccess</Code>
<Message>bucket is not authorized: AM-PRESIGNED-URLS</Message>
</Error>
```

This means your Application Key doesn't have permission to access the bucket "AM-PRESIGNED-URLS".

## Solution

You need to update your Application Key permissions in the Backblaze B2 dashboard.

### Step 1: Go to Application Keys

1. Log into https://secure.backblaze.com/
2. Go to "B2 Cloud Storage" → "App Keys"
3. Find your Application Key (the one you're using - check the keyID in your .env file)

### Step 2: Check Current Permissions

Look at the "capabilities" column for your key. It should include:
- `readFiles` (required for downloads)
- `writeFiles` (required for uploads)
- `listFiles` (required for listing files)

### Step 3: Check Bucket Access

Look at the "bucketName" or "bucket" column. It should show:
- Either "AM-PRESIGNED-URLS" (your specific bucket)
- Or "All Buckets" (access to all buckets)

### Step 4: Fix the Permissions

**Option A: Edit Existing Key (if possible)**
- Some keys can be edited, but many cannot
- If you see an "Edit" button, click it and:
  - Make sure "readFiles" is checked
  - Make sure "writeFiles" is checked (if you need uploads)
  - Make sure "AM-PRESIGNED-URLS" is selected in bucket access, or select "All Buckets"

**Option B: Create a New Key (Recommended)**
1. Click "Add a New Application Key"
2. Give it a name like "S3 API Key" or "Pre-signed URLs Key"
3. **Select Capabilities:**
   - Check "readFiles" (required for downloads)
   - Check "writeFiles" (required for uploads)
   - Check "listFiles" (required for listing files)
4. **Select Bucket Access:**
   - Choose "AM-PRESIGNED-URLS" from the dropdown
   - OR select "All Buckets" if you want access to all buckets
5. Click "Create New Key"
6. **IMPORTANT:** Copy both the keyID and applicationKey immediately (they're only shown once)

### Step 5: Update Your .env File

Replace the old keys with the new ones:

```env
B2_APPLICATION_KEY_ID=your_new_key_id_here
B2_APPLICATION_KEY=your_new_application_key_here
B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com
B2_BUCKET_NAME=AM-PRESIGNED-URLS
```

### Step 6: Restart Your Server

1. Stop your Flask server (Ctrl+C)
2. Start it again: `python app.py`
3. Test the download URL again

## Verify It's Fixed

After updating, you can test the connection:

1. Visit: `http://localhost:5001/api/check-config`
2. Look for `"bucket_access": "Authorized"` in the response
3. If it says "Unauthorized", double-check your key permissions

## Required Capabilities

For this application to work, your Application Key needs:

- **readFiles** - Required for generating download URLs
- **writeFiles** - Required for generating upload URLs
- **listFiles** - Required for listing files in the bucket

## Required Bucket Access

Your Application Key must have access to:
- The specific bucket: **AM-PRESIGNED-URLS**
- OR "All Buckets" (gives access to all buckets)

## Still Having Issues?

If you still get the error after updating permissions:

1. Make sure you restarted the server after updating .env
2. Verify the bucket name in .env matches exactly: `AM-PRESIGNED-URLS` (case-sensitive)
3. Check that you're using the correct Application Key (the one with the right permissions)
4. Try creating a completely new Application Key with all required permissions

