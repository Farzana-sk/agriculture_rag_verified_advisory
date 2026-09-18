# agriculture_rag_verified_advisory
# Voice-Based Multilingual Agricultural Advisory System Using RAG and Answer Verification

> Grounded Agricultural Extension via Context-Aware Answer Verification and Vernacular Speech Processing

---

## 📌 Project Overview
Generative Large Language Models (LLMs) deployed in agricultural advisory frequently face hallucination risks, generating ungrounded chemical formulations or incorrect pesticide schedules that can damage crops. Existing advisory systems are predominantly text-centric and English-focused, which creates an accessibility barrier for non-literate rural farmers.

This project implements a closed-loop, voice-enabled, multilingual agricultural advisory system. By coupling Context-Aware Retrieval-Augmented Generation (CA-RAG) with a post-generation Answer Verification Layer ($\tau \ge 0.6$), the system cross-references generated responses against authoritative agricultural documents before translating them into speech.

---

## 🚀 Key Features
* **Vernacular Speech Interface:** Enables farmers to interact naturally via voice input and output in Telugu, Hindi, and English using Whisper STT and Indic TTS.
* **Grounded Knowledge Retrieval:** Extracts verified Package of Practices (PoP) guidelines from ICAR and State Agricultural Universities indexed within ChromaDB.
* **High-Performance Generation:** Leverages Meta-Llama 3.1 8B for domain-specific agronomic advice synthesis[cite: 4].
* **Answer Verification Engine:** Uses a post-generation semantic similarity threshold ($\tau = 0.6$) adapted from Collini et al. (2025) to filter out hallucinations[cite: 4].
* **Evidence-Based Trust Scoring:** Displays a reliability and evidence-support score for each verified recommendation[cite: 4].

---

## 🏗️ System Architecture
[Farmer Voice Query] (Telugu / Hindi / English)[cite: 4]
│
▼
[1. Whisper Speech-to-Text] ──> [2. Language Detection][cite: 4]
│
▼
[3. Query Embedding (Sentence Transformers)][cite: 4]
│
▼
[4. ChromaDB Vector Search] <── [Trusted PoP Agricultural Knowledge Base][cite: 4]
│
▼
[5. Meta-Llama 3.1 8B Generation] ──> Candidate Response[cite: 4]
│
▼
[6. Answer Verification Engine] ──> Cosine Similarity Check (τ ≥ 0.6)[cite: 4]
│
┌────┴────────────────────────┐
▼                             ▼
[Passed: Trust Score Validated] [Failed: Flagged / Filtered][cite: 4]
│
▼
[7. Indic Text-to-Speech] ──> [Farmer Voice Output][cite: 4]
```markdown
# Voice-Based Multilingual Agricultural Advisory System Using RAG and Answer Verification[cite: 4]

> Grounded Agricultural Extension via Context-Aware Answer Verification and Vernacular Speech Processing[cite: 4]

---

## 📌 Project Overview
Generative Large Language Models (LLMs) deployed in agricultural advisory frequently face hallucination risks, generating ungrounded chemical formulations or incorrect pesticide schedules that can damage crops[cite: 4]. Existing advisory systems are predominantly text-centric and English-focused, which creates an accessibility barrier for non-literate rural farmers[cite: 4].

This project implements a closed-loop, voice-enabled, multilingual agricultural advisory system[cite: 4]. By coupling Context-Aware Retrieval-Augmented Generation (CA-RAG) with a post-generation Answer Verification Layer ($\tau \ge 0.6$), the system cross-references generated responses against authoritative agricultural documents before translating them into speech[cite: 4].

---

## 🚀 Key Features
* **Vernacular Speech Interface:** Enables farmers to interact naturally via voice input and output in Telugu, Hindi, and English using Whisper STT and Indic TTS[cite: 4].
* **Grounded Knowledge Retrieval:** Extracts verified Package of Practices (PoP) guidelines from ICAR and State Agricultural Universities indexed within ChromaDB[cite: 4].
* **High-Performance Generation:** Leverages Meta-Llama 3.1 8B for domain-specific agronomic advice synthesis[cite: 4].
* **Answer Verification Engine:** Uses a post-generation semantic similarity threshold ($\tau = 0.6$) adapted from Collini et al. (2025) to filter out hallucinations[cite: 4].
* **Evidence-Based Trust Scoring:** Displays a reliability and evidence-support score for each verified recommendation[cite: 4].

---

## 🏗️ System Architecture


```

[Farmer Voice Query] (Telugu / Hindi / English)
│
▼
[1. Whisper Speech-to-Text] ──> [2. Language Detection]
│
▼
[3. Query Embedding (Sentence Transformers)]
│
▼
[4. ChromaDB Vector Search] <── [Trusted PoP Agricultural Knowledge Base]
│
▼
[5. Meta-Llama 3.1 8B Generation] ──> Candidate Response
│
▼
[6. Answer Verification Engine] ──> Cosine Similarity Check (τ ≥ 0.6)
│
┌────┴────────────────────────┐
▼                             ▼
[Passed: Trust Score Validated] [Failed: Flagged / Filtered]
│
▼
[7. Indic Text-to-Speech] ──> [Farmer Voice Output]

```

---

## 🛠️ Technology Stack
* **Frontend:** React.js[cite: 4]
* **Backend:** FastAPI, PostgreSQL[cite: 4]
* **Vector Database:** ChromaDB[cite: 4]
* **Orchestration:** LangChain[cite: 4]
* **Core Models:**
  * **STT:** OpenAI Whisper[cite: 4]
  * **LLM:** Meta-Llama 3.1 8B[cite: 4]
  * **Embeddings:** Sentence Transformers[cite: 4]
  * **TTS:** Indic-TTS[cite: 4]

---

## 📚 Key Literature References
1. **Ref 01 (Base Paper):** Collini et al., *"Context-Aware Retrieval Augmented Generation Using Similarity Validation to Handle Context Inconsistencies in Large Language Models,"* *IEEE Access*, 2025 (Verification threshold $\tau = 0.6$)[cite: 4].
2. **Ref 02:** Dofitas Jr et al., *"Advanced Agricultural Query Resolution Using Ensemble-Based Large Language Models,"* *IEEE Access*, Feb. 2025 (Ensemble evaluation, 93.10% accuracy, Llama 3.1 benchmark)[cite: 3, 4].
3. **Ref 03:** Patel et al., *"FarmO’Cart: Multilingual Voice-Assisted Machine Learning Based Real-Time Price Prediction to Enhance Agricultural Income,"* *IEEE*, 2023 (Multilingual voice interface foundation)[cite: 4].

---

## 👥 Team & Project Details
* **Academic Institution:** Vasireddy Venkatadri Institute of Technology (VVIT), Guntur[cite: 4]
* **Department:** Computer Science and Machine Learning (CSM)[cite: 4]
* **Batch ID:** AIM-C10[cite: 4]
* **Project Guide:** Mr. Merigala Kishore Babu (Associate Professor, CSM, VVIT)[cite: 4]

### Team Members
| Roll Number | Name | Role |
| :--- | :--- | :--- |
| **24BQ5A6114**[cite: 4] | Shaik Farzana | Team Lead[cite: 4] |
| **24BQ5A6116**[cite: 4] | Thummalagunta Sumanth | Member[cite: 4] |
| **23BQ1A61F6**[cite: 4] | Pratikantam Veda Priyanka | Member[cite: 4] |
| **23BQ1A61B6**[cite: 4] | Ravela Rupesh | Member[cite: 4] |

```
