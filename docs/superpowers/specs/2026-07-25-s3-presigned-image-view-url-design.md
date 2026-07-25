# S3 图片预签名查看 URL 测试 —— 设计文档

日期：2026-07-25
主题：为 `tests/python/s3/` 新增「上传真实图片 + 生成可在浏览器内联查看的预签名 URL」测试

## 目标

上传一张真实 PNG 图片到 S3 兼容端点，生成带响应头覆盖的预签名下载 URL，使其：

1. 匿名 HTTP GET 能下载，且字节与上传内容一致
2. 响应 `Content-Type` 为 `image/png`
3. 人工在浏览器打开该 URL 时**内联渲染图片**（而非触发下载）

## 范围与依赖

- 新增文件：`tests/python/s3/fixtures/sample.png`（50x50 纯红 PNG，用标准库生成后提交入库）
- 修改文件：
  - `tests/python/s3/conftest.py`（新增 `image_object` fixture）
  - `tests/python/s3/test_s3.py`（新增 `test_view_presigned_image_url` 用例）
- 复用现有 fixture：`s3_client` / `s3_bucket`
- 无新增运行时依赖（`requests` 已在上个任务引入；PNG 用标准库 `zlib`+`struct` 生成）

## sample.png 的生成

用标准库生成 50x50 纯红 PNG，一次性运行，产物提交入库：

```python
import struct, zlib

def _png_chunk(tag, data):
    chunk = tag + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk))

W = H = 50
raw = b"".join(b"\x00" + b"\xff\x00\x00" * W for _ in range(H))
idat = zlib.compress(raw)
png = (
    b"\x89PNG\r\n\x1a\n"
    + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))  # 8bit, RGB
    + _png_chunk(b"IDAT", idat)
    + _png_chunk(b"IEND", b"")
)
open("tests/python/s3/fixtures/sample.png", "wb").write(png)
```

## fixture 与测试用例

`conftest.py` 新增：

```python
from pathlib import Path

_SAMPLE_PNG = Path(__file__).parent / "fixtures" / "sample.png"


@pytest.fixture
def image_object(s3_client, s3_bucket):
    """生成临时图片测试对象，测试结束后自动删除"""
    key = f"g01/{date.today():%y%m%d}/{uuid.uuid4().hex}.png"
    content = _SAMPLE_PNG.read_bytes()
    yield key, content
    s3_client.delete_object(Bucket=s3_bucket, Key=key)
```

`test_s3.py` 新增：

```python
def test_view_presigned_image_url(s3_client, s3_bucket, image_object):
    """上传真实图片，生成可在浏览器内联查看的预签名 URL"""
    key, content = image_object
    s3_client.put_object(
        Bucket=s3_bucket, Key=key, Body=content, ContentType="image/png"
    )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": s3_bucket,
            "Key": key,
            "ResponseContentType": "image/png",
            "ResponseContentDisposition": "inline",
        },
        ExpiresIn=300,
    )
    print(f"\n图片查看地址: {url}")

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == content
    assert resp.headers["Content-Type"] == "image/png"
```

要点：

- 上传时 `ContentType="image/png"`；签名时 `ResponseContentType=image/png` + `ResponseContentDisposition=inline` → 浏览器内联渲染而非下载。
- 三重断言：状态码 200 + 字节一致 + 响应头 `Content-Type` 为 `image/png`。
- `print` 输出可直接点开查看的图片地址（需 `-s` 才在通过时显示）。
- teardown 由 `image_object` fixture 自动删除对象。

## 已知风险

- 与现有预签名用例相同：`get_object` 是对象级请求，不触发 `conftest.py` 记录的 nginx 尾斜杠重定向；`requests` 默认跟随重定向但此处不涉及。沿用既有策略，不预防。

## 验证方式

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py -s
```

预期 5 个用例全部 PASS，输出打印「图片查看地址」；人工点开该 URL，浏览器应内联显示一张 50x50 红色图片。

## 不做的事（YAGNI）

- 不校验图片像素内容 / 尺寸（字节一致即证明完整）
- 不测多种图片格式（JPG/GIF 等）
- 不测 `ResponseContentDisposition=attachment`（下载模式）
- 不引入 Pillow
