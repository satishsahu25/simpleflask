import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from pii_det import remove_sensitive_info

app=Flask(__name__)
from langchain_openai import AzureChatOpenAI
import langchain

from dotenv import load_dotenv
load_dotenv()
import pickle

# -------PDF UPLOAD ISTARTS---------
# from fastapi import FastAPI, File, UploadFile

# # -----PDF IMPORTS STARTS--------
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import VectorDBQA
from langchain_openai import AzureOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

import requests
import io
import pdfplumber

from langchain_core.documents import Document

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
        # print("gdfsgfdf")
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

from new_download import getpdf


@app.route("/ask",methods=['GET','POST'])
def ask():
                query = request.args.get('content', default=None, type=str)
                # query = "what is deep work?"
                conversation_id = request.args.get('conversation_id', default=None, type=str)
                user_id = request.args.get('user_id', default=None, type=str)
                file_url = request.args.get('file_url', default=None, type=str)
                if file_url is not None:
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
                    db=Chroma.from_documents(texts,embeddings)
                    docs = db.similarity_search(query,k=2)
                    print(docs)
                    # text generation------------------------
                    result=model.invoke([HumanMessage(content=docs[0].page_content)])
                    return ({"response":result.content})
                else:
                    pass
    
    
from rag import RAG

@app.route("/index",methods=["GET", "POST"])
async def ragindex():
    query=request.args["query"]
    query=remove_sensitive_info(query)
    return RAG(query)  
   
if __name__ == '__main__':
  app.run(debug=True)
