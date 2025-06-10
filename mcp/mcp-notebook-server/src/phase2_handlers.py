        # Phase 2 tool handlers
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle all tool calls including Phase 2 advanced features."""
            try:
                # Phase 1 tools (existing handlers remain the same)
                if name == "capture_conversation_insight":
                    result = await capture_conversation_insight(
                        arguments.get("conversation_text", ""),
                        arguments.get("session_id", "")
                    )
                elif name == "auto_create_note":
                    result = await auto_create_note(
                        arguments.get("content", ""),
                        arguments.get("title", ""),
                        arguments.get("force_create", False)
                    )
                elif name == "search_semantic":
                    result = await search_semantic(
                        arguments.get("query", ""),
                        arguments.get("limit", 10),
                        arguments.get("threshold", 0.7)
                    )
                elif name == "suggest_connections":
                    result = await suggest_connections(
                        arguments.get("content", ""),
                        arguments.get("limit", 5)
                    )
                elif name == "get_inbox_items":
                    result = await get_inbox_items()
                elif name == "get_recent_insights":
                    result = await get_recent_insights(arguments.get("limit", 10))
                elif name == "search_exact":
                    result = await search_exact(
                        arguments.get("query", ""),
                        arguments.get("limit", 20)
                    )
                elif name == "get_vault_analytics":
                    result = await get_vault_analytics()
                elif name == "validate_inmpara_format":
                    result = await validate_inmpara_format(arguments.get("file_path", ""))
                elif name == "start_conversation_session":
                    result = await start_conversation_session()
                
                # Phase 2: Advanced intelligence tools
                elif name == "learn_from_feedback":
                    result = await learn_from_feedback_tool(
                        arguments.get("action_type", ""),
                        arguments.get("original_value", ""),
                        arguments.get("corrected_value", ""),
                        arguments.get("note_id", ""),
                        arguments.get("context", "{}")
                    )
                elif name == "get_session_context":
                    result = await get_session_context_tool(
                        arguments.get("session_id", "")
                    )
                elif name == "update_session_context":
                    result = await update_session_context_tool(
                        arguments.get("session_id", ""),
                        arguments.get("conversation_text", ""),
                        arguments.get("insights", "[]"),
                        arguments.get("notes_created", "[]")
                    )
                elif name == "find_related_sessions":
                    result = await find_related_sessions_tool(
                        arguments.get("session_id", ""),
                        arguments.get("limit", 5)
                    )
                elif name == "get_learning_insights":
                    result = await get_learning_insights_tool()
                elif name == "review_recent_auto_filings":
                    result = await review_recent_auto_filings_tool(
                        arguments.get("days", 7)
                    )
                elif name == "approve_recent_actions":
                    result = await approve_recent_actions_tool(
                        arguments.get("action_ids", ""),
                        arguments.get("approved", True)
                    )
                elif name == "get_confidence_recommendations":
                    result = await get_confidence_recommendations_tool(
                        arguments.get("content", "")
                    )
                else:
                    result = {"error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.error(f"Error handling tool call {name}: {str(e)}")
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
