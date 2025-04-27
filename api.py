import os
import os.path as path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']

creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('drive', 'v3', credentials=creds)

    # Upload a file to Google Drive
    def upload_file(file_path, mime_type):
        file_metadata = {'name': path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f'File ID: {file.get("id")}')

    # Download a file from Google Drive
    def download_file(file_id, destination):
        request = service.files().get_media(fileId=file_id)
        fh = open(destination, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f'Download {int(status.progress() * 100)}%.')
        fh.close()


    # List files in Google Drive
    def list_files(query=None):
        results = service.files().list(q=query, pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(f'{item["name"]} ({item["id"]})')
    
    # Delete a file from Google Drive
    def delete_file(file_id):
        try:
            service.files().delete(fileId=file_id).execute()
            print(f'File with ID {file_id} deleted successfully.')
        except HttpError as error:
            print(f'An error occurred: {error}')

    # Example usage
    if __name__ == '__main__':
        # Upload a file
        #upload_file('example.txt', 'text/plain')

        # List files
        #list_files()

        # Download a file (replace 'your_file_id' with the actual file ID)
        download_file('1D3my6UK7liPUqSjnHtd1S7X3IVZKei7F', 'teste_meza.txt')

        # Delete a file (replace 'your_file_id' with the actual file ID)
        #delete_file('your_file_id')

except HttpError as error:
    print(f'An error occurred: {error}')
    creds = None 

    # Handle the error as needed
    # For example, you can log the error or notify the user 
        