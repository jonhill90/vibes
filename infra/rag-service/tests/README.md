# RAG Service Tests

## Overview

This directory contains integration tests for the RAG service pipeline.

## Tests

### test_pipeline.py

Full end-to-end integration test that validates the complete RAG pipeline:

1. **Database Connection** - PostgreSQL connection pool
2. **Source Creation** - Create a source record
3. **Document Ingestion** - Parse and chunk documents
4. **Embedding Generation** - Generate OpenAI embeddings
5. **Vector Storage** - Store embeddings in Qdrant
6. **Semantic Search** - Search and retrieve relevant chunks

**Run from project root:**

```bash
# Ensure services are running
docker-compose up -d

# Run the test
python3 tests/test_pipeline.py
```

**Expected Output:**

```
🚀 Starting RAG Service Pipeline Test
======================================================================

📦 Step 1: Initializing connections...
✅ Database pool created
✅ Qdrant client initialized
✅ All services initialized

📦 Step 2: Creating test source...
✅ Source created: <uuid>

📦 Step 3: Ingesting test document...
✅ Document ingested: <uuid>
   Chunks created: X
   Embeddings generated: X

📦 Step 4: Testing vector search...
🔍 Query: 'What is RAG?'
   ✅ Found X results
   1. Score: 0.XXX | Content: ...

======================================================================
✅ Pipeline test completed successfully!
```

## Requirements

- Docker services running (PostgreSQL, Qdrant, API)
- OpenAI API key configured in `.env`
- Python dependencies installed (see `backend/requirements.txt`)

## Notes

- Tests use real OpenAI API calls (costs money)
- Each test run creates new data in the database
- Consider adding cleanup steps for production tests
