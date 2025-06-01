        Tool(
            name="run_command",
            description="Execute shell commands in the jumpbox environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory (optional)",
                        "default": "/workspace"
                    }
                },
                "required": ["command"]
            }
        )