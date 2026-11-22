# Rx Details Extractor

> **AI-Powered Prescription Data Extraction System**

An intelligent document processing solution that automatically extracts structured medical data from prescription documents (PDFs), replacing manual data entry with AI-powered automation.

---

## Overview

The **Rx Details Extractor** is designed for **pharmacy operations teams** who need to quickly digitize incoming prescriptions into structured records for processing and dispensing. The system leverages Google's Gemini AI to read, understand, and extract prescription information with confidence scoring and explainability.

---

## Problem Statement

| Challenge | Impact |
|-----------|--------|
| Pharmacies receive hundreds of prescriptions daily as faxes, scanned PDFs, and images | Manual reading and typing required for every document |
| Handwritten prescriptions are difficult to read | High risk of transcription errors in drug names, dosages, and patient details |
| Manual data entry is slow and labor-intensive | Bottleneck in prescription processing speed |
| Errors in prescription data can lead to patient safety issues | Regulatory and clinical risk |

---

## Business Value

| Benefit | Description |
|---------|-------------|
| **80%+ Time Reduction** | AI processes documents in seconds vs. minutes of manual typing |
| **Higher Accuracy** | Eliminates human transcription errors; flags ambiguous handwriting for review |
| **Confidence Scoring** | Every extracted field includes a confidence indicator (0-100%) |
| **Explainability** | AI provides reasoning for each extraction, ensuring transparency |
| **Scalability** | Handles high document volumes without proportional headcount increases |

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RX DETAILS EXTRACTOR FLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. UPLOAD              2. PROCESS              3. EXTRACT              4. REVIEW
│   ┌─────────┐           ┌─────────┐            ┌─────────┐            ┌─────────┐
│   │  PDF    │  ──────►  │  Queue  │  ──────►   │ Gemini  │  ──────►   │ Results │
│   │ Files   │           │ (Celery)│            │   AI    │            │Dashboard│
│   └─────────┘           └─────────┘            └─────────┘            └─────────┘
│                                                                              │
│   User uploads          Files stored in        AI extracts            Structured data
│   prescription(s)       GCS, tasks queued      30+ fields with        with confidence
│   via API               for processing         confidence scores      scores displayed
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Process

1. **Upload** — Client uploads prescription PDF(s) via REST API with authentication
2. **Queue** — Files are stored in Google Cloud Storage; extraction tasks are queued in Celery
3. **Extract** — Gemini AI analyzes documents and extracts structured prescription data
4. **Aggregate** — For multi-file batches, results are merged and validated for patient consistency
5. **Notify** — Webhook notification sent to client with completion status
6. **Retrieve** — Client fetches structured results via API

---

## Extracted Data Categories

### Patient Information
- First Name, Last Name, Date of Birth, Gender
- Address, Allergies, Diagnosis Codes
- Medicare Information, Delivery Indication

### Prescriber Information
- First Name, Last Name, Address
- NPI Number, DEA Number
- Prescribed Date

### Medication (Rx) Data
- Drug Name, Strength, Quantity
- Refills, Sig/Directions, Days Supply
- DAW (Dispense As Written), REG/PRN Indicator
- Refill Request Details (Rx No, Barcode, Denial Notes)

### Other Details
- Received/Sent Time, State License Number
- Prescriber Phone/Fax, Pharmacy Details
- Reference Numbers, Notes, Messages

---

## Confidence Scoring System

Each extracted field includes:

| Score Range | Category | Visual Indicator |
|-------------|----------|------------------|
| **100** | Fully Clear | 🟢 Green |
| **50-99** | Ambiguous | 🟡 Yellow |
| **0-49** | Unclear/Absent | 🔴 Red |

**Example Output:**
```json
{
  "patientFirstName": {
    "value": "John",
    "confidenceScore": 95,
    "confidenceCategory": "Ambiguous",
    "explanation": "Name found on page 1, top-right corner. Handwritten but clearly legible."
  }
}
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rx/extract` | Submit prescription PDF(s) for extraction |
| `GET` | `/rx/status/{request_id}` | Check processing status |
| `GET` | `/rx/results/{request_id}` | Retrieve extraction results |
| `GET` | `/rx/health` | Health check endpoint |

### Authentication
All endpoints require JWT Bearer token authentication.

---

## Request Types

| Type | Priority | Use Case |
|------|----------|----------|
| **LIVE** | High (2) | Real-time processing for urgent prescriptions |
| **BATCH** | Normal (1) | Background processing for bulk uploads |

---

## Key Features

- **Multi-File Batch Processing** — Upload multiple PDFs in a single request
- **Patient Data Validation** — Ensures consistency across multi-page prescriptions
- **Webhook Notifications** — Real-time status updates to your system
- **Structured JSON Output** — Clean, categorized data ready for integration
- **Token Usage Tracking** — Monitor AI API consumption per extraction
- **Async Processing** — Non-blocking API with status polling

---

## Quick Start

### Submit Extraction Request
```bash
curl -X POST "https://your-domain/rx/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "uuid=unique-request-id" \
  -F "webhook_url=https://your-webhook.com/callback" \
  -F "request_type=BATCH" \
  -F "files=@prescription1.pdf" \
  -F "files=@prescription2.pdf"
```

### Check Status
```bash
curl "https://your-domain/rx/status/unique-request-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Results
```bash
curl "https://your-domain/rx/results/unique-request-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Technical Write-Up](technical_write_up.md) | Detailed architecture and implementation |
| [Deployment Guide](DEPLOYMENT.md) | Installation and deployment instructions |
| [Demo Guide](DEMO_GUIDE.md) | Step-by-step demonstration walkthrough |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend API** | FastAPI (Python) |
| **AI/LLM** | Google Gemini via LangChain |
| **Task Queue** | Celery + RabbitMQ |
| **Database** | MongoDB |
| **File Storage** | Google Cloud Storage |
| **Logging** | Structlog + Loki + Grafana |
| **Monitoring** | Prometheus |

---

## Support

For technical support or questions, contact the AI Automation team.

