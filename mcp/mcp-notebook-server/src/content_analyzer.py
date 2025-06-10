"""
INMPARA Notebook Server - Content Analyzer
Analyzes content to classify type, extract domains, and determine filing decisions.
"""

import re
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContentAnalysisResult:
    """Result of content analysis with all metadata."""
    
    def __init__(self):
        self.content_type: str = ""
        self.primary_domain: str = ""
        self.domains: List[str] = []
        self.tags: List[str] = []
        self.title: str = ""
        self.slug: str = ""
        self.observations: List[Dict[str, Any]] = []
        self.relations: List[Dict[str, Any]] = []
        self.confidence: float = 0.0
        self.destination_folder: str = ""
        self.reasoning: str = ""
        self.semantic_markup: List[str] = []
        self.word_count: int = 0
        self.character_count: int = 0
        self.content_hash: str = ""


class INMPARAContentAnalyzer:
    """Analyzes content for INMPARA classification and filing."""
    
    def __init__(self):
        # Domain detection patterns
        self.domain_patterns = {
            'azure': [
                r'\bazure\b', r'\baz\b', r'\barm\b', r'\bresource group\b',
                r'\bsubscription\b', r'\btenant\b', r'\bactive directory\b',
                r'\bdatabricks\b', r'\bkey vault\b', r'\bstorage account\b',
                r'\bvirtual network\b', r'\bprivate endpoint\b'
            ],
            'terraform': [
                r'\bterraform\b', r'\btf\b', r'\bhcl\b', r'\bstate\b',
                r'\bprovider\b', r'\bresource\b', r'\bmodule\b', r'\bvariable\b',
                r'\boutput\b', r'\bdata\b', r'\blocals\b'
            ],
            'dns': [
                r'\bdns\b', r'\bdomain\b', r'\bzone\b', r'\brecord\b',
                r'\bnameserver\b', r'\bresolution\b', r'\ba record\b',
                r'\bcname\b', r'\bmx record\b', r'\bttl\b'
            ],
            'networking': [
                r'\bnetwork\b', r'\bsubnet\b', r'\brouting\b', r'\bfirewall\b',
                r'\bvpn\b', r'\bvnet\b', r'\bnsg\b', r'\bload balancer\b',
                r'\bproxy\b', r'\bssl\b', r'\btls\b'
            ],
            'devops': [
                r'\bci/cd\b', r'\bpipeline\b', r'\bdeployment\b', r'\bbuild\b',
                r'\brelease\b', r'\bartifact\b', r'\brepository\b', r'\bgit\b',
                r'\bdocker\b', r'\bkubernetes\b', r'\bhelm\b'
            ],
            'monitoring': [
                r'\bmonitoring\b', r'\balert\b', r'\bmetric\b', r'\blog\b',
                r'\bdashboard\b', r'\btelemetry\b', r'\bobservability\b',
                r'\bprometheus\b', r'\bgrafana\b'
            ],
            'security': [
                r'\bsecurity\b', r'\bauthentication\b', r'\bauthorization\b',
                r'\bencryption\b', r'\bcertificate\b', r'\bidentity\b',
                r'\bcompliance\b', r'\brbac\b'
            ]
        }
        
        # Content type indicators
        self.content_type_patterns = {
            'note': [
                r'\bfound that\b', r'\bdiscovered\b', r'\blearned\b',
                r'\binsight\b', r'\bobservation\b', r'\bkey finding\b',
                r'\bthe issue was\b', r'\bsolution is\b'
            ],
            'moc': [
                r'\boverview\b', r'\bmap of\b', r'\bcollection\b',
                r'\bcluster\b', r'\bindex\b', r'\btable of contents\b',
                r'\bnavigation\b'
            ],
            'project': [
                r'\bproject\b', r'\binitiative\b', r'\bmilestone\b',
                r'\btask\b', r'\bdeliverable\b', r'\bobjective\b',
                r'\bgoal\b', r'\btimeline\b'
            ],
            'area': [
                r'\barea\b', r'\bresponsibility\b', r'\bfunction\b',
                r'\brole\b', r'\bteam\b', r'\bdepartment\b',
                r'\bprocess\b', r'\bstandard\b'
            ],
            'resource': [
                r'\breference\b', r'\bdocumentation\b', r'\bguide\b',
                r'\btutorial\b', r'\bmanual\b', r'\blink\b',
                r'\barticle\b', r'\bbook\b', r'\btools\b'
            ]
        }
        
        # Observation patterns for semantic markup
        self.observation_patterns = {
            'technical-finding': [
                r'\bfound that\b', r'\bdiscovered\b', r'\brequires\b',
                r'\bmust have\b', r'\bneeds\b', r'\bspecific.*config\b'
            ],
            'insight': [
                r'\binsight\b', r'\bunderstood\b', r'\brealized\b',
                r'\bconnection\b', r'\bpattern\b', r'\brelationship\b'
            ],
            'issue': [
                r'\bproblem\b', r'\bissue\b', r'\berror\b', r'\bfailed\b',
                r'\bbug\b', r'\btrouble\b', r'\bchallenge\b'
            ],
            'requirement': [
                r'\brequired\b', r'\bmandatory\b', r'\bmust\b',
                r'\bnecessary\b', r'\bneeded\b', r'\bcrucial\b'
            ],
            'pattern': [
                r'\bpattern\b', r'\brecurring\b', r'\bconsistent\b',
                r'\bbehavior\b', r'\btrend\b', r'\bcommon\b'
            ]
        }
        
        # Relation extraction patterns
        self.relation_patterns = {
            'relates_to': [
                r'\brelated to\b', r'\bconnected to\b', r'\bassociated with\b',
                r'\bsimilar to\b', r'\bcompare to\b'
            ],
            'part_of': [
                r'\bpart of\b', r'\bcomponent of\b', r'\belement of\b',
                r'\bwithin\b', r'\binside\b'
            ],
            'enables': [
                r'\benables\b', r'\ballows\b', r'\bfacilitates\b',
                r'\bmakes possible\b', r'\bsupports\b'
            ],
            'requires': [
                r'\brequires\b', r'\bneeds\b', r'\bdepends on\b',
                r'\brely on\b', r'\bprerequisite\b'
            ],
            'solves': [
                r'\bsolves\b', r'\bfixes\b', r'\bresolves\b',
                r'\baddresses\b', r'\bhandles\b'
            ]
        }
    
    def analyze_content(self, content: str, context: Dict[str, Any] = None) -> ContentAnalysisResult:
        """Perform complete content analysis."""
        result = ContentAnalysisResult()
        
        # Basic content metrics
        result.word_count = len(content.split())
        result.character_count = len(content)
        result.content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract title
        result.title = self._extract_title(content)
        result.slug = self._generate_slug(result.title)
        
        # Classify content type
        result.content_type = self._classify_content_type(content)
        
        # Detect domains
        result.domains = self._detect_domains(content)
        result.primary_domain = result.domains[0] if result.domains else 'general'
        
        # Extract observations
        result.observations = self._extract_observations(content)
        result.semantic_markup = [obs['type'] for obs in result.observations]
        
        # Extract relations
        result.relations = self._extract_relations(content)
        
        # Generate tags
        result.tags = self._generate_tags(result)
        
        # Calculate confidence and determine destination
        result.confidence = self._calculate_confidence(result, content)
        result.destination_folder = self._determine_destination(result)
        result.reasoning = self._generate_reasoning(result)
        
        logger.info(f"Analyzed content: {result.title} -> {result.destination_folder} (confidence: {result.confidence:.2f})")
        return result
    
    def _extract_title(self, content: str) -> str:
        """Extract or generate title from content."""
        lines = content.strip().split('\n')
        
        # Look for markdown headers
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                title = re.sub(r'^#+\s*', '', line).strip()
                if title:
                    return title
        
        # Use first meaningful sentence
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            title = sentences[0][:80]  # Limit length
            return title
        
        return "Untitled Note"
    
    def _generate_slug(self, title: str) -> str:
        """Generate kebab-case slug from title."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')
    
    def _classify_content_type(self, content: str) -> str:
        """Classify content into INMPARA type."""
        content_lower = content.lower()
        type_scores = {}
        
        for content_type, patterns in self.content_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower, re.IGNORECASE))
                score += matches
            type_scores[content_type] = score
        
        # Additional heuristics
        word_count = len(content.split())
        
        # Long content with many references suggests MOC
        if word_count > 500 and content.count('[[') > 5:
            type_scores['moc'] = type_scores.get('moc', 0) + 3
        
        # Short, specific content suggests note
        if word_count < 300 and any(keyword in content_lower for keyword in ['found', 'discovered', 'issue', 'solution']):
            type_scores['note'] = type_scores.get('note', 0) + 2
        
        # Project indicators
        if any(keyword in content_lower for keyword in ['project', 'milestone', 'deliverable', 'timeline']):
            type_scores['project'] = type_scores.get('project', 0) + 2
        
        # Return highest scoring type, default to note
        if type_scores:
            return max(type_scores, key=type_scores.get)
        return 'note'
    
    def _detect_domains(self, content: str) -> List[str]:
        """Detect technical domains in content."""
        content_lower = content.lower()
        domain_scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower, re.IGNORECASE))
                score += matches
            if score > 0:
                domain_scores[domain] = score
        
        # Sort by score and return top domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        return [domain for domain, score in sorted_domains if score > 0]
    
    def _extract_observations(self, content: str) -> List[Dict[str, Any]]:
        """Extract semantic observations from content."""
        observations = []
        content_lower = content.lower()
        
        for obs_type, patterns in self.observation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    # Extract surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    # Extract relevant tags from context
                    context_domains = self._detect_domains(context)
                    
                    observations.append({
                        'type': obs_type,
                        'text': context,
                        'position': match.start(),
                        'confidence': 0.8,  # Base confidence
                        'tags': context_domains[:2]  # Top 2 relevant domains
                    })
        
        # Remove duplicates and sort by position
        unique_observations = []
        seen_contexts = set()
        
        for obs in sorted(observations, key=lambda x: x['position']):
            context_key = obs['text'][:50]  # Use first 50 chars as key
            if context_key not in seen_contexts:
                seen_contexts.add(context_key)
                unique_observations.append(obs)
        
        return unique_observations[:5]  # Limit to 5 observations
    
    def _extract_relations(self, content: str) -> List[Dict[str, Any]]:
        """Extract potential relations from content."""
        relations = []
        content_lower = content.lower()
        
        # Look for explicit wiki-style links
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in wiki_links:
            relations.append({
                'target': link.strip(),
                'type': 'relates_to',
                'confidence': 0.9,
                'context': f"Explicit link to {link}"
            })
        
        # Look for relation patterns
        for rel_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    # Try to extract target from surrounding text
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 30)
                    context = content[start:end].strip()
                    
                    relations.append({
                        'target': 'Unknown',  # Would need more sophisticated extraction
                        'type': rel_type,
                        'confidence': 0.6,
                        'context': context
                    })
        
        return relations[:3]  # Limit to 3 relations
    
    def _generate_tags(self, result: ContentAnalysisResult) -> List[str]:
        """Generate hierarchical tags for content."""
        tags = []
        
        # 1. Primary domain (required)
        if result.primary_domain:
            tags.append(result.primary_domain)
        
        # 2. Content type (required)
        tags.append(result.content_type)
        
        # 3. Additional domains (up to 2)
        for domain in result.domains[1:3]:
            if domain not in tags:
                tags.append(domain)
        
        # 4. Technology-specific tags based on observations
        tech_tags = set()
        for obs in result.observations:
            tech_tags.update(obs.get('tags', []))
        
        # Add tech tags (up to 2 more)
        for tag in list(tech_tags)[:2]:
            if tag not in tags:
                tags.append(tag)
        
        # Ensure we have 3-6 tags total
        if len(tags) < 3:
            tags.append('general')
        
        return tags[:6]
    
    def _calculate_confidence(self, result: ContentAnalysisResult, content: str) -> float:
        """Calculate confidence score for classification."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on clear indicators
        if result.primary_domain and result.primary_domain != 'general':
            confidence += 0.2
        
        if len(result.observations) > 0:
            confidence += 0.1 * len(result.observations)
        
        if result.content_type != 'note':  # Non-default classification
            confidence += 0.1
        
        if len(result.domains) > 1:  # Multiple domain matches
            confidence += 0.1
        
        # Word count confidence
        if 50 <= result.word_count <= 1000:  # Good length for atomic notes
            confidence += 0.1
        
        # Structured content indicators
        if '##' in content or '- [' in content:  # Headers or lists
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_destination(self, result: ContentAnalysisResult) -> str:
        """Determine INMPARA folder destination."""
        type_mapping = {
            'note': '1 - Notes',
            'moc': '2 - MOCs',
            'project': '3 - Projects',
            'area': '4 - Areas',
            'resource': '5 - Resources'
        }
        
        return type_mapping.get(result.content_type, '1 - Notes')
    
    def _generate_reasoning(self, result: ContentAnalysisResult) -> str:
        """Generate human-readable reasoning for classification."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Classified as {result.content_type}")
        
        if result.primary_domain:
            reasoning_parts.append(f"primary domain: {result.primary_domain}")
        
        if result.observations:
            obs_types = [obs['type'] for obs in result.observations]
            reasoning_parts.append(f"contains: {', '.join(set(obs_types))}")
        
        reasoning_parts.append(f"confidence: {result.confidence:.2f}")
        
        return " | ".join(reasoning_parts)
    
    def analyze_for_insights(self, conversation_text: str) -> List[Dict[str, Any]]:
        """Analyze conversation text for potential insights."""
        insights = []
        
        # Split into sentences for analysis
        sentences = re.split(r'[.!?]+', conversation_text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            insight_data = self._classify_insight(sentence)
            if insight_data['confidence'] > 0.6:
                # Add context from surrounding sentences
                start_idx = max(0, i - 1)
                end_idx = min(len(sentences), i + 2)
                context = '. '.join(sentences[start_idx:end_idx]).strip()
                
                insight_data['context'] = context
                insight_data['position'] = i
                insights.append(insight_data)
        
        # Remove duplicates and sort by confidence
        unique_insights = []
        seen_texts = set()
        
        for insight in sorted(insights, key=lambda x: x['confidence'], reverse=True):
            text_key = insight['text'][:50]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_insights.append(insight)
        
        return unique_insights[:3]  # Top 3 insights
    
    def _classify_insight(self, sentence: str) -> Dict[str, Any]:
        """Classify a sentence as a potential insight."""
        sentence_lower = sentence.lower()
        
        # Insight trigger patterns with confidence scores
        insight_triggers = {
            'technical-finding': {
                'patterns': [
                    r'\bfound that\b', r'\bdiscovered\b', r'\bturns out\b',
                    r'\brequires\b', r'\bmust have\b', r'\bneeds\b'
                ],
                'base_confidence': 0.8
            },
            'insight': {
                'patterns': [
                    r'\blearned that\b', r'\bkey insight\b', r'\brealized\b',
                    r'\bunderstood\b', r'\bimportant to note\b'
                ],
                'base_confidence': 0.75
            },
            'issue': {
                'patterns': [
                    r'\bthe issue was\b', r'\bproblem is\b', r'\berror\b',
                    r'\bfailed because\b', r'\btrouble with\b'
                ],
                'base_confidence': 0.85
            },
            'solution': {
                'patterns': [
                    r'\bsolution is\b', r'\bfix was\b', r'\bworkaround\b',
                    r'\bresolved by\b', r'\bsolves\b'
                ],
                'base_confidence': 0.9
            }
        }
        
        best_match = {
            'type': 'general',
            'text': sentence,
            'confidence': 0.0,
            'domains': self._detect_domains(sentence)
        }
        
        for insight_type, config in insight_triggers.items():
            for pattern in config['patterns']:
                if re.search(pattern, sentence_lower):
                    confidence = config['base_confidence']
                    
                    # Boost confidence for technical content
                    if best_match['domains']:
                        confidence += 0.1
                    
                    # Boost for specific technical terms
                    tech_terms = ['azure', 'terraform', 'dns', 'network', 'config']
                    if any(term in sentence_lower for term in tech_terms):
                        confidence += 0.05
                    
                    if confidence > best_match['confidence']:
                        best_match.update({
                            'type': insight_type,
                            'confidence': min(confidence, 1.0)
                        })
        
        return best_match
