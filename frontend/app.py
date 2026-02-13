import streamlit as st
import requests

# RESET QUIZ

if st.button("🔄 Reset Quiz"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# SESSION STATE INIT

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "completed" not in st.session_state:
    st.session_state.completed = set()


# PDF UPLOAD

st.subheader("📄 Upload Study PDF")

uploaded_file = st.file_uploader(
    "Upload a PDF (Any PDF)",
    type=["pdf"]
)

if uploaded_file is not None and "pdf_uploaded" not in st.session_state:

    with st.spinner("Indexing PDF..."):
        response = requests.post(
            "http://127.0.0.1:8000/upload-pdf",
            files={"file": uploaded_file}
        )

    if response.status_code == 200:
        st.session_state.pdf_uploaded = True
        st.success("PDF indexed successfully ✅")
    else:
        st.error("PDF upload failed ❌")


    if response.status_code == 200:
        st.success("PDF indexed successfully ✅")
    else:
        st.error("PDF upload failed ❌")



# QUIZ INPUTS

st.title("🧠 AI Quiz Generator")

topic = st.text_input("Enter quiz topic")
#summarize pdf
if st.button("📚 Summarize Topic"):
    response = requests.post(
        "http://127.0.0.1:8000/summarize",
        json={"topic": topic}
    )

    if response.status_code == 200:
        data = response.json()
        if "summary" in data:
            st.subheader("📖 Summary")
            st.write(data["summary"])
        else:
            st.error(data.get("error", "Error generating summary"))
    else:
        st.error("Backend error")

difficulty = st.selectbox(
    "Select difficulty level",
    ["easy", "medium", "hard"]
)


# GENERATE QUIZ (ONLY SET STATE)

if st.button("Generate Quiz"):
    response = requests.post(
        "http://127.0.0.1:8000/generate-quiz",
        json={
            "topic": topic,
            "difficulty": difficulty
        }
    )

    if response.status_code != 200:
        st.error("Backend error")
    else:
        st.session_state.quiz_data = response.json()
        st.session_state.score = 0
        st.session_state.completed = set()

        # clear old answers
        for key in list(st.session_state.keys()):
            if key.startswith("answered_") or key.startswith("result_"):
                del st.session_state[key]

        st.rerun()


# RENDER QUIZ (OUTSIDE BUTTON)

if st.session_state.quiz_data:
    data = st.session_state.quiz_data

    st.markdown(f"### 🧮 Current Score: {st.session_state.score}")

    for i, q in enumerate(data["questions"], 1):
        st.subheader(f"Q{i}. {q['question']}")

        answer = st.radio(
            "Choose an option:",
            q["options"],
            key=f"q{i}"
        )

        if f"answered_{i}" not in st.session_state:
            if st.button(f"Check Answer {i}", key=f"check_{i}"):
                st.session_state[f"answered_{i}"] = True
                is_correct = (answer == q["correct_answer"])
                st.session_state[f"result_{i}"] = is_correct

                if is_correct and i not in st.session_state.completed:
                    st.session_state.score += 1
                    st.session_state.completed.add(i)

                st.rerun()

        if st.session_state.get(f"answered_{i}"):
            if st.session_state.get(f"result_{i}"):
                st.success("Correct ✅")
            else:
                st.error("Wrong ❌")

            st.info(q["explanation"])


    # SUMMARY

    total_questions = len(data["questions"])

    answered_count = sum(
        1 for i in range(1, total_questions + 1)
        if st.session_state.get(f"answered_{i}")
    )

    if answered_count == total_questions:
        st.divider()
        st.subheader("📊 Quiz Summary")

        percentage = (st.session_state.score / total_questions) * 100

        st.write(f"**Score:** {st.session_state.score} / {total_questions}")
        st.write(f"**Percentage:** {percentage:.2f}%")

        if percentage == 100:
            st.success("Excellent! 🎉")
        elif percentage >= 60:
            st.info("Good job 👍")
        else:
            st.warning("Needs more practice 💪")
