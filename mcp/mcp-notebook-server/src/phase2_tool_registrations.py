        # Phase 2: Learning and feedback tools
        @server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools including Phase 2 advanced features."""
            return [
                # Phase 1 tools (existing)
                Tool(
                    name="capture_conversation_insight",
                    description="Intelligently capture and create INMPARA notes from conversation insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "conversation_text": {"type": "string"},
                            "session_id": {"type": "string", "default": ""}
                        },
                        "required": ["conversation_text"]
                    }
                ),
                Tool(
                    name="auto_create_note",
                    description="Create INMPARA-formatted note with automatic analysis and filing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "title": {"type": "string", "default": ""},
                            "force_create": {"type": "boolean", "default": False}
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="search_semantic",
                    description="Search vault content using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 10},
                            "threshold": {"type": "number", "default": 0.7}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="suggest_connections",
                    description="Suggest connections to existing vault content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "limit": {"type": "integer", "default": 5}
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="get_inbox_items",
                    description="Get items from inbox with analysis preview",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_recent_insights",
                    description="Get recently captured insights and their status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 10}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="search_exact",
                    description="Search vault using exact text matching",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 20}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_vault_analytics",
                    description="Get analytics about vault content and growth",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="validate_inmpara_format",
                    description="Validate INMPARA formatting compliance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="start_conversation_session",
                    description="Start new conversation session for context tracking",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                
                # Phase 2: Advanced intelligence tools
                Tool(
                    name="learn_from_feedback",
                    description="Learn from user corrections to improve AI decision making",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action_type": {"type": "string", "enum": ["moved_file", "changed_tags", "edited_content", "added_relation", "removed_relation"]},
                            "original_value": {"type": "string"},
                            "corrected_value": {"type": "string"},
                            "note_id": {"type": "string"},
                            "context": {"type": "string", "default": "{}"}
                        },
                        "required": ["action_type", "original_value", "corrected_value", "note_id"]
                    }
                ),
                Tool(
                    name="get_session_context",
                    description="Get or create conversation session context for cross-session tracking",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "default": ""}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="update_session_context",
                    description="Update session context with new conversation data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "conversation_text": {"type": "string"},
                            "insights": {"type": "string", "default": "[]"},
                            "notes_created": {"type": "string", "default": "[]"}
                        },
                        "required": ["session_id", "conversation_text"]
                    }
                ),
                Tool(
                    name="find_related_sessions",
                    description="Find sessions related to current session for cross-conversation context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string"},
                            "limit": {"type": "integer", "default": 5}
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="get_learning_insights",
                    description="Get insights about learned patterns and AI decision improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="review_recent_auto_filings",
                    description="Review recent AI decisions for audit and approval",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days": {"type": "integer", "default": 7}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="approve_recent_actions",
                    description="Approve or reject recent AI actions for learning feedback",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action_ids": {"type": "string"},
                            "approved": {"type": "boolean", "default": True}
                        },
                        "required": ["action_ids"]
                    }
                ),
                Tool(
                    name="get_confidence_recommendations",
                    description="Get confidence-based recommendations using learned patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"}
                        },
                        "required": ["content"]
                    }
                )
            ]
