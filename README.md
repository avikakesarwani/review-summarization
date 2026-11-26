# 📊 Product Review Summarizer & Insights Tool

An AI-powered web app that turns a CSV of customer reviews into quick, readable insights: sentiment counts, categorized feedback, and an executive summary written by Google Gemini.

**🔗 Live App:** <https://review-summarization-rqj8dzriqr4ecxtwpngadr.streamlit.app/>

---

## 🎯 Problem Statement

LLM-Based Product Review Summarization Tool — Summarizes thousands of reviews into pros/cons/sentiment. Upload your reviews and get a clear picture in seconds.

## ✨ Features

- **CSV upload:** drop in a file with a `review` column
- **Automatic sentiment classification:** every review is labeled Positive, Neutral, or Negative
- **Dashboard metrics:** total reviews and counts per sentiment at a glance
- **LLM-generated summary:** Google Gemini writes an executive summary with overall sentiment, key positives, key pain points, and a short consensus overview
- **Sentiment chart:** bar chart of the sentiment distribution
- **Data table view:** browse the full dataset with sentiment labels
- **Segmented feedback:** positive and negative reviews shown side by side
- **Sample CSV download:** a ready-made test file in the sidebar
- **Automatic model fallback:** the app asks the Gemini API which models are available and uses the best one, so it keeps working when Google retires older models

## 🧠 How It Works

```
CSV upload  →  Cleaning (remove empty rows)  →  Sentiment labeling
                                                      ↓
                          Dashboard + charts  ←  Review data
                                                      ↓
                    Reviews sent to Gemini  →  Executive summary
```

1. The user uploads a CSV file containing a `review` column.
2. Empty and missing reviews are removed and the text is cleaned.
3. Each review is classified using a keyword-based sentiment scorer (it counts positive and negative words).
4. Metrics, charts, and tables are shown in separate tabs.
5. When the user clicks **Generate AI Insights Summary**, up to 50 reviews are sent to Gemini with a structured prompt, and the response is displayed as formatted Markdown.

## 🛠️ Tech Stack

| Part | Technology |
| --- | --- |
| Language | Python 3 |
| Web framework | Streamlit |
| Data handling | Pandas |
| LLM | Google Gemini (`google-generativeai`) |
| Config | python-dotenv |
| Hosting | Streamlit Community Cloud |

## 📁 Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .env                # API key (local only, never uploaded)
```

## 🚀 Run It Locally

**1. Clone the repository**

```bash
git clone https:/avikakesarwani/review-summarization/github.com//review-summarization.git
cd review-summarization
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key**

Get a free key from [Google AI Studio](https://aistudio.google.com/), then create a file named `.env` in the project folder:

```
GEMINI_API_KEY=your_key_here
```

**4. Start the app**

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 📄 Input Format

Your CSV needs a column named `review`:
review_cleaned.csv

You can download a sample file from the app's sidebar.

## ☁️ Deployment

The app is deployed on Streamlit Community Cloud. The API key is stored securely in the app's **Secrets** settings (`GEMINI_API_KEY = "..."`) and is never committed to the repository.

## ⚠️ Limitations

- Sentiment is detected with a simple keyword list, so it can miss sarcasm, negation (for example "not good"), and words outside the list.
- Only the first 50 reviews are sent to the AI summary to stay within model limits.
- The summary quality depends on the Gemini model and on the quality of the uploaded reviews.
- Only English reviews are supported.

## 👤 Author

**AVIKA** — ABES ENGINEERING COLLEGE / BTECH-ECE / avika.24b0311099@abes.ac.in

---
