# S3 mime.py 新增下载图片功能 — 设计文档

日期：2026-07-25
范围：`src/python/s3/mime.py`

## 背景

`Attachment` 类当前提供两个方法：

- `upload(image_bytes) -> str`：上传图片，返回对外 key（形如 `g01_260725_<uuid>.png`）。
- `view_url(attachment_id, expire_seconds) -> str`：生成 `inline` 内联查看的预签名 URL。

需要新增「下载图片」能力，即在程序内直接取回图片的原始字节，供调用方自行处理（保存、二次处理等）。

## 目标

在 `Attachment` 类中新增 `download()` 方法，与现有方法对称，形成完整生命周期：
`upload → download / view_url`。

## 设计

### 方法签名

```python
def download(self, attachment_id: str) -> bytes:
    """传入 upload 返回的 key，从 S3 读取原始字节"""
    s3_key = attachment_id.replace("_", "/", 2)  # g01_260725_abc.png -> g01/260725/abc.png
    obj = self._client.get_object(Bucket=self._bucket, Key=s3_key)
    return obj["Body"].read()
```

### 决策要点

| 方面 | 决策 |
|------|------|
| 签名 | `download(attachment_id: str) -> bytes`，参数命名与 `view_url` 一致 |
| key 转换 | 复用 `attachment_id.replace("_", "/", 2)`，与 `view_url` 完全一致 |
| 对象不存在 | 直接抛出 boto3 的 `NoSuchKey` 异常，不做捕获，保持工具类简洁；由调用方处理 |
| 返回值 | 原始 `bytes`，不封装额外结构 |

## 测试

在 `tests/python/s3/test_mime.py` 中新增用例：

- `test_upload_and_download`：上传 `fixtures/sample.png` → 调用 `download(key)` → 断言返回 bytes 与原文件一致。
- 用不存在的 key 调用 `download()` → 断言抛出异常。

运行方式遵循项目约定：

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_mime.py
```

## 非目标（YAGNI）

- 不新增 `download_url()`（下载用预签名 URL）——本次只需程序内取字节。
- 不改动 `server.py`（其已有 `GET /images/{key}` 返回字节流）。
- 不改动 `upload()` / `view_url()`。
