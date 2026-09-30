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
            "description": "Calculate total price using price and quantity.",
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


# --------------------------------------------------
# User request
# --------------------------------------------------

messages = [
    {
        "role": "user",
        "content": "Calculate the total price for 5 items costing 200 each."
    }
]


# --------------------------------------------------
# Send request to LLM
# --------------------------------------------------

response = client.chat.completions.create(
    model="openrouter/free",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)


# --------------------------------------------------
# Read LLM response
# --------------------------------------------------

assistant_message = response.choices[0].message

print("\n========== LLM RESPONSE ==========")

if assistant_message.content:
    print(assistant_message.content)


# --------------------------------------------------
# Check for tool call
# --------------------------------------------------

if assistant_message.tool_calls:

    print("\n========== TOOL CALL ==========")

    for tool_call in assistant_message.tool_calls:

        function_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        print("Function:", function_name)
        print("Arguments:", arguments)

        # --------------------------------------------------
        # Execute local function
        # --------------------------------------------------

        if function_name == "calculate_total":

            price = arguments["price"]
            quantity = arguments["quantity"]

            result = calculate_total(
                price,
                quantity
            )

            print("\n========== TOOL OUTPUT ==========")
            print("Total Price:", result)

else:

    print("\nNo tool call was generated.")