import streamlit as st
import pandas as pd
import numpy as np

def app():
    # st.title("Lending Recommendation Page")
    # st.write("This is the Lending Recommendation page.")
 
 
    # Streamlit App
    st.title('Loan Eligibility, Defaults and Repayment Schedule')
    
    # Load account statement
    statement = pd.read_csv('..\\templates\\account_statement.csv')
    
    # Convert 'Date' column to datetime
    statement['Date'] = pd.to_datetime(statement['Date'])
    
    
    # Calculate total monthly income and total monthly expenses from the statement
    statement['Month'] = statement['Date'].dt.to_period('M')
    monthly_income = statement.groupby('Month')['Credit'].sum().mean()
    monthly_expenses = statement.groupby('Month')['Debit'].sum().mean()
    
    # Display total monthly income and expenses
    st.subheader('Total Monthly Income and Expenses')
    st.write(f'Total Monthly Income: ₹{monthly_income:,.2f}')
    st.write(f'Total Monthly Expenses: ₹{abs(monthly_expenses):,.2f}')
    
    # Calculate monthly disposable income
    disposable_income = monthly_income + monthly_expenses  # expenses are negative, so we add them
    
    # Ensure disposable income is positive
    if disposable_income <= 0:
        st.write("Your expenses exceed your income. You are not eligible for a new loan.")
    else:
        # Calculate maximum EMI the user can pay if availing a new loan
        max_emi_affordable = disposable_income * 0.5  # Assuming user can pay 50% of disposable income as EMI
    
        # Adjust for CIBIL score
        def adjust_for_cibil(cibil_score, max_loan):
            if cibil_score < 650:
                return 0
            elif cibil_score < 700:
                return max_loan * 0.8
            elif cibil_score < 750:
                return max_loan * 0.9
            else:
                return max_loan
    
        # Calculate maximum loan amount based on EMI affordability
        def calculate_max_loan_amount(emi, rate, time):
            rate = rate / (12 * 100)  # Monthly interest rate
            time = time * 12  # Loan period in months
            loan_amount = emi * ((1 + rate) ** time - 1) / (rate * (1 + rate) ** time)
            return loan_amount
    
        # Example CIBIL score
        cibil_score = st.slider('CIBIL Score', 300, 900, 750)
    
        # Calculate the maximum eligible loan amount
        max_loan_eligibility = calculate_max_loan_amount(max_emi_affordable, 10.0, 15)  # Assume default rate 10% and period 15 years
        adjusted_max_loan = max(adjust_for_cibil(cibil_score, max_loan_eligibility), 0)
    
        st.write(f"Adjusted Max Loan Eligibility based on CIBIL Score: ₹{adjusted_max_loan:,.2f}")
    
        # User Inputs for Loan Calculation
        interest_rate = st.number_input('Interest Rate (%)', min_value=0.0, max_value=20.0, value=10.0)
        loan_period = st.number_input('Loan Period (Years)', min_value=1, max_value=30, value=15)
        requested_loan_amount = st.number_input('Requested Loan Amount', min_value=0, max_value=int(adjusted_max_loan), value=int(adjusted_max_loan))
    
        # Calculate EMI for requested loan amount
        def calculate_emi(principal, rate, time):
            rate = rate / (12 * 100)  # Monthly interest rate
            time = time * 12  # Loan period in months
            emi = (principal * rate * (1 + rate) ** time) / ((1 + rate) ** time - 1)
            return emi
    
        emi = calculate_emi(requested_loan_amount, interest_rate, loan_period)
    
        # Ensure EMI does not exceed max affordable EMI
        if emi > max_emi_affordable:
            st.write(f"The requested loan amount results in an EMI of ₹{emi:,.2f}, which exceeds your maximum affordable EMI of ₹{max_emi_affordable:,.2f}. Please request a lower loan amount.")
        else:
            # Generate Repayment Schedule
            schedule = []
            outstanding_principal = requested_loan_amount
            for month in range(1, loan_period * 12 + 1):
                interest_payment = outstanding_principal * (interest_rate / (12 * 100))
                principal_payment = emi - interest_payment
                outstanding_principal -= principal_payment
                schedule.append([month, emi, principal_payment, interest_payment, outstanding_principal])
                if outstanding_principal <= 0:
                    break
    
            repayment_schedule = pd.DataFrame(schedule, columns=['Month', 'EMI', 'Principal Payment', 'Interest Payment', 'Outstanding Principal'])
    
            # Display Results
            st.subheader('Monthly EMI')
            st.write(f'₹{emi:,.2f}')
    
            st.subheader('Repayment Schedule')
            st.write(repayment_schedule)
 
# # Title of the application
# st.title("Market Financial KPI Analytics")
# st.subheader("1. Revenue Analysis")
# st.subheader("2. Competitor Benchmarking")
# st.subheader("3. Investment Analysis") 
    
