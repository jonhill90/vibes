            "actions_by_type": actions_by_type,
            "recent_actions": recent_actions[:20],  # Most recent 20
            "message": f"Found {total_actions} recent actions: {approved_count} approved, {rejected_count} rejected, {pending_count} pending"
        }
        
    except Exception as e:
        logger.error(f"Error in review_recent_auto_filings: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to review recent auto-filings"
        }

async def enhanced_confidence_scoring_tool(content: str, context: str = "{}"):
    """
    Get enhanced confidence scoring based on learned patterns.
    
    Args:
        content: Content to analyze
        context: Additional context as JSON string
    """
    try:
        import json
        
        context_dict = json.loads(context) if context else {}
        
        # Run standard content analysis
        analysis = content_analyzer.analyze_content(content)
        
        # Get confidence adjustments from learned patterns
        adjustments = pattern_learner.get_confidence_adjustments(analysis)
        
        # Apply adjustments
        enhanced_confidence = analysis.get('confidence', 0.0) + adjustments.get('overall_adjustment', 0.0)
        enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))  # Clamp to [0,1]
        
        # Get suggestions for improvement
        suggestions = pattern_learner.get_suggested_improvements(analysis)
        
        return {
            "success": True,
            "original_confidence": analysis.get('confidence', 0.0),
            "enhanced_confidence": enhanced_confidence,
            "confidence_adjustments": adjustments,
            "analysis": analysis,
            "improvement_suggestions": suggestions,
            "current_thresholds": pattern_learner.get_current_thresholds(),
            "message": f"Enhanced confidence: {enhanced_confidence:.3f} (original: {analysis.get('confidence', 0.0):.3f})"
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced_confidence_scoring: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get enhanced confidence scoring"
        }

async def cross_session_insights_tool(session_id: str, query: str = ""):
    """
    Get insights from cross-session analysis and related conversations.
    
    Args:
        session_id: Current session ID
        query: Optional query to focus the insights
    """
    try:
        # Get current session context
        current_context = session_manager.get_session_context(session_id)
        if not current_context:
            return {
                "success": False,
                "error": "Session not found",
                "message": f"Session {session_id} not found"
            }
        
        # Find related sessions
        related_sessions = session_manager.find_related_sessions(session_id, limit=10)
        
        # Get cross-session insights
        insights = []
        
        # Analyze patterns across sessions
        if related_sessions:
            # Topic evolution insights
            topic_evolution = {}
            for session in related_sessions:
                for topic in session.get('shared_topics', []):
                    if topic not in topic_evolution:
                        topic_evolution[topic] = 0
                    topic_evolution[topic] += 1
            
            if topic_evolution:
                most_common_topic = max(topic_evolution.items(), key=lambda x: x[1])
                insights.append({
                    'type': 'topic_pattern',
                    'title': f"Recurring topic: {most_common_topic[0]}",
                    'description': f"This topic has appeared in {most_common_topic[1]} related sessions",
                    'confidence': 0.8,
                    'details': topic_evolution
                })
            
            # Domain progression insights
            domain_progression = {}
            for session in related_sessions:
                for domain in session.get('shared_domains', []):
                    if domain not in domain_progression:
                        domain_progression[domain] = 0
                    domain_progression[domain] += 1
            
            if domain_progression:
                primary_domain = max(domain_progression.items(), key=lambda x: x[1])
                insights.append({
                    'type': 'domain_focus',
                    'title': f"Primary domain: {primary_domain[0]}",
                    'description': f"Your recent conversations focus heavily on {primary_domain[0]} ({primary_domain[1]} sessions)",
                    'confidence': 0.9,
                    'details': domain_progression
                })
        
        # Get related notes that might provide additional context
        current_domains = set(current_context.get('domains', []))
        current_topics = set(current_context.get('topics', []))
        
        if current_domains:
            related_notes = []
            for domain in current_domains:
                notes = db.search_notes({'domain': domain})
                related_notes.extend(notes[:3])  # Top 3 per domain
            
            if related_notes:
                insights.append({
                    'type': 'knowledge_base',
                    'title': f"Related knowledge base",
                    'description': f"Found {len(related_notes)} related notes in your vault",
                    'confidence': 0.7,
                    'details': {
                        'note_count': len(related_notes),
                        'notes': [{'title': note.get('title'), 'file_path': note.get('file_path')} 
                                for note in related_notes[:5]]
                    }
                })
        
        return {
            "success": True,
            "session_id": session_id,
            "current_context": current_context,
            "related_sessions_count": len(related_sessions),
            "cross_session_insights": insights,
            "related_sessions": related_sessions[:5],  # Top 5 most related
            "message": f"Found {len(insights)} cross-session insights from {len(related_sessions)} related sessions"
        }
        
    except Exception as e:
        logger.error(f"Error in cross_session_insights: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get cross-session insights"
        }
            "actions_by_type": actions_by_type,
            "recent_actions": recent_actions,
            "message": f"Found {total_actions} recent actions: {approved_count} approved, {rejected_count} rejected, {pending_count} pending"
        }
        
    except Exception as e:
        logger.error(f"Error in review_recent_auto_filings: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to review recent auto-filings"
        }

async def apply_learned_improvements_tool(
    content_text: str,
    content_type: str = None,
    domain: str = None
):
    """
    Apply learned patterns to improve content analysis and suggestions.
    
    Args:
        content_text: Content to analyze with learned improvements
        content_type: Optional content type hint
        domain: Optional domain hint
    """
    try:
        # Analyze content with current analyzer
        analysis = content_analyzer.analyze_content(content_text)
        
        # Get confidence adjustments from learned patterns
        confidence_adjustments = pattern_learner.get_confidence_adjustments(analysis)
        
        # Apply adjustments
        adjusted_analysis = analysis.copy()
        adjusted_analysis['original_confidence'] = analysis.get('confidence', 0.0)
        adjusted_analysis['confidence'] = min(1.0, max(0.0, 
            analysis.get('confidence', 0.0) + confidence_adjustments['overall_adjustment']
        ))
        
        # Get improvement suggestions
        suggestions = pattern_learner.get_suggested_improvements(analysis)
        
        # Get current thresholds for decision making
        thresholds = pattern_learner.get_current_thresholds()
        
        # Make filing decision with adjusted confidence
        if adjusted_analysis['confidence'] >= thresholds['auto_file']:
            decision = "auto_file"
        elif adjusted_analysis['confidence'] >= thresholds['suggest']:
            decision = "suggest"
        else:
            decision = "manual_review"
        
        return {
            "success": True,
            "original_analysis": analysis,
            "adjusted_analysis": adjusted_analysis,
            "confidence_adjustments": confidence_adjustments,
            "improvement_suggestions": suggestions,
            "decision_thresholds": thresholds,
            "recommended_action": decision,
            "improvements_applied": len(suggestions),
            "message": f"Applied {len(suggestions)} learned improvements, confidence adjusted from {analysis.get('confidence', 0.0):.2f} to {adjusted_analysis['confidence']:.2f}"
        }
        
    except Exception as e:
        logger.error(f"Error in apply_learned_improvements: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to apply learned improvements"
        }
            "actions_by_type": actions_by_type,
            "recent_actions": recent_actions,
            "message": f"Found {total_actions} recent actions ({approved_count} approved, {rejected_count} rejected, {pending_count} pending)"
        }
        
    except Exception as e:
        logger.error(f"Error in review_recent_auto_filings: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to review recent auto-filings"
        }

async def approve_auto_filing_tool(action_id: int, approved: bool, feedback: str = ""):
    """
    Approve or reject a specific auto-filing action for learning.
    
    Args:
        action_id: ID of the processing log entry
        approved: Whether to approve (True) or reject (False) the action
        feedback: Optional feedback about the decision
    """
    try:
        # Update the processing log entry
        with db.get_connection() as conn:
            # Get the original action
            cursor = conn.execute("""
                SELECT * FROM processing_log WHERE id = ?
            """, (action_id,))
            
            action = cursor.fetchone()
            if not action:
                return {
                    "success": False,
                    "error": "Action not found",
                    "message": f"No action found with ID {action_id}"
                }
            
            # Update approval status
            conn.execute("""
                UPDATE processing_log 
                SET user_approved = ?, feedback = ?
                WHERE id = ?
            """, (1 if approved else 0, feedback, action_id))
            
            # Learn from this feedback if it's a rejection
            if not approved and action['action'] in ['auto_create_note', 'auto_file_note']:
                # Create feedback for learning
                user_feedback = UserFeedback(
                    action_type="action_rejected",
                    original_value=action['destination_path'],
                    corrected_value=feedback,
                    note_id=action.get('note_id', ''),
                    confidence_impact=-0.1,
                    context={"action_id": action_id, "original_action": action['action']}
                )
                
                # Process through pattern learner
                pattern_learner.learn_from_feedback(user_feedback)
        
        return {
            "success": True,
            "action_id": action_id,
            "approved": approved,
            "feedback": feedback,
            "learning_triggered": not approved,
            "message": f"Action {action_id} {'approved' if approved else 'rejected'}"
        }
        
    except Exception as e:
        logger.error(f"Error in approve_auto_filing: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to approve/reject auto-filing"
        }

async def get_confidence_suggestions_tool(content: str, content_type: str = ""):
    """
    Get confidence-adjusted suggestions for content based on learned patterns.
    
    Args:
        content: Text content to analyze
        content_type: Optional content type hint
    """
    try:
        # Analyze content
        analysis = content_analyzer.analyze_content(content)
        
        # Get confidence adjustments from learned patterns
        confidence_adjustments = pattern_learner.get_confidence_adjustments(analysis)
        
        # Apply adjustments to original confidence
        adjusted_confidence = analysis.get('confidence', 0.0) + confidence_adjustments['overall_adjustment']
        adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))  # Clamp to [0,1]
        
        # Get pattern-based suggestions
        suggestions = pattern_learner.get_suggested_improvements(analysis)
        
        # Get current thresholds
        thresholds = pattern_learner.get_current_thresholds()
        
        # Determine recommended action based on adjusted confidence
        if adjusted_confidence >= thresholds['auto_create']:
            recommended_action = "auto_create"
        elif adjusted_confidence >= thresholds['suggest']:
            recommended_action = "suggest"
        else:
            recommended_action = "no_action"
        
        return {
            "success": True,
            "original_analysis": analysis,
            "confidence_adjustments": confidence_adjustments,
            "adjusted_confidence": adjusted_confidence,
            "recommended_action": recommended_action,
            "pattern_suggestions": suggestions,
            "current_thresholds": thresholds,
            "message": f"Confidence adjusted from {analysis.get('confidence', 0.0):.2f} to {adjusted_confidence:.2f}"
        }
        
    except Exception as e:
        logger.error(f"Error in get_confidence_suggestions: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get confidence suggestions"
        }
            "actions_by_type": actions_by_type,
            "recent_actions": recent_actions,
            "message": f"Reviewed {total_actions} recent actions from last {days} days"
        }
        
    except Exception as e:
        logger.error(f"Error in review_recent_auto_filings: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to review recent auto-filings"
        }

async def approve_recent_actions_tool(action_ids: str, approved: bool = True):
    """
    Approve or reject recent AI actions for learning feedback.
    
    Args:
        action_ids: Comma-separated list of processing log IDs
        approved: Whether to approve (True) or reject (False) the actions
    """
    try:
        import sqlite3
        from datetime import datetime
        
        ids = [int(id.strip()) for id in action_ids.split(',') if id.strip()]
        
        results = {
            "updated_count": 0,
            "learning_updates": [],
            "errors": []
        }
        
        with db.get_connection() as conn:
            for action_id in ids:
                try:
                    # Update approval status
                    cursor = conn.execute("""
                        UPDATE processing_log 
                        SET user_approved = ?
                        WHERE id = ?
                    """, (1 if approved else 0, action_id))
                    
                    if cursor.rowcount > 0:
                        results["updated_count"] += 1
                        
                        # Get the action details for learning
                        cursor = conn.execute("""
                            SELECT * FROM processing_log WHERE id = ?
                        """, (action_id,))
                        
                        action = cursor.fetchone()
                        if action:
                            # Create feedback for learning
                            if not approved:
                                # This was a mistake, create negative feedback
                                feedback = UserFeedback(
                                    action_type="ai_decision_rejected",
                                    original_value=action['destination_path'],
                                    corrected_value="rejected_by_user",
                                    note_id=action.get('source_path', ''),
                                    confidence_impact=-0.1,
                                    context={"action_id": action_id, "reasoning": action.get('reasoning', '')}
                                )
                                
                                learning_result = pattern_learner.learn_from_feedback(feedback)
                                results["learning_updates"].append({
                                    "action_id": action_id,
                                    "learning_result": learning_result
                                })
                    
                except Exception as e:
                    results["errors"].append({
                        "action_id": action_id,
                        "error": str(e)
                    })
        
        status = "approved" if approved else "rejected"
        return {
            "success": True,
            "updated_count": results["updated_count"],
            "learning_updates": results["learning_updates"],
            "errors": results["errors"],
            "message": f"Successfully {status} {results['updated_count']} actions"
        }
        
    except Exception as e:
        logger.error(f"Error in approve_recent_actions: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to approve/reject actions"
        }

async def get_confidence_recommendations_tool(content: str):
    """
    Get confidence-based recommendations for content using learned patterns.
    
    Args:
        content: Content to analyze for recommendations
    """
    try:
        # Analyze content using existing analyzer
        analysis = content_analyzer.analyze_content(content)
        
        # Get confidence adjustments from learned patterns
        adjustments = pattern_learner.get_confidence_adjustments({
            'content_type': analysis.get('content_type'),
            'domain': analysis.get('domain'),
            'keywords': analysis.get('keywords', []),
            'word_count': len(content.split()),
            'has_technical_terms': any(term in content.lower() for term in 
                                     ['azure', 'terraform', 'dns', 'api', 'config'])
        })
        
        # Apply adjustments to original confidence
        original_confidence = analysis.get('confidence', 0.5)
        adjusted_confidence = min(1.0, original_confidence + adjustments.get('overall_adjustment', 0.0))
        
        # Get improvement suggestions
        suggestions = pattern_learner.get_suggested_improvements(analysis)
        
        # Determine recommendation based on adjusted confidence
        if adjusted_confidence >= pattern_learner.get_current_thresholds()['auto_create']:
            recommendation = "auto_create"
        elif adjusted_confidence >= pattern_learner.get_current_thresholds()['suggest']:
            recommendation = "suggest"
        else:
            recommendation = "manual_review"
        
        return {
            "success": True,
            "original_analysis": analysis,
            "original_confidence": original_confidence,
            "confidence_adjustments": adjustments,
            "adjusted_confidence": adjusted_confidence,
            "recommendation": recommendation,
            "improvement_suggestions": suggestions,
            "current_thresholds": pattern_learner.get_current_thresholds(),
            "message": f"Confidence adjusted from {original_confidence:.2f} to {adjusted_confidence:.2f} - {recommendation}"
        }
        
    except Exception as e:
        logger.error(f"Error in get_confidence_recommendations: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get confidence recommendations"
        }
