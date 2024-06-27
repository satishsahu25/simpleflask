#------------------------Importing libraries----------------------------#
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

#--------------------Setting up Azure OpenAI creds----------------------# 
azure_openai_client = AzureOpenAI(azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                  api_version=os.getenv("AZURE_VERSION")
                                 )

#--------------------------Summarization part---------------------------#
def summarize_conversation(summarizable_buffer):
    summary_prompt="Following is the list of question-answer pairs in a conversation. Summarize them\
                    in a SINGLE CONCISE paragraph."
    summarizable_buffer_str = "\n".join(summarizable_buffer)
    completion = azure_openai_client.chat.completions.create(
                 model=os.getenv("CHAT_COMPLETIONS_DEPLOYMENT_NAME"),
                 temperature=0,
                 messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": summary_prompt + f":\n{summarizable_buffer_str}\n\nSummary:"
                    }
                 ]
            )
    summary = completion.choices[0].message.content
    return summary

#-------------Seperate recent chats from old chats part-----------------#
def seperate_recent_chats_from_buffer(buffer, buffer_size=5, summary_size=10):
    if len(buffer)<=buffer_size: # Edge case
        return None, buffer
    else:
        summary = "\n".join(buffer[:-buffer_size])
        return summary, buffer[-buffer_size:] # Hybrid memory management