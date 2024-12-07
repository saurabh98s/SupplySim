import pandas as pd
import numpy as np

def generate_synthetic_data():
    num_records = 1000
    np.random.seed(42)
    
    data = {
        'Date': pd.date_range(start='2023-01-01', periods=num_records, freq='D'),
        'SKU': np.random.choice(['SKU47', 'SKU48', 'SKU49', 'SKU50'], num_records),
        'Product_type': np.random.choice(['skincare', 'haircare'], num_records),
        'Price': np.random.uniform(10, 100, num_records),
        'Availability': np.random.randint(0, 200, num_records),
        'Number_of_products_sold': np.random.randint(0, 100, num_records),
        'Customer_demographics': np.random.choice(['Male', 'Female', 'Non-binary', 'Unknown'], num_records),
        'Stock_levels': np.random.randint(0, 100, num_records),
        'Lead_times': np.random.randint(1, 20, num_records),
        'Order_quantities': np.random.randint(10, 500, num_records),
        'Shipping_times': np.random.randint(1, 7, num_records),
        'Production_volumes': np.random.randint(500, 1000, num_records),
        'Manufacturing_lead_time': np.random.randint(5, 20, num_records),
        'Manufacturing_costs': np.random.uniform(30, 70, num_records),
        'Inspection_results': np.random.choice(['Pass', 'Fail', 'Pending'], num_records),
        'Defect_rates': np.random.uniform(0.5, 2.0, num_records),
        'Transportation_modes': np.random.choice(['Air', 'Road', 'Rail'], num_records),
        'Routes': np.random.choice(['Route A', 'Route B', 'Route C'], num_records),
        'Costs': np.random.uniform(200, 400, num_records),
        'Season': np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], num_records),
        'Demand_Factor': np.random.uniform(0.8, 1.2, num_records),
    }

    df = pd.DataFrame(data)
    df.to_csv('data/synthetic/improved_dataset.csv', index=False)
    print("Synthetic data generated and saved to data/synthetic/improved_dataset.csv")

if __name__ == '__main__':
    generate_synthetic_data()
