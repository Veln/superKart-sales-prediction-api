import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecast", layout="wide")
st.title("🛒 SuperKart Sales Forecast App")

st.markdown("---")
# --- Single Prediction ---
st.header("📝 Single Prediction: Enter Sales Information")
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.0)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0, value=0.05, format="%.3f")
        product_type = st.selectbox("Product Type", [
            "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy",
            "Frozen Foods", "Fruits and Vegetables", "Hard Drinks",
            "Health and Hygiene", "Household", "Meat", "Others",
            "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods"
        ])
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=150.0)
    with col2:
        store_establishment_year = st.number_input("Store Establishment Year", min_value=1980, max_value=2024, value=1999)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", [
            "Supermarket Type1", "Supermarket Type2",
            "Departmental Store", "Food Mart"
        ])

    submit_button = st.form_submit_button("Get Forecast")

if submit_button:
    data = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar_content,
        "Product_Allocated_Area": product_allocated_area,
        "Product_Type": product_type,
        "Product_MRP": product_mrp,
        "Store_Establishment_Year": store_establishment_year,
        "Store_Size": store_size,
        "Store_Location_City_Type": store_location_city_type,
        "Store_Type": store_type
    }
    with st.spinner("Predicting..."):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=data)
            if response.status_code == 200:
                prediction = response.json().get("SalesForecast")
                st.success(f"💰 Predicted Sales Revenue: **${prediction:.2f}**")
            else:
                st.error(f"Error from API: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

st.markdown("---")
# --- Batch Prediction ---
st.header("📁 Batch Prediction: Upload CSV")
uploaded_file = st.file_uploader("Choose a CSV file with product and store data", type="csv")

if st.button("Predict Batch") and uploaded_file is not None:
    with st.spinner("Processing batch..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files)

            if response.status_code == 200:
                predictions = response.json()
                res_df = pd.DataFrame(list(predictions.items()), columns=["Identifier", "Predicted_Sales_Total"])

                st.success("Batch prediction successful!")
                st.dataframe(res_df)

                # Provide a download button for the predictions
                csv_data = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Predictions as CSV",
                    data=csv_data,
                    file_name="superkart_batch_predictions.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"Error from API: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
