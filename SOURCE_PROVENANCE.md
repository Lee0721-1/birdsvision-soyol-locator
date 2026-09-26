# Source provenance and project boundary

This directory was assembled on 2026-09-27 from two **private** BirdsVision work repositories. It is a new, locator-only source tree; it is not a copy of either mixed repository's Git history.

| Path in this project | Source repository | Source revision |
| --- | --- | --- |
| `soyol/`, `tests/soyol/`, `SOYOL_MODEL_CARD.md`, attribution table, `LICENSE`, and third-party notices | `birdsvision-model-training` | `74b8abb55a5742af5aae694f41c988bea292aa79` |
| `birdsvision_locator/` | `birdsvision-inference-server` | `fb789d316a17ef52a3039302fcbcb3903625f864` |
| `deployment/20260927/vendor_provenance.json`, `deployment/20260927/verify_vendor_record.py` | `birdsvision-inference-server` | `fb789d316a17ef52a3039302fcbcb3903625f864` |

The copied `birdsvision_locator/app.py` also matches the deployed locator file recorded at `birdsvision-inference-server/deployment/20260927/server/birdsvision_locator/app.py` in that private revision. That source snapshot is evidence about the locator process only; the API and classifier files in the same historical snapshot are outside this project.

The SOYOL project may release its locator code, training code, model material, and corresponding deployment instructions as one fixed AGPL revision once its publication checks are complete. The independent classifier project retains its API, class table, training and inference code, and production weights privately. The only runtime connection is the locator's image-to-box HTTP contract. No classifier file was copied into this directory.

This file records source origin and the intended release contents. It does not replace a publication of the exact running version, does not grant image rights, and does not constitute a license interpretation from Ultralytics.
