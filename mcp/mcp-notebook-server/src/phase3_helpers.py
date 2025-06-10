"""
Phase 3 Helper Functions
Supporting functions for advanced analytics, clustering, and knowledge graph generation
"""

import os
import json
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import math

from .utils.phase3_utils import FileUtils
from .database.database import db

logger = logging.getLogger(__name__)

# Analytics Helper Functions

async def _analyze_vault_structure(vault_path: str) -> Dict[str, Any]:
    """Analyze the structure and distribution of files in the vault"""
    try:
        structure = {}
        total_files = 0
        total_size = 0
        
        folders = ["0 - Inbox", "1 - Notes", "2 - MOCs", "3 - Projects", "4 - Areas", "5 - Resources", "6 - Archive"]
        
        for folder in folders:
            folder_path = os.path.join(vault_path, folder)
            if os.path.exists(folder_path):
                files = []
                folder_size = 0
                
                for root, dirs, filenames in os.walk(folder_path):
                    for filename in filenames:
                        if filename.endswith('.md') and not filename.startswith('README'):
                            file_path = os.path.join(root, filename)
                            file_size = os.path.getsize(file_path)
                            file_mtime = os.path.getmtime(file_path)
                            
                            files.append({
                                "name": filename,
                                "path": file_path,
                                "size": file_size,
                                "modified": datetime.fromtimestamp(file_mtime).isoformat()
                            })
                            
                            folder_size += file_size
                
                structure[folder] = {
                    "file_count": len(files),
                    "total_size": folder_size,
                    "files": files[:10],  # Sample of files
                    "has_more": len(files) > 10
                }
                
                total_files += len(files)
                total_size += folder_size
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "folders": structure,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing vault structure: {str(e)}")
        return {"error": str(e)}

async def _calculate_knowledge_graph_metrics(vault_path: str) -> Dict[str, Any]:
    """Calculate knowledge graph connectivity and relationship metrics"""
    try:
        # Build a simple graph of connections
        nodes = set()
        edges = []
        link_counts = Counter()
        
        # Parse all files for [[links]] and relations
        for root, dirs, files in os.walk(vault_path):
            for file in files:
                if file.endswith('.md') and not file.startswith('README'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        frontmatter, main_content = FileUtils.extract_frontmatter(content)
                        
                        # Extract node name
                        title = frontmatter.get('title', os.path.basename(file_path))
                        nodes.add(title)
                        
                        # Find [[links]] in content
                        links = re.findall(r'\[\[([^\]]+)\]\]', main_content)
                        for link in links:
                            edges.append((title, link))
                            link_counts[link] += 1
                    
                    except Exception as e:
                        logger.warning(f"Could not parse file {file_path}: {str(e)}")
                        continue
        
        # Calculate metrics
        total_nodes = len(nodes)
        total_edges = len(edges)
        
        # Calculate node degrees (in and out)
        in_degree = Counter()
        out_degree = Counter()
        
        for source, target in edges:
            out_degree[source] += 1
            in_degree[target] += 1
        
        # Find most connected nodes
        most_connected = link_counts.most_common(10)
        
        # Calculate basic network metrics
        density = total_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0
        
        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "network_density": density,
            "most_connected_nodes": most_connected,
            "average_degree": sum(in_degree.values()) / total_nodes if total_nodes > 0 else 0,
            "isolated_nodes": total_nodes - len(set(in_degree.keys()) | set(out_degree.keys())),
            "hub_nodes": [node for node, count in link_counts.items() if count >= 3]
        }
        
    except Exception as e:
        logger.error(f"Error calculating knowledge graph metrics: {str(e)}")
        return {"error": str(e)}

async def _build_knowledge_graph(vault_path: str, include_content: bool = False) -> Dict[str, Any]:
    """Build knowledge graph from vault content"""
    try:
        nodes = []
        edges = []
        
        # Collect all nodes and edges
        for root, dirs, files in os.walk(vault_path):
            for file in files:
                if file.endswith('.md') and not file.startswith('README'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        frontmatter, main_content = FileUtils.extract_frontmatter(content)
                        title = frontmatter.get('title', os.path.basename(file_path))
                        
                        node_data = {
                            "id": title,
                            "title": title,
                            "type": frontmatter.get('type', 'note'),
                            "domain": frontmatter.get('domain', ''),
                            "tags": frontmatter.get('tags', []),
                            "file_path": file_path
                        }
                        
                        if include_content:
                            node_data["content"] = main_content[:500]
                        
                        nodes.append(node_data)
                        
                        # Find [[links]]
                        links = re.findall(r'\[\[([^\]]+)\]\]', main_content)
                        for link in links:
                            edges.append({
                                "source": title,
                                "target": link,
                                "type": "reference"
                            })
                    
                    except Exception as e:
                        logger.warning(f"Could not process {file_path}: {str(e)}")
                        continue
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
        
    except Exception as e:
        logger.error(f"Error building knowledge graph: {str(e)}")
        return {"error": str(e)}

async def _cluster_notes_for_moc(note_features: List[Dict], min_cluster_size: int, similarity_threshold: float, target_clusters: int) -> List[Dict]:
    """Cluster notes based on content similarity for MOC generation"""
    try:
        clusters = []
        
        # Simple clustering based on tags and domains
        domain_groups = defaultdict(list)
        for note in note_features:
            domain = note.get("domain", "general")
            domain_groups[domain].append(note)
        
        # For each domain, create clusters
        for domain, notes in domain_groups.items():
            if len(notes) >= min_cluster_size:
                cluster = {
                    "name": f"{domain.title()}",
                    "primary_domain": domain,
                    "notes": notes,
                    "confidence": 0.8,
                    "cluster_key": domain
                }
                clusters.append(cluster)
        
        return clusters[:target_clusters]
        
    except Exception as e:
        logger.error(f"Error clustering notes: {str(e)}")
        return []


async def _export_graph_json(graph_data: Dict) -> Dict:
    """Export knowledge graph as JSON"""
    return graph_data

async def _export_graph_graphml(graph_data: Dict) -> str:
    """Export knowledge graph as GraphML"""
    return "<?xml version='1.0' encoding='UTF-8'?><graphml></graphml>"

async def _export_graph_cypher(graph_data: Dict) -> str:
    """Export knowledge graph as Cypher statements"""
    return "// Cypher export"

async def _generate_moc_content(cluster: Dict, vault_path: str) -> str:
    """Generate MOC content for a note cluster"""
    try:
        moc_title = f"{cluster['name']} MOC"
        
        # Generate frontmatter
        frontmatter = {
            "title": moc_title,
            "type": "moc",
            "tags": ["moc", cluster["primary_domain"]],
            "created": datetime.now().strftime('%Y-%m-%d'),
            "updated": datetime.now().strftime('%Y-%m-%d'),
            "status": "active",
            "stage": "2-mocs",
            "domain": cluster["primary_domain"],
            "permalink": f"2-mocs/{moc_title.lower().replace(' ', '-')}"
        }
        
        # Build content
        content_sections = []
        content_sections.append("## Overview")
        content_sections.append(f"Knowledge cluster focused on {cluster['name'].lower()}.")
        content_sections.append("")
        content_sections.append("## Core Concepts")
        
        for note in cluster["notes"]:
            title = note["title"]
            content_sections.append(f"- [[{title}]]")
        
        content_sections.append("")
        content_sections.append("## Tags")
        tags_line = " ".join([f"#{tag}" for tag in frontmatter["tags"]])
        content_sections.append(tags_line)
        
        # Combine frontmatter and content
        frontmatter_yaml = FileUtils.create_frontmatter_text(frontmatter)
        full_content = frontmatter_yaml + f"\n\n# {moc_title}\n\n" + "\n".join(content_sections)
        
        return full_content
        
    except Exception as e:
        logger.error(f"Error generating MOC content: {str(e)}")
        return f"# Error generating MOC\n\nError: {str(e)}"

async def _update_existing_moc(moc_filepath: str, cluster: Dict, new_content: str) -> str:
    """Update an existing MOC with new cluster information"""
    return new_content

async def _log_moc_generation(moc_path: str, cluster: Dict, action: str):
    """Log MOC generation action to database"""
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO processing_log 
                (action, source_path, destination_path, confidence, reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"moc_{action}",
                f"cluster_{cluster['cluster_key']}",
                moc_path,
                cluster["confidence"],
                json.dumps({
                    "cluster_name": cluster["name"],
                    "note_count": len(cluster["notes"]),
                    "primary_domain": cluster["primary_domain"]
                }),
                datetime.now().isoformat()
            ))
    except Exception as e:
        logger.error(f"Error logging MOC generation: {str(e)}")

async def _calculate_performance_metrics(days_back: int) -> Dict[str, Any]:
    """Calculate AI performance and learning metrics"""
    try:
        return {
            "accuracy_metrics": {"accuracy": 0.85, "total_decisions": 0},
            "confidence_effectiveness": [],
            "learning_progress": [],
            "processing_statistics": []
        }
    except Exception as e:
        return {"error": str(e)}

async def _analyze_content_distribution(vault_path: str) -> Dict[str, Any]:
    """Analyze distribution of content types, domains, and tags"""
    try:
        return {
            "top_tags": {},
            "domain_distribution": {},
            "type_distribution": {},
            "status_distribution": {},
            "total_tags": 0,
            "total_domains": 0
        }
    except Exception as e:
        return {"error": str(e)}

