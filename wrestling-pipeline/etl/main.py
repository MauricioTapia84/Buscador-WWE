
from extract_thesportsdb import *
from extract_wikipedia import *
from extract_kaggle import *
from transform import *
from load import *

def run_pipeline():

    print("Extrayendo datos...")

    # Ejecutar extractores

    print("Transformando datos...")

    clean_wrestlers()

    clean_champions()

    print("Cargando datos...")

    print("ETL completado")

if __name__ == "__main__":
    run_pipeline()