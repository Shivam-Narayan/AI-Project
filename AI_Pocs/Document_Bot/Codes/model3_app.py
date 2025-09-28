import streamlit as st
import torch
from sentence_transformers import SentenceTransformer, util
import pickle
import fitz  # PyMuPDF
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict 

# Load the embedding model (required for querying)
embedding_model = SentenceTransformer('all-mpnet-base-v2')

# Load preprocessed data (embeddings, chunks, etc.)
@st.cache_resource  # Cache the data to avoid reloading it every time
def load_preprocessed_data(file_path: str):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data['embeddings'], data['chunks']

# Function to retrieve relevant resources based on query
def retrieve_relevant_resources(query: str, embeddings: torch.Tensor, model: SentenceTransformer, n_resources_to_return: int = 3):
    query_embedding = model.encode(query, convert_to_tensor=True)
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    n_resources_to_return = min(n_resources_to_return, len(dot_scores))
    scores, indices = torch.topk(input=dot_scores, k=n_resources_to_return)
    return scores, indices

# Function to display top results and generate the framed response
def display_top_results(query: str, embeddings: torch.Tensor, chunks: List[Dict], n_resources_to_return: int = 3):
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, model=embedding_model, n_resources_to_return=n_resources_to_return)
    results = []
    for score, index in zip(scores, indices):
        chunk = chunks[index]["sentence_chunk"]
        page_number = chunks[index]['page_number']
        is_table = chunks[index].get('is_table', False)
        images = chunks[index].get('images', [])
        
        # Handle tables
        if is_table:
            chunk = f"(Table detected on page {page_number})\n" + chunk
        
        results.append((score, chunk, page_number, images, is_table))
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

def display_pdf_page_with_extras(pdf_path, page_num, images):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)
    
    # Display page content
    display_pdf_page(pdf_path, page_num)
    
    # Display extracted images
    # if images:
    #     for img in images:
    #         st.image(img)  # Display each image

# Streamlit UI
def main_function3():
    st.title("Ascendum Document Query App")

    # Load the preprocessed data
    embeddings, chunks = load_preprocessed_data("../models/Marine_preprocessed_data.pkl")

    # User query input
    query = st.text_input("Ask a question about the document")

    if query:
        top_results = display_top_results(query=query, embeddings=embeddings, chunks=chunks)

        # Display the top result with page numbers and scores
        st.subheader("Top Results:")
        for idx, (score, chunk, page_number, images, is_table) in enumerate(top_results):
            st.markdown(f"**Page {page_number}, Score: {score:.4f}**")
            st.write(f"{chunk}.")
            
            # Automatically display images right after the text
            if images:
                st.write(f"Found {len(images)} image on page {page_number}:")
                for img in images:
                    st.image(img)  # Display each image

            # Add the "Show page" button after images are shown
            if st.button(f"Show page {page_number}", key=f"{page_number}_{idx}"):
                display_pdf_page_with_extras("../templates/Marine_ecosystems.pdf", page_number, images)

