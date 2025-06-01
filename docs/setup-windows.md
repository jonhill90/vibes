# Vibes Setup for Windows 🪟

*Complete beginner guide - no experience needed!*

## What You're About to Do

You're going to give Claude Desktop superpowers by connecting it to some helper programs. Once set up, you can just chat with Claude and it will be able to run code, remember things, and help you build projects.

**Time needed:** 20-40 minutes  
**Experience needed:** None! We'll walk through everything.

## Step 1: Install Claude Desktop

1. Go to https://claude.ai/download
2. Click "Download for Windows"
3. Run the downloaded installer
4. Follow the setup wizard
5. Launch Claude Desktop

*✅ You should now have Claude Desktop running*

## Step 2: Install WSL2 (Windows Subsystem for Linux)

WSL2 gives you a Linux environment inside Windows. This makes everything work smoothly.

### Enable WSL2

1. **Open PowerShell as Administrator:**
   - Press Windows key
   - Type "PowerShell"
   - Right-click "Windows PowerShell"
   - Choose "Run as administrator"

2. **Install WSL2:**
   ```powershell
   wsl --install
   ```

3. **Restart your computer** when prompted

4. **After restart, set up Ubuntu:**
   - A Ubuntu window should open automatically
   - Create a username (use lowercase, no spaces)
   - Create a password (you won't see it as you type - this is normal)
   - Remember these credentials!

*✅ You should now have Ubuntu running in WSL2*

## Step 3: Install Docker Desktop

1. Go to https://docker.com/products/docker-desktop
2. Click "Download for Windows"
3. Run the installer
4. **Important:** During installation, make sure "Use WSL 2 instead of Hyper-V" is checked
5. Restart when prompted
6. Open Docker Desktop
7. Sign up for a free Docker account when prompted

### Configure Docker for WSL2

1. Open Docker Desktop
2. Go to Settings (gear icon)
3. Go to "Resources" → "WSL Integration"
4. Make sure "Enable integration with my default WSL distro" is checked
5. Turn on integration for "Ubuntu"
6. Click "Apply & Restart"

*✅ You should see Docker Desktop running with a whale icon in your system tray*

## Step 4: Install Git

We need Git to download the Vibes code.

1. Go to https://git-scm.com/download/win
2. Download the installer
3. Run the installer
4. **Important settings during install:**
   - Choose "Use Git from the Windows Command Prompt"
   - Choose "Checkout Windows-style, commit Unix-style line endings"
   - Choose "Use Windows' default console window"

*✅ Test by opening Command Prompt and typing `git --version`*

## Step 5: Download Vibes

### Option A: Using WSL2 Ubuntu (Recommended)

1. **Open Ubuntu** (search for "Ubuntu" in Start menu)

2. **Update Ubuntu first:**
   ```bash
   sudo apt update
   ```

3. **Navigate to your home folder and download Vibes:**
   ```bash
   cd ~
   git clone https://github.com/your-username/vibes.git
   cd vibes
   ```

### Option B: Using Windows Command Prompt

1. **Open Command Prompt** (search for "cmd" in Start menu)

2. **Go to your user folder:**
   ```cmd
   cd C:\Users\%USERNAME%
   ```

3. **Download Vibes:**
   ```cmd
   git clone https://github.com/your-username/vibes.git
   cd vibes
   ```

*✅ You should now have a "vibes" folder*

## Step 6: Build the Vibes Container

### Using WSL2 Ubuntu (Recommended)

1. **Open Ubuntu**

2. **Navigate to the vibes folder:**
   ```bash
   cd ~/vibes/mcp/mcp-vibes-server
   ```

3. **Build the container:**
   ```bash
   docker build -t mcp-vibes:latest .
   ```

*This might take a few minutes - Docker is downloading and setting everything up*

*✅ When done, you'll see "Successfully tagged mcp-vibes:latest"*

## Step 7: Set Up Memory (Optional but Recommended)

This lets Claude remember things between conversations.

1. **Get an OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Sign up or log in
   - Click "Create new secret key"
   - Copy the key (starts with "sk-")

2. **In Ubuntu, set up the memory system:**
   ```bash
   cd ~/vibes/mcp/mcp-openmemory-server
   export OPENAI_API_KEY=your-key-here
   export USER=your-name
   docker-compose up -d
   ```

   *Replace "your-key-here" with your actual API key and "your-name" with your name*

*✅ You should see containers starting up*

## Step 8: Connect Claude Desktop

Now we tell Claude Desktop how to use these new powers.

### Find Your Vibes Path

**If you used WSL2 Ubuntu:**
- Your vibes folder is at: `\\wsl$\Ubuntu\home\YOUR-UBUNTU-USERNAME\vibes`
- To find your Ubuntu username, in Ubuntu type: `whoami`

**If you used Windows Command Prompt:**
- Your vibes folder is at: `C:\Users\YOUR-WINDOWS-USERNAME\vibes`

### Create the Config File

1. **Open File Explorer**

2. **Navigate to:**
   ```
   C:\Users\YOUR-WINDOWS-USERNAME\AppData\Roaming\Claude
   ```
   
   *If this folder doesn't exist, create it*

3. **Create a new file called `claude_desktop_config.json`**

4. **Open it in Notepad and add this configuration:**

   **For WSL2 setup:**
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
         "command": "wsl",
         "args": [
           "docker",
           "run",
           "-i",
           "--rm",
           "--name",
           "mcp-vibes-server",
           "-v",
           "/var/run/docker.sock:/var/run/docker.sock",
           "-v",
           "/home/YOUR-UBUNTU-USERNAME/vibes:/workspace/vibes:rw",
           "mcp-vibes:latest"
         ]
       },
       "openmemory": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "http://localhost:8765/mcp/claude/sse/YOUR-NAME"
         ]
       }
     }
   }
   ```

   **For Windows Command Prompt setup:**
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
           "C:/Users/YOUR-WINDOWS-USERNAME/vibes:/workspace/vibes:rw",
           "mcp-vibes:latest"
         ]
       },
       "openmemory": {
         "command": "npx",
         "args": [
           "mcp-remote",
           "http://localhost:8765/mcp/claude/sse/YOUR-NAME"
         ]
       }
     }
   }
   ```

5. **Replace the placeholders:**
   - Replace `YOUR-UBUNTU-USERNAME` or `YOUR-WINDOWS-USERNAME` with your actual username
   - Replace `YOUR-NAME` with the name you used in Step 7

6. **Save the file**

## Step 9: Restart Claude Desktop

1. Close Claude Desktop completely
2. Open Claude Desktop again
3. Look for small icons in the bottom of the chat that show the connected tools

## Step 10: Test Everything

Start a conversation with Claude Desktop and try:

```
"Can you run 'ls -la' to show me what's in the workspace?"
```

If it works, you should see a list of files and folders!

Try this too:
```
"Remember that I just successfully set up Vibes on my Windows computer"
```

## Troubleshooting

### WSL2 Issues
- Make sure Windows is updated to version 1903 or higher
- Try running `wsl --update` in PowerShell as Administrator
- Restart your computer after installing WSL2

### Docker not working?
- Make sure Docker Desktop is running (whale icon in system tray)
- Check that WSL2 integration is enabled in Docker settings
- Try restarting Docker Desktop

### Can't find the config file location?
- The full path is: `C:\Users\YOUR-USERNAME\AppData\Roaming\Claude\`
- You might need to show hidden files in File Explorer

### Commands not working?
- Double-check your username in the config file
- Make sure the vibes folder path is correct
- Try restarting Claude Desktop
- If using WSL2, make sure Docker is running in Ubuntu: `docker ps`

### Memory not working?
- Check that containers are running: `docker ps` (in Ubuntu if using WSL2)
- Verify your OpenAI API key is correct
- Make sure port 8765 isn't being used by something else

### Path Issues on Windows
- Use forward slashes (/) in Docker volume mounts, even on Windows
- For WSL2, use Linux-style paths: `/home/username/vibes`
- For Windows, use: `C:/Users/username/vibes` (forward slashes!)

## What's Next?

🎉 **Congratulations!** You now have a supercharged Claude Desktop that can:
- Run code and commands
- Remember things between conversations  
- Analyze GitHub repositories
- Help you build projects

**Try asking Claude:**
- "What can you do now that you have these tools?"
- "Help me create a simple Python script"
- "Clone an interesting GitHub repository and explain it to me"
- "Remember my coding preferences and help me start a project"

Check out the [Examples Guide](examples.md) for more ideas!

---

*You just gave Claude the power to teach you anything through conversation* 🚀
