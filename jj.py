import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import zoomus
import os
from googleapiclient.http import MediaFileUpload

# Define your functions for starting and stopping Zoom meetings and recording
def start_zoom_meeting():
    # Create a Zoom client object with your Zoom API key and secret
    client = zoomus.ZoomClient('1R2i8fIcTOKZgR59xVXDgA', 'qRqw2dEAxDkn8fZjm98aqmo7eMkE2WwbeQDo')

    # Create a new Zoom meeting with the desired settings
    meeting = client.meeting.create(user_id='me', topic='Zoom Meeting', type=2, start_time='now', duration=60)

    # Start the Zoom meeting
    client.meeting.start(meeting_id=meeting['id'])

    # Start recording the Zoom meeting
    client.recording.start(meeting_id=meeting['id'])

def stop_zoom_meeting():
    # Create a Zoom client object with your Zoom API key and secret
    client = zoomus.ZoomClient('1R2i8fIcTOKZgR59xVXDgA', 'qRqw2dEAxDkn8fZjm98aqmo7eMkE2WwbeQDo')

    # Stop the recording of the Zoom meeting
    client.recording.stop(meeting_id='YOUR_MEETING_ID')

    # End the Zoom meeting
    client.meeting.end(meeting_id='YOUR_MEETING_ID')

def record_zoom_meeting():
    # Create a Zoom client object with your Zoom API key and secret
    client = zoomus.ZoomClient('1R2i8fIcTOKZgR59xVXDgA', 'qRqw2dEAxDkn8fZjm98aqmo7eMkE2WwbeQDo')

    # Get the recording files for the Zoom meeting
    recordings = client.recording.list(meeting_id='YOUR_MEETING_ID')

    # Download the first recording file to the local file system
    recording_url = recordings['recording_files'][0]['download_url']
    recording_file = requests.get(recording_url)
    with open('recording.mp4', 'wb') as f:
        f.write(recording_file.content)

def upload_to_google_drive():
    # Authenticate with the Google Drive API using your credentials file
    creds = Credentials.from_authorized_user_file('/path/to/credentials.json', ['https://www.googleapis.com/auth/drive'])

    # Create a Google Drive API client object
    service = build('drive', 'v3', credentials=creds)

    # Upload the recorded Zoom meeting to Google Drive
    file_metadata = {'name': 'recording.mp4'}
    media = MediaFileUpload('recording.mp4', mimetype='video/mp4')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Get the link to the uploaded file
    file_id = file.get('id')
    file_url = f'https://drive.google.com/file/d/{file_id}/view'

    # Delete the local recording file
    os.remove('recording.mp4')

    # Return the link to the uploaded file
    return file_url

# Define your command handlers for the Telegram bot
def start_handler(update, context):
    # Call the function to start the Zoom meeting and recording
    start_zoom_meeting()

    # Send a message to the user to let them know the meeting has started
    context.bot.send_message(chat_id=update.effective_chat.id, text="Zoom meeting started. Recording in progress.")

def stop_handler(update, context):
    # Call the function to stop the Zoom meeting and recording
    stop_zoom_meeting()

    # Call the function to download the recorded meeting and save it to a file
    record_zoom_meeting()

    # Call the function to upload the recorded meeting to Google Drive
    file_url = upload_to_google_drive()

    # Send a message to the user with a link to the recorded meeting on Google Drive
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Zoom meeting stopped. Recording saved to Google Drive: {file_url}")

# Create an instance of the Telegram bot using your bot token
bot = telegram.Bot(token='6099582498:AAEKh_BuTfhzU_n0cf2586qPi593jfea8Wk')

# Create an instance of the Updater class with your Telegram bot token
#updater = Updater(token='6099582498:AAEKh_BuTfhzU_n0cf2586qPi593jfea8Wk', use_context=True)


# Create an instance of the Updater class with your Telegram bot token
updater = Updater('6099582498:AAEKh_BuTfhzU_n0cf2586qPi593jfea8Wk')



# Get the dispatcher to register command handlers
dp = updater.dispatcher

# Register your command handlers with the dispatcher
dp.add_handler(CommandHandler("start", start_handler))
dp.add_handler(CommandHandler("stop", stop_handler))

# Start the bot
updater.start_polling()

# Run the bot until Ctrl-C is pressed or the process receives SIGINT, SIGTERM or SIGABRT
updater.idle()