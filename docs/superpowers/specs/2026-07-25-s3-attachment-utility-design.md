# S3 附件工具类（Attachment）—— 设计文档

日期：2026-07-25
主题：将验证过的 S3 上传 / 预签名操作提炼为可复用的 `Attachment` 工具类

## 目标

新建 `src/python/s3/mime.py`，提供 `Attachment` 类，封装两个方法：

1. `upload(image_bytes) -> str`：上传图片，返回 key（格式 `g01_YYMMDD_<uuid>.png`）
2. `view_url(attachment_id, expire_seconds=300) -> str`：传入 upload 返回的 key，生成可在浏览器内联查看的预签名 URL

## 范围与约束

- 新增文件：`src/python/s3/mime.py`（工具类）、`tests/python/s3/test_mime.py`（测试）
- 配置来源：内部用 `python-decouple` 从 `.env` 读取（构造函数无参）
- S3 客户端：SigV4 + path-style，复用现有测试验证过的配置；**不加** nginx `ListObjectsV2` 尾斜杠钩子（工具类不做 list 操作，YAGNI）
- 无新增运行时依赖（boto3 / requests / python-decouple 均已在 requirements.txt）
- 不引入 mock；测试依赖真实 S3 端点（集成测试）

## 类实现

`src/python/s3/mime.py`：

```python
import uuid
from datetime import date

import boto3
from botocore.config import Config
from decouple import config


class Attachment:
    """S3 附件工具类：上传图片 + 生成查看签名 URL"""

    def __init__(self):
        # 配置从 .env 读取（python-decouple）
        self._bucket = config("S3_BUCKET")
        self._client = boto3.client(
            "s3",
            endpoint_url=config("S3_ENDPOINT_URL"),
            aws_access_key_id=config("S3_ACCESS_KEY"),
            aws_secret_access_key=config("S3_SECRET_KEY"),
            region_name=config("S3_REGION", default="us-east-1"),
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def upload(self, image_bytes: bytes) -> str:
        """上传图片，返回 key，格式 'g01_YYMMDD_<uuid>.png'"""
        key = f"g01_{date.today():%y%m%d}_{uuid.uuid4().hex}.png"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=image_bytes,
            ContentType="image/png",
        )
        return key

    def view_url(self, attachment_id: str, expire_seconds: int = 300) -> str:
        """传入 upload 返回的 key，生成内联查看的预签名 URL"""
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket,
                "Key": attachment_id,
                "ResponseContentType": "image/png",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expire_seconds,
        )
```

要点：

- 客户端配置复用 conftest 验证过的 SigV4 + path-style，不加 list 钩子（YAGNI）。
- `upload` 内部生成 key（`g01_YYMMDD_<uuid>.png`，uuid 用 `uuid.uuid4().hex`），上传时带 `ContentType=image/png`，返回 key。
- `view_url` 带 `ResponseContentType=image/png` + `ResponseContentDisposition=inline`，浏览器内联查看；`expire_seconds` 默认 300，可调。

## 测试

`tests/python/s3/test_mime.py`：

```python
import requests
from src.python.s3.mime import Attachment


def test_upload_and_view():
    """上传图片 → 查看签名 URL → 匿名下载内容一致"""
    att = Attachment()
    data = open("tests/python/s3/fixtures/sample.png", "rb").read()
    key = att.upload(data)
    assert key.startswith("g01_")
    assert key.endswith(".png")
    assert len(key) == len("g01_YYMMDD_") + 32 + len(".png")

    url = att.view_url(key)
    assert "response-content-type=image" in url
    assert "response-content-disposition=inline" in url

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == data
    assert resp.headers["Content-Type"] == "image/png"
```

导入路径 `from src.python.s3.mime import Attachment` 依赖 pytest rootdir（仓库根）在 `sys.path` 上。pytest 默认将 rootdir 加入路径；若导入失败，在计划中通过在仓库根放置空 `conftest.py` 或调整 `sys.path` 解决。

## 验证方式

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_mime.py -s -v
```

预期 1 个用例通过，输出包含签名 URL（含 `response-content-type` 参数）。

## 不做的事（YAGNI）

- 不做 list / delete 方法（本次只上传 + 查看）
- 不加 nginx 尾斜杠钩子
- 不做多图片格式（仅 png）
- 测试不做 teardown 删除（临时对象，依赖手动清理或 S3 生命周期）
- 不支持自定义前缀（`g01_` 固定）
