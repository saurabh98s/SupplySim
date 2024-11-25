import pandas as pd
import matplotlib.pyplot as plt

file_path = 'S:/SJSU/DATA_226/group_project/daily_time_series_data.csv'
daily_df = pd.read_csv(file_path)

# Convert the 'Date' column to a datetime object
daily_df['Date'] = pd.to_datetime(daily_df['Date'])

# Plotting daily sales and stock levels for visualization
plt.figure(figsize=(20, 6))

# Plot daily sales
plt.subplot(1, 2, 1)
for sku in daily_df['SKU'].unique():
    product_data = daily_df[daily_df['SKU'] == sku]
    plt.plot(product_data['Date'], product_data['Daily Sales'], label=f"{sku} Sales")
plt.xlabel('Date')
plt.ylabel('Daily Sales')
plt.title('Daily Sales Over Time')
plt.legend()
plt.tight_layout()
plt.show()

# Plot stock levels
plt.subplot(1, 2, 2)
for sku in daily_df['SKU'].unique():
    product_data = daily_df[daily_df['SKU'] == sku]
    plt.plot(product_data['Date'], product_data['Stock Level'], label=f"{sku} Stock Level")
plt.xlabel('Date')
plt.ylabel('Stock Level')
plt.title('Stock Levels Over Time')
plt.legend()

plt.tight_layout()
plt.show()