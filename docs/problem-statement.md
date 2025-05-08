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
---

### 🎯 Intended Users

- University students studying in small or medium-sized cohorts.
- Particularly useful for exam revision groups or project teams.
- Teaching assistants and tutors may also use it to manage FAQs or monitor group activity.

---

### 🧠 GenAI integration

- A lightweight Python micro‑service built with **LangChain** handles retrieval‑augmented generation (RAG) for the study‑group assistant.  
- All course artefacts — PDFs, slides, office docs, and even scanned handwritten pages — pass through an **OCR + normalisation** pipeline, are embedded, and stored in a **Weaviate** vector database.  
- At query time LangChain performs similarity search on this private corpus, injects the matches into the prompt, and the LLM produces an answer strictly grounded in the uploaded material.  
- **Exposed API endpoints support:**  
  - context‑aware Q&A  
  - automatic lecture‑note summarisation  
  - on‑demand quiz generation for revision  

This keeps responses focused on the group’s own content, with no dependency on generic web data.
---

### 📘 User Scenarios

#### Scenario 1: Group Collaboration
Anna joins her Operating Systems study group on StudySync. She uploads the lecture slides and seminar notes. Her groupmates can now ask questions like _“What did the professor say about semaphores in week 3?”_, and the GenAI assistant returns the specific answer from the slides.

#### Scenario 2: Solo Revision
Lukas uploads his personal notes and slides into a private group. A week before the exam, he asks the assistant: _“Can you summarize the key points from all my uploaded documents?”_ and receives a bullet-point summary.

#### Scenario 3: Group Q&A History
Before the final, a group of students revisits questions asked earlier in the semester, like _“Explain the difference between deadlock prevention and avoidance.”_ All answers are archived and searchable by keywords.

---

📌 **Note:** This is the first version of our design. We expect to evolve it as we proceed with development and feedback.

---

📂 **Storage**  
This document will be stored in our GitHub repository at:  
`/docs/problem-statement.md`
