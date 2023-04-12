import os
import time
import requests
from zoomus import ZoomClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import telegram

# Install the required libraries
!pip install zoomus google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-telegram-bot==13.7.0

# Set up the Zoom client with your API key and secret
zoom_client = ZoomClient(api_key='YOUR_ZOOM_API_KEY', api_secret='YOUR_ZOOM_API_SECRET')

# Set up the Google Drive API client with your credentials file and folder ID
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'PATH_TO_YOUR_CREDENTIALS_FILE'
creds = None
if os.path.exists(SERVICE_ACCOUNT_FILE):
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

# Set up the Telegram bot with your bot token and chat ID
bot = telegram.Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
chat_id = 'YOUR_TELEGRAM_CHAT_ID'

# Define a function to join the Zoom meeting and start recording
def start_recording_zoom_meeting(meeting_link, meeting_password):
    # Join the Zoom meeting using the link or ID and password
    join_url = zoom_client.meeting.join_url(meeting_link, meeting_password)
    meeting_id = join_url.split('/')[-1]
    meeting_password = join_url.split('/')[-2]
    # Start the recording of the meeting
    recording_settings = {
        'recording_type': 'cloud',
        'audio_transcript': 'false'
    }
    response = zoom_client.recording.start(meeting_id, **recording_settings)
    if response['status'] == 'success':
        print('Recording started successfully')
    else:
        print('Recording failed to start')

# Define a function to stop the recording of the Zoom meeting and upload it to Google Drive
def stop_recording_zoom_meeting():
    # Stop the recording of the meeting
    response = zoom_client.recording.stop()
    if response['status'] == 'success':
        print('Recording stopped successfully')
    else:
        print('Recording failed to stop')
    # Get the recording file URL and download it
    recording_files = response['recording_files']
    for recording_file in recording_files:
        if recording_file['recording_type'] == 'shared_screen_with_speaker_view':
            recording_file_url = recording_file['download_url']
            recording_file_name = recording_file['recording_start'].replace(':', '-') + '.mp4'
            response = requests.get(recording_file_url)
            with open(recording_file_name, 'wb') as f:
                f.write(response.content)
    # Upload the recording file to Google Drive
    if creds is not None:
        file_metadata = {'name': recording_file_name, 'parents': [FOLDER_ID]}
        media = googleapiclient.http.MediaFileUpload(recording_file_name, resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        print('File ID: %s' % file_id)
        # Send a notification to the Telegram bot
        message = 'The Zoom meeting recording has been uploaded to Google Drive: https://drive.google.com/file/d/%s/view' % file_id
        bot.send_message(chat_id=chat_id, text=message)
    else:
        print('Google Drive API credentials not found')

# Join the Zoom meeting and start recording
start_recording_zoom_meeting('YOUR_ZOOM_MEETING_LINK_OR_ID', 'YOUR_ZOOM_MEETING_PASSWORD')

# Wait for the meeting to end
time.sleep(60 * 60)

# Stop the recording of the Zoom meeting and upload it to Google Drive
stop_recording_zoom_meeting()