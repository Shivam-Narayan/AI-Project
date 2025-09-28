import os
from PIL import Image, ImageOps
import numpy as np
import joblib
from skimage import filters, morphology
from skimage.feature import hog, local_binary_pattern
from scipy.fftpack import fft2, fftshift
import pywt
import mahotas as mh
from mahotas.features import zernike_moments
import winsound
import tkinter as tk
from tkinter import messagebox
import streamlit as st

# Load the saved model
model_path = '../models/stitch_detection_ensemble_model_3.pkl'
voting_clf = joblib.load(model_path)

# Define the feature extraction function (same as used in training)
def extract_features(image_array):
    edges = filters.sobel(image_array)
    edges_threshold = edges > 0.1
    edges_cleaned = morphology.binary_closing(edges_threshold)
    continuous_points = np.sum(edges_cleaned)

    row_gaps = []
    for row in range(edges_cleaned.shape[0]):
        stitch_pixels = np.where(edges_cleaned[row] == 1)[0]
        if len(stitch_pixels) > 1:
            gaps = np.diff(stitch_pixels)
            row_gaps.append(np.max(gaps) if len(gaps) > 0 else 0)

    max_gap = np.max(row_gaps) if len(row_gaps) > 0 else 0
    skipped_stitch_flag = 1 if max_gap > np.median(row_gaps) * 2 else 0
    overlap_flag = 1 if np.mean([len(np.where(edges_cleaned[row] == 1)[0]) for row in range(edges_cleaned.shape[0])]) > np.median(row_gaps) * 1.5 else 0

    texture_contrast = np.mean(filters.rank.gradient(image_array, morphology.disk(3)))
    texture_energy = np.mean(image_array ** 2)

    hog_features = hog(image_array, pixels_per_cell=(16, 16), cells_per_block=(2, 2), visualize=False)
    hog_features = hog_features[:100] if len(hog_features) > 100 else np.pad(hog_features, (0, 100 - len(hog_features)))

    lbp = local_binary_pattern(image_array, P=8, R=1, method='uniform')
    lbp_histogram, _ = np.histogram(lbp.ravel(), bins=np.arange(0, 11), range=(0, 10))
    lbp_histogram = lbp_histogram.astype('float')
    lbp_histogram /= (lbp_histogram.sum() + 1e-6)

    fft_result = np.abs(fftshift(fft2(image_array)))
    fft_mean = np.mean(fft_result)
    fft_std = np.std(fft_result)

    gabor_responses = []
    for theta in range(4):
        theta = theta / 4. * np.pi
        filt_real, filt_imag = filters.gabor(image_array, frequency=0.6, theta=theta)
        gabor_responses.append(filt_real.mean())
        gabor_responses.append(filt_imag.mean())

    coeffs = pywt.wavedec2(image_array, 'db1', level=2)
    wavelet_mean = np.mean(coeffs[0])
    wavelet_std = np.std(coeffs[0])

    haralick_features = mh.features.haralick(image_array).mean(axis=0)
    zernike_feat = zernike_moments(image_array, radius=15)

    return np.hstack([continuous_points, max_gap, texture_contrast, texture_energy,
                      hog_features, lbp_histogram, fft_mean, fft_std, gabor_responses,
                      wavelet_mean, wavelet_std, haralick_features, zernike_feat,
                      skipped_stitch_flag, overlap_flag])

# Function to predict the label of a single image
def predict_image(image_path):
    img = Image.open(image_path)
    img_gray = ImageOps.grayscale(img)
    img_array = np.array(img_gray)
    
    # Extract features from the image
    features = extract_features(img_array)
    
    # Normalize the features (ensure the scaler is consistent with training)
    scaler = joblib.load('../models/scaler.pkl')  # Load the scaler used during training
    features_scaled = scaler.transform([features])
    
    # Make a prediction
    prediction = voting_clf.predict(features_scaled)

    
    
    # Map prediction to label
    label_map = {0: 'Normal', 1: 'Broken', 2: 'Overlap', 3: 'Skipped'}
    predicted_label = label_map[prediction[0]]

    if predicted_label != 'Normal':
        flag = 'Yes'

    else:
        # predicted_label = label_map[prediction[0]]
        flag = 'NO'

      
    return predicted_label, flag

# Test the model with a random image
# image_path = r'C:\Users\harshithc\OneDrive - Ascendum US\Harshith\Projects\POC\Laguna POC\nayan_dataset\Skipped Stitches\G. Chiffon-Poly_1. Skipped stitch_G_01_020.jpg'  # Replace with the path of the image to test


# predicted_result = predict_image(image_path)
# print(f"Predicted result: {predicted_result}")