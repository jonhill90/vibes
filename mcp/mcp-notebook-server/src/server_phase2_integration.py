"""
Integration code for Phase 2 tools into the main INMPARA server
This code should be added to the server.py file
"""

# Add these tool registrations after the existing tools in server.py

        # =================================
        # PHASE 2: Advanced Intelligence Tools
        # =================================

        @server.call_tool()
        async def learn_from_feedback(
            action_type: str,
            original_value: str, 
            corrected_value: str,
            note_id: str,
            context: str = ""
        ) -> List[TextContent]:
            """
            Learn from user feedback and corrections to improve AI decision making.
            This enables the system to adapt and improve based on user corrections.
            """
            try:
                import json
                from datetime import datetime
                
                feedback = UserFeedback(
                    action_type=action_type,
                    original_value=original_value,
                    corrected_value=corrected_value,
                    note_id=note_id,
                    confidence_impact=0.0,
                    context=json.loads(context) if context else {}
                )
                
                # Process feedback through pattern learner
                results = self.pattern_learner.learn_from_feedback(feedback)
                
                # Get updated statistics
                new_thresholds = self.pattern_learner.get_current_thresholds()
                learning_stats = self.pattern_learner.get_learning_stats()
                
                response = {
                    "success": True,
                    "feedback_processed": True,
                    "patterns_updated": results.get('patterns_updated', []),
                    "confidence_adjustments": results.get('confidence_adjustments', {}),
                    "updated_thresholds": new_thresholds,
                    "learning_stats": learning_stats,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"✅ Learned from {action_type}: {len(results.get('patterns_updated', []))} patterns updated"
                }
                
                return [TextContent(type="text", text=f"🧠 **Learning Update**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to process feedback"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def get_session_context(session_id: str = "") -> List[TextContent]:
            """
            Get or create conversation session context for cross-session tracking.
            Enables intelligent context awareness across multiple conversations.
            """
            try:
                if not session_id:
                    # Start new session
                    new_session_id = self.session_manager.start_session()
                    context = self.session_manager.get_session_context(new_session_id)
                    
                    response = {
                        "success": True,
                        "session_created": True,
                        "session_id": new_session_id,
                        "context": context,
                        "message": f"🆕 Started new session: {new_session_id}"
                    }
                else:
                    # Get existing session
                    context = self.session_manager.get_session_context(session_id)
                    
                    if context:
                        response = {
                            "success": True,
                            "session_found": True,
                            "session_id": session_id,
                            "context": context,
                            "message": f"📋 Retrieved session: {session_id}"
                        }
                    else:
                        # Create new session with provided ID
                        new_session_id = self.session_manager.start_session(session_id)
                        new_context = self.session_manager.get_session_context(new_session_id)
                        
                        response = {
                            "success": True,
                            "session_created": True,
                            "session_id": new_session_id,
                            "context": new_context,
                            "message": f"🆕 Session not found, created: {new_session_id}"
                        }
                
                return [TextContent(type="text", text=f"📱 **Session Context**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to get session context"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def update_session_context(
            session_id: str,
            conversation_text: str,
            insights: str = "[]",
            notes_created: str = "[]"
        ) -> List[TextContent]:
            """
            Update session context with new conversation data and get intelligent suggestions.
            This enables cross-conversation learning and context awareness.
            """
            try:
                import json
                
                insights_list = json.loads(insights) if insights else []
                notes_list = json.loads(notes_created) if notes_created else []
                
                # Update session context
                updated_context = self.session_manager.update_session_context(
                    session_id=session_id,
                    conversation_text=conversation_text,
                    insights=insights_list,
                    notes_created=notes_list
                )
                
                # Get context-based suggestions
                suggestions = self.session_manager.get_context_based_suggestions(
                    session_id, conversation_text
                )
                
                response = {
                    "success": True,
                    "session_updated": True,
                    "context": updated_context,
                    "suggestions": suggestions,
                    "cross_session_connections": updated_context.get('cross_session_connections', []),
                    "message": f"🔄 Updated session {session_id} with new context"
                }
                
                return [TextContent(type="text", text=f"🧠 **Context Update**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to update session context"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def find_related_sessions(session_id: str, limit: int = 5) -> List[TextContent]:
            """
            Find sessions related to the current session for cross-conversation context.
            Discovers connections between different conversation sessions.
            """
            try:
                related_sessions = self.session_manager.find_related_sessions(session_id, limit)
                session_stats = self.session_manager.get_session_statistics()
                
                response = {
                    "success": True,
                    "session_id": session_id,
                    "related_sessions": related_sessions,
                    "total_found": len(related_sessions),
                    "session_statistics": session_stats,
                    "message": f"🔗 Found {len(related_sessions)} related sessions"
                }
                
                return [TextContent(type="text", text=f"🔍 **Related Sessions**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to find related sessions"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def get_learning_insights() -> List[TextContent]:
            """
            Get insights about learned patterns and AI decision improvements.
            Shows how the system has learned and adapted from user feedback.
            """
            try:
                # Get learning statistics
                learning_stats = self.pattern_learner.get_learning_stats()
                thresholds = self.pattern_learner.get_current_thresholds()
                
                # Get recent patterns by type
                recent_patterns = {
                    'filing': self.db.get_learning_patterns('filing')[:5],
                    'tagging_positive': self.db.get_learning_patterns('tagging_positive')[:5],
                    'relation_positive': self.db.get_learning_patterns('relation_positive')[:3]
                }
                
                # Get processing statistics
                processing_stats = self.db.get_processing_stats(days=30)
                
                response = {
                    "success": True,
                    "learning_statistics": learning_stats,
                    "confidence_thresholds": thresholds,
                    "recent_patterns": recent_patterns,
                    "processing_statistics": processing_stats,
                    "message": f"🎯 AI has learned {learning_stats['total_patterns']} patterns with {learning_stats['avg_success_rate']:.2f} avg success rate"
                }
                
                return [TextContent(type="text", text=f"🧠 **Learning Insights**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to get learning insights"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def review_recent_auto_filings(days: int = 7) -> List[TextContent]:
            """
            Review recent AI decisions for audit and approval.
            Provides transparency and control over AI decision making.
            """
            try:
                from datetime import datetime, timedelta
                import sqlite3
                
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Get recent processing log entries
                with self.db.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute("""
                        SELECT * FROM processing_log
                        WHERE timestamp >= ?
                        ORDER BY timestamp DESC
                        LIMIT 50
                    """, (cutoff_date,))
                    
                    recent_actions = []
                    for row in cursor.fetchall():
                        action_dict = dict(row)
                        
                        # Add note details if available
                        if action_dict['action'] == 'auto_create_note' and action_dict['destination_path']:
                            note_info = self.db.search_notes({'file_path': action_dict['destination_path']})
                            if note_info:
                                action_dict['note_details'] = note_info[0]
                        
                        recent_actions.append(action_dict)
                
                # Group by action type
                actions_by_type = {}
                for action in recent_actions:
                    action_type = action['action']
                    if action_type not in actions_by_type:
                        actions_by_type[action_type] = []
                    actions_by_type[action_type].append(action)
                
                # Calculate statistics
                total_actions = len(recent_actions)
                approved_count = sum(1 for a in recent_actions if a.get('user_approved') == 1)
                rejected_count = sum(1 for a in recent_actions if a.get('user_approved') == 0)
                pending_count = sum(1 for a in recent_actions if a.get('user_approved') is None)
                
                response = {
                    "success": True,
                    "review_period_days": days,
                    "total_actions": total_actions,
                    "approved_count": approved_count,
                    "rejected_count": rejected_count,
                    "pending_count": pending_count,
                    "approval_rate": approved_count / total_actions if total_actions > 0 else 0.0,
                    "actions_by_type": actions_by_type,
                    "recent_actions": recent_actions[:10],  # Show top 10 for readability
                    "message": f"📊 Found {total_actions} recent actions ({approved_count} approved, {rejected_count} rejected, {pending_count} pending)"
                }
                
                return [TextContent(type="text", text=f"📋 **Recent Auto-Filings Review**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to review recent auto-filings"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def approve_auto_filing(action_id: int, approved: bool, feedback: str = "") -> List[TextContent]:
            """
            Approve or reject a specific auto-filing action for learning.
            Provides user control and enables learning from corrections.
            """
            try:
                import sqlite3
                
                # Get database connection
                with self.db.get_connection() as conn:
                    # Get the original action
                    cursor = conn.execute("""
                        SELECT * FROM processing_log WHERE id = ?
                    """, (action_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return [TextContent(type="text", text=f"❌ No action found with ID {action_id}")]
                    
                    # Convert row to dict
                    action = dict(sqlite3.Row(cursor.description, row))
                    
                    # Update approval status
                    conn.execute("""
                        UPDATE processing_log 
                        SET user_approved = ?
                        WHERE id = ?
                    """, (1 if approved else 0, action_id))
                    
                    # Learn from rejection feedback
                    if not approved and action['action'] in ['auto_create_note', 'auto_file_note']:
                        user_feedback = UserFeedback(
                            action_type="action_rejected",
                            original_value=action['destination_path'] or "",
                            corrected_value=feedback,
                            note_id=action.get('note_id', ''),
                            confidence_impact=-0.1,
                            context={"action_id": action_id, "original_action": action['action']}
                        )
                        
                        # Process through pattern learner
                        self.pattern_learner.learn_from_feedback(user_feedback)
                
                response = {
                    "success": True,
                    "action_id": action_id,
                    "approved": approved,
                    "feedback": feedback,
                    "learning_triggered": not approved,
                    "original_action": action,
                    "message": f"✅ Action {action_id} {'approved' if approved else 'rejected'}"
                }
                
                return [TextContent(type="text", text=f"⚡ **Filing Decision**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to approve/reject auto-filing"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]

        @server.call_tool()
        async def get_confidence_suggestions(content: str, content_type: str = "") -> List[TextContent]:
            """
            Get confidence-adjusted suggestions based on learned patterns.
            Shows how learning has improved confidence in AI decisions.
            """
            try:
                # Analyze content
                analysis = self.content_analyzer.analyze_content(content)
                
                # Get confidence adjustments from learned patterns
                confidence_adjustments = self.pattern_learner.get_confidence_adjustments(analysis)
                
                # Apply adjustments
                original_confidence = analysis.get('confidence', 0.0)
                adjusted_confidence = original_confidence + confidence_adjustments['overall_adjustment']
                adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))
                
                # Get pattern-based suggestions
                suggestions = self.pattern_learner.get_suggested_improvements(analysis)
                
                # Get current thresholds
                thresholds = self.pattern_learner.get_current_thresholds()
                
                # Determine recommended action
                if adjusted_confidence >= thresholds['auto_create']:
                    recommended_action = "auto_create"
                elif adjusted_confidence >= thresholds['suggest']:
                    recommended_action = "suggest"
                else:
                    recommended_action = "no_action"
                
                response = {
                    "success": True,
                    "original_analysis": analysis,
                    "confidence_adjustments": confidence_adjustments,
                    "original_confidence": original_confidence,
                    "adjusted_confidence": adjusted_confidence,
                    "recommended_action": recommended_action,
                    "pattern_suggestions": suggestions,
                    "current_thresholds": thresholds,
                    "message": f"🎯 Confidence adjusted from {original_confidence:.2f} to {adjusted_confidence:.2f}"
                }
                
                return [TextContent(type="text", text=f"📊 **Confidence Analysis**\n\n{json.dumps(response, indent=2)}")]
                
            except Exception as e:
                error_response = {
                    "success": False,
                    "error": str(e),
                    "message": "❌ Failed to get confidence suggestions"
                }
                return [TextContent(type="text", text=f"Error: {json.dumps(error_response, indent=2)}")]
