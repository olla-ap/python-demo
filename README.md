# python-demo

Python AI Agent 演示代码 —— 一个从零实现的极简对话式 Agent 示例。

## 功能特性

- **记忆系统**：保存对话历史，支持上下文理解
- **工具调用**：内置计算器、时间查询等工具，Agent 可自主决定调用
- **ReAct 循环**：思考（Thought）→ 行动（Action）→ 观察（Observation）→ 回答
- **零依赖运行**：使用模拟 LLM，无需 API Key 即可直接运行

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/olla-ap/python-demo.git
cd python-demo

# 运行演示（无需安装任何依赖）
python agent_demo.py
```

## 代码结构

```
agent_demo.py
├── 工具系统        # calculator / get_time 等可调用工具
├── 模拟 LLM        # mock_llm()，可替换为真实 API
├── SimpleAgent 类  # Agent 核心：记忆、Prompt 构建、工具解析与执行
└── main()          # 交互式运行入口
```

## 扩展方向

将 `mock_llm()` 替换为真实大模型 API 调用（如豆包、OpenAI、通义千问），即可成为一个真正可用的 AI Agent。

## 许可证

MIT License
