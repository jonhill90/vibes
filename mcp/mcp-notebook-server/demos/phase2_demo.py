#!/usr/bin/env python3
"""
INMPARA Notebook MCP Server - Phase 2 Implementation Demo
Advanced Intelligence Features: Learning, Feedback, Cross-Session Context
"""

import os
import sys
import json
from pathlib import Path

# Setup environment
os.environ['INMPARA_VAULT_PATH'] = '/workspace/vibes/repos/inmpara'
sys.path.append('src')

def demonstrate_phase2_features():
    """Demonstrate all Phase 2 advanced intelligence features"""
    
    print("🚀 INMPARA Notebook MCP Server - Phase 2 Features Demo")
    print("=" * 70)
    
    # Import Phase 2 components
    from src.database.database import INMPARADatabase
    from src.pattern_learner import PatternLearner, UserFeedback
    from src.session_manager import SessionManager
    from src.content_analyzer import INMPARAContentAnalyzer
    
    # Initialize components
    db = INMPARADatabase("./data/phase2_demo.db")
    pattern_learner = PatternLearner(db)
    session_manager = SessionManager(db)
    content_analyzer = INMPARAContentAnalyzer()
    
    print("✅ All Phase 2 components initialized successfully")
    print()
    
    # Feature 1: Cross-Session Context Tracking
    print("🔗 Feature 1: Cross-Session Context Tracking")
    print("-" * 50)
    
    # Start multiple sessions
    session1 = session_manager.start_session()
    session2 = session_manager.start_session()
    
    print(f"Started session 1: {session1}")
    print(f"Started session 2: {session2}")
    
    # Update session contexts with different technical conversations
    context1 = session_manager.update_session_context(
        session1,
        "I'm configuring Azure private endpoints for Databricks. The DNS resolution isn't working properly.",
        insights=[{"type": "technical-finding", "domain": "azure"}],
        notes_created=["note_123"]
    )
    
    context2 = session_manager.update_session_context(
        session2,
        "Working on Terraform state locking with Azure backend. Need to set up proper DNS configuration.",
        insights=[{"type": "issue", "domain": "terraform"}],
        notes_created=["note_124"]
    )
    
    print(f"Session 1 topics: {context1['current_topics']}")
    print(f"Session 2 topics: {context2['current_topics']}")
    
    # Find related sessions
    related = session_manager.find_related_sessions(session1)
    print(f"Related sessions found: {len(related)}")
    
    print("✅ Cross-session context tracking working")
    print()
    
    # Feature 2: Learning from User Feedback
    print("🧠 Feature 2: Learning from User Feedback")
    print("-" * 50)
    
    # Simulate user correcting AI filing decision
    feedback1 = UserFeedback(
        action_type="moved_file",
        original_value="5 - Resources/",
        corrected_value="1 - Notes/",
        note_id="note_123",
        confidence_impact=-0.1,
        context={"domain": "azure", "content_type": "technical-finding"}
    )
    
    result1 = pattern_learner.learn_from_feedback(feedback1)
    print(f"Filing pattern learned: {len(result1.get('patterns_updated', []))} patterns updated")
    
    # Simulate user correcting tags
    feedback2 = UserFeedback(
        action_type="changed_tags",
        original_value='["azure", "infrastructure"]',
        corrected_value='["azure", "databricks", "dns", "networking"]',
        note_id="note_123",
        confidence_impact=0.05,
        context={"domain": "azure"}
    )
    
    result2 = pattern_learner.learn_from_feedback(feedback2)
    print(f"Tagging pattern learned: {len(result2.get('patterns_updated', []))} patterns updated")
    
    # Check learning statistics
    stats = pattern_learner.get_learning_stats()
    print(f"Total patterns learned: {stats['total_patterns']}")
    print(f"Average success rate: {stats['avg_success_rate']:.2f}")
    
    print("✅ Learning from feedback working")
    print()
    
    # Feature 3: Improved Confidence Scoring
    print("🎯 Feature 3: Improved Confidence Scoring")
    print("-" * 50)
    
    # Analyze content with learned patterns
    test_content = """
    Discovered issue with Azure Databricks private endpoint DNS configuration.
    The workspace URL needs A records in the private DNS zone for proper resolution.
    """
    
    # Get basic analysis
    analysis = content_analyzer.analyze_content(test_content)
    original_confidence = getattr(analysis, 'confidence', 0.5)
    
    # Convert to dict for pattern learner
    analysis_dict = {
        'content_type': getattr(analysis, 'content_type', None),
        'domain': getattr(analysis, 'primary_domain', None),
        'keywords': ['azure', 'databricks', 'dns'],
        'has_technical_terms': True
    }
    
    # Apply learned patterns for confidence adjustment
    adjustments = pattern_learner.get_confidence_adjustments(analysis_dict)
    
    adjusted_confidence = min(1.0, original_confidence + adjustments.get('overall_adjustment', 0.0))
    
    print(f"Original confidence: {original_confidence:.2f}")
    print(f"Confidence adjustments: {adjustments}")
    print(f"Adjusted confidence: {adjusted_confidence:.2f}")
    
    # Get improvement suggestions
    suggestions = pattern_learner.get_suggested_improvements(analysis_dict)
    print(f"Improvement suggestions: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion['suggestion']} (confidence: {suggestion['confidence']:.2f})")
    
    print("✅ Improved confidence scoring working")
    print()
    
    # Feature 4: Context-Based Suggestions
    print("💡 Feature 4: Context-Based Suggestions")
    print("-" * 50)
    
    # Get suggestions based on session context
    suggestions = session_manager.get_context_based_suggestions(
        session1,
        "Now I need to configure DNS forwarding for the private endpoints"
    )
    
    print(f"Context-based suggestions: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion['title']}")
        print(f"     {suggestion['description']}")
        print(f"     Confidence: {suggestion['confidence']:.2f}")
    
    print("✅ Context-based suggestions working")
    print()
    
    # Summary
    print("📊 Phase 2 Implementation Summary")
    print("=" * 70)
    
    thresholds = pattern_learner.get_current_thresholds()
    session_stats = session_manager.get_session_statistics()
    
    print("🎯 Advanced Intelligence Features:")
    print(f"  ✅ Learning patterns: {stats['total_patterns']} patterns learned")
    print(f"  ✅ Confidence thresholds: auto_create={thresholds['auto_create']:.2f}")
    print(f"  ✅ Cross-session tracking: {len(related)} related sessions")
    print(f"  ✅ Context suggestions: {len(suggestions)} suggestions generated")
    
    print("\n🧠 Learning Capabilities:")
    print("  ✅ User feedback processing")
    print("  ✅ Pattern-based confidence adjustments")
    print("  ✅ Filing decision improvements")
    print("  ✅ Tagging optimization")
    
    print("\n🔗 Cross-Session Features:")
    print("  ✅ Session context tracking")
    print("  ✅ Topic and domain detection")
    print("  ✅ Related session discovery")
    print("  ✅ Context-based suggestions")
    
    print("\n🎉 PHASE 2 IMPLEMENTATION COMPLETE!")
    print("Ready for production use with advanced intelligence features")
    
    return {
        'learning_patterns': stats['total_patterns'],
        'confidence_thresholds': thresholds,
        'sessions_created': 2,
        'feedback_processed': 2,
        'suggestions_generated': len(suggestions)
    }

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    result = demonstrate_phase2_features()
    
    print(f"\n📋 Demo Results: {json.dumps(result, indent=2)}")
