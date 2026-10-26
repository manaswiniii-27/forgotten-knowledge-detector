
import json
from pathlib import Path
from datetime import date, timedelta

import streamlit as st

# -------------------------------
# 1. Basic application settings
# -------------------------------

st.set_page_config(
    page_title="Forgotten Knowledge Detector",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Forgotten Knowledge Detector")
st.write("Track what you learn and identify topics that need revision.")

# -------------------------------
# 2. File used to store topics
# -------------------------------

DATA_FILE = Path(__file__).parent / "topics.json"


# -------------------------------
# 3. Load topics from JSON
# -------------------------------

def load_topics():
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


# -------------------------------
# 4. Save topics to JSON
# -------------------------------

def save_topics(topics):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(topics, file, indent=4)


# -------------------------------
# 5. Load existing information
# -------------------------------

topics = load_topics()

# -------------------------------
# 6. Add a new topic
# -------------------------------

st.header("Add a Learning Topic")

with st.form("topic_form"):
    topic_name = st.text_input("Topic name")

    score = st.slider(
        "How well do you understand it?",
        min_value=1,
        max_value=5,
        value=3
    )

    learned_date = st.date_input(
        "Date you learned it",
        value=date.today()
    )

    submitted = st.form_submit_button("Save Topic")

    if submitted:
        if not topic_name.strip():
            st.error("Please enter a topic name.")

        elif any(
            topic["name"].casefold() == topic_name.strip().casefold()
            for topic in topics
        ):
            st.warning("This topic already exists.")

        else:
            # Lower scores mean more revision is needed.
            if score <= 2:
                review_days = 1
            elif score == 3:
                review_days = 3
            else:
                review_days = 7

            new_topic = {
                "name": topic_name.strip(),
                "score": score,
                "learned_date": learned_date.isoformat(),
                "revision_date": (
                    learned_date + timedelta(days=review_days)
                ).isoformat()
            }

            topics.append(new_topic)
            save_topics(topics)

            st.success("Topic saved successfully!")
            st.rerun()

# -------------------------------
# 7. Identify topics for revision
# -------------------------------

today = date.today()
due_topics = []

for topic in topics:
    revision_date = date.fromisoformat(topic["revision_date"])

    if revision_date <= today:
        due_topics.append(topic)

# -------------------------------
# 8. Display dashboard
# -------------------------------

st.header("Your Learning Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Topics", len(topics))
col2.metric("Topics to Revise", len(due_topics))
col3.metric("Well Understood", sum(
    1 for topic in topics if topic["score"] >= 4
))

# -------------------------------
# 9. Display all saved topics
# -------------------------------

st.header("All Learning Topics")

if topics:
    for index, topic in enumerate(topics):
        revision_date = date.fromisoformat(
            topic["revision_date"]
        )

        with st.expander(topic["name"]):
            st.write(f"Understanding score: {topic['score']}/5")
            st.write(f"Learned on: {topic['learned_date']}")
            st.write(f"Revision date: {revision_date}")

            if revision_date <= today:
                st.warning("Revision is due!")
            else:
                st.info("Revision is scheduled.")

            if st.button("Delete Topic", key=f"delete_{index}"):
                topics.pop(index)
                save_topics(topics)
                st.rerun()
else:
    st.info("No topics saved yet. Add your first topic above.")

# -------------------------------
# 10. Generate a learning report
# -------------------------------

st.header("Learning Report")

if topics:
    average_score = sum(
        topic["score"] for topic in topics
    ) / len(topics)

    st.write(f"Average understanding score: {average_score:.2f}/5")

    st.subheader("Topics needing more practice")

    weak_topics = [
        topic for topic in topics
        if topic["score"] <= 2
    ]

    if weak_topics:
        for topic in weak_topics:
            st.write(f"- {topic['name']} ({topic['score']}/5)")
    else:
        st.write("No low-scoring topics right now.")

    report = {
        "total_topics": len(topics),
        "topics_due_for_revision": len(due_topics),
        "average_score": round(average_score, 2),
        "topics": topics
    }

    st.download_button(
        "Download Learning Report",
        data=json.dumps(report, indent=4),
        file_name="learning_report.json",
        mime="application/json"
    )
