# Vibes Development ToDo

> **Current Focus**: Enable Claude Desktop to have visual capabilities for building the system  
> **Priority**: Phase 0 - Setting up the development environment with proper MCP tools

---

## 🚨 Immediate Priority: MCP Tools for Claude Desktop

### Visual/Browser MCP Servers Needed
- [ ] **Screenshot MCP Server**
  - [ ] Research existing MCP servers for screenshots
  - [ ] Test Puppeteer/Playwright MCP capabilities
  - [ ] Set up screenshot workflow for UI feedback

- [ ] **Browser Control MCP Server**
  - [ ] Find/install Puppeteer MCP server
  - [ ] Configure for local development
  - [ ] Test browser automation capabilities

- [ ] **Development Server MCP**
  - [ ] Create/find MCP for running `npm run dev`
  - [ ] Enable hot-reload visibility
  - [ ] Set up process management

---

## 📱 Phase 1: Discord-like UI Development

### Initial UI Setup
- [ ] **Prepare Concept Repo**
  - [ ] Install dependencies in concept folder
  - [ ] Configure Vite for development
  - [ ] Set up Tailwind CSS properly
  - [ ] Test basic UI rendering

- [ ] **Core Layout Components**
  - [ ] Left sidebar for agent selection
  - [ ] Main chat area with proper scrolling
  - [ ] Bottom input area with attachments
  - [ ] Top header with view controls

### Agent UI Components
- [ ] **Agent Icons and Identity**
  - [ ] Design unique icons for each agent type
  - [ ] Implement color coding system
  - [ ] Add status indicators (idle/active/error)
  - [ ] Create hover states and tooltips

- [ ] **Screen Share View**
  - [ ] Split view layout (agent screen + chat)
  - [ ] Terminal/code viewer component
  - [ ] Browser preview component
  - [ ] Resizable panels

---

## 🤖 Phase 2: Agent Architecture

### File Agent (Start Simple)
- [ ] **Basic Implementation**
  - [ ] File listing endpoint
  - [ ] Safe file reading
  - [ ] Directory navigation
  - [ ] File type detection

- [ ] **UI Integration**
  - [ ] File browser component
  - [ ] Preview capabilities
  - [ ] Drag-and-drop support
  - [ ] Permission prompts

### Browser Agent (Lightpanda Integration)
- [ ] **Core Features**
  - [ ] Web page navigation
  - [ ] Element selection
  - [ ] Form filling
  - [ ] Screenshot capture

- [ ] **Observable Execution**
  - [ ] Live browser view
  - [ ] Action highlighting
  - [ ] Step-by-step replay
  - [ ] Error handling

### Code Agent
- [ ] **Execution Environment**
  - [ ] Sandboxed containers
  - [ ] Multi-language support
  - [ ] Output streaming
  - [ ] Error capture

- [ ] **UI Features**
  - [ ] Syntax highlighting
  - [ ] Code diff view
  - [ ] Execution status
  - [ ] Output display

---

## 🔄 Phase 3: Agent Communication

### Message Router
- [ ] **Core Router**
  - [ ] WebSocket server setup
  - [ ] Message protocol definition
  - [ ] Agent registration system
  - [ ] Request/response handling

- [ ] **Smart Routing**
  - [ ] Intent detection
  - [ ] Agent capability matching
  - [ ] Load balancing
  - [ ] Fallback handling

### Memory System
- [ ] **Session Memory**
  - [ ] Conversation history
  - [ ] Context preservation
  - [ ] Agent state tracking
  - [ ] User preferences

- [ ] **Persistent Memory**
  - [ ] SQLite/similar setup
  - [ ] Knowledge indexing
  - [ ] Search capabilities
  - [ ] Privacy controls

---

## 🎙️ Phase 4: Voice Features

### Speech Integration
- [ ] **Speech-to-Text**
  - [ ] Research local STT options
  - [ ] Implement basic recognition
  - [ ] Add wake word detection
  - [ ] Handle multiple languages

- [ ] **Text-to-Speech**
  - [ ] Research local TTS options
  - [ ] Implement voice synthesis
  - [ ] Create agent-specific voices
  - [ ] Add voice controls

---

## ☁️ Phase 5: Cloud LLM Integration

### LLM Router
- [ ] **AWS Bedrock Setup**
  - [ ] Authentication configuration
  - [ ] Model selection logic
  - [ ] Request routing
  - [ ] Cost tracking

- [ ] **Azure OpenAI Setup**
  - [ ] Service configuration
  - [ ] Model deployment
  - [ ] Endpoint management
  - [ ] Usage monitoring

### Security Layer
- [ ] **Data Protection**
  - [ ] Input sanitization
  - [ ] Output validation
  - [ ] Encryption at rest
  - [ ] Audit logging

---

## 🔧 Development Workflow

### For Claude Desktop
- [ ] **Workflow Setup**
  1. [ ] Install browser MCP tools
  2. [ ] Set up screenshot pipeline
  3. [ ] Create feedback loop
  4. [ ] Document the process

### For Development
- [ ] **Environment Setup**
  1. [ ] Create development scripts
  2. [ ] Set up debugging tools
  3. [ ] Configure hot reload
  4. [ ] Create test scenarios

---

## 📊 Success Metrics

### Phase 0 (Current)
- [ ] Claude can see the UI
- [ ] Claude can control browser
- [ ] Development cycle < 30 seconds
- [ ] Basic components working

### MVP (Phases 1-3)
- [ ] 3 working agents
- [ ] Agents can collaborate
- [ ] UI feels responsive
- [ ] Tasks complete end-to-end

### Full Product
- [ ] Voice works naturally
- [ ] Cloud LLMs integrated
- [ ] System learns from use
- [ ] Better than Manus UX

---

## 🚧 Known Issues

### Current Blockers
1. **No MCP browser tools** - Can't see or control UI
2. **No process management** - Can't run dev servers
3. **No visual feedback** - Building blind

### Technical Debt
- [ ] Need proper error handling
- [ ] Need testing framework
- [ ] Need deployment strategy
- [ ] Need documentation

---

*This ToDo list focuses on actionable items to build the Vibes system using Claude Desktop as the primary builder. The key is to solve the visual feedback problem first, then iterate on the UI and agent capabilities.*
