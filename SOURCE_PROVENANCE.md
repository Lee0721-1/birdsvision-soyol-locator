# Source provenance and project boundary

This directory was assembled on 2026-09-27 from two **private** BirdsVision work repositories. It is a new, locator-only source tree; it is not a copy of either mixed repository's Git history.

| Path in this project | Source repository | Source revision |
| --- | --- | --- |
| `soyol/`, `tests/soyol/`, `SOYOL_MODEL_CARD.md`, attribution table, `LICENSE`, and third-party notices | `birdsvision-model-training` | `74b8abb55a5742af5aae694f41c988bea292aa79` |
| `birdsvision_locator/` | `birdsvision-inference-server` | `fb789d316a17ef52a3039302fcbcb3903625f864` |
| `deployment/20260927/vendor_provenance.json`, `deployment/20260927/verify_vendor_record.py` | `birdsvision-inference-server` | `fb789d316a17ef52a3039302fcbcb3903625f864` |

The copied `birdsvision_locator/app.py` also matches the deployed locator file recorded at `birdsvision-inference-server/deployment/20260927/server/birdsvision_locator/app.py` in that revision. That source snapshot is evidence about the locator process only; the API and classifier files in the same historical snapshot are outside this project.

The documented 1,316-photo training run recorded `birdsvision-model-training` commit `b77936170cdaf9520498bdf65ecd5953853d6c11` as its training-time source. The four recorded training and validation source files match the corresponding files in this locator-only tree byte for byte. The release manifest records both that training-time revision and the fixed revision of this repository.

The SOYOL project provides its locator code, training code, model material, and corresponding deployment instructions as one fixed AGPL revision. The independent classifier project's API, training, and inference source are public in separate repositories; its production weights, class table, and data remain private. The only runtime connection is the locator's image-to-box HTTP contract. No classifier file was copied into this directory.

This file records source origin and release contents. It does not grant image rights or constitute a license interpretation from Ultralytics.
