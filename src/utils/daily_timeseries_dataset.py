import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Load the cleaned dataset
file_path = 'S:/SJSU/DATA_226/group_project/data/processed/cleaned_improved_dataset.csv'
data = pd.read_csv(file_path)

# Function to generate daily time-series data
def generate_daily_data(record):
    daily_data = []
    current_date = datetime.now() - timedelta(days=60)  # Start 30 days ago
    stock_level = 1000000  # Initial stock level from the dataset
    daily_sales_avg = record["Number of products sold"]  # Average daily sales from the dataset
    demand_factor = record["Demand Factor"]  # Demand multiplier for variability

    # Set to keep track of generated dates to avoid duplicates
    generated_dates = set()

    for day in range(30):
        date = current_date + timedelta(days=day)
        date_str = date.strftime("%Y-%m-%d")

        if date_str in generated_dates:
            continue  # Skip if the date is already in the set

        generated_dates.add(date_str)  # Add the date to the set

        # Simulate daily sales with randomness and the demand factor
        daily_sales = max(0, np.random.poisson(daily_sales_avg * demand_factor))
        stock_level = max(0, stock_level - daily_sales)  # Ensure stock level doesn't go negative

        # Create a daily record
        daily_record = {
            "Date": date_str,
            "Product type": record["Product type"],
            "SKU": record["SKU"],
            "Daily Sales": daily_sales,
            "Stock Level": stock_level,
            "Price": record["Price"],
            "Revenue Generated": daily_sales * record["Price"],  # Calculate daily revenue
            "Season": record["Season"],
            "Demand Factor": record["Demand Factor"]
        }
        daily_data.append(daily_record)

    return daily_data

# Generate daily data for each product in the dataset
all_daily_data = []
for index, record in data.iterrows():
    all_daily_data.extend(generate_daily_data(record))

# Convert to DataFrame
daily_df = pd.DataFrame(all_daily_data)
# Remove duplicates based on 'Date' and 'SKU' columns
daily_df = daily_df.drop_duplicates(subset=["Date", "SKU"])

# Save to a new CSV file
daily_df.to_csv('daily_time_series_data_cleaned.csv', index=False)

# Display the first few rows
print(daily_df.head())

# Save to a new CSV file
daily_df.to_csv('daily_time_series_data_with_seasonal_effects.csv', index=False)

# Display the first few rows
print(daily_df.head())

# Check for duplicates: Same SKU and same Date
duplicates = daily_df.duplicated(subset=["SKU", "Date"], keep=False)

# Display rows that are duplicates
duplicate_rows = daily_df[duplicates]

# Check if there are any duplicates and print the result
if not duplicate_rows.empty:
    print("Duplicate entries found for the same SKU on the same date:")
    print(duplicate_rows)
else:
    print("No duplicate entries found for the same SKU on the same date.")