# Import necessary libraries
from flask import Flask, jsonify, request
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
    WebSearchTool,
    OpenAIServerModel,
    tool
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
result = load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# SMTP configuration
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', '587'))
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')

# Create a tool to visit a webpage
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

# Create a tool to send an email
@tool
def send_email(email_address: str, content: str) -> bool:
    """
    Send an email to a specified email address with given content.
    
    Args:
        email_address (str): The recipient's email address
        content (str): The email content/body
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email_address
        message["Subject"] = "Today's News Letter"
        
        # Add content
        message.attach(MIMEText(content, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_address, message.as_string())
        
        return True        
    except Exception as e:
        return False

# Initialize the OpenAI model
model_id = "gpt-4.1-mini"
model = OpenAIServerModel(model_id=model_id, api_key=OPENAI_API_KEY)

# Create the newsletter agent
newsletter_agent = ToolCallingAgent(
    tools=[WebSearchTool(), visit_webpage, send_email],
    model=model,
    max_steps=5,
    name="newletter_agent",
    description="An agent that helps to create a newsletter by searching for news, visiting webpages, and sending emails.",
)

# Create the manager agent that manages agent
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[newsletter_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)

# Initialize Flask for REST APIs
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the AI Newsletter Service! Please send a POST request with your sources and emails."
    })

@app.route('/newsletter', methods=['POST'])
def newsletter():
    try:
        print(f"Received {request.method} request at {request.path}")
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate that data exists and has the expected structure
        if not data or 'sources' not in data:
            return jsonify({
                "error": "Invalid request. Expected JSON with 'sources' array."
            }), 400
        
        sources = data['sources']
        emails = data['emails']
        
        # Validate that sources is a list
        if not isinstance(sources, list):
            return jsonify({
                "error": "Sources must be an array of strings."
            }), 400
        
        # Validate that all sources are strings
        if not all(isinstance(source, str) for source in sources):
            return jsonify({
                "error": "All sources must be strings."
            }), 400
        
        # Create dynamic query based on sources
        sources_str = ", ".join(sources)
        emails_str = ", ".join(emails)
        format = """{
            "title": string,
            "summary": string,
            "url": string
        }"""
        query = f"""
        Use the newsletter_agent to get the most viewed Singapore news today from {sources_str}. 
        Format it into an array of json objects with title, summary and url.
        Use the newsletter_agent to send formatted news as a newsletter email with the title 'Today's News' to these email addresses: {emails_str}.
        Return the final output from formatted news. The format should be an array of {format}
        """

        # Run the agent with the dynamic query
        answer = manager_agent.run(query, max_steps=10)


        return answer
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # This runs the development server.
    # In a production environment, you would use a more robust server.
    app.run(debug=True)