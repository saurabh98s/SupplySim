import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import mlflow
import mlflow.sklearn

def train_model():
    # Load historical data
    df = pd.read_csv('data/processed/transformed_data.csv')
    df = df[df['Date'] < '2023-09-01']  # Use data before September 2023 for training
    
    # Prepare data
    X = df[['Availability', 'Price', 'Stock_levels', 'Lead_times', 'Order_quantities', 'Production_volumes']]
    y = df['Number_of_products_sold']
    X = pd.get_dummies(X)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("random_state", 42)
        
        # Train the model
        model.fit(X, y)
        
        # Predictions on training set
        predictions = model.predict(X)
        
        # Calculate metrics
        mse = mean_squared_error(y, predictions)
        mlflow.log_metric("mse", mse)
        
        # Log the model
        mlflow.sklearn.log_model(model, "model")
        
        # Save the model locally
        joblib.dump(model, 'models/trained_model.joblib')
        print("Model trained and saved at models/trained_model.joblib")

if __name__ == '__main__':
    mlflow.set_tracking_uri("http://localhost:5001")  # Ensure MLflow tracking server is accessible
    train_model()
