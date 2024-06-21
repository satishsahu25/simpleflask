# ---------------Importing libraries----------------------------#
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from classify_query import extract_features, classify_text

# ---------------Fetch credentials------------------------------#
load_dotenv()
search_service_endpoint = os.getenv("AI_SEARCH_ENDPOINT")
api_key = os.getenv("AI_SEARCH_APIKEY")
indexer_name = os.getenv("INDEXER_NAME")
index_name = os.getenv("INDEX_NAME")

azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
chat_deployment_name = os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME")
embedding_deployment_name = os.getenv("EMBEDDINGS_DEPLOYMENT_NAME")



# -----------Initializing Azure services clients----------------#
search_client = SearchClient(endpoint=search_service_endpoint, 
                             index_name=index_name, 
                             credential=AzureKeyCredential(api_key)
                            )
azure_openai_client = AzureOpenAI(azure_endpoint=azure_openai_endpoint,
                                  api_key=azure_openai_api_key,
                                  api_version="2024-02-01"
                                 )

#-------------------------Helper functions----------------------#
def get_embeddings(query: str):
    embedding = azure_openai_client.embeddings.create(input=[query], model=embedding_deployment_name)
    return embedding.data[0].embedding

def retrieval(query: str, vector_query, category: str):
    # Hybrid search without reranking
    if category=='simple':
        results_vec = search_client.search(search_text=None,  
                                           vector_queries=[vector_query],
                                           select=["title", "chunk"], # The list of fields to retrieve. If unspecified, all fields marked as retrievable are included.
                                           search_fields=['chunk']
                                        )
        return results_vec
    elif category=='intermediate':
        results_hyb = search_client.search(search_text=query,  
                                           vector_queries=[vector_query],
                                           select=["title", "chunk"], 
                                           top=10, # For keyword search
                                           search_fields=['chunk']
                                        )
        return results_hyb
    elif category=='complex':
        # Run a hybrid query with semantic reranking
        results_hyb_rerank = search_client.search(search_text=query,  
                                                  vector_queries=[vector_query],
                                                  select=["title", "chunk"], 
                                                  top=10,
                                                  search_fields=['chunk'],
                                                  query_type='semantic', 
                                                  semantic_configuration_name='test-semantic-config',
                                                  query_caption='extractive'
                                                )
        return results_hyb_rerank

system_prompt = "You are a helpful assistant. You are well-versed in logical reasoning and answering user queries."
query_prompt = "Here is the question provided by the user: "
knowledge_base_prompt = "Below are the relevant contextual documents retrieved from a knowledge base according to the query.\
Use this as the basis of your answer. Keep in mind that there may be some overlap of the corresponding documents' content"
def generate_response(query: str, docs):
    completion = azure_openai_client.chat.completions.create(
                 model=chat_deployment_name,
                 temperature=0,
                 messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"{query_prompt}{query}\n{knowledge_base_prompt}:\n{docs}\nAnswer: "
                    }
                 ]
            )
    answer = completion.choices[0].message.content
    return answer

#-------------------------Main RAG function-----------------------#
def RAG(query: str):
    # Classifiy the query
    features = extract_features(query)
    category = classify_text(features)

    # Vectorize the query
    vector_query = VectorizedQuery(vector=get_embeddings(query), 
                                   k_nearest_neighbors=10, 
                                   fields="text_vector",
                                   exhaustive=False, # When true, triggers an exhaustive k-nearest neighbor search across all vectors within the vector index.
                                  )
    # Fetch the top k results
    k = 5
    results = retrieval(query, vector_query, category)
    top_results = [result["chunk"] for i, result in enumerate(results) if i<k]

    # Construct the input for the GPT model
    docs = "\n\n".join(f"Document-{i+1}:\n{doc}" for i, doc in enumerate(top_results))

    answer = generate_response(query, docs)
    return answer