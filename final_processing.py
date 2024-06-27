#------------------------Importing libraries----------------------------#
from az_cdb import get_conversation_history, save_conversation_history
from chat_memory import seperate_recent_chats_from_buffer, summarize_conversation

def construct_final_query(user_id, query, documents):
    # Handling chat history management -- Summarizing old conversations and appending recent conversations
    buffer = get_conversation_history(user_id)
    if buffer:
        summarizable_buffer, recent_chats = seperate_recent_chats_from_buffer(buffer)
        if summarizable_buffer:
            summary = summarize_conversation(summarizable_buffer)
            memory = "Summary of old conversations:\n" + summary + "\n\nRecent conversations:\n"+ "\n".join(recent_chats)
        else:
            memory = "\nRecent conversations:\n" + "\n".join(recent_chats)
    else:
        memory = "[No past conversations]"
        buffer = None
        
    # Prepare the context with chat history and the latest query and documents
    context = memory + f"\n\nUseful docs to answer the question:\n{documents}" + f"\n\nUsing the above context, answer the following question: {query}"
    return context, buffer
