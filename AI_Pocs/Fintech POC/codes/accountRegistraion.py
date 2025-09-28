# Step 1 : Account Registration:

 

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np
import os
from PIL import Image
import pytesseract
import requests
import re
from geopy.geocoders import Nominatim
import pandas as pd

 

# Function to save captured image




def save_image(image, folder="captured_images"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, "captured_face.jpg")
    cv2.imwrite(file_path, image)

    return file_path

 

# Function to save uploaded file

def save_uploaded_file(uploaded_file, folder="uploaded_documents"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

 

# Video transformer class for Streamlit WebRTC

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.image = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.image = img

        return img

 

# Function to extract text from image using OCR

def extract_text_from_image(image_path, lang='eng'):
    #image = Image.open(image_path)

    #text = pytesseract.image_to_string(image, lang=lang)

    #return text
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pil_image = Image.fromarray(image_rgb)
    text = pytesseract.image_to_string(pil_image)

    return text

 

 

# Function to extract information from OCR text using regex
def extract_info(text, doc_type):
    name, dob, aadhar, pan = None, None, None, None
    lines = text.split('\n')

    if doc_type == 'pan':
        found_income_tax = False

        for i, line in enumerate(lines):
            if "INCOME TAX DEPARTMENT" in line:
                found_income_tax = True
                if i + 2 < len(lines):
                    name = lines[i + 2].strip()

                # Try finding DOB in lines +5, +6 from the name line
                if name:
                    for offset in [5, 6]:
                        if i + offset < len(lines):
                            pan_dob_match = re.search(r'\d{2}/\d{2}/\d{4}', lines[i + offset])

                            if pan_dob_match:
                                dob = pan_dob_match.group(0)
                                break

                    # Try finding PAN in lines +2, +3, +4 from the DOB line and +7, +8, +9 from the name line

                    for offset in [2, 3, 4]:

                        if i + 5 + offset < len(lines):

                            pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', lines[i + 5 + offset])

                            if pan_match:

                                pan = pan_match.group(0)

                                break

                    if not pan:

                        for offset in [7, 8, 9]:

                            if i + offset < len(lines):

                                pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', lines[i + offset])

                                if pan_match:

                                    pan = pan_match.group(0)

                                    break

                    if not pan:

                        for offset in [11, 12, 13]:

                            if i + offset < len(lines):

                                pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', lines[i + offset])

                                if pan_match:

                                    pan = pan_match.group(0)

                                    break

 

        # If not found, try a more general search

        if not dob or not pan:

            for i, line in enumerate(lines):

                if not dob:

                    pan_dob_match = re.search(r'\d{2}/\d{2}/\d{4}', line)

                    if pan_dob_match:

                        dob = pan_dob_match.group(0)

                if not pan:

                    pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', line)

                    if pan_match:

                        pan = pan_match.group(0)

                if dob and pan:

                    break

 

    elif doc_type == 'aadhar':

        for i, line in enumerate(lines):

            if "DOB" in line or "Date of Birth" in line:

                name = lines[i - 1].strip()

                name = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', name)

                dob_match = re.search(r'\d{2}/\d{2}/\d{4}', line)

                if dob_match:

                    dob = dob_match.group(0)

            if re.match(r'\d{4}\s\d{4}\s\d{4}', line):

                aadhar = line.strip()

 

    return name, dob, aadhar, pan

 

# Function to get user's IP address and location
def get_ip_location():

    response = requests.get('https://ipinfo.io')

    data = response.json()

    ip = data.get("ip")

    location = data.get("loc")

    lat, lon = location.split(',')

    return ip, lat, lon

 

# Function to get location name from latitude and longitude
def get_location_name(lat, lon):

    geolocator = Nominatim(user_agent="geoapiExercises")

    try:

        location = geolocator.reverse((lat, lon), language='en')

        return location.address if location else "Location not found"

    except Exception as e:

        print(f"Error getting location name: {e}")

        return "Error getting location name"

 
def registration():
    # Streamlit app

    st.title("KYC Document and Face Capture System")

    st.write("Capture a face photo and upload your PAN and Aadhar card images for verification.")

    

    # WebRTC streamer

    ctx = webrtc_streamer(key="example", video_transformer_factory=VideoTransformer, media_stream_constraints={"video": True, "audio": False})

    

    # Upload PAN card image

    pan_image_file = st.file_uploader("Upload PAN Card Image", type=["jpg", "jpeg", "png"])

    if pan_image_file is not None:

        pan_image_path = save_uploaded_file(pan_image_file)

        st.success(f"PAN Card image saved to {pan_image_path}")

        pan_image = Image.open(pan_image_file)

        st.image(pan_image, caption="PAN Card Image", use_column_width=True)

    

    # Upload Aadhar card image

    aadhar_image_file = st.file_uploader("Upload Aadhar Card Image", type=["jpg", "jpeg", "png"])

    if aadhar_image_file is not None:

        aadhar_image_path = save_uploaded_file(aadhar_image_file)

        st.success(f"Aadhar Card image saved to {aadhar_image_path}")

        aadhar_image = Image.open(aadhar_image_file)

        st.image(aadhar_image, caption="Aadhar Card Image", use_column_width=True)

    

    # Capture photo button

    if ctx.video_transformer:

        if st.button("Capture Face Photo"):

            face_image = ctx.video_transformer.image

            if face_image is not None:

                face_image_path = save_image(face_image)

                st.success(f"Face photo saved to {face_image_path}")

                st.image(face_image, caption="Captured Face Image", use_column_width=True)

                ip, lat, lon = get_ip_location()

                location_name = get_location_name(lat, lon)

                st.write(f"IP Address: {ip}")

                st.write(f"Location: {location_name} (Lat: {lat}, Lon: {lon})")

            else:

                st.warning("No image captured. Please try again.")

    

    # Extract and display information from KYC documents

    if pan_image_file or aadhar_image_file:

        st.write("### Extracted Information:")

    

        if pan_image_file:

            pan_text = extract_text_from_image(pan_image_path, lang='eng')

            pan_name, pan_dob, _, pan_number = extract_info(pan_text, doc_type='pan')

            st.write(f"**PAN Name:** {pan_name}")

            st.write(f"**PAN DOB:** {pan_dob}")

            st.write(f"**PAN Number:** {pan_number}")

        

        if aadhar_image_file:

            aadhar_text = extract_text_from_image(aadhar_image_path, lang='eng')

            aadhar_name, aadhar_dob, aadhar_number, _ = extract_info(aadhar_text, doc_type='aadhar')

            st.write(f"**Aadhar Name:** {aadhar_name}")

            st.write(f"**Aadhar DOB:** {aadhar_dob}")

            st.write(f"**Aadhar Number:** {aadhar_number}")

    

        ip, lat, lon = get_ip_location()

        location_name = get_location_name(lat, lon)

        st.write(f"IP Address: {ip}")

        st.write(f"Location: {location_name} (Lat: {lat}, Lon: {lon})")

    

 


# Step 2: Loan Request:

def loanRequest():

    # Streamlit App

    st.title('Loan Eligibility, Defaults and Repayment Schedule')

    

    # Load account statement

    statement = pd.read_csv('account_statement.csv')

    

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


# Step 3: Process Loans


def app():

    value = st.sidebar.selectbox("Account Registration", options=['Account Registration', 'Loan Request', 'Process Loans'])

    if value == 'Account Registration':
        registration()
    elif value == 'Loan Request':
        loanRequest()
    else:
        st.title("Project in progress.......")