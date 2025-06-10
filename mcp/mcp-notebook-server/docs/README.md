# INMPARA Notebook MCP Server

> **Intelligent automatic knowledge capture with INMPARA methodology and AI-powered filing**

## Overview

The INMPARA Notebook MCP Server provides seamless, automatic knowledge capture from conversations, transforming insights into perfectly formatted INMPARA notes. It monitors conversations for technical insights, patterns, and discoveries, then automatically creates structured notes that integrate into your INMPARA knowledge management system.

### Key Features

✅ **Phase 1 Implementation Complete**
- **Intelligent conversation monitoring** - Automatic insight detection without explicit commands
- **Perfect INMPARA formatting** - Proper frontmatter, semantic markup, and folder structure
- **High-confidence auto-filing** - Creates notes automatically when confident, suggests when uncertain
- **Real-time connection suggestions** - Shows related existing notes during conversations
- **Cross-session context tracking** - Maintains conversation context for better insights
- **Learning from feedback** - Improves classification accuracy over time

### Architecture

- **Hybrid Database**: SQLite for metadata + Qdrant for semantic search
- **Content Analysis Pipeline**: Multi-stage classification and confidence scoring
- **Template Engine**: INMPARA-compliant note generation
- **Vector Search**: Semantic similarity and connection discovery
- **File Management**: Vault structure maintenance and operations

## Quick Start

### 1. Prerequisites

```bash
# Required: Docker for Qdrant vector database
docker --version

# Required: Python 3.11+
python3 --version
```

### 2. Clone and Setup

```bash
cd /workspace/vibes/mcp/mcp-notebook-server

# Install dependencies and start services
./build.sh

# Configure environment (edit as needed)
cp .env.example .env
```

### 3. Start Server

```bash
# Start the MCP server
python3 main.py

# Or for development
python3 -m src.server
```

### 4. Test Basic Functionality

```bash
# Run comprehensive tests
python3 test_basic_functionality.py
```

## Integration with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "inmpara-notebook": {
      "command": "python3",
      "args": ["/workspace/vibes/mcp/mcp-notebook-server/main.py"],
      "env": {
        "INMPARA_VAULT_PATH": "/workspace/vibes/repos/inmpara"
      }
    }
  }
}
```

## Phase 1 MCP Tools

### Core Automation Tools

#### `capture_conversation_insight`
**Purpose**: Intelligent automatic insight detection during chat
- Monitors conversation for technical findings, insights, patterns, requirements  
- Auto-creates INMPARA-formatted notes when confidence >80%
- Suggests note creation for medium confidence (60-80%)
- Connects to existing vault content automatically

**Parameters**:
```json
{
  "conversation_text": "I found that Azure Databricks requires...",
  "user_id": "user",
  "session_id": "optional-session-id"
}
```

**Auto-Creation Triggers**:
- Technical discoveries: "Azure private endpoints need...", "Found that Terraform..."
- Problem-solution pairs: "The issue was..." → "Solution is..."
- Learning moments: "I learned that...", "Key insight is..."

#### `auto_create_note`
**Purpose**: Background note creation with perfect INMPARA formatting
- Generates proper frontmatter with all required fields
- Applies semantic markup ([technical-finding], [insight], etc.)
- Auto-assigns appropriate tags based on content analysis
- Creates relations to existing notes
- Files in correct INMPARA folder based on content type

**Parameters**:
```json
{
  "content": "Note content here",
  "title": "Optional title override",
  "content_type": "note|moc|project|area|resource",
  "domain": "azure|terraform|dns|etc",
  "context": "Additional context",
  "source_type": "conversation|manual|inbox"
}
```

### Search & Discovery Tools

#### `search_semantic`
**Purpose**: Vector similarity search for concept exploration
- Embed query and find semantically similar content
- Cross-reference vector similarity with metadata
- Return related concepts even with different terminology

#### `suggest_connections`
**Purpose**: Real-time connection discovery during conversation
- Analyze current conversation context
- Find existing notes that relate to current topic
- Display relationship confidence scores

#### `search_exact`
**Purpose**: Traditional text search for specific terms
- Search across all vault content
- Support quoted phrases and boolean operators
- Return file paths, matched content snippets, relevance scores

### Management Tools

#### `get_inbox_items`
**Purpose**: Preview pending items with analysis preview
- List all files in 0 - Inbox/ with metadata
- Show preliminary analysis and confidence scores
- Preview suggested destinations and reasoning

#### `get_recent_insights`
**Purpose**: Show recent conversation insights with processing status
- Display insights detected in recent conversations
- Show which insights became notes vs suggestions
- Track processing confidence and outcomes

#### `start_conversation_session`
**Purpose**: Start new conversation session for insight tracking
- Returns session ID for context tracking across messages
- Enables cross-message insight correlation
- Maintains conversation context for better analysis

### Utility Tools

#### `validate_inmpara_format`
**Purpose**: Ensure notes follow INMPARA standards
- Check frontmatter completeness and format
- Validate semantic markup syntax
- Verify folder placement matches content type

#### `get_vault_analytics`
**Purpose**: Provide insights about knowledge base growth
- Content distribution across INMPARA folders
- Tag usage patterns and domain evolution
- Processing statistics and confidence trends

## Configuration

### Environment Variables

```bash
# Vault Configuration
INMPARA_VAULT_PATH=/workspace/vibes/repos/inmpara
INBOX_FOLDER="0 - Inbox"
NOTES_FOLDER="1 - Notes"
MOCS_FOLDER="2 - MOCs"
PROJECTS_FOLDER="3 - Projects"
AREAS_FOLDER="4 - Areas"
RESOURCES_FOLDER="5 - Resources"
ARCHIVE_FOLDER="6 - Archive"

# Database Configuration
SQLITE_DB_PATH=./data/inmpara_vault.db
QDRANT_HOST=localhost
QDRANT_PORT=6334
QDRANT_COLLECTION=inmpara_vault

# Processing Configuration
AUTO_FILE_THRESHOLD=0.85
INSIGHT_DETECTION_THRESHOLD=0.8
SUGGESTION_THRESHOLD=0.6
```

### Confidence Thresholds

- **Auto-Create Threshold (0.8)**: Insights above this confidence automatically become notes
- **Suggestion Threshold (0.6)**: Insights above this threshold generate suggestions
- **Auto-File Threshold (0.85)**: Inbox items above this confidence are automatically filed

## Example Usage

### Automatic Insight Capture

```markdown
User: "I discovered that Azure Databricks requires specific DNS configuration for private endpoints. The issue was that the private DNS zone wasn't properly linked to the VNet. Found that you need to create an A record mapping the workspace URL to the private endpoint IP."

Response: 📝 Auto-created note: **Azure Databricks Private Endpoint DNS Configuration**
```

**Generated Note**:
```yaml
---
title: Azure Databricks Private Endpoint DNS Configuration
type: note
tags:
  - dns
  - azure
  - databricks
  - networking
  - troubleshooting
created: 2025-06-10
updated: 2025-06-10
status: active
stage: 1-notes
domain: dns
permalink: 1-notes/azure-databricks-private-endpoint-dns-configuration
---

# Azure Databricks Private Endpoint DNS Configuration

## Content
Discovered that Azure Databricks requires specific DNS configuration for private endpoints. The issue was that the private DNS zone wasn't properly linked to the VNet. Found that you need to create an A record mapping the workspace URL to the private endpoint IP.

## Context
Captured from conversation on 2025-06-10

## Observations
- [technical-finding] Azure Databricks requires specific DNS configuration for private endpoints #azure #dns
- [issue] Private DNS zone wasn't properly linked to the VNet #networking #troubleshooting
- [solution] Create A record mapping workspace URL to private endpoint IP #dns #databricks

## Relations
- part_of [[Azure Infrastructure MOC]]
- relates_to [[Azure Private Endpoint Best Practices]]
- solves [[Databricks Connectivity Issues]]

## Related Knowledge
- [[Azure Networking MOC]]
- [[DNS Configuration Patterns]]
- [[Private Endpoint Troubleshooting]]

## Tags
#dns #azure #databricks #networking #troubleshooting
```

### Connection Suggestions

When discussing related topics, the system automatically suggests connections:

```markdown
💡 You have existing notes about Azure networking: 
- [[Azure VNet Configuration]]
- [[Private Endpoint Best Practices]]
- [[DNS Troubleshooting Guide]]
```

## Database Schema

### Core Tables
- **notes**: Note metadata and tracking
- **tags**: Dynamic tagging system
- **relationships**: Semantic relationships between notes
- **conversation_insights**: Insight detection tracking
- **learning_patterns**: AI learning and improvement
- **user_feedback**: Correction tracking for learning
- **processing_log**: Complete audit trail

### Vector Database
- **Collection**: `inmpara_vault`
- **Dimensions**: 384 (sentence-transformers/all-MiniLM-L6-v2)
- **Distance**: Cosine similarity
- **Metadata**: Full INMPARA frontmatter + content analysis

## Development

### Project Structure
```
mcp-notebook-server/
├── src/
│   ├── server.py              # Main MCP server
│   ├── conversation_monitor.py # Intelligent monitoring
│   ├── content_analyzer.py     # Content classification
│   ├── template_engine.py      # INMPARA note generation
│   ├── database/
│   │   ├── database.py         # SQLite operations
│   │   └── vector_search.py    # Qdrant operations
│   └── utils/
│       └── file_utils.py       # File management
├── main.py                     # Entry point
├── build.sh                    # Setup script
├── docker-compose.yml          # Qdrant service
├── requirements.txt            # Dependencies
└── test_basic_functionality.py # Tests
```

### Running Tests
```bash
# Basic functionality test
python3 test_basic_functionality.py

# Content analysis test
python3 -c "
import sys; sys.path.insert(0, 'src')
from content_analyzer import INMPARAContentAnalyzer
analyzer = INMPARAContentAnalyzer()
result = analyzer.analyze_content('Azure requires DNS configuration')
print(f'Analysis: {result.title} -> {result.destination_folder}')
"
```

### Adding New Tools

1. Add tool definition in `src/server.py` using `@self.server.tool()`
2. Implement logic using existing components (analyzer, template_engine, etc.)
3. Add to documentation and tests
4. Update version in docker-compose.yml

## Roadmap

### Phase 2: Intelligence (Coming Soon)
- Advanced semantic search with filters
- Cross-conversation context tracking  
- Learning from user corrections
- Improved confidence scoring

### Phase 3: Automation (Future)
- Complete inbox processing pipeline
- Bulk reprocessing and quality improvements
- Advanced analytics and reporting
- Knowledge graph visualization

## Troubleshooting

### Common Issues

**Database locked error**:
```bash
# Stop all processes using the database
pkill -f inmpara
rm -f ./data/inmpara_vault.db-wal ./data/inmpara_vault.db-shm
```

**Qdrant connection failed**:
```bash
# Start Qdrant service
docker-compose up -d qdrant

# Check health
curl http://localhost:6334/health
```

**Import errors**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"
```

## Support

- **Documentation**: See `TODO.md` for complete specification
- **Issues**: Check logs in `./data/` directory
- **INMPARA Standards**: See `/workspace/vibes/repos/inmpara/99 - Meta/`

---

**Built for seamless AI-enhanced knowledge management with complete INMPARA compliance.**
