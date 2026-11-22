"""
SuperKart sales forecasting API (Flask backend).

Routes:
    GET  /                -> health check, returns a welcome message
    POST /v1/predict      -> predicts the sales of ONE product-store combination sent as JSON
    POST /v1/predictbatch -> predicts the sales of MANY rows uploaded as a CSV file (form field "file")
"""

# Import the necessary libraries
import joblib                              # to load the serialized model pipeline
import pandas as pd                        # to build the DataFrame the model expects
from flask import Flask, request, jsonify  # to create the REST API

# Initialize the Flask app with a name
superkart_api = Flask("SuperKart")

# Keep the keys of the JSON responses in insertion order (row 0, 1, 2, ...) instead of sorting them
superkart_api.json.sort_keys = False

# Load the trained pipeline (preprocessing + model) once, when the server starts
model = joblib.load("superkart_model.joblib")

# The 10 features the model was trained on, in the training order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (also used as a health check)
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart System"


# Define an endpoint to predict the sales of a single product (online inference)
@superkart_api.post("/v1/predict")
def predict_sales():
    # Get the JSON data sent in the body of the request
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "The request body must be a JSON object."}), 400

    # Check that every feature expected by the model is present
    missing = [feature for feature in FEATURES if feature not in data]
    if missing:
        return jsonify({"error": f"Missing feature(s): {missing}"}), 400

    # Keep only the model features (in the training order) in a one-row DataFrame
    input_data = pd.DataFrame([{feature: data[feature] for feature in FEATURES}])

    # Make a prediction using the trained model
    try:
        prediction = float(model.predict(input_data)[0])
    except Exception as e:  # e.g., a text value sent for a numeric feature
        return jsonify({"error": f"Prediction failed: {e}"}), 400

    # Return the prediction as a JSON response
    return jsonify({"Sales": round(prediction, 2)})


# Define an endpoint to predict the sales of a batch of products (batch inference)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Get the uploaded CSV file from the request and read it into a DataFrame
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file in the form field 'file'."}), 400
    input_data = pd.read_csv(request.files["file"])

    # Check that every feature expected by the model is present
    missing = [feature for feature in FEATURES if feature not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing column(s): {missing}"}), 400

    # Make predictions for all the rows of the batch
    try:
        predictions = model.predict(input_data[FEATURES])
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 400

    # Map each row index to its predicted sales value (rounded to 2 decimals)
    output_dict = {str(i): round(float(pred), 2) for i, pred in enumerate(predictions)}
    return jsonify(output_dict)


# Run the Flask development server when the script is executed directly
# (inside the Docker container the app is served by Gunicorn instead, see the Dockerfile)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
