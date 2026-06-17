import os
import pandas as pd
import logging
from logging_config import configure_logging
from validate import validate_and_report


def main():
    configure_logging()
    logger = logging.getLogger("etl.run")
    logger.info("Starting one-shot ETL")
    df = pd.DataFrame({"id": [1, 2], "name": ["John Example", "Jane Demo"]})
    out = os.getenv("ETL_OUTPUT", "/app/output")
    os.makedirs(out, exist_ok=True)
    csv_path = os.path.join(out, "wrestlers_extracted.csv")
    df.to_csv(csv_path, index=False)
    logger.info("Wrote sample CSV", extra={"path": csv_path})
    # run validations and emit reports next to output
    reports = validate_and_report(wrestlers_df=df, out_prefix=os.path.join(out, "validation_report"))
    logger.info("Validation reports written", extra={"reports": reports})
    logger.info("ETL finished")


if __name__ == '__main__':
    main()
