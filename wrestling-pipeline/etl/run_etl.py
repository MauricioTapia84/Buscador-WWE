import os
import pandas as pd

def main():
    print("Starting one-shot ETL")
    df = pd.DataFrame({"id": [1,2], "name": ["John Example", "Jane Demo"]})
    out = "/app/output"
    os.makedirs(out, exist_ok=True)
    csv_path = os.path.join(out, "wrestlers_extracted.csv")
    df.to_csv(csv_path, index=False)
    print(f"Wrote sample CSV to {csv_path}")
    print("ETL finished")

if __name__ == '__main__':
    main()
