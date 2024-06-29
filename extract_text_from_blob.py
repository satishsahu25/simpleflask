import os
from io import BytesIO
import pdfplumber
from azure.storage.blob import BlobClient
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

# Fetching the credentials
account_key = os.getenv('AZURE_BLOB_STORAGE_ACCOUNT_KEY')

def extract_text(blob_url: str):
    # Create a BlobClient object using the blob URL
    blob_client = BlobClient.from_blob_url(blob_url, credential=account_key)
    # Determine the type of file
    file_type = blob_url.split('.')[-1]

    blob_content=[]

    # For txt file
    if file_type=='txt':
        text = blob_client.download_blob().readall().decode('utf-8') # Download the blob content and store it in a variable
        blob_content.append(Document(page_content=text, metadata={"source": blob_url}))
        # print(blob_content)

    # For pdf file
    elif file_type=='pdf':
        blob_pdf = blob_client.download_blob()
        
        stream = BytesIO()
        blob_pdf.download_to_stream(stream)

        with pdfplumber.open(stream) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text or structured data from each page
                text = page.extract_text()
                # return {"response":text}
                document = Document(
                                    page_content=text,
                                    metadata={"source": blob_url, "page": page_num}
                                   )
                blob_content.append(document)  # Each page's text is treated as a separate document
    
    # For other file types
    else:
        blob_content = None

    return blob_content
