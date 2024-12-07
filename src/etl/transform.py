import pandas as pd

def transform_data():
    df = pd.read_csv('data/processed/extracted_data.csv')
    
    # Perform transformations
    df['Price'] = df['Price'].round(2)
    df['Manufacturing_costs'] = df['Manufacturing_costs'].round(2)
    df['Defect_rates'] = df['Defect_rates'].round(2)
    df['Costs'] = df['Costs'].round(2)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Handle missing values if any
    df.fillna(method='ffill', inplace=True)
    
    df.to_csv('data/processed/transformed_data.csv', index=False)
    print("Data transformed and saved to data/processed/transformed_data.csv")

if __name__ == '__main__':
    transform_data()
