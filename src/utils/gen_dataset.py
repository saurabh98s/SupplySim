import pandas as pd
import random

# Function to generate a seasonal demand factor
def generate_seasonal_demand():
    # Seasonal demand can be higher or lower depending on the time of year
    seasons = ["Winter", "Spring", "Summer", "Fall"]
    season = random.choice(seasons)
    
    # Assigning demand factors: higher in Summer and Winter, moderate in Spring and Fall
    demand_factor = {
        "Winter": random.uniform(1.2, 1.5),  # Higher demand in Winter
        "Spring": random.uniform(0.8, 1.1),  # Moderate demand in Spring
        "Summer": random.uniform(1.3, 1.6),  # Higher demand in Summer
        "Fall": random.uniform(0.9, 1.2)     # Moderate demand in Fall
    }
    
    return season, demand_factor[season]

# Function to generate a better quality random datapoint
def generate_better_random_datapoint():
    product_type = random.choice(["haircare", "skincare"])
    sku = f"SKU{random.randint(0, 100)}"

    # Logical pricing: skincare is typically more expensive than haircare
    price = round(random.uniform(5, 50) if product_type == "haircare" else random.uniform(20, 100), 2)
    
    # Availability and stock levels should be consistent with demand and product type
    availability = random.randint(10, 200)
    stock_levels = random.randint(10, availability)  # Stock levels shouldn't exceed availability

    # Sales data and revenue: Higher price and availability imply potentially higher revenue
    number_of_products_sold = random.randint(1, availability)
    revenue_generated = round(price * number_of_products_sold, 2)

    # Customer demographics should be a realistic mix
    customer_demographics = random.choice(["Male", "Female", "Non-binary", "Unknown"])

    # Order quantities should be sensible given stock levels
    order_quantities = random.randint(1, min(availability, 50))

    # Shipping times and carriers: Faster times for air transport, slower for road or rail
    transportation_modes = random.choice(["Road", "Air", "Rail"])
    shipping_times = {
        "Road": random.randint(5, 10),
        "Air": random.randint(1, 5),
        "Rail": random.randint(3, 7)
    }[transportation_modes]

    shipping_carriers = {
        "Road": random.choice(["Carrier A", "Carrier B"]),
        "Air": "Carrier C",
        "Rail": random.choice(["Carrier D", "Carrier E"])
    }[transportation_modes]

    shipping_costs = round(random.uniform(10, 100) if transportation_modes == "Air" else random.uniform(5, 50), 2)

    # Supplier details and production logic
    supplier_name = random.choice(["Supplier 1", "Supplier 2", "Supplier 3"])
    location = random.choice(["Mumbai", "Delhi", "Bangalore"])
    production_volumes = random.randint(100, 1000)
    lead_time = random.randint(7, 30)  # Lead time for getting supplies from the supplier
    manufacturing_lead_time = random.randint(5, 20)  # Shorter time for faster production

    # Costs and quality checks: Higher costs might be associated with better quality
    manufacturing_costs = round(random.uniform(10, 50), 2)
    inspection_results = random.choice(["Pass", "Fail", "Pending"])
    defect_rates = round(random.uniform(0, 2) if inspection_results == "Pass" else random.uniform(2, 5), 3)

    # Transportation logic: Routes and costs should be in sync with the mode
    routes = random.choice(["Route A", "Route B", "Route C"])
    costs = round(random.uniform(100, 500), 2)

    # Seasonal demand factors: Making higher demand more likely in summer and winter
    season, demand_factor = generate_seasonal_demand()

    return {
        "Product type": product_type,
        "SKU": sku,
        "Price": price,
        "Availability": availability,
        "Number of products sold": number_of_products_sold,
        "Revenue generated": revenue_generated,
        "Customer demographics": customer_demographics,
        "Stock levels": stock_levels,
        "Lead times": lead_time,
        "Order quantities": order_quantities,
        "Shipping times": shipping_times,
        "Shipping carriers": shipping_carriers,
        "Shipping costs": shipping_costs,
        "Supplier name": supplier_name,
        "Location": location,
        "Lead time": lead_time,
        "Production volumes": production_volumes,
        "Manufacturing lead time": manufacturing_lead_time,
        "Manufacturing costs": manufacturing_costs,
        "Inspection results": inspection_results,
        "Defect rates": defect_rates,
        "Transportation modes": transportation_modes,
        "Routes": routes,
        "Costs": costs,
        "Season": season,
        "Demand Factor": demand_factor
    }

# Generate 100 better quality random datapoints
better_data = [generate_better_random_datapoint() for _ in range(1000)]

# Create a DataFrame with improved data quality
better_df = pd.DataFrame(better_data)
data = better_df
# Code to check for common data issues in the dataset

# 1. Check for Missing Values
missing_values = data.isnull().sum()
print("Missing Values in Each Column:\n", missing_values)

# 2. Identify Outliers Using Z-score Method
from scipy import stats

# Calculating z-scores for each numeric column to identify outliers
z_scores = stats.zscore(data[numeric_columns])
outliers = (abs(z_scores) > 3).sum(axis=0)
print("\nNumber of Outliers in Each Numeric Column (Z-score > 3):\n", outliers)

# 3. Check Skewness of Numeric Columns
skewness = data[numeric_columns].skew()
print("\nSkewness of Numeric Columns:\n", skewness)

# 4. Analyze Distribution of Categorical Variables
categorical_columns = data.select_dtypes(include=['object']).columns
categorical_distributions = {col: data[col].value_counts() for col in categorical_columns}
print("\nDistribution of Categorical Variables:")
for col, distribution in categorical_distributions.items():
    print(f"\n{col}:\n{distribution}")

# 5. Check for Class Imbalance in Categorical Variables
class_imbalance = {col: (data[col].value_counts(normalize=True) * 100).to_dict() for col in categorical_columns}
print("\nClass Imbalance (Percentage Distribution) of Categorical Variables:")
for col, imbalance in class_imbalance.items():
    print(f"\n{col}:\n{imbalance}")

# 6. Checking for High Correlation (Redundancy)
high_correlation_pairs = []
correlation_threshold = 0.8
for i in range(len(numeric_columns)):
    for j in range(i+1, len(numeric_columns)):
        if abs(correlation_matrix.iloc[i, j]) > correlation_threshold:
            high_correlation_pairs.append((numeric_columns[i], numeric_columns[j], correlation_matrix.iloc[i, j]))

print("\nHighly Correlated Feature Pairs (Correlation > 0.8):")
for pair in high_correlation_pairs:
    print(f"{pair[0]} and {pair[1]}: {pair[2]}")

# Output results
missing_values, outliers, skewness, categorical_distributions, class_imbalance, high_correlation_pairs


# Save the DataFrame to a CSV file
better_df.to_csv("S:/SJSU\DATA_226/group_project/data/raw/improved_dataset.csv", index=False)
better_df.head()
