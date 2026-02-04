# Google Drive API Setup Guide

This guide explains how to set up Google Drive API for the document summarizer.

## Why Use Google Drive API?

The document summarizer can work in two modes:

1. **Direct URL Method** - For public files, no authentication needed
2. **Google Drive API Method** - For private folders, requires setup but more reliable

## Quick Start (For Public Files)

If your Google Drive folder is publicly accessible, you can use the direct URL method without any setup:

```bash
# Just provide file IDs
python summarize_gdrive.py --file-ids FILE_ID1 FILE_ID2 FILE_ID3
```

To get file IDs from a public folder:
1. Open the folder in browser
2. Click on each file
3. Copy the ID from the URL: `https://drive.google.com/file/d/FILE_ID_HERE/view`

## Full Setup (For Private Folders)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project name

### Step 2: Enable Google Drive API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### Step 3: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in app name (e.g., "Document Summarizer")
   - Add your email as developer contact
   - Skip optional scopes
   - Add yourself as test user
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Document Summarizer"
   - Click "Create"
5. Download the credentials JSON file
6. Save it as `credentials.json` in your project folder

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

### Step 5: First Run (Authentication)

```bash
python summarize_gdrive.py --folder "YOUR_FOLDER_URL" --credentials credentials.json
```

On first run:
1. Browser will open automatically
2. Sign in with your Google account
3. Grant permissions to access Google Drive
4. A `token.json` file will be created (keeps you logged in)

## Usage

### Using Google Drive API

```bash
# Basic usage
python summarize_gdrive.py --folder "https://drive.google.com/drive/folders/1x6EKNkVw6PlFVTr6cGrsVscmRuwqGrXd"

# With custom credentials location
python summarize_gdrive.py --folder "FOLDER_URL" --credentials path/to/credentials.json

# With different model
python summarize_gdrive.py --folder "FOLDER_URL" --model google/gemini-flash-1.5:free
```

### Using Direct File IDs (No Auth Required)

```bash
# For public files
python summarize_gdrive.py --file-ids FILE_ID1 FILE_ID2 FILE_ID3
```

## Troubleshooting

### "credentials.json not found"

Make sure you've downloaded the OAuth credentials from Google Cloud Console and saved them as `credentials.json`.

### "Access denied" or "Forbidden"

1. Make sure the OAuth consent screen includes your Google account as a test user
2. Check that Google Drive API is enabled
3. Try deleting `token.json` and re-authenticating

### "This app isn't verified"

During OAuth flow, you might see a warning. Click "Advanced" > "Go to [app name] (unsafe)" to continue. This is normal for apps in development/testing.

### Rate Limits

Google Drive API has rate limits:
- 20,000 requests per 100 seconds per project
- 10,000 requests per 100 seconds per user

For most use cases, this is more than enough.

## Security Notes

### Protecting Your Credentials

- **Never commit `credentials.json` to git** (it's in `.gitignore`)
- **Never commit `token.json` to git** (it's in `.gitignore`)
- Keep these files secure on your local machine

### Revoking Access

To revoke access:
1. Go to [Google Account Settings](https://myaccount.google.com/permissions)
2. Find your app
3. Click "Remove Access"

### OAuth Scopes

The app requests:
- `https://www.googleapis.com/auth/drive.readonly` - Read-only access to Drive

This means the app can:
- ✅ Read file names and content
- ✅ List files in folders
- ❌ Cannot modify files
- ❌ Cannot delete files
- ❌ Cannot share files

## Alternative: Service Account (Advanced)

For automated/server deployments, use a Service Account instead of OAuth:

1. In Google Cloud Console > "Credentials"
2. Create "Service Account"
3. Download the JSON key
4. Share your Google Drive folder with the service account email
5. Use the service account key for authentication

This is more complex but better for automation.

## Cost

Google Drive API is **free** for reasonable use:
- Free tier: Very generous limits
- No credit card required for basic usage
- Only pay if you exceed free tier limits (unlikely for most users)

## References

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
