import os
import fitz  # PyMuPDF for reading PDFs
import torch
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
import pickle  # For saving the preprocessed data
from typing import List  # Import List for type annotations

# Check for device (use CPU if no CUDA device is available)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize the embedding model with the correct device
embedding_model = SentenceTransformer('all-mpnet-base-v2', device=device)

# Function to format text from the PDF
def text_formatter(text: str) -> str:
    return text.replace("\n", " ").strip()

# Function to read and extract text from the PDF
def open_and_read_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    pages_and_texts = []
    for page_number, page in tqdm(enumerate(doc), total=doc.page_count):
        text = page.get_text()
        text = text_formatter(text)
        if text:
            pages_and_texts.append({
                "page_number": page_number + 1,
                "text": text
            })
    return pages_and_texts

# Function to split sentences into chunks
def split_list(input_list: List[str], slice_size: int) -> List[List[str]]:
    return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

# Preprocess the PDF and save embeddings, chunks, and pages to a file
def preprocess_and_save(pdf_path: str, save_path: str):
    pages_and_texts = open_and_read_pdf(pdf_path)
    
    # Split text into chunks for embeddings
    chunks = []
    for page in pages_and_texts:
        sentences = page["text"].split(". ")
        chunks.extend([{
            "page_number": page["page_number"],
            "sentence_chunk": " ".join(chunk)
        } for chunk in split_list(sentences, 5) if " ".join(chunk).strip()])

    if chunks:
        # Embed the document chunks
        embeddings = embedding_model.encode([chunk["sentence_chunk"] for chunk in chunks], convert_to_tensor=True)

        # Save the embeddings, chunks, and pages information to a file
        with open(save_path, 'wb') as f:
            pickle.dump({
                'embeddings': embeddings,
                'chunks': chunks
            }, f)
        print("Preprocessing and saving completed.")
    else:
        print("The document contains no valid text to process.")


pdf_path = "../templates/PrinciplesofFinance.pdf"
model_path = "../models/Finance_preprocessed_data.pkl"
# Call this function once to preprocess and save the data
preprocess_and_save(pdf_path, model_path)
