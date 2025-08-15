# Group Project: Agentic AI

Idea: Top News of the day

- Description: Agentic AI that gathers the top headlines from online specified news sources, prioritieses the most popular (by views), summarises them. Additionally, sends the summary to a specified email.

Software Components:

- Tools:
  - Visit Webpage (To get news)
  - Send Email (To send summary)
- Agent:
  - Newsletter Agent (Uses above tools to get, sumamrise, then send the news)
- Manager:
  - Manager Agent: Manages the above agent

# Quickstart

## Frontend Application


1. Navigate into the frontend folder and install node modules
``` bash
cd ai-frontend
npm install
```

2. Start up development server
``` bash
 npm run dev
```

3. Navigate to landing page
go to "http://localhost:5173"

## Python Backend Application

1. Prepare the env file from `.env.template`
2. Install all the dependencies by running

```bash
pip install -r requirements.txt
```

3. Run the application

```bash
python app.py
```

4. By default, the application will be running at `localhost:5000`
5. Generate today news letter by calling the API at

```
curl --location 'http://localhost:5000/newsletter' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sources": ["reddit"],
    "emails": ["someone@email.com"]
}'
```
