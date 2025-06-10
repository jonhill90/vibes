"""
INMPARA Notebook Server - Template Engine
Generates INMPARA-compliant notes with proper frontmatter and structure.
"""

import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class INMPARATemplateEngine:
    """Generates INMPARA-formatted notes with correct templates and frontmatter."""
    
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.folder_mapping = {
            'note': '1 - Notes',
            'moc': '2 - MOCs',
            'project': '3 - Projects',
            'area': '4 - Areas',
            'resource': '5 - Resources',
            'archive': '6 - Archive'
        }
        
        # Observation templates for semantic markup
        self.observation_templates = {
            'technical-finding': "- [technical-finding] {text} #{tags}",
            'insight': "- [insight] {text} #{tags}",
            'pattern': "- [pattern] {text} #{tags}",
            'requirement': "- [requirement] {text} #{tags}",
            'issue': "- [issue] {text} #{tags}",
            'constraint': "- [constraint] {text} #{tags}",
            'solution': "- [solution] {text} #{tags}",
            'decision': "- [decision] {text} #{tags}",
            'idea': "- [idea] {text} #{tags}"
        }
    
    def generate_frontmatter(self, analysis_result, source_type: str = "auto") -> str:
        """Generate INMPARA-compliant frontmatter."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Build permalink
        stage_folder = self.folder_mapping.get(analysis_result.content_type, '1 - Notes')
        permalink = f"{stage_folder.lower().replace(' ', '-')}/{analysis_result.slug}"
        
        frontmatter = {
            'title': analysis_result.title,
            'type': analysis_result.content_type,
            'tags': analysis_result.tags,
            'created': timestamp,
            'updated': timestamp,
            'status': 'active',
            'stage': stage_folder.lower().replace(' ', '-'),
            'domain': analysis_result.primary_domain,
            'permalink': permalink
        }
        
        # Add source metadata for tracking
        if source_type:
            frontmatter['source'] = source_type
            frontmatter['confidence'] = round(analysis_result.confidence, 2)
        
        return yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    
    def generate_note(self, analysis_result, content: str, 
                     context: str = "", source_type: str = "auto") -> str:
        """Generate a complete INMPARA note."""
        
        frontmatter = self.generate_frontmatter(analysis_result, source_type)
        
        # Format observations
        observations_section = self._format_observations(analysis_result.observations)
        
        # Format relations
        relations_section = self._format_relations(analysis_result.relations)
        
        # Generate related knowledge section
        related_knowledge = self._generate_related_knowledge(analysis_result)
        
        # Generate tag string
        tag_string = " ".join(f"#{tag}" for tag in analysis_result.tags)
        
        # Build the complete note
        note_content = f"""---
{frontmatter}---

# {analysis_result.title}

## Content
{content.strip()}

{self._format_context_section(context)}

{observations_section}

{relations_section}

{related_knowledge}

## Tags
{tag_string}
"""
        
        return note_content
    
    def generate_moc(self, analysis_result, notes_cluster: List[Dict[str, Any]], 
                    overview: str = "") -> str:
        """Generate a Map of Content (MOC)."""
        
        frontmatter = self.generate_frontmatter(analysis_result, "auto")
        
        # Build knowledge clusters
        clusters_section = self._format_knowledge_clusters(notes_cluster)
        
        # Format observations for MOC
        observations_section = self._format_observations(analysis_result.observations)
        
        # Generate tag string
        tag_string = " ".join(f"#{tag}" for tag in analysis_result.tags)
        
        moc_content = f"""---
{frontmatter}---

# {analysis_result.title}

## Overview
{overview or "Knowledge cluster for " + analysis_result.primary_domain}

## Core Concepts
{self._format_core_concepts(notes_cluster)}

{clusters_section}

{observations_section}

## Relations
{self._format_relations(analysis_result.relations)}

## Emerging Patterns
{self._generate_emerging_patterns(analysis_result)}

## Potential Projects
{self._generate_potential_projects(analysis_result)}

## Tags
{tag_string}
"""
        
        return moc_content
    
    def _format_observations(self, observations: List[Dict[str, Any]]) -> str:
        """Format observations section with semantic markup."""
        if not observations:
            return "## Observations\n[No specific observations extracted]"
        
        formatted_observations = []
        for obs in observations:
            obs_type = obs.get('type', 'general')
            text = obs.get('text', '').strip()
            tags = obs.get('tags', [])
            
            # Clean up text for observation
            cleaned_text = self._clean_observation_text(text)
            tag_string = " ".join(f"#{tag}" for tag in tags[:2])  # Limit to 2 tags
            
            if obs_type in self.observation_templates:
                formatted_obs = self.observation_templates[obs_type].format(
                    text=cleaned_text,
                    tags=tag_string
                )
                formatted_observations.append(formatted_obs)
        
        return "## Observations\n" + "\n".join(formatted_observations)
    
    def _format_relations(self, relations: List[Dict[str, Any]]) -> str:
        """Format relations section."""
        if not relations:
            return "## Relations\n- relates_to [[Future Connections]]"
        
        formatted_relations = []
        for rel in relations:
            rel_type = rel.get('type', 'relates_to')
            target = rel.get('target', 'Unknown')
            
            # Format as wiki link if not already
            if not target.startswith('[['):
                target = f"[[{target}]]"
            
            formatted_relations.append(f"- {rel_type} {target}")
        
        return "## Relations\n" + "\n".join(formatted_relations)
    
    def _format_context_section(self, context: str) -> str:
        """Format context section if provided."""
        if not context.strip():
            return ""
        
        return f"""## Context
{context.strip()}

"""
    
    def _generate_related_knowledge(self, analysis_result) -> str:
        """Generate related knowledge section with forward references."""
        # Create forward references based on domains and content type
        related_items = []
        
        # Add domain-specific MOCs
        if analysis_result.primary_domain != 'general':
            domain_title = analysis_result.primary_domain.replace('-', ' ').title()
            related_items.append(f"[[{domain_title} MOC]]")
        
        # Add related concepts based on tags
        for tag in analysis_result.tags[2:4]:  # Skip domain and type tags
            if tag not in ['note', 'moc', 'project', 'area', 'resource']:
                concept_title = tag.replace('-', ' ').title()
                related_items.append(f"[[{concept_title} Concepts]]")
        
        # Add generic references
        if analysis_result.content_type == 'note':
            related_items.append(f"[[{analysis_result.primary_domain.title()} Best Practices]]")
        
        # Ensure we have at least some forward references
        if not related_items:
            related_items = ["[[Future Connections]]", "[[Related Concepts]]"]
        
        return "## Related Knowledge\n" + "\n".join(f"- {item}" for item in related_items[:3])
    
    def _format_knowledge_clusters(self, notes_cluster: List[Dict[str, Any]]) -> str:
        """Format knowledge clusters for MOCs."""
        if not notes_cluster:
            return "## Knowledge Clusters\n### Core Notes\n- [[Future Note 1]]\n- [[Future Note 2]]"
        
        # Group notes by subdomain or type
        clusters = {}
        for note in notes_cluster:
            subdomain = note.get('subdomain', 'General')
            if subdomain not in clusters:
                clusters[subdomain] = []
            clusters[subdomain].append(note)
        
        formatted_clusters = ["## Knowledge Clusters"]
        
        for cluster_name, cluster_notes in clusters.items():
            formatted_clusters.append(f"### {cluster_name}")
            for note in cluster_notes[:5]:  # Limit to 5 notes per cluster
                title = note.get('title', 'Unknown Note')
                formatted_clusters.append(f"- [[{title}]]")
        
        return "\n".join(formatted_clusters)
    
    def _format_core_concepts(self, notes_cluster: List[Dict[str, Any]]) -> str:
        """Format core concepts section for MOCs."""
        if not notes_cluster:
            return "- [[Key Concept 1]] - Core understanding\n- [[Key Concept 2]] - Important principle"
        
        core_concepts = []
        for note in notes_cluster[:5]:  # Top 5 notes
            title = note.get('title', 'Unknown Note')
            summary = note.get('summary', 'Important concept')
            core_concepts.append(f"- [[{title}]] - {summary}")
        
        return "\n".join(core_concepts)
    
    def _generate_emerging_patterns(self, analysis_result) -> str:
        """Generate emerging patterns section for MOCs."""
        patterns = []
        
        # Pattern based on primary domain
        if analysis_result.primary_domain != 'general':
            patterns.append(f"Consistent patterns emerging in {analysis_result.primary_domain} implementations")
        
        # Pattern based on observations
        if analysis_result.observations:
            obs_types = [obs['type'] for obs in analysis_result.observations]
            if 'technical-finding' in obs_types:
                patterns.append("Technical solutions follow similar architectural principles")
            if 'issue' in obs_types:
                patterns.append("Common failure modes and resolution strategies")
        
        if not patterns:
            patterns = ["Patterns will emerge as knowledge cluster grows"]
        
        return "\n".join(patterns)
    
    def _generate_potential_projects(self, analysis_result) -> str:
        """Generate potential projects section for MOCs."""
        projects = []
        
        # Project ideas based on domain
        domain_projects = {
            'azure': "Azure infrastructure automation project",
            'terraform': "Terraform module standardization initiative", 
            'dns': "DNS management automation system",
            'networking': "Network monitoring and troubleshooting toolkit",
            'devops': "CI/CD pipeline optimization project"
        }
        
        if analysis_result.primary_domain in domain_projects:
            projects.append(domain_projects[analysis_result.primary_domain])
        
        # Generic project suggestions
        projects.append(f"Knowledge synthesis and documentation for {analysis_result.primary_domain}")
        
        if not projects:
            projects = ["Future projects will be identified as patterns emerge"]
        
        return "\n".join(f"- {project}" for project in projects[:3])
    
    def _clean_observation_text(self, text: str) -> str:
        """Clean and format observation text."""
        # Remove newlines and extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure proper sentence structure
        if not cleaned.endswith('.'):
            cleaned += '.'
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        # Limit length
        if len(cleaned) > 150:
            cleaned = cleaned[:147] + "..."
        
        return cleaned
    
    def generate_filename(self, analysis_result, timestamp: datetime = None) -> str:
        """Generate INMPARA-compliant filename."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format: YYYY-MM-DD-title-slug.md
        date_prefix = timestamp.strftime("%Y-%m-%d")
        filename = f"{date_prefix}-{analysis_result.slug}.md"
        
        return filename
    
    def get_file_path(self, analysis_result, timestamp: datetime = None) -> str:
        """Get complete file path for the note."""
        folder = self.folder_mapping.get(analysis_result.content_type, '1 - Notes')
        filename = self.generate_filename(analysis_result, timestamp)
        
        return f"{self.vault_path}/{folder}/{filename}"
    
    def generate_inbox_processing_report(self, processed_items: List[Dict[str, Any]]) -> str:
        """Generate a processing report for inbox items."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report_sections = [
            f"# Inbox Processing Report - {timestamp}",
            "",
            f"**Total Items Processed**: {len(processed_items)}",
            ""
        ]
        
        # Group by action
        auto_filed = [item for item in processed_items if item.get('action') == 'auto_filed']
        suggestions = [item for item in processed_items if item.get('action') == 'suggested']
        errors = [item for item in processed_items if item.get('action') == 'error']
        
        if auto_filed:
            report_sections.extend([
                f"## Auto-Filed Items ({len(auto_filed)})",
                ""
            ])
            for item in auto_filed:
                conf = item.get('confidence', 0)
                report_sections.append(
                    f"✅ **{item['title']}** → `{item['destination']}` (Confidence: {conf:.0%})"
                )
                report_sections.append(f"   *{item.get('reasoning', 'No reasoning provided')}*")
                report_sections.append("")
        
        if suggestions:
            report_sections.extend([
                f"## Suggestions Requiring Review ({len(suggestions)})",
                ""
            ])
            for item in suggestions:
                conf = item.get('confidence', 0)
                report_sections.append(
                    f"⚠️ **{item['title']}** → `{item['destination']}` (Confidence: {conf:.0%})"
                )
                report_sections.append(f"   *{item.get('reasoning', 'No reasoning provided')}*")
                report_sections.append("")
        
        if errors:
            report_sections.extend([
                f"## Processing Errors ({len(errors)})",
                ""
            ])
            for item in errors:
                report_sections.append(f"❌ **{item['title']}**: {item.get('error', 'Unknown error')}")
                report_sections.append("")
        
        # Summary stats
        total_auto_filed = len(auto_filed)
        avg_confidence = sum(item.get('confidence', 0) for item in auto_filed) / max(len(auto_filed), 1)
        
        report_sections.extend([
            "## Summary Statistics",
            "",
            f"- **Auto-filed**: {total_auto_filed} items",
            f"- **Average Confidence**: {avg_confidence:.0%}",
            f"- **Items Needing Review**: {len(suggestions)}",
            f"- **Processing Errors**: {len(errors)}",
            "",
            "---",
            "*Generated by INMPARA Notebook Server*"
        ])
        
        return "\n".join(report_sections)
    
    def validate_inmpara_format(self, content: str) -> Dict[str, Any]:
        """Validate content against INMPARA formatting standards."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        lines = content.split('\n')
        
        # Check for frontmatter
        if not content.startswith('---'):
            validation_result['valid'] = False
            validation_result['errors'].append("Missing YAML frontmatter")
        else:
            # Extract and validate frontmatter
            try:
                frontmatter_end = content.find('---', 3)
                if frontmatter_end == -1:
                    validation_result['valid'] = False
                    validation_result['errors'].append("Malformed frontmatter - missing closing ---")
                else:
                    frontmatter_yaml = content[3:frontmatter_end]
                    frontmatter = yaml.safe_load(frontmatter_yaml)
                    
                    # Check required fields
                    required_fields = ['title', 'type', 'tags', 'created', 'updated', 'status', 'stage', 'domain']
                    for field in required_fields:
                        if field not in frontmatter:
                            validation_result['errors'].append(f"Missing required frontmatter field: {field}")
                    
                    # Validate tag format
                    if 'tags' in frontmatter:
                        tags = frontmatter['tags']
                        if not isinstance(tags, list) or len(tags) < 3:
                            validation_result['warnings'].append("Should have at least 3 tags in hierarchical order")
            
            except yaml.YAMLError as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Invalid YAML frontmatter: {e}")
        
        # Check for title matching
        h1_pattern = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not h1_pattern:
            validation_result['errors'].append("Missing main title (# header)")
        
        # Check for required sections
        required_sections = ['## Content', '## Observations', '## Relations', '## Tags']
        for section in required_sections:
            if section not in content:
                validation_result['warnings'].append(f"Missing recommended section: {section}")
        
        # Check semantic markup format
        observation_pattern = r'- \[[\w-]+\] .+ #[\w-]+'
        if '## Observations' in content and not re.search(observation_pattern, content):
            validation_result['suggestions'].append("Observations should use semantic markup: - [category] text #tags")
        
        # Check wiki links format
        wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        for link in wiki_links:
            if not link.strip():
                validation_result['warnings'].append("Empty wiki link found")
        
        if validation_result['errors']:
            validation_result['valid'] = False
        
        return validation_result
