# 🛢️ HPCL B2B Lead Intelligence System

> **Transforming Public Market Signals into Actionable Sales Intelligence**

## 🎯 Executive Summary

In B2B industrial sales, timing is everything. A new petrochemical plant commissioning, a capacity expansion announcement, or a fuel procurement tender represents millions in potential revenue—but only if discovered early.

**The Challenge:** Critical demand signals are scattered across public sources (news, tenders, company websites) and often detected too late, after competitors have already engaged.

**Our Solution:** An intelligent decision-support system that automatically detects, analyzes, and prioritizes B2B opportunities for HPCL's Direct Sales division—combining real-time signal processing, domain-aware product inference, and explainable AI to give sales teams an early-mover advantage.

**Key Innovation:** We separate *company intelligence* (long-lived entity profiles) from *opportunities* (time-bound buying events), enabling both new customer discovery and existing customer cross-sell within a unified framework.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PUBLIC DATA SOURCES                       │
│  Tenders • News • Company Websites • Industry Reports       │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│            WEB INTELLIGENCE & GOVERNANCE LAYER              │
│  • Policy-compliant crawling (robots.txt, rate limits)      │
│  • Source reliability scoring                               │
│  • Timestamp tracking & deduplication                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│            ENTITY RESOLUTION & COMPANY PROFILING              │
│  • Fuzzy matching across data sources                       │
│  • Industry classification (NAICS/NIC mapping)              │
│  • Geographic & operational context                         │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│            PRODUCT-NEED INFERENCE ENGINE ⭐                 │
│  • Rule-based business logic + ML feature extraction        │
│  • Industry → Product mapping (explained)                   │
│  • Confidence calibration & uncertainty quantification      │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              LEAD SCORING & PRIORITIZATION                  │
│  • Multi-factor weighted scoring:                           │
│    - Signal strength (tender > expansion > news)            │
│    - Temporal freshness decay                               │
│    - Geographic proximity to depots                         │
│    - Estimated deal size                                    │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              SALES OFFICER INTERFACE                        │
│  • Prioritized lead queue                                   │
│  • Explainable recommendations                              │
│  • Guided outreach workflows                                │
│  • Feedback capture (Accept/Reject/Convert)                 │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│            CONTINUOUS LEARNING LOOP                         │
│  • Feedback analysis & pattern recognition                  │
│  • Human-reviewed rule refinement                           │
│  • Performance monitoring & A/B testing                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧮 The Mathematics Behind Intelligence

### 1. **Lead Scoring Algorithm**

Each opportunity receives a composite score combining multiple weighted factors:

```
Score(L) = w₁·I(L) + w₂·F(L) + w₃·S(L) + w₄·G(L)

where:
  I(L) = Intent Strength Score ∈ [0, 1]
  F(L) = Freshness Score = e^(-λt)  // exponential decay
  S(L) = Scale Proxy ∈ [0, 1]
  G(L) = Geographic Relevance ∈ [0, 1]
  
  w₁ + w₂ + w₃ + w₄ = 1  // normalized weights
```

**Intent Strength Mapping:**
- Tender notice: 1.0
- Capacity expansion: 0.8
- New plant commissioning: 0.75
- General industry news: 0.4

**Freshness Decay:** λ = 0.1 per day (90% relevance after 1 day, 50% after ~7 days)

### 2. **Product-Need Inference Logic**

Rather than black-box classification, we use transparent domain rules. Confidence is mapped as:
- **High (≥0.8):** Auto-surface to sales
- **Medium (0.5-0.8):** Require validation
- **Low (<0.5):** Hold for review

---

## 🔍 Signal Detection & Processing

### Supported Signal Types

| Signal Type | Source Examples | Confidence Baseline | Avg. Processing Time |
|-------------|----------------|---------------------|---------------------|
| **Tender Notices** | GeM, eProcurement portals | 0.95 | 2-5 minutes |
| **Capacity Expansion** | Press releases, NSE filings | 0.80 | 5-10 minutes |
| **New Commissioning** | Industry news, company websites | 0.75 | 5-15 minutes |
| **Procurement RFQs** | Direct company portals | 0.90 | 3-7 minutes |

### Source Governance

All data collection follows strict compliance:
- **Robots.txt Respect**: Strictly adhered to.
- **Rate Limiting**: configured to avoid server load (e.g., 1 request per 2 seconds).
- **User-Agent**: Explicit identification as "HPCL-Intelligence-Bot".

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for Frontend)
- **Git**

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/IITR-HPCL.git
cd IITR-HPCL
```

### 2. Environment Setup

**Backend (Scraper)**
```bash
cd Scraper
cp .env.example .env
# Edit .env with your configuration (Database, API Keys, etc.)
```

**Frontend**
```bash
cd ../frontend
cp .env.example .env
# Edit .env with your API URL if different from default
```

### 3. Running with Docker (Recommended)

The easiest way to run the entire stack is with Docker Compose.

```bash
# From root directory
docker-compose up --build
```

- **Backend API**: http://localhost:8000
- **Frontend App**: http://localhost:3000

### 4. Manual Setup (Alternative)

#### Backend Setup
Navigate to the `Scraper` directory:
```bash
cd Scraper
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Initialize the database (if applicable/needed):
```bash
# Example command if a seed script exists, otherwise skip
python backend/scripts/seed_data.py
```

Create a `.env` file in the `Scraper` directory with necessary configurations (refer to `.env.example`).

#### 3. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd ../frontend
```

Install Node.js dependencies:
```bash
npm install
```

### Running the Application

#### 1. Start the Backend Server
From the `Scraper` directory (with venv activated):
```bash
# Uses uvicorn to run the FastAPI app
uvicorn backend.app.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

#### 2. Start the Frontend Application
From the `frontend` directory:
```bash
npm run dev
```
The application will be available at `http://localhost:3000`.

#### 3. Running the Scraper
From the `Scraper` directory (with venv activated):

**Option A: Continuous Service (Recommended)**
Runs on a schedule (Tenders: 1h, News: 6h, Directories: 24h).
```bash
python scraper.py
```

**Option B: Single Pass**
Runs all scrapers once and exits. Useful for testing or cron jobs.
```bash
python run_once.py
```

**Monitor Progress:**
View real-time stats and logs:
```bash
python monitor.py
```

---

## 🛠️ Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.11, FastAPI | High-performance API & async business logic |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Structured data storage |
| **Scraping** | BeautifulSoup, Selenium | Data collection from public sources |
| **Frontend** | Next.js 14, React, TailwindCSS | Responsive Sales Officer interface |
| **Deployment** | Docker, Systemd | Production process management |

---

## 📂 Directory Structure

```
IITR-HPCL/
├── Scraper/                 # Backend & Scraping Logic
│   ├── backend/             # FastAPI Application
│   │   ├── app/             # Main App Logic (Routers, Models)
│   │   └── scripts/         # Utility Scripts (Seeding, etc.)
│   ├── deployment/          # Deployment Configs (Systemd, Nginx)
│   ├── data/                # Data Storage (SQLite, Backups)
│   ├── requirements.txt     # Python Dependencies
│   └── ...
├── frontend/                # Next.js Frontend Application
│   ├── src/                 # Source Code (Components, Pages)
│   ├── public/              # Static Assets
│   ├── package.json         # Node.js Dependencies
│   └── ...
└── README.md                # Project Documentation
```

## 📚 Documentation

- **[Deployment Guide](Scraper/DEPLOYMENT.md)** — Production setup & Systemd configuration
- **[API Reference](Scraper/API_QUICK_REFERENCE.md)** — Endpoints and data schemas
- **[Frontend Integration](Scraper/FRONTEND_INTEGRATION.md)** — Guide for frontend developers

---

## 👥 Team

Built with ❤️ by Team Blacklist

---

<div align="center">

**"The system coordinates people, it does not replace them."**

*Intelligence amplifies judgment. Technology scales expertise.*

</div>
