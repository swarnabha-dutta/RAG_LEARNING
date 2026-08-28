import os

from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from groq import Groq
import re


load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API KEY WAS NOT FOUND!!")


client = Groq(api_key=my_api_key)

model = "openai/gpt-oss-120b"


def get_product_price(product):

    if product == "iPhone 17":
        return 1000

    elif product == "iPhone 15":
        return 500

    else:
        return 0


def calculator(expression):

    try:
        return eval(expression)

    except:
        return "calc error!"


tools = {
    "get_product_price": get_product_price,
    "calculator": calculator
}


system_prompt = """

# ROLE:

You are a shopping assistant.


# TASK:

You have to decide what action to take to complete the user's
shopping-related task.


You have access to these tools:

get_product_price(product)

calculator(expression)


# CONSTRAINT:

You must follow these rules:

1. Decide what you need to do next.

2. Call ONLY ONE tool at a time.

3. After writing an Action, STOP immediately.

4. Never guess or invent a tool result.

5. Wait until you receive an Observation.

6. After receiving an Observation, decide your next action.

7. When the task is complete, provide the Final Answer.

8. Whenever arithmetic or numerical calculation is required,
you MUST use the calculator tool.

Tool calls must follow the exact format shown below.


# OUTPUT FORMAT:

When you need to use a tool, output:

Thought: what you need to do

Action: tool_name(argument)


When the task is complete, output:

Final Answer: your answer


# EXAMPLE:

For example:

Action: get_product_price("iPhone 17")

Action: calculator("5000 - 1000")


Never write:

get_product_price(product="iPhone 17")


Never write:

calculator(expression="5000 - 1000")


After writing an Action, STOP immediately and wait for the Observation.

Never invent or assume the result of a tool call.


# FALLBACK:

If no tool is required, directly provide the Final Answer.

If a tool is required, use ONLY ONE tool at a time and wait for
the Observation before taking the next action.


This is a user constraint:

The assistant should act as a shopping assistant and use the
available tools only when necessary.

"""


def run_agent(question):

    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": question
        }

    ]


    for step in range(5):

        print("\n------------------------")
        print("STEP", step + 1)
        print("--------------------------")


        response = client.chat.completions.create(

            model=model,
            messages=messages,
            temperature=0

        )


        answer = response.choices[0].message.content

        print(answer)


        # Agent has finished work

        if "Final Answer:" in answer:
            break


        # Find the Action

        match = re.search(

            r"Action:\s*(\w+)\((.*?)\)",

            answer

        )


        if match:

            tool_name = match.group(1)

            tool_input = match.group(2)

            tool_input = tool_input.strip()

            tool_input = tool_input.strip('"')


            # Run the tool

            if tool_name in tools:

                tool = tools[tool_name]

                observation = tool(tool_input)

            else:

                observation = "Tool not found"


            print(
                "Observation:",
                observation
            )


            # Add LLM response to memory

            messages.append({

                "role": "assistant",

                "content": answer

            })


            # Give tool result back to LLM

            messages.append({

                "role": "user",

                "content":
                    "Observation: "
                    + str(observation)

            })


            sleep(5)


prompt = """

I have 50000 rupees. What is the price of an iphone 17?

and how much money will I have left?

"""


run_agent(prompt)