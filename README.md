# Google Sheets & Drive access (Python)

This repository contains a small example script that shows how to:

- Authenticate using a Google Service Account
- Read from and write to Google Sheets
- Upload and download files to/from Google Drive

Prerequisites
- A Google Cloud project with the Google Sheets API and Google Drive API enabled.
- A Service Account with a JSON key file.
- Share the Google Sheet you want to access with the service account's email (the service account must have access to the spreadsheet).

Quick steps
1. Create a Google Cloud Project (or use an existing one).
2. Enable APIs:
   - Google Sheets API
   - Google Drive API
3. Create a Service Account and generate a JSON key. Download the JSON file and save it as `service_account.json` in the same directory as the script (or set SERVICE_ACCOUNT_FILE to the path).
4. Share your Google Sheet with the service account email (something like my-service@project.iam.gserviceaccount.com).
5. Install dependencies:
   - pip install -r requirements.txt
6. Update `sheets_drive.py` placeholders (e.g., `SPREADSHEET_ID`, `FILE_ID`, etc.) or call the functions programmatically.
7. Run the script:
   - python sheets_drive.py

Security note
- Do NOT commit your `service_account.json` to public repositories. Add it to `.gitignore` or use environment-based secret management.

References
- Google Sheets API: https://developers.google.com/sheets/api
- Google Drive API: https://developers.google.com/drive/api