import streamlit as st
import pandas as pd
import numpy as np
import lightgbm as lgb
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go


def insurance_claim():
        
    # Load the trained model
    model = lgb.Booster(model_file='../templates/realistic_insurance_claims_model.txt')

    # Load the dataset  
    df = pd.read_csv('../templates/realistic_insurance_claims_data.csv')
    df['claim_date'] = pd.to_datetime(df['claim_date'])

    # Define mappings for categorical variables
    gender_map = {'Male': 0, 'Female': 1}
    smoking_status_map = {'Non-smoker': 0, 'Former smoker': 1, 'Current smoker': 2}
    disease_map = {'Flu': 0, 'Fracture': 1, 'Pneumonia': 2, 'Diabetes': 3, 'Heart Disease': 4, 'Cancer': 5}
    insurance_scheme_map = {'Basic': 0, 'Standard': 1, 'Premium': 2}

    # Apply mappings to the dataset
    df['gender'] = df['gender'].map(gender_map)
    df['smoking_status'] = df['smoking_status'].map(smoking_status_map)
    df['disease'] = df['disease'].map(disease_map)
    df['insurance_scheme'] = df['insurance_scheme'].map(insurance_scheme_map)

    st.title('Insurance Claims Prediction Dashboard')

    # Sidebar for patient selection and date range
    st.sidebar.header('Patient Information')
    patient_ids = sorted(df['patient_id'].unique())
    selected_patient_id = st.sidebar.selectbox('Select Patient ID', patient_ids)

    forecast_option = st.sidebar.selectbox('Select Forecast Type', ['Yearly', 'Custom'])

    # Date range selection
    if forecast_option == 'Yearly':
        start_date = datetime(2024, 8, 9)
        end_date = datetime(2025, 8, 8)
    
    else:  # Custom
        start_date = st.sidebar.date_input("Start Date", datetime.now().date())
        end_date = st.sidebar.date_input("End Date", datetime.now().date() + timedelta(days=365))
        
    # Generate button
    generate_button = st.sidebar.button('Generate Forecast')

    if generate_button:
        patient_data = df[df['patient_id'] == selected_patient_id].sort_values('claim_date')
        
        if not patient_data.empty:
            latest_data = patient_data.iloc[-1]
            
            # Calculate historical claim frequency
            total_months = (patient_data['claim_date'].max() - patient_data['claim_date'].min()).days / 30.44  # average days in a month
            claim_frequency = len(patient_data) / total_months if total_months > 0 else 0
            
            date_range = pd.date_range(start=start_date, end=end_date, freq='M')
            predictions = []
            
            for date in date_range:
                input_data = pd.DataFrame({
                    'age': [latest_data['age'] + (date.year - latest_data['claim_date'].year)],
                    'gender': [latest_data['gender']],
                    'bmi': [latest_data['bmi']],
                    'smoking_status': [latest_data['smoking_status']],
                    'pre_existing_condition': [latest_data['pre_existing_condition']],
                    'year': [date.year],
                    'month': [date.month],
                    'day_of_week': [date.dayofweek],
                    'quarter': [date.quarter],
                    'disease': [latest_data['disease']],
                    'insurance_scheme': [latest_data['insurance_scheme']]
                })
                
                predicted_amount = model.predict(input_data)[0]
                # Adjust prediction based on historical claim frequency
                adjusted_prediction = predicted_amount * claim_frequency
                predictions.append({'date': date, 'predicted_claim': adjusted_prediction})
            
            forecast_df = pd.DataFrame(predictions)
            total_predicted_claim = forecast_df['predicted_claim'].sum()
            
            st.header(f'Claim Forecast for Patient ID: {selected_patient_id}')
            st.write(f"Total Predicted Claim Amount: ${total_predicted_claim:.2f}")
            st.write(f"Historical Claim Frequency: {claim_frequency:.2f} claims per month")
            
            # Visualization of forecast
            fig = px.line(forecast_df, x='date', y='predicted_claim', 
                        title='Predicted Monthly Claims Over Time (Adjusted for Claim Frequency)')
            st.plotly_chart(fig)

            # Actual claims graph for the specified period
            previous_start = datetime(2018, 12, 12)
            previous_end = datetime(2023, 1, 1)
            
            actual_claims = patient_data[(patient_data['claim_date'] >= previous_start) & 
                                        (patient_data['claim_date'] <= previous_end)]
            
            fig_actual = go.Figure()
            fig_actual.add_trace(go.Scatter(x=actual_claims['claim_date'], y=actual_claims['approved_claim($)'],
                                            mode='markers+lines', name='Actual Claims($)'))
            fig_actual.update_layout(title='Actual Claims (2018-12-12 to 2023-01-01)',
                                    xaxis_title='Date',
                                    yaxis_title='Claim Amount')
            st.plotly_chart(fig_actual)

            if not patient_data.empty:
                patient_data = df[df['patient_id'] == selected_patient_id]
                st.table(patient_data[['claim_date', 'disease', 'approved_claim($)']].rename(columns={
                    'claim_date': 'Claim Date',
                    'disease': 'Disease',
                    'approved_claim': 'Approved Claim Amount($)'
                }).set_index('Claim Date'))
                st.write(f"Data for Patient ID {selected_patient_id}:")
                st.write(patient_data)
                st.write(f"Note for disease index and insurance scheme index")
                st.write("{0: 'Flu', 1: 'Fracture', 2: 'Pneumonia', 3: 'Diabetes', 4: 'Heart Disease', 5: 'Cancer'}")
                st.write("{0: 'Basic', 1: 'Standard', 2: 'Premium'}")
            else:
                st.write("No historical claims data available for this patient.")

    else:
        st.write("Please select a patient ID and date range, then click 'Generate Forecast'.")

    