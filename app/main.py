import json
from typing import MutableMapping

import uvicorn
import yaml
from fastapi import FastAPI, Query, HTTPException
from sdc.crypto.jwe_helper import JWEHelper
from sdc.crypto.key_store import KeyStore

KEY_PURPOSE_SDS = "supplementary_data"

app = FastAPI()

with open("dev-keys.yml", encoding="UTF-8") as keys_file:
    keys = KeyStore(yaml.safe_load(keys_file))


@app.get("/v1/unit_data")
def get_sds_data(dataset_id: str = Query()) -> MutableMapping:
    dataset_id_to_mock_data = {
        "c067f6de-6d64-42b1-8b02-431a3486c178": "mock_data/supplementary_data_no_repeat.json",
        "34a80231-c49a-44d0-91a6-8fe1fb190e64": "mock_data/supplementary_data_with_repeat.json",
        "6b378962-f0c7-4e8c-947e-7d24ee1b6b88": "mock_data/supplementary_data_with_repeat_v2.json",
    }

    if mock_data := dataset_id_to_mock_data.get(dataset_id):
        return encrypt_mock_data(load_mock_data(mock_data))

    raise HTTPException(status_code=404)


@app.get("/v1/dataset_metadata")
def get_sds_dataset_ids(survey_id: str = Query()) -> dict:
    return load_mock_sds_dataset_metadata(survey_id)


def load_mock_data(filename: str) -> dict:
    with open(filename, encoding="utf-8") as mock_data_file:
        return json.load(mock_data_file)


def load_mock_sds_dataset_metadata(survey_id: str) -> dict:
    if survey_id == "123":
        return load_mock_data("mock_data/supplementary_dataset_metadata_response.json")

    raise HTTPException(status_code=404)


def encrypt_mock_data(mock_data: MutableMapping) -> MutableMapping:
    key = keys.get_key(purpose=KEY_PURPOSE_SDS, key_type="private")
    mock_data["data"] = JWEHelper.encrypt_with_key(
        json.dumps(mock_data["data"]), key.kid, key.as_jwk()
    )
    return mock_data


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5003)
