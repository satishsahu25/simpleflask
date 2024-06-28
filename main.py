import os
from flask import Flask, request
from pii_det import remove_sensitive_info

from langchain_openai import AzureChatOpenAI
import langchain
from dotenv import load_dotenv
load_dotenv()


app=Flask(__name__)


# # -----PDF IMPORTS STARTS--------
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.messages import HumanMessage

import requests
import io
import pdfplumber

from langchain_core.documents import Document
# from new_download import getpdf
from rag import RAG
from az_cdb import save_conversation_history
from final_processing import construct_final_query

# -----PDF IMPORTS END--------
openai_apiverson=os.getenv("AZURE_VERSION") 
openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") 
openai_apikey=os.getenv("AZURE_OPENAI_API_KEY") 
openai_model_name=os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME")
embed_model=os.getenv("EMBED_MODEL_NAME")
embed_deploy_name=os.getenv("EMBED_DEPLOY_MODEL_NAME")
embed_endpoint=os.getenv("EMBED_ENDPOINT")
embed_openai_key=os.getenv("EMBED_OPENAI_KEY")

model=AzureChatOpenAI(
    openai_api_version=openai_apiverson,
    azure_deployment=openai_model_name,
    api_key=openai_apikey
    )


def getpdf(url):
        # Load PDF from the BytesIO stream
    response = requests.get(url)
    response.raise_for_status()
    pdf_stream = io.BytesIO(response.content)
    documents = []

    with pdfplumber.open(pdf_stream) as pdf:
        for pgno,page in enumerate(pdf.pages):
            # Extract text or structured data from each page
            text = page.extract_text()
            document = Document(
            page_content=text,
            metadata={"source": url,"page":pgno}
            )
            documents.append(document)  # Each page's text is treated as a separate document
    return documents


@app.route("/")
async def hell():
    return {"Hello, world!":"hi"}


@app.route("/ask",methods=['GET','POST'])
def ask():
                query = request.args.get('query', default=None, type=str)
                user_id = request.args.get('user_id', default=None, type=str)
                file_url = request.args.get('file_url', default="", type=str)
                if file_url != "":
                    documents=getpdf(file_url)
                    # # chunking ---------
                    text_splitter=CharacterTextSplitter(chunk_size=800,chunk_overlap=20)
                    texts=text_splitter.split_documents(documents) 
                    # embeddings-------------
                    embeddings= AzureOpenAIEmbeddings(
                                                        model=embed_model,
                                                        azure_deployment=embed_deploy_name,
                                                        azure_endpoint=embed_endpoint,
                                                        openai_api_key=embed_openai_key,
                                                        openai_api_version=openai_apiverson
                                                    )
                    db=Chroma.from_documents(texts, embeddings)
                    docs = db.similarity_search(query, k=2)
                    print(docs)
                    # text generation------------------------
                    final_query, buffer = construct_final_query(user_id, query, docs[0].page_content)
                    final_query = "Below is the past conversation history and relevant documents retrieved from a knowledge base." + f"\n{final_query}\n If the answer is not present in the chat history or provided documents, give the answer from your own knowledge.\n So, the answer is:"
                    result = model.invoke([HumanMessage(content=final_query)])
                    answer = result.content
                    # Update/save coversation history------------------------
                    if buffer:
                        new_entry = f"Q: {query}\nA: {answer}"
                        buffer.append(new_entry)
                        save_conversation_history(user_id, buffer)
                    else:
                        new_entry = [f"Q: {query}\nA: {answer}"]
                        save_conversation_history(user_id, new_entry)
                    return ({"response": answer})
                else:
                    query=remove_sensitive_info(query)
                    return ({"response":RAG(query, user_id)})
    
if __name__ == '__main__':
  app.run(debug=True)
