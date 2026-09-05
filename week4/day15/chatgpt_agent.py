
# ============================================================
# STEP 1: IMPORTS AND ENVIRONMENT
# ============================================================

import os
import ast
import json
import operator
import re
import time
from typing import Any

from dotenv import load_dotenv
from groq import Groq

# These imports are kept because they are part of your project stack.
# They are not required by this 2-tool agent yet.
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    PayloadSchemaType,
)
from sentence_transformers import SentenceTransformer

# Load variables from .env
load_dotenv()


# ============================================================
# STEP 2: CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TRAVILY_API_KEY = os.getenv("TRAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in your .env file.")

if not TRAVILY_API_KEY:
    raise ValueError("TRAVILY_API_KEY is missing in your .env file.")

# Current Groq models supporting local tool/function calling can be
# changed independently through the environment.
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Maximum number of agent iterations.
# One iteration = one LLM decision + possible tool execution.
MAX_ITERATIONS = 5

# Minimum time between external API calls.
# This is intentionally simple and uses time.sleep(), as requested.
MIN_REQUEST_INTERVAL = 1.0


# ============================================================
# STEP 3: CLIENTS
# ============================================================

groq_client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# STEP 4: SIMPLE RATE LIMITER
# ============================================================

class RateLimiter:
    """
    Very small rate limiter.

    Before every external API request, wait until at least
    MIN_REQUEST_INTERVAL seconds have passed since the previous request.
    """

    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_request_time = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.monotonic()


rate_limiter = RateLimiter(MIN_REQUEST_INTERVAL)


# ============================================================
# STEP 5: SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a research assistant and mathematical computation assistant.

You have exactly two tools:

1. web_search
   Use this tool whenever the user needs:
   - current or updated information
   - recent facts
   - news or reports
   - statistics that may change over time
   - information about a particular person, company, product, event, etc.
   - an unknown word, term, concept, or meaning that may require web research
   - any other information that should be verified from the web

2. calculator
   - Use this tool whenever the user asks you to perform arithmetic.
   - This includes basic, intermediate, and medium/advanced arithmetic
   - involving integers, decimals, percentages when expressible as arithmetic,
   - parentheses, powers, division, modulo, and multiple numbers.

IMPORTANT RULES:
- Do not hallucinate facts.
- If a tool is needed, use the appropriate tool instead of guessing.
- For arithmetic, do not calculate the result mentally; use calculator.
- For current/updated information, do not answer from memory; use web_search.
- Use only the information relevant to the user's request.
- After receiving sufficient tool results, answer the user directly.
- Do not call a tool again unless another tool call is genuinely necessary.
- If web search does not provide enough reliable information, say so rather
  than inventing an answer.
- Keep the final answer clear and concise.
"""


# ============================================================
# STEP 6: TOOL DEFINITIONS / JSON SCHEMAS
# ============================================================

# These schemas are sent to Groq so the model knows:
# - what tools exist
# - when they should be used
# - what arguments each tool accepts

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web using Tavily. Use this for current or updated "
                "information, recent facts, news, reports, statistics, "
                "information about people/companies/events/products, or "
                "unknown terms/meanings that require web verification."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A clear natural-language search query. "
                            "Include the important topic, person, event, "
                            "date, or other context needed to answer the user."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Perform safe arithmetic calculations. The input is always a "
                "string and may contain natural language around the expression. "
                "Extract and evaluate the arithmetic expression. Supports "
                "+, -, *, /, //, %, **, ^, parentheses, integers and decimals."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The user's arithmetic request as a string. "
                            "Example: '432432 * 386786 + 23234'."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# ============================================================
# STEP 7: TAVILY WEB SEARCH TOOL
# ============================================================

def web_search(query: str) -> str:
    """
    Search Tavily using its REST API.

    We intentionally use Python's standard library here, so you do not
    need to install an additional Tavily package.

    Tavily endpoint:
        https://api.tavily.com/search
    """

    if not isinstance(query, str) or not query.strip():
        return "Web search error: query must be a non-empty string."

    # Import only here because the rest of the agent does not need urllib.
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    rate_limiter.wait()

    payload = {
        "query": query.strip(),
        "search_depth": "basic",
        "topic": "general",
        "max_results": 5,
        "include_answer": "advanced",
        "include_raw_content": False,
        "include_images": False,
    }

    request = Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TRAVILY_API_KEY}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

    except HTTPError as exc:
        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            error_body = str(exc)

        return f"Web search failed with HTTP {exc.code}: {error_body}"

    except URLError as exc:
        return f"Web search failed because of a network error: {exc.reason}"

    except Exception as exc:
        return f"Web search failed: {exc}"

    # Keep the result reasonably small before sending it back to the LLM.
    # The model mainly needs the synthesized answer + useful source snippets.
    answer = data.get("answer") or ""

    results = []
    for item in data.get("results", [])[:5]:
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
        )

    result = {
        "query": data.get("query", query),
        "answer": answer,
        "sources": results,
    }

    return json.dumps(result, ensure_ascii=False)


# ============================================================
# STEP 8: SAFE CALCULATOR
# ============================================================

# Allowed operators for the AST-based calculator.
# We deliberately DO NOT use eval().
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> int | float:
    """Recursively evaluate only approved arithmetic AST nodes."""

    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(
            node.value, (int, float)
        ):
            raise ValueError("Only numeric values are allowed.")
        return node.value

    if isinstance(node, ast.BinOp):
        operator_function = BINARY_OPERATORS.get(type(node.op))

        if operator_function is None:
            raise ValueError("Unsupported arithmetic operator.")

        left = _safe_eval(node.left)
        right = _safe_eval(node.right)

        # Prevent unnecessarily huge exponent calculations.
        if isinstance(node.op, ast.Pow):
            if abs(right) > 100:
                raise ValueError("Exponent is too large. Maximum allowed is 100.")

        return operator_function(left, right)

    if isinstance(node, ast.UnaryOp):
        operator_function = UNARY_OPERATORS.get(type(node.op))

        if operator_function is None:
            raise ValueError("Unsupported unary operator.")

        return operator_function(_safe_eval(node.operand))

    raise ValueError("Only arithmetic expressions are allowed.")


def _normalise_math_words(text: str) -> str:
    """
    Convert common natural-language math words into symbols.

    Example:
        "432 plus 20 times 3"
    becomes:
        "432 + 20 * 3"
    """

    text = text.lower()

    replacements = [
        (r"\bmultiplied\s+by\b", "*"),
        (r"\bmultiply\s+by\b", "*"),
        (r"\btimes\b", "*"),
        (r"\bdivided\s+by\b", "/"),
        (r"\bdivide\s+by\b", "/"),
        (r"\bplus\b", "+"),
        (r"\bminus\b", "-"),
        (r"\bmodulo\b", "%"),
        (r"\bmod\b", "%"),
        (r"\bpower\s+of\b", "**"),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    # Remove thousands separators:
    # 432,432 -> 432432
    text = re.sub(r"(?<=\d),(?=\d)", "", text)

    return text


def _extract_expression(query: str) -> str:
    """
    Extract an arithmetic expression from a natural-language query.

    Example:
        "what is the answer of 432432 * 386786 + 23234?"
    ->    "432432 * 386786 + 23234"
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Calculator query must be a non-empty string.")

    query = _normalise_math_words(query)

    # Look for a sequence beginning with a number and containing
    # arithmetic characters.
    matches = re.findall(
        r"[0-9]+(?:\.[0-9]+)?(?:\s*(?:\+|-|\*{1,2}|/|//|%|\^|\(|\))\s*"
        r"[0-9]+(?:\.[0-9]+)?)*",
        query,
    )

    if not matches:
        raise ValueError(
            "Could not find a valid arithmetic expression in the query."
        )

    # Usually the longest match is the actual calculation.
    expression = max(matches, key=len).strip()

    # Convert ^ into Python's exponent operator.
    expression = expression.replace("^", "**")

    return expression


def calculator(query: str) -> str:
    """
    Safely calculate an arithmetic expression extracted from a string.

    Example:
        calculator(
            "what is the answer of 432432 * 386786 + 23234?"
        )
    """

    try:
        expression = _extract_expression(query)

        # Avoid unnecessarily large expressions.
        if len(expression) > 500:
            raise ValueError("Arithmetic expression is too long.")

        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)

        # Clean up -0.0
        if result == 0:
            result = 0

        return json.dumps(
            {
                "expression": expression,
                "result": result,
            },
            ensure_ascii=False,
        )

    except Exception as exc:
        return json.dumps(
            {
                "error": str(exc),
            },
            ensure_ascii=False,
        )


# ============================================================
# STEP 9: TOOL ROUTER
# ============================================================

def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """
    Route the model's requested tool call to the correct Python function.
    """

    if tool_name == "web_search":
        return web_search(arguments.get("query", ""))

    if tool_name == "calculator":
        return calculator(arguments.get("query", ""))

    return json.dumps(
        {
            "error": f"Unknown tool requested: {tool_name}"
        }
    )


# ============================================================
# STEP 10: AGENT LOOP
# ============================================================

def run_agent(user_query: str) -> str:
    """
    Run the agent.

    Flow:
        User
          ↓
        Groq LLM
          ↓
        Tool call?
        /      \
      Yes       No
       ↓         ↓
    Execute    Final answer
       ↓
    Send result back to LLM
       ↓
    Repeat (maximum 5 iterations)
    """

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n[Agent iteration {iteration}/{MAX_ITERATIONS}]")

        # Rate-limit Groq API calls as well.
        rate_limiter.wait()

        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0,
            max_completion_tokens=2048,
        )

        message = response.choices[0].message

        # If the model does not request a tool, we have our final answer.
        if not message.tool_calls:
            return message.content or "I could not generate an answer."

        # Save the assistant tool-call message in the conversation.
        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ],
            }
        )

        # Execute every tool call requested by the model.
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            print(f"[Tool selected] {tool_name}")
            print(f"[Tool arguments] {arguments}")

            tool_result = execute_tool(tool_name, arguments)

            # Send the tool result back to Groq.
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result,
                }
            )

    # Safety fallback if the model keeps requesting tools for all 5 iterations.
    return (
        "I reached the maximum of 5 agent iterations before a final answer "
        "could be produced."
    )


# ============================================================
# STEP 11: SIMPLE CLI
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Groq AI Agent")
    print("Tools: web_search + calculator")
    print(f"Model: {MODEL}")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            if not user_input:
                continue

            answer = run_agent(user_input)

            print(f"\nAgent: {answer}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        except Exception as exc:
            print(f"\nAgent error: {exc}")
