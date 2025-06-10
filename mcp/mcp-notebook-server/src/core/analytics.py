"""
INMPARA Analytics Module

This module handles comprehensive vault analytics, reporting, knowledge graph
export, and MOC generation from content clusters.

Target: ~400 lines - Complete analytics and reporting functionality
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class AnalyticsManager:
    """
    Manages analytics and reporting operations for the INMPARA vault.
    
    Handles vault statistics, content analysis, knowledge graph generation,
    MOC creation from clusters, and comprehensive reporting.
    """
    
    def __init__(self, vault_path: str, database=None, vector_search=None):
        """Initialize the AnalyticsManager with required components."""
        self.vault_path = vault_path
        self.database = database
        self.vector_search = vector_search
        
        logger.info(f"AnalyticsManager initialized for vault: {vault_path}")
    
    async def generate_vault_analytics(self, include_patterns: bool = True,
                                     include_trends: bool = True) -> Dict[str, Any]:
        """Generate comprehensive vault analytics and insights."""
        try:
            analytics = {
                'generated_at': datetime.now().isoformat(),
                'vault_path': self.vault_path
            }
            
            # Basic vault statistics
            analytics['basic_stats'] = self._get_basic_stats()
            
            # Content distribution analysis
            analytics['content_distribution'] = self._analyze_content_distribution()
            
            # Folder structure analysis
            analytics['folder_structure'] = self._analyze_folder_structure()
            
            # Content quality metrics
            analytics['quality_metrics'] = self._analyze_content_quality()
            
            # Database-dependent analytics
            if self.database:
                analytics['tag_analysis'] = self._analyze_tags()
                analytics['domain_analysis'] = self._analyze_domains()
                analytics['processing_metrics'] = self._get_processing_metrics()
                
                if include_patterns:
                    analytics['learned_patterns'] = self._analyze_learned_patterns()
                    
                if include_trends:
                    analytics['trends'] = self._analyze_trends()
            
            return {
                'success': True,
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error generating vault analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    async def export_knowledge_graph(self, format: str = 'json', include_metadata: bool = True,
                                   output_path: str = None) -> Dict[str, Any]:
        """Export vault as knowledge graph in various formats."""
        try:
            # Build knowledge graph
            graph_data = await self._build_knowledge_graph(include_metadata)
            
            if not graph_data:
                return {'success': False, 'error': 'Failed to build knowledge graph'}
            
            # Export in requested format
            if format.lower() == 'json':
                result = self._export_json_graph(graph_data, output_path)
            elif format.lower() == 'graphml':
                result = self._export_graphml_graph(graph_data, output_path)
            elif format.lower() == 'cypher':
                result = self._export_cypher_graph(graph_data, output_path)
            else:
                return {'success': False, 'error': f'Unsupported format: {format}'}
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting knowledge graph: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_basic_stats(self) -> Dict[str, Any]:
        """Get basic vault statistics."""
        stats = {
            'total_notes': 0,
            'total_size_bytes': 0,
            'folders': {},
            'file_types': defaultdict(int)
        }
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                folder_name = os.path.relpath(root, self.vault_path)
                if folder_name == '.':
                    folder_name = 'root'
                
                folder_stats = {'files': 0, 'size': 0}
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    folder_stats['files'] += 1
                    folder_stats['size'] += file_size
                    stats['file_types'][file_ext] += 1
                    
                    if file.endswith('.md'):
                        stats['total_notes'] += 1
                    
                    stats['total_size_bytes'] += file_size
                
                if folder_stats['files'] > 0:
                    stats['folders'][folder_name] = folder_stats
            
        except Exception as e:
            logger.error(f"Error getting basic stats: {e}")
        
        return stats
    
    def _analyze_content_distribution(self) -> Dict[str, Any]:
        """Analyze content distribution across the vault."""
        distribution = {
            'by_folder': defaultdict(int),
            'by_size': {'small': 0, 'medium': 0, 'large': 0},
            'by_age': {'recent': 0, 'month': 0, 'older': 0}
        }
        
        now = datetime.now()
        recent_threshold = now - timedelta(days=7)
        month_threshold = now - timedelta(days=30)
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    folder_name = os.path.relpath(root, self.vault_path)
                    
                    # Count by folder
                    distribution['by_folder'][folder_name] += 1
                    
                    # Analyze by size
                    file_size = os.path.getsize(file_path)
                    if file_size < 1000:  # < 1KB
                        distribution['by_size']['small'] += 1
                    elif file_size < 10000:  # < 10KB
                        distribution['by_size']['medium'] += 1
                    else:
                        distribution['by_size']['large'] += 1
                    
                    # Analyze by age
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time > recent_threshold:
                        distribution['by_age']['recent'] += 1
                    elif mod_time > month_threshold:
                        distribution['by_age']['month'] += 1
                    else:
                        distribution['by_age']['older'] += 1
        
        except Exception as e:
            logger.error(f"Error analyzing content distribution: {e}")
        
        return dict(distribution)
    
    def _analyze_folder_structure(self) -> Dict[str, Any]:
        """Analyze the folder structure and organization."""
        structure = {
            'depth': 0,
            'folders_by_level': {},
            'largest_folders': {},
            'empty_folders': []
        }
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                level = root.replace(self.vault_path, '').count(os.sep)
                structure['depth'] = max(structure['depth'], level)
                
                if level not in structure['folders_by_level']:
                    structure['folders_by_level'][level] = 0
                structure['folders_by_level'][level] += 1
                
                folder_name = os.path.relpath(root, self.vault_path)
                md_files = [f for f in files if f.endswith('.md')]
                
                if md_files:
                    structure['largest_folders'][folder_name] = len(md_files)
                elif not files and not dirs:
                    structure['empty_folders'].append(folder_name)
            
            # Keep only top 10 largest folders
            structure['largest_folders'] = dict(
                sorted(structure['largest_folders'].items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
        except Exception as e:
            logger.error(f"Error analyzing folder structure: {e}")
        
        return structure
    
    def _analyze_content_quality(self) -> Dict[str, Any]:
        """Analyze content quality metrics."""
        quality = {
            'notes_with_frontmatter': 0,
            'notes_with_tags': 0,
            'notes_with_links': 0,
            'average_word_count': 0,
            'quality_score_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        total_notes = 0
        total_words = 0
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    total_notes += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for frontmatter
                        if content.startswith('---'):
                            quality['notes_with_frontmatter'] += 1
                            
                            # Parse frontmatter for tags
                            try:
                                import yaml
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    frontmatter = yaml.safe_load(parts[1])
                                    if frontmatter.get('tags'):
                                        quality['notes_with_tags'] += 1
                            except:
                                pass
                        
                        # Check for internal links
                        if '[[' in content and ']]' in content:
                            quality['notes_with_links'] += 1
                        
                        # Count words
                        word_count = len(content.split())
                        total_words += word_count
                        
                        # Assess quality score
                        score = self._calculate_quality_score(content)
                        if score >= 0.7:
                            quality['quality_score_distribution']['high'] += 1
                        elif score >= 0.4:
                            quality['quality_score_distribution']['medium'] += 1
                        else:
                            quality['quality_score_distribution']['low'] += 1
                            
                    except Exception as e:
                        logger.warning(f"Error analyzing file {file_path}: {e}")
            
            if total_notes > 0:
                quality['average_word_count'] = total_words / total_notes
                
        except Exception as e:
            logger.error(f"Error analyzing content quality: {e}")
        
        return quality
    
    def _analyze_tags(self) -> Dict[str, Any]:
        """Analyze tag usage across the vault."""
        tag_analysis = {
            'total_unique_tags': 0,
            'most_common_tags': [],
            'tag_frequency': {},
            'orphan_tags': []
        }
        
        if not self.database:
            return tag_analysis
        
        try:
            tag_stats = self.database.get_tag_statistics()
            tag_analysis['total_unique_tags'] = len(tag_stats)
            
            sorted_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)
            tag_analysis['most_common_tags'] = sorted_tags[:20]
            tag_analysis['tag_frequency'] = dict(sorted_tags)
            tag_analysis['orphan_tags'] = [tag for tag, count in sorted_tags if count == 1]
            
        except Exception as e:
            logger.error(f"Error analyzing tags: {e}")
        
        return tag_analysis
    
    def _analyze_domains(self) -> Dict[str, Any]:
        """Analyze domain distribution across the vault."""
        domain_analysis = {
            'total_domains': 0,
            'domain_distribution': {},
            'notes_by_domain': {}
        }
        
        if not self.database:
            return domain_analysis
        
        try:
            domain_stats = self.database.get_domain_statistics()
            domain_analysis['total_domains'] = len(domain_stats)
            domain_analysis['domain_distribution'] = domain_stats
            
            for domain in domain_stats.keys():
                notes = self.database.search_by_domain(domain)
                domain_analysis['notes_by_domain'][domain] = len(notes)
                
        except Exception as e:
            logger.error(f"Error analyzing domains: {e}")
        
        return domain_analysis
    
    def _get_processing_metrics(self) -> Dict[str, Any]:
        """Get AI processing performance metrics."""
        metrics = {
            'total_actions': 0,
            'auto_approved': 0,
            'manual_review': 0,
            'accuracy_rate': 0.0
        }
        
        try:
            actions = self.database.get_recent_processing_actions(limit=1000)
            metrics['total_actions'] = len(actions)
            
            approved = sum(1 for action in actions if action.get('approved', False))
            rejected = sum(1 for action in actions if action.get('rejected', False))
            
            metrics['auto_approved'] = approved
            metrics['manual_review'] = rejected
            
            if approved + rejected > 0:
                metrics['accuracy_rate'] = approved / (approved + rejected)
                
        except Exception as e:
            logger.error(f"Error getting processing metrics: {e}")
        
        return metrics
    
    def _analyze_learned_patterns(self) -> Dict[str, Any]:
        """Analyze learned patterns and their effectiveness."""
        pattern_analysis = {
            'total_patterns': 0,
            'pattern_types': {},
            'effectiveness': {}
        }
        
        try:
            if hasattr(self.database, 'get_learned_patterns'):
                patterns = self.database.get_learned_patterns()
                pattern_analysis['total_patterns'] = len(patterns)
                
                for pattern in patterns:
                    pattern_type = pattern.get('type', 'unknown')
                    if pattern_type not in pattern_analysis['pattern_types']:
                        pattern_analysis['pattern_types'][pattern_type] = 0
                    pattern_analysis['pattern_types'][pattern_type] += 1
                    
        except Exception as e:
            logger.error(f"Error analyzing learned patterns: {e}")
        
        return pattern_analysis
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends in vault activity and growth."""
        trends = {
            'note_creation_trend': {},
            'processing_trends': {}
        }
        
        try:
            for i in range(12):
                month_start = datetime.now().replace(day=1) - timedelta(days=30 * i)
                month_key = month_start.strftime('%Y-%m')
                
                note_count = self._count_notes_in_month(month_start)
                trends['note_creation_trend'][month_key] = note_count
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
        
        return trends
    
    async def _build_knowledge_graph(self, include_metadata: bool) -> Dict[str, Any]:
        """Build knowledge graph data structure."""
        graph = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'include_metadata': include_metadata
            }
        }
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    node = self._create_graph_node(file_path, include_metadata)
                    if node:
                        graph['nodes'].append(node)
            
            graph['edges'] = await self._find_note_connections(graph['nodes'])
            
        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")
            return None
        
        return graph
    
    def _create_graph_node(self, file_path: str, include_metadata: bool) -> Optional[Dict]:
        """Create a graph node from a note file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            node = {
                'id': os.path.relpath(file_path, self.vault_path),
                'label': os.path.basename(file_path).replace('.md', ''),
                'type': 'note',
                'file_path': file_path
            }
            
            if include_metadata:
                if content.startswith('---'):
                    try:
                        import yaml
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            frontmatter = yaml.safe_load(parts[1])
                            node['metadata'] = frontmatter
                    except:
                        pass
                
                stat = os.stat(file_path)
                node['file_size'] = stat.st_size
                node['created'] = stat.st_ctime
                node['modified'] = stat.st_mtime
                node['word_count'] = len(content.split())
            
            return node
            
        except Exception as e:
            logger.warning(f"Error creating node for {file_path}: {e}")
            return None
    
    async def _find_note_connections(self, nodes: List[Dict]) -> List[Dict]:
        """Find connections between notes."""
        edges = []
        
        for node in nodes:
            try:
                with open(node['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import re
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                
                for link in links:
                    target_node = self._find_node_by_title(nodes, link)
                    if target_node:
                        edges.append({
                            'source': node['id'],
                            'target': target_node['id'],
                            'type': 'link',
                            'label': 'links to'
                        })
                        
            except Exception as e:
                logger.warning(f"Error finding connections for {node['id']}: {e}")
        
        return edges
    
    def _find_node_by_title(self, nodes: List[Dict], title: str) -> Optional[Dict]:
        """Find a node by its title."""
        for node in nodes:
            if node['label'].lower() == title.lower():
                return node
        return None
    
    def _export_json_graph(self, graph_data: Dict, output_path: str = None) -> Dict[str, Any]:
        """Export graph as JSON."""
        try:
            if not output_path:
                output_path = os.path.join(self.vault_path, 'knowledge_graph.json')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, default=str)
            
            return {
                'success': True,
                'format': 'json',
                'output_path': output_path,
                'nodes': len(graph_data['nodes']),
                'edges': len(graph_data['edges'])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _export_graphml_graph(self, graph_data: Dict, output_path: str = None) -> Dict[str, Any]:
        """Export graph as GraphML."""
        try:
            if not output_path:
                output_path = os.path.join(self.vault_path, 'knowledge_graph.graphml')
            
            graphml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            graphml_content += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
            graphml_content += '<graph id="knowledge_graph" edgedefault="directed">\n'
            
            for node in graph_data['nodes']:
                graphml_content += f'<node id="{node["id"]}">\n'
                graphml_content += f'<data key="label">{node["label"]}</data>\n'
                graphml_content += '</node>\n'
            
            for edge in graph_data['edges']:
                graphml_content += f'<edge source="{edge["source"]}" target="{edge["target"]}">\n'
                graphml_content += f'<data key="label">{edge["label"]}</data>\n'
                graphml_content += '</edge>\n'
            
            graphml_content += '</graph>\n</graphml>'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(graphml_content)
            
            return {
                'success': True,
                'format': 'graphml',
                'output_path': output_path,
                'nodes': len(graph_data['nodes']),
                'edges': len(graph_data['edges'])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _export_cypher_graph(self, graph_data: Dict, output_path: str = None) -> Dict[str, Any]:
        """Export graph as Cypher statements."""
        try:
            if not output_path:
                output_path = os.path.join(self.vault_path, 'knowledge_graph.cypher')
            
            cypher_statements = []
            
            for node in graph_data['nodes']:
                stmt = f"CREATE (n:{node['type']} {{id: '{node['id']}', label: '{node['label']}'}})"
                cypher_statements.append(stmt)
            
            for edge in graph_data['edges']:
                stmt = f"MATCH (a {{id: '{edge['source']}'}}), (b {{id: '{edge['target']}'}}) CREATE (a)-[:{edge['type'].upper()}]->(b)"
                cypher_statements.append(stmt)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cypher_statements))
            
            return {
                'success': True,
                'format': 'cypher',
                'output_path': output_path,
                'statements': len(cypher_statements)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate a quality score for content."""
        score = 0.0
        
        if content.startswith('---'):
            score += 0.3
        
        if '\n#' in content:
            score += 0.2
        
        if '[[' in content or 'http' in content:
            score += 0.2
        
        word_count = len(content.split())
        if 50 <= word_count <= 2000:
            score += 0.3
        elif word_count > 2000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _count_notes_in_month(self, month_start: datetime) -> int:
        """Count notes created in a specific month."""
        count = 0
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end - timedelta(days=month_end.day)
        
        try:
            for root, dirs, files in os.walk(self.vault_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if not file.endswith('.md'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    created_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if month_start <= created_time <= month_end:
                        count += 1
        
        except Exception as e:
            logger.error(f"Error counting notes in month: {e}")
        
        return count
    
    def _calculate_recent_accuracy(self, actions: List[Dict]) -> float:
        """Calculate accuracy for recent actions."""
        if not actions:
            return 0.0
        
        approved = sum(1 for action in actions if action.get('approved', False))
        total = len(actions)
        
        return approved / total if total > 0 else 0.0
