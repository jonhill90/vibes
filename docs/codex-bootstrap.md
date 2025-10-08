# Codex CLI Bootstrap Guide

**Purpose**: Step-by-step installation, authentication, and verification procedures for OpenAI Codex CLI integration with Vibes PRP-driven development.

**Target Audience**: Developers setting up Codex for the first time.

**Prerequisites**:
- macOS, Linux, or Windows with WSL
- Node.js 16+ (for npm installation) OR Homebrew
- OpenAI account (for ChatGPT login or API key)

---

## Installation

Choose one installation method based on your environment:

### Option 1: npm (Recommended for Most Users)

```bash
# Install globally
npm install -g @openai/codex

# Verify installation
codex --version
```

**Pros**:
- Universal (works on any platform with Node.js)
- Automatic updates via npm
- Easy uninstall

**Cons**:
- Requires Node.js/npm
- May have version conflicts with other npm packages

---

### Option 2: Homebrew (macOS/Linux)

```bash
# Install via Homebrew
brew install openai-codex

# Verify installation
codex --version
```

**Pros**:
- Native binary (no Node.js dependency)
- Managed by system package manager
- Automatic updates via brew

**Cons**:
- macOS/Linux only
- May lag behind latest npm releases

---

### Option 3: Binary Download (Air-Gapped Environments)

```bash
# 1. Download latest release
curl -L https://github.com/openai/codex/releases/latest/download/codex-$(uname -s)-$(uname -m).tar.gz -o codex.tar.gz

# 2. Extract binary
tar -xzf codex.tar.gz

# 3. Move to PATH
sudo mv codex /usr/local/bin/codex
sudo chmod +x /usr/local/bin/codex

# 4. Verify installation
codex --version
```

**Pros**:
- Works in air-gapped/restricted environments
- No package manager required
- Full control over version

**Cons**:
- Manual update process
- Platform-specific binary required
- PATH configuration needed

---

## Authentication

Codex requires authentication before executing any commands. Choose one method:

### Method 1: ChatGPT Login (Primary - Recommended)

```bash
# Initiate login flow
codex login

# Browser will open for ChatGPT authentication
# Follow prompts to authorize Codex CLI
```

**Process**:
1. Run `codex login`
2. Browser opens to ChatGPT login page
3. Sign in with your OpenAI account
4. Click "Authorize" for Codex CLI
5. Return to terminal (login complete)

**Verification**:
```bash
codex login status
# Output: Logged in as user@example.com
```

**Important Notes**:
- Tokens expire periodically (re-run `codex login` if auth fails)
- Requires browser access (see SSH port forwarding for remote machines)
- Stores credentials in `~/.codex/auth.json` (protect this file)

---

### Method 2: API Key (Headless/CI Environments)

For machines without browser access (servers, CI/CD pipelines):

```bash
# Option A: Interactive (secure, stdin-based)
codex login --with-api-key
# Paste API key when prompted (not visible in shell history)

# Option B: Manual auth.json creation
mkdir -p ~/.codex
cat > ~/.codex/auth.json <<EOF
{
  "api_key": "sk-your-api-key-here"
}
EOF
chmod 600 ~/.codex/auth.json
```

**Verification**:
```bash
codex login status
# Output: Logged in with API key
```

**Security Considerations**:
- NEVER use `--api-key` flag directly (exposes key in shell history)
- Use `--with-api-key` for stdin entry (secure)
- Set file permissions to 600: `chmod 600 ~/.codex/auth.json`
- Rotate API keys regularly

---

### Method 3: SSH Port Forwarding (Remote Machines)

For remote machines that need browser-based login:

```bash
# On local machine (with browser):
ssh -L 8080:localhost:8080 user@remote-host

# On remote machine:
codex login
# Browser on LOCAL machine will open (uses forwarded port)
```

**Process**:
1. SSH with port forwarding: `ssh -L 8080:localhost:8080 remote-host`
2. On remote: run `codex login`
3. Browser opens on local machine
4. Complete authentication
5. Remote machine receives credentials

**Alternative**: Copy auth.json from working machine
```bash
# On working machine:
scp ~/.codex/auth.json user@remote-host:~/.codex/auth.json

# On remote machine:
chmod 600 ~/.codex/auth.json
codex login status  # Verify
```

---

## Verification Steps

After installation and authentication, verify Codex is working:

### Step 1: Check CLI Installed

```bash
which codex
# Output: /usr/local/bin/codex (or npm global path)

codex --version
# Output: codex x.y.z
```

**Expected**: Version number displayed (e.g., `codex 1.2.3`)

**Troubleshooting**:
- "command not found" → Binary not in PATH (add to `~/.bashrc` or `~/.zshrc`)
- Permission denied → Run `chmod +x /usr/local/bin/codex`

---

### Step 2: Verify Authentication

```bash
codex login status
```

**Expected Output**:
```
✓ Logged in as user@example.com
```

**Troubleshooting**:
- "Not authenticated" → Run `codex login` (or create auth.json)
- "Token expired" → Re-run `codex login` to refresh
- "Auth file not found" → Check `~/.codex/auth.json` exists and has correct permissions

---

### Step 3: Test Sandbox Mode

Verify sandbox execution works:

```bash
# Test read-only sandbox (safest)
codex exec --sandbox read-only "echo 'Hello from Codex'"

# Expected: "Hello from Codex" output, exit code 0
echo $?  # Should print: 0
```

**Expected**: Command executes successfully, prints output

**Troubleshooting**:
- "Sandbox not available" → Platform doesn't support sandboxing (use `--sandbox danger-full-access` with caution)
- "Permission denied" → Sandbox config issue (check profile settings)
- Hangs indefinitely → Approval policy prompting for stdin (use `--ask-for-approval never` for testing)

---

### Step 4: Verify Profile Configuration (Optional)

If using dedicated Codex profile:

```bash
# Check profile exists
codex config show --profile codex-prp

# Validate config file
codex config validate
```

**Expected**: Profile settings displayed (model, approval_policy, sandbox_mode, etc.)

**Troubleshooting**:
- "Profile not found" → Create `~/.codex/config.toml` with profile (see config guide)
- "Invalid config" → Check TOML syntax (use `toml get` to validate)

---

## Troubleshooting Guide

### Issue 1: Authentication Loop / Silent Failure

**Symptoms**:
- `codex login` completes but `codex exec` fails with "unauthorized"
- Authentication works once, then fails on subsequent runs
- Browser login successful but CLI reports "not authenticated"

**Root Cause**: ChatGPT login tokens expire without warning; Codex does NOT read `OPENAI_API_KEY` env var

**Solutions**:
1. **Clear browser cache and re-login**:
   ```bash
   # Clear Codex auth
   rm ~/.codex/auth.json

   # Re-authenticate
   codex login
   ```

2. **Switch to API key authentication** (more reliable for automation):
   ```bash
   codex login --with-api-key
   # Paste API key when prompted
   ```

3. **Check auth file permissions**:
   ```bash
   ls -la ~/.codex/auth.json
   # Should be: -rw------- (600)

   chmod 600 ~/.codex/auth.json
   ```

---

### Issue 2: Binary Not Found (PATH Configuration)

**Symptoms**:
- "command not found: codex" after installation
- `which codex` returns nothing
- Installation succeeded but CLI unavailable

**Root Cause**: Binary not in system PATH

**Solutions**:
1. **Find Codex binary location**:
   ```bash
   # npm installation
   npm list -g @openai/codex | head -1

   # Homebrew installation
   brew --prefix openai-codex
   ```

2. **Add to PATH** (bash):
   ```bash
   # Add to ~/.bashrc or ~/.bash_profile
   export PATH="$PATH:/usr/local/bin"
   # OR for npm global
   export PATH="$PATH:$(npm config get prefix)/bin"

   # Reload shell
   source ~/.bashrc
   ```

3. **Add to PATH** (zsh):
   ```bash
   # Add to ~/.zshrc
   export PATH="$PATH:/usr/local/bin"

   # Reload shell
   source ~/.zshrc
   ```

---

### Issue 3: Permission Errors (File Ownership)

**Symptoms**:
- "Permission denied" when running `codex exec`
- "Cannot write to ~/.codex/auth.json"
- Sandbox violations on valid writes

**Root Cause**: Incorrect file permissions or ownership

**Solutions**:
1. **Fix Codex binary permissions**:
   ```bash
   sudo chmod +x /usr/local/bin/codex
   sudo chown $USER /usr/local/bin/codex
   ```

2. **Fix auth file permissions**:
   ```bash
   mkdir -p ~/.codex
   chmod 700 ~/.codex
   chmod 600 ~/.codex/auth.json
   ```

3. **Fix workspace permissions** (if sandbox write fails):
   ```bash
   # Ensure workspace directory is writable
   chmod -R u+w ~/source/vibes/prps
   ```

---

### Issue 4: Network/Firewall Blocking

**Symptoms**:
- `codex login` fails with "connection refused"
- API requests timeout
- "Unable to reach OpenAI servers"

**Root Cause**: Firewall, proxy, or network restrictions

**Solutions**:
1. **Check firewall rules**:
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

   # Linux
   sudo ufw status
   ```

2. **Configure proxy** (if behind corporate firewall):
   ```bash
   export HTTPS_PROXY=http://proxy.company.com:8080
   codex login
   ```

3. **Test connectivity**:
   ```bash
   curl -I https://api.openai.com/v1/models
   # Should return: HTTP/2 200 (or 401 if not authenticated)
   ```

---

### Issue 5: Windows Compatibility Issues

**Symptoms**:
- Codex commands fail inconsistently on Windows
- PowerShell/CMD errors
- Approval prompts don't respect settings

**Root Cause**: Windows support is experimental; sandbox unreliable on native Windows

**Solutions**:
1. **Use WSL (Recommended)**:
   ```bash
   # Install WSL
   wsl --install

   # Inside WSL, install Codex
   npm install -g @openai/codex

   # Run from Windows
   wsl codex --version
   ```

2. **Use forward slashes in paths**:
   ```toml
   # In config.toml
   cwd = "C:/Users/jon/source/vibes"  # Works on Windows
   # NOT: cwd = "C:\Users\jon\source\vibes"
   ```

3. **Escalate sandbox mode** (if workspace-write fails):
   ```bash
   codex exec --sandbox danger-full-access --profile codex-prp "..."
   ```

---

## Quick Start Commands

Once installation and authentication are complete:

```bash
# 1. Create profile (see config guide for full profile)
mkdir -p ~/.codex
cat > ~/.codex/config.toml <<'EOF'
[profiles.codex-prp]
model = "o4-mini"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
cwd = "/Users/jon/source/vibes"
EOF

# 2. Test profile
codex config show --profile codex-prp

# 3. Run first command
codex exec --profile codex-prp "echo 'Codex is ready!'"

# 4. Interactive session (optional)
codex --profile codex-prp
```

---

## Health Check Script

Use this script to validate your Codex setup:

```bash
#!/bin/bash
# codex-health-check.sh

echo "=== Codex CLI Health Check ==="

# Check 1: CLI installed
echo -n "1. Codex CLI installed... "
if command -v codex &> /dev/null; then
    echo "✓ ($(codex --version))"
else
    echo "✗ Not found in PATH"
    exit 1
fi

# Check 2: Authentication
echo -n "2. Authentication... "
if codex login status &> /dev/null; then
    echo "✓ Authenticated"
else
    echo "✗ Not authenticated (run: codex login)"
    exit 1
fi

# Check 3: Sandbox test
echo -n "3. Sandbox execution... "
if codex exec --sandbox read-only "echo test" &> /dev/null; then
    echo "✓ Works"
else
    echo "✗ Sandbox not available"
fi

# Check 4: Profile (optional)
echo -n "4. Profile 'codex-prp'... "
if codex config show --profile codex-prp &> /dev/null; then
    echo "✓ Configured"
else
    echo "⚠ Not found (optional)"
fi

echo ""
echo "=== Health Check Complete ==="
echo "✓ Codex CLI ready for use"
```

---

## Next Steps

After completing bootstrap:

1. **Configure Profile**: See `docs/codex-config.md` for profile setup
2. **Understand Artifacts**: See `docs/codex-artifacts.md` for directory structure
3. **Learn Validation**: See `docs/codex-validation.md` for pre-flight checks
4. **Run Commands**: Use `/codex-generate-prp` or `/codex-execute-prp` (when available)

---

## Common Mistakes to Avoid

1. **Relying on `OPENAI_API_KEY` env var**: Codex does NOT read this (use `codex login` instead)
2. **Skipping auth verification**: Always run `codex login status` before execution
3. **Using default profile**: Always specify `--profile codex-prp` to avoid config pollution
4. **Ignoring sandbox errors**: Don't immediately escalate to `danger-full-access`; diagnose first
5. **Windows native installation**: Use WSL for reliability (native Windows support experimental)

---

## Support & Resources

- **Official Docs**: https://github.com/openai/codex/blob/main/docs/getting-started.md
- **Authentication Guide**: https://github.com/openai/codex/blob/main/docs/authentication.md
- **Sandbox Reference**: https://github.com/openai/codex/blob/main/docs/sandbox.md
- **Community Forum**: https://community.openai.com/c/codex-cli
- **GitHub Issues**: https://github.com/openai/codex/issues

---

**Bootstrap Complete**: You're ready to use Codex CLI for PRP-driven development!

**Last Updated**: 2025-10-07
**Tested Versions**: Codex CLI 1.0.0+
**Platforms**: macOS (primary), Linux (tested), Windows WSL (recommended)
