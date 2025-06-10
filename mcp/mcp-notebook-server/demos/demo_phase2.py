#!/usr/bin/env python3
"""
INMPARA Notebook MCP Server - Phase 2 Demo
Demonstrates advanced intelligence features: learning, feedback, cross-session context
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.database import INMPARADatabase
from pattern_learner import PatternLearner, UserFeedback
from session_manager import SessionManager
from content_analyzer import INMPARAContentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_phase2_features():
    """Comprehensive demo of Phase 2 advanced intelligence features"""
    
    print("🚀 INMPARA Notebook MCP Server - Phase 2 Demo")
    print("=" * 60)
    print("Demonstrating: Learning from Feedback, Cross-Session Context, Improved Confidence")
    print()
    
    # Initialize components
    vault_path = "/workspace/vibes/repos/inmpara"
    db_path = "./data/demo_phase2.db"
    
    # Clean start
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize database
    db = INMPARADatabase(db_path)
    await db.initialize()
    
    # Initialize components
    content_analyzer = INMPARAContentAnalyzer(vault_path)
    pattern_learner = PatternLearner(db)
    session_manager = SessionManager(db)
    
    print("✅ Initialized database and components")
    print()
    
    # =================================
    # Demo 1: Session Management and Cross-Session Context
    # =================================
    print("📱 DEMO 1: Session Management & Cross-Session Context")
    print("-" * 50)
    
    # Start first session
    session1_id = session_manager.start_session()
    print(f"🆕 Started session 1: {session1_id}")
    
    # Simulate conversation in session 1
    conversation1 = """
    I'm working on Azure Databricks and having issues with private endpoints.
    The DNS resolution isn't working properly for the workspace URL.
    I discovered that you need to create A records in the private DNS zone.
    """
    
    context1 = session_manager.update_session_context(
        session_id=session1_id,
        conversation_text=conversation1,
        insights=[
            {"text": "DNS resolution issues with Databricks private endpoints", "confidence": 0.9},
            {"text": "Need A records in private DNS zone", "confidence": 0.95}
        ],
        notes_created=["note1", "note2"]
    )
    
    print(f"📝 Session 1 context: {context1['current_topics']} | {context1['current_domains']}")
    print()
    
    # Start second session (different time)
    await asyncio.sleep(1)  # Small delay to simulate time difference
    session2_id = session_manager.start_session()
    print(f"🆕 Started session 2: {session2_id}")
    
    # Simulate conversation in session 2 (related topic)
    conversation2 = """
    Now I'm setting up private endpoints for Azure Storage.
    I remember having similar DNS issues before.
    The private DNS zone configuration seems similar to what I did with Databricks.
    """
    
    context2 = session_manager.update_session_context(
        session_id=session2_id,
        conversation_text=conversation2,
        insights=[
            {"text": "Setting up Azure Storage private endpoints", "confidence": 0.85},
            {"text": "Similar DNS configuration to Databricks", "confidence": 0.9}
        ]
    )
    
    print(f"📝 Session 2 context: {context2['current_topics']} | {context2['current_domains']}")
    
    # Find related sessions
    related_sessions = session_manager.find_related_sessions(session2_id)
    print(f"🔗 Found {len(related_sessions)} related sessions:")
    for session in related_sessions:
        print(f"   - {session['session_id']}: {session['similarity']:.2f} similarity")
        print(f"     Shared: {session['shared_domains']} domains, {session['shared_topics']} topics")
    print()
    
    # Get context-based suggestions
    suggestions = session_manager.get_context_based_suggestions(session2_id, conversation2)
    print(f"💡 Context-based suggestions: {len(suggestions)} found")
    for suggestion in suggestions:
        print(f"   - {suggestion['type']}: {suggestion['title']} (confidence: {suggestion['confidence']:.2f})")
    print()
    
    # =================================
    # Demo 2: Pattern Learning from Feedback
    # =================================
    print("🧠 DEMO 2: Pattern Learning from User Feedback")
    print("-" * 50)
    
    # Simulate AI making a filing decision
    test_content = "Azure Databricks private endpoint DNS configuration troubleshooting"
    analysis = content_analyzer.analyze_content(test_content)
    
    print(f"🤖 AI Analysis:")
    print(f"   Content Type: {analysis.get('content_type')}")
    print(f"   Domain: {analysis.get('domain')}")
    print(f"   Suggested Folder: {analysis.get('destination_folder')}")
    print(f"   Original Confidence: {analysis.get('confidence', 0.0):.2f}")
    print()
    
    # User corrects the AI decision
    print("👤 User moves file from '1 - Notes' to '5 - Resources'")
    
    feedback1 = UserFeedback(
        action_type="moved_file",
        original_value="1 - Notes",
        corrected_value="5 - Resources", 
        note_id="test_note_1",
        confidence_impact=-0.1,
        context={"content_type": analysis.get('content_type'), "domain": analysis.get('domain')}
    )
    
    # Learn from feedback
    learning_results = pattern_learner.learn_from_feedback(feedback1)
    print(f"📚 Learning Results:")
    print(f"   Patterns Updated: {len(learning_results.get('patterns_updated', []))}")
    print(f"   New Patterns: {len(learning_results.get('new_patterns_created', []))}")
    print()
    
    # User also changes tags
    print("👤 User changes tags from ['dns', 'azure', 'databricks'] to ['dns', 'azure', 'databricks', 'troubleshooting']")
    
    feedback2 = UserFeedback(
        action_type="changed_tags",
        original_value=json.dumps(["dns", "azure", "databricks"]),
        corrected_value=json.dumps(["dns", "azure", "databricks", "troubleshooting"]),
        note_id="test_note_1",
        confidence_impact=0.0,
        context={}
    )
    
    learning_results2 = pattern_learner.learn_from_feedback(feedback2)
    print(f"📚 Tag Learning Results:")
    print(f"   Patterns Updated: {len(learning_results2.get('patterns_updated', []))}")
    print()
    
    # Test improved confidence scoring
    print("🎯 Testing Improved Confidence Scoring")
    print("-" * 40)
    
    # Re-analyze similar content
    similar_content = "Azure Storage private endpoint DNS troubleshooting guide"
    new_analysis = content_analyzer.analyze_content(similar_content)
    
    # Get confidence adjustments
    confidence_adjustments = pattern_learner.get_confidence_adjustments(new_analysis)
    adjusted_confidence = new_analysis.get('confidence', 0.0) + confidence_adjustments['overall_adjustment']
    adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))
    
    print(f"📊 Confidence Analysis for Similar Content:")
    print(f"   Original Confidence: {new_analysis.get('confidence', 0.0):.2f}")
    print(f"   Adjustments: {confidence_adjustments}")
    print(f"   Adjusted Confidence: {adjusted_confidence:.2f}")
    print()
    
    # Get pattern-based suggestions
    suggestions = pattern_learner.get_suggested_improvements(new_analysis)
    print(f"💡 Pattern-Based Suggestions: {len(suggestions)} found")
    for suggestion in suggestions:
        print(f"   - {suggestion['type']}: {suggestion['suggestion']}")
        print(f"     Confidence: {suggestion['confidence']:.2f} | {suggestion['reasoning']}")
    print()
    
    # =================================
    # Demo 3: Learning Statistics and Insights
    # =================================
    print("📈 DEMO 3: Learning Statistics & Insights")
    print("-" * 50)
    
    # Add more feedback to build patterns
    additional_feedback = [
        UserFeedback("moved_file", "1 - Notes", "5 - Resources", "note2", -0.05, {"domain": "azure"}),
        UserFeedback("changed_tags", '["terraform"]', '["terraform", "devops"]', "note3", 0.0, {}),
        UserFeedback("moved_file", "2 - MOCs", "1 - Notes", "note4", -0.1, {"content_type": "note"}),
    ]
    
    for feedback in additional_feedback:
        pattern_learner.learn_from_feedback(feedback)
    
    # Get learning statistics
    learning_stats = pattern_learner.get_learning_stats()
    print(f"🧠 Learning Statistics:")
    print(f"   Total Patterns: {learning_stats['total_patterns']}")
    print(f"   Average Success Rate: {learning_stats['avg_success_rate']:.2f}")
    print(f"   Recent Feedback Count: {learning_stats['recent_feedback_count']}")
    print()
    
    print(f"📊 Patterns by Type:")
    for pattern_type, stats in learning_stats['by_type'].items():
        print(f"   - {pattern_type}: {stats['count']} patterns, {stats['avg_success_rate']:.2f} avg success")
    print()
    
    # Current confidence thresholds
    thresholds = pattern_learner.get_current_thresholds()
    print(f"🎯 Current Confidence Thresholds:")
    for threshold_name, value in thresholds.items():
        print(f"   - {threshold_name}: {value:.2f}")
    print()
    
    # =================================
    # Demo 4: Session Statistics and Patterns
    # =================================
    print("📊 DEMO 4: Session Statistics & Cross-Session Patterns")
    print("-" * 50)
    
    # End sessions
    session1_summary = session_manager.end_session(session1_id)
    session2_summary = session_manager.end_session(session2_id)
    
    print(f"📋 Session 1 Summary:")
    print(f"   Duration: {session1_summary['duration_minutes']:.1f} minutes")
    print(f"   Topics: {session1_summary['topics_covered']}")
    print(f"   Domains: {session1_summary['domains_explored']}")
    print(f"   Insights: {session1_summary['insights_captured']}")
    print()
    
    print(f"📋 Session 2 Summary:")
    print(f"   Duration: {session2_summary['duration_minutes']:.1f} minutes") 
    print(f"   Topics: {session2_summary['topics_covered']}")
    print(f"   Domains: {session2_summary['domains_explored']}")
    print(f"   Insights: {session2_summary['insights_captured']}")
    print()
    
    # Get session statistics
    session_stats = session_manager.get_session_statistics(days=1)
    print(f"📈 Session Statistics:")
    print(f"   Total Sessions: {session_stats.get('total_sessions', 0)}")
    print(f"   Average Duration: {session_stats.get('avg_duration', 0):.1f} minutes")
    print(f"   Total Insights: {session_stats.get('total_insights', 0)}")
    print(f"   Total Notes: {session_stats.get('total_notes', 0)}")
    print()
    
    if session_stats.get('top_topics'):
        print(f"🔥 Top Topics:")
        for topic in session_stats['top_topics'][:5]:
            print(f"   - {topic['topic']}: {topic['frequency']} times")
    print()
    
    if session_stats.get('top_domains'):
        print(f"🎯 Top Domains:")
        for domain in session_stats['top_domains'][:5]:
            print(f"   - {domain['domain']}: {domain['frequency']} times")
    print()
    
    # =================================
    # Summary
    # =================================
    print("🏆 PHASE 2 DEMO COMPLETE")
    print("=" * 60)
    print("✅ Session Management: Cross-conversation context tracking")
    print("✅ Pattern Learning: AI learns from user corrections")
    print("✅ Improved Confidence: Adjusts based on learned patterns")
    print("✅ Cross-Session Connections: Finds related conversations")
    print("✅ Learning Statistics: Transparent AI improvement tracking")
    print()
    print("🎯 Key Benefits:")
    print("  • AI gets smarter with every correction")
    print("  • Context preserved across conversations")
    print("  • Confidence scores improve over time")
    print("  • Related topics automatically connected")
    print("  • Complete transparency in AI learning")
    print()
    print("Ready for Phase 3: Complete Inbox Automation!")

if __name__ == "__main__":
    asyncio.run(demo_phase2_features())
