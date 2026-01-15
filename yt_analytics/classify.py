def classify_hook(retention_score):
    """
    Classify hook strength based on retention score.
    """
    if retention_score >= 0.55:
        return "strong"
    elif retention_score >= 0.35:
        return "average"
    return "weak"
