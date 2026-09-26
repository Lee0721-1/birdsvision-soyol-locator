# 2026-09-27 线上定位进程记录

线上 SOYOL 使用独立进程监听 `127.0.0.1:8001`，启动入口为 `uvicorn birdsvision_locator.app:app`，仅通过 `POST /v1/locate` 向分类 API 返回原图尺寸和鸟框。本仓库 `birdsvision_locator/app.py` 与当天线上定位进程的源文件一致；分类 API、类表、权重和 TYLO 不属于本项目。

当天记录的主机为 Ubuntu 24.04.4 LTS、Python 3.12.3。共享虚拟环境中的定位服务相关版本为 FastAPI 0.141.1、Pillow 12.3.0、PyTorch 2.13.0+cpu、torchvision 0.28.0+cpu、Uvicorn 0.52.1。Ultralytics 8.4.126 由部署目录的 `vendor/` 提供；[vendor_provenance.json](vendor_provenance.json)记录已安装包与 PyPI wheel 的逐文件核对结果，[verify_vendor_record.py](verify_vendor_record.py)可在持有私有部署目录和 wheel 的环境中复核。wheel、正式权重和部署目录不在仓库中。

仓库根目录的依赖清单是项目开发环境版本，不能当作上述共享生产环境的完整锁文件。此目录记录定位进程对应的运行事实，不包含分类器的部署文件；复现时须自行安装匹配 Python/PyTorch 的依赖，并使用有权使用的单类 Detect 权重。
