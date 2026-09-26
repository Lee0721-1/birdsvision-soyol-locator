# SPDX-FileCopyrightText: 2026 lee0G21
# SPDX-License-Identifier: AGPL-3.0-only
import csv
import json

import pytest

from soyol import soyol_release_bundle as release


def evidence(tmp_path, monkeypatch):
    weight = tmp_path / "best.pt"
    weight.write_bytes(b"synthetic-weight")
    attribution = tmp_path / "attribution.csv"
    with attribution.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(release.EXPECTED_ATTRIBUTION_FIELDS))
        writer.writeheader()
        writer.writerow({
            "record_id": "inaturalist:1", "photo_id": "1", "observation_id": "2",
            "source_page_url": "https://www.inaturalist.org/observations/2",
            "source_image_sha256": "a" * 64, "license_code": "cc-by",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "license_url_basis": "current_site_code_mapping_not_historical_photo_page_capture",
            "attribution": "Example", "changes": "Bird detection annotation",
            "publication_review": "platform_terms_reply_pending",
            "metadata_checked_at_utc": "2026-09-24T00:00:00+00:00",
        })
    monkeypatch.setattr(release, "TRAINING_ATTRIBUTION", attribution)
    recheck = tmp_path / "recheck.jsonl"
    recheck.write_text(json.dumps({
        "record_id": "inaturalist:1", "photo_found": True,
        "license_code_matches": True, "current_photo_license_code": "cc-by",
        "current_photo_attribution": "Example",
        "metadata_checked_at_utc": "2026-09-27T00:00:00+00:00",
    }) + "\n", encoding="utf-8")
    counts = {
        "train_parents": 1, "train_boxes": 1, "train_no_bird": 0,
        "validation_parents": 0, "validation_boxes": 0,
        "validation_no_bird": 0,
    }
    metrics = {"mAP50": 0.5, "mAP50_95": 0.25,
               "precision": 0.4, "recall": 0.6}
    validation = tmp_path / "validation.json"
    validation.write_text(json.dumps({
        "format": "birdsvision-soyol-a-nms-validation-v1",
        "dataset_verification": {"status": "verified", "counts": counts},
        "postprocess": "one_to_many_branch_then_nms", "max_det": 10,
        "results": {name: metrics | {"weight_path": "D:\\private\\best.pt"}
                    for name in ("best", "last")},
        "selected_checkpoint": "best", "final_test_read_or_written": False,
    }), encoding="utf-8")
    record = tmp_path / "record.json"
    record.write_text(json.dumps({
        "format": "birdsvision-soyol-documented-train-validation-record-v1",
        "status": "training_and_validation_completed_publication_pending",
        "selected_checkpoint": "best.pt", "final_test_read_or_written": False,
        "weight_sha256": {"best.pt": release.digest(weight)},
        "attribution_sha256": release.digest(attribution),
        "validation_report_sha256": release.digest(validation),
        "validation_split": counts,
        "nms_validation_metrics": {"best": metrics, "last": metrics},
        "selection_sha256": "b" * 64,
        "training_contract_sha256": "c" * 64,
        "source_repo_commit_at_training": "e" * 40,
        "source_file_sha256": {
            name: release.digest(release.REPO_ROOT / "soyol" / name)
            for name in release.TRAINING_SOURCE_FILES
        },
        "platform_terms_reply_pending": True,
    }), encoding="utf-8")
    return record, weight, attribution, validation, recheck


def test_private_bundle_binds_inputs_and_removes_local_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(release, "checked_source_commit", lambda: "d" * 40)
    output = tmp_path / "bundle"
    manifest = release.build_bundle(*evidence(tmp_path, monkeypatch), output)
    assert release.verify_bundle(output) == manifest
    assert manifest["source_repository"] == "https://github.com/Lee0721-1/birdsvision-soyol-locator"
    assert manifest["attribution_rows"] == 1
    assert manifest["final_test_completed"] is False
    assert manifest["training_source_commit"] == "e" * 40
    assert manifest["weight_release_license"] == "AGPL-3.0-only"
    assert manifest["attribution_changed_since_training"] == 0
    assert (output / "SOURCE_PROVENANCE.md").is_file()
    assert "weight_path" not in (output / "VALIDATION.json").read_text(encoding="utf-8")
    assert "D:\\private" not in (output / "VALIDATION.json").read_text(encoding="utf-8")
    (output / "extra.jpg").write_bytes(b"unexpected image")
    with pytest.raises(ValueError, match="missing or extra"):
        release.verify_bundle(output)
    (output / "extra.jpg").unlink()
    (output / "best.pt").write_bytes(b"altered")
    with pytest.raises(ValueError, match="release file changed"):
        release.verify_bundle(output)


def test_private_bundle_rejects_mismatched_weight(tmp_path, monkeypatch):
    inputs = evidence(tmp_path, monkeypatch)
    inputs[1].write_bytes(b"different")
    with pytest.raises(ValueError, match="selected weight"):
        release.build_bundle(*inputs, tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()


def test_private_bundle_rejects_changed_training_source_record(tmp_path, monkeypatch):
    inputs = evidence(tmp_path, monkeypatch)
    record = json.loads(inputs[0].read_text(encoding="utf-8"))
    record["source_file_sha256"]["soyol_train.py"] = "0" * 64
    inputs[0].write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="training source file changed"):
        release.build_bundle(*inputs, tmp_path / "bundle")


def test_private_bundle_accepts_only_rechecked_attribution_change(tmp_path, monkeypatch):
    monkeypatch.setattr(release, "checked_source_commit", lambda: "d" * 40)
    inputs = list(evidence(tmp_path, monkeypatch))
    publication = tmp_path / "publication.csv"
    rows = release.read_attribution(inputs[2])
    rows[0]["attribution"] = "Updated credit"
    rows[0]["metadata_checked_at_utc"] = "2026-09-27T00:00:00+00:00"
    with publication.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    inputs[2] = publication
    recheck = json.loads(inputs[4].read_text(encoding="utf-8"))
    recheck["current_photo_attribution"] = "Updated credit"
    inputs[4].write_text(json.dumps(recheck) + "\n", encoding="utf-8")
    manifest = release.build_bundle(*inputs, tmp_path / "bundle")
    assert manifest["attribution_changed_since_training"] == 1
    assert json.loads((tmp_path / "bundle" / "ATTRIBUTION_RECHECK.json").read_text(
        encoding="utf-8"))["attribution_changes_since_training"][0]["current"] == "Updated credit"
    rows[0]["license_code"] = "cc0"
    with publication.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="metadata changed|training field"):
        release.validate_inputs(*inputs)
