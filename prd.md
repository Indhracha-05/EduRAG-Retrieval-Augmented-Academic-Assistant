# Product Requirements Document (PRD)

## Project Title
Context-Aware Academic RAG Assistant

## Project Overview
The Context-Aware Academic RAG Assistant is an AI-powered academic support system that helps students understand course material, revise for exams, and practice viva questions.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from academic documents such as syllabi, lecture notes, lab manuals, and past question papers. It then generates accurate, context-grounded responses using a large language model.

The assistant also includes multiple teaching styles, source transparency, exam probability indication, and concept relationships to enhance the learning experience.

---

# Objectives

1. Build a domain-specific academic question-answering system.
2. Use RAG to reduce hallucination and ensure answers come from course materials.
3. Provide explanations in multiple teaching styles.
4. Help students prepare for exams and viva.
5. Demonstrate concepts from Information Retrieval and NLP pipelines.

---

# Target Users

Primary Users:
- Undergraduate students
- Students preparing for lab exams or viva

Secondary Users:
- Teaching assistants
- Professors demonstrating AI-assisted learning

---

# Core Features

## 1. Academic Document Ingestion

The system should ingest academic material including:

- Course syllabus
- Lecture notes
- Lab manuals
- Past question papers

Steps:
1. Upload PDF documents
2. Extract text
3. Clean and preprocess text
4. Split into chunks
5. Store chunks for retrieval

---

## 2. Retrieval-Augmented Generation (RAG)

The system should implement the following pipeline:

1. Convert document chunks into embeddings
2. Store embeddings in a vector database
3. Convert user query into embedding
4. Perform similarity search
5. Retrieve top relevant chunks
6. Send retrieved context + query to LLM
7. Generate grounded answer

Goal:
Ensure answers are derived from academic documents.

---

## 3. Teaching Modes

Users can select how the system explains a concept.

Teaching modes:

### Exam Mode
- Structured answer
- Bullet points
- Suitable for writing in exams

### Beginner Mode
- Very simple explanation
- Assume no prior knowledge

### Detailed Mode
- Deep conceptual explanation
- Include examples

### Analogy Mode
- Explain concept using real-world analogy

### Step-by-Step Mode
- Break concept into sequential steps

The selected mode modifies the prompt sent to the language model.

---

## 4. Source-Aware Answers

Every generated answer must include sources.

Example:

Sources:
- Module 2 – Databases for Data Science
- Lab Manual – SQL Section
- Past Question Paper

Purpose:
Improve credibility and traceability of answers.

---

## 5. Exam Probability Indicator

The system estimates the likelihood of the topic appearing in exams.

Logic:

High probability:
- Retrieved chunk originates from past question papers

Medium probability:
- Retrieved chunk originates from syllabus or lecture notes

Output example:

Exam Probability: High  
Reason: Topic appears in past question papers.

---

## 6. Mind Map Generator

After answering a question, the system generates related concepts.

Example:

Topic: SQL Joins

Related Concepts:
- Tables
- Primary Keys
- Foreign Keys
- Relational Databases

This helps students understand relationships between topics.

---

# User Flow

1. User opens the application
2. User enters a question
3. User selects teaching mode
4. System retrieves relevant document chunks
5. LLM generates context-grounded answer
6. System displays:
   - Answer
   - Sources
   - Exam probability
   - Related concepts

---

# User Interface

The UI should include:

- Question input field
- Teaching mode dropdown
- Ask button
- Answer display section
- Sources section
- Exam probability indicator
- Mind map / related concepts section

The interface should be implemented using Streamlit.

---

# Non-Functional Requirements

Performance:
- Query response time < 5 seconds

Accuracy:
- Answers must rely on retrieved document context

Scalability:
- System should support adding more documents

Usability:
- Interface should be simple and intuitive

---

# Deliverables

1. Working RAG application
2. Streamlit user interface
3. Document ingestion pipeline
4. Retrieval system
5. Answer generation system
6. Source citation system
7. Exam probability indicator
8. Mind map generator