# SOYOL Bird Locator

SOYOL means Student YOLO. It is an independent BirdsVision bird-localization project. The internal teacher model, TYLO (Teacher YOLO), is used to compare results and is not part of this project. The separate species classifier and its weights are not included.

The locator receives an image and returns its dimensions and bird boxes. It does not identify species. A separate classifier can call its loopback HTTP API. The locator does not load classifier code, labels, or weights. See the [BirdsVision website](https://www.birdsvision.com.cn/) for the app.

`birdsvision_locator/` contains the standalone FastAPI process. `soyol/` contains data export, training, validation, attribution, and release-bundle tools. `SOYOL_MODEL_CARD.md` records the training evidence and unresolved platform inquiry. Source code and the SOYOL `best.pt` weight are AGPL-3.0-only; the weight is distributed as a separate GitHub Release asset. Training images retain their individual licenses.

`soyol/ATTRIBUTION_TRAINING_20260926.csv` preserves the attribution table bound to the training record. `soyol/ATTRIBUTION_A_DOCUMENTED_20260926.csv` is the updated table intended for publication. The staging bundle verifies it against a fresh per-photo metadata check supplied through `--recheck`.

The separate [classifier API](https://github.com/Lee0721-1/birdsvision-inference-server) and [classifier training code](https://github.com/Lee0721-1/birdsvision-model-training) are public. Classifier weights, production labels, training images, and TYLO are excluded. The iNaturalist platform inquiry is awaiting a human response, and the independent `final_test` has not been completed.

Run the locator in its own Python environment:

```bash
python -m pip install -r requirements-locator.txt
export BIRDSVISION_SOYOL_MODEL_PATH=/private/path/best.pt
uvicorn birdsvision_locator.app:app --host 127.0.0.1 --port 8001
```

`POST /v1/locate` accepts `application/octet-stream` image bytes and returns `width`, `height`, and `boxes`. Keep the port on loopback. For training and synthetic tests, install `requirements-training.txt` and `requirements-test.txt`, then run `python -m pytest -q`. Images, private selection records, production weights, and TYLO are outside this repository.
