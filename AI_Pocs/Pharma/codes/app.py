import streamlit as st
import drug_clinical_trial
from Personalized_Medication_Recommendation import personalized_med_recommendation
import insurance_claim_mgmt


print(dir(drug_clinical_trial))  # This will list all attributes and methods of the 'drug' module


def home():
    st.title("Drug Analysis Tool")
    st.write("Drug discovery and Clinical trial")
    st.markdown("A support assistant to the R&D team to help accelarate the Drug Analysis and early identification of new variants")
    st.image('../templates/Flowchart.png',)

def app():

    st.sidebar.title("Navigate")


    pages = {
        "Home": home,
        # "Drug Discovery": drug_discovery,
        "Drug Discovery" : drug_clinical_trial.drug_discovery,
        "Clinical Trial": drug_clinical_trial.clinical_Trial,
        "Personalized Recommended Medicine": personalized_med_recommendation, 
        "Insurance Claim Management": insurance_claim_mgmt.insurance_claim
    }
    page = st.sidebar.selectbox("Go to", list(pages.keys()))
    
    
    # Call the selected page function
    pages[page]()


    

if __name__ == '__main__':
    app()