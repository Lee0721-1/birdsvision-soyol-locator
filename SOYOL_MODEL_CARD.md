# SOYOL v1 model card

The repository contains the locator source and attribution table. The SOYOL `best.pt` weight is distributed as a separate GitHub Release asset. Training images, classifier weights and labels, and an independent final-test result are not included.

## Documented-source retraining completed on 2026-09-26

An internal derived A-tier selection keeps 1,316 individually checked iNaturalist photo records (1,249 with human-confirmed bird boxes and 67 explicitly reviewed as having no bird box), with 1,078 train and 238 validation images. It excludes five original observations that could no longer be checked and 174 Hugging Face dataset images lacking a documented original-photo rights chain. The internal export passed this repository's `soyol.soyol_dataset.verify` check. The images and private selection remain outside this repository.

The new run completed 20 epochs on the official YOLO26n Detect initialization, with `imgsz=640`, `batch=8`, Ultralytics 8.4.126 and no TYLO checkpoint. On the retained 238-image validation split (322 human bird boxes), the project's one-to-many branch followed by NMS and `max_det=10` gave both `best.pt` and `last.pt` mAP50 0.7775 and mAP50-95 0.4525. The two checkpoint files are distinct; the validation metrics tie, so `best.pt` is recorded as the selected checkpoint. These are validation results, not independent `final_test` results. The older run described below used a different validation set; its scores are not a direct comparison.

The retained photos have recorded photo-level CC BY or CC0 codes and current attribution text. Their license URLs are derived from iNaturalist's current code-to-URL mapping, rather than captured historical URLs for each photo. iNaturalist has not yet given a human response to the platform-terms inquiry. Preparation of this dataset does not clear the planned AGPL-3.0 weight publication.

On 2026-09-27, a fresh public API check found all 1,316 retained photos with the same photo-level license codes. The five excluded observations were still not returned. One retained photo, `inaturalist:693812782`, had an updated attribution string: `(c) Kesava Garimella, some rights reserved (CC BY)`. `soyol/ATTRIBUTION_TRAINING_20260926.csv` preserves the table bound to the training record; `soyol/ATTRIBUTION_A_DOCUMENTED_20260926.csv` is the updated publication table. The release bundle checks both against the fresh metadata record and lists the change. This metadata check does not verify legal ownership or historical license URLs.

## Model and intended output

SOYOL v1 is a single-class YOLO26n Detect bird locator. It returns zero to ten post-NMS bird boxes for one image. It does not classify bird species, reject non-bird images, or output keypoints. In the BirdsVision 1.0.2 service it supplies crops for a separate classifier; that classifier's production weights are outside this repository.

## Older 1,495-image training provenance retained internally

- Initialization: official Ultralytics `yolo26n.pt` Detect checkpoint, SHA-256 `9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`; no TYLO Pose checkpoint was loaded.
- Supervision: A-tier images only, using strict human-confirmed final boxes. The export contains 1,495 images, 1,428 with boxes and 67 explicitly reviewed as having no bird box. Train has 1,220 images and 1,656 boxes; validation has 275 images and 360 boxes. B-tier authorization is deferred; C-tier images were not used for weight updates.
- Run: Ultralytics 8.4.126, 20 complete epochs, image size 640, batch 8. The saved best checkpoint came from epoch 18.
- Validation: for the selected checkpoint on the one-to-many NMS branch, mAP50 was 0.816 and mAP50-95 was 0.515. Inference uses `conf=0.25`, `iou=0.7`, and `max_det=10`. The ten-box limit never truncates ground-truth labels.

These numbers come from the internal training and validation records. The independent SOYOL `final_test` has not been run or accepted. An A-tier image quality review is also recorded as `not_started`. The release does not claim independent acceptance or guarantee detection quality.

## Attribution and publication boundary

The **older** internal A-tier selection contains 1,093 CC BY records, 228 CC0 records, and 174 CC0-1.0 records. The newly trained selection contains only the 1,316 iNaturalist photos described above: 1,088 photo-level CC BY records and 228 CC0 records. `soyol/ATTRIBUTION_A_DOCUMENTED_20260926.csv` records their current attribution, source pages, mapped license URLs and change notices without exporting images. The license on this repository's source code does not relicense the training images.

Of the older A-tier records, 1,321 were obtained from iNaturalist and 174 from a Hugging Face bird-species dataset. The new run excluded all 174 Hugging Face records and the five unavailable iNaturalist observations. The project owner describes the new training as noncommercial research and learning. iNaturalist's current platform terms prohibit training on its data **for commercial purposes**; they do not state that every AGPL publication of a model trained noncommercially is prohibited. The support inquiry about this planned release and the public service has not received a human reply. The photo-level licenses and the platform terms must be recorded as separate issues; the pending inquiry is not affirmative platform permission.

The Hugging Face dataset card marks the dataset CC0-1.0 but says it was sourced from a Kaggle dataset. All 174 records in the older selection use the same dataset-level attribution string; the recorded evidence does not identify the original photographer or an image-specific rights grant. These photos were excluded from the released `best.pt` training run. Any future publicly released model trained on them would first need upstream, image-level rights verification. The attribution exporter's CSV is an evidence inventory, not a publication approval.

SOYOL code and the `best.pt` weight follow the Ultralytics AGPL-3.0 route, with both offered under AGPL-3.0-only. SOYOL localization and ConvNeXt classification are separate projects. The classifier API and training source are available in their own repositories; the classifier class table, production weights, and internal TYLO teacher model are not part of this SOYOL release. On 2026-09-27 the production service switched to a separate SOYOL locator process that communicates with the classifier API over loopback HTTP. This technical and release boundary is the project's architecture decision; it does not by itself settle the scope of the corresponding source. See [Ultralytics licensing guidance](https://www.ultralytics.com/license) and the [GNU FAQ on separate programs](https://www.gnu.org/licenses/gpl-faq.en.html#MereAggregation).

The weight release includes the corresponding source revision, third-party notices, attribution table, and a fixed release manifest. It states explicitly that independent `final_test` was omitted and reports the retained validation metrics only.
