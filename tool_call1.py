from together import Together
import json
import requests

# Initialize TogetherAI API Key
client = Together(api_key="together-api-key")

# Define a mock tool: Fetching weather info
def get_weather(city):
    """Fetches weather information for a city."""
    # response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=YOUR_WEATHER_API_KEY&q={city}")
    # data = response.json()
    data = {'current': {'temp_c': 20, 'condition': {'text': 'sunny'}}}
    print('data', data)
    return f"The weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."

def calculate_sum(a, b):
    return a + b

def calculate_multiply(a, b):
    return a * b

# Define tools as function mappings
TOOLS = {
    "get_weather": get_weather,
    "calculate_sum": calculate_sum,
    "calculate_multiply": calculate_multiply
}


prompt_1 = """
You are an AI assistant that can use external tools when needed.

Don't make up tool calls. Just ignore them. Only use the ones that are provided in the examples. 
If you see one tool call, return a JSON formatted tool call as follows:

Example:
User: What’s the weather like in New York?
Response: {"tool": "get_weather", "parameters": {"city": "New York"}}

User: What’s the sum of 1 and 2?
Response: {"tool": "calculate_sum", "parameters": {"a": 1, "b": 2}}

User: What’s the product of 2 and 3?
Response: {"tool": "calculate_multiply", "parameters": {"a": 2, "b": 3}}

User: What's the product of iPhone and 22?
Response: {"tool": "calculate_multiply", "error": "Invalid input"}

If you see multiple tool calls, combine individual tool calls to a JSON formatted list of tool calls as follows: 

Example:
User: What's the weather like in Tokyo? What's the sum of 1 and 20?
Response: [{"tool": "get_weather", "parameters": {"city": "Tokyo"}}, {"tool": "calculate_sum", "parameters": {"a": 1, "b": 20}}]

Now, process this request:
User: What’s the weather like in Shimla? What is the division of 11 and 21?
"""

prompt_2 = """
You are an AI assistant that can use external tools when needed.

If you see one tool call, return a JSON formatted tool call. 
If you see multiple tool calls, combine individual tool calls to a JSON formatted list of tool calls.
Don't make up tool calls. Just ignore them. Only use the ones that are provided in the examples below:

Example:
User: What’s the weather like in New York?
Response: {"tool": "get_weather", "parameters": {"city": "New York"}}

User: What’s the sum of 1 and 2?
Response: {"tool": "calculate_sum", "parameters": {"a": 1, "b": 2}}

User: What’s the product of 2 and 3?
Response: {"tool": "calculate_multiply", "parameters": {"a": 2, "b": 3}}

User: What's the product of iPhone and 22?
Response: {"tool": "calculate_multiply", "error": "Invalid input"}

User: What's the weather like in Tokyo? What's the sum of 1 and 20?
Response: [{"tool": "get_weather", "parameters": {"city": "Tokyo"}}, {"tool": "calculate_sum", "parameters": {"a": 1, "b": 20}}]

Now, process this request:
User: What’s the weather like in Shimla? What is the division of 11 and 21?
"""

prompt_3 = """
You are an AI assistant that can use external tools when needed.

You have the following tools available:

"get_weather": Fetches weather information for a city.
"calculate_sum": Calculates the sum of two numbers.
"calculate_multiply": Calculates the product of two numbers.

Don't make up tool calls. Return error message if the tool is not available.

If you see one tool call, return a JSON formatted tool call. 
If you see multiple tool calls, combine individual tool calls to a JSON formatted list of tool calls.

Example:
User: What’s the weather like in New York?
Response: {"tool": "get_weather", "parameters": {"city": "New York"}}

User: What’s the sum of 1 and 2?
Response: {"tool": "calculate_sum", "parameters": {"a": 1, "b": 2}}

User: What’s the capital of France?
Response: {"question": "What's the capital of France?", "error": "tool not available"}

User: What’s the product of 2 and 3?
Response: {"tool": "calculate_multiply", "parameters": {"a": 2, "b": 3}}

User: What's the product of iPhone and 22?
Response: {"tool": "calculate_multiply", "error": "Invalid input"}

User: What's the weather like in Tokyo? What's the sum of 1 and 20?
Response: [{"tool": "get_weather", "parameters": {"city": "Tokyo"}}, {"tool": "calculate_sum", "parameters": {"a": 1, "b": 20}}]

User: What's the weather like in Paris? What's the sum of 11 and 20?
Response: [{"tool": "get_weather", "parameters": {"city": "Paris"}}, {"tool": "calculate_sum", "parameters": {"a": 11, "b": 20}}]

Now, process this request:
User: What’s the weather like in Shimla? What is the product of 11 and 21?
"""


llama_8b = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"
llama_70b = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"

response = client.chat.completions.create(
    model=llama_8b,
    messages=[{"role": "user", "content": prompt_3}],
    # prompt=prompt,
    temperature=0.5,
    max_tokens=150,
    top_p=0.9,
)

# print(response)

# Parse LLaMA's structured tool request
answers = response.choices[0].message.content
print(answers)

def call_tool(tool_name, parameters):
        # Call the correct tool
        if tool_name in TOOLS:
            result = TOOLS[tool_name](**parameters)
            print("Tool Response:", result)
        else:
            print("No valid tool call detected.")

def post_process_8b(answers_list):
    for answer in answers_list:
        try:
            tool_call = json.loads(answer)
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            call_tool(tool_name, parameters)
        except Exception as e:
            print(f"Error processing answer: {e}")

def post_process_70b(answers_json):
    for tool_call in answers_json:
        tool_name = tool_call.get("tool")
        parameters = tool_call.get("parameters", {})
        call_tool(tool_name, parameters)

# uncomment for 8b
# returns a list of tools calls separated by new lines. 
# Some times it may return a list of tool calls separated by comma. In that case, just rerun the code.
answers_list = answers.split('\n')
post_process_8b(answers_list)

# uncomment for 70b
# returns a JSON formatted list of tool calls.
# answers_json = json.loads(answers)
# post_process_70b(answers_json)
