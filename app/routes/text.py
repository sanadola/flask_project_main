from flasgger import swag_from
from flask import request, jsonify
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
import nltk
from transformers import pipeline
import gensim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import io
import base64

from app.utils.auth_helpers import check_token_revoked

text_api = Blueprint('text_api', __name__)

# Download NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')


# =============================================================================================================
#                                                      Summarize the Text
# ==============================================================================================================

@text_api.route('/summarize_text', methods=['POST'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Text'],
    'summary': 'summarize_text',
    'description': 'summarize_text from the text',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'},

                },
                'required': ['text']}}
    ],
    'responses': {
        200: {
            'description': 'summarize_text from the text',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                                'summary': {'summary': 'string'},
                    },

                }
            }
        }
    },
    'security': [{'Bearer': []}]})

def summarize_text():
    data = request.get_json()
    text = data.get('text')

    # Use Transformers' summarization pipeline
    summarizer = pipeline("summarization")
    summary = summarizer(text)[0]['summary_text']

    return jsonify({'summary': summary})

# ======================================================================================================================
#                                               Extract the keywords from text
# ======================================================================================================================

@text_api.route('/extract_keywords', methods=['POST'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Text'],
    'summary': 'extract_keywords',
    'description': 'extract_keywords from the text',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'},

                },
                'required': ['text']}}
    ],
    'responses': {
        200: {
            'description': 'extract_keywords from the text',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'keywords': {'keywords': 'string'},


                            }
                        }
                    },

                }
            }
        }
    },
    'security': [{'Bearer': []}]
})
def extract_keywords():
    data = request.get_json()
    text = data.get('text')

    # Use Gensim's TF-IDF and NMF for keyword extraction
    docs = [text]
    dictionary = gensim.corpora.Dictionary(docs)
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    tfidf = gensim.models.TfidfModel(corpus)
    nmf = gensim.models.Nmf(tfidf[corpus], num_topics=5)

    topic_words = []
    for topic in nmf.show_topics(formatted=False):
        topic_words.append([word for word, _ in topic])

    return jsonify({'keywords': topic_words})



# =====================================================================================================================
#                                                         Anaylyze the Text
# =====================================================================================================================

@text_api.route('/analyze_sentiment', methods=['Post'])
@jwt_required()
@check_token_revoked
@staticmethod
@swag_from({
    'tags': ['Text'],
    'summary': 'analyze_sentiment',
    'description': 'analyze_sentiment from the text',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'Text': {'type': 'string'},

        },
                'required': ['text']}}
    ],
    'responses': {
        200: {
            'description': 'analyze_sentiment from the text',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'sentiment': {'sentiment': 'string'},
                                'confidence': {'confidence': 'string'},

                            }
                        }
                    },

                }
            }
        }
    },
    'security': [{'Bearer': []}]
})
def analyze_sentiment():
    data = request.get_json()
    text = data.get('text')

    # Use Transformers' sentiment analysis pipeline
    sentiment_analyzer = pipeline("sentiment-analysis")
    result = sentiment_analyzer(text)[0]

    return jsonify({'sentiment': result['label'], 'confidence': result['score']})




# ===================================================================================================================
#                                                       TSNE Display from Text
# ===================================================================================================================

@text_api.route('/tsne_display', methods=['Post'])
@jwt_required()
@check_token_revoked
@swag_from({
    'tags': ['Text'],
    'summary': 'tsne_display',
    'description': 'tsne_display from the text',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'Text': {'type': 'string'},

                },
                'required': ['text']}}
    ],
    'responses': {
        200: {
            'description': 'tsne_display from the text',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                                'image_base64': {'image_base64': 'string'},
                    },

                }
            }
        }
    },
    'security': [{'Bearer': []}]})

def tsne_display():
    data = request.get_json()
    texts = data.get('texts')

    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    # Apply T-SNE
    tsne = TSNE(n_components=2, random_state=0)
    X_embedded = tsne.fit_transform(X.toarray())

    # Plot the results
    plt.figure(figsize=(8, 6))
    plt.scatter(X_embedded[:, 0], X_embedded[:, 1])

    # Convert plot to base64 image
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    image_base64 = base64.b64encode(img_buf.read()).decode('utf-8')

    return jsonify({'image_base64': image_base64})

