# How to Find Your Correct Backblaze B2 Application Key ID

## The Problem

Your current `B2_APPLICATION_KEY_ID` is only **12 characters** (`0428f1a90627`), but Backblaze B2 Application Key IDs should be:
- **~25 characters long**
- **Start with "K"** (like `K001abc123def456ghi789jkl`)

## How to Get the Correct Application Key ID

### Step 1: Log into Backblaze B2 Dashboard
1. Go to https://secure.backblaze.com/
2. Log into your account

### Step 2: Navigate to Application Keys
1. Click on **"B2 Cloud Storage"** in the left menu
2. Click on **"App Keys"** or **"Application Keys"** in the left menu
3. You should see a list of your application keys

### Step 3: Find or Create an Application Key
- **If you see existing keys**: Look for the **"keyID"** column - this is what you need
  - It will look like: `K001abc123def456ghi789jkl` (25 characters, starts with K)
- **If you don't have a key or need a new one**:
  1. Click **"Add a New Application Key"**
  2. Give it a name (e.g., "Pre-signed URLs App")
  3. Select the capabilities you need (at minimum: **"Read Files"** and **"Write Files"**)
  4. Select which bucket(s) it can access (or "All Buckets")
  5. Click **"Create New Key"**
  6. **IMPORTANT**: Copy the **keyID** immediately (it starts with "K")
  7. Also copy the **applicationKey** (the secret, ~40+ characters)

### Step 4: Update Your .env File

Your `.env` file should look like this:

```env
B2_APPLICATION_KEY_ID=K001abc123def456ghi789jkl
B2_APPLICATION_KEY=0052eb40f46b6526bee7a690fc6635d42ec762d209
B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com
B2_BUCKET_NAME=AM-PRESIGNED-URLS
```

**Important Notes:**
- The `B2_APPLICATION_KEY_ID` should be ~25 characters and start with "K"
- The `B2_APPLICATION_KEY` (your secret) looks correct at 40 characters
- No quotes, no extra spaces

## What You Currently Have

Based on your current values:
- ❌ `B2_APPLICATION_KEY_ID=0428f1a90627` - **TOO SHORT** (12 chars, should be ~25)
- ✅ `B2_APPLICATION_KEY=0052eb40f46b6526bee7a690fc6635d42ec762d209` - **CORRECT** (40 chars)
- ✅ `B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com` - **CORRECT**
- ✅ `B2_BUCKET_NAME=AM-PRESIGNED-URLS` - **CORRECT**

## Quick Check

After updating your `.env` file, run:
```bash
python test_env.py
```

This will verify that:
- The key ID is the correct length (~25 chars)
- The key ID starts with "K"
- All variables are loaded correctly

## Still Having Issues?

If you can't find the Application Key ID in your dashboard:
1. Make sure you're looking at **"App Keys"** or **"Application Keys"**, not "Master Key" or "Account ID"
2. The keyID column might be labeled as "Key ID" or "Application Key ID"
3. If you only see a "keyName", you need to create a new key to see the keyID

