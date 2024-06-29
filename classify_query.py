# ---------------Importing libraries----------------------------#
import numpy as np
import spacy
# from nltk import tokenize
nlp = spacy.load("en_core_web_sm") # Load SpaCy model

def lexical_density(doc):
    content_words = [token for token in doc if token.pos_ in {'NOUN', 'VERB', 'ADJ', 'ADV'}]
    return len(content_words)/len(doc)

def max_syntactic_tree_depth(node, depth):
    if node.n_lefts + node.n_rights > 0:
        return max(max_syntactic_tree_depth(child, depth + 1) for child in node.children)
    else:
        return depth

def extract_features(query: str):
    doc = nlp(query)
    sentences = list(doc.sents) # tokenize.sent_tokenize()
    features = {
        "num_sentences": len(sentences),
        "lexical_density": lexical_density(doc),
        "syntactic_tree_depth": [max_syntactic_tree_depth(sent.root, 0) for sent in doc.sents][0],
        "named_entity_count": len(doc.ents),

    }
    return features

def classify_text(features):
    if features["num_sentences"]<=2 and features['lexical_density']<0.4 and features["syntactic_tree_depth"]<=6 :
        return "simple"
    elif (features["num_sentences"]>2 and features["num_sentences"]<=4) and (features['lexical_density']>=0.4 and features['lexical_density']<0.65) and (features["syntactic_tree_depth"]>6 and features["syntactic_tree_depth"]<=8) and (features["named_entity_count"]>=2 and features["named_entity_count"]<4):
        return "intermediate"
    elif features["num_sentences"]>4 and features['lexical_density']>=0.65 and features["syntactic_tree_depth"]>8 and features["named_entity_count"]>4:
        return "complex"
    else:
        return "complex"
    
    
