import os
import pandas as pd
import logging
from etl.utils import configure_logging
from etl.validate import validate_and_report
from etl.extractors import read_kaggle_tables, extract_wrestlers_from_thesportsdb, extract_wikipedia_pages
from etl.transform import clean_wrestlers, clean_champions, normalize_wrestlers, normalize_matches


def main():
    configure_logging()
    logger = logging.getLogger("etl.run")
    logger.info("Starting one-shot ETL")

    out = os.getenv("ETL_OUTPUT", "data/processed")
    raw = os.getenv("DATA_RAW", "data/raw")
    os.makedirs(out, exist_ok=True)

    raw_wrestlers_path = os.path.join(raw, "wrestlers_api.csv")
    if os.path.exists(raw_wrestlers_path):
        logger.info("Loading wrestlers from raw CSV", extra={"path": raw_wrestlers_path})
        df = pd.read_csv(raw_wrestlers_path)
    else:
        kag = read_kaggle_tables(raw_folder=raw)
        if not kag.get("wrestlers", pd.DataFrame()).empty:
            df = kag["wrestlers"]
        else:
            sample = os.getenv("SAMPLE_NAMES", "Undertaker,Cena,Triple,Stone,Rock,Lesnar,Orton,Michaels").split(",")
            df = extract_wrestlers_from_thesportsdb([s.strip() for s in sample if s.strip()])

    if df is None or df.empty:
        logger.warning("No wrestlers extracted; creating empty frame")
        df = pd.DataFrame(columns=["id", "name"])
    else:
        df = clean_wrestlers(df)

    csv_path = os.path.join(out, "wrestlers_extracted.csv")
    df.to_csv(csv_path, index=False)
    logger.info("Wrote wrestlers CSV", extra={"path": csv_path})

    kag = read_kaggle_tables(raw_folder=raw)
    titles_df = kag.get("titles", pd.DataFrame())
    if titles_df.empty:
        titles_df = pd.DataFrame([
            {"title": "WWE Championship", "holder": "John Cena", "won_date": "2017-01-29", "reign_days": 14},
            {"title": "Universal Championship", "holder": "Roman Reigns", "won_date": "2020-08-30", "reign_days": 1316},
            {"title": "World Heavyweight Championship", "holder": "Triple H", "won_date": "2002-09-02", "reign_days": 280}
        ])
    else:
        titles_df = clean_champions(titles_df)

    titles_path = os.path.join(out, "titles_extracted.csv")
    titles_df.to_csv(titles_path, index=False)
    logger.info("Wrote titles CSV", extra={"path": titles_path})

    wiki_urls = os.getenv("WIKI_URLS", "").split(";") if os.getenv("WIKI_URLS") else []
    if wiki_urls:
        wiki_df = extract_wikipedia_pages(wiki_urls)
        wiki_path = os.path.join(out, "wikipedia_snippets.csv")
        wiki_df.to_csv(wiki_path, index=False)

    reports = validate_and_report(wrestlers_df=df, champions_df=titles_df, out_prefix=os.path.join(out, "validation_report"))
    logger.info("Validation reports written", extra={"reports": reports})

    try:
        normalize_wrestlers(processed_dir=out)
        normalize_matches(processed_dir=out, raw_dir=raw)
    except Exception:
        logger.exception("Normalization failed")

    logger.info("ETL finished")


if __name__ == '__main__':
    main()
