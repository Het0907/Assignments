# Technical Write-Up: Rx Details Extractor

> **Comprehensive Technical Documentation for Developers and Architects**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [API Design](#api-design)
7. [Task Processing (Celery)](#task-processing-celery)
8. [LLM Integration](#llm-integration)
9. [Database Schema](#database-schema)
10. [Authentication & Security](#authentication--security)
11. [Logging & Observability](#logging--observability)
12. [Error Handling](#error-handling)
13. [Configuration Management](#configuration-management)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              RX DETAILS EXTRACTOR ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐                │
│   │   Client     │  HTTP   │   FastAPI    │  AMQP   │   RabbitMQ   │                │
│   │  Application │ ──────► │   Backend    │ ──────► │   Broker     │                │
│   └──────────────┘         └──────────────┘         └──────────────┘                │
│                                   │                        │                         │
│                                   │                        ▼                         │
│                                   │                 ┌──────────────┐                │
│                                   │                 │   Celery     │                │
│                                   │                 │   Workers    │                │
│                                   │                 │ (Extraction) │                │
│                                   │                 └──────────────┘                │
│                                   │                        │                         │
│                                   ▼                        ▼                         │
│                            ┌──────────────┐         ┌──────────────┐                │
│                            │   MongoDB    │         │   Google     │                │
│                            │  (Jobs DB)   │         │   Gemini AI  │                │
│                            └──────────────┘         └──────────────┘                │
│                                   │                        │                         │
│                            ┌──────────────┐         ┌──────────────┐                │
│                            │   Google     │◄────────│   LangChain  │                │
│                            │Cloud Storage │         │  Integration │                │
│                            └──────────────┘         └──────────────┘                │
│                                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────────────┐  │
│   │                           OBSERVABILITY STACK                                 │  │
│   │  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐        │  │
│   │  │  Structlog │───►│  Promtail  │───►│    Loki    │───►│  Grafana   │        │  │
│   │  └────────────┘    └────────────┘    └────────────┘    └────────────┘        │  │
│   │                                                         ┌────────────┐        │  │
│   │                                              ◄──────────│ Prometheus │        │  │
│   │                                                         └────────────┘        │  │
│   └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Framework** | FastAPI | Async REST API with automatic OpenAPI docs |
| **Task Queue** | Celery | Distributed task processing |
| **Message Broker** | RabbitMQ | AMQP message broker for Celery |
| **Database** | MongoDB | Document storage for jobs and results |
| **File Storage** | Google Cloud Storage | PDF file storage with lifecycle management |
| **AI/LLM** | Google Gemini 3.1 Pro | Document understanding and extraction |
| **LLM Framework** | LangChain | LLM orchestration and prompt management |
| **Logging** | Structlog | Structured JSON logging |
| **Log Aggregation** | Loki + Promtail | Centralized log collection |
| **Visualization** | Grafana | Dashboards and log exploration |
| **Metrics** | Prometheus | Application metrics collection |
| **Authentication** | JWT (RS256) | Token-based API authentication |

---

## Project Structure

```
rx-details-extractor/
├── backend/
│   ├── app/
│   │   ├── core/                    # Configuration and constants
│   │   │   ├── configs/             # Environment-based configs
│   │   │   │   ├── celery.py        # Celery configuration
│   │   │   │   ├── config.py        # General app config
│   │   │   │   ├── gemini.py        # Gemini LLM config
│   │   │   │   └── mongo.py         # MongoDB config
│   │   │   ├── constants.py         # Enums (StatusLevels, QueueNames)
│   │   │   └── google_project_hermes.json  # GCP service account
│   │   │
│   │   ├── models/                  # Data models
│   │   │   ├── pydantic/            # Request/Response schemas
│   │   │   │   ├── request.py       # InputParams model
│   │   │   │   └── response.py      # AnswerResponse, StatusResponse
│   │   │   └── database/            # MongoDB schemas
│   │   │       └── mongo_schema.py  # DocumentRequest model
│   │   │
│   │   ├── routers/                 # API endpoints
│   │   │   └── route.py             # /extract, /status, /results
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── bucket/              # GCS file operations
│   │   │   │   └── bucket_service.py
│   │   │   ├── celery/              # Celery app management
│   │   │   │   └── celery_service.py
│   │   │   ├── database/            # MongoDB operations
│   │   │   │   └── mongo_service.py
│   │   │   ├── fax_route/           # Document processing bot
│   │   │   │   └── bot.py
│   │   │   └── llm/                 # LLM interaction
│   │   │       └── llm_services.py
│   │   │
│   │   ├── tasks/                   # Celery tasks
│   │   │   └── tasks.py             # process_document_task, batch_completed_task
│   │   │
│   │   ├── prompts/                 # LLM prompts
│   │   │   └── prompt.py            # Extraction prompt template
│   │   │
│   │   ├── structured_logging/      # Logging infrastructure
│   │   │   ├── config.py            # Structlog configuration
│   │   │   ├── logger.py            # AppLogger class
│   │   │   └── log_factory.py       # Logger factory singleton
│   │   │
│   │   ├── utils/                   # Utility functions
│   │   │   ├── auth_utils.py        # JWT validation
│   │   │   ├── file_utils.py        # File operations
│   │   │   └── json_utils.py        # JSON coercion
│   │   │
│   │   └── main.py                  # FastAPI application entry
│   │
│   ├── .env                         # Environment variables
│   └── requirements.txt             # Python dependencies
│
├── deployment/
│   ├── docker-compose.yml           # Full stack deployment
│   ├── services/                    # Systemd service files
│   │   ├── rx-detail-extractor.service
│   │   ├── rx-main-celery.service
│   │   └── rx-callback-celery.service
│   ├── loki-config.yaml             # Loki configuration
│   ├── promtail-config.yaml         # Promtail configuration
│   └── prometheus.yml               # Prometheus configuration
│
└── frontend/                        # (Optional) Web UI
```

---

## Core Components

### 1. FastAPI Backend (`app/main.py`)

The main application entry point:

```python
app = FastAPI(
    title="Rx Details Extractor",
    version="1.0.0",
    description="Rx Auto Typing",
    root_path="/rx",
)

@app.on_event("startup")
async def startup_event():
    MongoJobManager.init_connection(MongoConfig.uri, MongoConfig.db_name)
```

**Key Features:**
- Async request handling
- Automatic OpenAPI documentation at `/rx/docs`
- MongoDB connection pooling on startup
- Health check endpoint at `/rx/health`

---

### 2. Celery Service (`services/celery/celery_service.py`)

Manages Celery application and task orchestration:

```python
class CeleryService:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        # Singleton pattern for Celery app
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
```

**Celery Configuration:**
- **Broker**: RabbitMQ (AMQP)
- **Result Backend**: MongoDB
- **Serialization**: JSON
- **Acknowledgment**: Late ACK (acks_late=True)
- **Queues**: `RX_EXTRACTION` (main), `RX_CALLBACK` (aggregation)

---

### 3. Task Processing (`tasks/tasks.py`)

#### Extraction Task
```python
@celery_app.task(bind=True, name="fax_routing_task")
def process_document_task(self, request_id, blob_path, client_id, client_name, queue_name):
    # 1. Get GCS URI for the file
    gcs_uri = gcp_manager.get_gcs_uri(blob_path)
    
    # 2. Send to Gemini AI for extraction
    response = asyncio.run(get_enhanced_answer_from_bot(gcs_uri=gcs_uri))
    
    # 3. Return structured results
    return {"results": results, "status": StatusLevels.SUCCESS.value}
```

#### Batch Callback Task
```python
@celery_app.task(name="batch_completed_task")
def batch_completed_task(file_results, *, request_id, webhook_url):
    # 1. Aggregate results from all files
    # 2. Validate patient data consistency
    # 3. Merge token usage
    # 4. Update MongoDB with final status
    # 5. Send webhook notification
```

**Chord Pattern:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         CELERY CHORD                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐                                           │
│   │ process_task(A) │ ──┐                                       │
│   │ process_task(B) │ ──┼──► batch_completed_task(results)      │
│   │ process_task(C) │ ──┘                                       │
│   └─────────────────┘                                           │
│                                                                  │
│   All tasks run in parallel, callback receives aggregated list  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4. LLM Integration (`services/llm/llm_services.py`)

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=1,
    thinking_level="medium",
    max_retries=3,
    response_mime_type="application/json",
)

async def run_prompt(model_name, user_input_type, user_input, prompt, use_gcs_uri=True):
    # Build message with GCS URI file reference
    message = HumanMessage(
        content=[{
            "type": "file",
            "file_id": user_input,  # gs://bucket/path
            "mime_type": "application/pdf",
        }]
    )
    
    response = await llm.ainvoke(messages)
    return {
        "content": response.content,
        "time_taken": time_taken,
        "input_tokens": usage_metadata["input_tokens"],
        "output_tokens": usage_metadata["output_tokens"],
    }
```

**Key Features:**
- Direct GCS URI support (no file download required)
- Async invocation with `ainvoke()`
- Token usage tracking
- Automatic retry on failures

---

### 5. Google Cloud Storage (`services/bucket/bucket_service.py`)

```python
class GCSStorageManager:
    def upload_file_from_uploadfile(self, file, destination_file_name, folder_name):
        blob_path = f"{folder_name}/{destination_file_name}"
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file.file, content_type=file.content_type)
        return blob_path
    
    def get_gcs_uri(self, blob_path):
        return f"gs://{self.bucket_name}/{blob_path}"
```

**Lifecycle Management:**
- Auto-delete files after 30 days
- Organized by request_id folders

---

## Data Flow

### Request Processing Flow

```
1. CLIENT REQUEST
   POST /rx/extract
   ├── uuid: "abc-123"
   ├── files: [file1.pdf, file2.pdf]
   ├── webhook_url: "https://..."
   └── request_type: "BATCH"

2. API HANDLER (route.py)
   ├── Validate JWT token
   ├── Create job in MongoDB (status: PENDING)
   ├── Upload files to GCS
   ├── Create Celery chord:
   │   ├── Task 1: process_document_task(file1)
   │   ├── Task 2: process_document_task(file2)
   │   └── Callback: batch_completed_task
   └── Return: {"uuid": "abc-123", "status": "RECEIVED"}

3. CELERY WORKER (tasks.py)
   ├── process_document_task:
   │   ├── Get GCS URI
   │   ├── Send to Gemini AI
   │   ├── Parse JSON response
   │   └── Return structured result
   │
   └── batch_completed_task (after all tasks complete):
       ├── Aggregate results
       ├── Validate patient consistency
       ├── Update MongoDB (status: SUCCESS/FAILED)
       └── Send webhook notification

4. CLIENT RETRIEVAL
   GET /rx/results/abc-123
   └── Return: {results, token_usage, status}
```

---

## API Design

### POST /rx/extract

**Request:**
```
Content-Type: multipart/form-data
Authorization: Bearer <JWT>

uuid: UUID (required)
webhook_url: string (optional)
request_type: "LIVE" | "BATCH" (default: BATCH)
files: File[] (required, PDF only)
```

**Response:**
```json
{
  "uuid": "a1d2830d-53c2-7258-2f69-ba74d2c6424a",
  "status": "RECEIVED"
}
```

### GET /rx/results/{request_id}

**Response:**
```json
{
  "uuid": "a1d2830d-53c2-7258-2f69-ba74d2c6424a",
  "status": "SUCCESS",
  "reason": "We have successfully processed the job.",
  "results": [
    {
      "file_name": "prescription.pdf",
      "Extracted_fields": {
        "patientData": {
          "patientFirstName": {
            "value": "John",
            "confidenceScore": 100,
            "confidenceCategory": "FullyClear",
            "explanation": "Found on page 1, clearly printed."
          }
        }
      }
    }
  ],
  "token_usage": {
    "input_tokens": 1500,
    "output_tokens": 800
  }
}
```

---

## Database Schema

### MongoDB Collections

#### `jobs` Collection
```javascript
{
  "_id": ObjectId,
  "request_id": "uuid-string",
  "status": "PENDING" | "PROCESSING" | "SUCCESS" | "FAILED",
  "payload": {
    "uuid": "...",
    "client_id": "63072",
    "client_name": "WebIPS Rx Typing",
    "webhook_url": "https://...",
    "request_type": "BATCH"
  },
  "results": {
    "uuid": "...",
    "results": [...],
    "token_usage": {...}
  },
  "error_message": null,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

---

## Authentication & Security

### JWT Validation Flow

```python
async def validate_token(request: Request):
    # 1. Extract Bearer token from Authorization header
    # 2. Fetch JWKS from auth service
    # 3. Validate signature with RS256
    # 4. Verify audience and issuer
    # 5. Extract client_id and client_name
    # 6. Store in request.state for downstream use
```

**Configuration:**
```
AUTH_SERVICE_JWKS_URL="http://aibot.meditab.com/auth/.well-known/jwks.json"
AUTH_ALGORITHM="RS256"
AUTH_AUDIENCE="auth-service"
AUTH_ISSUER="auth-service"
```

---

## Logging & Observability

### Structured Logging

```python
# Initialize logger
worker_logger = get_logger("extraction-worker-service")

# Log with context
worker_logger.info(
    "Processing job",
    request_id=request_id,
    client_id=client_id,
    file_name=file_name
)
```

**Log Output (JSON):**
```json
{
  "timestamp": "2026-06-05 05:41:09",
  "level": "info",
  "message": "Processing job",
  "request_id": "a1d2830d-53c2-7258-2f69-ba74d2c6424a",
  "client_id": "63072",
  "client_name": "WebIPS Rx Typing",
  "logger_name": "worker-logger",
  "environment": "dev",
  "service": "extraction-worker-service"
}
```

### Request Context Binding

```python
# Bind context at start of request/task
bind_request_context(request_id=request_id, client_id=client_id, client_name=client_name)

# All subsequent logs include this context automatically

# Clear context when done
clear_request_context()
```

---

## Error Handling

### Task-Level Error Handling

```python
@celery_app.task(bind=True, name="fax_routing_task")
def process_document_task(self, ...):
    try:
        # Normal processing
        return {"status": "SUCCESS", "results": results}
    
    except SoftTimeLimitExceeded as e:
        # Soft timeout - task can still return
        return {"status": "FAILED", "message": "Task timed out"}
    
    except Exception as e:
        # General error
        return {"status": "FAILED", "message": str(e)}
```

### Batch-Level Validation

```python
def batch_completed_task(file_results, ...):
    # Check for patient data consistency across files
    if first_patient_data != current_patient_data:
        all_patients_match = False
        error_message = "Patient data mismatch"
```

---

## Configuration Management

### Environment Variables (.env)

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS="app/core/google_project_hermes.json"
GOOGLE_CLOUD_PROJECT="meditab-autm-neutral-acent"
GCS_BUCKET_NAME="rx-auto-typing-bucket"

# Gemini AI
GEMINI_MODEL="gemini-3.1-pro-preview"
TEMPERATURE=1
THINKING_LEVEL="medium"

# MongoDB
MONGO_URI="mongodb://localhost:27017"
MONGO_DB_NAME="rx_auto_typing_db"

# Celery
CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
CELERY_RESULT_DB="rx_auto_typing_results"
CELERY_TASK_LIMIT=300

# Authentication
AUTH_SERVICE_JWKS_URL="http://aibot.meditab.com/auth/.well-known/jwks.json"
AUTH_ALGORITHM="RS256"
```

### Configuration Classes

```python
# core/configs/config.py
class Config:
    api_port = int(get_env_variable("API_PORT", 8511))
    webhook_url = get_env_variable("WEBHOOK_URL")

# core/configs/gemini.py
class GeminiConfig:
    model_name = get_env_variable("GEMINI_MODEL")
    temperature = float(get_env_variable("TEMPERATURE", 1))
    thinking_level = get_env_variable("THINKING_LEVEL", "medium")
```

---

## Performance Considerations

### Celery Worker Configuration

| Queue | Concurrency | Purpose |
|-------|-------------|---------|
| `RX_EXTRACTION` | 10 | Main document processing |
| `RX_CALLBACK` | 2 | Result aggregation |

### Task Timeouts

```python
CELERY_TASK_LIMIT = 600  # 10 minute soft limit. Raises SoftTimeLimitExceeded.
```

### Request Priority

| Request Type | Priority | Queue Behavior |
|--------------|----------|----------------|
| LIVE | 2 (High) | Processed first |
| BATCH | 1 (Normal) | Standard processing |

---

## Integration Points

| Integration | Type | Details |
|-------------|------|---------|
| **Google Gemini** | LLM API | Document understanding via `langchain-google-genai` |
| **Google Cloud Storage** | File Storage | PDF storage with GCS URI for direct LLM access |
| **MongoDB** | Database | Job persistence and result storage |
| **RabbitMQ** | Message Broker | Celery task queue |
| **Webhook** | HTTP Callback | Status notifications to client systems |

---

## Future Enhancements

1. **Hard Timeout Handling** — Implement chord error handler for partial result recovery
2. **Retry Logic** — Add exponential backoff for LLM API failures
3. **Caching** — Cache repeated extractions for identical documents
4. **Rate Limiting** — Implement per-client rate limits
5. **Metrics** — Add Prometheus metrics for extraction latency and success rates

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [LangChain Google GenAI](https://python.langchain.com/docs/integrations/chat/google_generative_ai)
- [Google Cloud Storage Python](https://cloud.google.com/storage/docs/reference/libraries)
- [Structlog Documentation](https://www.structlog.org/)
