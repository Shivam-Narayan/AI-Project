import streamlit as st
import Depreciation
import Analytics
import LendingRecommendation
import fintech_chatbot
import accountRegistraion 
import Mutual_Fund

# Sidebar for navigation


# button = st.sidebar.selectbox("App", ['Analytics','Depreciation Investment Analysis', 'Research Analyst','Lending Recommendation', 'Fintech ChatBot', 'Account Registration'])

button = st.sidebar.selectbox("App", ['Analytics','Depreciation Investment Analysis', 'Research Analyst','Lending Recommendation', 'Account Registration'])

# Load the selected page
if button == "Analytics":
     Analytics.app()

elif button == "Depreciation Investment Analysis": 
    Depreciation.app()

elif button == "Lending Recommendation":
    LendingRecommendation.app() 

elif button == "Account Registration":
    accountRegistraion.app()
    
elif button == "Fintech ChatBot":
    fintech_chatbot.chatbot()

elif button == "Research Analyst":
    Mutual_Fund.mutual_fund_main()


     

    
