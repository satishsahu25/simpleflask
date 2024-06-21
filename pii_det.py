import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

def remove_sensitive_info(prompt):
    # Authenticate the client using key and endpoint 
    language_key = os.getenv("LANGUAGE_KEY")
    language_endpoint = os.getenv("LANGUAGE_ENDPOINT")
    client = TextAnalyticsClient(endpoint=language_endpoint, 
                                 credential=AzureKeyCredential(language_key),
                                 minimumPrecision=0.6
                                )
    
    allowed_categories = ['PersonType', 'DateTime', 'Quantity']
    # Detecting sensitive information (PII) from text 
    response = client.recognize_pii_entities([prompt], language="en")

    for doc in response: # Looping over 1 element list
        if doc.is_error:
            return prompt
        else:
            if len(doc.entities)==0:
                return prompt
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
