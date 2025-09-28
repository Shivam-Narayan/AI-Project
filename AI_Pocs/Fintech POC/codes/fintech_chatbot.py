import streamlit as st
from langchain.document_loaders import TextLoader
from pypdf import PdfReader
from langchain import HuggingFaceHub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import pandas as pd
from docx import Document
import json

def chatbot():
    
    # Reading the input document
    def take_input_document(file, file_type):
        documents = ''
        if file_type == 'pdf':  
            reader = PdfReader(file)
            for page in reader.pages:
                documents += page.extract_text()

            if not documents.strip():
                st.error("No content found in the document.")

            return documents

        elif file_type == 'txt':
            # Load txt documents
            reader = TextLoader(file.name)
            documents = reader.load()[0]

            if not(documents) and not('page_content' in documents):
                st.error("No content found in the document.")
                
            return documents.page_content

        elif file_type == 'csv':
            df = pd.read_csv(file)
            if df.empty:
                st.error("No content found in the document.")
            documents = df.to_string(index=False)
            return documents
        
        elif file_type == 'xlsx' or file_type == 'xls':
            df = pd.read_excel(file)
            if df.empty:
                st.error("No content found in the document.")
            documents = df.to_string(index=False)
            return documents
        
        elif file_type == 'docx':
            doc = Document(file)
            for para in doc.paragraphs:
                documents += para.text + '\n'
            if not documents.strip():
                st.error("No content found in the document.")
            return documents
        
        elif file_type == 'json':
            json_data = json.load(file)
            documents = json.dumps(json_data, indent=2)
            if not documents.strip():
                st.error("No content found in the document.")
            return documents

        else:
            st.error("Unsupported file type")

    # Function to process the document and get the LLM response
    def process_document_and_get_response(document, prompt):
        # Document Splitting
        chunk_size = 200
        chunk_overlap = 20

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        split_1 = splitter.split_text(document)
        split_1 = splitter.create_documents(split_1)

        # Load embeddings instructor
        instructor_embeddings = HuggingFaceInstructEmbeddings(
            model_name='hkunlp/instructor-xl', model_kwargs={'device':'cuda'}
        )

        # Implement embeddings
        db = FAISS.from_documents(split_1, instructor_embeddings)

        # Save db
        db.save_local('vector_store/doc')

        # Load db
        loaded_db = FAISS.load_local(
            'vector_store/doc', instructor_embeddings, allow_dangerous_deserialization=True
        )

        # Load LLM
        temperature = 1
        max_length = 10000
        llm_model_name = 'tiiuae/falcon-7b-instruct'
        token = "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"
        
        llm = HuggingFaceHub(
            repo_id=llm_model_name,
            model_kwargs={'temperature': temperature, 'max_length': max_length},
            huggingfacehub_api_token=token
        )

        # Create the chatbot
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=loaded_db.as_retriever(),
            return_source_documents=True,
        )

        # Ask a question
        response = qa({'query': prompt})
        answer = response.get('result').split('Helpful Answer:')[1].strip()
        return answer



    st.title("Personalized Chat Bot Application")

    # Initialize session state for input and output
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = ''
    if 'result' not in st.session_state:
        st.session_state['result'] = ''

    file_type = st.selectbox("Plese choose the type of file to upload", ["pdf", "txt", "csv", "xlsx","docx", "json"])
    # File uploader
    uploaded_file = st.file_uploader(f"Upload a {file_type} file", type=[file_type])


    # Text input for prompt
    prompt = st.text_input("Enter your question", value=st.session_state['prompt'], key='prompt_input')

    if st.button("Get Answer"):
        if uploaded_file is not None and prompt:
            # Read the document
            document = take_input_document(uploaded_file, file_type)
            
            # Show progress bar during processing
            with st.spinner("Processing..."):
                # Get the response from the LLM
                result = process_document_and_get_response(document, prompt)
            
            st.success("Processing completed")
            st.session_state['result'] = result
            st.write(result)
        else:
            st.warning("Please upload a file and enter a question")


    # Clear input and output when file type is changed
    if file_type != st.session_state.get('prev_file_type', None):
        st.session_state['prompt'] = ''
        st.session_state['result'] = ''
        # st.session_state['prompt_input'] = ''
        st.session_state['prev_file_type'] = file_type
