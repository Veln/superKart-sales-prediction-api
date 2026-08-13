from flask import Flask, request, jsonify
import joblib
import pandas as pd
import traceback

app = Flask("Superkart Sales Forecast API")

# Load the serialized model
# We assume the model file will be copied to the same directory as app.py in the Docker container
try:
    model = joblib.load("superkart_sales_model.joblib")
except FileNotFoundError:
    # Fallback for local testing if run from the parent directory
    model = joblib.load("deployment_files/superkart_sales_model.joblib")

@app.get('/')
def home():
    """
    GET endpoint to display a welcome message and check API health.
    """
    return "Welcome to the SuperKart Sales Forecasting API!"


@app.post('/v1/predict')
def predict():
    """
    POST endpoint to make sales predictions.
    Expects a JSON payload with the product and store features.
    """
    try:
        # Get JSON data from the POST request
        sales_data = request.get_json()

        # Extract relevant sales features from the input data
        sample = {
            'Product_Weight': sales_data.get('Product_Weight'),
            'Product_Sugar_Content': sales_data.get('Product_Sugar_Content'),
            'Product_Allocated_Area': sales_data.get('Product_Allocated_Area'),
            'Product_Type': sales_data.get('Product_Type'),
            'Product_MRP': sales_data.get('Product_MRP'),
            'Store_Establishment_Year': sales_data.get('Store_Establishment_Year'),
            'Store_Size': sales_data.get('Store_Size'),
            'Store_Location_City_Type': sales_data.get('Store_Location_City_Type'),
            'Store_Type': sales_data.get('Store_Type')
        }

        # Convert the JSON data into a pandas DataFrame
        input_data = pd.DataFrame([sample])

        # Use the loaded model to make predictions
        prediction = model.predict(input_data).tolist()[0]

        # Return the predictions as a JSON response
        return jsonify({"SalesForecast": prediction})

    except Exception as e:
        # Return error message and a 400 Bad Request status code
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 400

# Define an endpoint to predict sales for a batch of products
@app.post('/v1/predictbatch')
def predict_sales_batch():
    try:
        # Get the uploaded CSV file from the request
        file = request.files['file']

        # Read the file into a DataFrame
        input_data = pd.read_csv(file)

        # Identify columns to drop (identifiers not used in the model)
        drop_cols = [col for col in ['Product_Id', 'Store_Id', 'Product_Store_Sales_Total'] if col in input_data.columns]
        features = input_data.drop(columns=drop_cols)

        # Make predictions for the batch data
        predictions = model.predict(features).tolist()

        # Convert predictions into a readable format mapping Product_Id to predicted sales
        if 'Product_Id' in input_data.columns:
            id_list = input_data['Product_Id'].astype(str).tolist()
        else:
            id_list = [f"Row_{i}" for i in range(len(input_data))]

        output_dict = dict(zip(id_list, predictions))

        return jsonify(output_dict)

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
