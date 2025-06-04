def debounce_tag(previous_tag, current_tag, count, threshold=3):
    """
    Returns confirmed tag if current tag appears 'threshold' times in a row.
    """
    if previous_tag == current_tag:
        count += 1
    else:
        count = 1
    if count >= threshold:
        return current_tag, count, True
    return current_tag, count, False
