try:
    from etl.extractors.wikipedia import (
        enrich_events,
        enrich_wrestlers,
        enrich_wrestlers_from_titles,
        extract_from_wikipedia_urls,
        extract_wikipedia_pages,
        extract_wwe_champions_page,
        run_and_save,
    )
except ImportError:
    from extractors.wikipedia import (
        enrich_events,
        enrich_wrestlers,
        enrich_wrestlers_from_titles,
        extract_from_wikipedia_urls,
        extract_wikipedia_pages,
        extract_wwe_champions_page,
        run_and_save,
    )

__all__ = [
    "extract_wikipedia_pages",
    "extract_from_wikipedia_urls",
    "extract_wwe_champions_page",
    "enrich_wrestlers",
    "enrich_wrestlers_from_titles",
    "enrich_events",
    "run_and_save",
]


if __name__ == '__main__':
    run_and_save()
