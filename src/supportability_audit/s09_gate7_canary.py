def legacy_gap(value: int) -> int:
    """Retained canary debt used only by the disposable Gate 8 qualification."""
    score = 0
    if value > 0:
        score += 1
    if value > 1:
        score += 1
    if value > 2:
        score += 1
    if value > 3:
        score += 1
    if value > 4:
        score += 1
    if value > 5:
        score += 1
    if value > 6:
        score += 1
    if value > 7:
        score += 1
    if value > 8:
        score += 1
    if value > 9:
        score += 1
    if value > 10:
        score += 1
    if value > 11:
        score += 1
    if value > 12:
        score += 1
    return score


S09_GATE7_CANARY = "s09-gate7-quality"
