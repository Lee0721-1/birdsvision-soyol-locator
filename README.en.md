# SOYOL Bird Locator

SOYOL means Student YOLO. It is an independent BirdsVision bird-localization project. The internal teacher model, TYLO (Teacher YOLO), is used to compare results and is not part of this project. The separate species classifier and its weights are not included.

The locator receives an image and returns its dimensions and bird boxes. It does not identify species. A separate classifier can call its loopback HTTP API. The locator does not load classifier code, labels, or weights. See the [BirdsVision website](https://www.birdsvision.com.cn/) for the app.

`birdsvision_locator/` contains the standalone FastAPI process. `soyol/` contains data export, training, validation, attribution, and private release-bundle tools. `SOYOL_MODEL_CARD.md` records the training evidence and unresolved publication conditions. Source code is [AGPL-3.0-only](LICENSE); training images retain their individual licenses.

This GitHub repository remains private. No weight has been published or uploaded from this directory. The iNaturalist platform inquiry is awaiting a human response, and the independent `final_test` has not been completed.

Run the locator in its own Python environment:

```bash
python -m pip install -r requirements-locator.txt
export BIRDSVISION_SOYOL_MODEL_PATH=/private/path/best.pt
uvicorn birdsvision_locator.app:app --host 127.0.0.1 --port 8001
```

`POST /v1/locate` accepts `application/octet-stream` image bytes and returns `width`, `height`, and `boxes`. Keep the port on loopback. For training and synthetic tests, install `requirements-training.txt` and `requirements-test.txt`, then run `python -m pytest -q`. Images, private selection records, production weights, and TYLO are outside this repository.
