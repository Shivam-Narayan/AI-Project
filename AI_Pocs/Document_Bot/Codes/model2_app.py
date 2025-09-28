import streamlit as st
import torch
from sentence_transformers import SentenceTransformer, util
import pickle
import fitz 
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict  # Import List and Dict for type annotations

# Load the embedding model (required for querying)
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# Load preprocessed data (embeddings, chunks, etc.)
@st.cache_resource  # Cache the data to avoid reloading it every time
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
def display_top_results(query: str, embeddings: torch.Tensor, chunks: List[Dict], n_resources_to_return: int = 5):  # Updated type hints
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, model=embedding_model, n_resources_to_return=n_resources_to_return)
    results = []
    for score, index in zip(scores, indices):
        chunk = chunks[index]["sentence_chunk"]
        page_number = chunks[index]['page_number']
        results.append((score, chunk, page_number))
    return results

def display_pdf_page(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)  # Pages are 0-indexed in PyMuPDF
    img = page.get_pixmap(dpi=300)
    doc.close()
    
    img_array = np.frombuffer(img.samples_mv, dtype=np.uint8).reshape((img.h, img.w, img.n))
    plt.figure(figsize=(13, 10))
    plt.imshow(img_array)
    plt.axis('off')  # Turn off axis for a cleaner view
    st.pyplot(plt)

# Streamlit UI
def main_function2():
    st.title("Ascendum Document Query App")

    # Load the preprocessed data
    embeddings, chunks = load_preprocessed_data("../models/Finance_preprocessed_data.pkl")

    # User query input
    query = st.text_input("Ask a question about the document")

    if query:
        # Retrieve top results based on the query
        results = display_top_results(query=query, embeddings=embeddings, chunks=chunks)

        # Display the top result
        st.subheader("Top Results:")
        for idx, (score, chunk, page_number) in enumerate(results):
            st.markdown(f"**Page {page_number}, Score: {score:.4f}**")
            st.write(f"{chunk}.")
        
        # Option to display the relevant page
            if st.button(f"Show page {page_number}", key=f"{page_number}_{idx}"):
                pdf_path = "../templates/PrinciplesofFinance.pdf"
                display_pdf_page(pdf_path, page_number)
