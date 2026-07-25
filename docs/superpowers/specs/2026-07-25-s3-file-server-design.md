# S3 文件服务（上传/查看图片）—— 设计文档

日期：2026-07-25
主题：基于 FastAPI 的文件服务，提供上传图片与查看图片接口

## 目标

构建一个 HTTP 文件服务，提供两个端点：

1. `POST /images` — 上传图片，返回 key 与查看地址
2. `GET /images/{key}` — 查看图片，服务从 S3 读取并直接返回字节流（不暴露 S3 地址、不跳转）

## 架构

- FastAPI 应用，自建 boto3 S3 client（复用 `mime.py` 验证过的 SigV4 + path-style 配置，但不 import `Attachment`）
- 配置通过 `python-decouple` 从 `.env` 读取
- 上传校验 `Content-Type` 以 `image/` 开头，按实际类型保存（扩展名 + content-type 跟随上传文件）
- 查看时从 S3 读回，用存储时的 `ContentType` 作为响应的 `media_type`

## 范围与约束

- 新增文件：`src/python/s3/server.py`、`tests/python/s3/test_server.py`
- 修改文件：`requirements.txt`（新增 `python-multipart~=0.0.21`、`httpx~=0.28.0`）
- 不引用 `src.python.s3.mime.Attachment`，服务自带 boto3 client
- 依赖真实 S3 端点（集成测试，不引入 mock）
- 测试上传后不自动删除对象（模拟真实使用场景，暂不清理）

## 接口

### `POST /images`

- 入参：`multipart/form-data`，字段名 `file`，类型 `UploadFile`
- 校验：`file.content_type` 必须以 `image/` 开头，否则 400
- 处理：按 content-type 映射扩展名（`image/png`→`.png`, `image/jpeg`→`.jpg`, `image/gif`→`.gif`, `image/webp`→`.webp`，其他→`.bin`）；key 格式 `g01_YYMMDD_<uuid>.{ext}`
- 返回：`{"key": "g01_YYMMDD_xxx.png", "view_url": "/images/g01_YYMMDD_xxx.png"}`

### `GET /images/{key}`

- 入参：路径参数 `key`（即 upload 返回的 key）
- 处理：`s3.get_object` 读取，不存在返回 404
- 返回：字节流，`Content-Type` 为存储时的值

## server.py 实现

```python
import uuid
from datetime import date

import boto3
from botocore.config import Config
from decouple import config
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI()

_BUCKET = config("S3_BUCKET")
_client = boto3.client(
    "s3",
    endpoint_url=config("S3_ENDPOINT_URL"),
    aws_access_key_id=config("S3_ACCESS_KEY"),
    aws_secret_access_key=config("S3_SECRET_KEY"),
    region_name=config("S3_REGION", default="us-east-1"),
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

_EXT = {"image/png": "png", "image/jpeg": "jpg", "image/gif": "gif", "image/webp": "webp"}


@app.post("/images")
async def upload_image(file: UploadFile):
    """上传图片，返回 key 与查看地址"""
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")
    ext = _EXT.get(content_type, "bin")
    key = f"g01_{date.today():%y%m%d}_{uuid.uuid4().hex}.{ext}"
    _client.put_object(
        Bucket=_BUCKET, Key=key, Body=await file.read(), ContentType=content_type
    )
    return {"key": key, "view_url": f"/images/{key}"}


@app.get("/images/{key}")
async def view_image(key: str):
    """从 S3 读取图片并直接返回字节流"""
    try:
        obj = _client.get_object(Bucket=_BUCKET, Key=key)
    except _client.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="图片不存在")
    return Response(
        content=obj["Body"].read(),
        media_type=obj.get("ContentType", "application/octet-stream"),
    )
```

## 测试

`tests/python/s3/test_server.py`：

```python
from pathlib import Path

from fastapi.testclient import TestClient

from src.python.s3.server import app

client = TestClient(app)
_SAMPLE_PNG = Path(__file__).parent / "fixtures" / "sample.png"


def test_upload_and_view():
    """上传图片 → 拿 view_url → 查看返回相同字节"""
    data = _SAMPLE_PNG.read_bytes()
    resp = client.post(
        "/images",
        files={"file": ("sample.png", data, "image/png")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"].startswith("g01_")
    assert body["key"].endswith(".png")

    view = client.get(body["view_url"])
    assert view.status_code == 200
    assert view.content == data
    assert view.headers["content-type"] == "image/png"


def test_upload_rejects_non_image():
    """上传非图片返回 400"""
    resp = client.post(
        "/images",
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400
```

## 依赖变更

`requirements.txt` 新增：

```
python-multipart~=0.0.21
httpx~=0.28.0
```

## 验证方式

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_server.py -v
```

预期 2 个用例通过。

## 启动方式

```bash
PYTHONNOUSERSITE=1 uvicorn src.python.s3.server:app
```

## 不做的事（YAGNI）

- 不加鉴权/认证
- 不限制文件大小（暂不处理大文件流式上传）
- 不做图片尺寸校验
- 不加 `__init__.py`
- 不用 mock，依赖真实 S3 端点