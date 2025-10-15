# PRP: RAG Service Completion Phase 2

**Generated**: 2025-10-14
**Based On**: prps/INITIAL_rag_service_completion_phase2.md
**Archon Project**: TBD (create at kickoff)

---

## Goal

Deliver the remaining functionality, integrations, and hardening work required to ship the standalone RAG service MVP defined in `prps/rag_service_research/ARCHITECTURE.md`. This phase closes implementation gaps by stabilizing the MCP server (streamable HTTP), adding Crawl4AI-based ingestion, exposing REST + frontend interfaces, aligning the embedding cache, and expanding automated validation so agents and users can ingest, search, and manage knowledge bases end-to-end.

**End State**:
- MCP server reachable over HTTP, tools functioning without runtime errors.
- Crawl4AI pipeline ingests external sites into the Docling → chunk → embed → store flow.
- REST API and frontend deliver upload, crawl, search, and source management experiences.
- Hybrid search toggle exposed via API/MCP with validated fallback behaviour.
- Embedding cache writes succeed; cache metrics available.
- Ruff, mypy, and pytest suites pass with ≥80% backend coverage.

## Why

- **Operational Gaps**: Current MCP server wiring is broken (constructor mismatch, STDIO transport) and prevents tool usage.
- **Feature Completeness**: Architecture requires Crawl4AI ingestion, but no crawler integration exists yet.
- **User Experience**: Frontend scaffolding and REST routes are incomplete, leaving ingestion/search workflows inaccessible.
- **Reliability & Cost**: Embedding cache fails on insert due to schema mismatch; hybrid search is implemented but not surfaced or validated.
- **Quality Gates**: Minimal automated tests leave regressions undetected; coverage and lint/type checks need enforcement.

Shipping this phase unlocks a production-ready knowledge service reusable across projects and enables agents to rely on consistent RAG tooling.

## What

### Workstreams

1. **Service Naming Alignment**
   - Rename `api` service to `backend` throughout `infra/rag-service/docker-compose.yml`, health checks, and dependent docs/scripts.

2. **MCP Server Repair & Migration**
   - Instantiate `openai.AsyncOpenAI` via settings and inject into `EmbeddingService`.
   - Update Base/Hybrid strategy constructor calls in `backend/src/mcp_server.py` to match definitions.
   - Switch FastMCP to streamable HTTP, expose MCP port, document config changes, and revalidate tools.

3. **Crawl4AI Integration**
   - Add Crawl4AI client wrapper (browser setup, retries, rate limits) and ingest outputs into existing Docling/chunk/embedding pipeline.
   - Implement crawl job lifecycle (create/list/status/cancel) using `crawl_jobs` + `sources` tables.
   - Surface crawl management via REST + MCP.

4. **REST API Expansion**
   - Implement FastAPI routers for documents, sources, search, and crawl jobs with schemas, pagination, and error handling.
   - Update OpenAPI docs and align dependency injection with service layer.

5. **Frontend Experience**
   - Build upload workflow, search view (scores, snippets, filters), and source/crawl management UI.
   - Wire frontend to REST endpoints and add component/unit tests.

6. **Hybrid Search Enablement**
   - Expose configuration toggles, return combined scores, log latency metrics, and validate fallback to vector search.

7. **Embedding Cache Alignment**
   - Add missing `text_preview` column (or adjust SQL) so `_cache_embedding` inserts succeed; log cache stats.

8. **Testing & Tooling**
   - Add unit, integration, and MCP smoke tests; increase backend coverage to ≥80%.
   - Document validation workflow (`ruff`, `mypy`, `pytest`) and ensure Docker Compose stack passes health checks.

### Deliverables

- Updated backend source implementing the above workstreams.
- Enhanced frontend (Vite/React) with functional UI flows.
- Documentation updates: README snippets, `.env.example`, MCP config instructions.
- Automated test coverage reports.
- Manifest/log updates reflecting MCP transport change.

## Success Criteria

- [ ] MCP server available at configured HTTP endpoint; `search_knowledge_base`, `manage_document`, and `rag_manage_source` succeed from Claude desktop.
- [ ] Crawl job can be created, processed via Crawl4AI, and ingested into storage with retriable failure handling.
- [ ] REST routes (`/api/documents`, `/api/sources`, `/api/search`, `/api/crawls`) return validated responses with pagination.
- [ ] Frontend allows uploading documents, initiating crawls, and running searches with visible scores and metadata.
- [ ] Hybrid search toggle works across MCP/API, including fallback logging when hybrid disabled or fails.
- [ ] Embedding cache writes succeed without warnings; logs show hit/miss statistics.
- [ ] `ruff check .`, `mypy .`, and `pytest -v` under `infra/rag-service/` pass; pytest coverage ≥80% for backend modules.
- [ ] Docker Compose stack (`docker compose up -d`) stabilizes with healthy services after restart.

## Scope & Out of Scope

**Included**:
- MCP transport change, Crawl4AI ingestion, REST/Frontend completion, hybrid validation, cache fix, testing.

**Excluded**:
- Multi-tenancy features, analytics dashboards, advanced reranking models beyond current code, production deployment automation.

## Implementation Plan (Sequenced)

1. Service rename + documentation sweep.
2. MCP repair/migration (constructor fixes, AsyncOpenAI wiring, HTTP transport).
3. Embedding cache schema alignment (quick win to unblock ingestion).
4. Crawl4AI service + job lifecycle; integrate with ingestion pipeline.
5. REST routers + unit tests.
6. Frontend feature build + integration tests.
7. Hybrid search surfacing + logging/perf validation.
8. Comprehensive testing, lint/type checks, Docker validation, documentation updates.

## Dependencies & References

- `prps/rag_service_research/ARCHITECTURE.md`
- `infra/rag-service/backend/src/mcp_server.py`
- `infra/rag-service/backend/src/services/`
- `infra/rag-service/database/scripts/init.sql`
- `infra/rag-service/docker-compose.yml`
- Crawl4AI docs: https://docs.crawl4ai.com/
- OpenAI Python library: https://platform.openai.com/docs/libraries/python
- FastMCP HTTP pattern: `vibesbox/src/mcp_server.py`

## Testing Strategy

- **Unit Tests**: Services (documents, sources, vector, embeddings), search strategies, Crawl4AI client wrapper, REST routers.
- **Integration Tests**: Ingestion pipeline (Docling + embeddings), hybrid search end-to-end, MCP tool invocations (using HTTP transport), REST API contract tests.
- **Frontend Tests**: Component tests for upload/search flows (React Testing Library), optional Playwright smoke test for full workflow.
- **Regression**: Run `ruff`, `mypy`, `pytest`, and Docker Compose health checks in CI.

## Risks & Mitigations

- **Crawl4AI Playwright setup failures** → Provide install script, pre-download browser binaries, document manual steps.
- **OpenAI rate limit/quota issues** → Reuse EmbeddingService backoff, monitor failures, support local model toggle if needed.
- **Latency regressions from hybrid search** → Add logging + benchmarks comparing vector vs hybrid; allow runtime toggle.
- **Docker resource contention** → Document minimum resource requirements, provide troubleshooting tips.

## Acceptance Checklist

- [ ] MCP manifest updated for HTTP transport, ports exposed in Docker Compose, Claude config documented.
- [ ] Crawl4AI ingest path verified with sample site; failures retriable and logged.
- [ ] REST + MCP endpoints documented in README/addendum with example requests.
- [ ] Frontend demonstrates ingest/search workflows in manual QA pass.
- [ ] Cache alignment verified (no warnings, stats logged).
- [ ] Test commands and coverage report captured in completion notes.
- [ ] Archon tasks moved to review with evidence (test logs, screenshots, PR links).

