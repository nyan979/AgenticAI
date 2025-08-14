from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import re
import requests
from markdownify import markdownify
from requests.exceptions import RequestException
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    InferenceClientModel,
    WebSearchTool,
    LiteLLMModel,
    OpenAIServerModel,
    tool
)


result = load_dotenv()
print(result)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(OPENAI_API_KEY)

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

model_id = "gpt-4.1-mini"

model = OpenAIServerModel(model_id=model_id, api_key=OPENAI_API_KEY)

web_agent = ToolCallingAgent(
    tools=[WebSearchTool(), visit_webpage],
    model=model,
    max_steps=10,
    name="web_search_agent",
    description="Runs web searches for you.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)




app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    answer = manager_agent.run("Get the most viewed Singapore news today from Straits Times and Reddit. Format it into an array of json object with the its title and summary", max_steps=5)
    print(f"my answer is {answer}")
    return answer

if __name__ == '__main__':
    # This runs the development server.
    # In a production environment, you would use a more robust server.
    app.run(debug=True)