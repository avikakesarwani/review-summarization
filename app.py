import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Product Review Analyzer | Enterprise AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; color: #F8FAFC; }
    .hero-subtitle { font-size: 1rem; color: #94A3B8; max-width: 650px; margin: 0 auto; }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-label { font-size: 0.875rem; color: #64748B; text-transform: uppercase; }
    .review-card-pos {
        background-color: #F0FDF4; border-left: 4px solid #16A34A;
        padding: 1rem; border-radius: 6px; margin-bottom: 0.75rem; color: #14532D;
    }
    .review-card-neg {
        background-color: #FEF2F2; border-left: 4px solid #DC2626;
        padding: 1rem; border-radius: 6px; margin-bottom: 0.75rem; color: #7F1D1D;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Gemini Setup
# ----------------------------
api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
if api_key:
    genai.configure(api_key=api_key)

PREFERRED_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]


@st.cache_data(show_spinner=False)
def get_candidate_models(_key):
    """Ask the API which models this key can use, preferred ones first."""
    try:
        available = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
    except Exception:
        return PREFERRED_MODELS
    ordered = [m for m in PREFERRED_MODELS if m in available]
    others = [m for m in available if "flash" in m and m not in ordered]
    return (ordered + others)[:6] or PREFERRED_MODELS

# ----------------------------
# Sentiment Logic
# ----------------------------
def calculate_sentiment(review):
    positive_words = ["good", "great", "excellent", "amazing", "love", "easy", "fast", "quality", "useful", "perfect", "happy", "best"]
    negative_words = ["bad", "terrible", "poor", "hate", "broken", "worst", "slow", "problem", "issue", "damaged", "useless"]

    text = str(review).lower()
    positive_score = sum(word in text for word in positive_words)
    negative_score = sum(word in text for word in negative_words)

    if positive_score > negative_score:
        return "Positive"
    elif negative_score > positive_score:
        return "Negative"
    else:
        return "Neutral"

# ----------------------------
# AI Summary Function
# ----------------------------
def generate_gemini_summary(reviews):
    if not api_key:
        return "⚠️ `GEMINI_API_KEY` .env file me nahi mila. Please check environment variables."

    if not reviews:
        return "No reviews available."

    selected_reviews = reviews[:50]
    review_text = "\n".join(f"{idx}. {review}" for idx, review in enumerate(selected_reviews, start=1))

    prompt = f"""
You are an expert product insights analyst. Analyze the following customer reviews and generate an executive summary:

### Executive Highlights
- **Overall Sentiment**: [State overall tone and key conclusion]
- **Key Positives**: [List 2-3 prominent positive aspects]
- **Key Negatives & Pain Points**: [List 2-3 common issues reported]

### Comprehensive Summary
Provide a 2-3 sentence overview summarizing the consensus across these reviews.

Customer Reviews Batch:
{review_text}
"""

    last_error = None
    for model_name in get_candidate_models(api_key):
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
            return "No summary generated."
        except Exception as e:
            last_error = e
            continue

    return f"⚠️ Error generating summary: {str(last_error)}"

# ----------------------------
# Streamlit Layout
# ----------------------------
st.markdown("""
<div class='hero-container'>
    <div class='hero-title'>📊 Product Review Summarizer & Insights Tool</div>
    <div class='hero-subtitle'>Automated sentiment classification and LLM-powered review synthesis using Google Gemini.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuration")
    show_all_reviews = st.checkbox("Show full dataset in preview", value=True)
    st.markdown("---")
    sample_df = pd.DataFrame({
        "review": [
            "Great product! Very easy to assemble and smooth operation.",
            "Poor build quality, stopped working within 3 days.",
            "Excellent value for money. Very happy with the purchase.",
            "Delivery was fast, but the package arrived slightly damaged.",
            "Average performance. Meets basic expectations."
        ]
    })
    st.download_button(
        label="📥 Download Sample CSV",
        data=sample_df.to_csv(index=False),
        file_name="sample_reviews.csv",
        mime="text/csv",
        use_container_width=True
    )

uploaded_file = st.file_uploader("Upload Customer Reviews Dataset (.CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if "review" not in df.columns:
            st.error(f"❌ Missing 'review' column. Found: {list(df.columns)}")
            st.stop()

        df["review"] = df["review"].fillna("").astype(str).str.strip()
        df = df[df["review"] != ""].copy()

        df["sentiment"] = df["review"].apply(calculate_sentiment)

        total_reviews = len(df)
        pos_count = int((df["sentiment"] == "Positive").sum())
        neu_count = int((df["sentiment"] == "Neutral").sum())
        neg_count = int((df["sentiment"] == "Negative").sum())

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Reviews</div><div class='metric-value'>{total_reviews}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Positive</div><div class='metric-value' style='color:#16A34A;'>{pos_count}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Neutral</div><div class='metric-value' style='color:#64748B;'>{neu_count}</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Negative</div><div class='metric-value' style='color:#DC2626;'>{neg_count}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["🤖 LLM AI Summary", "📈 Sentiment Breakdown", "📋 Review Data Table", "🔍 Segmented Feedback"])

        with tab1:
            st.subheader("LLM Insights & Synthesis")
            if st.button("✨ Generate AI Insights Summary", type="primary", use_container_width=True):
                with st.spinner("Analyzing dataset patterns with Gemini..."):
                    summary_output = generate_gemini_summary(df["review"].tolist())
                with st.container(border=True):
                    st.markdown(summary_output)

        with tab2:
            st.subheader("Dataset Sentiment Distribution")
            st.bar_chart(df["sentiment"].value_counts())

        with tab3:
            st.subheader("Raw Review Data")
            display_data = df if show_all_reviews else df.head(10)
            st.dataframe(display_data, use_container_width=True)

        with tab4:
            col_pos, col_neg = st.columns(2)
            with col_pos:
                st.subheader("🟢 Positive Reviews")
                pos_list = df[df["sentiment"] == "Positive"]["review"].tolist()
                for i, rev in enumerate(pos_list[:15], 1):
                    st.markdown(f"<div class='review-card-pos'><b>{i}.</b> {rev}</div>", unsafe_allow_html=True)
            with col_neg:
                st.subheader("🔴 Negative Reviews")
                neg_list = df[df["sentiment"] == "Negative"]["review"].tolist()
                for i, rev in enumerate(neg_list[:15], 1):
                    st.markdown(f"<div class='review-card-neg'><b>{i}.</b> {rev}</div>", unsafe_allow_html=True)

    except Exception as err:
        st.error(f"❌ Error: {err}")
else:
    st.info("👆 Upload a CSV file to test.")