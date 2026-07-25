# ai demo

一个学习 / 验证性质的 Python 示例仓库，收集了 LLM、LangChain、LlamaIndex、Agent 框架、MCP、FastAPI、S3 等技术的独立可运行脚本与测试。每个子目录是一个自包含的主题，脚本之间基本无相互依赖，可按需单独运行。

## 环境准备

```bash
# 建议使用 conda ai 环境
pip install -r requirements.txt
```

配置通过 `.env` + [python-decouple](https://github.com/HBNetwork/python-decouple) 读取，需在仓库根目录创建 `.env`：

```dotenv
# DeepSeek（OpenAI 兼容）
DS_BASE_URL=https://api.deepseek.com
DS_API_KEY=your_api_key

# S3 兼容对象存储
S3_ENDPOINT_URL=https://your-s3-endpoint
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET=your_bucket
S3_REGION=us-east-1
```

> 运行 pytest / python 时请带上 `PYTHONNOUSERSITE=1` 并使用 conda `ai` 环境的解释器，避免 user-site 旧包污染环境。

## 运行

```bash
# 运行全部 pytest 用例
PYTHONNOUSERSITE=1 python -m pytest

# 运行单个测试文件 / 单个用例
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py
PYTHONNOUSERSITE=1 python -m pytest tests/python/s3/test_s3.py::test_download_roundtrip

# 直接跑某个示例脚本
PYTHONNOUSERSITE=1 python tests/llm/deepseek/deepseek-chat.py
```

> 说明：`tests/**` 下绝大多数 `.py` 是**演示脚本**（顶层执行、`print` 输出），并非 pytest 用例；真正的 pytest 用例目前位于 `tests/python/s3/`。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `tests/llm/deepseek/` | 直接用 `openai` SDK 调 DeepSeek（chat / reasoner / prompt / chain） |
| `tests/langchain/` | LangChain：prompt、loader（pdf/csv/docx/web…）、vector(chroma)、embed、rerank、ollama、database、langserve 服务/客户端 |
| `tests/llamaindex/deepseek/` | LlamaIndex basic / chat / rag |
| `tests/agent/` | AutoGen、Swarm、DSPy 等多智能体框架示例 |
| `tests/python/fastapi/` | FastAPI 示例 |
| `tests/python/mcp/` | MCP server / client / demo |
| `tests/python/s3/` | boto3 对 S3 兼容端点的 pytest 测试 |

## 主要依赖

Python 3.x，核心依赖见 [`requirements.txt`](requirements.txt)：langchain、langgraph、langserve、llama-index、openai、autogen-agentchat、swarm、chromadb、fastapi、boto3、pytest 等。

## License

见 [LICENSE](LICENSE)。
