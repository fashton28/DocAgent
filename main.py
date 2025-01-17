from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os
from openai import OpenAI

#Load environment variables
load_dotenv()

# Your AI-AGENT Writing Assitant.
#We don't do the writing for you. We are all about the ideation and enhancing your creative process.
#Learn as you write
#Writing and writing-knnots --> If you're thinking without writing, you only think you're thinking.
#Write to think. Think to write. 


# Verify API key is available immediately after loading
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    #Raise Value when API KEY not found.
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Update scopes to the correct format --> Scopes define the access the API has to our Google Doc files.
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]


DOCUMENT_ID = "1-Jx57aROf-10iVL1WVai2olCuMmT6er-DoVgsekXnXs"


#Getting
def get_end_index(service, document_id):
    document = service.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content')
    
    end_index = 1
    for element in content:
        if 'endIndex' in element:
            end_index = max(end_index, element['endIndex'])
    print(f"this is the end Index: {end_index}")
    return end_index

def get_all_paragraphs(service, document_id):
    """Get all paragraphs as a list of tuples (index, text)"""
    document = service.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content')
    
    paragraphs = [] 
    current_index = 1  # Google Docs indices start at 1
    
    for element in content:
        if 'paragraph' in element:
            text = ''
            # Get the startIndex from the paragraph element
            start_index = element.get('startIndex', current_index)
            
            for text_run in element['paragraph']['elements']:
                if 'textRun' in text_run:
                    text += text_run['textRun']['content']
            
            if text.strip():  # Only add non-empty paragraphs
                paragraphs.append((start_index, text))
            
            current_index = element.get('endIndex', current_index)
    
    return paragraphs

def main():
    creds = None
    # Update the path to where your credentials.json actually is
    CREDENTIALS_PATH = "/Users/fashton/Desktop/DocAgent/DocAgent/credentials.json"  # If it's in the root directory
    # or use absolute path if needed
    # CREDENTIALS_PATH = "/Users/fashton/Desktop/DocAgent/credentials.json"

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)
        
        # Get all paragraphs with their indices
        paragraphsChoose = []
        textChoose = []
        paragraphs = get_all_paragraphs(service, DOCUMENT_ID)
        for index, text in paragraphs:
            paragraphsChoose.append(index)
            textChoose.append(text)#Potentially change into dictionary
            print(f"Index {index}:", text)
        # Retrieve the documents contents
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        print(f"The title of the document is: {document.get('title')}")
        get_end_index(service, DOCUMENT_ID)
        
        
        # Initialize the OpenAI client with the pre-verified API key
        client = OpenAI(api_key=api_key)
        # paragraph = int(input("Write down the paragraph you want to analyze? ")) - 1
        # action  = (input("What action do you want to Perform? "))
        # Make a chat completion request using the new client format
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate greate ideas for people to get unstuck while writing. Perhaps I get stuck because i don't know what to write about, you help me with ideas."},
                {"role": "user", "content": f"Please give me some ideas in the form of bullet points based on the following prompt: {textChoose[len(textChoose) - 1]}. "}
            ],
            max_tokens= 200
        )
        
        # Print the response (updated to match new response format)
        agentResponse = (completion.choices[0].message.content)
        
        requests = [
            # {
            #     'deleteContentRange': {
            #         'range': {
            #             'startIndex': paragraphsChoose[paragraph],
            #             'endIndex': paragraphsChoose[paragraph] + len(textChoose[paragraph])
            #         }
            #     }
            # },
            {
                'insertText': {
                    'location': {
                        'index': get_end_index(service, DOCUMENT_ID) - 1 ,
                        'tabId': "t.0"
                    },
                    'text': f"{agentResponse}"
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
    

