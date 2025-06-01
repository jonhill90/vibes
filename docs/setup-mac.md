# Vibes Setup for Mac 🍎

*Complete beginner guide - no experience needed!*

## What You're About to Do

You're going to give Claude Desktop superpowers by connecting it to some helper programs. Once set up, you can just chat with Claude and it will be able to run code, remember things, and help you build projects.

**Time needed:** 15-30 minutes  
**Experience needed:** None! We'll walk through everything.

## Step 1: Install Claude Desktop

1. Go to https://claude.ai/download
2. Click "Download for Mac"
3. Open the downloaded file and drag Claude to Applications
4. Open Claude Desktop from Applications

*✅ You should now have Claude Desktop running*

## Step 2: Install Docker Desktop

Docker lets us run programs in safe, isolated containers. Think of it like a virtual computer inside your computer.

1. Go to https://docker.com/products/docker-desktop
2. Click "Download for Mac"
3. Choose your Mac type:
   - **Intel Mac**: Download the Intel version
   - **Apple Silicon (M1/M2/M3)**: Download the Apple Silicon version
   
   *Not sure which you have? Click the Apple menu → About This Mac*

4. Open the downloaded file and drag Docker to Applications
5. Open Docker Desktop from Applications
6. Follow the setup wizard (just click "Next" through everything)
7. Sign up for a free Docker account when prompted

*✅ You should see Docker Desktop running with a whale icon in your menu bar*

## Step 3: Install Git (for downloading code)

Git helps us download code from the internet. We'll use it to get Vibes.

**Option A: Easy way (if you have Homebrew)**
```bash
brew install git
```

**Option B: Download installer**
1. Go to https://git-scm.com/download/mac
2. Download the installer
3. Run the installer and follow the prompts

**Option C: Use Xcode tools**
1. Open Terminal (press Cmd+Space, type "Terminal", press Enter)
2. Type: `git --version`
3. If prompted, install Xcode command line tools

*✅ Test by opening Terminal and typing `git --version` - you should see a version number*

## Step 4: Download Vibes

Now we'll download the Vibes code to your computer.

1. **Open Terminal** (press Cmd+Space, type "Terminal", press Enter)

2. **Navigate to your home folder:**
   ```bash
   cd ~
   ```

3. **Download Vibes:**
   ```bash
   git clone https://github.com/your-username/vibes.git
   cd vibes
   ```

*✅ You should now have a "vibes" folder in your home directory*

## Step 5: Build the Vibes Container

This creates the special environment where Claude can run commands safely.

1. **In Terminal, make sure you're in the vibes folder:**
   ```bash
   cd ~/vibes
   ```

2. **Build the container:**
   ```bash
   cd mcp/mcp-vibes-server
   docker build -t mcp-vibes:latest .
   ```

   *This might take a few minutes - Docker is downloading and setting everything up*

*✅ When done, you'll see "Successfully tagged mcp-vibes:latest"*

## Step 6: Set Up Memory (Optional but Recommended)

This lets Claude remember things between conversations.

1. **Get an OpenAI API key** (needed for the memory system):
   - Go to https://platform.openai.com/api-keys
   - Sign up or log in
   - Click "Create new secret key"
   - Copy the key (starts with "sk-")

2. **Set up the memory system:**
   ```bash
   cd ~/vibes/mcp/mcp-openmemory-server
   export OPENAI_API_KEY=your-key-here
   export USER=your-name
   docker-compose up -d
   ```

   *Replace "your-key-here" with your actual API key and "your-name" with your name*

*✅ You should see containers starting up*

## Step 7: Connect Claude Desktop

Now we tell Claude Desktop how to use these new powers.

1. **Find your config file location:**
   - Open Finder
   - Press Cmd+Shift+G (Go to Folder)
   - Type: `~/Library/Application Support/Claude`
   - If the folder doesn't exist, create it

2. **Create the config file:**
   - In that folder, create a new file called `claude_desktop_config.json`
   - Open it in TextEdit or any text editor

3. **Add this configuration:**
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
           "/Users/YOUR-USERNAME/vibes:/workspace/vibes:rw",
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

4. **Important: Replace the placeholders:**
   - Replace `YOUR-USERNAME` with your Mac username
   - Replace `YOUR-NAME` with the name you used in Step 6
   
   *To find your username, in Terminal type: `whoami`*

5. **Save the file**

## Step 8: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q)
2. Open Claude Desktop again
3. Look for small icons in the bottom of the chat that show the connected tools

## Step 9: Test Everything

Start a conversation with Claude Desktop and try:

```
"Can you run 'ls -la' to show me what's in the workspace?"
```

If it works, you should see a list of files and folders!

Try this too:
```
"Remember that I just successfully set up Vibes on my Mac"
```

## Troubleshooting

### Docker not working?
- Make sure Docker Desktop is running (whale icon in menu bar)
- Try restarting Docker Desktop

### Can't find the config file location?
- The full path is: `/Users/YOUR-USERNAME/Library/Application Support/Claude/`
- The Library folder might be hidden - use Cmd+Shift+. to show hidden files

### Commands not working?
- Check that your username is correct in the config file
- Make sure the vibes folder path is right
- Try restarting Claude Desktop

### Memory not working?
- Check that the OpenMemory containers are running: `docker ps`
- Verify your OpenAI API key is correct
- Make sure port 8765 isn't being used by something else

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
