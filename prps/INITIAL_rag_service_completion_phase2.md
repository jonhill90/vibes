# INITIAL: RAG Service Completion Phase 2

## FEATURE

Finish the remaining work to ship the standalone RAG service MVP as described in `prps/rag_service_research/ARCHITECTURE.md` and the partially completed implementation in `infra/rag-service/`. This phase focuses on stabilizing the MCP server, adding Crawl4AI-driven ingestion, exposing REST + frontend experiences, aligning the embedding cache, and expanding automated test coverage.

**Core Goal**: Deliver a production-ready RAG service with web crawling, hybrid search exposure, functional UI/API surfaces, and robust tooling so agents and users can manage knowledge bases end-to-end.

**Output**: Updated backend, MCP, and frontend code that passes lint/type/test gates, exposes the new capabilities, and satisfies the success criteria below.

## EXAMPLES

### Reference Architecture & Implementation

- `prps/rag_service_research/ARCHITECTURE.md` — canonical design decisions for vector DB, schema, search pipeline, ingestion flow, MCP tools, and Docker topology.
- `infra/rag-service/backend/src/mcp_server.py` — current FastMCP setup (needs transport + constructor fixes).
- `infra/rag-service/backend/src/services/embeddings/embedding_service.py` — embedding cache logic (requires schema alignment + AsyncOpenAI wiring).
- `infra/rag-service/backend/src/services/search/` — base and hybrid search strategies already implemented.
- `infra/rag-service/backend/src/services/` — service layer patterns (document/source/vector/ingestion) matching task-manager style.

### Crawl4AI Patterns

- `repos/ottomator-agents/docling-rag-agent/` (if available locally) — reference for integrating Crawl4AI with Docling pipelines.
- Crawl4AI docs: https://docs.crawl4ai.com/ (Quick Start, API Reference, Retry/Rate-limit strategies).

## DOCUMENTATION

- FastMCP Streamable HTTP transport: `vibesbox/src/mcp_server.py` and `docs/mcp/streamable-http.md` (if present).
- Crawl4AI quick start & async usage: https://docs.crawl4ai.com/
- AsyncOpenAI client docs: https://platform.openai.com/docs/libraries/python
- FastAPI routers pattern: `infra/task-manager/backend/src/api_routes/`
- Frontend scaffolding: `infra/rag-service/frontend/README.md` (if present) and Vite docs https://vitejs.dev/guide/
- Testing conventions: `AGENTS.md` (pytest, ruff, mypy expectations)

## OTHER CONSIDERATIONS

### Success Criteria

- [ ] MCP server runs via streamable HTTP, exposes ports in Docker Compose, and tools can be invoked from Claude/agents without runtime errors.
- [ ] Crawl4AI ingestion pipeline can crawl a site, persist crawl jobs, and push parsed content through Docling → chunking → embedding → storage.
- [ ] REST API exposes `/api/documents`, `/api/sources`, `/api/search`, and `/api/crawls` (or similar) with validation, pagination, and error handling.
- [ ] Frontend provides upload, search, and source/crawl management flows that interact with the API.
- [ ] Hybrid search toggle works through API + MCP (vector-only fallback validated) with logging around latency and weighting.
- [ ] Embedding cache writes succeed (schema + SQL aligned) and cache hit-rate metrics logged.
- [ ] Unit + integration test suite expanded (services, search strategies, ingestion, MCP, API, basic UI tests) with ≥80% backend coverage and all CI checks passing (`ruff`, `mypy`, `pytest`).

### Task Breakdown

1. **Service Naming Alignment**
   - Rename `api` service to `backend` in `infra/rag-service/docker-compose.yml` and adjust health checks, container names, and frontend dependencies.

2. **MCP Server Repair & Migration**
   - Instantiate `openai.AsyncOpenAI` using env config and inject into `EmbeddingService`.
   - Update Base/Hybrid strategy constructors in `mcp_server.py` to match definitions.
   - Switch FastMCP to streamable HTTP, expose MCP port/env vars, and update docs/configs.
   - Smoke-test MCP tools (search/document/source) ensuring JSON responses and hybrid toggle.

3. **Crawl4AI Integration**
   - Add Crawl4AI client wrapper with Playwright setup, rate limiting, and retries.
   - Extend ingestion flow to handle crawl jobs (create/list/status/abort) via `crawl_jobs` and `sources` tables.
   - Store crawl artifacts, feed them into Docling/chunking/embedding pipeline, and surface via API + MCP.

4. **REST API Endpoints**
   - Implement FastAPI routers for documents, sources, search, and crawl jobs with request/response models, pagination, error handling, and dependency injection.
   - Add OpenAPI tags/docs and align with frontend expectations.

5. **Frontend Experience**
   - Build document upload UI (file picker, source selector, progress, error states).
   - Implement search results view (query input, list with scores/snippets, filters, pagination) and source/crawl management screens.
   - Wire to REST endpoints and add minimal unit/component tests.

6. **Hybrid Search Enablement**
   - Surface `USE_HYBRID_SEARCH` configuration, expose toggles via API/MCP, add logging for combined scores, and validate fallback behaviour.

7. **Embedding Cache Alignment**
   - Add missing `text_preview` column to `embedding_cache` (or remove from insert), ensure cache hit/miss logs, and cover with tests.

8. **Testing & Tooling**
   - Add pytest coverage for services, strategies, ingestion, MCP, and API routes.
   - Introduce MCP integration tests and UI smoke tests (e.g., Playwright/component-level).
   - Document command sequence (`ruff check .`, `mypy .`, `pytest -v`) and ensure they pass locally.

### Risks & Mitigations

- **Playwright/Crawl4AI setup failures** — provide bootstrap script and Docker instructions, cache browser binaries in image or document manual step.
- **OpenAI quota/rate limits** — reuse EmbeddingService backoff, ensure crawl ingestion batches respect limits, add configuration for local embedding fallback if needed.
- **Performance regressions** — log ingestion/search latency and add benchmarks where possible (hybrid vs vector-only, crawl throughput).

### Validation Checklist

- Run `ruff check .`, `mypy .`, and `pytest -v` under `infra/rag-service/` before completion.
- Manual validation: ingest uploaded file, crawl site, run vector+hybrid searches via API + MCP, verify frontend displays results, confirm cache stats in logs, and ensure Docker Compose stack is stable across restarts.

