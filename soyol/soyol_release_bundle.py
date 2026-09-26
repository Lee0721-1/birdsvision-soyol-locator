# SPDX-FileCopyrightText: 2026 lee0G21
# SPDX-License-Identifier: AGPL-3.0-only
"""Build a SOYOL release bundle from verified local evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REPOSITORY_URL = "https://github.com/Lee0721-1/birdsvision-soyol-locator"
TRAINING_SOURCE_REPOSITORY_URL = "https://github.com/Lee0721-1/birdsvision-model-training"
WEIGHT_RELEASE_LICENSE = "AGPL-3.0-only"
TRAINING_SOURCE_FILES = {
    "soyol_dataset.py", "soyol_output_policy.py", "soyol_train.py", "soyol_validate.py",
}
TRAINING_ATTRIBUTION = REPO_ROOT / "soyol" / "ATTRIBUTION_TRAINING_20260926.csv"
COPIED_REPO_FILES = {
    "MODEL_CARD.md": "SOYOL_MODEL_CARD.md",
    "SOURCE_PROVENANCE.md": "SOURCE_PROVENANCE.md",
    "LICENSE": "LICENSE",
    "THIRD_PARTY_NOTICES.md": "THIRD_PARTY_NOTICES.md",
}
EXPECTED_ATTRIBUTION_FIELDS = {
    "record_id", "photo_id", "observation_id", "source_page_url",
    "source_image_sha256", "license_code", "license_url",
    "license_url_basis", "attribution", "changes",
    "publication_review", "metadata_checked_at_utc",
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_attribution(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or ()) != EXPECTED_ATTRIBUTION_FIELDS:
            raise ValueError("attribution columns do not match the reviewed schema")
        return list(reader)


def checked_source_commit() -> str:
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=REPO_ROOT, check=True, capture_output=True, text=True,
    ).stdout
    if status.strip():
        raise ValueError("source repository must be clean before staging")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError("invalid source repository commit")
    return commit


def validate_inputs(record_path: Path, weight_path: Path, attribution_path: Path,
                    validation_path: Path, recheck_path: Path) -> tuple[dict, dict, int, dict]:
    record = read_json(record_path)
    validation = read_json(validation_path)
    if (record["format"] != "birdsvision-soyol-documented-train-validation-record-v1"
            or record["status"] != "training_and_validation_completed_publication_pending"
            or record["selected_checkpoint"] != "best.pt"
            or record["final_test_read_or_written"] is not False):
        raise ValueError("training record does not describe the selected private release")
    if digest(weight_path) != record["weight_sha256"]["best.pt"]:
        raise ValueError("selected weight does not match the training record")
    if digest(TRAINING_ATTRIBUTION) != record["attribution_sha256"]:
        raise ValueError("training attribution does not match the training record")
    if digest(validation_path) != record["validation_report_sha256"]:
        raise ValueError("validation report does not match the training record")
    if re.fullmatch(r"[0-9a-f]{40}", record["source_repo_commit_at_training"]) is None:
        raise ValueError("invalid training source commit")
    if set(record["source_file_sha256"]) != TRAINING_SOURCE_FILES:
        raise ValueError("training source file list changed")
    for name, expected_digest in record["source_file_sha256"].items():
        if digest(REPO_ROOT / "soyol" / name) != expected_digest:
            raise ValueError(f"training source file changed: {name}")
    if (validation["format"] != "birdsvision-soyol-a-nms-validation-v1"
            or validation["postprocess"] != "one_to_many_branch_then_nms"
            or validation["max_det"] != 10
            or validation["selected_checkpoint"] != "best"
            or validation["final_test_read_or_written"] is not False
            or validation["dataset_verification"]["status"] != "verified"
            or validation["dataset_verification"]["counts"] != record["validation_split"]):
        raise ValueError("validation report contradicts the training record")
    for name in ("best", "last"):
        metrics = {key: value for key, value in validation["results"][name].items()
                   if key != "weight_path"}
        if metrics != record["nms_validation_metrics"][name]:
            raise ValueError(f"{name} metrics contradict the training record")
    recorded_rows = read_attribution(TRAINING_ATTRIBUTION)
    rows = read_attribution(attribution_path)
    expected_rows = (record["validation_split"]["train_parents"]
                     + record["validation_split"]["validation_parents"])
    if (len(rows) != expected_rows or len(recorded_rows) != expected_rows
            or len({row["record_id"] for row in rows}) != len(rows)
            or [row["record_id"] for row in rows]
            != [row["record_id"] for row in recorded_rows]):
        raise ValueError("attribution count or record IDs are inconsistent")
    if any(row["license_code"] not in {"cc-by", "cc0"}
           or not row["attribution"] or not row["source_page_url"].startswith(
               "https://www.inaturalist.org/observations/"
           ) or row["publication_review"] != "platform_terms_reply_pending"
           for row in rows):
        raise ValueError("attribution contains an unreviewed source or license")
    rechecked = {}
    with recheck_path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                item = json.loads(line)
                if item["record_id"] in rechecked:
                    raise ValueError("duplicate photo in metadata recheck")
                rechecked[item["record_id"]] = item
    changed = []
    checked_at = set()
    for row, old in zip(rows, recorded_rows):
        rid = row["record_id"]
        meta = rechecked.get(rid)
        if (meta is None or meta["photo_found"] is not True
                or meta["license_code_matches"] is not True
                or meta["current_photo_license_code"] != row["license_code"]
                or meta["current_photo_attribution"] != row["attribution"]):
            raise ValueError(f"selected photo metadata changed or is missing: {rid}")
        checked_at.add(meta["metadata_checked_at_utc"])
        for field in EXPECTED_ATTRIBUTION_FIELDS - {
                "attribution", "metadata_checked_at_utc"}:
            if row[field] != old[field]:
                raise ValueError(f"publication attribution changed training field: {rid} {field}")
        if row["attribution"] != old["attribution"]:
            if row["metadata_checked_at_utc"] != meta["metadata_checked_at_utc"]:
                raise ValueError(f"attribution change lacks current check time: {rid}")
            changed.append({"record_id": rid, "previous": old["attribution"],
                            "current": row["attribution"]})
        elif row["metadata_checked_at_utc"] != old["metadata_checked_at_utc"]:
            raise ValueError(f"unchanged attribution has modified check time: {rid}")
    if len(checked_at) != 1:
        raise ValueError("metadata recheck times are inconsistent")
    recheck = {
        "selected_photos_verified": len(rows),
        "checked_at_utc": checked_at.pop(),
        "source_records_sha256": digest(recheck_path),
        "attribution_changes_since_training": changed,
    }
    return record, validation, len(rows), recheck


def build_bundle(record_path: Path, weight_path: Path, attribution_path: Path,
                 validation_path: Path, recheck_path: Path, output: Path,
                 distribution: bool = False) -> dict:
    record, validation, attribution_count, recheck = validate_inputs(
        record_path, weight_path, attribution_path, validation_path, recheck_path
    )
    output = output.resolve()
    if output == REPO_ROOT or REPO_ROOT in output.parents:
        raise ValueError("weight bundle must stay outside the Git repository")
    if output.exists():
        raise FileExistsError(output)
    source_commit = checked_source_commit()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="soyol-release-", dir=output.parent) as temp:
        bundle = Path(temp)
        shutil.copyfile(weight_path, bundle / "best.pt")
        shutil.copyfile(attribution_path, bundle / "ATTRIBUTION.csv")
        for destination, source in COPIED_REPO_FILES.items():
            shutil.copyfile(REPO_ROOT / source, bundle / destination)
        public_validation = {
            key: value for key, value in validation.items() if key != "results"
        }
        public_validation["results"] = {
            name: {key: value for key, value in result.items()
                   if key != "weight_path"}
            for name, result in validation["results"].items()
        }
        (bundle / "VALIDATION.json").write_text(
            json.dumps(public_validation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (bundle / "ATTRIBUTION_RECHECK.json").write_text(
            json.dumps(recheck, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        shared_readme = (
            "其中不包含原图、裁剪图、分类器权重或私有数据清单。\n\n"
            "`best.pt` 是可考证 A 层训练权重；逐图署名见 `ATTRIBUTION.csv`。"
            "训练时署名与本次发布署名的差异见 `ATTRIBUTION_RECHECK.json`。"
            "验证结果见 `VALIDATION.json`，没有独立 final_test。"
            "第三方训练图片保留各自许可，AGPL-3.0-only 不重新许可这些图片。"
            "iNaturalist 平台条款询问仍未收到人工答复。\n\n"
            f"当前独立源码提交：{source_commit}\n"
            f"训练时源码提交：{record['source_repo_commit_at_training']}\n"
        )
        if distribution:
            readme = (
                "# SOYOL v1 公开分发包\n\n"
                "`best.pt` 与对应 SOYOL 源码按 AGPL-3.0-only 提供。"
                "此包已核对文件完整性，但打包本身不代表 GitHub 发布成功。"
                + shared_readme
            )
        else:
            readme = (
                "# SOYOL 私密预发布包\n\n"
                "此包用于核对发布材料，尚未获准公开或上传。"
                "计划公开时，`best.pt` 与对应源码按 AGPL-3.0-only 提供。"
                + shared_readme
            )
        (bundle / "README.md").write_text(readme, encoding="utf-8")
        filenames = ("best.pt", "ATTRIBUTION.csv", "ATTRIBUTION_RECHECK.json", "MODEL_CARD.md",
                     "SOURCE_PROVENANCE.md", "LICENSE",
                     "THIRD_PARTY_NOTICES.md", "VALIDATION.json", "README.md")
        manifest = {
            "format": ("birdsvision-soyol-distribution-bundle-v1" if distribution
                       else "birdsvision-soyol-private-release-bundle-v1"),
            "status": ("prepared_for_public_distribution" if distribution
                       else "private_staging_not_publication_clearance"),
            "source_repository": SOURCE_REPOSITORY_URL,
            "source_commit": source_commit,
            "training_source_repository": TRAINING_SOURCE_REPOSITORY_URL,
            "training_source_commit": record["source_repo_commit_at_training"],
            "weight_release_license": WEIGHT_RELEASE_LICENSE,
            "training_selection_sha256": record["selection_sha256"],
            "training_contract_sha256": record["training_contract_sha256"],
            "attribution_rows": attribution_count,
            "attribution_changed_since_training": len(recheck["attribution_changes_since_training"]),
            "checkpoint": "best.pt",
            "final_test_completed": False,
            "platform_terms_reply_pending": record["platform_terms_reply_pending"],
            "files": {name: digest(bundle / name) for name in filenames},
        }
        (bundle / "RELEASE_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        bundle.replace(output)
    return manifest


def verify_bundle(directory: Path) -> dict:
    manifest = read_json(directory / "RELEASE_MANIFEST.json")
    if manifest["format"] not in {
            "birdsvision-soyol-private-release-bundle-v1",
            "birdsvision-soyol-distribution-bundle-v1"}:
        raise ValueError("invalid release manifest format")
    expected_status = {
        "birdsvision-soyol-private-release-bundle-v1":
            "private_staging_not_publication_clearance",
        "birdsvision-soyol-distribution-bundle-v1":
            "prepared_for_public_distribution",
    }[manifest["format"]]
    if manifest["status"] != expected_status:
        raise ValueError("invalid release manifest status")
    expected_files = set(manifest["files"]) | {"RELEASE_MANIFEST.json"}
    actual_files = {path.name for path in directory.iterdir() if path.is_file()}
    if actual_files != expected_files or any(path.is_dir() for path in directory.iterdir()):
        raise ValueError("release bundle contains missing or extra files")
    for filename, expected_digest in manifest["files"].items():
        if Path(filename).name != filename or digest(directory / filename) != expected_digest:
            raise ValueError(f"release file changed: {filename}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--weight", type=Path, required=True)
    parser.add_argument("--attribution", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--recheck", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--distribution", action="store_true",
                        help="prepare the checked files for a public GitHub release")
    args = parser.parse_args()
    result = build_bundle(args.record, args.weight, args.attribution,
                          args.validation, args.recheck, args.output,
                          distribution=args.distribution)
    verify_bundle(args.output)
    print(json.dumps({"status": result["status"], "files": list(result["files"]),
                      "attribution_rows": result["attribution_rows"]},
                     ensure_ascii=False))
