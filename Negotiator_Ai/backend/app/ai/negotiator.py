def negotiate(user_a, user_b, duration):
    for a in user_a["availability"]:
        for b in user_b["availability"]:
            if a["day"] == b["day"]:
                start = max(a["start"], b["start"])
                end = min(a["end"], b["end"])
                if end - start >= duration:
                    return {
                        "status": "CONFIRMED",
                        "day": a["day"],
                        "start": start,
                        "end": start + duration
                    }
    return {"status": "NO_OVERLAP"}
