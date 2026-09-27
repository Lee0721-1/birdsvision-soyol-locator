# Third-party notices

本项目调用 FastAPI、Uvicorn、PyTorch、torchvision、Pillow、pytest 和 Ultralytics。它们各自适用其上游许可证。SOYOL 训练代码使用 Ultralytics YOLO26 Detect，官方提供 AGPL-3.0 与 Enterprise 许可路线，见 https://www.ultralytics.com/license 。Git 源码树不包含 Ultralytics 预训练权重、SOYOL 微调权重、数据集或图片；SOYOL `best.pt` 作为[固定 GitHub Release](https://github.com/Lee0721-1/birdsvision-soyol-locator/releases/tag/soyol-v1-a-documented-20260927) 附件单独发布。使用者必须另行确认所用依赖、权重和图片的适用条款及来源授权。
