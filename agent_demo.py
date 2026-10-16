# -*- coding: utf-8 -*-
"""
简单 AI Agent 演示代码
======================
一个从零实现的极简 Agent，包含：
  1. 记忆系统（对话历史）
  2. 工具注册与调用
  3. 思考-行动循环（ReAct 风格）
  4. 模拟 LLM 响应（无需 API Key 即可运行）

运行方式：
    python agent_demo.py
"""

from typing import Callable, Dict, List, Optional
import json
import re


# ============================================================
# 1. 工具系统：Agent 可以调用的外部能力
# ============================================================

def tool_calculator(expression: str) -> str:
    """计算器工具：计算简单的数学表达式"""
    try:
        # 安全限制：只允许数字和基本运算符
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return "错误：表达式包含非法字符"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


def tool_get_time() -> str:
    """时间工具：获取当前时间"""
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间是：{now}"


def tool_search_memory(query: str, memory: List[str]) -> str:
    """记忆检索工具：在对话历史中查找相关信息"""
    relevant = [msg for msg in memory if query.lower() in msg.lower()]
    if relevant:
        return "找到相关记忆：\n" + "\n".join(relevant[-3:])
    return "记忆中没有找到相关信息"


# 工具注册表
TOOLS: Dict[str, Callable] = {
    "calculator": tool_calculator,
    "get_time": tool_get_time,
}

TOOL_DESCRIPTIONS = """
可用工具：
- calculator(expression): 计算数学表达式，例如 calculator("2+3*4")
- get_time(): 获取当前日期和时间
"""


# ============================================================
# 2. 模拟 LLM：实际项目中替换为真实 API 调用
# ============================================================

def mock_llm(prompt: str) -> str:
    """
    模拟大语言模型的响应。
    真实场景下，这里应该调用 OpenAI / 通义千问 / 豆包等 API。
    """
    # 简单规则模拟：根据用户输入决定是否调用工具
    if any(kw in prompt for kw in ["算", "计算", "+", "-", "*", "/", "等于"]):
        # 提取数学表达式
        match = re.search(r'([\d+\-*/().\s]+)', prompt)
        if match:
            expr = match.group(1).strip()
            return f"我需要计算一下。\nAction: calculator({expr})"
    
    if "时间" in prompt or "几点" in prompt or "日期" in prompt:
        return "让我看看现在几点。\nAction: get_time()"
    
    if "你好" in prompt or "hi" in prompt.lower() or "hello" in prompt.lower():
        return "你好！我是一个简单的 AI Agent 演示。我可以帮你计算数学题、查询时间，或者和你聊天。有什么可以帮你的？"
    
    if "你是谁" in prompt or "介绍" in prompt:
        return "我是一个用 Python 从零实现的极简 AI Agent。我拥有记忆系统和工具调用能力，虽然我的'大脑'目前是用规则模拟的，但架构和真实 Agent 是一样的！"
    
    return f"你说的是'{prompt.strip()}'。这是一个模拟回复——在真实项目中，这里会调用大语言模型生成更智能的回答。"


# ============================================================
# 3. Agent 核心类
# ============================================================

class SimpleAgent:
    """
    极简 AI Agent
    
    核心循环：
        用户输入 → 构建 Prompt（含记忆+工具说明）→ LLM 思考
        → 解析是否需要调用工具 → 执行工具 → 观察结果
        → 再次思考或给出最终回答
    """
    
    def __init__(self, name: str = "小助手"):
        self.name = name
        self.memory: List[str] = []  # 对话记忆
        self.max_memory = 20  # 记忆上限
    
    def _remember(self, role: str, content: str):
        """将对话存入记忆"""
        self.memory.append(f"[{role}] {content}")
        # 超过上限时保留最近的对话
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def _build_prompt(self, user_input: str) -> str:
        """构建发送给 LLM 的完整 Prompt"""
        memory_context = "\n".join(self.memory[-6:]) if self.memory else "（暂无历史对话）"
        
        return f"""你是一个有用的 AI 助手，名字叫{self.name}。

{TOOL_DESCRIPTIONS}
如果需要使用工具，请按以下格式回复：
    Action: 工具名(参数)
如果不需要工具，直接回答用户即可。

对话历史：
{memory_context}

用户：{user_input}
助手："""
    
    def _parse_action(self, response: str) -> Optional[tuple]:
        """从 LLM 响应中解析工具调用"""
        match = re.search(r'Action:\s*(\w+)\((.*?)\)', response)
        if match:
            tool_name = match.group(1)
            tool_args = match.group(2).strip()
            return tool_name, tool_args
        return None
    
    def _execute_tool(self, tool_name: str, args: str) -> str:
        """执行工具并返回观察结果"""
        if tool_name not in TOOLS:
            return f"错误：未知工具 '{tool_name}'"
        
        tool_func = TOOLS[tool_name]
        try:
            if args:
                # 去除参数两端的引号
                args = args.strip('"').strip("'")
                result = tool_func(args)
            else:
                result = tool_func()
            return f"Observation: {result}"
        except Exception as e:
            return f"Observation: 工具执行出错 - {e}"
    
    def run(self, user_input: str) -> str:
        """
        处理用户输入，返回 Agent 的回答。
        这是 Agent 的主入口。
        """
        self._remember("用户", user_input)
        
        # 第一轮：LLM 思考
        prompt = self._build_prompt(user_input)
        response = mock_llm(prompt)
        
        # 检查是否需要调用工具
        action = self._parse_action(response)
        
        if action:
            tool_name, tool_args = action
            print(f"  🛠  调用工具: {tool_name}({tool_args})")
            
            # 执行工具
            observation = self._execute_tool(tool_name, tool_args)
            print(f"  👀 {observation}")
            
            # 第二轮：将工具结果交给 LLM，生成最终回答
            follow_up_prompt = prompt + response + "\n" + observation + "\n根据以上结果，给用户一个简洁的最终回答："
            final_answer = mock_llm(follow_up_prompt)
            
            # 去掉可能的 Action 部分，只保留自然语言
            final_answer = re.sub(r'Action:.*', '', final_answer).strip()
            if not final_answer:
                final_answer = observation.replace("Observation: ", "")
            
            self._remember("助手", final_answer)
            return final_answer
        else:
            # 不需要工具，直接回答
            self._remember("助手", response)
            return response


# ============================================================
# 4. 交互式运行
# ============================================================

def main():
    print("=" * 50)
    print("  🤖 简单 AI Agent 演示")
    print("  输入 'exit' 或 'quit' 退出")
    print("=" * 50)
    print()
    
    agent = SimpleAgent(name="小助手")
    
    # 预设演示对话
    demo_questions = [
        "你好，你是谁？",
        "帮我算一下 15 * 23 + 100 等于多少",
        "现在几点了？",
    ]
    
    print("--- 自动演示 ---")
    for q in demo_questions:
        print(f"\n👤 用户: {q}")
        answer = agent.run(q)
        print(f"🤖 助手: {answer}")
    
    print("\n" + "=" * 50)
    print("  演示结束，进入自由对话模式")
    print("=" * 50)
    
    # 自由对话
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        
        if user_input.lower() in ("exit", "quit", "退出"):
            print("再见！")
            break
        
        if not user_input:
            continue
        
        answer = agent.run(user_input)
        print(f"🤖 {agent.name}: {answer}")


if __name__ == "__main__":
    main()
