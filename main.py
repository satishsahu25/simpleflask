# IMPORTANT
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# 

import os
from flask import Flask, request

from langchain_openai import AzureChatOpenAI
import langchain
from dotenv import load_dotenv
load_dotenv()

from flask_cors import CORS
app=Flask(__name__)
CORS(app)


#  -----PDF IMPORTS STARTS--------
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.messages import HumanMessage

from langchain_core.documents import Document
from rag import RAG
from az_cdb import save_conversation_history
from final_processing import construct_final_query
from pii_det import remove_sensitive_info
from extract_text_from_blob import extract_text

# -----PDF IMPORTS END-----------
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

@app.route("/", methods=['GET','POST','PUT'])
def basic():
    return {"Hello, world!": "hi"}

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate



# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are an assistant for question-answering tasks"),
#         ("human", "{input}"),
#     ]
# )

@app.route("/ask",methods=['GET','POST'])
def ask():
    query = request.args.get('query', default=None, type=str)
    user_id = request.args.get('user_id', default=None, type=str)
    file_url = request.args.get('file_url', default="x", type=str)
    if file_url != "x":
        documents = extract_text(file_url)
        # return {"response": documents}
        try:
            if documents==None:
                 return {"response": "Not a txt/pdf file!"}
            else:
                
                # chunking --------------
                text_splitter = CharacterTextSplitter(chunk_size=800,chunk_overlap=20)
                texts = text_splitter.split_documents(documents) 
                # embeddings-------------
                # return {"resp":embed_model+embed_deploy_name+embed_endpoint+embed_openai_key+openai_apiverson}
                embeddings = AzureOpenAIEmbeddings(
                                                    model=embed_model,
                                                    azure_deployment=embed_deploy_name,
                                                    azure_endpoint=embed_endpoint,
                                                    openai_api_key=embed_openai_key,
                                                    openai_api_version=openai_apiverson
                                                )
                # return {"response":embeddings}
                db = Chroma.from_documents(documents=texts, embedding=embeddings)
                # docs = db.similarity_search(query, k=1)
                # return {"response":docs}
                retriever=db.as_retriever()
                question_answer_chain = create_stuff_documents_chain(model, ChatPromptTemplate.from_messages(
    [
        ("system", "You are an assistant for question-answering tasks"),
        ("human", "{input}"),
    ]
))
                rag_chain = create_retrieval_chain(retriever, question_answer_chain)
                results = rag_chain.invoke({"input": query})
                return {"response":results} 
                # print(docs)
                # text generation------------------------
                final_query, buffer = construct_final_query(user_id, query, docs[0].page_content)
                final_query = "Below is the past conversation history and relevant documents retrieved from a knowledge base." + f"\n{final_query}\n If the answer is not present in the chat history or provided documents, give the answer from your own knowledge.\n So, the answer is:"
                result = model.invoke([HumanMessage(content=final_query)])
                answer = result.content
                # print(answer)
                # Update/save coversation history------------------------
                if buffer:
                    new_entry = f"Q: {query}\nA: {answer}"
                    buffer.append(new_entry)
                    save_conversation_history(user_id, buffer)
                else:
                    new_entry = [f"Q: {query}\nA: {answer}"]
                    save_conversation_history(user_id, new_entry)
                return {"response":answer}
        except:
                return {"response": "error in getting file"}
    else:
            query = remove_sensitive_info(query)
            return {"response": RAG(query, user_id)}


if __name__ == '__main__':
  app.run(host="0.0.0.0", debug=True, port=8000)
