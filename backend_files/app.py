# ------------------------------------------------------------
# SuperKart Sales Prediction API (Flask backend)
# ------------------------------------------------------------

# joblib  -> loads the saved model pipeline from disk
# pandas  -> converts incoming request data into a DataFrame the model expects
# Flask   -> the web framework; request reads incoming data, jsonify sends JSON back
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Create the Flask app. The variable name 'superkart_api' matches the
# endpoint decorators referenced in the notebook template.
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained pipeline ONCE when the server starts (not on every request),
# so each prediction is fast. The file sits in the same folder as app.py.
model = joblib.load("superkart_model.joblib")


# --- Home route: a simple health check ---
# Opening the base URL in a browser shows this message,
# which confirms the server is up before testing predictions.
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# --- Online (single) prediction endpoint ---
# Receives ONE product-store record as JSON and returns ONE prediction.
@superkart_api.post("/v1/predict")
def predict_sales():
    # Read the JSON body sent by the client (Streamlit or the notebook)
    data = request.get_json()

    # Pick out exactly the 10 features the model was trained on.
    # Building the dict explicitly means any extra fields in the request are ignored.
    sample = {
        "Product_Weight": data["Product_Weight"],
        "Product_Sugar_Content": data["Product_Sugar_Content"],
        "Product_Allocated_Area": data["Product_Allocated_Area"],
        "Product_MRP": data["Product_MRP"],
        "Store_Size": data["Store_Size"],
        "Store_Location_City_Type": data["Store_Location_City_Type"],
        "Store_Type": data["Store_Type"],
        "Product_Id_char": data["Product_Id_char"],
        "Store_Age_Years": data["Store_Age_Years"],
        "Product_Type_Category": data["Product_Type_Category"],
    }

    # The pipeline expects a DataFrame (a table), so wrap the single record in a list
    input_df = pd.DataFrame([sample])

    # predict() returns an array; [0] takes the single value out of it
    prediction = model.predict(input_df)[0]

    # Convert numpy float -> plain Python float (JSON can't serialize numpy types)
    # and round to 2 decimals like a currency amount
    prediction = round(float(prediction), 2)

    # Send the result back as JSON
    return jsonify({"Predicted_Sales": prediction})


# --- Batch prediction endpoint ---
# Receives a CSV FILE with many rows and returns one prediction per row.
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # The uploaded file arrives under the key 'file' (matches the notebook's batch_input)
    file = request.files["file"]

    # Read the uploaded CSV straight into a DataFrame
    input_df = pd.read_csv(file)

    # Predict all rows at once (much faster than looping one by one)
    predictions = model.predict(input_df)

    # Build a dictionary: row index -> predicted sales
    # Keys are strings because JSON object keys must be text
    results = {}
    for i in range(len(predictions)):
        results[str(i)] = round(float(predictions[i]), 2)

    return jsonify(results)


# --- Start the server ---
# Runs only when this file is executed directly (python app.py), not when imported.
# host="0.0.0.0" -> accept connections from outside the container (required for Docker)
# port=7860      -> the port the notebook template expects
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
