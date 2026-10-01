import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env file"
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


def calculate_total(price, quantity):
    """
    Calculate total price.
    """
    return price * quantity


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_total",
            "description": "Calculate the total price using price and quantity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "description": "Price of one item"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items"
                    }
                },
                "required": ["price", "quantity"]
            }
        }
    }
]


# -----------------------------------
# User Request
# -----------------------------------

messages = [
    {
        "role": "user",
        "content": "I bought 2 items and each item costs 500. Calculate the total."
    }
]


# -----------------------------------
# DAY 31
# Send Tool Definition to LLM
# -----------------------------------

response = client.chat.completions.create(
    model="openrouter/free",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

message = response.choices[0].message


print("========== DAY 31 ==========")

print("\nLLM Tool Call:")

if not message.tool_calls:
    print(message.content)
    exit()

tool_call = message.tool_calls[0]

print("Tool Name:", tool_call.function.name)
print("Arguments:", tool_call.function.arguments)


# -----------------------------------
# DAY 32
# Tool Execution Router
# -----------------------------------

def execute_tool(tool_call):

    tool_name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments
    )

    print("\n========== DAY 32 ==========")

    print("Executing Tool:", tool_name)
    print("Arguments:", arguments)

    # Route to correct local function
    if tool_name == "calculate_total":

        result = calculate_total(
            arguments["price"],
            arguments["quantity"]
        )

        return result

    else:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )


# -----------------------------------
# DAY 32
# Execute Tool
# -----------------------------------

tool_result = execute_tool(tool_call)

print("Tool Result:", tool_result)


# -----------------------------------
# DAY 32
# Send Tool Result Back to LLM
# -----------------------------------

messages.append(message)

messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(tool_result)
    }
)


# -----------------------------------
# Get Final LLM Response
# -----------------------------------

final_response = client.chat.completions.create(
    model="openrouter/free",
    messages=messages
)

final_message = final_response.choices[0].message


print("\n========== FINAL RESPONSE ==========")
print(final_message.content)