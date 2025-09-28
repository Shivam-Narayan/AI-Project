from django.shortcuts import render
import torch
from sentence_transformers import SentenceTransformer, util
import pickle
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from googletrans import Translator
from deep_translator import GoogleTranslator



MODEL_PATH = os.getenv("MODEL_PATH", "bot/Finance_preprocessed_data.pkl")

def home(request):
    return render(request, 'home.html')

# Create your views here.
def training(request):
    return render(request, 'bot_train.html')

# Load the embedding model (required for querying)
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# Load preprocessed data (embeddings, chunks, etc.)
def load_preprocessed_data(file_path: str):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data['embeddings'], data['chunks']

# Function to retrieve relevant resources based on query
def retrieve_relevant_resources(query: str, embeddings: torch.Tensor, model: SentenceTransformer, n_resources_to_return: int = 5):
    query_embedding = model.encode(query, convert_to_tensor=True)
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    scores, indices = torch.topk(input=dot_scores, k=n_resources_to_return)
    return scores, indices

# Function to display top results
def display_top_results(query: str, embeddings, chunks, n_resources_to_return: int = 5):
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, model=embedding_model, n_resources_to_return=n_resources_to_return)
    results = []
    for score, index in zip(scores, indices):
        chunk = chunks[index]["sentence_chunk"]
        page_number = chunks[index]['page_number']
        results.append((score, chunk, page_number))
    return results

# @csrf_exempt
# def query(request):
#     # Load preprocessed data
#     # embeddings, chunks = load_preprocessed_data(r"bot/Finance_preprocessed_data.pkl")
#     embeddings, chunks = load_preprocessed_data(MODEL_PATH)

#     if request.method == "POST":
#         try:
#             if request.headers.get('Content-Type') == 'application/json':  # Check if the request is JSON
#                 # Handle JSON response for Postman
#                 data = json.loads(request.body)
#                 user_query = data.get("query", "")

#                 if user_query:
#                     # Retrieve top results based on the query
#                     results = display_top_results(query=user_query, embeddings=embeddings, chunks=chunks)
#                     top_result = results[0][1] if results else "No relevant results found."

#                     # Prepare the JSON response
#                     response_data = {
#                         "query": user_query,
#                         "top_result": top_result,
#                         "all_results": [{"score": float(score), "chunk": chunk, "page_number": page_number} for score, chunk, page_number in results],
#                     }
#                     return JsonResponse(response_data, status=200)

#                 return JsonResponse({"error": "Query not provided"}, status=400)

#             else:  # Handle HTML response for regular browser request
#                 # Handle HTML response when not a JSON request (browser behavior)
#                 user_query = request.POST.get("query", "")

#                 if user_query:
#                     # Retrieve top results based on the query
#                     results = display_top_results(query=user_query, embeddings=embeddings, chunks=chunks)
#                     top_result = results[0][1] if results else "No relevant results found."

#                     # Render HTML page with results
#                     return render(request, 'bot_query.html', {'top_result': top_result, 'query': user_query})

#                 # Initial load (no query entered)
#                 return render(request, 'bot_query.html')

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     elif request.method == "GET":
#         # Render the initial HTML page for GET requests
#         return render(request, 'bot_query.html')

#     # Handle case where request method is neither POST nor GET
#     return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

@csrf_exempt
def query(request):
    # Load preprocessed data
    embeddings, chunks = load_preprocessed_data(MODEL_PATH)

    if request.method == "POST":
        try:
            # Check if the request is JSON
            if request.headers.get('Content-Type') == 'application/json':  
                data = json.loads(request.body)
                user_query = data.get("query", "")

                if user_query:
                    results = display_top_results(query=user_query, embeddings=embeddings, chunks=chunks)
                    top_result = results[0][1] if results else "No relevant results found."

                    response_data = {
                        "query": user_query,
                        "top_result": top_result,
                        "all_results": [{"score": float(score), "chunk": chunk, "page_number": page_number} for score, chunk, page_number in results],
                    }
                    return JsonResponse(response_data, status=200)

                return JsonResponse({"error": "Query not provided"}, status=400)

            # Handle HTML response
            user_query = request.POST.get("query", "")
            if user_query:
                results = display_top_results(query=user_query, embeddings=embeddings, chunks=chunks)
                top_result = results[0][1] if results else "No relevant results found."

                return render(request, 'bot_query.html', {'top_result': top_result, 'query': user_query})

            # Handle conversion logic when the "Convert" button is clicked
            if "convert" in request.POST:
                text_to_convert = request.POST.get("text_to_convert", "")
                selected_language = request.POST.get("language", "")
                if text_to_convert and selected_language:
                    converted_text = convert(text_to_convert, selected_language)
                    return render(request, 'bot_query.html', {
                        'converted_text': converted_text,
                        'top_result': text_to_convert,
                        'language': selected_language,
                    })

            return render(request, 'bot_query.html')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == "GET":
        return render(request, 'bot_query.html')

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)


def convert(text, language):
    """
    Converts the given text into the specified language.

    Args:
        text (str): The text to be translated.
        language (str): The language code (e.g., 'en' for English, 'es' for Spanish).

    Returns:
        str: The translated text.
    """
    try:
        # Translate the text to the specified language
        translated_text = GoogleTranslator(source='auto', target=language).translate(text)
        return translated_text
    except Exception as e:
        return f"Error in translation: {str(e)}"





