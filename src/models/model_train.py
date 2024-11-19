import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import mlflow
import mlflow.sklearn

# Load the cleaned dataset
data = pd.read_csv('S:/SJSU/DATA_226/group_project/data/raw/cleaned_improved_dataset.csv')

# 1. Feature Engineering
# Include "SKU" in the categorical columns for one-hot encoding
categorical_columns = ["Product type", "SKU", "Customer demographics", "Shipping carriers", 
                       "Supplier name", "Location", "Inspection results", 
                       "Transportation modes", "Routes", "Season"]

# One-hot encoding for all categorical variables, including SKU
data_encoded = pd.get_dummies(data, columns=categorical_columns, drop_first=True)

# Extract features and target variable
X = data_encoded.drop(columns=["Revenue generated"])  # Features
y = data_encoded["Revenue generated"]  # Target

# Identify the numeric columns for transformations
numeric_columns = X.select_dtypes(include=['float64', 'int64']).columns

# Standardize numerical features
scaler = StandardScaler()
X[numeric_columns] = scaler.fit_transform(X[numeric_columns])

# Cyclical Encoding for Temporal Features
season_mapping = {"Winter": 0, "Spring": 1, "Summer": 2, "Fall": 3}
data_encoded["Season_Cyclical"] = data["Season"].map(season_mapping)
X["Season_Sin"] = np.sin(2 * np.pi * data_encoded["Season_Cyclical"] / 4)
X["Season_Cos"] = np.cos(2 * np.pi * data_encoded["Season_Cyclical"] / 4)
X = X.drop(columns=["Season_Cyclical"], errors='ignore')

# 2. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Start an MLflow run
mlflow.start_run()

# 3. Model Training: Random Forest Regressor
model = RandomForestRegressor(n_estimators=400, random_state=45)
model.fit(X_train, y_train)

# 4. Model Evaluation
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Log parameters and metrics to MLflow
mlflow.log_param("n_estimators", 400)
mlflow.log_param("random_state", 45)
mlflow.log_metric("mse", mse)
mlflow.log_metric("r2", r2)

# Log the model
mlflow.sklearn.log_model(model, "random_forest_model")

# End the MLflow run
mlflow.end_run()

# Print metrics
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# 5. Feature Importance Analysis
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

# Print the top 10 important features
print("\nTop 10 Important Features:")
print(feature_importance_df.head(10))
