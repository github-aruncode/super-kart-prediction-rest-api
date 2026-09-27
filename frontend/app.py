import os

import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:7860").rstrip("/")

# Set the title of the Streamlit app
st.title("Super Kart Price Prediction")

# Section for online prediction
st.subheader("Online Prediction")

# Collect user input for property features
Product_Weight = st.number_input("Product Weight", min_value=0.0, step=0.01, value=1.0)
Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, step=0.01, value=1.0)
Product_MRP = st.number_input("Product MRP", min_value=0.0, step=1.0, value=1.0)
Store_Age_Years = st.number_input("Store Age Years", min_value=0, step=1, value=200)
Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar", "reg"])
Product_Type_Category = st.selectbox("Product Type Category", ["Fruits and Vegetables ", "Snack Foods", "Frozen Foods", "Dairy", "Household", "Baking Goods",
                                             "Canned", "Health and Hygiene", "Meat", "Soft Drinks", "Breads", "Hard Drinks",
                                             "Others", "Starchy Foods", "Breakfast", "Seafood"])

Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart "])


# Convert user input into a DataFrame
input_data = pd.DataFrame([{
    'Product_Weight': Product_Weight,
    'Product_Allocated_Area': Product_Allocated_Area,
    'Product_MRP': Product_MRP,
    'Store_Age_Years': Store_Age_Years,
    'Product_Sugar_Content': Product_Sugar_Content,
    'Product_Type_Category': Product_Type_Category,
    'Store_Size': Store_Size,
    'Store_Location_City_Type': Store_Location_City_Type,
    'Store_Type': Store_Type
}])

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=input_data.to_dict(orient='records')[0],
            timeout=30,
        )
        response.raise_for_status()
        prediction = response.json()['Prediction']
        st.write(f"Predicted Price : {prediction}")
    except requests.RequestException as exc:
        st.error(f"Prediction API request failed at {BACKEND_URL}: {exc}")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file},
                timeout=120,
            )
            response.raise_for_status()
            predictions = response.json()
            st.header("Batch predictions Results")
            st.write(predictions)  # Display the predictions
        except requests.RequestException as exc:
            st.error(f"Batch prediction request failed at {BACKEND_URL}: {exc}")