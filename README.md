# NicheRadar 🎯

**NicheRadar** is a **Social Intent & Lead Discovery Engine**. It scans social platforms (Reddit, LinkedIn, Quora, Twitter/X, Forums) for real-time posts, questions, and discussions matching a specific **Niche** and **Location** (e.g., *"Real Estate"* in *"Miami"*), scoring buying intent and delivering direct post links for instant engagement.

---

## 🚀 Features (Phase 1 MVP)

- **Multi-Platform Scanning**: Reddit RSS JSON fetcher + Bing SERP fallback + optional Serper.dev API support.
- **Intent Signal Classifier**: Detects High Intent signals (*"looking for"*, *"need recommendation"*, *"who is the best"*, *"hiring"*) vs Medium and Informational queries.
- **Glassmorphism Streamlit UI**: Dark mode dashboard with lead metric cards, rich post feed, and interactive filter controls.
- **Direct Link Triggers**: One-click direct link navigation to target social media threads.
- **AI Outreach Helper**: Generates tailored response templates ready to copy & paste into post comments.
- **Export Data**: One-click download of leads as CSV.

---

## 🛠️ Installation & Setup

1. **Activate Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment (Optional)**:
   Copy `.env.example` to `.env` if you wish to add paid/custom API keys:
   ```bash
   cp .env.example .env
   ```

---

## 🧪 How to Test & Run NicheRadar

### 1. Run the Streamlit App
Execute the following command in your terminal:
```bash
streamlit run app.py
```
This will open the dashboard in your browser at `http://localhost:8501`.

### 2. Step-by-Step UI Test Flow
1. **Enter Radar Parameters**:
   - **Niche / Industry**: `Real Estate`, `Law Firm`, `Dentist`, `Tax Advisor`, or `Mortgage Broker`.
   - **City / Country**: `Miami`, `New York`, `London`, `Dubai`, or `Toronto`.
2. **Select Target Platforms**: Check **Reddit**, **LinkedIn**, or **Quora**.
3. **Click `Scan Radar 📡`**: Watch the live progress bar as posts are fetched and classified.
4. **Explore Lead Results**:
   - Filter by **🔥 High Intent Only**.
   - Click **Open Post Link 🔗** to view the live social thread in a new tab.
   - Go to **✍️ AI Outreach Helper** tab, select a post, and copy the customized outreach message template!
5. **Export Leads**: Go to **📊 Data Table View** tab and click **📥 Export Leads to CSV**.

---

## 🗝️ Do You Need an API Key?

| Feature | Key Required? | Details |
| :--- | :--- | :--- |
| **Reddit Fetcher** | ❌ **NO** | Uses Reddit's public RSS/search endpoints out of the box. |
| **Bing SERP Scraper** | ❌ **NO** | Uses free SERP HTML parsing + base64 link decoding out of the box. |
| **Serper.dev API (Optional)** | 🔑 **OPTIONAL** | Add `SERPER_API_KEY` in `.env` for high-precision Google SERP results (2,500 free searches). |
| **Reddit API (Optional)** | 🔑 **OPTIONAL** | Add `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` in `.env` for official OAuth queries. |

---

## 🏗️ Project Structure

```text
NicheRadar/
│
├── .venv/                  # Virtual environment
├── requirements.txt        # Project dependencies
├── config.py               # Keyword lists & platform configuration
├── app.py                  # Streamlit dashboard
├── .env.example            # Environment template
│
├── fetchers/               # Scraping & link retrieval engine
│   ├── base.py             # PostItem Pydantic schema
│   ├── reddit_fetcher.py   # Reddit search fetcher
│   └── serp_fetcher.py     # Bing & Serper API fetchers with link decoder
│
└── utils/                  # Helper utilities
    ├── intent_analyzer.py  # Intent scoring logic
    └── exporter.py         # CSV & DataFrame exporter
```