import streamlit as st
from model1_app import main_function1
from model2_app import main_function2
from model3_app import main_function3

def main():

    st.sidebar.header("Ascendum Bot Models")
    select_options = st.sidebar.selectbox("Choose Bots", options=["Choose Bots", "Ascendum Bot 1", "Ascendum Bot 2", "Ascendum Bot 3"])

    if select_options == "Ascendum Bot 1":
        main_function1()

    elif select_options == "Ascendum Bot 2":
        main_function2()
    
    elif select_options == "Ascendum Bot 3":
        main_function3()

    if select_options == "Choose Bots":
        st.title("Ascendum Chat Bot Application")

        st.header("Ascendum Bot 1")

        st.write('''In Model 1, users can upload a document, and the system will process it dynamically. 
                 Users can input queries based on the document's content, and the relevant answers will be provided in real-time. 
                 The model also tracks and displays the history of user queries for easy reference.''')


        st.header("Ascendum Bot 2 and 3")

        st.write('''Model 2 allows documents to be pre-processed and trained in the backend, significantly reducing response time. 
                 Users can input queries through the interface, 
                 and the system will retrieve accurate answers along with the specific page numbers and a content page from the document. ''')


if __name__ == "__main__":
    main()