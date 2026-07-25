# S3 图片预签名查看 URL 测试 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上传一张真实 50x50 PNG，生成带响应头覆盖的预签名 URL，验证匿名下载字节一致、`Content-Type` 为 `image/png`，且浏览器可内联查看。

**Architecture:** 用标准库生成固定 PNG fixture 提交入库；`conftest.py` 新增 `image_object` fixture 读取该文件；`test_s3.py` 新增一个用例，用 boto3 `generate_presigned_url` 带 `ResponseContentType`/`ResponseContentDisposition`，用 `requests` 匿名 GET 校验。

**Tech Stack:** Python、pytest、boto3、requests、标准库 zlib/struct

## Global Constraints

- 运行 pytest / python 必须带 `PYTHONNOUSERSITE=1` 并用 conda `ai` 环境解释器，避免 user-site 旧包污染
- 无新增运行时依赖（`requests` 已在上个任务引入；PNG 用标准库生成）
- 不引入 Pillow；不引入 mock（集成测试，依赖真实 S3 端点）
- teardown 由 `image_object` fixture 负责，用例内不额外清理
- 图片 key 格式沿用现有约定：`g01/{date:%y%m%d}/{uuid.hex}.png`

---

### Task 1: 生成 sample.png fixture

**Files:**
- Create: `tests/python/s3/fixtures/sample.png`（50x50 纯红 PNG，二进制产物）

**Interfaces:**
- Produces: 文件 `tests/python/s3/fixtures/sample.png`，可被 `Path.read_bytes()` 读取，是合法可渲染的 PNG

- [ ] **Step 1: 运行生成脚本创建 PNG**

Run（一次性脚本，直接在命令行执行，不留脚本文件）：

```bash
PYTHONNOUSERSITE=1 python -c "
import struct, zlib, pathlib
def chunk(tag, data):
    c = tag + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))
W = H = 50
raw = b''.join(b'\x00' + b'\xff\x00\x00' * W for _ in range(H))
png = (b'\x89PNG\r\n\x1a\n'
    + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    + chunk(b'IDAT', zlib.compress(raw))
    + chunk(b'IEND', b''))
p = pathlib.Path('tests/python/s3/fixtures/sample.png')
p.parent.mkdir(parents=True, exist_ok=True)
p.write_bytes(png)
print('wrote', p, p.stat().st_size, 'bytes')
"
```

Expected: 输出 `wrote tests/python/s3/fixtures/sample.png <N> bytes`

- [ ] **Step 2: 验证是合法 PNG**

Run:

```bash
PYTHONNOUSERSITE=1 python -c "
data = open('tests/python/s3/fixtures/sample.png','rb').read()
assert data[:8] == b'\x89PNG\r\n\x1a\n', 'bad signature'
assert data[12:16] == b'IHDR', 'no IHDR'
print('valid PNG, size', len(data))
"
```

Expected: 输出 `valid PNG, size <N>`，无 AssertionError

- [ ] **Step 3: Commit**

```bash
git add tests/python/s3/fixtures/sample.png
git commit -m "test: 新增 S3 测试用 50x50 PNG fixture"
```

---

### Task 2: 新增 image_object fixture 与图片预签名查看用例

**Files:**
- Modify: `tests/python/s3/conftest.py`（新增 `from pathlib import Path`、`_SAMPLE_PNG` 常量、`image_object` fixture）
- Modify: `tests/python/s3/test_s3.py`（末尾新增 `test_view_presigned_image_url` 用例）
- Test: `tests/python/s3/test_s3.py::test_view_presigned_image_url`

**Interfaces:**
- Consumes（来自 `tests/python/s3/conftest.py`）:
  - `s3_client` — 已配置 SigV4 + path-style 的 boto3 S3 client
  - `s3_bucket` — `str`，目标桶名
  - `image_object` — 本任务新增 fixture，`yield (key: str, content: bytes)`，content 为 sample.png 字节，测试后自动删除该 key
  - `tests/python/s3/fixtures/sample.png`（Task 1 产物）
  - `requests` 模块（`test_s3.py` 已有 `import requests`）
- Produces: pytest 用例 `test_view_presigned_image_url(s3_client, s3_bucket, image_object)`，无返回值

- [ ] **Step 1: 在 conftest.py 新增 Path 导入与 image_object fixture**

在 `tests/python/s3/conftest.py` 顶部导入区，`import uuid` 后新增：

```python
from pathlib import Path
```

在文件末尾（现有 `test_object` fixture 之后）新增：

```python
_SAMPLE_PNG = Path(__file__).parent / "fixtures" / "sample.png"


@pytest.fixture
def image_object(s3_client, s3_bucket):
    """生成临时图片测试对象，测试结束后自动删除"""
    key = f"g01/{date.today():%y%m%d}/{uuid.uuid4().hex}.png"
    content = _SAMPLE_PNG.read_bytes()
    yield key, content
    # teardown：删除临时对象，保持桶干净
    s3_client.delete_object(Bucket=s3_bucket, Key=key)
```

- [ ] **Step 2: 在 test_s3.py 末尾新增用例**

在 `tests/python/s3/test_s3.py` 末尾新增：

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

- [ ] **Step 3: 运行新用例确认通过**

Run:

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py::test_view_presigned_image_url -s -v
```

Expected: PASS，输出打印 `图片查看地址: https://...`（含 `response-content-type` 与 `response-content-disposition` 查询参数）。若端点不可达则报连接错误（环境问题，非代码问题）。

- [ ] **Step 4: 运行全部 S3 测试确认无回归**

Run:

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py -s
```

Expected: 5 个用例全部 PASS。

- [ ] **Step 5: Commit**

```bash
git add tests/python/s3/conftest.py tests/python/s3/test_s3.py
git commit -m "test: 新增 S3 图片预签名内联查看 URL 测试"
```

---

## Self-Review

**1. Spec coverage:**
- 上传真实 PNG → Task 1 生成 + Task 2 Step 2 `put_object(ContentType=image/png)` ✓
- 生成内联查看 URL（`ResponseContentType`/`ResponseContentDisposition=inline`）→ Task 2 Step 2 ✓
- 匿名下载字节一致 + Content-Type=image/png → Task 2 三重断言 ✓
- `image_object` fixture → Task 2 Step 1 ✓
- fixtures/sample.png 50x50 纯红标准库生成 → Task 1 ✓
- 打印图片地址 + `-s` → Step 2 代码含 print，Step 3/4 命令带 `-s` ✓
- 验证 5 用例全过 → Task 2 Step 4 ✓
- YAGNI 边界（不校验像素/不多格式/不 attachment/不 Pillow）→ 计划未引入，符合 ✓

**2. Placeholder scan:** 无 TBD/TODO，所有步骤含完整代码与命令 ✓

**3. Type consistency:** `image_object` 解包 `(key, content)` 与其 `yield key, content` 一致；`_SAMPLE_PNG` 路径指向 Task 1 产物；`generate_presigned_url` 参数 `Params`/`ExpiresIn` 为 boto3 标准签名；conftest 已有 `date`/`uuid`/`pytest`，仅补 `Path` ✓

无问题。
