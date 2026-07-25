# S3 预签名下载 URL 测试 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `tests/python/s3/test_s3.py` 新增一个端到端用例，验证 `get_object` 预签名下载 URL 可被匿名 HTTP GET 且内容一致。

**Architecture:** 复用 `conftest.py` 现有 fixture（`s3_client` / `s3_bucket` / `test_object`）；用 boto3 `generate_presigned_url` 生成签名 URL，用 `requests` 发匿名 GET 下载，断言状态码与字节内容。

**Tech Stack:** Python、pytest、boto3、requests

## Global Constraints

- 运行 pytest / python 必须带 `PYTHONNOUSERSITE=1` 并用 conda `ai` 环境解释器，避免 user-site 旧包污染
- 新增依赖版本约束：`requests~=2.34.0`（写入 `requirements.txt`）
- 不引入 mock；测试依赖真实 S3 端点（集成测试）
- teardown 由现有 `test_object` fixture 负责，用例内不额外清理

---

### Task 1: 新增预签名下载 URL 端到端测试

**Files:**
- Modify: `requirements.txt`（在 `boto3~=1.35.0` 行附近新增 `requests~=2.34.0`）
- Modify: `tests/python/s3/test_s3.py`（顶部加 `import requests`，末尾新增用例）
- Test: `tests/python/s3/test_s3.py::test_download_presigned_url`

**Interfaces:**
- Consumes（来自 `tests/python/s3/conftest.py`，均为 pytest fixture）:
  - `s3_client` — 已配置 SigV4 + path-style 的 boto3 S3 client
  - `s3_bucket` — `str`，目标桶名
  - `test_object` — `yield (key: str, content: bytes)`，测试结束自动删除该 key
- Produces: 一个 pytest 用例函数 `test_download_presigned_url(s3_client, s3_bucket, test_object)`，无返回值

- [ ] **Step 1: 安装 requests 依赖并写入 requirements.txt**

在 `requirements.txt` 中 `boto3~=1.35.0` 行之后新增一行：

```
requests~=2.34.0
```

安装：

```bash
PYTHONNOUSERSITE=1 python -m pip install "requests~=2.34.0"
```

Expected: 成功安装 requests 2.34.x（或已满足要求）

- [ ] **Step 2: 写入失败测试**

在 `tests/python/s3/test_s3.py` 顶部新增导入（文件当前无 import，加在第 1 行）：

```python
import requests
```

在文件末尾新增用例：

```python
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

- [ ] **Step 3: 运行测试确认收集到用例**

Run:

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py::test_download_presigned_url -s -v
```

Expected: 用例被收集并执行；若端点可达则 PASS 并打印 `预签名下载地址: https://...`。若端点不可达，报连接错误（属环境问题，非代码问题）。

- [ ] **Step 4: 运行全部 S3 测试确认无回归**

Run:

```bash
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py -s
```

Expected: 4 个用例全部 PASS，输出中包含预签名 URL。

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/python/s3/test_s3.py
git commit -m "test: 新增 S3 预签名下载 URL 端到端测试"
```

---

## Self-Review

**1. Spec coverage:**
- 目标（上传→生成预签名→匿名 GET→内容一致）→ Task 1 Step 2 全部覆盖 ✓
- 依赖 `requests~=2.34.0` → Task 1 Step 1 ✓
- 复用现有 fixture → Interfaces 块列明 ✓
- 打印下载地址 + `-s` 运行 → Step 2 代码含 `print`，Step 3/4 命令带 `-s` ✓
- 验证方式（4 用例全过）→ Step 4 ✓
- YAGNI 边界（不测过期/错误 key/上传签名）→ 计划未引入这些，符合 ✓

**2. Placeholder scan:** 无 TBD/TODO，所有代码步骤含完整代码与命令 ✓

**3. Type consistency:** `test_object` 解包为 `(key, content)` 与 conftest `yield key, content` 一致；`generate_presigned_url` 参数名 `Params` / `ExpiresIn` 为 boto3 标准签名 ✓

无问题。
