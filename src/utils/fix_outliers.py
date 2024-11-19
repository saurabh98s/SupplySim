# Import necessary libraries
import pandas as pd
import numpy as np
from scipy import stats

# Load the dataset from the CSV file
file_path = 'S:/SJSU/DATA_226/group_project/data/raw/improved_dataset.csv'
data = pd.read_csv(file_path)

# 1. Handling Outliers Using Z-score Method
# We'll cap the outliers in "Number of products sold", "Revenue generated", and "Stock levels"
z_scores = stats.zscore(data[["Number of products sold", "Revenue generated", "Stock levels"]])
threshold = 3

# Cap the outliers beyond the threshold
for column in ["Number of products sold", "Revenue generated", "Stock levels"]:
    upper_limit = data[column].mean() + threshold * data[column].std()
    lower_limit = data[column].mean() - threshold * data[column].std()
    data[column] = np.where(data[column] > upper_limit, upper_limit, data[column])
    data[column] = np.where(data[column] < lower_limit, lower_limit, data[column])

# 2. Transform Skewed Variables
# Applying log transformation to reduce skewness in "Revenue generated" and "Stock levels"
data["Revenue generated"] = np.log1p(data["Revenue generated"])  # log1p to handle zero values
data["Stock levels"] = np.log1p(data["Stock levels"])

# 3. Dropping Redundant Features
# Removing "Lead time" due to perfect correlation with "Lead times"
data = data.drop(columns=["Lead time"])

# Save the cleaned dataset to a new CSV file
cleaned_file_path = 'cleaned_improved_dataset.csv'
data.to_csv(cleaned_file_path, index=False)

cleaned_file_path
