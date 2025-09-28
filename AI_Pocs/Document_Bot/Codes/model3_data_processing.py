# import os
# import fitz  # PyMuPDF for reading PDFs
# import torch
# from tqdm.auto import tqdm
# from sentence_transformers import SentenceTransformer
# import pickle  # For saving the preprocessed data
# from PIL import Image
# import io


# # Check for device (use CPU if no CUDA device is available)
# device = "cuda" if torch.cuda.is_available() else "cpu"

# embedding_model = SentenceTransformer('all-mpnet-base-v2', device=device)

# def check_pdf_integrity_with_pymupdf(pdf_path):
#     """Check if the PDF is valid using PyMuPDF."""
#     try:
#         # Open the document
#         doc = fitz.open(pdf_path)
#         # Try accessing any page to check for errors
#         _ = doc.load_page(0)  # Attempt to load the first page

#         print("The PDF is well-formed and not corrupted.")
#         return True

#     except fitz.fitz.FileDataError as e:
#         print(f"PDF data error: {e}")
#         return False

#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return False

# # Function to format text from the PDF
# def text_formatter(text: str) -> str:
#     return text.replace("\n", " ").strip()

# def extract_images_from_page(doc, page):
#     """Extract images from a given page in a PDF document."""
#     image_list = page.get_images(full=True)  # Get all images from the page
#     images = []

#     for img_index, img in enumerate(image_list):
#         xref = img[0]  # Extract the image reference (xref)
#         base_image = fitz.Pixmap(doc, xref)  # Use Pixmap to extract image data

#         try:
#             # Check if the image is in grayscale or RGB format
#             if base_image.n == 1:  # GRAY scale image
#                 img_bytes = base_image.tobytes("png")  # Convert grayscale to PNG byte data
#             elif base_image.n == 3:  # RGB format
#                 img_bytes = base_image.tobytes("jpeg")  # Convert RGB to JPEG byte data
#             elif base_image.n == 4:  # CMYK format, we need to convert to RGB
#                 base_image = fitz.Pixmap(fitz.csRGB, base_image)
#                 img_bytes = base_image.tobytes("jpeg")  # Convert CMYK to JPEG byte data
#             else:
#                 # Convert any other color space to RGB
#                 base_image = fitz.Pixmap(fitz.csRGB, base_image)
#                 img_bytes = base_image.tobytes("png")  # Convert unknown formats to PNG byte data

#             # Convert the byte data to a PIL image and store it in the list
#             image = Image.open(io.BytesIO(img_bytes))
#             images.append(image)  # Add the PIL image to the list

#         except Exception as e:
#             print(f"Error processing image {img_index}: {e}")
#             continue  # Skip the problematic image and move to the next one

#     return images


# # Function to read and extract text and images from the PDF
# def open_and_read_pdf(pdf_path: str):
#     doc = fitz.open(pdf_path)
#     pages_and_texts = []
#     for page_number, page in tqdm(enumerate(doc), total=doc.page_count):
#         text = page.get_text()
#         text = text_formatter(text)

#         images = extract_images_from_page(doc, page)  # Extract images from the page

#         if text or images:
#             pages_and_texts.append({
#                 "page_number": page_number + 1,
#                 "text": text,
#                 "images": images,  # Append extracted images
#             })
#     return pages_and_texts

# # Function to split sentences into chunks
# def split_list(input_list: list, slice_size: int) -> list[list[str]]:
#     return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

# # Function to check if the query is relevant to the images
# def query_relevant_images(query: str, chunks: list) -> list:
#     """Check if the query is relevant to images by embedding the text and comparing with the query."""
#     relevant_images = []
#     query_embedding = embedding_model.encode(query, convert_to_tensor=True)

#     for chunk in chunks:
#         chunk_text = chunk["sentence_chunk"]
#         chunk_embedding = embedding_model.encode(chunk_text, convert_to_tensor=True)
#         similarity = torch.nn.functional.cosine_similarity(query_embedding, chunk_embedding, dim=0)

#         if similarity.item() > 0.7 and chunk["images"]:  # Threshold for relevance
#             relevant_images.extend(chunk["images"])

#     return relevant_images

# # Preprocess the PDF and save embeddings, chunks, and pages to a file
# def preprocess_and_save(pdf_path: str, save_path: str, query: str):
#     pages_and_texts = open_and_read_pdf(pdf_path)
    
#     if not pages_and_texts:
#         print("No valid text found in the document.")
#         return
    
#     # Split text into chunks for embeddings
#     chunks = []
#     for page in pages_and_texts:
#         sentences = page["text"].split(". ")
#         chunks.extend([{
#             "page_number": page["page_number"],
#             "sentence_chunk": " ".join(chunk),
#             "images": page.get("images", [])  # Track any images in the chunk
#         } for chunk in split_list(sentences, 5) if " ".join(chunk).strip()])

#     # Get the relevant images based on the query
#     relevant_images = query_relevant_images(query, chunks)

#     # Embed the document chunks
#     if chunks:
#         embeddings = embedding_model.encode([chunk["sentence_chunk"] for chunk in chunks], convert_to_tensor=True)

#         # Save the embeddings, chunks, and pages information to a file
#         with open(save_path, 'wb') as f:
#             pickle.dump({
#                 'embeddings': embeddings,
#                 'chunks': chunks,
#                 'relevant_images': relevant_images  # Save relevant images
#             }, f)
#         print("Preprocessing and saving completed.")
#     else:
#         print("The document contains no valid text to process.")

# # Call this function once to preprocess and save the data

# pdf_path = "../templates/Marine_ecosystems.pdf"
# model_path = "../models/preprocessed_data.pkl"
# query = "nutrition diagram"  # Example query related to images

# check_pdf = check_pdf_integrity_with_pymupdf(pdf_path)

# if check_pdf == True:
#     preprocess_and_save(pdf_path, model_path, query)
# else:
#     print("Pdf is not well-formatted")


import os
import fitz  # PyMuPDF for reading PDFs
import torch
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
import pickle  # For saving the preprocessed data
from PIL import Image
import io
from typing import List, Dict  # Use List and Dict for type annotations

# Check for device (use CPU if no CUDA device is available)
device = "cuda" if torch.cuda.is_available() else "cpu"

embedding_model = SentenceTransformer('all-mpnet-base-v2', device=device)

def check_pdf_integrity_with_pymupdf(pdf_path):
    """Check if the PDF is valid using PyMuPDF."""
    try:
        # Open the document
        doc = fitz.open(pdf_path)
        # Try accessing any page to check for errors
        _ = doc.load_page(0)  # Attempt to load the first page

        print("The PDF is well-formed and not corrupted.")
        return True

    except fitz.fitz.FileDataError as e:
        print(f"PDF data error: {e}")
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# Function to format text from the PDF
def text_formatter(text: str) -> str:
    return text.replace("\n", " ").strip()

def extract_images_from_page(doc, page):
    """Extract images from a given page in a PDF document."""
    image_list = page.get_images(full=True)  # Get all images from the page
    images = []

    for img_index, img in enumerate(image_list):
        xref = img[0]  # Extract the image reference (xref)
        base_image = fitz.Pixmap(doc, xref)  # Use Pixmap to extract image data

        try:
            # Check if the image is in grayscale or RGB format
            if base_image.n == 1:  # GRAY scale image
                img_bytes = base_image.tobytes("png")  # Convert grayscale to PNG byte data
            elif base_image.n == 3:  # RGB format
                img_bytes = base_image.tobytes("jpeg")  # Convert RGB to JPEG byte data
            elif base_image.n == 4:  # CMYK format, we need to convert to RGB
                base_image = fitz.Pixmap(fitz.csRGB, base_image)
                img_bytes = base_image.tobytes("jpeg")  # Convert CMYK to JPEG byte data
            else:
                # Convert any other color space to RGB
                base_image = fitz.Pixmap(fitz.csRGB, base_image)
                img_bytes = base_image.tobytes("png")  # Convert unknown formats to PNG byte data

            # Convert the byte data to a PIL image and store it in the list
            image = Image.open(io.BytesIO(img_bytes))
            images.append(image)  # Add the PIL image to the list

        except Exception as e:
            print(f"Error processing image {img_index}: {e}")
            continue  # Skip the problematic image and move to the next one

    return images

# Function to read and extract text and images from the PDF
def open_and_read_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    pages_and_texts = []
    for page_number, page in tqdm(enumerate(doc), total=doc.page_count):
        text = page.get_text()
        text = text_formatter(text)

        images = extract_images_from_page(doc, page)  # Extract images from the page

        if text or images:
            pages_and_texts.append({
                "page_number": page_number + 1,
                "text": text,
                "images": images,  # Append extracted images
            })
    return pages_and_texts

# Function to split sentences into chunks
def split_list(input_list: list, slice_size: int) -> List[List[str]]:
    return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]

# Function to check if the query is relevant to the images
def query_relevant_images(query: str, chunks: List[Dict]) -> List:
    """Check if the query is relevant to images by embedding the text and comparing with the query."""
    relevant_images = []
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)

    for chunk in chunks:
        chunk_text = chunk["sentence_chunk"]
        chunk_embedding = embedding_model.encode(chunk_text, convert_to_tensor=True)
        similarity = torch.nn.functional.cosine_similarity(query_embedding, chunk_embedding, dim=0)

        if similarity.item() > 0.7 and chunk["images"]:  # Threshold for relevance
            relevant_images.extend(chunk["images"])

    return relevant_images

# Preprocess the PDF and save embeddings, chunks, and pages to a file
def preprocess_and_save(pdf_path: str, save_path: str, query: str):
    pages_and_texts = open_and_read_pdf(pdf_path)
    
    if not pages_and_texts:
        print("No valid text found in the document.")
        return
    
    # Split text into chunks for embeddings
    chunks = []
    for page in pages_and_texts:
        sentences = page["text"].split(". ")
        chunks.extend([{
            "page_number": page["page_number"],
            "sentence_chunk": " ".join(chunk),
            "images": page.get("images", [])  # Track any images in the chunk
        } for chunk in split_list(sentences, 5) if " ".join(chunk).strip()])

    # Get the relevant images based on the query
    relevant_images = query_relevant_images(query, chunks)

    # Embed the document chunks
    if chunks:
        embeddings = embedding_model.encode([chunk["sentence_chunk"] for chunk in chunks], convert_to_tensor=True)

        # Save the embeddings, chunks, and pages information to a file
        with open(save_path, 'wb') as f:
            pickle.dump({
                'embeddings': embeddings,
                'chunks': chunks,
                'relevant_images': relevant_images  # Save relevant images
            }, f)
        print("Preprocessing and saving completed.")
    else:
        print("The document contains no valid text to process.")

# Call this function once to preprocess and save the data

pdf_path = "../templates/Marine_ecosystems.pdf"
model_path = "../models/Marine_preprocessed_data.pkl"
query = "nutrition diagram"  # Example query related to images

check_pdf = check_pdf_integrity_with_pymupdf(pdf_path)

if check_pdf == True:
    preprocess_and_save(pdf_path, model_path, query)
else:
    print("Pdf is not well-formatted")
