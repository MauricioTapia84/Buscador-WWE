from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_entities(master_list: list, candidate_list: list, threshold: float = 0.8) -> list:
    """Attempt to reconcile candidate_list against master_list by name similarity.
    Returns list of tuples (candidate, best_match_or_None, score)."""
    out = []
    for c in candidate_list:
        best = None
        best_score = 0.0
        cn = c.get("name") if isinstance(c, dict) else str(c)
        for m in master_list:
            mn = m.get("name") if isinstance(m, dict) else str(m)
            s = similarity(cn, mn)
            if s > best_score:
                best = m
                best_score = s
        out.append((c, best if best_score >= threshold else None, best_score))
    return out
