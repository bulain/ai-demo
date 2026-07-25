# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

`ai demo` —— 一个学习/验证性质的 Python 示例仓库，收集了 LLM、LangChain、LlamaIndex、
Agent 框架（AutoGen/Swarm/DSPy）、MCP、FastAPI、S3 等技术的独立可运行脚本与测试。
每个子目录是一个自包含的主题，脚本之间基本无相互依赖。

## 环境与运行

- 依赖统一在 `requirements.txt`，无 `pyproject.toml`/`setup.py`。安装：`pip install -r requirements.txt`
- 配置通过 `.env` + `python-decouple` 读取（`from decouple import config`）。
  关键变量：`DS_BASE_URL` / `DS_API_KEY`（DeepSeek，OpenAI 兼容），
  `S3_ENDPOINT_URL` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` / `S3_BUCKET` / `S3_REGION`。
- **运行 pytest / python 时务必带 `PYTHONNOUSERSITE=1` 并使用 conda `ai` 环境的解释器**，
  否则 user-site 的旧包会污染环境导致导入/版本错误。

### 常用命令

```bash
# 运行全部测试
PYTHONNOUSERSITE=1 python -m pytest

# 运行单个测试文件 / 单个用例
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py::test_download_roundtrip

# 直接跑某个示例脚本
PYTHONNOUSERSITE=1 python tests/llm/deepseek/deepseek-chat.py
```

注意：绝大多数 `tests/**/*.py` 是**演示脚本**（顶层执行、`print` 输出），并非 pytest 用例。
真正的 pytest 用例目前只有 `tests/python/s3/`（含 `conftest.py` + `test_*.py`）。

## 目录结构（按主题）

- `tests/llm/deepseek/` —— 直接用 `openai` SDK 调 DeepSeek（chat/reasoner/prompt/chain）
- `tests/langchain/` —— LangChain：prompt、loader（pdf/csv/docx/web…）、vector(chroma)、
  embed、rerank、ollama、database、langserve 服务/客户端
- `tests/llamaindex/deepseek/` —— LlamaIndex basic/chat/rag
- `tests/agent/` —— AutoGen、Swarm、DSPy 等多智能体框架示例
- `tests/python/fastapi/` —— FastAPI 示例；`tests/python/mcp/` —— MCP server/client/demo
- `tests/python/s3/` —— boto3 对 S3 兼容端点的 pytest 测试

## S3 测试的关键约定（易踩坑）

`tests/python/s3/conftest.py` 针对 **nginx 反代的 S3 兼容端点**做了特殊适配：

- 客户端固定 `signature_version="s3v4"` + `addressing_style="path"`。
- bucket 级操作（如 `ListObjectsV2`）访问 `/bucket` 会被 nginx 301 到 `/bucket/`，
  但 SigV4 已对无斜杠路径签名无法跟随重定向，且 botocore 会把 301 误判为区域重定向导致无限递归。
  解决办法是注册 `before-sign.s3.ListObjectsV2` 钩子（`_add_trailing_slash`）在**签名前**补尾斜杠。
- `test_object` fixture 生成的 key 格式为 `g01/YYMMDD/<uuid>.png`，测试结束自动删除以保持桶干净。
