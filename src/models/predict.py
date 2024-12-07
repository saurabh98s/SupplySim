import pandas as pd
import joblib
import mlflow

def generate_weekly_predictions():
    # Load the model
    model = joblib.load('models/trained_model.joblib')
    
    # Load new data
    df = pd.read_csv('data/processed/transformed_data.csv')
    df = df[df['Date'] >= '2023-09-01']  # Use recent data for prediction
    
    # Prepare data
    X = df[['Availability', 'Price', 'Stock_levels', 'Lead_times', 'Order_quantities', 'Production_volumes']]
    X = pd.get_dummies(X)
    
    # Ensure the feature columns match the training data
    model_features = model.feature_names_in_
    for feature in model_features:
        if feature not in X.columns:
            X[feature] = 0
    X = X[model_features]
    
    # Generate predictions
    with mlflow.start_run():
        predictions = model.predict(X)
        
        # Log prediction artifacts
        df['Predicted_Sales'] = predictions
        df.to_csv('data/processed/predictions.csv', index=False)
        mlflow.log_artifact('data/processed/predictions.csv', artifact_path="predictions")
        
        print("Weekly predictions generated and saved to data/processed/predictions.csv")

if __name__ == '__main__':
    mlflow.set_tracking_uri("http://localhost:5001")
    generate_weekly_predictions()
