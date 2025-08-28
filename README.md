
# QuickBooks Integration with Airtable (Async Processing)

This project integrates **Airtable** and **QuickBooks Online** using FastAPI, Celery, and Redis for asynchronous processing. It allows for background processing of bill creation, enabling seamless communication between Airtable records and QuickBooks.

## Prerequisites

Before starting, ensure you have the following software installed on your local machine:

- **Python 3.7+**: Required for running the application.
- **Redis**: Used as the message broker for Celery.
- **ngrok** (optional): For exposing your local server to the internet (useful for webhooks).
- **FastAPI**: The web framework for building the API.
- **Celery**: The task/job queue system used for handling asynchronous tasks.

---

## Setup Instructions

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/yourusername/quickbooks-airtable-integration.git
cd quickbooks-airtable-integration
```

### 2. Set Up a Virtual Environment

It is recommended to use a virtual environment for Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # For MacOS/Linux
.venv\Scripts\Activate      # For Windows
```

### 3. Install Dependencies

Install the required Python packages using **pip**:

```bash
pip install -r requirements.txt
```

Ensure Redis is running locally as the broker for Celery tasks.

---

## Running the Project Locally

### Step 1: Start Redis

Start the Redis server, which will act as the message broker for Celery:

```bash
redis-server
```

You can install Redis from [here](https://redis.io/).

### Step 2: Start the Celery Worker

Run the Celery worker to process asynchronous tasks. It listens for jobs and processes them in the background:

```bash
celery -A src.app.core.celery_worker worker --loglevel=info --concurrency=1 --pool=solo
```

**Explanation of flags**:
- `-A`: Specifies the module path for Celery (`src.app.core.celery_worker`).
- `--loglevel=info`: Outputs detailed logging information.
- `--concurrency=1`: Processes one task at a time (useful in development).
- `--pool=solo`: Runs Celery in "solo" mode (ideal for development).

### Step 3: Expose Your Local FastAPI App with ngrok

To allow webhooks to communicate with your FastAPI app, expose your local server to the internet using **ngrok**:

```bash
ngrok http 8000
```

This will provide a public URL (e.g., **http://<random_string>.ngrok.io**) that can be used to test webhooks from Airtable or QuickBooks.

### Step 4: Start the FastAPI App

Run the FastAPI development server using **uvicorn**:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

**Explanation of flags**:
- `--reload`: Enables auto-reloading of the server on code changes.
- `--host 0.0.0.0`: Makes the app available on all network interfaces (for local testing).
- `--port 8000`: Runs the server on port 8000.

### Step 5: Verify the Setup

Access the FastAPI documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

The webhook endpoint (`/bills/webhook`) will be available for receiving requests from Airtable.

Tasks will be processed in the background by Celery and Redis.

---

## Environment Variables

Ensure to set the following environment variables before running the app:

- `REDIS_URL`: URL to connect to your Redis instance.
- `QBO_CLIENT_ID`: Your QuickBooks Online client ID.
- `QBO_CLIENT_SECRET`: Your QuickBooks Online client secret.
- `QBO_REDIRECT_URI`: The redirect URI for OAuth authentication.
- `AIRTABLE_API_KEY`: Your Airtable API key.
- `AIRTABLE_BASE_ID`: The base ID for your Airtable table.

---

## Testing

For testing purposes, the system allows you to:

1. Update an Airtable record to trigger a webhook.
2. Ensure the webhook sends the correct data to the FastAPI server.
3. The FastAPI server processes the data, adds it to the queue, and uses Celery to create a bill in QuickBooks Online.

---

## Troubleshooting

- **Redis connection error**: Ensure Redis is running locally or on your cloud provider. Check the `REDIS_URL` environment variable.
- **Celery task not running**: Ensure the Celery worker is running and that there are no issues with the task queue configuration.
- **Webhook issues**: Ensure the webhook URL is correctly configured in Airtable and that ngrok is exposing the FastAPI app.

---
