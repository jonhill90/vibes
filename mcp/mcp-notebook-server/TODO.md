# INMPARA Notebook MCP Server - Complete Implementation Specification

> **Vision**: Intelligent automatic knowledge capture with INMPARA methodology and AI-powered filing
> **Status**: STARTING FROM SCRATCH - All previous implementations deleted
> **Core Principle**: Create INMPARA-formatted notes with intelligent automatic knowledge capture

## Context for Future Sessions

### Critical Paths & Resources
```
/workspace/vibes/repos/inmpara/                           # User's actual INMPARA vault
├── 0 - Inbox/                                           # Items to be processed daily
├── 1 - Notes/                                           # Atomic notes (auto-filed)
├── 2 - MOCs/                                            # Maps of Content  
├── 3 - Projects/                                        # Active initiatives
├── 4 - Areas/                                           # Ongoing responsibilities
├── 5 - Resources/                                       # Reference materials
├── 6 - Archive/                                         # Completed items
└── 99 - Meta/
    ├── inmpara-formatting-standards.md                  # COMPLETE formatting specification
    └── methodological-foundations.md                    # INMPARA methodology explanation

/workspace/vibes/mcp/mcp-notebook-server/                # Clean implementation directory
└── TODO.md                                             # This specification file
```

### User Profile & Requirements
- **Experience Level**: Starting fresh with INMPARA - NO existing notes to learn from
- **Daily Workflow**: Dump content in inbox + chat insights → AI processes daily on command
- **Trust Model**: High confidence auto-filing, detailed explanations for failures
- **Integration**: Must work exactly like  for seamless conversation capture
- **Knowledge Domains**: Azure, Terraform, DNS, infrastructure, automation, networking

---

## Complete MCP Tool Specification

### 🤖 Core Automation Tools (Primary Workflow)

#### `process_inbox`
**Purpose**: Daily batch processing of 0 - Inbox folder  
**Behavior**: 
- Analyze all .md files in `/workspace/vibes/repos/inmpara/0 - Inbox/`
- Auto-file items with confidence >85% to appropriate INMPARA folders
- Leave unclear items with detailed suggestions and confidence scores
- Generate processing report with explanations for all decisions

**Parameters**:
```json
{
  "auto_file_threshold": 0.85,
  "include_suggestions": true,
  "dry_run": false
}
```

**Output**: Processing report with file movements, confidence scores, and reasoning

---

#### `capture_conversation_insight` 
**Purpose**:  automatic insight detection during chat  
**Behavior**:
- Monitor conversation for technical findings, insights, patterns, requirements
- Auto-create INMPARA-formatted notes when confidence >80%
- Suggest note creation for medium confidence (60-80%)
- Connect to existing vault content automatically

**Trigger Patterns**:
- Technical discoveries: "Azure private endpoints need...", "Found that Terraform..."
- Problem-solution pairs: "The issue was..." → "Solution is..."
- Learning moments: "I learned that...", "Key insight is..."
- References: "This article explains...", "Documentation shows..."

**Auto-Creation Logic**:
```
IF technical_finding AND confidence >80% → Auto-create note
IF insight/pattern AND confidence >75% → Auto-create note  
IF requirement/constraint AND confidence >85% → Auto-create note
ELSE → Suggest note creation with explanation
```

---

#### `auto_create_note`
**Purpose**: Background note creation with perfect INMPARA formatting  
**Behavior**:
- Generate proper frontmatter with all required fields
- Apply semantic markup ([technical-finding], [insight], etc.)
- Auto-assign appropriate tags based on content analysis
- Create relations to existing notes
- File in correct INMPARA folder based on content type

**Content Analysis Pipeline**:
1. **Content Classification**: note/moc/project/area/resource
2. **Domain Detection**: azure, terraform, dns, infrastructure, etc.
3. **Semantic Markup**: Extract observations with proper categories
4. **Relation Inference**: Find connections to existing vault content
5. **Tag Generation**: Primary domain + content type + technology + specifics

---

### 🔍 Search & Discovery Tools

#### `search_exact`
**Purpose**: Traditional text search for specific terms  
**Behavior**: 
- Search across all vault content (excluding 0 - Inbox)
- Support quoted phrases, boolean operators
- Return file paths, matched content snippets, relevance scores
- Include frontmatter field matching

**Parameters**:
```json
{
  "query": "private endpoint dns",
  "folders": ["1 - Notes", "2 - MOCs"],
  "include_frontmatter": true,
  "limit": 20
}
```

---

#### `search_semantic`
**Purpose**: Vector similarity search for concept exploration  
**Behavior**:
- Embed query and find semantically similar content
- Cross-reference vector similarity with metadata
- Return related concepts even with different terminology
- Suggest broader/narrower search terms

**Parameters**:
```json
{
  "query": "networking troubleshooting",
  "similarity_threshold": 0.7,
  "content_types": ["note", "moc"],
  "limit": 15
}
```

---

#### `find_related`
**Purpose**: Show connections when creating/discussing content  
**Behavior**:
- Analyze current conversation context
- Find existing notes that relate to current topic
- Suggest potential connections during note creation
- Display relationship confidence scores

**Real-time Triggers**:
- During conversation about topics with existing notes
- When creating new notes (suggest relations)
- When processing inbox items (show similar content)

---

### 📊 Intelligence & Learning Tools

#### `suggest_connections`
**Purpose**: Real-time connection discovery during conversation  
**Behavior**:
- Monitor conversation for topics matching existing vault content
- Interrupt with "BTW, you already have notes about X" notifications
- Suggest creating relations between current topic and existing notes
- Propose MOC creation when related notes accumulate

**Notification Triggers**:
```
IF conversation_topic matches existing_note_domain AND confidence >70%
→ "You have existing notes about [topic]: [[Note1]], [[Note2]]"

IF related_notes_count >5 AND no_moc_exists
→ "Consider creating a MOC for [domain] - you have [count] related notes"
```

---

#### `learn_from_feedback`
**Purpose**: Update patterns based on user corrections  
**Behavior**:
- Track when user moves auto-filed notes to different folders
- Monitor manual tag changes on auto-created notes
- Adjust confidence thresholds based on success rates
- Update domain/content classification patterns

**Learning Triggers**:
- File moved from auto-destination → Learn filing pattern
- Tags modified on auto-created note → Learn tagging pattern  
- Note content edited → Learn template preferences
- Relation added/removed → Learn connection patterns

**Feedback Loop**:
```
User Action → Pattern Update → Confidence Adjustment → Improved Auto-Filing
```

---

### 📋 Review & Management Tools

#### `review_recent_auto_filings`
**Purpose**: Show what AI processed recently with audit trail  
**Behavior**:
- Display all auto-created/auto-filed content from last N days
- Show original source, destination, confidence scores, reasoning
- Enable bulk approval/rejection of recent actions
- Provide "undo" functionality for recent auto-filings

**Output Format**:
```
Recent Auto-Filings (Last 7 Days):
✅ [Note] azure-private-endpoint-fix.md → 1 - Notes/ (Confidence: 92%)
   Source: Conversation insight about DNS resolution
   Reasoning: Technical finding with clear Azure domain

⚠️  [Note] terraform-best-practices.md → 5 - Resources/ (Confidence: 68%)
   Source: Inbox processing
   Reasoning: General information, could be Note or Resource
   
Action: [Approve All] [Review Uncertain] [Undo Recent]
```

---

#### `get_filing_suggestions`
**Purpose**: Manual analysis of any content for filing decisions  
**Behavior**:
- Analyze provided content (text, file path, or URL)
- Return detailed filing recommendation with reasoning
- Show confidence scores for each possible destination
- Suggest frontmatter and semantic markup

**Analysis Output**:
```
Content: "Azure Databricks private endpoint configuration..."

Recommendations:
1. 1 - Notes/ (Confidence: 87%)
   - Content Type: note  
   - Domain: azure
   - Tags: azure, databricks, private-endpoints, networking
   - Semantic Markup: [technical-finding], [requirement]
   - Relations: relates_to [[Azure Networking MOC]]

2. 5 - Resources/ (Confidence: 23%)
   - Reasoning: Could be reference material, but contains specific findings
```

---

#### `get_inbox_items`
**Purpose**: Preview pending items with analysis preview  
**Behavior**:
- List all files in 0 - Inbox/ with metadata
- Show preliminary analysis and confidence scores
- Preview suggested destinations and reasoning
- Enable selective processing

**Preview Format**:
```
Inbox Contents (3 items):

📄 terraform-state-locking.md (Created: 2025-06-10)
   Preview: Technical finding about state locking best practices
   Suggested: 1 - Notes/ (Confidence: 91%)
   Domain: terraform, devops
   
📄 azure-networking-resources.md (Created: 2025-06-09)  
   Preview: Collection of networking documentation links
   Suggested: 5 - Resources/ (Confidence: 78%)
   Domain: azure, networking
   
📄 meeting-notes-project-kickoff.md (Created: 2025-06-08)
   Preview: Project planning and action items
   Suggested: 3 - Projects/ (Confidence: 85%)
   Domain: project-management
```

---

#### `update_knowledge_relations`
**Purpose**: Build semantic connections between notes  
**Behavior**:
- Analyze vault content to discover implicit relationships
- Suggest new relation types based on content analysis
- Update existing relations with improved confidence scores
- Generate relation reports for knowledge graph visualization

**Relation Discovery**:
- **Content Similarity**: Notes discussing similar technical topics
- **Problem-Solution**: Issues paired with their solutions  
- **Hierarchical**: Part-of relationships for MOC organization
- **Sequential**: Process steps or learning progressions
- **Cross-Domain**: Connections between different knowledge areas

---

#### `bulk_reprocess`
**Purpose**: Re-analyze content with updated intelligence  
**Behavior**:
- Re-run analysis on specified date ranges or folders
- Apply updated confidence thresholds and patterns
- Generate comparison reports (old vs new analysis)
- Enable batch acceptance of improved classifications

**Use Cases**:
- After major pattern learning updates
- When confidence thresholds are adjusted
- For quality assurance audits
- Post-feedback integration

---

### 🔧 Utility & Maintenance Tools

#### `validate_inmpara_format`
**Purpose**: Ensure all notes follow INMPARA standards  
**Behavior**:
- Check frontmatter completeness and format
- Validate semantic markup syntax
- Verify folder placement matches content type
- Generate compliance reports with fix suggestions

---

#### `generate_vault_analytics`
**Purpose**: Provide insights about knowledge base growth  
**Behavior**:
- Content distribution across INMPARA folders
- Tag usage patterns and domain evolution
- Relation network analysis and knowledge clusters
- Growth trends and processing statistics

---

#### `export_knowledge_graph`
**Purpose**: Generate visualization data for external tools  
**Behavior**:
- Export relations in standard graph formats (JSON, GraphML)
- Include node metadata (content type, domains, confidence)
- Generate Obsidian-compatible graph data
- Create summary statistics

---

## Technical Implementation Details

### Database Schema Design

#### Core Tables
```sql
-- Note metadata and tracking
CREATE TABLE notes (
    id TEXT PRIMARY KEY,              -- UUID for note
    title TEXT NOT NULL,              -- From frontmatter
    file_path TEXT UNIQUE,            -- Relative to vault root
    content_type TEXT,                -- note/moc/project/area/resource
    domain TEXT,                      -- Primary domain (azure, terraform, etc.)
    created_date DATE,                -- From frontmatter
    modified_date DATE,               -- File system timestamp
    confidence_score REAL,            -- Auto-filing confidence
    source_type TEXT,                 -- conversation/inbox/manual
    word_count INTEGER,               -- Content statistics
    character_count INTEGER,
    content_hash TEXT,                -- For change detection
    last_processed DATE               -- Last analysis timestamp
);

-- Dynamic tagging system
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id TEXT,                     -- Reference to notes.id
    tag TEXT,                         -- Tag value (azure, dns, etc.)
    tag_type TEXT,                    -- domain/content_type/technology/semantic
    confidence REAL DEFAULT 1.0,     -- Tag assignment confidence
    source TEXT,                      -- auto/manual/learned
    created_date DATE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id)
);

-- Semantic relationships
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_note_id TEXT,              -- Source note ID
    target_note_id TEXT,              -- Target note ID (may not exist yet)
    relationship_type TEXT,           -- relates_to/part_of/solves/enables/etc.
    confidence REAL DEFAULT 1.0,     -- Relationship confidence
    context TEXT,                     -- Surrounding text where found
    source TEXT,                      -- auto/manual/suggested
    created_date DATE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_note_id) REFERENCES notes(id)
);

-- Conversation insights tracking
CREATE TABLE conversation_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,                  -- Chat session identifier
    insight_text TEXT,                -- Original conversation text
    note_id TEXT,                     -- Created note (if any)
    confidence REAL,                  -- Insight detection confidence
    insight_type TEXT,                -- technical-finding/insight/pattern/etc.
    domains TEXT,                     -- JSON array of detected domains
    created_date DATE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (note_id) REFERENCES notes(id)
);

-- Learning and feedback tracking
CREATE TABLE learning_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT,                -- filing/tagging/relation/content_type
    pattern_data TEXT,                -- JSON pattern definition
    confidence REAL,                  -- Pattern reliability
    usage_count INTEGER DEFAULT 1,   -- How often pattern used
    success_rate REAL,                -- User approval rate
    last_updated DATE DEFAULT CURRENT_TIMESTAMP
);

-- User feedback and corrections
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT,                 -- file_moved/tag_changed/relation_added/etc.
    original_value TEXT,              -- What AI suggested
    corrected_value TEXT,             -- What user changed it to
    note_id TEXT,                     -- Associated note
    confidence_impact REAL,           -- How this affects confidence
    feedback_date DATE DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,  -- Whether learning was updated
    FOREIGN KEY (note_id) REFERENCES notes(id)
);

-- Processing audit trail
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,                      -- process_inbox/auto_create/etc.
    source_path TEXT,                 -- Original file/conversation
    destination_path TEXT,            -- Where it was filed
    confidence REAL,                  -- Decision confidence
    reasoning TEXT,                   -- Why this decision was made
    user_approved BOOLEAN,            -- User feedback on action
    timestamp DATE DEFAULT CURRENT_TIMESTAMP
);
```

### Vector Database Schema

#### Qdrant Collection Configuration
```python
collection_config = {
    "collection_name": "inmpara_vault",
    "vector_size": 384,               # sentence-transformers/all-MiniLM-L6-v2
    "distance": "Cosine",
    "payload_schema": {
        "file_path": "keyword",       # Exact file path matching
        "title": "text",              # Searchable title
        "content_type": "keyword",    # note/moc/project/area/resource
        "domain": "keyword",          # azure/terraform/dns/etc.
        "tags": "keyword[]",          # Array of tags
        "created_date": "datetime",   # Temporal filtering
        "confidence": "float",        # Quality filtering
        "semantic_markup": "text[]",  # Observation types
        "relations": "keyword[]"      # Relationship targets
    }
}
```

#### Vector Search Strategies
```python
# Semantic similarity search
semantic_search = {
    "vector": query_embedding,
    "filter": {
        "must": [
            {"key": "content_type", "match": {"value": "note"}},
            {"key": "confidence", "range": {"gte": 0.7}}
        ]
    },
    "limit": 15,
    "with_payload": True
}

# Hybrid search (semantic + metadata)
hybrid_search = {
    "vector": query_embedding,
    "filter": {
        "must": [
            {"key": "domain", "match": {"any": ["azure", "networking"]}},
            {"key": "created_date", "range": {"gte": "2025-01-01"}}
        ]
    }
}
```

### File System Integration

#### Vault Structure Monitoring
```python
# Watch for changes in INMPARA vault
vault_watcher = {
    "base_path": "/workspace/vibes/repos/inmpara/",
    "watch_patterns": ["*.md"],
    "ignore_patterns": ["README*.md", ".obsidian/**"],
    "events": ["created", "modified", "moved", "deleted"],
    "handler": "update_database_on_change"
}

# Folder mapping for auto-filing
folder_mapping = {
    "0 - Inbox": "inbox",             # Temporary holding
    "1 - Notes": "note",              # Atomic insights
    "2 - MOCs": "moc",                # Knowledge maps
    "3 - Projects": "project",        # Active work
    "4 - Areas": "area",              # Ongoing responsibilities
    "5 - Resources": "resource",      # Reference materials
    "6 - Archive": "archive",         # Completed/inactive
    "99 - Meta": "meta"               # System files
}
```

### INMPARA Template Engine

#### Frontmatter Generation
```python
def generate_frontmatter(content_analysis):
    """Generate INMPARA-compliant frontmatter"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter = {
        "title": content_analysis.title,
        "type": content_analysis.content_type,
        "tags": content_analysis.tags,           # [domain, type, tech, specifics]
        "created": timestamp,
        "updated": timestamp,
        "status": "active",
        "stage": f"{content_analysis.stage_number}-{content_analysis.content_type}s",
        "domain": content_analysis.primary_domain,
        "permalink": f"{content_analysis.stage_number}-{content_analysis.content_type}s/{content_analysis.slug}"
    }
    
    return yaml.dump(frontmatter, default_flow_style=False)
```

#### Content Structure Templates
```python
note_template = """---
{frontmatter}---

# {title}

## Content
{content}

## Observations
{observations}

## Relations
{relations}

## Related Knowledge
{related_knowledge}

## Tags
{tag_string}
"""

# Observation formatting
observation_templates = {
    "technical-finding": "- [technical-finding] {text} #{tags}",
    "insight": "- [insight] {text} #{tags}",
    "pattern": "- [pattern] {text} #{tags}",
    "requirement": "- [requirement] {text} #{tags}",
    "issue": "- [issue] {text} #{tags}",
    "constraint": "- [constraint] {text} #{tags}"
}
```

### Content Analysis Pipeline

#### Multi-Stage Analysis Process
```python
class ContentAnalyzer:
    def analyze_content(self, text, context=None):
        """Complete content analysis pipeline"""
        
        # Stage 1: Basic classification
        content_type = self.classify_content_type(text)
        primary_domain = self.detect_domain(text)
        
        # Stage 2: Semantic extraction
        observations = self.extract_observations(text)
        relations = self.infer_relations(text, context)
        
        # Stage 3: Metadata generation
        tags = self.generate_tags(content_type, primary_domain, observations)
        title = self.generate_title(text, content_type)
        
        # Stage 4: Confidence scoring
        confidence = self.calculate_confidence(
            content_type, primary_domain, observations, relations
        )
        
        # Stage 5: Filing recommendation
        destination = self.recommend_filing(content_type, confidence)
        
        return AnalysisResult(
            content_type=content_type,
            primary_domain=primary_domain,
            observations=observations,
            relations=relations,
            tags=tags,
            title=title,
            confidence=confidence,
            destination=destination
        )
```

#### Pattern Learning Engine
```python
class PatternLearner:
    def learn_from_feedback(self, original_decision, user_correction):
        """Update patterns based on user corrections"""
        
        # Extract pattern from correction
        if user_correction.action == "moved_file":
            self.update_filing_pattern(
                content_features=original_decision.features,
                correct_destination=user_correction.new_location,
                confidence_adjustment=-0.1
            )
            
        elif user_correction.action == "changed_tags":
            self.update_tagging_pattern(
                content_features=original_decision.features,
                correct_tags=user_correction.new_tags
            )
            
        # Recalculate confidence thresholds
        self.adjust_confidence_thresholds()
```

###  Integration Pattern

#### Conversation Monitoring
```python
class ConversationMonitor:
    def __init__(self):
        self.insight_patterns = [
            r"(?i)(the issue was|i found that|turns out|discovered that)",
            r"(?i)(key insight|important to note|learned that)",
            r"(?i)(azure .+ requires|terraform .+ needs)",
            r"(?i)(solution is|fix was|workaround is)"
        ]
        
    def detect_insights(self, conversation_text):
        """Detect conversation insights like """
        insights = []
        
        for pattern in self.insight_patterns:
            matches = re.finditer(pattern, conversation_text)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 100)
                end = min(len(conversation_text), match.end() + 200)
                context = conversation_text[start:end]
                
                insight = {
                    "text": context,
                    "confidence": self.calculate_insight_confidence(context),
                    "type": self.classify_insight_type(context),
                    "domains": self.extract_domains(context)
                }
                
                if insight["confidence"] > 0.6:
                    insights.append(insight)
                    
        return insights
```

#### Auto-Creation Logic
```python
class AutoNoteCreator:
    def process_conversation_insight(self, insight):
        """Create INMPARA note from conversation insight"""
        
        if insight.confidence > 0.8:
            # High confidence - auto-create
            note = self.create_note(insight)
            self.file_note(note)
            return f"📝 Auto-created note: {note.title}"
            
        elif insight.confidence > 0.6:
            # Medium confidence - suggest
            suggestion = self.generate_suggestion(insight)
            return f"💡 Suggestion: {suggestion}"
            
        else:
            # Low confidence - ignore
            return None
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic  conversation monitoring with INMPARA output

**Deliverables**:
- [ ] `capture_conversation_insight` - Basic insight detection
- [ ] `auto_create_note` - INMPARA template generation
- [ ] Basic database schema with notes and tags tables
- [ ] File system integration with vault monitoring
- [ ] Simple confidence scoring (rule-based)

**Success Criteria**:
- Detect technical findings from conversation
- Create properly formatted INMPARA notes
- File notes in correct folders based on content type

### Phase 2: Intelligence (Week 3-4)
**Goal**: Smart search, learning, and cross-conversation context

**Deliverables**:
- [ ] `search_semantic` - Vector similarity search
- [ ] `suggest_connections` - Real-time relation discovery
- [ ] `learn_from_feedback` - Pattern learning from corrections
- [ ] Conversation context tracking across sessions
- [ ] Improved confidence scoring with learning

**Success Criteria**:
- Find related content during conversations
- Learn from user corrections to improve filing
- Connect insights across multiple chat sessions

### Phase 3: Automation (Week 5-6)
**Goal**: Complete inbox processing and advanced analytics

**Deliverables**:
- [ ] `process_inbox` - Full batch processing pipeline
- [ ] `review_recent_auto_filings` - Audit and approval workflow
- [ ] `bulk_reprocess` - Quality improvement tools
- [ ] Advanced analytics and reporting
- [ ] Knowledge graph visualization export

**Success Criteria**:
- User can dump content in inbox and trust AI processing
- Complete audit trail for all AI decisions
- System improves over time with usage

## Quality Assurance Checklist

### INMPARA Compliance
- [ ] All notes have complete frontmatter with required fields
- [ ] Semantic markup follows exact patterns from user's standards
- [ ] File naming uses timestamp-title format
- [ ] Folder placement matches content type classification
- [ ] Tag hierarchy follows domain → type → technology → specifics
- [ ] Relations use standard relationship types

###  Behavior
- [ ] Insights detected automatically without explicit commands
- [ ] Cross-conversation context maintained and utilized
- [ ] Real-time suggestions provided during relevant discussions
- [ ] Seamless integration without interrupting conversation flow

### Technical Requirements
- [ ] Vector database separate from  (port 6334)
- [ ] All operations logged with confidence scores
- [ ] Learning patterns updated from user feedback
- [ ] Search performance <2 seconds for typical queries
- [ ] File operations atomic and error-safe

### User Experience
- [ ] High confidence auto-filing trusted without review
- [ ] Clear explanations when AI cannot determine intent
- [ ] Easy correction workflow when AI makes mistakes
- [ ] Non-intrusive notifications about related content
- [ ] Daily processing workflow completes in under 30 seconds

---

## Critical Success Factors

1. **Perfect INMPARA Formatting**: Every auto-created note must follow exact standards
2. **-Level Automation**: User should not think about note creation
3. **Trust-Based Operation**: High confidence decisions must be reliable
4. **Learning Capability**: System must improve from user corrections
5. **Cross-Session Context**: Connect related concepts across conversations
6. **Performance**: Real-time suggestions without conversation lag

## Files to Create

### Core Server Implementation
- [ ] `server.py` - Main MCP server with all tools
- [ ] `content_analyzer.py` - Content classification and analysis
- [ ] `pattern_learner.py` - Learning engine for user feedback
- [ ] `template_engine.py` - INMPARA note generation
- [ ] `conversation_monitor.py` -  insight detection
- [ ] `vector_search.py` - Semantic search implementation
- [ ] `database.py` - SQLite + Qdrant integration

### Configuration & Setup
- [ ] `docker-compose.yml` - Server + dedicated Qdrant instance
- [ ] `requirements.txt` - All dependencies
- [ ] `Dockerfile` - Container configuration
- [ ] `.env.example` - Configuration template
- [ ] `build.sh` - Build and deployment script

### Documentation
- [ ] `README.md` - Setup and usage instructions
- [ ] `DEVELOPMENT.md` - Implementation details and architecture
- [ ] `PATTERNS.md` - Learned patterns and confidence algorithms

---

**NEXT SESSION START HERE:**
1. Read INMPARA standards: `/workspace/vibes/repos/inmpara/99 - Meta/inmpara-formatting-standards.md`
2. Examine user's vault structure: `/workspace/vibes/repos/inmpara/`
3. Begin Phase 1 implementation with `capture_conversation_insight` tool
4. Set up basic database schema and file system integration

**REMEMBER**: This must work exactly like  but create perfectly formatted INMPARA notes. The user wants to completely trust the AI for knowledge capture and filing.

