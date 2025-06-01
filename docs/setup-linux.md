# Vibes Setup for Linux 🐧

*Complete beginner guide - no experience needed!*

## What You're About to Do

You're going to give Claude Desktop superpowers by connecting it to some helper programs. Once set up, you can just chat with Claude and it will be able to run code, remember things, and help you build projects.

**Time needed:** 15-25 minutes  
**Experience needed:** None! We'll walk through everything.

## Step 1: Install Claude Desktop

### For Ubuntu/Debian

1. **Download Claude Desktop:**
   ```bash
   wget https://claude.ai/download/linux -O claude-desktop.deb
   ```

2. **Install it:**
   ```bash
   sudo dpkg -i claude-desktop.deb
   sudo apt-get install -f
   ```

### For Other Distributions

1. Go to https://claude.ai/download
2. Download the appropriate package for your distribution
3. Install using your package manager

### Launch Claude Desktop

```bash
claude-desktop
```

*Or find it in your applications menu*

*✅ You should now have Claude Desktop running*

## Step 2: Install Docker

Docker lets us run programs in safe, isolated containers.

### Ubuntu/Debian

1. **Update your system:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Docker:**
   ```bash
   # Install required packages
   sudo apt install -y ca-certificates curl gnupg lsb-release
   
   # Add Docker's official GPG key
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   
   # Add the repository
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   
   # Install Docker
   sudo apt update
   sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```

3. **Add your user to the docker group:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

### Fedora/RHEL/CentOS

```bash
# Install Docker
sudo dnf install -y docker docker-compose

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Arch Linux

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

*✅ Test by running `docker --version` - you should see a version number*

## Step 3: Install Git

Git helps us download code from the internet.

### Ubuntu/Debian
```bash
sudo apt install -y git
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install -y git
```

### Arch Linux
```bash
sudo pacman -S git
```

*✅ Test by running `git --version` - you should see a version number*

## Step 4: Download Vibes

1. **Open a terminal**

2. **Navigate to your home directory:**
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

1. **Navigate to the MCP server directory:**
   ```bash
   cd ~/vibes/mcp/mcp-vibes-server
   ```

2. **Build the container:**
   ```bash
   docker build -t mcp-vibes:latest .
   ```

   *This might take a few minutes - Docker is downloading and setting everything up*

*✅ When done, you'll see "Successfully tagged mcp-vibes:latest"*

## Step 6: Install Node.js and npm

We need these to connect to some of the MCP servers.

### Ubuntu/Debian
```bash
# Install Node.js from NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install -y nodejs npm
```

### Arch Linux
```bash
sudo pacman -S nodejs npm
```

*✅ Test by running `node --version` and `npm --version`*

## Step 7: Set Up Memory (Optional but Recommended)

This lets Claude remember things between conversations.

1. **Get an OpenAI API key:**
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

## Step 8: Connect Claude Desktop

Now we tell Claude Desktop how to use these new powers.

1. **Create the config directory:**
   ```bash
   mkdir -p ~/.config/Claude
   ```

2. **Create the config file:**
   ```bash
   nano ~/.config/Claude/claude_desktop_config.json
   ```

   *If you don't have nano, use any text editor like vim, gedit, or kate*

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
           "/home/YOUR-USERNAME/vibes:/workspace/vibes:rw",
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

4. **Replace the placeholders:**
   - Replace `YOUR-USERNAME` with your Linux username
   - Replace `YOUR-NAME` with the name you used in Step 7
   
   *To find your username, run: `whoami`*

5. **Save the file:**
   - In nano: Press Ctrl+X, then Y, then Enter
   - In other editors: Use Ctrl+S or the File menu

## Step 9: Restart Claude Desktop

1. **Close Claude Desktop:**
   ```bash
   pkill claude-desktop
   ```

2. **Start Claude Desktop again:**
   ```bash
   claude-desktop &
   ```

3. Look for small icons in the bottom of the chat that show the connected tools

## Step 10: Test Everything

Start a conversation with Claude Desktop and try:

```
"Can you run 'ls -la' to show me what's in the workspace?"
```

If it works, you should see a list of files and folders!

Try this too:
```
"Remember that I just successfully set up Vibes on my Linux computer"
```

## Troubleshooting

### Docker permission issues?
```bash
# Make sure you're in the docker group
sudo usermod -aG docker $USER
newgrp docker

# Or restart your session
sudo reboot
```

### Claude Desktop won't start?
```bash
# Check if it's already running
ps aux | grep claude

# Kill any existing processes
pkill claude-desktop

# Start fresh
claude-desktop
```

### Can't find the config file location?
- The config should be at: `~/.config/Claude/claude_desktop_config.json`
- Some distributions might use: `~/.local/share/Claude/` instead

### Commands not working?
- Check that your username is correct in the config file
- Make sure Docker is running: `docker ps`
- Verify the vibes folder path is correct
- Try restarting Claude Desktop

### Memory not working?
- Check that containers are running: `docker ps`
- Verify your OpenAI API key is correct
- Make sure port 8765 isn't being used: `ss -tlnp | grep 8765`

### Node.js/npm issues?
- Make sure you have Node.js 16 or higher: `node --version`
- Try installing mcp-remote globally: `npm install -g mcp-remote`

## Distribution-Specific Notes

### Flatpak/Snap Claude Desktop
If Claude Desktop is installed via Flatpak or Snap, the config location might be different:
- **Flatpak**: `~/.var/app/com.anthropic.claude/config/Claude/`
- **Snap**: `~/snap/claude-desktop/current/.config/Claude/`

### SELinux (Fedora/RHEL)
If you're on a system with SELinux, you might need to set the proper context:
```bash
sudo setsebool -P container_manage_cgroup on
```

### Firewall Issues
If the memory system isn't working, check your firewall:
```bash
# Ubuntu/Debian
sudo ufw allow 8765

# Fedora/RHEL
sudo firewall-cmd --add-port=8765/tcp --permanent
sudo firewall-cmd --reload
```

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
