import pandas as pd

def extract_data():
    df = pd.read_csv('data/synthetic/improved_dataset.csv')
    df.to_csv('data/processed/extracted_data.csv', index=False)
    print("Data extracted to data/processed/extracted_data.csv")

if __name__ == '__main__':
    extract_data()
