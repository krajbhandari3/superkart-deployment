# ------------------------------------------------------------
# SuperKart Sales Forecast - Streamlit frontend
# ------------------------------------------------------------

import os
import requests            # sends HTTP requests to the Flask backend
import pandas as pd        # handles the uploaded batch CSV
import streamlit as st     # builds the web UI

# Backend address. Inside the Docker network, containers reach each other
# by CONTAINER NAME, so "superkart-backend" resolves to the Flask container.
# os.getenv lets us override it without editing code; the second value is the default.
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

# Page setup
st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a store.")

# ============================================================
# SECTION 1: Online prediction (one product)
# ============================================================
st.subheader("Online Prediction (single product)")

# Two side-by-side columns: product details left, store details right.
# Default values match the notebook's sample payload, so the first
# prediction can be checked against the notebook's online inference result.
col1, col2 = st.columns(2)

with col1:
    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                   value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
    product_id_char = st.selectbox("Product Category Code", ["FD", "DR", "NC"])

with col2:
    # index= sets which option is pre-selected (0 = first item)
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
    store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_type = st.selectbox("Store Type",
                              ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"],
                              index=2)
    store_age = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)
    product_type_cat = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"], index=1)

# Everything inside this 'if' runs only when the button is clicked
if st.button("Predict Sales"):
    # Package inputs using the EXACT column names the model was trained on
    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar,
        "Product_Allocated_Area": product_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_city,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": store_age,
        "Product_Type_Category": product_type_cat,
    }

    # try/except shows a friendly message instead of crashing the page
    # if the backend is down or unreachable
    try:
        response = requests.post(BACKEND_URL + "/v1/predict", json=payload, timeout=30)

        # 200 = success
        if response.status_code == 200:
            result = response.json()
            st.success("Predicted Sales: " + str(result["Predicted_Sales"]))
        else:
            st.error("API error " + str(response.status_code) + ": " + response.text)

    except requests.exceptions.RequestException as error:
        st.error("Could not reach the backend API: " + str(error))

# Visual separator between the two sections
st.divider()

# ============================================================
# SECTION 2: Batch prediction (CSV upload)
# ============================================================
st.subheader("Batch Prediction (CSV upload)")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Only show the rest once a file has been uploaded
if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(batch_df.head())

    if st.button("Predict Batch"):
        try:
            # Same format the notebook uses: CSV text encoded to bytes under key 'file'
            files = {"file": batch_df.to_csv(header=True, index=False).encode("utf-8")}
            response = requests.post(BACKEND_URL + "/v1/predictbatch", files=files, timeout=60)

            if response.status_code == 200:
                # Response looks like {"0": 1150.74, "1": 3690.94, ...}
                predictions = response.json()

                # Line each prediction up with its row, in order
                predicted_values = []
                for i in range(len(batch_df)):
                    predicted_values.append(predictions[str(i)])

                # Add predictions as a new column and show the full table
                batch_df["Predicted_Sales"] = predicted_values
                st.success("Batch prediction complete!")
                st.dataframe(batch_df)
            else:
                st.error("API error " + str(response.status_code) + ": " + response.text)

        except requests.exceptions.RequestException as error:
            st.error("Could not reach the backend API: " + str(error))
