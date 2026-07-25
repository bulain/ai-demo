# S3 上传/下载测试代码设计

日期：2026-07-25

## 目标

针对一个 S3 兼容的对象存储端点，编写 pytest 测试套件，验证文件的上传、列举与下载往返（roundtrip）功能是否正常。

## 背景

给定的连接配置指向一个 S3 兼容服务（非真实 AWS）：

- `url`: `https://dify.iloglip.cn`
- `api`: `S3v4`（签名版本 s3v4）
- `path`: `auto`（路径寻址）
- 桶名：`cnn-s3-rg-dify-dev`

项目现有约定：

- 测试脚本位于 `tests/<分类>/<工具>/` 目录下
- 凭证通过 `python-decouple` 的 `config()` 从 `.env` 读取，不硬编码
- 注释使用中文

## 技术选型

- **客户端库**：`boto3`（AWS 官方 SDK，通过 `endpoint_url` + 路径寻址支持任意 S3 兼容端点，与 `S3v4` 签名匹配）
- **测试框架**：`pytest`（带断言与 fixture）

需在 `requirements.txt` 新增：`boto3`、`pytest`。

## 文件结构

- `tests/python/s3/test_s3.py` — pytest 测试套件
- `tests/python/s3/conftest.py` — fixture（boto3 客户端、测试对象数据、清理逻辑）
- `.env` — 新增 `S3_*` 配置项

### `.env` 新增内容

```
S3_ENDPOINT_URL=https://dify.iloglip.cn
S3_ACCESS_KEY=cMtwJ9Nwyo5yABYnr1X1cxs6r34rKGxy
S3_SECRET_KEY=vBqH8MxvPN7HNEVm3E7T1TZnefoQkwU24K44040h
S3_BUCKET=cnn-s3-rg-dify-dev
S3_REGION=us-east-1
```

> 注意：上述密钥已在明文中出现，使用后应尽快轮换。

## 客户端构造

关键在于适配 S3 兼容端点：

```python
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
    config=Config(
        signature_version="s3v4",              # 对应 api: S3v4
        s3={"addressing_style": "path"},       # 对应 path: auto，桶名放在 URL 路径中
    ),
)
```

`addressing_style="path"` 是必需的：让桶名出现在 URL 路径里，而不是作为自定义域名的子域名。

## 测试流程

`conftest.py` 提供：

- `s3_client` fixture — 构造并返回 boto3 客户端；连接或凭证失败时抛出异常，使测试报错并给出清晰信息
- `test_object` fixture — 生成随机 key（如 `test-<uuid>.txt`）与已知内容字节；在测试结束后（teardown）自动删除该对象

测试用例（一次完整往返）：

1. **上传** — `put_object`，断言响应 HTTP 状态码为 200
2. **列举** — `list_objects_v2` 按 key 前缀查询，断言测试 key 存在于返回结果中
3. **下载 + 校验** — `get_object`，断言下载的字节内容与上传的字节完全一致

## 清理策略

`test_object` fixture 的 teardown 阶段调用 `delete_object` 删除临时测试对象，确保桶不会被测试文件填满。真实的上传/下载/校验在删除前已全部完成并断言通过。

## 错误处理

- 客户端连接失败或凭证错误：`s3_client` fixture 抛出异常，所有依赖它的测试直接 error，信息明确指向连接问题
- 上传/下载失败：对应断言失败，pytest 报告具体的操作与期望值

## 成功标准

- `pytest tests/python/s3/` 全部通过
- 上传的对象能被列举到，下载内容与上传内容字节一致
- 测试结束后桶中不残留临时测试对象
