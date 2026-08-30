import json
from pathlib import Path


from schemas import Candidate


def load_candidate():
    file_path=Path(__file__).parent / "data" / "candidate.json"

    with open(file_path, "r", encoding="utf-8") as file:
        data=json.load(file)

    return Candidate.model_validate(data)