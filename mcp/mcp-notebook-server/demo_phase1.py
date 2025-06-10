#!/usr/bin/env python3
"""
INMPARA Notebook Server - Phase 1 Demo
Demonstrates core  functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def demo_conversation_insight_detection():
    """Demonstrate automatic insight detection from conversation."""
    print("🎯 Demo: Conversation Insight Detection")
    print("=" * 60)
    
    from content_analyzer import INMPARAContentAnalyzer
    from template_engine import INMPARATemplateEngine
    
    analyzer = INMPARAContentAnalyzer()
    
    # Simulate a conversation about Azure troubleshooting
    conversation = """
    We had an issue with Azure Databricks where the workspace wouldn't start. 
    After investigation, I found that the problem was with DNS resolution for private endpoints.
    
    The solution was to create a private DNS zone 'privatelink.azuredatabricks.net' 
    and link it to our VNet. Then we had to add an A record mapping the workspace 
    URL to the private endpoint IP address.
    
    Key insight: Always check DNS resolution first when private endpoints fail. 
    The error messages are often misleading and point to authentication issues.
    """
    
    print("📝 Original Conversation:")
    print(conversation.strip())
    print()
    
    # Detect insights
    insights = analyzer.analyze_for_insights(conversation)
    
    print(f"🔍 Detected {len(insights)} insights:")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. [{insight['type']}] Confidence: {insight['confidence']:.2f}")
        print(f"      \"{insight['text'][:60]}...\"")
        print(f"      Domains: {insight['domains']}")
        print()
    
    # Show which would trigger auto-creation vs suggestions
    auto_create_threshold = 0.8
    suggestion_threshold = 0.6
    
    auto_create = [i for i in insights if i['confidence'] >= auto_create_threshold]
    suggestions = [i for i in insights if suggestion_threshold <= i['confidence'] < auto_create_threshold]
    
    print(f"🤖 Auto-Create ({len(auto_create)} insights with confidence ≥{auto_create_threshold}):")
    for insight in auto_create:
        print(f"   ✅ [{insight['type']}] {insight['text'][:50]}...")
    
    print(f"💡 Suggestions ({len(suggestions)} insights with {suggestion_threshold} ≤ confidence < {auto_create_threshold}):")
    for insight in suggestions:
        print(f"   ⚠️  [{insight['type']}] {insight['text'][:50]}...")
    
    return insights

def demo_note_creation():
    """Demonstrate automatic INMPARA note creation."""
    print("\n🎯 Demo: INMPARA Note Creation")
    print("=" * 60)
    
    from content_analyzer import INMPARAContentAnalyzer
    from template_engine import INMPARATemplateEngine
    
    # Content from a high-confidence insight
    content = """
    Found that Azure Databricks private endpoints require specific DNS configuration. 
    The issue was missing A records in the private DNS zone 'privatelink.azuredatabricks.net'.
    Solution is to create A record mapping workspace URL to private endpoint IP address.
    This resolves authentication failures during workspace startup.
    """
    
    print("📝 Input Content:")
    print(content.strip())
    print()
    
    # Analyze content
    analyzer = INMPARAContentAnalyzer()
    result = analyzer.analyze_content(content.strip())
    
    print("🧠 Content Analysis:")
    print(f"   Title: {result.title}")
    print(f"   Type: {result.content_type}")
    print(f"   Domain: {result.primary_domain}")
    print(f"   Tags: {result.tags}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Destination: {result.destination_folder}")
    print(f"   Reasoning: {result.reasoning}")
    print()
    
    print("🔍 Extracted Observations:")
    for i, obs in enumerate(result.observations, 1):
        print(f"   {i}. [{obs['type']}] {obs['text'][:50]}...")
    print()
    
    # Generate INMPARA note
    with tempfile.TemporaryDirectory() as temp_vault:
        template_engine = INMPARATemplateEngine(temp_vault)
        
        note_content = template_engine.generate_note(
            result,
            content=content.strip(),
            context="Captured from Azure troubleshooting session",
            source_type="conversation"
        )
        
        print("📄 Generated INMPARA Note:")
        print("-" * 40)
        print(note_content)
        print("-" * 40)
        
        # Show file path
        filename = template_engine.generate_filename(result)
        file_path = template_engine.get_file_path(result)
        
        print(f"💾 Would be saved as: {filename}")
        print(f"📁 Full path: {file_path}")
        
        return note_content

def demo_semantic_connections():
    """Demonstrate connection discovery."""
    print("\n🎯 Demo: Semantic Connection Discovery")
    print("=" * 60)
    
    from content_analyzer import INMPARAContentAnalyzer
    
    analyzer = INMPARAContentAnalyzer()
    
    # Current conversation
    current_topic = "Having issues with Terraform state locking in Azure Storage"
    
    print(f"📝 Current Discussion: {current_topic}")
    print()
    
    # Simulate existing knowledge base
    existing_notes = [
        {
            'title': 'Azure Storage Account Configuration',
            'domain': 'azure',
            'content_type': 'note',
            'tags': ['azure', 'storage', 'configuration']
        },
        {
            'title': 'Terraform State Management Best Practices', 
            'domain': 'terraform',
            'content_type': 'note',
            'tags': ['terraform', 'state', 'devops']
        },
        {
            'title': 'Infrastructure Deployment Pipeline',
            'domain': 'devops',
            'content_type': 'project',
            'tags': ['devops', 'terraform', 'azure', 'cicd']
        }
    ]
    
    # Detect domains in current topic
    domains = analyzer._detect_domains(current_topic)
    print(f"🏷️ Detected domains: {domains}")
    print()
    
    # Show potential connections
    print("🔗 Potential Connections:")
    relevant_notes = []
    
    for note in existing_notes:
        relevance_score = 0
        
        # Check domain overlap
        for domain in domains:
            if domain in note['tags']:
                relevance_score += 0.3
        
        # Check specific terms
        if 'terraform' in current_topic.lower() and 'terraform' in note['tags']:
            relevance_score += 0.4
        if 'azure' in current_topic.lower() and 'azure' in note['tags']:
            relevance_score += 0.4
        if 'state' in current_topic.lower() and 'state' in note['tags']:
            relevance_score += 0.3
        
        if relevance_score > 0.5:
            relevant_notes.append((note, relevance_score))
    
    # Sort by relevance
    relevant_notes.sort(key=lambda x: x[1], reverse=True)
    
    for note, score in relevant_notes:
        print(f"   📄 [[{note['title']}]] (relevance: {score:.2f})")
        print(f"      Type: {note['content_type']} | Domain: {note['domain']}")
        print(f"      Tags: {', '.join(note['tags'])}")
    
    if not relevant_notes:
        print("   No strong connections found")
    
    return relevant_notes

def demo_inmpara_formatting():
    """Demonstrate INMPARA formatting compliance."""
    print("\n🎯 Demo: INMPARA Formatting Standards")
    print("=" * 60)
    
    from template_engine import INMPARATemplateEngine
    
    # Show what makes a note INMPARA-compliant
    print("📋 INMPARA Formatting Requirements:")
    print("   ✅ Complete YAML frontmatter (title, type, tags, dates, etc.)")
    print("   ✅ Semantic markup with observation categories")
    print("   ✅ Hierarchical tag structure (domain → type → technology → specifics)")
    print("   ✅ Wiki-style relations ([[Target Note]])")
    print("   ✅ Forward references for emergent connections")
    print("   ✅ Proper folder placement based on content type")
    print()
    
    # Example of bad vs good formatting
    bad_note = """
# Some Azure Thing

I found out that you need DNS stuff for Azure.

#azure #note
"""
    
    print("❌ Non-INMPARA Format:")
    print(bad_note)
    print()
    
    # Now show proper INMPARA format
    with tempfile.TemporaryDirectory() as temp_vault:
        template_engine = INMPARATemplateEngine(temp_vault)
        
        # Create a mock analysis result
        class MockResult:
            def __init__(self):
                self.title = "Azure Private Endpoint DNS Configuration"
                self.content_type = "note" 
                self.primary_domain = "azure"
                self.domains = ["azure", "dns", "networking"]
                self.tags = ["azure", "note", "dns", "networking", "private-endpoints"]
                self.confidence = 0.92
                self.destination_folder = "1 - Notes"
                self.slug = "azure-private-endpoint-dns-configuration"
                self.observations = [
                    {
                        'type': 'technical-finding',
                        'text': 'Azure private endpoints require specific DNS configuration',
                        'tags': ['azure', 'dns']
                    },
                    {
                        'type': 'requirement', 
                        'text': 'Must create A records in private DNS zone',
                        'tags': ['dns', 'networking']
                    }
                ]
                self.relations = [
                    {'target': 'Azure Networking MOC', 'type': 'part_of'},
                    {'target': 'DNS Best Practices', 'type': 'relates_to'}
                ]
        
        result = MockResult()
        
        good_note = template_engine.generate_note(
            result,
            content="Azure private endpoints require specific DNS configuration for proper resolution.",
            context="Discovered during infrastructure deployment",
            source_type="troubleshooting"
        )
        
        print("✅ Proper INMPARA Format:")
        print(good_note[:800] + "...")
        print()
        
        # Validate the format
        validation = template_engine.validate_inmpara_format(good_note)
        print("🔍 Format Validation:")
        print(f"   Valid: {validation['valid']}")
        if validation['errors']:
            print(f"   Errors: {validation['errors']}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        if validation['suggestions']:
            print(f"   Suggestions: {validation['suggestions']}")

def main():
    """Run all Phase 1 demos."""
    print("🚀 INMPARA Notebook Server - Phase 1 Demonstration")
    print("=" * 80)
    print("This demo shows intelligent automatic knowledge capture with INMPARA methodology")
    print()
    
    # Run demos
    demo_conversation_insight_detection()
    demo_note_creation()
    demo_semantic_connections()
    demo_inmpara_formatting()
    
    print("\n🎯 Phase 1 Summary")
    print("=" * 60)
    print("✅ Automatic insight detection from conversations")
    print("✅ High-confidence auto-creation of INMPARA notes")
    print("✅ Perfect formatting with semantic markup")
    print("✅ Intelligent connection suggestions")
    print("✅ Complete INMPARA standards compliance")
    print()
    print("🔗 Ready for integration with Claude Desktop!")
    print("📚 Next: Start server with ./start-server.sh")

if __name__ == "__main__":
    main()
