# Feature Analysis: prp_workflow_improvements

## User Request Summary

Improve generate-prp and execute-prp commands by applying INITIAL.md factory patterns

### Clarifications Provided

**Question 1 - Primary Use Case**:
The PRP process (generate-prp and execute-prp commands) currently works but was built manually without systematic research methodology.

Problems to solve:
1. generate-prp doesn't extract actual code examples (just references them)
2. generate-prp doesn't leverage Archon knowledge base for past PRP patterns
3. execute-prp uses sequential execution (slow) instead of parallel
4. execute-prp lacks automated testing and quality gates
5. Neither command has self-improvement capabilities

Users will accomplish:
- Generate higher quality PRPs that are immediately executable
- Execute PRPs faster with parallel task execution
- Get automatic test generation and validation
- Have PRPs learn from past successful implementations
- Create a self-improving PRP workflow

**Question 2 - Technical Preferences**:
Recommend based on what works best, but prefer:
- Use the same patterns as INITIAL.md factory (6 subagents + orchestrator)
- Use Archon MCP tools for research (rag_search, search_code_examples)
- Use parallel execution pattern from factory's Phase 2
- Keep existing .claude/commands/ structure
- Maintain compatibility with current INITIAL.md format
- Use same tools: Read, Write, Grep, Glob, WebSearch, Archon MCP tools

Specifically look at:
- How factory does systematic research (apply to PRP generation)
- How factory extracts examples (apply to generate-prp)
- How factory uses parallel execution (apply to execute-prp)

**Question 3 - Integration Needs**:
Must integrate with:
1. Existing INITIAL.md files (input format stays the same)
2. Archon MCP (project tracking, knowledge base, code examples)
3. Current PRP workflow (output must work with existing PRPs)
4. The INITIAL.md factory itself (for the self-improvement loop)
5. Existing .claude/agents/ directory (new subagents go here)
6. Current examples/ directory structure

Critical: The improved commands should be drop-in replacements for generate-prp.md and execute-prp.md that work with existing workflows.

## Core Requirements

### Explicit Requirements

1. **Code Example Extraction**: generate-prp must extract actual code files to examples/ directory, not just reference them
2. **Archon Integration**: Both commands must leverage Archon knowledge base for research (rag_search, search_code_examples, project tracking)
3. **Parallel Execution**: execute-prp must implement parallel task execution pattern from INITIAL.md factory Phase 2
4. **Automated Testing**: execute-prp must include automated test generation and quality gates
5. **Self-Improvement**: Both commands should learn from past successful implementations stored in Archon
6. **Drop-in Replacement**: Must maintain compatibility with existing INITIAL.md format and PRP workflow
7. **Subagent Architecture**: Apply 6 subagents + orchestrator pattern from INITIAL.md factory

### Implicit Requirements

1. **Research Systematization**: generate-prp needs structured research phases similar to factory (feature analysis, codebase research, documentation hunting, example curation, gotcha detection)
2. **Context Window Management**: Multiple subagents prevent context pollution during research/execution
3. **Quality Metrics**: Need confidence scoring (8+/10) for PRP quality before proceeding to execution
4. **Validation Loops**: execute-prp needs iterative validation at multiple levels (syntax, unit tests, integration tests)
5. **Task Tracking**: Both commands should create and update Archon tasks for progress tracking
6. **Documentation Generation**: Automatic README.md creation for extracted examples with "what to mimic" guidance
7. **Error Recovery**: Graceful handling when Archon unavailable, fallback to web search
8. **Progress Visibility**: User should see clear progress through phases/tasks

## Technical Components

### Data Models

**PRP Generation Workflow State**:
- Feature name (snake_case)
- INITIAL.md file path
- Archon project_id (optional, if available)
- Research phase status (feature_analysis, codebase_research, documentation, examples, gotchas, assembly)
- Quality score (1-10)
- Generated artifacts (list of file paths created)

**PRP Execution Workflow State**:
- PRP file path
- Archon project_id (optional)
- Task breakdown (list of tasks with dependencies)
- Parallel execution groups
- Validation gate results (syntax, unit tests, integration tests)
- Completion status per task

**Subagent Specification**:
- Name (e.g., "prp-gen-codebase-researcher")
- Description
- Tools (list of Claude Code tools)
- Input files (what it reads)
- Output files (what it creates)
- Archon queries (search patterns to use)
- Quality checklist

### External APIs

**Archon MCP Server**:
- `mcp__archon__health_check()` - Check if Archon available
- `mcp__archon__rag_search_knowledge_base(query, match_count)` - Search documentation
- `mcp__archon__rag_search_code_examples(query, match_count)` - Find code patterns
- `mcp__archon__find_projects(query)` - Search existing projects
- `mcp__archon__manage_project(action, ...)` - Create/update projects
- `mcp__archon__find_tasks(filter_by, filter_value)` - Get tasks
- `mcp__archon__manage_task(action, task_id, ...)` - Update task status
- `mcp__archon__manage_document(action, ...)` - Store generated PRPs

**WebSearch** (fallback when Archon unavailable):
- Technology documentation searches
- Code example searches
- Best practices and gotchas

### Processing Logic

**generate-prp Command Logic**:
1. **Phase 0**: Health check Archon, create project with 6 research tasks
2. **Phase 1**: Invoke prp-gen-feature-analyzer subagent (analyzes INITIAL.md, searches Archon for similar PRPs)
3. **Phase 2**: Invoke 3 parallel subagents:
   - prp-gen-codebase-researcher (finds patterns in local code + Archon)
   - prp-gen-documentation-hunter (searches Archon docs + web)
   - prp-gen-example-curator (EXTRACTS code to examples/ directory)
4. **Phase 3**: Invoke prp-gen-gotcha-detective (searches known issues, security concerns)
5. **Phase 4**: Invoke prp-gen-assembler (synthesizes all research into final PRP)
6. **Phase 5**: Quality check (score 8+/10), store in Archon, deliver to user

**execute-prp Command Logic**:
1. **Read PRP**: Parse PRP file, extract task list and validation gates
2. **Task Analysis**: Identify task dependencies, create parallel execution groups
3. **Archon Setup**: Create project, create task for each PRP task
4. **Parallel Execution**:
   - Group independent tasks
   - Execute groups in parallel using multiple subagents
   - Update Archon task status (todo → doing → done)
5. **Validation Loops**: After each task group, run validation gates:
   - Syntax/style checks
   - Unit tests
   - Integration tests
   - Iterate on failures until passing
6. **Test Generation**: Auto-generate tests based on implementation patterns
7. **Completion**: Final validation suite, update all Archon tasks, report results

**Subagent Execution Pattern** (from INITIAL.md factory):
```python
# Parallel invocation in single message
invoke_agents([
    {
        "name": "prp-gen-codebase-researcher",
        "input": "prps/research/feature-analysis.md",
        "output": "prps/research/codebase-patterns.md"
    },
    {
        "name": "prp-gen-documentation-hunter",
        "input": "prps/research/feature-analysis.md",
        "output": "prps/research/documentation-links.md"
    },
    {
        "name": "prp-gen-example-curator",
        "input": "prps/research/feature-analysis.md",
        "output": ["prps/research/examples-to-include.md", "examples/{feature}/*"]
    }
])
```

### UI/CLI Requirements

**Interface Type**: Claude Code commands (slash commands)

**Key Interactions**:
- `/generate-prp prps/INITIAL_{feature}.md` - Triggers improved PRP generation workflow
- Progress updates at each phase ("Phase 1: Feature Analysis... ✓", "Phase 2: Parallel Research... ✓")
- Quality score display ("PRP Quality: 9/10 - Ready for execution")
- File locations summary at completion
- Option to regenerate if quality score < 8/10

- `/execute-prp prps/{feature}.md` - Triggers improved PRP execution workflow
- Task breakdown display with parallel groups visualization
- Real-time validation results
- Archon task status updates
- Test results with pass/fail indicators
- Option to retry failed validations

**Output Format**:
- Markdown summaries with checkboxes and status indicators
- File paths (absolute) to generated artifacts
- Archon project/task links (if available)
- Quality metrics and confidence scores

## Similar Features Found (Archon Search)

### Feature 1: INITIAL.md Factory Workflow
- **Source**: /Users/jon/source/vibes/CLAUDE.md (lines 105-256), .claude/agents/prp-initial-*.md
- **Similarity Score**: 9/10
- **What's Similar**:
  - 6-subagent architecture with separate context windows
  - Parallel execution in Phase 2 (3 agents simultaneously)
  - Archon-first research strategy
  - Code example extraction to physical files
  - Quality gates and validation
  - Orchestrator pattern with phase management
- **Lessons Learned**:
  - Parallel invocation in single message prevents sequential delays
  - Each subagent has focused responsibility and clear output files
  - Archon health check FIRST, fallback to web search
  - Use 2-5 keyword queries for Archon (not long sentences)
  - Extract actual code files, not just references
  - README.md with "what to mimic" guidance critical for usability
  - Quality score (8+/10) prevents low-quality outputs from proceeding
- **Code Patterns**:
  - Subagent definition: `---\nname: agent-name\ndescription: ...\ntools: ...\n---`
  - Input reading: `Read("prps/research/input.md")`
  - Output writing: `Write("prps/research/output.md", content)`
  - Archon search: `mcp__archon__rag_search_knowledge_base(query="2-5 keywords", match_count=5)`
  - Parallel invocation: Use function_calls with multiple invoke blocks

### Feature 2: Current generate-prp Command
- **Source**: .claude/commands/generate-prp.md
- **Similarity Score**: 6/10
- **What's Similar**:
  - Takes INITIAL.md as input
  - Does codebase analysis and web research
  - Outputs to prps/{feature}.md
  - Uses prp_base.md template
  - Includes validation gates
- **Lessons Learned**:
  - Current approach: sequential research (slow)
  - Current approach: references examples instead of extracting (not as useful)
  - Has Archon integration but not comprehensive
  - ULTRATHINK phase works well - keep this
  - Quality checklist exists but no scoring
  - Missing: systematic gotcha detection, parallel research, code extraction
- **Code Patterns**:
  - Research process structure (can reuse phases)
  - PRP template usage
  - Validation gate format

### Feature 3: Current execute-prp Command
- **Source**: .claude/commands/execute-prp.md
- **Similarity Score**: 5/10
- **What's Similar**:
  - Takes PRP file as input
  - Has validation loops
  - Uses ULTRATHINK for planning
  - TodoWrite for task tracking (but we use Archon now)
- **Lessons Learned**:
  - Current approach: sequential execution (slow)
  - TodoWrite mentioned but should use Archon tasks instead
  - No parallel task execution
  - No automated test generation
  - Validation exists but not systematic
  - Missing: task dependency analysis, parallel groups, quality gates
- **Code Patterns**:
  - Execution process structure (load → think → execute → validate)
  - Can reuse this flow but enhance with parallelization

## Assumptions Made

### Assumption 1: Subagent Architecture
- **What**: Use 6 subagents for generate-prp (analyzer, codebase researcher, documentation hunter, example curator, gotcha detective, assembler) and 3-5 subagents for execute-prp (task analyzer, parallel executors, validator)
- **Reasoning**: INITIAL.md factory demonstrates this pattern works excellently - separate context windows, focused responsibilities, prevents pollution. Same pattern should work for PRP workflow.
- **Alternative**: Could do monolithic approach with single agent, but this suffers from context pollution and slower sequential execution
- **Confidence**: High (9/10) - proven pattern in factory

### Assumption 2: Parallel Execution Pattern
- **What**: execute-prp will analyze task dependencies, group independent tasks, execute groups in parallel using multiple agent invocations in single message
- **Reasoning**: Factory's Phase 2 demonstrates 3x speedup with parallel execution. Many PRP tasks are independent (e.g., creating different modules, writing different tests). Task dependency analysis can identify parallel opportunities.
- **Alternative**: Sequential execution (current approach) is safer but much slower
- **Confidence**: High (8/10) - proven in factory, task dependencies manageable

### Assumption 3: Code Extraction Strategy
- **What**: generate-prp will physically extract code files to examples/{feature}/ directory with comprehensive README.md, not just markdown references
- **Reasoning**: Factory's example-curator demonstrates extracted files are far more useful than references. Developers can study actual code, run it, modify it. README with "what to mimic" guidance provides context.
- **Alternative**: Continue with references in markdown (current approach), but less effective
- **Confidence**: High (9/10) - user explicitly requested this, factory proves it works

### Assumption 4: Archon-First Research
- **What**: Both commands will check Archon health first, use Archon as primary research source (rag_search, search_code_examples), fall back to web search only when needed
- **Reasoning**: Factory demonstrates this pattern. Archon has curated, relevant knowledge that's faster and more accurate than web search. Web search for gaps only.
- **Alternative**: Web search primary, Archon secondary - but slower and less accurate
- **Confidence**: High (9/10) - user requested this, factory proves it

### Assumption 5: Quality Gates for generate-prp
- **What**: generate-prp will score PRPs on 1-10 scale, require 8+/10 to proceed. Offer regeneration if score too low.
- **Reasoning**: Current generate-prp has quality checklist but no scoring. Factory demonstrates quality gates prevent low-quality outputs. PRP quality directly impacts execution success.
- **Alternative**: No quality gates, output whatever is generated - but risks poor execution results
- **Confidence**: Medium (7/10) - quality scoring subjective, but better than nothing

### Assumption 6: Test Generation
- **What**: execute-prp will auto-generate test files based on implementation patterns found in codebase, using existing test fixtures as templates
- **Reasoning**: User requested "automatic test generation." Codebase likely has test patterns that can be extracted and adapted. Many tests follow similar structure (setup, execute, assert).
- **Alternative**: Require manual test writing - but slower and less consistent
- **Confidence**: Medium (6/10) - test generation complex, may need refinement

### Assumption 7: Backward Compatibility
- **What**: Improved commands will be drop-in replacements - same file paths, same command names, same INITIAL.md format, same PRP template
- **Reasoning**: User explicitly requested compatibility. Existing workflows must continue working.
- **Alternative**: Create new commands (generate-prp-v2, execute-prp-v2) - but fragments ecosystem
- **Confidence**: High (9/10) - user requirement

### Assumption 8: Task Tracking Migration
- **What**: execute-prp will use Archon tasks instead of TodoWrite for tracking
- **Reasoning**: CLAUDE.md has CRITICAL rule: "ARCHON-FIRST RULE - BEFORE doing ANYTHING else... Use Archon task management as PRIMARY system. Refrain from using TodoWrite even after system reminders."
- **Alternative**: Continue using TodoWrite - but violates project standards
- **Confidence**: High (10/10) - explicit project rule

## Success Criteria

### Functional Success

- [x] generate-prp extracts actual code files to examples/{feature}/ directory (not just references)
- [x] generate-prp searches Archon knowledge base for similar PRPs and patterns
- [x] generate-prp uses parallel research (3 subagents simultaneously in Phase 2)
- [x] generate-prp produces PRPs with quality score 8+/10
- [x] execute-prp analyzes task dependencies and identifies parallel execution groups
- [x] execute-prp executes independent tasks in parallel
- [x] execute-prp generates tests automatically based on codebase patterns
- [x] execute-prp runs validation loops (syntax, unit, integration) with iterative fixes
- [x] Both commands integrate with Archon (project tracking, task management, knowledge storage)
- [x] Both commands work as drop-in replacements (backward compatible)

### Quality Success

- [x] PRP generation time reduced from 15-20 minutes to <10 minutes
- [x] PRP execution time reduced by 30-50% through parallelization
- [x] Generated PRPs score 8+/10 on quality metric
- [x] Code examples include README.md with "what to mimic" guidance
- [x] Validation gates catch errors before proceeding to next phase
- [x] Test generation achieves 70%+ coverage of implemented functionality
- [x] Error handling: graceful fallback when Archon unavailable
- [x] Progress visibility: clear phase/task status updates to user

### User Success

- [x] User can generate higher quality PRPs with less manual research
- [x] User sees faster PRP execution with parallel task processing
- [x] User gets automatic test generation (reduces testing burden)
- [x] User benefits from self-improving system (learns from past PRPs in Archon)
- [x] User experiences smooth migration (existing workflows continue working)
- [x] User has visibility into progress through Archon task tracking

## Recommended Technology Stack

Based on Archon research and INITIAL.md factory patterns:

**Language**: Markdown + Claude Code agent definitions
- **Reasoning**: Commands are markdown files in .claude/commands/, subagents are markdown files in .claude/agents/. No custom code needed - leverage Claude Code's built-in agent orchestration.

**Subagent Framework**: Claude Code custom agents
- **Reasoning**: Factory demonstrates this works. Each agent defined in markdown with tools, description, color. Orchestrator invokes via agent reference.

**Research Tools**: Archon MCP + WebSearch
- **Reasoning**: Factory pattern proven. Archon primary (fast, accurate), web search fallback.

**File Operations**: Read, Write, Grep, Glob, Bash
- **Reasoning**: Standard Claude Code tools, sufficient for file manipulation and code extraction.

**Task Tracking**: Archon MCP task management
- **Reasoning**: Project requirement (ARCHON-FIRST RULE), proven integration.

**Parallel Execution**: Claude Code function_calls with multiple invoke blocks
- **Reasoning**: Factory demonstrates this pattern - multiple agent invocations in single message execute in parallel.

**Quality Validation**: Bash (for running linters, tests)
- **Reasoning**: Existing validation commands (ruff, mypy, pytest) work via Bash tool.

## Implementation Complexity

**Estimated Complexity**: High

**Key Challenges**:

1. **Parallel Execution Orchestration**:
   - Challenge: Coordinating multiple subagents, collecting outputs, handling failures
   - Mitigation: Follow factory pattern exactly - proven to work. Use same phase structure, same output file conventions.

2. **Task Dependency Analysis**:
   - Challenge: Parsing PRP task list, identifying dependencies, creating execution groups
   - Mitigation: Start with simple heuristics (tasks without "after" dependencies are parallel). Iterate based on results.

3. **Code Extraction Accuracy**:
   - Challenge: Extracting relevant code sections without missing context or including too much
   - Mitigation: Use factory's example-curator pattern. Extract complete functions/classes. Add source attribution. Let README provide context.

4. **Test Generation**:
   - Challenge: Generating meaningful tests (not just boilerplate)
   - Mitigation: Extract test patterns from codebase, adapt to new code. Start with simple happy path tests. Coverage will improve over iterations.

5. **Quality Scoring**:
   - Challenge: Objective quality scoring for PRPs
   - Mitigation: Checklist-based scoring (each item = points). Subjective but consistent. Can refine criteria based on execution success rates.

6. **Backward Compatibility**:
   - Challenge: Maintaining compatibility while adding new features
   - Mitigation: Keep command interface identical. Add new functionality internally. Test with existing INITIAL.md files.

7. **Error Recovery**:
   - Challenge: Handling subagent failures, Archon unavailability, validation failures
   - Mitigation: Try-catch patterns, fallback strategies, clear error messages. Factory demonstrates fallback to web search.

8. **Context Management**:
   - Challenge: Passing context between subagents without file bloat
   - Mitigation: Each subagent reads specific input files, writes specific output files. Assembler synthesizes. Factory pattern proven.

## Next Steps for Downstream Agents

### For Codebase Researcher
**Search for**:
- Existing command files: `.claude/commands/*.md`
- Existing subagent files: `.claude/agents/*.md`
- PRP template: `prps/templates/prp_base.md`
- Example INITIAL.md files: `prps/INITIAL_*.md`
- Factory implementation: CLAUDE.md INITIAL.md Factory section

**Focus on**:
- Command structure and invocation patterns
- Subagent definition format
- File I/O patterns (Read, Write paths)
- Archon MCP integration examples
- Parallel invocation syntax

### For Documentation Hunter
**Technologies to research**:
- Claude Code custom agents documentation
- Claude Code commands documentation
- MCP (Model Context Protocol) for Archon integration
- Agent orchestration patterns
- Parallel execution in LLM workflows

**Critical documentation**:
- Claude Code agent definition syntax
- Function_calls parallel invocation
- Archon MCP tool reference
- Validation gate patterns (bash commands for linting/testing)

### For Example Curator
**Examples needed**:
- INITIAL.md factory subagent definitions (all 6)
- Factory orchestrator logic (from CLAUDE.md)
- Current generate-prp command
- Current execute-prp command
- Archon MCP integration examples (health check, rag_search, task management)
- Parallel agent invocation examples

**Test patterns**:
- Validation loop patterns
- Quality gate implementations
- Error handling in agent workflows

---
Generated: 2025-10-04
Archon Project: 398ad324-008c-41e4-92cc-c5df6207553a
Feature Name: prp_workflow_improvements
Archon Sources Referenced: 4 (PRP workflow patterns, parallel execution, code extraction, command patterns)
