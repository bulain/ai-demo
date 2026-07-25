# S3 上传/下载测试代码 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 编写一个 pytest 测试套件，验证向 S3 兼容端点上传、列举、下载文件的完整往返功能。

**Architecture:** 使用 boto3 构造适配 S3 兼容端点的客户端（s3v4 签名 + 路径寻址）。配置通过 python-decouple 从 `.env` 读取。conftest.py 提供客户端与测试对象 fixture（含自动清理），test_s3.py 覆盖上传/列举/下载校验三个用例。

**Tech Stack:** Python, boto3, botocore, pytest, python-decouple

## Global Constraints

- 凭证不硬编码，一律通过 `python-decouple` 的 `config()` 从 `.env` 读取
- 测试文件放在 `tests/python/s3/` 目录下（遵循 `tests/<分类>/<工具>/` 约定）
- 代码注释使用中文
- 客户端必须用 `signature_version="s3v4"` 与 `addressing_style="path"`
- 桶名：`cnn-s3-rg-dify-dev`（无结尾斜杠）
- 测试结束后自动删除临时测试对象

---

### Task 1: 依赖与配置

**Files:**
- Modify: `requirements.txt`
- Modify: `.env`

**Interfaces:**
- Consumes: 无
- Produces: `.env` 中的 `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET`, `S3_REGION` 五个配置项，供后续 conftest.py 读取

- [ ] **Step 1: 在 requirements.txt 末尾追加依赖**

```
boto3~=1.35.0
pytest~=8.3.0
```

- [ ] **Step 2: 在 .env 末尾追加 S3 配置**

```
S3_ENDPOINT_URL=https://dify.iloglip.cn
S3_ACCESS_KEY=cMtwJ9Nwyo5yABYnr1X1cxs6r34rKGxy
S3_SECRET_KEY=vBqH8MxvPN7HNEVm3E7T1TZnefoQkwU24K44040h
S3_BUCKET=cnn-s3-rg-dify-dev
S3_REGION=us-east-1
```

- [ ] **Step 3: 安装依赖**

Run: `pip install boto3 pytest`
Expected: 安装成功，无报错

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .env
git commit -m "chore: 新增 boto3/pytest 依赖与 S3 配置"
```

---

### Task 2: conftest.py — 客户端与测试对象 fixture

**Files:**
- Create: `tests/python/s3/conftest.py`

**Interfaces:**
- Consumes: `.env` 中的 `S3_*` 配置（Task 1 产出）
- Produces:
  - fixture `s3_client` — 返回 `boto3.client("s3", ...)` 实例
  - fixture `s3_bucket` — 返回桶名字符串（来自 `S3_BUCKET`）
  - fixture `test_object` — 返回 `(key: str, content: bytes)` 元组；key 形如 `test-<uuid>.txt`，content 为已知随机字节；teardown 阶段调用 `delete_object` 删除该 key

- [ ] **Step 1: 编写 conftest.py**

```python
import uuid

import boto3
import pytest
from botocore.config import Config
from decouple import config


@pytest.fixture(scope="session")
def s3_client():
    """构造适配 S3 兼容端点的 boto3 客户端"""
    return boto3.client(
        "s3",
        endpoint_url=config("S3_ENDPOINT_URL"),
        aws_access_key_id=config("S3_ACCESS_KEY"),
        aws_secret_access_key=config("S3_SECRET_KEY"),
        region_name=config("S3_REGION", default="us-east-1"),
        config=Config(
            signature_version="s3v4",              # 对应 api: S3v4
            s3={"addressing_style": "path"},       # 对应 path: auto
        ),
    )


@pytest.fixture(scope="session")
def s3_bucket():
    """返回目标桶名"""
    return config("S3_BUCKET")


@pytest.fixture
def test_object(s3_client, s3_bucket):
    """生成临时测试对象，测试结束后自动删除"""
    key = f"test-{uuid.uuid4()}.txt"
    content = f"hello s3 {uuid.uuid4()}".encode("utf-8")
    yield key, content
    # teardown：删除临时对象，保持桶干净
    s3_client.delete_object(Bucket=s3_bucket, Key=key)
```

- [ ] **Step 2: 验证 fixture 可被 pytest 收集**

Run: `pytest tests/python/s3/ --collect-only -q`
Expected: 无收集错误（此时尚无测试用例，输出 "no tests ran" 也可接受）

- [ ] **Step 3: Commit**

```bash
git add tests/python/s3/conftest.py
git commit -m "test: 新增 S3 客户端与测试对象 fixture"
```

---

### Task 3: 上传测试

**Files:**
- Create: `tests/python/s3/test_s3.py`

**Interfaces:**
- Consumes: fixture `s3_client`, `s3_bucket`, `test_object`（Task 2 产出）
- Produces: 测试函数 `test_upload`

- [ ] **Step 1: 编写上传测试（失败测试）**

```python
def test_upload(s3_client, s3_bucket, test_object):
    """上传对象，断言响应状态码为 200"""
    key, content = test_object
    resp = s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
```

- [ ] **Step 2: 运行测试确认结果**

Run: `pytest tests/python/s3/test_s3.py::test_upload -v`
Expected: PASS（若连接/凭证失败，会在 fixture 处 error 并给出明确信息）

- [ ] **Step 3: Commit**

```bash
git add tests/python/s3/test_s3.py
git commit -m "test: 新增 S3 上传测试"
```

---

### Task 4: 列举测试

**Files:**
- Modify: `tests/python/s3/test_s3.py`

**Interfaces:**
- Consumes: fixture `s3_client`, `s3_bucket`, `test_object`
- Produces: 测试函数 `test_list`

- [ ] **Step 1: 追加列举测试**

```python
def test_list(s3_client, s3_bucket, test_object):
    """先上传再列举，断言测试 key 出现在结果中"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    resp = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=key)
    keys = [obj["Key"] for obj in resp.get("Contents", [])]
    assert key in keys
```

- [ ] **Step 2: 运行测试确认通过**

Run: `pytest tests/python/s3/test_s3.py::test_list -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/python/s3/test_s3.py
git commit -m "test: 新增 S3 列举测试"
```

---

### Task 5: 下载 + 校验测试

**Files:**
- Modify: `tests/python/s3/test_s3.py`

**Interfaces:**
- Consumes: fixture `s3_client`, `s3_bucket`, `test_object`
- Produces: 测试函数 `test_download_roundtrip`

- [ ] **Step 1: 追加下载校验测试**

```python
def test_download_roundtrip(s3_client, s3_bucket, test_object):
    """上传后下载，断言内容字节完全一致"""
    key, content = test_object
    s3_client.put_object(Bucket=s3_bucket, Key=key, Body=content)
    resp = s3_client.get_object(Bucket=s3_bucket, Key=key)
    downloaded = resp["Body"].read()
    assert downloaded == content
```

- [ ] **Step 2: 运行全部测试确认通过**

Run: `pytest tests/python/s3/ -v`
Expected: 3 个测试全部 PASS，测试结束后桶中无残留临时对象

- [ ] **Step 3: Commit**

```bash
git add tests/python/s3/test_s3.py
git commit -m "test: 新增 S3 下载往返校验测试"
```
