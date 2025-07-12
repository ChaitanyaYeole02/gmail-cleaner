# Gmail Resume Scanner

A Python script that automatically scans Gmail emails for resume PDF attachments and categorizes them based on your search criteria. Unqualified resumes are automatically labeled as "To Be Deleted" for easy cleanup.

## Features

- 🔍 **Smart Resume Scanning**: Searches through Gmail for emails with PDF attachments
- 📄 **PDF Text Extraction**: Extracts and analyzes text content from resume PDFs
- 🎯 **Keyword Matching**: Uses your search criteria to determine resume qualification
- 🏷️ **Automatic Labeling**: Labels unqualified resumes as "To Be Deleted"
- 📊 **Detailed Reporting**: Shows scanning statistics and results
- 🤖 **AI-Powered Job Application Filtering**: Pre-filters emails to only process job applications
- 💾 **Memory-Efficient Batch Processing**: Processes emails in batches to avoid memory issues

## Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud Project with Gmail API enabled

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Download the credentials file and rename it to `credentials.json`
5. Place `credentials.json` in the same directory as the script

### 4. Configuration Setup

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:

   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_APP_PASSWORD`: Your Google App Password

3. Optional: Configure processing settings:
   - `MAX_EMAILS_TO_PROCESS`: Maximum emails to process (default: 1000)
   - `PDF_SEARCH_QUERY`: Custom Gmail search query (default: has:attachment filename:pdf)

**Security Note**: The `.env` file is automatically ignored by Git to keep your API keys secure.

### 5. First Run Authentication

On first run, the script will:

1. Open your browser for OAuth authentication
2. Ask you to log in to your Google account
3. Grant permissions to access your Gmail
4. Save authentication tokens for future use

## Usage

### Basic Usage

```bash
python gmail_resume_scanner.py
```

The script will prompt you for search criteria. Examples:

- `"Find me a candidate who is skilled in Java"`
- `"Looking for Python developers with Django experience"`
- `"Need someone with React and TypeScript skills"`

### How It Works

1. **Email Search**: Finds all emails with PDF attachments
2. **PDF Processing**: Extracts text from each PDF attachment
3. **Keyword Analysis**: Compares resume content with your search criteria
4. **Qualification Check**: Determines if resume matches requirements (50% keyword match threshold)
5. **Labeling**: Marks unqualified resumes with "To Be Deleted" label
6. **Reporting**: Shows detailed statistics of the scanning process

### Output Example

```
Gmail Resume Scanner
==================================================
Enter your search criteria: Find me a candidate who is skilled in Java

Scanning emails with criteria: 'Find me a candidate who is skilled in Java'
This may take a few minutes...

==================================================
SCANNING RESULTS
==================================================
Total emails scanned: 15
Emails marked for deletion: 8
Emails that qualify: 7

8 emails have been labeled as 'To Be Deleted'
```

## Configuration

### Customizing Keyword Matching

The script uses a simple keyword matching algorithm. You can modify the `check_resume_qualification` method in `gmail_resume_scanner.py` to:

- Adjust the match threshold (currently 50%)
- Add more sophisticated NLP processing
- Implement fuzzy matching
- Add industry-specific keyword dictionaries

### Changing Label Name

To change the label name from "To Be Deleted", modify this line in the `scan_resumes` method:

```python
label_id = self.create_label_if_not_exists("Your Custom Label Name")
```

## Troubleshooting

### Common Issues

1. **"credentials.json not found"**

   - Download credentials from Google Cloud Console
   - Ensure file is named `credentials.json`
   - Place in the same directory as the script

2. **Authentication Errors**

   - Delete `token.json` and re-run the script
   - Check that Gmail API is enabled in Google Cloud Console
   - Ensure OAuth consent screen is configured

3. **No PDFs Found**

   - Check that emails actually have PDF attachments
   - Verify Gmail search query is working correctly

4. **PDF Text Extraction Errors**
   - Some PDFs may be image-based or password-protected
   - The script will skip these and continue processing others

### Logging

The script provides detailed logging. Check the console output for:

- Authentication status
- Number of emails found
- PDF processing results
- Label creation and application status

## Security Notes

- The script only requests Gmail modification permissions (no read access to email content)
- Authentication tokens are stored locally in `token.json`
- Never share your `credentials.json` or `token.json` files
- Consider using environment variables for production use

## Limitations

- Only processes PDF attachments (not other formats)
- Simple keyword matching (not advanced NLP)
- Processes only the first PDF attachment per email
- Requires manual review of labeled emails before deletion

## Contributing

Feel free to enhance the script with:

- Support for other file formats (DOC, DOCX)
- Advanced NLP for better keyword matching
- Machine learning for resume classification
- Batch processing capabilities
- Email notification features

## License

This project is open source. Feel free to modify and distribute as needed.
