from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os.path
from openai import OpenAI

load_dotenv()

# Update scopes to include both read and write permissions
SCOPES = [
    "https://www.googleapis.com/auth/documents",  # Full access to documents
]

DOCUMENT_ID = "1-Jx57aROf-10iVL1WVai2olCuMmT6er-DoVgsekXnXs"

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "DocAgent/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)
        
        # Retrieve the documents contents
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        print(f"The title of the document is: {document.get('title')}")
        
        

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 150,
                        'tabId': "t.m16nn6qb7h0"
                    },
                    'text': "Hello my name is hello"
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()
        print("Text inserted successfully")
        
    except HttpError as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    main()

