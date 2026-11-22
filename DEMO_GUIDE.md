
---

## Demo Entry Point

| Component | URL |
|---|---|
| **Web Interface** | `http://localhost:3131` |
| **API Documentation** | `http://localhost:8511/rx/docs` |
| **Health Check** | `http://localhost:8511/rx/health` |

> Ensure both the backend and frontend servers are running before starting the demo. See `DEPLOYMENT.md` for setup instructions.

---

## Required Input Files

Prepare sample prescription documents in any of the supported formats:

| File Type | Example Filename |
|---|---|
| PDF | `\\indard\Demo Projects\Rx_Details_Extractor\app\data\input\sample_files \face sheet epic.pdf` |
| PDF | `\\indard\Demo Projects\Rx_Details_Extractor\app\data\input\sample_files\face sheet point click care.pdf` |

Place sample files in a convenient location on your machine (e.g., Desktop) for easy drag-and-drop during the demo.

### Ideal Sample Documents Should Contain:
- Patient name, date of birth, and address
- Prescriber name, NPI number, and contact information
- One or more medications with dosage, quantity, and refill instructions
- A mix of printed and handwritten text (to showcase confidence scoring)

---

## Step-by-Step Demo Instructions

### Step 1 — Application Overview

1. Open `http://localhost:3131` in a browser (Chrome recommended)
2. Point out the clean interface layout:
   - **Header** with gradient title and theme toggle
   - **Upload area** with drag-and-drop zone
   - **Animated background** with subtle floating gradient blobs

> **Talk Track:** *"This is the Rx Details Extractor — an AI-powered tool that reads prescription documents and extracts structured data automatically, replacing manual data entry."*

---

### Step 2 — Theme Toggle

1. Click the **Dark / Light** toggle button in the top-right corner
2. Show the smooth theme transition

> **Talk Track:** *"The interface is designed for pharmacy operators who work on screens all day. The dark mode reduces eye strain during extended use."*

---

### Step 3 — Upload a Document

1. **Drag and drop** a sample prescription PDF onto the upload zone
   - Alternatively, click the zone to open a file picker
2. Observe the file name and size preview appearing in the drop zone
3. Click **"Extract Details"**

> **Talk Track:** *"The operator simply drops the incoming fax or prescription document here. No manual data entry required."*

---

### Step 4 — AI Processing

1. Watch the loading spinner and "Processing..." indicator
2. Wait for the results to appear (typically 5–15 seconds)

> **Talk Track:** *"The document is being analyzed by Google's Gemini 2.5 Pro model. It reads both printed and handwritten text, identifies medical fields, and structures everything into categorized data — what would normally take 5-10 minutes of manual typing."*

---

### Step 5 — Review Extracted Data

1. Once results load, the layout expands to show:
   - **Sidebar** (left): Upload area + prescription category badge
   - **Results area** (right): Tabbed data display
2. Click through each tab:
   - **Prescriptions** — Drug name, strength, quantity, refills, Sig instructions, days supply
   - **Patient Data** — First name, last name, DOB, address, allergies, diagnosis code
   - **Prescriber Data** — Doctor name, NPI, DEA number, prescribed date
   - **Other Details** — Fax numbers, phone numbers, pharmacy details, reference codes

> **Talk Track:** *"The AI has automatically organized the extracted data into four categories. Each field is populated with the value found on the document."*

---

### Step 6 — Confidence Indicators

1. Hover over any **colored dot** next to a field label:
   - 🟢 **Green** = Fully Clear (100% confidence)
   - 🟡 **Yellow** = Ambiguous (50-99% confidence — handwritten, blurry, or inferred)
   - 🔴 **Red** = Absent (0% confidence — not found in document)
2. Show how the confidence text smoothly reveals on hover

> **Talk Track:** *"This is a critical feature. Every extracted field has a confidence score. Green means the AI is certain. Yellow flags data that may need human verification — perhaps it was handwritten. Red means the field wasn't found on the document at all. This ensures staff know exactly what to double-check."*

---

### Step 7 — AI Explainability

1. Click the **"Explain"** or **"Explanation"** button below any extracted field
2. Show the AI's reasoning text that appears

> **Talk Track:** *"Unlike a black-box system, our AI explains exactly where it found each piece of data and why it assigned that confidence score. This is essential for medical compliance and auditability."*

---

### Step 8 — Prescription Category

1. Point out the **Category badge** in the sidebar (e.g., "New Rx", "Refill Rx", "Refill Authorization Request")

> **Talk Track:** *"The system also classifies the entire document — is this a new prescription, a refill, or a refill authorization? This helps route the document to the right workflow."*

---

### Step 9 — Upload Another Document

1. While results are displayed, upload a second document using the compact upload zone in the sidebar
2. Click "Extract Details" again
3. Show that results refresh with new data

> **Talk Track:** *"Operators can process documents one after another without navigating away. The interface stays clean and efficient."*

---

## Expected Outputs

After a successful extraction, the audience should see:

| Output | Description |
|---|---|
| **Prescription Category** | Document classified as New Rx / Refill / Authorization |
| **Patient Data Cards** | 8+ fields (name, DOB, gender, address, allergies, etc.) |
| **Prescriber Data Cards** | 6+ fields (name, NPI, DEA, address, date) |
| **Rx Data Cards** | Per-medication cards with drug, strength, qty, sig, refills, days supply |
| **Other Details Cards** | 15+ fields (phone, fax, reference, pharmacy info, etc.) |
| **Confidence Dots** | Green / Yellow / Red for every field |
| **Explanations** | Expandable AI reasoning per field |

---

## Key Points to Highlight During Demo

| Feature | Why It Matters |
|---|---|
| **Speed** | Seconds vs. minutes of manual data entry |
| **Accuracy** | AI reads and structures complex medical data with high precision |
| **Confidence Scoring** | Staff know immediately which fields to verify — no guessing |
| **Explainability** | Every extraction is traceable and auditable |
| **Multi-format Support** | Handles PDFs, images, and faxes from any source |
| **No Training Required** | Intuitive drag-and-drop interface requires zero onboarding |
| **Scalability** | Can process high volumes without additional staff |
