VALIDATION_RULES = {
    "quantity": {
        "min": 1,
    },
    "revenue": {
        "min": 0,
    },
    "region": {
        "allowed": [
            "North",
            "South",
            "East",
            "West",
        ],
    },
}