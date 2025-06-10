# INMPARA Notebook MCP Server

🤖 **Intelligent automatic knowledge capture with INMPARA methodology and AI-powered filing**

## 🎯 Project Status

- ✅ **Phase 1**: Basic conversation monitoring and note creation
- ✅ **Phase 2**: Advanced intelligence with learning and cross-session context  
- ✅ **Phase 3**: Complete automation with advanced analytics and batch processing
- 🚀 **Current**: Production ready with full automation + vector search

## 🏗️ Architecture

```
INMPARA MCP Server Stack:
├── 🤖 MCP Server           # INMPARA note processing
├── 🕸️  Qdrant Vector DB    # Semantic search & similarity
├── 🗄️  SQLite Database     # Metadata & learning patterns
└── 📁 INMPARA Vault        # Your knowledge base
```

## 🏗️ Project Structure

```
mcp-notebook-server/
├── 📁 src/                     # Core source code
│   ├── database/               # Database layer (SQLite + Qdrant)
│   ├── phase1_*.py            # Basic functionality
│   ├── phase2_*.py            # Advanced intelligence
│   └── phase3_*.py            # Complete automation
├── 📁 bin/                     # Executable scripts
├── 📁 demos/                   # Feature demonstrations
├── 📁 tests/                   # Test suites
├── 📁 docker/                  # Docker configuration
├── 📁 scripts/                 # Build and deployment scripts
└── 📁 docs/                    # Documentation
```

## 🚀 Quick Start

### 1. Full Stack Deployment (Recommended)
```bash
# Build everything
scripts/build.sh

# Start full stack (MCP Server + Qdrant)
scripts/start-server.sh
```

### 2. Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Qdrant
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.4

# Run server
cd bin/
python3 production_server.py
```

### 3. Test All Features
```bash
cd demos/
python3 demo_phase3.py  # Full automation demo
```

## 🎯 Core Features

### 📥 **Complete Inbox Automation**
- Batch process all files in `00 - Inbox/`
- AI-powered filing with high confidence decisions
- INMPARA methodology compliance
- Learned pattern application

### 🔍 **Vector Search & Semantic Similarity**
- Qdrant vector database for semantic search
- Find related notes automatically
- Content similarity analysis
- Intelligent linking suggestions

### 🔧 **Quality Improvement Tools**
- Bulk reprocessing of existing notes
- Quality enhancement suggestions
- Batch improvement workflows

### 📊 **Advanced Analytics**
- Processing activity analysis
- Learning pattern insights
- Vault structure metrics
- User feedback analytics

### 🕸️ **Knowledge Graph Export**
- JSON format for web applications
- GraphML for network analysis
- Cypher queries for Neo4j
- Multi-format visualization

### 📚 **Intelligent MOC Generation**
- Automatic note clustering
- Smart MOC creation with proper structure
- Domain-based organization
- Confidence-based processing

## 🐳 Docker Services

### Start Full Stack
```bash
cd docker/
docker-compose up -d
```

### Access Services
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Qdrant API**: http://localhost:6333
- **MCP Server**: http://localhost:8000 (future HTTP transport)

### Check Status
```bash
docker-compose ps
docker logs inmpara-mcp-server
docker logs inmpara-qdrant
```

## 📖 Documentation

- [Complete Implementation Docs](docs/)
- [Phase 3 Status](docs/PHASE3_IMPLEMENTATION_COMPLETE.md)
- [TODO & Roadmap](docs/TODO.md)

## 🔧 Development

### Run Tests
```bash
cd tests/
python3 run_tests.py
```

### Demo All Phases
```bash
cd demos/
python3 demo_phase1.py  # Basic features
python3 demo_phase2.py  # Advanced intelligence  
python3 demo_phase3.py  # Complete automation
```

## 📋 Requirements

- Python 3.8+
- Docker & Docker Compose
- SQLite 3
- INMPARA vault structure
- MCP client (Claude Desktop or compatible)

## 🔧 Configuration

Environment variables (see `docker/.env.example`):
- `VAULT_PATH`: Path to your INMPARA vault
- `QDRANT_HOST`: Qdrant server host
- `QDRANT_PORT`: Qdrant gRPC port (6334)
- `ENABLE_VECTOR_SEARCH`: Enable semantic search features

---

**Ready for production use with complete automation + semantic search!** 🎉
