# Vibes Setup Guide 🚀

Get Vibes running with Claude Desktop in under 5 minutes.

## Prerequisites

- **Claude Desktop** - Download from Anthropic
- **Docker** - For running the MCP servers
- **Git** - For cloning the repository

## Step 1: Clone Vibes

```bash
git clone https://github.com/your-username/vibes.git
cd vibes
```

## Step 2: Build the MCP Server

```bash
cd mcp/mcp-vibes-server
docker build -t mcp-vibes:latest .
```

## Step 3: Start OpenMemory (Optional)

If you want persistent memory:

```bash
cd mcp/mcp-openmemory-server
# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here
export USER=your-username
docker-compose up -d
```

## Step 4: Configure Claude Desktop

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "deepwiki": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.deepwiki.com/sse"
      ]
    },
    "mcp-vibes": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name",
        "mcp-vibes-server",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        "/path/to/your/vibes:/workspace/vibes:rw",
        "mcp-vibes:latest"
      ]
    },
    "openmemory": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8765/mcp/claude/sse/your-username"
      ]
    }
  }
}
```

**Important:** Replace `/path/to/your/vibes` with your actual Vibes directory path.

## Step 5: Restart Claude Desktop

Quit and restart Claude Desktop to load the new configuration.

## Step 6: Test the Setup

Start a conversation with Claude Desktop:

```
"Can you run 'ls -la' to show me what's in the workspace?"
```

If everything works, you should see the Vibes directory structure!

## Troubleshooting

### MCP Server Won't Start
- Check Docker is running: `docker ps`
- Verify the image exists: `docker images | grep mcp-vibes`
- Check file paths in the configuration

### Memory Server Issues
- Ensure OpenMemory containers are running: `docker-compose ps`
- Check the API key is set correctly
- Verify port 8765 is not in use: `lsof -i :8765`

### Permission Issues
- Make sure Docker socket is accessible
- Check directory permissions for the mounted volume

## Next Steps

- Read the [Examples Guide](examples.md) to see what you can do
- Check out the [Architecture Overview](architecture.md) to understand how it works
- Start building projects in the `/projects/` folder!

---

*You're now ready to chat with Claude and test any tool*
for you. I'll use my shell access to create the files and set everything up."

*Claude then creates files, writes code, sets up a local server, and walks you through everything step by step - all through natural conversation.*

This is the power of Vibes: **learning through doing, guided by AI**.

---

## Troubleshooting Resources

Each platform guide includes detailed troubleshooting sections, but here are some universal tips:

### General Issues
- **Restart everything** - Close Claude Desktop, restart Docker, try again
- **Check the basics** - Make sure Docker is running, config file is saved correctly
- **Path problems** - Double-check usernames and folder locations in config

### Getting Help
- **Read the error messages** - they usually tell you exactly what's wrong
- **Ask Claude** - Once basic setup works, Claude can help debug issues
- **Check Docker** - Run `docker ps` to see if containers are running

### Platform-Specific Help
- **Mac**: Check if you have Intel or Apple Silicon chip
- **Windows**: Make sure WSL2 is working properly
- **Linux**: Verify you're in the docker group

---

## After Setup: What's Possible

Once Vibes is running, you can:

### 🎓 Learn Anything
```
"Teach me Python by building a simple game"
"Explain machine learning using practical examples"
"Show me how databases work by creating one"
```

### 🛠️ Build Projects
```
"Let's create a personal website"
"Build a tool to organize my files"
"Make a simple mobile app"
```

### 🔍 Explore Code
```
"Clone the React repository and explain how it works"
"Analyze this open source project I found"
"Compare different web frameworks"
```

### 💾 Remember Everything
```
"Remember my coding style preferences"
"Keep track of the projects we're working on"
"Store useful code snippets for later"
```

---

## Why Vibes Changes Everything

### Traditional Learning Path
1. Read documentation
2. Watch tutorials
3. Set up development environment
4. Make mistakes
5. Debug problems
6. Repeat...

### Vibes Learning Path
1. "Claude, I want to learn X"
2. Claude teaches you by building real examples
3. You learn by doing, not reading
4. Claude remembers your progress
5. You advance at your own pace

---

## Security & Safety

### Containerized Environment
- All code runs in isolated Docker containers
- Your main system stays safe and clean
- Easy to reset if something goes wrong

### Controlled Access
- Claude only has access to the Vibes workspace
- Docker socket access is carefully managed
- No access to your personal files outside the workspace

### Open Source
- All code is visible and auditable
- No hidden functionality
- Community can contribute and improve

---

## Next Steps

1. **Choose your platform** and follow the setup guide
2. **Test the basic functionality** with simple commands
3. **Explore the [Examples](examples.md)** to see what's possible
4. **Start your first project** - ask Claude "What should we build?"

---

## Community & Support

### Getting Started
- Each platform guide has troubleshooting sections
- Start with simple tests before complex projects
- Don't hesitate to ask Claude for help once basic setup works

### Sharing Your Experience
- Document your projects in the `/projects/` folder
- Share interesting discoveries with others
- Help improve the setup guides based on your experience

---

*Ready to transform how you learn and build with AI? Pick your platform and let's get started!* 🎯
