# SPDX-FileCopyrightText: 2026 lee0G21
# SPDX-License-Identifier: AGPL-3.0-only
"""The public locator contract can be exercised without classifier modules."""

import ast
import io
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from PIL import Image

from birdsvision_locator import app as locator_app


def test_locator_has_no_classifier_imports():
    root = Path(__file__).resolve().parents[1]
    for package in ("birdsvision_locator", "soyol"):
        for path in (root / package).glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [item.name for item in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                assert not any(name == "convnext" or name.startswith("convnext.")
                               or name == "birdsvision_server"
                               or name.startswith("birdsvision_server.")
                               or name == "timm" or name.startswith("timm.")
                               for name in names), path
    assert not (root / "convnext").exists()
    assert not (root / "birdsvision_server").exists()


def test_locator_returns_boxes_without_classifier(monkeypatch):
    output = io.BytesIO()
    Image.new("RGB", (40, 20), "white").save(output, format="PNG")

    class FakeCoordinates:
        def detach(self):
            return self

        def cpu(self):
            return self

        def tolist(self):
            return [[2.0, 3.0, 30.0, 18.0]]

    predictions = [SimpleNamespace(boxes=SimpleNamespace(xyxy=FakeCoordinates()))]
    calls = []

    def predict(**kwargs):
        calls.append(kwargs)
        return predictions

    fake = SimpleNamespace(model=SimpleNamespace(end2end=False),
                           predict=predict)
    monkeypatch.setattr(locator_app, "init_model", lambda: None)
    monkeypatch.setattr(locator_app, "_model", fake)

    with TestClient(locator_app.app) as client:
        response = client.post("/v1/locate", content=output.getvalue(),
                               headers={"content-type": "application/octet-stream"})
    assert response.status_code == 200
    assert response.json() == {"width": 40, "height": 20,
                               "boxes": [[2.0, 3.0, 30.0, 18.0]]}
    assert {key: calls[0][key] for key in ("imgsz", "conf", "iou", "max_det")} == {
        "imgsz": 640, "conf": 0.25, "iou": 0.7, "max_det": 10,
    }


def test_locator_rejects_invalid_upload(monkeypatch):
    monkeypatch.setattr(locator_app, "init_model", lambda: None)
    monkeypatch.setattr(locator_app, "_model", object())
    with TestClient(locator_app.app) as client:
        response = client.post("/v1/locate", content=b"not an image",
                               headers={"content-type": "application/octet-stream"})
    assert response.status_code == 400
