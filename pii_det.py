import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

language_key = os.getenv("LANGUAGE_KEY")
language_endpoint = os.getenv("LANGUAGE_ENDPOINT")

def remove_sensitive_info(prompt):
    # Authenticate the client using key and endpoint 
    client = TextAnalyticsClient(endpoint=language_endpoint, 
                                 credential=AzureKeyCredential(language_key),
                                 minimumPrecision=0.6
                                )
    
    allowed_categories = ['PersonType', 'DateTime', 'Quantity']
    # Detecting sensitive information (PII) from text 
    response = client.recognize_pii_entities([prompt], language="en")

    for doc in response: # Looping over 1 element list
        if doc.is_error:
            return "\nNo sensitive information was detected, safe."
        else:
            idx = 0
            new_prompt = ""
            # print("Redacted Text: {}".format(doc.redacted_text))
            for entity in doc.entities:
                if entity.category not in allowed_categories:
                    new_prompt += prompt[idx:entity.offset] + '[.]'
                    idx = entity.offset + entity.length
            new_prompt += prompt[idx:]
            return new_prompt

# prompt = "The employee's name is Rosie and her SSN is 859-98-0987. Hello there. I am a bus driver. Today is 4th July. I am in my 60s."
# print(remove_sensitive_info(prompt))