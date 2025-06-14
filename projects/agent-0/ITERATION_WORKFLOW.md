# Context-Driven Iteration Workflow

## 🎯 Goal
Create a workflow where you gather context, I iterate on implementation, and you verify results.

## 🔄 The Workflow

### 1. Context Gathering (You)
```
1. Describe what you want (text, sketches, examples)
2. Provide references (URLs, repos, images)
3. Define success criteria ("It works when...")
4. Set constraints ("Don't do X", "Must have Y")
```

### 2. Implementation Iteration (Me)
```
1. Read all context
2. Ask clarifying questions
3. Build/modify code
4. Test what I can
5. Document what I did
6. Flag what needs visual verification
```

### 3. Verification (You)
```
1. Run the code
2. Take screenshot if UI
3. Test the functionality
4. Provide feedback:
   - ✅ "This works"
   - ❌ "This is broken because..."
   - 🔄 "Close but needs..."
```

### 4. Refinement Loop
```
Repeat steps 2-3 until success criteria met
```

## 📁 Context File Structure

```
projects/Agent-0/iterations/
├── current/
│   ├── CONTEXT.md        # What we're building
│   ├── SUCCESS.md        # How we know it's done
│   ├── CONSTRAINTS.md    # What to avoid
│   ├── REFERENCES.md     # Links, examples
│   └── FEEDBACK.md       # Your responses
├── archive/
│   └── [timestamp]/      # Completed iterations
```

## 🛠️ Tools Needed for This Workflow

### Immediate (This Week)
1. **Basic Screenshot Tool**
   - You take screenshots manually
   - Save to iterations/current/screenshots/
   - I read and understand them

2. **Feedback Protocol**
   - Structured feedback format
   - Clear success/fail states
   - Specific improvement notes

### Next Phase (With MCP)
1. **Screenshot MCP**
   - I can see UI directly
   - Faster iteration

2. **Browser Control MCP**
   - I can test interactions
   - Less manual verification needed

## 📝 Example Iteration

### You provide:
```markdown
# CONTEXT.md
I want a button that:
- Says "Hello World"
- Is blue with white text
- Centered on page
- Changes to green on hover

# SUCCESS.md
- Button visible
- Text readable
- Hover effect works
- Looks good on mobile

# REFERENCES.md
- Like this button: [screenshot]
- Similar to: discord.com/channels button
```

### I iterate:
1. Create HTML/CSS/JS
2. Test what I can
3. Flag: "Need screenshot to verify colors"

### You verify:
1. Run code
2. Screenshot result
3. Feedback: "Button works but needs more padding"

### I refine:
1. Adjust padding
2. Update code
3. Ready for re-test

## 🚀 Starting This Workflow NOW

### Option 1: Manual Screenshots
1. You describe what you want
2. I build it
3. You screenshot and share
4. We iterate

### Option 2: Simple HTTP Server
```python
# I can create a simple server that:
1. Serves the UI
2. Logs interactions
3. Provides feedback endpoint
4. You can access locally
```

### Option 3: Progressive Enhancement
1. Start with static mockups
2. Add functionality incrementally
3. Test each addition
4. Build complexity over time

## 💡 Key Insights

### What Makes This Work:
- **Clear context upfront** - Less guessing
- **Specific success criteria** - Know when done
- **Structured feedback** - Actionable improvements
- **Incremental progress** - Small wins daily

### What Kills This Workflow:
- Vague requirements
- Moving goalposts
- No feedback loops
- Trying to do too much at once

## 📊 Success Metrics

- **Iteration Speed**: How fast context → implementation
- **Accuracy**: How often first attempt is close
- **Refinement Cycles**: How many loops to success
- **Context Quality**: How clear the requirements

## 🎬 Let's Start!

1. Pick one small feature of Vibes
2. Create context files
3. I'll implement
4. You verify
5. We refine
6. Move to next feature

This workflow works TODAY without any new tools!

