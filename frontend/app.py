"""
SuperKart sales forecasting - Streamlit frontend.

The user enters the details of a product and a store (or uploads a CSV file of products); the app sends
them to the Flask backend API and displays the predicted sales.
"""
import os

import pandas as pd
import requests
import streamlit as st

# Base URL of the Flask backend.
# Inside the Docker network the backend container is reached through its container name ("backend").
# The BACKEND_URL environment variable can override it, e.g., when running the app outside Docker.
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

# Page configuration and title
st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecasting")
st.write("Enter the product and store details below to predict the total sales of the product in the store.")

# ------------------------------------------------------------------
# Online (single) prediction
# ------------------------------------------------------------------
st.subheader("Single Prediction")

# Input fields: product details on the left, store details on the right.
# The options are the categories seen during training; the default values match the sample payload.
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Product details**")
    Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input(
        "Product Allocated Area (share of the display area)",
        min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f",
    )
    Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
    Product_Id_char = st.selectbox(
        "Product ID Prefix", ["FD", "DR", "NC"], help="FD = Food, DR = Drinks, NC = Non-Consumables"
    )
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"], index=1)

with col2:
    st.markdown("**Store details**")
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    Store_Type = st.selectbox(
        "Store Type", ["Departmental Store", "Food Mart", "Supermarket Type1", "Supermarket Type2"], index=3
    )
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16, step=1)

# JSON payload with the exact feature names expected by the backend
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

# Send the payload to the backend and show the predicted sales
if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted Product Store Sales Total: {predicted_sales:,.2f}")
        else:
            st.error(f"The API returned an error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the prediction API at {BACKEND_URL}: {e}")

# ------------------------------------------------------------------
# Batch prediction
# ------------------------------------------------------------------
st.subheader("Batch Prediction")
st.write("Upload a CSV file with the 10 feature columns to predict the sales of many products at once.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Preview the uploaded data
    input_df = pd.read_csv(uploaded_file)
    st.write("Preview of the uploaded data:")
    st.dataframe(input_df.head(), use_container_width=True)

    if st.button("Predict for Batch", type="primary"):
        try:
            # Send the CSV file to the batch endpoint
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                timeout=60,
            )
            if response.status_code == 200:
                # The API returns {"0": prediction, "1": prediction, ...}: add the values as a new column
                predictions = response.json()
                results = input_df.copy()
                results["Predicted_Sales"] = [predictions[str(i)] for i in range(len(results))]

                st.success("Predictions completed successfully!")
                st.dataframe(results, use_container_width=True)

                # Let the user download the predictions
                st.download_button(
                    "Download predictions as CSV",
                    data=results.to_csv(index=False).encode("utf-8"),
                    file_name="superkart_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"The API returned an error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the prediction API at {BACKEND_URL}: {e}")
