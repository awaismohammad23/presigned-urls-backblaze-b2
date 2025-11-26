# Update Your .env File

## Your New Keys (from the screenshot):

Based on your Backblaze B2 dashboard, you need to update your `.env` file with these values:

```env
B2_APPLICATION_KEY_ID=0050428f1a906270000000001
B2_APPLICATION_KEY=K005rH1B5kjFA6QgKtyAbzl1F80qMeY
B2_ENDPOINT_URL=s3.us-east-005.backblazeb2.com
B2_BUCKET_NAME=AM-PRESIGNED-URLS
```

## Important Notes:

1. **B2_APPLICATION_KEY_ID** = The `keyID` from Backblaze (25 characters: `0050428f1a906270000000001`)
2. **B2_APPLICATION_KEY** = The `applicationKey` from Backblaze (starts with 'K': `K005rH1B5kjFA6QgKtyAbzl1F80qMeY`)

## Steps:

1. Open your `.env` file
2. Replace the old values with the new ones above
3. Make sure there are:
   - NO quotes around the values
   - NO extra spaces
   - Exact match of the values
4. Save the file
5. **Restart your Flask server** (stop with Ctrl+C, then run `python app.py` again)

## Verify:

After updating, when you start the server, you should see:
```
✓ Loaded B2_APPLICATION_KEY_ID: 0050428f1a... (length: 25)
✓ Loaded B2_APPLICATION_KEY: ********************... (length: 25)
```

If you still see the old 12-character keyID, the .env file wasn't updated correctly.

