# inventory_simulation.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor

# 1. Data Simulation Function
def simulate_daily_data(start_date, end_date, skus):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    simulated_data = []

    for current_date in date_range:
        for sku in skus:
            daily_data = {
                "Date": current_date,
                "Product type": np.random.choice(["haircare", "skincare"]),
                "SKU": sku,
                "Price": np.random.uniform(20.0, 100.0),
                "Availability": np.random.randint(50, 150),
                "Number of products sold": np.random.randint(10, 70),
                "Customer demographics": np.random.choice(["Female", "Male", "Non-binary", "Unknown"]),
                "Stock levels": np.random.randint(20, 100),
                "Lead times": np.random.randint(1, 15),
                "Order quantities": np.random.randint(10, 50),
                "Shipping times": np.random.randint(1, 7),
                "Shipping carriers": np.random.choice(["Carrier A", "Carrier B", "Carrier C"]),
                "Shipping costs": np.random.uniform(10.0, 30.0),
                "Supplier name": np.random.choice(["Supplier 1", "Supplier 2", "Supplier 3", "Supplier 4"]),
                "Location": np.random.choice(["Delhi", "Mumbai", "Kolkata", "Bangalore"]),
                "Production volumes": np.random.randint(400, 1000),
                "Manufacturing lead time": np.random.randint(5, 20),
                "Manufacturing costs": np.random.uniform(30.0, 70.0),
                "Inspection results": np.random.choice(["Pass", "Fail", "Pending"]),
                "Defect rates": np.random.uniform(0.5, 3.0),
                "Transportation modes": np.random.choice(["Air", "Road", "Rail"]),
                "Routes": np.random.choice(["Route A", "Route B", "Route C"]),
                "Costs": np.random.uniform(150.0, 350.0),
                "Season": np.random.choice(["Spring", "Summer", "Fall", "Winter"]),
                "Demand Factor": np.random.uniform(0.8, 1.5)
            }
            simulated_data.append(daily_data)

    return pd.DataFrame(simulated_data)

# 2. Generate Simulated Data for Model Training
def generate_training_data():
    # For simplicity, we'll simulate training data similar to the daily data
    skus = ["SKU" + str(i) for i in range(1, 46)]  # 45 SKUs for training
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)  # One year of data

    training_data = simulate_daily_data(start_date, end_date, skus)

    # Add target variables for training
    training_data['Restock Indicator'] = np.random.randint(0, 2, size=len(training_data))
    training_data['Restock Date (days)'] = np.random.randint(5, 15, size=len(training_data))
    training_data['Restock Quantity'] = np.random.randint(10, 100, size=len(training_data))
    training_data['Predicted Costs'] = np.random.uniform(200.0, 500.0, size=len(training_data))

    return training_data

# 3. Prepare Data for Model Training
def prepare_training_data(training_data):
    # Drop unnecessary columns
    X = training_data.drop(columns=['Date', 'SKU', 'Restock Indicator', 'Restock Date (days)', 'Restock Quantity', 'Predicted Costs'])
    y = training_data[['Restock Indicator', 'Restock Date (days)', 'Restock Quantity', 'Predicted Costs']]

    # Identify categorical and numerical columns
    categorical_columns = X.select_dtypes(include=['object']).columns.tolist()
    numeric_columns = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # One-hot encode categorical columns
    X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

    # Standardize numeric columns
    scaler = StandardScaler()
    X_encoded[numeric_columns] = scaler.fit_transform(X_encoded[numeric_columns])

    return X_encoded, y, scaler, categorical_columns, numeric_columns

# 4. Train the Model
def train_model(X, y):
    # Use a Random Forest Regressor as the base estimator
    base_estimator = RandomForestRegressor(n_estimators=100, random_state=42)
    multi_output_model = MultiOutputRegressor(base_estimator)
    multi_output_model.fit(X, y)
    return multi_output_model

# 5. Prediction Function
def predict_inventory_management(new_data, multi_output_model, X_columns, scaler, categorical_columns, numeric_columns):
    """
    Predict warehouse metrics for multiple SKUs using the trained multi-output model.
    """
    # One-hot encode new data and align it with training data
    new_data_encoded = pd.get_dummies(new_data, columns=categorical_columns, drop_first=True)
    
    # Identify and add any missing columns to match the training data
    missing_cols = list(set(X_columns) - set(new_data_encoded.columns))
    # Create a DataFrame of zeros for missing columns and concatenate
    if missing_cols:
        missing_df = pd.DataFrame(0, index=new_data_encoded.index, columns=missing_cols)
        new_data_encoded = pd.concat([new_data_encoded, missing_df], axis=1)
    
    # Reorder columns to match the training set
    new_data_encoded = new_data_encoded[X_columns]

    # Standardize numeric columns
    new_data_encoded[numeric_columns] = scaler.transform(new_data_encoded[numeric_columns])

    # Make predictions
    predictions = multi_output_model.predict(new_data_encoded)

    # Format the results for each SKU
    inventory_metrics = []
    for i in range(len(new_data)):
        metrics = {
            "SKU": new_data["SKU"].iloc[i],
            "Restock Indicator": int(round(predictions[i][0])),
            "Restock Date (days)": int(round(predictions[i][1])),
            "Restock Quantity": int(round(predictions[i][2])),
            "Predicted Costs": round(predictions[i][3], 2)
        }
        inventory_metrics.append(metrics)

    return inventory_metrics

# 6. Main Function to Run the Simulation
def main():
    # Generate and prepare training data
    training_data = generate_training_data()
    X, y, scaler, categorical_columns, numeric_columns = prepare_training_data(training_data)

    # Train the model
    multi_output_model = train_model(X, y)
    X_columns = X.columns  # Save column names for aligning during prediction

    # Define the SKUs to simulate
    skus = ["SKU47", "SKU48", "SKU49", "SKU50"]

    # Define the simulation period
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)  # Simulate for one month

    # Simulate daily data for the entire period
    simulated_data = simulate_daily_data(start_date, end_date, skus)

    # Initialize a list to store all daily predictions
    daily_predictions = []

    # Process data day by day
    current_date = start_date
    while current_date <= end_date:
        # Get data for the current day
        daily_data = simulated_data[simulated_data['Date'] == current_date]

        if not daily_data.empty:
            # Drop the 'Date' column for prediction
            prediction_data = daily_data.drop(columns=['Date']).reset_index(drop=True)

            # Generate predictions for the day
            predictions = predict_inventory_management(
                prediction_data, multi_output_model, X_columns, scaler, categorical_columns, numeric_columns
            )

            # Add the date to each prediction
            for i, prediction in enumerate(predictions):
                prediction['Date'] = current_date
                prediction['Product type'] = daily_data.iloc[i]['Product type']
                daily_predictions.append(prediction)

        # Move to the next day
        current_date += timedelta(days=1)

    # Convert daily_predictions to a DataFrame
    predictions_df = pd.DataFrame(daily_predictions)

    # Aggregate weekly predictions
    predictions_df['Date'] = pd.to_datetime(predictions_df['Date'])
    predictions_df['Week'] = predictions_df['Date'].dt.isocalendar().week

    weekly_predictions = predictions_df.groupby(['Week', 'SKU']).agg({
        'Restock Indicator': 'sum',
        'Restock Date (days)': 'mean',
        'Restock Quantity': 'sum',
        'Predicted Costs': 'sum',
        'Product type': 'first'
    }).reset_index()

    weekly_predictions = weekly_predictions.sort_values(by=['Week', 'SKU'])

    # Save the results to CSV files (optional)
    simulated_data.to_csv('simulated_data.csv', index=False)
    predictions_df.to_csv('daily_predictions.csv', index=False)
    weekly_predictions.to_csv('weekly_predictions.csv', index=False)

    # Print the weekly predictions
    print("Weekly Predictions:")
    print(weekly_predictions)

    # Visualize the results
    visualize_results(weekly_predictions, skus)

# 7. Visualization Function
def visualize_results(weekly_predictions, skus):
    # Plot Restock Quantity per SKU over Weeks
    plt.figure(figsize=(10, 6))
    for sku in skus:
        sku_data = weekly_predictions[weekly_predictions['SKU'] == sku]
        plt.plot(sku_data['Week'], sku_data['Restock Quantity'], marker='o', label=sku)

    plt.xlabel('Week Number')
    plt.ylabel('Total Restock Quantity')
    plt.title('Weekly Restock Quantity per SKU')
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the main function
if __name__ == '__main__':
    main()
