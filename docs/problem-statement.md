# 📝 Problem Statement

## 1. Problem Statement

### 💡 What problem does your application solve?

All students know the struggle of juggling endless platforms, apps, forums to get in touch with fellow collegues and keep up with the course materials. Specifically at TUM, each course often has its own platform and refers to different resources, from books to videos to obscure websites. This fragmented system leaves many students overwhelmed, isolated, or unsure where to start when preparing for exams. While messaging platforms and file-sharing tools exist, they are fragmented and not designed with academic collaboration and intelligent assistance in mind.  
**StudySync** aims to address this gap by providing a unified, AI-powered platform for collaborative studying. It enables students to form study groups, share materials, ask questions, and get instant, context-aware answers using uploaded files as a knowledge base. Think of it as a TUM-all-in-one study companion, built to turn scattered effort into shared academic success.

---

### 🔧 Main Functionality

- **User Signup & Group Management**: Students create accounts, join or create study groups, and manage membership.
- **File Upload & Processing**: Users can upload lecture slides (PDF or PPTX), notes, and PDFs which will be indexed for retrieval.
- **Chat with GenAI Assistant**: Students ask questions in natural language and receive answers grounded in the uploaded materials.
- **Search & History**: Users can browse previous questions and responses in group-specific or personal threads.
- **Notifications**: Group members get notified of new messages, uploads, or AI summaries before exams. POTENTIALLY WILL REMOVE THIS!

---

### 🎯 Intended Users

- University students studying in small or medium-sized cohorts.
- Particularly useful for exam revision groups or project teams.
- Teaching assistants and tutors may also use it to manage FAQs or monitor group activity.

---

### 🧠 How will you integrate GenAI meaningfully?

- **LangChain (Python)** will be used to build a dedicated microservice that powers the AI assistant.
- The AI service will:
    - Provide **context-aware answers** based on specific study group content, not generic internet data.
    - Allow functionality like summarization of lecture PDFs or generating quiz questions for revision.
    - ADD MORE TECHY PART AND REVISE THIS A BIT

---

### 📘 User Scenarios

#### Scenario 1: Group Collaboration
Anna joins her Operating Systems study group on StudySync. She uploads the lecture slides and seminar notes. Her groupmates can now ask questions like _“What did the professor say about semaphores in week 3?”_, and the GenAI assistant returns the specific answer from the slides.

#### Scenario 2: Solo Revision
Lukas uploads his personal notes and slides into a private group. A week before the exam, he asks the assistant: _“Can you summarize the key points from all my uploaded documents?”_ and receives a bullet-point summary.

#### Scenario 3: Group Q&A History
Before the final, a group of students revisits questions asked earlier in the semester, like _“Explain the difference between deadlock prevention and avoidance.”_ All answers are archived and searchable by keywords.

#### Scenario 4: Alerts and Notifications
The system notifies users when someone uploads new content or if the AI assistant detects an upcoming exam (from file names or keywords) and offers a summary. MIGHT REMOVE THIS

---

📌 **Note:** This is the first version of our design. We expect to evolve it as we proceed with development and feedback.

---

📂 **Storage**  
This document will be stored in our GitHub repository at:  
`/docs/problem-statement.md`
