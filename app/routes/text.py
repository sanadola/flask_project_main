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
from nltk.tokenize import word_tokenize

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
import spacy
import gensim
from gensim import corpora
from gensim.models import TfidfModel, Nmf
nlp = spacy.load('en_core_web_sm')

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
                'required': ['text']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'extract_keywords from the text',
            'schema': {
                'type': 'object',
                'properties': {
                    'keywords': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        }
    },
    'security': [{'Bearer': []}]
})
def extract_keywords():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Process text using spaCy for tokenization and lemmatization
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]

    if not tokens:
        return jsonify({'error': 'No valid tokens found in the text'}), 400

    # Create a Gensim dictionary and corpus
    dictionary = corpora.Dictionary([tokens])  # List of tokens as the document
    corpus = [dictionary.doc2bow(tokens)]  # List of documents (one document in this case)

    # Check if corpus is empty or has zero variance
    if not corpus or all(len(doc) == 0 for doc in corpus):
        return jsonify({'error': 'Corpus has no valid terms after preprocessing'}), 400

    try:
        # Apply TF-IDF model to the corpus
        tfidf_model = TfidfModel(corpus)
        tfidf_corpus = tfidf_model[corpus]

        # Fit the NMF model
        nmf_model = Nmf(tfidf_corpus, num_topics=5, id2word=dictionary)

        # Extract top words for each topic
        topic_words = []
        for topic_id, topic in nmf_model.show_topics(formatted=False, num_words=5):
            topic_words.append([word for word, _ in topic])

        # Return keywords as the top words of the topics
        return jsonify({'keywords': topic_words})

    except ZeroDivisionError:
        return jsonify({'error': 'Model encountered a division by zero error during processing'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================================================================================
#                                                         Anaylyze Sentiment the Text
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

    # Check if text is provided
    if not text:
        return jsonify({"error": "Text is required"}), 400

    # Explicitly specify the model for sentiment analysis (optional but recommended for production)
    sentiment_analyzer = pipeline("sentiment-analysis",
                                  model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

    # Perform sentiment analysis
    result = sentiment_analyzer(text)[0]

    # Return the sentiment and confidence score in the expected format
    return jsonify({
        'data': [{
            'sentiment': result['label'],
            'confidence': result['score']
        }]
    })
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
    texts = data.get('text')

    if not texts or not isinstance(texts, list):
        return jsonify({'error': 'Texts must be a list of strings'}), 400

    # Get the number of samples (documents)
    n_samples = len(texts)

    # Check if there are enough samples to proceed
    if n_samples < 2:
        return jsonify({'error': 'At least two documents are required for t-SNE.'}), 400

    # Create the TF-IDF matrix
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    # Dynamically adjust perplexity to be less than n_samples
    perplexity = min(30, n_samples - 1)  # Ensure perplexity is less than n_samples

    # Apply t-SNE with the adjusted perplexity
    tsne = TSNE(n_components=2, random_state=0, perplexity=perplexity)
    X_embedded = tsne.fit_transform(X.toarray())

    # Plot the results
    plt.figure(figsize=(8, 6))
    plt.scatter(X_embedded[:, 0], X_embedded[:, 1])

    # Convert plot to base64 image
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    image_base64 = base64.b64encode(img_buf.read()).decode('utf-8')

    # Return the base64 encoded image as part of the response
    return jsonify({'image_base64': image_base64})

