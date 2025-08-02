def merge_results(*results):
    merged = []
    for res in results:
        if isinstance(res, list):
            merged.extend(res)
    return merged