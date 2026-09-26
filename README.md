# SOYOL 鸟体定位器

SOYOL 是 BirdsVision 的独立鸟体定位项目。名称取自 Student YOLO。内部用于效果比对的教师模型称 TYLO（Teacher YOLO）；TYLO、分类器及其权重不属于本项目。

本项目只接收图片并返回原图尺寸和鸟框，不识别鸟种。分类器是另一个项目，通过本机 HTTP 调用定位器；定位器不加载分类器代码、类表或权重。[鸟视官网](https://www.birdsvision.com.cn/)介绍应用与下载。

## 项目内容

- `birdsvision_locator/`：独立 FastAPI 进程，`POST /v1/locate` 接收 `application/octet-stream` 图片，返回 `width`、`height`、`boxes`。
- `soyol/`：A 层审计数据导出、YOLO26n Detect 训练、验证、逐图署名及私密发布包工具。
- `soyol/ATTRIBUTION_A_DOCUMENTED_20260926.csv`：现有 1,316 张训练图片的逐图署名审阅表；不含图片。
- [SOYOL_MODEL_CARD.md](SOYOL_MODEL_CARD.md)：训练与验证事实、发布限制。

源码采用 [AGPL-3.0-only](LICENSE)。图片各有自己的许可；本仓库的源码许可证不改变图片许可。当前仅为**本地私密整理版**，未上传 GitHub、未公开模型权重。平台条款询问仍待 iNaturalist 人工答复。独立 `final_test` 尚未完成，不把 validation 当作独立验收。

## 独立安装与运行

定位服务与训练工具可使用两个 Python 环境，均不依赖分类器：

```bash
python -m pip install -r requirements-locator.txt
export BIRDSVISION_SOYOL_MODEL_PATH=/private/path/best.pt
uvicorn birdsvision_locator.app:app --host 127.0.0.1 --port 8001
```

`GET /health` 可检查模型是否加载。定位接口只供受控的本机调用，不应将 8001 端口直接暴露到公网。训练工具的依赖见 `requirements-training.txt`；训练命令和数据合同见源码及模型卡。训练图片、选择清单、运行目录、正式权重和 TYLO 均须保存在仓库外。

## 验证

```bash
python -m pip install -r requirements-training.txt
python -m pip install -r requirements-test.txt
python -m pytest -q
```

测试使用合成数据与模拟模型，不读取生产权重或训练图片。正式发布时，还需将实际线上定位进程的对应源码、依赖来源、权重、模型卡和逐图署名绑定到同一固定版本；本地整理版不能代替线上运行文件的核对。
