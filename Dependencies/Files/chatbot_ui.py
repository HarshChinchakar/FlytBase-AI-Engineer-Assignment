
import os
import json
import torch
import pandas as pd
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

EVENT_LOG_FILE = "events/event_logs.csv"
CHAT_MEMORY_FILE = "chat_memory.txt"
ALERT_FILE = "events/alerts.csv"
EMBEDDINGS_FILE = "events/event_embeddings.json"
GORQ_API_URL = "https://api.groq.com/v1/chat/completions"
GORQ_API_KEY = "your-groq-api-key"  # Replace this

semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_data():
    events_df = pd.read_csv(EVENT_LOG_FILE)
    with open(EMBEDDINGS_FILE, 'r') as f:
        embeddings = json.load(f)
    return events_df, embeddings

def retrieve_relevant_context(query, events_df, embeddings):
    query_emb = semantic_model.encode([query])[0]
    sim_scores = [np.dot(query_emb, e['embedding']) / (np.linalg.norm(query_emb) * np.linalg.norm(e['embedding'])) for e in embeddings]
    sem_results = sorted(zip(events_df.to_dict(orient="records"), sim_scores), key=lambda x: x[1], reverse=True)[:10]

    tfidf = TfidfVectorizer(stop_words='english')
    corpus = [log['caption'] for log in events_df.to_dict(orient="records")]
    tfidf_matrix = tfidf.fit_transform(corpus)
    query_vec = tfidf.transform([query])
    tfidf_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    tfidf_results = sorted(zip(events_df.to_dict(orient="records"), tfidf_scores), key=lambda x: x[1], reverse=True)[:10]

    seen_ids = set()
    final_results = []
    for entry in sem_results + tfidf_results:
        if entry[0]['event_id'] not in seen_ids:
            final_results.append(entry[0])
            seen_ids.add(entry[0]['event_id'])
    return final_results[:10]

def query_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GORQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(GORQ_API_URL, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def save_chat_memory(user_msg, bot_msg):
    with open(CHAT_MEMORY_FILE, "a") as f:
        f.write(f"User: {user_msg}\nBot: {bot_msg}\n\n")

def get_recent_chats(n=3):
    if not os.path.exists(CHAT_MEMORY_FILE):
        return ""
    with open(CHAT_MEMORY_FILE, "r") as f:
        chats = f.read().strip().split("\n\n")
    return "\n\n".join(chats[-n:])

def generate_report(events_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Daily Anomaly Report", ln=True, align="C")

    for i, row in events_df.iterrows():
        pdf.multi_cell(0, 10, f"Event ID: {row['event_id']}\nTime: {row['start_time']}\nSummary: {row['caption']}\n\n")

    fig, ax = plt.subplots()
    events_df['start_time'] = pd.to_numeric(events_df['start_time'], errors='coerce')
    events_df = events_df.dropna(subset=['start_time'])
    times = events_df['start_time'].astype(float)
    ax.hist(times, bins=10, color='red')
    ax.set_title("Alert Event Timeline")
    fig.savefig("alert_timeline.png")
    pdf.image("alert_timeline.png", w=180)

    pdf.output("daily_report.pdf")

def run_app():
    st.set_page_config(page_title="Anomaly Chatbot", layout="centered")
    st.title("🔎 Agentic Anomaly Analyst")

    query = st.text_input("Ask your question:", placeholder="e.g., What happened today?")
    if st.button("Submit"):
        events_df, embeddings = load_data()
        relevant_context = retrieve_relevant_context(query, events_df, embeddings)
        context_text = "\n\n".join([f"Event {e['event_id']}: {e['caption']}" for e in relevant_context])
        history = get_recent_chats()

        final_prompt = f"You are an anomaly reporting assistant. Here is the chat history:\n{history}\n\nNow answer this query precisely using the context below:\n{context_text}\n\nUser asked: {query}"
        response = query_llm(final_prompt)
        save_chat_memory(query, response)
        st.markdown(f"**Response:** {response}")

        if "report" in query.lower():
            generate_report(events_df)
            with open("daily_report.pdf", "rb") as f:
                st.download_button("Download PDF Report", f, file_name="daily_report.pdf")
