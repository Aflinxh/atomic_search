def app_value():
    return {
        "getElementById": {
            "molecule_similarity": "-2"
        },
        "querySelector": {
            "molecule_similarity": "-2"
        },
        "addEventListener": {
            "molecule_similarity": "-2"
        },
        "setTimeout": {
            "molecule_similarity": "-2"
        },
        "localStorage": {
            "molecule_similarity": "-2"
        },
        "innerHTML": {
            "molecule_similarity": "-2"
        },
        "console": {
            "molecule_similarity": "100%"
        },
        "eval": {
            "molecule_similarity": "100%"
        }
    }

target_words = list(app_value().keys())
molecule_similarity = {key: value["molecule_similarity"] for key, value in app_value().items()}