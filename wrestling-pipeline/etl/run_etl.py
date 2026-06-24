import os
import pandas as pd
import logging
try:
    from utils.logging_config import configure_logging
    from validate import validate_and_report
    from extract_thesportsdb import extract_all as extract_thesportsdb
    from extract_wikipedia import extract_from_wikipedia_urls, enrich_wrestlers_from_titles
    from extract_kaggle import read_kaggle_tables
except ImportError:
    from etl.utils.logging_config import configure_logging
    from etl.validate import validate_and_report
    from etl.extract_thesportsdb import extract_all as extract_thesportsdb
    from etl.extract_wikipedia import extract_from_wikipedia_urls, enrich_wrestlers_from_titles
    from etl.extract_kaggle import read_kaggle_tables


def _seed_wrestler_names(raw_dir: str) -> list[str]:
    seeded = []

    champions_path = os.path.join(raw_dir, "wwe_champions_initial.csv")
    if os.path.exists(champions_path):
        try:
            champions = pd.read_csv(champions_path)
            seeded.extend(champions.get("champion", pd.Series(dtype="object")).dropna().astype(str).tolist())
        except Exception:
            pass

    defaults = [
        "The Undertaker",
        "John Cena",
        "Triple H",
        "The Rock",
        "Brock Lesnar",
        "Randy Orton",
        "Shawn Michaels",
        "Roman Reigns",
        "Seth Rollins",
        "Cody Rhodes",
        "Hulk Hogan",
        "The Iron Sheik",
        "Bob Backlund",
        "Andre the Giant",
        "Randy Savage",
    ]
    seeded.extend(defaults)

    cleaned = []
    seen = set()
    for name in seeded:
        text = str(name).replace('"', "").strip()
        if not text:
            continue
        if text.lower() in seen:
            continue
        seen.add(text.lower())
        cleaned.append(text)
    return cleaned


def main():
    configure_logging()
    logger = logging.getLogger("etl.run")
    logger.info("Starting one-shot ETL")

    out = os.getenv("ETL_OUTPUT", "data/processed")
    raw = os.getenv("DATA_RAW", "data/raw")
    os.makedirs(out, exist_ok=True)

    # Prefer existing raw CSV if provided
    raw_wrestlers_path = os.path.join(raw, "wrestlers_api.csv")
    if os.path.exists(raw_wrestlers_path):
        logger.info("Loading wrestlers from raw CSV", extra={"path": raw_wrestlers_path})
        source_df = pd.read_csv(raw_wrestlers_path)
    else:
        # Try to load from Kaggle raw files
        kag = read_kaggle_tables(raw_folder=raw)
        if not kag.get("wrestlers", pd.DataFrame()).empty:
            source_df = kag["wrestlers"]
        else:
            # Fallback: call TheSportsDB using real WWE names from title history + curated defaults.
            env_sample = [s.strip() for s in os.getenv("SAMPLE_NAMES", "").split(",") if s.strip()]
            sample = env_sample or _seed_wrestler_names(raw)
            source_df = extract_thesportsdb(sample)
            if not source_df.empty:
                rich_path = os.path.join(out, "wrestlers_thesportsdb.csv")
                source_df.to_csv(rich_path, index=False)
                logger.info("Wrote rich TheSportsDB wrestlers CSV", extra={"path": rich_path, "rows": len(source_df)})

    # Ensure dataframe
    if source_df is None or source_df.empty:
        logger.warning("No wrestlers extracted; creating empty frame")
        df = pd.DataFrame(columns=["id", "name"])
    else:
        try:
            from transform.clean import clean_wrestlers
        except ImportError:
            from etl.transform import clean_wrestlers
        df = clean_wrestlers(source_df)

        target_file = os.path.join(os.path.dirname(__file__), "target_wrestlers.txt")
        if os.path.exists(target_file):
            with open(target_file, "r", encoding="utf-8") as f:
                targets = [line.strip().lower() for line in f if line.strip()]
            if targets:
                def _slugify(val):
                    import re, unicodedata
                    if not val: return ""
                    t = str(val).strip()
                    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii").lower()
                    return re.sub(r"[^a-z0-9]+", " ", t).strip()
                
                target_slugs = set(_slugify(t) for t in targets if _slugify(t))
                
                def is_target(name):
                    return _slugify(name) in target_slugs

                df = df[df["name"].apply(is_target)].copy()
                logger.info("Filtered wrestlers against target list", extra={"retained": len(df)})


    csv_path = os.path.join(out, "wrestlers_extracted.csv")
    df.to_csv(csv_path, index=False)
    logger.info("Wrote wrestlers CSV", extra={"path": csv_path})

    # Titles should prefer real source data. Use Kaggle titles first, then the
    # curated raw champion history shipped with the repository.
    kag = read_kaggle_tables(raw_folder=raw)
    titles_df = kag.get("titles", pd.DataFrame())
    if titles_df.empty:
        champions_path = os.path.join(raw, "wwe_champions_initial.csv")
        if os.path.exists(champions_path):
            titles_df = pd.read_csv(champions_path).rename(
                columns={
                    "champion": "holder",
                    "date_won": "won_date",
                    "event": "event_name",
                    "days_held": "reign_days",
                }
            )
            titles_df["title"] = "WWE Championship"
        else:
            titles_df = pd.DataFrame(columns=["title", "holder", "won_date", "reign_days", "event_name"])
    else:
        try:
            from transform.clean import clean_champions
        except ImportError:
            from etl.transform import clean_champions
        titles_df = clean_champions(titles_df)

        if os.path.exists(target_file) and targets:
            def _slugify(val):
                import re, unicodedata
                if not val: return ""
                t = str(val).strip()
                t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii").lower()
                return re.sub(r"[^a-z0-9]+", " ", t).strip()
            
            target_slugs = set(_slugify(t) for t in targets if _slugify(t))
            
            def is_target(name):
                return _slugify(name) in target_slugs

            titles_df = titles_df[titles_df["holder"].apply(is_target)].copy()
            logger.info("Filtered titles against target list", extra={"retained": len(titles_df)})

    titles_path = os.path.join(out, "titles_extracted.csv")
    titles_df.to_csv(titles_path, index=False)
    logger.info("Wrote titles CSV", extra={"path": titles_path})

    # Enrich wrestler profiles from Wikipedia summaries + infobox scraping.
    wiki_enabled = os.getenv("ENABLE_WIKIPEDIA_ENRICHMENT", "1").strip().lower() not in {"0", "false", "no"}
    if wiki_enabled:
        try:
            wikipedia_names = []
            seen = set()
            for source_name in list(df.get("name", pd.Series(dtype="object")).dropna().astype(str)) + list(
                titles_df.get("holder", pd.Series(dtype="object")).dropna().astype(str)
            ):
                candidate = str(source_name).strip()
                if not candidate:
                    continue
                lowered = candidate.lower()
                if lowered in seen:
                    continue
                seen.add(lowered)
                wikipedia_names.append(candidate)

            if wikipedia_names:
                logger.info("Starting Wikipedia wrestler enrichment", extra={"names": len(wikipedia_names)})
                wiki_df = enrich_wrestlers_from_titles(wikipedia_names)
                if not wiki_df.empty:
                    wiki_path = os.path.join(out, "wrestlers_enriched.csv")
                    wiki_df.to_csv(wiki_path, index=False)
                    logger.info("Wrote Wikipedia wrestler enrichment", extra={"path": wiki_path, "rows": len(wiki_df)})
                else:
                    logger.warning("Wikipedia wrestler enrichment returned no rows", extra={"names": len(wikipedia_names)})
            else:
                logger.warning("Wikipedia wrestler enrichment skipped because no wrestler names were collected")
        except Exception:
            logger.exception("Wikipedia enrichment failed")

    # Optionally extract wikipedia snippets if provided via env
    wiki_urls = os.getenv("WIKI_URLS", "").split(";") if os.getenv("WIKI_URLS") else []
    if wiki_urls:
        wiki_df = extract_from_wikipedia_urls(wiki_urls)
        wiki_path = os.path.join(out, "wikipedia_snippets.csv")
        wiki_df.to_csv(wiki_path, index=False)

    # run validations and emit reports next to output
    reports = validate_and_report(wrestlers_df=df, champions_df=titles_df, out_prefix=os.path.join(out, "validation_report"))
    logger.info("Validation reports written", extra={"reports": reports})
    # run normalization to produce final processed CSVs/parquets
    try:
        try:
            from transform.normalize import normalize_wrestlers, normalize_matches, normalize_titles
        except ImportError:
            from etl.transform.normalize import normalize_wrestlers, normalize_matches, normalize_titles
        normalize_wrestlers(processed_dir=out)
        normalize_matches(processed_dir=out, raw_dir=raw)
        normalize_titles(processed_dir=out, raw_dir=raw)
    except Exception:
        logger.exception("Normalization failed")

    logger.info("ETL finished")


if __name__ == '__main__':
    main()
