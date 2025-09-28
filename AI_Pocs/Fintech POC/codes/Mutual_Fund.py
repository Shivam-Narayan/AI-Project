import os
import pickle
import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
import langchain
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI 
from langchain.vectorstores import FAISS
from langchain.schema import Document  # Import Document from langchain.schema
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../templates/.env')
load_dotenv(dotenv_path)


def mutual_fund_main():
    # Set up the Streamlit app
    st.title("Ascendum Market Research Tool")

    st.sidebar.title("News Article URLs")

    # Collect URLs from the sidebar
    urls = []
    for ele in range(3):
        url = st.sidebar.text_input(f"URL {ele+1}")
        urls.append(url)

    file_path = "../models/faiss_store_openai.pkl"

    process_url_clicked = st.sidebar.button("Process URLs")
    main_placefolder = st.empty()
    
    llm = OpenAI(temperature=0.9, max_tokens=500)


    # Function to load data from URLs using requests and BeautifulSoup
    def load_data_from_urls(urls):
        data = []
        for url in urls:
            if url:
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")
                        page_data = soup.get_text(separator='\n')  # Extract the text content from the webpage
                        # Create a Document object with page_content and metadata
                        doc = Document(page_content=page_data, metadata={"source": url})
                        data.append(doc)
                    else:
                        st.error(f"Failed to fetch data from {url} (Status Code: {response.status_code})")
                except Exception as e:
                    st.error(f"Error loading data from {url}: {e}")
        return data

    # Handle the URL processing
    if process_url_clicked:
        if not any(urls):
            st.sidebar.warning("Please enter at least one URL!")
        else:
            # Load the data
            main_placefolder.text("Data Loading Started.....")
            data = load_data_from_urls(urls)  # Using the updated function to load data as Document objects
            
            if not data:
                st.error("No data loaded from the provided URLs.")
                st.stop()  # Stop execution if no data is loaded

            # Split the data
            text_split = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", '.'],
                chunk_size=1000
            )

            main_placefolder.text("Text Splitting Started.....")
            docs = text_split.split_documents(data)  # This now works because data is a list of Document objects

            # Create embeddings
            main_placefolder.text("Creating Embeddings.....")
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_documents(docs, embeddings)

            main_placefolder.text("Embedding Vector Building Started.....")
            time.sleep(2)

            # Save the FAISS index to a pickle file
            with open(file_path, 'wb') as f:
                pickle.dump(vector_store, f)


    # Query Interface
    query = st.text_input("Question: ")

    if query:
        if not any(urls):
            st.warning("Please enter the URLs and ask a query based on the URL content!")
        else:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    vector_store = pickle.load(f)
                    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vector_store.as_retriever())
                    result = chain({"question": query}, return_only_outputs=True)
                    
                    # Display the answer
                    st.header("Answer")
                    st.markdown(result.get("answer", ""))

                    # Display the sources, if available
                    sources = result.get("sources", "")
                    if sources:
                        st.subheader("Sources")
                        sources_list = sources.split("\n")  # Split the sources by newline
                        for source in sources_list:
                            st.markdown(f"- {source.strip()}")
            else:
                st.error("Vector store not found. Please process the URLs first.")

