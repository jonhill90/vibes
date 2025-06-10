"""
Monitors conversations for insights and automatically creates INMPARA notes.
 automatic conversation insight detection and note creation.
"""

import asyncio
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import logging

from .content_analyzer import INMPARAContentAnalyzer, ContentAnalysisResult
from .template_engine import INMPARATemplateEngine
from .database.database import INMPARADatabase
from .database.vector_search import VectorSearchEngine

logger = logging.getLogger(__name__)


class ConversationInsight:
    """Represents a detected conversation insight."""
    
    def __init__(self, text: str, insight_type: str, confidence: float, 
                 domains: List[str], context: str = "", session_id: str = ""):
        self.text = text
        self.insight_type = insight_type
        self.confidence = confidence
        self.domains = domains
        self.context = context
        self.session_id = session_id
        self.timestamp = datetime.now()
        self.note_id: Optional[str] = None
        self.processed = False


class ConversationMonitor:
    """Monitors conversations for insights and automatically creates INMPARA notes."""
    
    def __init__(self, database: INMPARADatabase, vector_search: VectorSearchEngine,
                 template_engine: INMPARATemplateEngine, vault_path: str):
        self.database = database
        self.vector_search = vector_search
        self.template_engine = template_engine
        self.vault_path = vault_path
        self.content_analyzer = INMPARAContentAnalyzer()
        
        # Configuration
        self.auto_create_threshold = 0.8
        self.suggestion_threshold = 0.6
        self.min_insight_length = 20
        
        # Session tracking
        self.current_session_id = str(uuid.uuid4())
        self.session_context = []
        self.recent_insights = []
        
        # Callbacks for notifications
        self.on_insight_detected: Optional[Callable] = None
        self.on_note_created: Optional[Callable] = None
        self.on_suggestion_generated: Optional[Callable] = None
        
        # Insight detection patterns (enhanced from content analyzer)
        self.insight_patterns = {
            'technical-finding': [
                r'(?i)(found that|discovered that|turns out|learned that)',
                r'(?i)(azure .+ (requires|needs)|terraform .+ (requires|needs))',
                r'(?i)(the issue was|problem is|error occurs when)',
                r'(?i)(must have|crucial to|essential to|required to)',
                r'(?i)(configuration needs|setup requires|implementation needs)'
            ],
            'solution': [
                r'(?i)(solution is|fix was|workaround is|resolved by)',
                r'(?i)(solved by|fixed by|addressed by|handled by)',
                r'(?i)(way to fix|how to solve|approach is to)',
                r'(?i)(can be resolved|can fix this|solves the problem)'
            ],
            'insight': [
                r'(?i)(key insight|important to note|realized that)',
                r'(?i)(understanding is|pattern is|principle is)',
                r'(?i)(what I learned|takeaway is|conclusion is)',
                r'(?i)(interesting that|notable that|worth noting)'
            ],
            'requirement': [
                r'(?i)(requirement is|must be|has to be|needs to be)',
                r'(?i)(required for|necessary for|essential for)',
                r'(?i)(prerequisite|dependency|constraint)',
                r'(?i)(compliance requires|security requires|policy requires)'
            ],
            'pattern': [
                r'(?i)(pattern is|consistently|always happens|recurring)',
                r'(?i)(every time|whenever|typical behavior|common issue)',
                r'(?i)(trend is|tendency is|usually|generally)',
                r'(?i)(best practice|standard approach|recommended way)'
            ]
        }
        
        logger.info("Conversation monitor initialized")
    
    def start_new_session(self) -> str:
        """Start a new conversation session."""
        self.current_session_id = str(uuid.uuid4())
        self.session_context = []
        self.recent_insights = []
        logger.info(f"Started new conversation session: {self.current_session_id}")
        return self.current_session_id
    
    async def process_message(self, message: str, user_id: str = "user") -> List[Dict[str, Any]]:
        """Process a conversation message for insights."""
        # Add to session context
        self.session_context.append({
            'timestamp': datetime.now(),
            'user_id': user_id,
            'message': message
        })
        
        # Keep context manageable (last 10 messages)
        if len(self.session_context) > 10:
            self.session_context = self.session_context[-10:]
        
        # Detect insights in the message
        insights = await self._detect_insights(message)
        
        # Process each insight
        responses = []
        for insight in insights:
            response = await self._process_insight(insight)
            if response:
                responses.append(response)
        
        # Check for connection opportunities
        connections = await self._suggest_connections(message)
        if connections:
            responses.append({
                'type': 'connections',
                'suggestions': connections
            })
        
        return responses
    
    async def _detect_insights(self, message: str) -> List[ConversationInsight]:
        """Detect potential insights in a conversation message."""
        insights = []
        
        # Split message into sentences for analysis
        sentences = re.split(r'[.!?]+', message)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < self.min_insight_length:
                continue
            
            # Check against insight patterns
            for insight_type, patterns in self.insight_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence):
                        # Calculate confidence
                        confidence = self._calculate_insight_confidence(sentence, insight_type)
                        
                        if confidence > self.suggestion_threshold:
                            # Detect domains
                            domains = self.content_analyzer._detect_domains(sentence)
                            
                            # Build context from surrounding sentences
                            context = self._build_context(sentence, message)
                            
                            insight = ConversationInsight(
                                text=sentence,
                                insight_type=insight_type,
                                confidence=confidence,
                                domains=domains,
                                context=context,
                                session_id=self.current_session_id
                            )
                            
                            insights.append(insight)
                            break  # Don't match multiple patterns for same sentence
        
        # Remove duplicates and sort by confidence
        unique_insights = self._deduplicate_insights(insights)
        return sorted(unique_insights, key=lambda x: x.confidence, reverse=True)
    
    def _calculate_insight_confidence(self, sentence: str, insight_type: str) -> float:
        """Calculate confidence score for an insight."""
        base_confidence = 0.6
        
        # Boost for technical terms
        technical_terms = [
            'azure', 'terraform', 'dns', 'network', 'config', 'setup',
            'deployment', 'infrastructure', 'security', 'authentication'
        ]
        
        tech_matches = sum(1 for term in technical_terms if term.lower() in sentence.lower())
        base_confidence += tech_matches * 0.05
        
        # Boost for specific insight types
        if insight_type == 'solution' and any(word in sentence.lower() for word in ['fix', 'solve', 'resolve']):
            base_confidence += 0.15
        
        if insight_type == 'technical-finding' and any(word in sentence.lower() for word in ['found', 'discovered', 'issue']):
            base_confidence += 0.1
        
        # Boost for longer, more detailed sentences
        if len(sentence.split()) > 10:
            base_confidence += 0.05
        
        # Boost if sentence contains specific details
        if re.search(r'\b\d+\b', sentence):  # Contains numbers
            base_confidence += 0.05
        
        if '"' in sentence or "'" in sentence:  # Contains quotes (specific config/commands)
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _build_context(self, sentence: str, full_message: str) -> str:
        """Build context around a sentence from the full message."""
        # Find sentence position in message
        sentence_pos = full_message.find(sentence)
        if sentence_pos == -1:
            return full_message[:200]  # Fallback to beginning of message
        
        # Extract context before and after
        start = max(0, sentence_pos - 100)
        end = min(len(full_message), sentence_pos + len(sentence) + 100)
        
        context = full_message[start:end].strip()
        return context
    
    def _deduplicate_insights(self, insights: List[ConversationInsight]) -> List[ConversationInsight]:
        """Remove duplicate insights based on text similarity."""
        unique_insights = []
        seen_texts = set()
        
        for insight in insights:
            # Use first 50 characters as deduplication key
            text_key = insight.text[:50].lower().strip()
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_insights.append(insight)
        
        return unique_insights
    
    async def _process_insight(self, insight: ConversationInsight) -> Optional[Dict[str, Any]]:
        """Process a detected insight - create note or suggestion."""
        
        # Store insight in database
        insight_data = {
            'session_id': insight.session_id,
            'insight_text': insight.text,
            'confidence': insight.confidence,
            'insight_type': insight.insight_type,
            'domains': insight.domains
        }
        
        insight_id = self.database.add_conversation_insight(insight_data)
        
        if insight.confidence >= self.auto_create_threshold:
            # High confidence - auto-create note
            return await self._auto_create_note(insight)
        
        elif insight.confidence >= self.suggestion_threshold:
            # Medium confidence - suggest note creation
            return await self._suggest_note_creation(insight)
        
        return None
    
    async def _auto_create_note(self, insight: ConversationInsight) -> Dict[str, Any]:
        """Automatically create a note from a high-confidence insight."""
        try:
            # Analyze the insight context for note creation
            analysis_result = self.content_analyzer.analyze_content(
                insight.context,
                context={'insight_type': insight.insight_type, 'domains': insight.domains}
            )
            
            # Override title to be more specific
            analysis_result.title = self._generate_insight_title(insight)
            analysis_result.slug = self.template_engine._generate_slug(analysis_result.title)
            
            # Generate the note content
            note_content = self.template_engine.generate_note(
                analysis_result,
                content=insight.context,
                context=f"Captured from conversation on {insight.timestamp.strftime('%Y-%m-%d')}",
                source_type="conversation"
            )
            
            # Save the note
            file_path = self.template_engine.get_file_path(analysis_result)
            
            # Create directories if needed
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            # Add to database
            note_data = {
                'title': analysis_result.title,
                'file_path': file_path,
                'content_type': analysis_result.content_type,
                'domain': analysis_result.primary_domain,
                'created_date': datetime.now().isoformat(),
                'modified_date': datetime.now().isoformat(),
                'confidence_score': analysis_result.confidence,
                'source_type': 'conversation',
                'word_count': analysis_result.word_count,
                'character_count': analysis_result.character_count,
                'content_hash': analysis_result.content_hash,
                'frontmatter': {
                    'title': analysis_result.title,
                    'type': analysis_result.content_type,
                    'tags': analysis_result.tags
                },
                'tags': [{'tag': tag, 'tag_type': 'auto'} for tag in analysis_result.tags],
                'relationships': []
            }
            
            note_id = self.database.add_note(note_data)
            
            # Add to vector search
            vector_data = note_data.copy()
            vector_data['id'] = note_id
            vector_data['content'] = insight.context
            self.vector_search.add_note(vector_data)
            
            # Update insight with note ID
            insight.note_id = note_id
            insight.processed = True
            
            # Log the action
            self.database.log_processing_action({
                'action': 'auto_create_note',
                'source_path': 'conversation',
                'destination_path': file_path,
                'confidence': insight.confidence,
                'reasoning': f"Auto-created from {insight.insight_type} with confidence {insight.confidence:.2f}"
            })
            
            logger.info(f"Auto-created note: {analysis_result.title}")
            
            # Notify callback if set
            if self.on_note_created:
                self.on_note_created(note_id, analysis_result.title, file_path)
            
            return {
                'type': 'note_created',
                'note_id': note_id,
                'title': analysis_result.title,
                'file_path': file_path,
                'confidence': insight.confidence,
                'insight_type': insight.insight_type,
                'message': f"📝 Auto-created note: **{analysis_result.title}**"
            }
            
        except Exception as e:
            logger.error(f"Error auto-creating note: {e}")
            return {
                'type': 'error',
                'message': f"Failed to create note: {str(e)}"
            }
    
    async def _suggest_note_creation(self, insight: ConversationInsight) -> Dict[str, Any]:
        """Suggest note creation for medium-confidence insights."""
        
        # Generate preview of what the note would look like
        preview_analysis = self.content_analyzer.analyze_content(insight.context)
        preview_title = self._generate_insight_title(insight)
        
        suggestion = {
            'type': 'note_suggestion',
            'insight_id': id(insight),  # Use object id as temporary reference
            'title': preview_title,
            'confidence': insight.confidence,
            'insight_type': insight.insight_type,
            'domains': insight.domains,
            'preview': {
                'content_type': preview_analysis.content_type,
                'destination': preview_analysis.destination_folder,
                'tags': preview_analysis.tags
            },
            'message': f"💡 **Suggestion**: Create note about {preview_title} (confidence: {insight.confidence:.0%})"
        }
        
        # Notify callback if set
        if self.on_suggestion_generated:
            self.on_suggestion_generated(suggestion)
        
        return suggestion
    
    def _generate_insight_title(self, insight: ConversationInsight) -> str:
        """Generate a meaningful title for an insight."""
        # Extract key terms from the insight text
        text = insight.text.lower()
        
        # Common title patterns based on insight type
        if insight.insight_type == 'technical-finding':
            if 'azure' in text:
                return f"Azure {insight.domains[0].title()} Configuration Finding"
            elif 'terraform' in text:
                return f"Terraform {insight.domains[0].title()} Implementation"
            else:
                return f"{insight.domains[0].title()} Technical Finding"
        
        elif insight.insight_type == 'solution':
            if 'dns' in text:
                return "DNS Resolution Solution"
            elif 'network' in text:
                return "Network Configuration Fix"
            else:
                return f"{insight.domains[0].title()} Solution"
        
        elif insight.insight_type == 'issue':
            return f"{insight.domains[0].title()} Issue Resolution"
        
        elif insight.insight_type == 'requirement':
            return f"{insight.domains[0].title()} Requirements"
        
        elif insight.insight_type == 'pattern':
            return f"{insight.domains[0].title()} Pattern"
        
        else:
            # Generic insight
            domain = insight.domains[0] if insight.domains else 'General'
            return f"{domain.title()} Insight"
    
    async def _suggest_connections(self, message: str) -> List[Dict[str, Any]]:
        """Suggest connections to existing notes based on current conversation."""
        
        # Detect domains in current message
        domains = self.content_analyzer._detect_domains(message)
        
        if not domains:
            return []
        
        # Search for related notes
        connections = self.vector_search.suggest_connections(
            message, 
            existing_note_domains=domains,
            limit=3,
            similarity_threshold=0.7
        )
        
        if not connections:
            return []
        
        # Format connection suggestions
        suggestions = []
        for conn in connections:
            suggestions.append({
                'title': conn['title'],
                'file_path': conn['file_path'],
                'similarity_score': conn['similarity_score'],
                'domain': conn['domain'],
                'content_type': conn['content_type']
            })
        
        return suggestions
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            'session_id': self.current_session_id,
            'message_count': len(self.session_context),
            'insights_detected': len(self.recent_insights),
            'notes_created': len([i for i in self.recent_insights if i.note_id]),
            'session_duration': (datetime.now() - self.session_context[0]['timestamp']).seconds if self.session_context else 0
        }
    
    def update_thresholds(self, auto_create_threshold: float = None, 
                         suggestion_threshold: float = None):
        """Update confidence thresholds based on user feedback."""
        if auto_create_threshold is not None:
            self.auto_create_threshold = auto_create_threshold
            logger.info(f"Updated auto-create threshold to {auto_create_threshold}")
        
        if suggestion_threshold is not None:
            self.suggestion_threshold = suggestion_threshold
            logger.info(f"Updated suggestion threshold to {suggestion_threshold}")
