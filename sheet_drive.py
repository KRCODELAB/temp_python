"""
sheets_drive.py

Example utilities to:
- authenticate with a Google Service Account
- read/write Google Sheets (via Sheets API)
- upload/download files on Google Drive

Set SERVICE_ACCOUNT_FILE to the path of your service account JSON key.
Share the target spreadsheet with the service account email.
"""

import os
import io
from typing import List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Path to your service account JSON key
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

# Scopes required for Sheets and Drive access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",  # read/write sheets
    "https://www.googleapis.com/auth/drive",         # drive file operations
]


def get_credentials(sa_file: str = SERVICE_ACCOUNT_FILE, scopes: List[str] = SCOPES):
    """
    Load service account credentials from JSON file.
    """
    if not os.path.exists(sa_file):
        raise FileNotFoundError(f"Service account file not found: {sa_file}")
    creds = service_account.Credentials.from_service_account_file(sa_file, scopes=scopes)
    return creds


#
# Sheets helpers (using the Sheets REST API)
#
def read_sheet_values(spreadsheet_id: str, range_name: str, creds=None) -> List[List[str]]:
    """
    Read values from a sheet range.

    - spreadsheet_id: the id from the spreadsheet URL (https://docs.google.com/spreadsheets/d/<ID>/...)
    - range_name: A1 notation or sheet range e.g. 'Sheet1!A1:C10' or 'Sheet1'
    Returns a list of rows (each row is a list of cell strings).
    """
    creds = creds or get_credentials()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get("values", [])


def write_sheet_values(spreadsheet_id: str, range_name: str, values: List[List], creds=None, value_input_option: str = "RAW"):
    """
    Write values to a sheet range (overwrites existing contents in that range).

    - values: list of rows, each row is a list of cell values, e.g. [[1,2],[3,4]]
    - value_input_option: "RAW" or "USER_ENTERED"
    """
    creds = creds or get_credentials()
    service = build("sheets", "v4", credentials=creds)
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name, valueInputOption=value_input_option, body=body
    ).execute()
    return result  # contains updatedCells etc.


#
# Drive helpers
#
def upload_file_to_drive(file_path: str, mime_type: str = None, creds=None, parent_folder_id: Optional[str] = None) -> str:
    """
    Upload a local file to Google Drive.

    Returns the uploaded file ID.
    """
    creds = creds or get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": os.path.basename(file_path)}
    if parent_folder_id:
        file_metadata["parents"] = [parent_folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")


def download_file_from_drive(file_id: str, destination_path: str, creds=None) -> str:
    """
    Download a file from Google Drive into destination_path.

    Requires permission to read the file (the service account must have access).
    Returns the destination_path on success.
    """
    creds = creds or get_credentials()
    drive_service = build("drive", "v3", credentials=creds)

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, mode="wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download {int(status.progress() * 100)}%.")

    fh.close()
    return destination_path


def get_file_metadata(file_id: str, creds=None) -> dict:
    """
    Get metadata for a Drive file.
    """
    creds = creds or get_credentials()
    drive_service = build("drive", "v3", credentials=creds)
    return drive_service.files().get(fileId=file_id, fields="id, name, mimeType, size, parents").execute()


#
# Example usage
#
def main():
    creds = get_credentials()

    # --- Sheets: read example ---
    SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"  # TODO: replace
    RANGE = "Sheet1!A1:C10"                 # example
    try:
        values = read_sheet_values(SPREADSHEET_ID, RANGE, creds)
        print("Read values:")
        for row in values:
            print(row)
    except Exception as e:
        print("Error reading sheet:", e)

    # --- Sheets: write example ---
    try:
        write_values = [["Name", "Age"], ["Alice", "30"], ["Bob", "28"]]
        write_result = write_sheet_values(SPREADSHEET_ID, "Sheet1!A1:B3", write_values, creds)
        print("Write result:", write_result)
    except Exception as e:
        print("Error writing sheet:", e)

    # --- Drive: upload example ---
    LOCAL_FILE = "example_upload.txt"
    # create a tiny test file if it doesn't exist
    if not os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "w", encoding="utf-8") as f:
            f.write("Hello from service account upload!\n")

    try:
        uploaded_id = upload_file_to_drive(LOCAL_FILE, mime_type="text/plain", creds=creds)
        print("Uploaded file ID:", uploaded_id)
    except Exception as e:
        print("Error uploading file:", e)

    # --- Drive: download example ---
    # To test download, set FILE_ID to a file that the service account can access.
    FILE_ID = "YOUR_FILE_ID"  # TODO: replace
    DEST = "downloaded_example.txt"
    if FILE_ID != "YOUR_FILE_ID":
        try:
            downloaded_path = download_file_from_drive(FILE_ID, DEST, creds)
            print("Downloaded to:", downloaded_path)
        except Exception as e:
            print("Error downloading file:", e)
    else:
        print("Set FILE_ID to a real file id to test download.")


if __name__ == "__main__":
    main()