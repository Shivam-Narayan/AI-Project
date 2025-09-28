
import openai
import re
import streamlit as st
import pandas as pd
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
        model_name='hkunlp/instructor-xl', model_kwargs={'device':'cpu'}
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


def personalized_med_recommendation():
        
    # OpenAI API key
    openai.api_key = 'sk-proj-fKcIZYsf6Q8iuEIl5A2UT3BlbkFJCes8oljbs05oJ3Ek1DVp'

    # This is updated function 
    def get_recommendation(patient_data):

        prompt = (f'''Based on the following patient data, recommend the top 3 medical treatments. 
                  Please summarize each recommendation in full sentences, formatted as bullet points or numbered lists. 
                  Each point should be concise, not exceeding 200 words, and provide at least 5 medicine points.\n\n'''
                f"Age: {patient_data['Age']}\n"
                f"Gender: {patient_data['Gender']}\n"
                f"GeneticInfo: {patient_data['GeneticInfo']}\n"
                f"MedicalHistory: {patient_data['MedicalHistory']}\n"
                f"CurrentMedications: {patient_data['CurrentMedications']}\n"
                f"Diagnosis: {patient_data['Diagnosis']}\n"
                f"LabResults: {patient_data['LabResults']}\n"
                f"Region: {patient_data['Region']}\n\n"
                f'''What are the top 4 medications you would suggest for the above patient? 
                Please provide them in bullet points or numbered lists, with each recommendation being a complete sentence.''')

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        text = response['choices'][0]['message']['content'].strip()

        # Updated regex pattern to match bullet points and numbered lists more effectively
        pattern = r'(\d+\..*|•.*|-\s.*)'

        # Find all matches
        matches = re.findall(pattern, text, re.MULTILINE)

        # Join matches with line breaks
        formatted_text = '\n'.join(matches) 
        
        return formatted_text

    
    # updated function
    def get_ayurveda_recommendation(patient_data):
        prompt = (
            f"Based on the following patient data, recommend the top 3 Ayurveda medicines and "
            f"summarize in bullet points. Each point should be a full sentence, "
            f"and the list should not exceed 5 points in total:\n\n"
            f"Age: {patient_data['Age']}\n"
            f"Gender: {patient_data['Gender']}\n"
            f"Genetic Info: {patient_data['GeneticInfo']}\n"
            f"Medical History: {patient_data['MedicalHistory']}\n"
            f"Current Medications: {patient_data['CurrentMedications']}\n"
            f"Diagnosis: {patient_data['Diagnosis']}\n"
            f"Lab Results: {patient_data['LabResults']}\n"
            f"Region: {patient_data['Region']}\n\n"
            f"What are the top 3 Ayurveda medicines you would suggest for the above patient? "
            f"Please provide the response in clear bullet points or numbered format, please ignore I sentences ensuring each point is a full sentence."
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        text = response['choices'][0]['message']['content'].strip()

        # Regex pattern to match bullet points or numbered lists
        pattern = r'(\d+\.\s.*?|•\s.*?|-\s.*?)(?=\n|$)'

        # Find all matches using regex
        matches = re.findall(pattern, text, re.MULTILINE)
        
        # Join matches with line breaks
        formatted_text = '\n'.join(matches)
        
        return formatted_text


    # Streamlit UI
    st.header('Personalized Medicine Recommendation')


    # Input fields
    age = st.number_input('Age', min_value=1)
    gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
    genetic_info = st.selectbox('Genetic Info', ['BRCA1:Mut+', 'BRCA1:Mut-', 'BRCA2:Mut+', 'BRCA2:Mut-'])
    medical_history = st.text_input('Medical History')
    current_medications = st.text_input('Current Medications')
    diagnosis = st.text_input('Diagnosis')
    lab_results = st.text_input('Lab Results')
    region = st.text_input("Region")

    # Collect all input fields in a list
    input_fields = [medical_history, current_medications, diagnosis, lab_results, region]

    # Determine whether any field is empty
    is_any_field_empty = any(not field for field in input_fields)

    option = st.selectbox("Choose Medicine Recommendation", options = ['Choose Medicine Recommendation','Modern Medicine Recommendation', 'Auyerveda Medicine Recommendation'])

    if not is_any_field_empty and option == 'Modern Medicine Recommendation':
        # Button to get recommendation
        patient_data = {
            'Age': age,
            'Gender': gender,
            'GeneticInfo': genetic_info,
            'MedicalHistory': medical_history,
            'CurrentMedications': current_medications,
            'Diagnosis': diagnosis,
            'LabResults': lab_results,
            'Region' : region
        }
        
        recommendation = get_recommendation(patient_data)
        st.write('Recommended Modern Medication')
        st.write(recommendation)

    elif not is_any_field_empty and option == 'Auyerveda Medicine Recommendation':        
        # if st.button('Ayurveda Med Recommendation'):
        patient_data = {
            'Age': age,
            'Gender': gender,
            'GeneticInfo': genetic_info,
            'MedicalHistory': medical_history,
            'CurrentMedications': current_medications,
            'Diagnosis': diagnosis,
            'LabResults': lab_results,
            'Region': region
        }
        
        recommendation = get_ayurveda_recommendation(patient_data)
        st.write('Recommended Ayurveda Medication')
        st.write(recommendation)



    # Initialize session state for input and output
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = ''
    if 'result' not in st.session_state:
        st.session_state['result'] = ''

    file_type = st.selectbox("Plese choose the type of file to upload a Medical Report", ["pdf", "txt", "csv", "xlsx","docx", "json"])
    # File uploader
    uploaded_file = st.file_uploader(f"Upload a {file_type} file", type=[file_type])

    prompt = """Summarize the following medical report in complete and coherent sentences:
                1. Extract and summarize the patient's health issues identified from the medical report in Bullet points.
                2. Summarize no less than 10000 words.
                3. Avoid incomplete thoughts or truncation.
                4. Present the summary in bullet points.
                """
    
        # and also at last print the how many words is used.
    if st.button("Summarize the Report"):
        if uploaded_file is not None:
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