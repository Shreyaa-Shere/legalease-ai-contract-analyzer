# ⚖️ LegalEase – AI-Powered Contract Analyzer & Summary App

> 🚧 **Status**: In Development  
> Helping people understand what they’re signing — one contract at a time.

LegalEase is a full-stack AI-powered platform that simplifies the way individuals and professionals handle legal contracts. Users can upload contracts (PDF, DOCX), and LegalEase automatically extracts key clauses and highlights potential risks — like auto-renewals, indemnity terms, and early termination triggers — using NLP and GPT models.

It’s designed to help users gain legal clarity without needing to read through 20 pages of legal jargon.

---

## 🌐 Tech Stack

| Layer       | Tools & Services                               |
|-------------|------------------------------------------------|
| Frontend    | React, Tailwind CSS                            |
| Backend     | Django, Django REST Framework                  |
| Database    | PostgreSQL                                     |
| Cloud       | AWS EC2, S3                                    |
| AI / NLP    | OpenAI (GPT), custom clause extractor (NLP)    |
| Async Tasks | Celery (for heavy file processing)             |
| DevOps      | GitHub Actions (CI/CD)                         |
| Testing     | PyTest                                         |

---

## 🚀 Key Features

- 📄 **Contract Upload** – Upload legal contracts in PDF or DOCX format  
- 🔍 **Clause Extraction** – Automatically extract and tag legal clauses (e.g. “Termination”, “Confidentiality”)  
- 🧠 **Risk Summarization** – Highlight risky clauses using GPT (e.g. “auto-renewal in 7 days”)  
- 📌 **Clause Highlighting UI** – Web interface for clause-by-clause review with filters  
- ⏰ **Reminders** – Track expiration or renewal deadlines with dashboard alerts  
- ☁️ **Secure Cloud Storage** – Uploads securely stored on AWS S3  
- 👩‍⚖️ **Multi-Contract Management** – Dashboard to manage all your signed agreements

---

## 💡 Why LegalEase?

Reading long contracts is tedious. LegalEase empowers users — whether freelancers, renters, or founders — to make faster, smarter decisions without missing critical details buried in fine print. It’s like having a junior legal assistant built into your browser.

---

## 👩‍💻 Author

**Shreya**  
Passionate about backend development, applied NLP, and building tools that solve real-world problems.  

---

