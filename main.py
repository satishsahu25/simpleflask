import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

app=Flask(__name__)
from langchain_openai import AzureChatOpenAI
import langchain

from dotenv import load_dotenv
load_dotenv()
import pickle

# from pii_det import remove_sensitive_info--------------------------------------------------------------

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

# -----PDF IMPORTS END--------
openai_apiverson=os.getenv("AZURE_OPENAI_VERSION") 
openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") 
openai_apikey=os.getenv("AZURE_OPENAI_API_KEY") 
openai_model_name=os.getenv("MODEL_DEPLOY_NAME")
embed_model=os.getenv("EMBED_MODEL_NAME")
embed_deploy_name=os.getenv("EMBED_DEPLOY_MODEL_NAME")
embed_endpoint=os.getenv("EMBED_ENDPOINT")
embed_openai_key=os.getenv("EMBED_OPENAI_KEY")


model=AzureChatOpenAI(
    openai_api_version=openai_apiverson,
    azure_deployment=openai_model_name,
    )

@app.route("/",methods=['GET'])
async def basic():
    return {"Hello, world!":"hi"}


@app.route("/ask",methods=['GET'])
async def basic_ask():
    prompt=request.args["query"]
    # prompt=remove_sensitive_info(query)-----------------------------------------
    result=model.invoke([prompt]).content
    return {"response": result}

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOADED_FILE_NAME=""
file_path=os.getenv("file_path")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(file_path, 'wb') as file:
                # Serialize and write the variable to the file
                pickle.dump("./"+filename, file)
    return "uploaded"



loaded_data = ""
@app.route("/rag",methods=["GET", "POST"])
async def rag():
            query=request.args["query"]
            # query=remove_sensitive_info(query)------------------------------------------------------------------
            # # loading--------------
            # Open the file in binary mode
            with open(os.getenv("file_path"), 'rb') as file:
                # Deserialize and retrieve the variable from the file
                loaded_data = pickle.load(file)
            # print(loaded_data)
            fileloader=PyPDFLoader(loaded_data)
            documents=fileloader.load() 
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
            docs = db.similarity_search(query,k=1)
            # print(docs)
            # text generation------------------------
            result=model.invoke([docs[0].page_content])
            return({"response":result.content})

# -------------------------------------------------------------------------
# from rag import RAG
# @app.route("/index",methods=["GET", "POST"])
# async def ragindex():
#     query=request.args["query"]
#     query=remove_sensitive_info(query)
#     return RAG(query) 


   
if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True, port=8000)
