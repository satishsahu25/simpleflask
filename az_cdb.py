#-----------------------Importing libraries--------------------#
import os
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
load_dotenv()

#-------------Setting up Cosmos DB configuration---------------#
endpoint = os.getenv("AZURE_COSMOS_DB_ENDPOINT")
key = os.getenv("AZURE_COSMOS_DB_PRIMARY_KEY")
database_name = os.getenv("AZURE_COSMOS_DB_DATABASE_NAME")
container_name = os.getenv("AZURE_COSMOS_DB_CONTAINER_NAME")

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

#-----------Function to retrieve conversation history----------#
def get_conversation_history(user_id):
    try:
        buffer_item = container.read_item(item=user_id, partition_key=user_id)
        buffer = buffer_item['text']
    except exceptions.CosmosResourceNotFoundError:
        buffer = None
    return buffer

#-----------Function to save conversation history--------------#
def save_conversation_history(user_id, buffer):
    buffer_item = {
        'id': user_id,
        'userId': user_id,  # Ensure this field matches the partition key
        'text': buffer
    }
    container.upsert_item(buffer_item)