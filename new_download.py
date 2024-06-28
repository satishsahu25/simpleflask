import requests
import io
import pdfplumber

from langchain_core.documents import Document

def getpdf(url):
    try:
                # Load PDF from the BytesIO stream
        response = requests.get(url)
        response.raise_for_status()
        print(response.content)
        return "hi"
        # pdf_stream = io.BytesIO(response.content)
        # documents = []

        # with pdfplumber.open(pdf_stream) as pdf:
        #     # print("gdfsgfdf")
        #     for pgno,page in enumerate(pdf.pages):
        #         # Extract text or structured data from each page
        #         text = page.extract_text()
        #         document = Document(
        #         page_content=text,
        #         metadata={"source": url,"page":pgno}
        #         )
        #         documents.append(document)  # Each page's text is treated as a separate document
        # return documents
    except requests.RequestException as e:
        return {'error': str(e)}, 500
