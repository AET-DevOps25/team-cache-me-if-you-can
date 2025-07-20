## 🌟 Cache-Me-If-You-Can: Study Group Management System 🌟

> A microservices-based application that powers collaborative study groups with seamless auth, file sharing, and GenAI-driven document Q\&A.
---
The core idea is for students to share their notes, course files and chat within one study group. The StudySync AI is a smart assistant- students can ask questions, and based on documents within the group, AI will answer. 
No more fake-news on google, get your answers directly from your notes, even faster than ctrl+f.

### 🚀 Quick Start (Local)

Get up and running in under **10 seconds** with just **3 simple commands**. No deep DevOps knowledge required!


# 1️⃣ Clone the repo 
```bash
git clone https://github.com/aet-devops25/team-cache-me-if-you-can.git \
```
# 2️⃣ Build all services (!!!Important!!! Docker must be running for this step!!!)
```bash
./build-all.sh 
```

# 3️⃣ Launch everything with Docker Compose
```bash
docker-compose up --build  
```
#  Explore the app & API docs
```bash
open http://localhost:3000          # React UI
Gateway: http://localhost:8080/swagger-ui.html  # All routes pass through here
Files:   http://localhost:8082/swagger-ui.html  # File upload/download
Group:   http://localhost:8083/swagger-ui.html  # Group mgmt & GenAI chat

# AWS
http://34.200.80.0:3000
```

*Pro Tip*: If `open` isn’t available on your shell, just copy-paste the URLs into your browser.

---
### 🏅 Bonus Features

- Advanced Kubernetes use 
- Full RAG pipeline implementation 
- Real-world-grade observability 
- Beautiful, original UI or impactful project topic	
- Advanced monitoring setup with extensive and meaningful metrics 

### 🏗️ Architecture Overview

Visualize how components interact at runtime:
![arh](https://github.com/user-attachments/assets/460073ac-90de-4e11-aedd-b6327dbf38d3)


**Key Components Explained:**

* **Gateway Service** (Port 8080) : Central router that authenticates JWTs and forwards API calls to the correct service.
* **User Service** (Port 8081) : Handles registration, login, token issuance/validation, and logout flows.
* **Files Service** (Port 8082) ️: Manages multipart file uploads, stores metadata in MySQL, and serves files via signed URLs.
* **Group Service** (Port 8083) : Enables CRUD for study groups, membership management (join/leave), real-time chat, and interfaces with GenAI for Q\&A.
* **GenAI Service** (Port 8000) : Processes uploaded documents, builds embeddings, and answers user queries using a trained language model.
* **MySQL Database** (Port 3306) ️: Single source of truth for users, groups, files, and chat history.
* **React Frontend** (Port 3000) : Intuitive SPA built with TypeScript and Tailwind, consuming REST endpoints.
* **Monitoring Stack** :

  * **Prometheus** collects metrics from each service.
  * **Loki** gathers application logs and error traces.
  * **Grafana** visualizes both metrics and logs in customizable dashboards.

---

### 📝 Usage Guide

Follow these steps to unlock collaboration power:

1. **Register &  Login**
   Create an account via the signup page, then log in to receive your JWT token.
2. **Create /  Join** a Study Group

   * **Create**: Set a group name, university name, and optional description.
   * **Join**: Enter an existing invite code to collaborate instantly.
3. **Upload Documents**
   Upload PDFs, slides, or notes into the Files tab. Uploaded files are indexed by GenAI.
4. **Chat with GenAI**
   Ask questions like “What are the key concepts in chapter 3?” and receive concise answers with references to your documents.
5. **Real-time Chat**
   Discuss with peers; messages are stored and searchable within the group.

> 💡 *Hint*: Upload your handwritten notes and download them in a latex format!

---

### 🔄 CI/CD & ⚙️ GenAI Integration

**CI/CD Pipelines** (GitHub Actions) ensure every change is built, tested, and deployed automatically:

* **Server Pipeline**:

  1. **Checkout** code and set up Java 17 environment.
  2. **Build** each Spring Boot service into Docker images. 
  3. **Test** with JUnit & Mockito (unit + integration). 
  4. **Push** images to GHCR using commit SHA tags. 
  5. **Apply** Terraform to deploy to Kubernetes (Dev & Prod). 

* **Client Pipeline**:

  1. **Lint** TypeScript with ESLint rules. 
  2. **Test** React components using Jest & React Testing Library. 
  3. **Build** production bundle and Docker image. 
  4. **Push** to GHCR & **Deploy** via Terraform. 

**GenAI Document Flow:**

1. **Upload** your file: `POST /api/v1/groups/{groupId}/documents`  
2. **Embedding**: GenAI processes text into vector store.
3. **Query**: `POST /api/v1/groups/{groupId}/chat` with a prompt. 
4. **Response**: GenAI Service returns answers with snippet citations and confidence scores.

---

### 📈 Monitoring

All monitoring configuration files live under `environment/`:

* **Prometheus**: `prometheus.yml` for scrape targets.
* **Loki**: `loki-config.yml` for log collection from containers.
* **Grafana**: JSON dashboards—import `java-dashboard.json` for service metrics and `genai-dashboard.json` for AI metrics. Additionally, under `environment/grafana/alerting` you can find `alert-rules.yml and `rules.yml`.

---

### 👩‍💻 Student Responsibilities

| Name    | Role                | Responsibilities                                                      |
| ------- | ------------------- |-----------------------------------------------------------------------|
| Jasmina | **Server Engineer** | Develop server services, secure JWT flows, and deployments 🤖         |
| Xiyue   | **Client Engineer** | Build React UI, configure ESLint/tests, and deployments 🎨            |
| Igor    | **GenAI Engineer**  | Integrate LLM, manage vector DB, monitor services, and deployments 🧠 |

---


### 📬 Contact

For questions or feedback:
* Join our Artemis channel: **[https://artemis.tum.de/](https://artemis.tum.de/)**

Happy studying! 🚀✨
