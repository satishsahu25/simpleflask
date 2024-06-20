from flask import Flask, request
import os
app=Flask(__name__)
from langchain_openai import AzureChatOpenAI
import langchain
from dotenv import load_dotenv
load_dotenv()
import pickle
# from fastapi.middleware.cors import CORSMiddleware
# -------PDF UPLOAD ISTARTS---------
# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse


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
# openai_apiverson=os.environ["AZURE_OPENAI_VERSION"] 
# openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"] 
# openai_apikey=os.environ["AZURE_OPENAI_API_KEY"] 
# openai_model_name=os.environ["MODEL_DEPLOY_NAME"]
# embed_model=os.environ["EMBED_MODEL_NAME"]
# embed_deploy_name=os.environ["EMBED_DEPLOY_MODEL_NAME"]
# embed_endpoint=os.environ["EMBED_ENDPOINT"]

openai_apiverson=os.getenv"AZURE_OPENAI_VERSION"] 
openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"] 
openai_apikey=os.environ["AZURE_OPENAI_API_KEY"] 
openai_model_name=os.environ["MODEL_DEPLOY_NAME"]
embed_model=os.environ["EMBED_MODEL_NAME"]
embed_deploy_name=os.environ["EMBED_DEPLOY_MODEL_NAME"]
embed_endpoint=os.environ["EMBED_ENDPOINT"]

model=AzureChatOpenAI(
    openai_api_version=openai_apiverson,
    azure_deployment=openai_model_name,
    )

@app.route("/",methods=['GET'])
def hell():
    return "Hello, world!"

@app.route("/ask",methods=['GET'])
def hell():
    print(openai_apiverson)
    return {openai_apiverson}
    
@app.route("/api",methods=['GET'])
def hell():
    print(openai_endpoint)
    return {openai_endpoint}

# @app.route("/ask",methods=['GET'])
# async def ask():
#     prompt=request.args
#     result=model.invoke([prompt])
#     return({"response":result["content"]})
   
