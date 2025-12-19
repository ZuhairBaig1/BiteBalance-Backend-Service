# BiteBalance – Backend Service

BiteBalance Backend is a Flask-based API that powers a health-aware, AI-driven recipe recommendation system.  
It integrates LLMs, vector search (RAG), and external search tools to generate personalized, safe recipes based on a user’s health conditions.

This repository contains only the backend implementation, which I was solely responsible for designing and developing.

## 🚀 Overview

The backend serves as the core intelligence layer of BiteBalance. It:

- Accepts user health conditions and food queries
- Retrieves disease-specific dietary constraints using vector similarity search
- Fetches detailed base recipes using web search tools
- Uses an LLM (GPT-4o) to generate safe, personalized ingredients and cooking instructions
- Exposes this functionality via a RESTful Flask API

The architecture follows a Retrieval-Augmented Generation (RAG) approach to ensure responses are context-aware, accurate, and health-conscious.

## 🧠 Backend Architecture

### High-level Flow

1. Client sends:
   - Food name
   - Health conditions

2. Backend:
   - Fetches base recipe data using Tavily Search
   - Retrieves health-specific dietary constraints from a Cassandra vector database

3. LLM combines:
   - Health context
   - Dietary restrictions
   - Recipe ingredients

4. Backend returns:
   - Safe alternative ingredients
   - Detailed cooking instructions

## 🛠️ Technologies Used

### Flask
- Lightweight WSGI framework
- Handles routing, request validation, and JSON responses

### LangChain
- Orchestrates LLM calls, prompts, and tool usage
- Connects LLMs with vector databases and external search tools

### OpenAI GPT-4o
- Generates human-like, context-aware recipe instructions
- Adapts recipes based on health conditions

### Cassandra (DataStax Astra DB)
- Used as a vector database
- Stores health and disease-related dietary embeddings
- Enables fast similarity-based retrieval for RAG

### Tavily Search API
- Fetches detailed, real-world recipe ingredients and instructions
- Acts as an external knowledge source
