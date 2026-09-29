def overlaps(a_start, a_end, b_start, b_end, duration):
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return (earliest_end - latest_start) >= duration
