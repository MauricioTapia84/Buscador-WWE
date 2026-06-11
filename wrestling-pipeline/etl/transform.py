
import pandas as pd

def clean_wrestlers():

    df = pd.read_csv(
        "../data/raw/wrestlers_api.csv"
    )

    df["name"] = df["name"].str.strip()

    df = df.drop_duplicates()

    return df

def clean_champions():

    df = pd.read_csv(
        "../data/raw/champions.csv"
    )

    df["champion"] = df["champion"].str.strip()

    df = df.drop_duplicates()

    return df