# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
super_kart_price_predictor_api = Flask("super kart Price Predictor")

# Load the trained machine learning model
model = joblib.load("superkart_prediction_rf_tuned_model_v1_0.joblib")

# Define a route for the home page (GET request)
@super_kart_price_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the Super Kart Price Prediction API!"

# Define an endpoint for single property prediction (POST request)
@super_kart_price_predictor_api.post('/v1/predict')
def predict_rental_price():
    """
    This function handles POST requests to the '/v1/predict' endpoint.
    It expects a JSON payload containing property details and returns
    the predicted rental price as a JSON response.
    """
    # Get the JSON data from the request body
    property_data = request.get_json()



    # Extract relevant features from the JSON data and map them to the model's expected input format
    sample = {
        'Product_Weight': property_data['Product_Weight'],
        'Product_Allocated_Area': property_data['Product_Allocated_Area'],
        'Product_MRP': property_data['Product_MRP'],
        'Store_Establishment_Year': property_data['Store_Age_Years'],
        'Product_Sugar_Content': property_data['Product_Sugar_Content'],
        'Product_Type': property_data['Product_Type_Category'],
        'Store_Size': property_data['Store_Size'],
        'Store_Location_City_Type': property_data['Store_Location_City_Type'],
        'Store_Type': property_data['Store_Type']
        
    }

    print('sample', sample)

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    model_resp = model.predict(input_data)

    print('model_resp',model_resp)

    # Make prediction get retrive the precicted price from the model's response
    predicted_price = model.predict(input_data)[0]
    

    print('predicted_price',predicted_price)

    # # Calculate actual price
    # predicted_price = np.exp(predicted_log_price)

    # # Convert predicted_price to Python float
    # predicted_price = round(float(predicted_price), 2)
    # # The conversion above is needed as we convert the model prediction (log price) to actual price using np.exp, which returns predictions as NumPy float32 values.
    # # When we send this value directly within a JSON response, Flask's jsonify function encounters a datatype error

    # Return the actual price
    return jsonify({'Prediction': predicted_price})


# Define an endpoint for batch prediction (POST request)
@super_kart_price_predictor_api.post('/v1/predictbatch')
def predict_rental_price_batch():
    """
    This function handles POST requests to the '/v1/predictbatch' endpoint.
    It expects a CSV file containing property details for multiple properties
    and returns the predicted rental prices as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Rename columns to match the model's expected input format
    batch_dataset_copy = input_data.rename(columns={
        'Store_Age_Years': 'Store_Establishment_Year',
        'Product_Type_Category': 'Product_Type'
    })

    #extract Product_Id_char column from the input_data DataFrame
    product_ids = input_data['Product_Id_char'].tolist()

    # Drop 'Product_Id_char' as it is not a feature used by the model
    batch_dataset_copy = batch_dataset_copy.drop(columns=['Product_Id_char'])

    # Define the expected order of columns for the model
    expected_columns = [
        'Product_Weight',
        'Product_Allocated_Area',
        'Product_MRP',
        'Store_Establishment_Year',
        'Product_Sugar_Content',
        'Product_Type',
        'Store_Size',
        'Store_Location_City_Type',
        'Store_Type'
    ]

    # Reorder the columns in batch_dataset_copy to match the model's input order
    batch_dataset_copy = batch_dataset_copy[expected_columns]

    
    # Make predictions for all products in the DataFrame
    predicted_prices = model.predict(batch_dataset_copy).tolist()

    #Round the predicted prices to 2 decimal places
    rounded_predicted_prices = [round(price, 2) for price in predicted_prices]
    
    # To display all product_id and predicted_price pairs, even with duplicate product_ids,
    # we can create a list of tuples.
    output_dict = list(zip(product_ids, rounded_predicted_prices)) 

    # Calculate actual prices
    # predicted_prices = [round(float(np.exp(log_price)), 2) for log_price in predicted_log_prices]

    # Create a dictionary of predictions with property IDs as keys
    # property_ids = input_data['id'].tolist()  # Assuming 'id' is the property ID column
    # output_dict = dict(zip(property_ids, predicted_prices))  # Use actual prices
    

    # Return the predictions dictionary as a JSON response
    return output_dict

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    super_kart_price_predictor_api.run(debug=True)
