# S3 预签名下载 URL 测试 —— 设计文档

日期：2026-07-25
主题：为 `tests/python/s3/test_s3.py` 新增「生成下载预签名地址」端到端测试用例

## 目标

新增一个 pytest 用例，验证以下端到端流程：

1. 上传测试对象到 S3 兼容端点
2. 调用 `generate_presigned_url("get_object", ...)` 生成带签名的下载 URL
3. 用匿名 HTTP GET（无凭证）请求该 URL
4. 断言返回内容与上传内容字节完全一致

这能真实证明预签名签名有效、nginx 反代端点可正确响应匿名带签名请求。

## 范围与依赖

- 修改文件：`tests/python/s3/test_s3.py`（新增一个用例，复用现有 fixture）
- 依赖变更：`requirements.txt` 新增 `requests~=2.34.0`
- 复用 `conftest.py` 现有 fixture：`s3_client` / `s3_bucket` / `test_object`

## 实现

在 `test_s3.py` 顶部新增 `import requests`，末尾新增用例：

```python
import requests


def test_download_presigned_url(s3_client, s3_bucket, test_object):
    """生成 get_object 预签名 URL，匿名下载并校验内容一致"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_bucket, "Key": key},
        ExpiresIn=300,
    )
    print(f"\n预签名下载地址: {url}")

    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200
    assert resp.content == content
```

要点：

- 先 `put_object` 上传，保证对象存在（与 `test_list` / `test_download_roundtrip` 模式一致）。
- `generate_presigned_url` 用 `get_object`，`ExpiresIn=300`（5 分钟，足够测试跑完）。
- `print` 输出下载地址便于人工验证；pytest 默认捕获输出，需加 `-s` 才在通过时显示。
- `requests.get` 匿名请求（不带任何凭证），签名参数全在 URL query 中——这正是被验证的对象。
- 双重断言：状态码 200 + 内容字节完全一致。
- teardown 由 `test_object` fixture 自动删除对象，无需额外清理。

## 已知风险

- **nginx 重定向**：`conftest.py` 记录了 bucket 级请求会被 nginx 301 到尾斜杠路径并破坏 SigV4 签名。但 `get_object` 是对象级请求（路径末尾无斜杠），不触发该重定向。`requests` 默认跟随重定向，若真遇到 3xx 会丢签名导致失败——按 YAGNI 先不预防，用断言 200 及早暴露；实测失败再针对性处理。
- **网络可达性**：该测试与现有 3 个用例一样依赖真实 S3 端点，属集成测试；不引入 mock，保持风格一致。

## 验证方式

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py -s
```

预期 4 个用例全部通过，并打印出预签名 URL。

## 不做的事（YAGNI）

- 不测过期（`ExpiresIn` 到期后失效）
- 不测错误 key / 不存在对象
- 不测 `put_object` 预签名上传
- 本次仅聚焦「下载签名地址」这一个场景
