try:
    from etl.extractors.wikipedia import extract_wikipedia_pages, extract_from_wikipedia_urls, extract_wwe_champions_page, enrich_wrestlers, enrich_events, run_and_save
except ImportError:
    from extractors.wikipedia import extract_wikipedia_pages, extract_from_wikipedia_urls, extract_wwe_champions_page, enrich_wrestlers, enrich_events, run_and_save

__all__ = [
    "extract_wikipedia_pages",
    "extract_from_wikipedia_urls",
    "extract_wwe_champions_page",
    "enrich_wrestlers",
    "enrich_events",
    "run_and_save",
]


if __name__ == '__main__':
    run_and_save()
