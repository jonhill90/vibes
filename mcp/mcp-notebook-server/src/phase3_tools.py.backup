from .phase3_helpers import _build_knowledge_graph, _cluster_notes_for_moc, _export_graph_json, _export_graph_graphml, _export_graph_cypher, _generate_moc_content, _update_existing_moc, _log_moc_generation, _calculate_performance_metrics, _analyze_content_distribution, _analyze_vault_structure, _calculate_knowledge_graph_metrics
"""
Phase 3 Tools: Complete Automation & Advanced Analytics
Advanced batch processing, analytics, and knowledge graph features for INMPARA MCP Server
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import glob
import re
from collections import defaultdict, Counter

# Import our existing components
from .content_analyzer import content_analyzer
from .pattern_learner import pattern_learner
from .session_manager import session_manager
from .database.database import db
from .template_engine import template_engine
from .utils.phase3_utils import FileUtils

logger = logging.getLogger(__name__)

# Phase 3 Analytics & Batch Processing Tools

async def process_inbox_tool(
    vault_path: str = "/workspace/vibes/repos/inmpara",
    batch_size: int = 10,
    confidence_threshold: float = 0.7,
    auto_approve: bool = False
) -> Dict[str, Any]:
    """
    Complete batch processing pipeline for 0 - Inbox folder.
    Processes all inbox items with learned patterns and high-confidence automation.
    
    Args:
        vault_path: Path to INMPARA vault
        batch_size: Number of items to process in one batch
        confidence_threshold: Minimum confidence for auto-processing
        auto_approve: Whether to automatically approve high-confidence decisions
    """
    try:
        inbox_path = os.path.join(vault_path, "0 - Inbox")
        if not os.path.exists(inbox_path):
            return {
                "success": False,
                "error": "Inbox folder not found",
                "message": f"Inbox not found at {inbox_path}"
            }
        
        # Get all markdown files in inbox
        inbox_files = glob.glob(os.path.join(inbox_path, "**/*.md"), recursive=True)
        # Exclude README files
        inbox_files = [f for f in inbox_files if not f.endswith("README.md") and not "README" in os.path.basename(f)]
        
        if not inbox_files:
            return {
                "success": True,
                "processed_count": 0,
                "auto_processed": 0,
                "manual_review": 0,
                "message": "Inbox is empty - no files to process"
            }
        
        # Limit to batch size
        files_to_process = inbox_files[:batch_size]
        
        results = {
            "processed_count": 0,
            "auto_processed": 0,
            "manual_review": 0,
            "errors": [],
            "processed_files": [],
            "pending_review": []
        }
        
        for file_path in files_to_process:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip if already processed (has proper frontmatter)
                if content.startswith('---') and '---\n' in content[4:]:
                    logger.info(f"Skipping already processed file: {file_path}")
                    continue
                
                # Analyze content with learned patterns
                analysis = content_analyzer.analyze_content(content)
                confidence_adjustments = pattern_learner.get_confidence_adjustments(analysis)
                
                # Apply learned pattern adjustments
                adjusted_confidence = min(1.0, analysis.get('confidence', 0.0) + confidence_adjustments.get('overall_adjustment', 0.0))
                
                # Get current thresholds from pattern learner
                thresholds = pattern_learner.get_current_thresholds()
                
                file_result = {
                    "file_path": file_path,
                    "original_confidence": analysis.get('confidence', 0.0),
                    "adjusted_confidence": adjusted_confidence,
                    "analysis": analysis
                }
                
                # Process based on confidence
                if adjusted_confidence >= thresholds.get('auto_file', 0.85):
                    # High confidence - auto process
                    processed_result = await _auto_process_inbox_file(
                        file_path, content, analysis, vault_path, auto_approve
                    )
                    file_result.update(processed_result)
                    file_result["decision"] = "auto_processed"
                    results["auto_processed"] += 1
                    
                elif adjusted_confidence >= thresholds.get('suggest', 0.6):
                    # Medium confidence - suggest but don't auto-process
                    suggestions = await _generate_processing_suggestions(
                        file_path, content, analysis, vault_path
                    )
                    file_result.update(suggestions)
                    file_result["decision"] = "manual_review"
                    results["pending_review"].append(file_result)
                    results["manual_review"] += 1
                    
                else:
                    # Low confidence - flag for manual review
                    file_result["decision"] = "manual_review"
                    file_result["reason"] = "Low confidence score"
                    results["pending_review"].append(file_result)
                    results["manual_review"] += 1
                
                results["processed_files"].append(file_result)
                results["processed_count"] += 1
                
                # Log processing action
                await _log_inbox_processing_action(file_path, file_result, adjusted_confidence)
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return {
            "success": True,
            "vault_path": vault_path,
            "inbox_files_found": len(inbox_files),
            "batch_processed": len(files_to_process),
            **results,
            "message": f"Processed {results['processed_count']} files: {results['auto_processed']} auto-processed, {results['manual_review']} need review"
        }
        
    except Exception as e:
        logger.error(f"Error in process_inbox: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process inbox"
        }

async def bulk_reprocess_tool(
    vault_path: str = "/workspace/vibes/repos/inmpara",
    target_folder: str = "1 - Notes",
    reprocess_count: int = 20,
    min_confidence_improvement: float = 0.1
) -> Dict[str, Any]:
    """
    Quality improvement tools using learned patterns to reprocess existing notes.
    Uses learned patterns to improve confidence scores and suggestions for existing content.
    
    Args:
        vault_path: Path to INMPARA vault
        target_folder: Folder to reprocess (default: "1 - Notes")
        reprocess_count: Maximum number of notes to reprocess
        min_confidence_improvement: Minimum improvement needed to suggest changes
    """
    try:
        target_path = os.path.join(vault_path, target_folder)
        if not os.path.exists(target_path):
            return {
                "success": False,
                "error": "Target folder not found",
                "message": f"Folder not found at {target_path}"
            }
        
        # Get all markdown files in target folder
        target_files = glob.glob(os.path.join(target_path, "**/*.md"), recursive=True)
        # Exclude README files
        target_files = [f for f in target_files if not f.endswith("README.md") and not "README" in os.path.basename(f)]
        
        if not target_files:
            return {
                "success": True,
                "reprocessed_count": 0,
                "message": f"No files found in {target_folder}"
            }
        
        # Get learning insights to understand current patterns
        learning_insights = pattern_learner.get_learning_stats()
        
        # Sort files by potential for improvement (oldest first, lowest confidence first)
        files_to_reprocess = target_files[:reprocess_count]
        
        results = {
            "reprocessed_count": 0,
            "improvements_found": 0,
            "recommendations": [],
            "errors": []
        }
        
        for file_path in files_to_reprocess:
            try:
                # Read current file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract current frontmatter and content
                frontmatter, main_content = FileUtils.extract_frontmatter(content)
                
                # Re-analyze with current learned patterns
                analysis = content_analyzer.analyze_content(main_content)
                confidence_adjustments = pattern_learner.get_confidence_adjustments(analysis)
                
                # Get improved confidence score
                original_confidence = analysis.get('confidence', 0.0)
                improved_confidence = min(1.0, original_confidence + confidence_adjustments.get('overall_adjustment', 0.0))
                
                # Check if significant improvement possible
                confidence_improvement = improved_confidence - original_confidence
                
                if confidence_improvement >= min_confidence_improvement:
                    # Generate improvement recommendations
                    suggestions = pattern_learner.get_suggested_improvements(analysis)
                    
                    # Suggest better tags based on learned patterns
                    improved_tags = await _suggest_improved_tags(analysis, frontmatter)
                    
                    # Suggest better filing location if applicable
                    improved_location = await _suggest_improved_location(analysis, file_path, vault_path)
                    
                    recommendation = {
                        "file_path": file_path,
                        "original_confidence": original_confidence,
                        "improved_confidence": improved_confidence,
                        "confidence_improvement": confidence_improvement,
                        "current_frontmatter": frontmatter,
                        "improvement_suggestions": suggestions,
                        "improved_tags": improved_tags,
                        "improved_location": improved_location,
                        "analysis": analysis
                    }
                    
                    results["recommendations"].append(recommendation)
                    results["improvements_found"] += 1
                
                results["reprocessed_count"] += 1
                
            except Exception as e:
                error_msg = f"Error reprocessing {file_path}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return {
            "success": True,
            "target_folder": target_folder,
            "files_analyzed": len(files_to_reprocess),
            "learning_insights": learning_insights,
            **results,
            "message": f"Reprocessed {results['reprocessed_count']} files, found {results['improvements_found']} improvement opportunities"
        }
        
    except Exception as e:
        logger.error(f"Error in bulk_reprocess: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to bulk reprocess files"
        }

async def get_advanced_analytics_tool(
    vault_path: str = "/workspace/vibes/repos/inmpara",
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Advanced analytics and reporting on vault usage, AI decisions, and learning patterns.
    
    Args:
        vault_path: Path to INMPARA vault
        days_back: Number of days to analyze
    """
    try:
        # Get database analytics
        with db.get_connection() as conn:
            # Processing activity over time
            cursor = conn.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    action,
                    COUNT(*) as count,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN user_approved = 1 THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN user_approved = 0 THEN 1 ELSE 0 END) as rejected_count
                FROM processing_log 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY DATE(timestamp), action
                ORDER BY date DESC
            """.format(days_back))
            
            activity_data = [dict(row) for row in cursor.fetchall()]
            
            # Learning patterns statistics
            cursor = conn.execute("""
                SELECT 
                    pattern_type,
                    COUNT(*) as pattern_count,
                    AVG(confidence_impact) as avg_impact,
                    MAX(last_updated) as last_updated
                FROM learning_patterns
                GROUP BY pattern_type
                ORDER BY pattern_count DESC
            """)
            
            learning_stats = [dict(row) for row in cursor.fetchall()]
            
            # User feedback analysis
            cursor = conn.execute("""
                SELECT 
                    action_type,
                    COUNT(*) as feedback_count,
                    AVG(confidence_impact) as avg_confidence_impact
                FROM user_feedback
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY action_type
            """.format(days_back))
            
            feedback_stats = [dict(row) for row in cursor.fetchall()]
            
            # Session insights
            cursor = conn.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(*) as total_summaries,
                    AVG(topic_count) as avg_topics_per_session
                FROM session_summaries
                WHERE created_at >= datetime('now', '-{} days')
            """.format(days_back))
            
            session_stats = dict(cursor.fetchone())
        
        # Vault structure analysis
        vault_analytics = await _analyze_vault_structure(vault_path)
        
        # Content distribution analysis
        content_analytics = await _analyze_content_distribution(vault_path)
        
        # Knowledge graph metrics
        graph_metrics = await _calculate_knowledge_graph_metrics(vault_path)
        
        # Performance metrics
        performance_metrics = await _calculate_performance_metrics(days_back)
        
        return {
            "success": True,
            "analysis_period": f"Last {days_back} days",
            "generated_at": datetime.now().isoformat(),
            "processing_activity": activity_data,
            "learning_patterns": learning_stats,
            "user_feedback": feedback_stats,
            "session_analytics": session_stats,
            "vault_structure": vault_analytics,
            "content_distribution": content_analytics,
            "knowledge_graph": graph_metrics,
            "performance_metrics": performance_metrics,
            "message": f"Generated comprehensive analytics for {days_back} day period"
        }
        
    except Exception as e:
        logger.error(f"Error in get_advanced_analytics: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate advanced analytics"
        }

async def export_knowledge_graph_tool(
    vault_path: str = "/workspace/vibes/repos/inmpara",
    format: str = "json",
    include_content: bool = False
) -> Dict[str, Any]:
    """
    Knowledge graph visualization export capabilities.
    
    Args:
        vault_path: Path to INMPARA vault
        format: Export format (json, graphml, cypher)
        include_content: Whether to include full content or just metadata
    """
    try:
        # Build knowledge graph from vault content
        graph_data = await _build_knowledge_graph(vault_path, include_content)
        
        # Export in requested format
        if format == "json":
            export_data = await _export_graph_json(graph_data)
        elif format == "graphml":
            export_data = await _export_graph_graphml(graph_data)
        elif format == "cypher":
            export_data = await _export_graph_cypher(graph_data)
        else:
            return {
                "success": False,
                "error": "Unsupported format",
                "message": f"Format '{format}' not supported. Use: json, graphml, cypher"
            }
        
        # Save export to file
        export_filename = f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        export_path = os.path.join(vault_path, "99 - Meta", "exports", export_filename)
        
        # Ensure export directory exists
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(export_data, f, indent=2, default=str)
            else:
                f.write(export_data)
        
        return {
            "success": True,
            "export_format": format,
            "export_path": export_path,
            "graph_stats": {
                "node_count": len(graph_data.get("nodes", [])),
                "edge_count": len(graph_data.get("edges", [])),
                "included_content": include_content
            },
            "message": f"Knowledge graph exported to {export_path}"
        }
        
    except Exception as e:
        logger.error(f"Error in export_knowledge_graph: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to export knowledge graph"
        }

async def generate_moc_from_clusters_tool(
    vault_path: str = "/workspace/vibes/repos/inmpara",
    min_cluster_size: int = 3,
    similarity_threshold: float = 0.7,
    target_clusters: int = 5
) -> Dict[str, Any]:
    """
    MOC auto-generation from note clusters using content similarity and learned patterns.
    
    Args:
        vault_path: Path to INMPARA vault
        min_cluster_size: Minimum notes required to create a MOC
        similarity_threshold: Minimum similarity for clustering
        target_clusters: Target number of clusters to generate
    """
    try:
        # Get all notes from 1 - Notes folder
        notes_path = os.path.join(vault_path, "1 - Notes")
        notes_files = glob.glob(os.path.join(notes_path, "**/*.md"), recursive=True)
        notes_files = [f for f in notes_files if not f.endswith("README.md")]
        
        if len(notes_files) < min_cluster_size:
            return {
                "success": False,
                "error": "Insufficient notes",
                "message": f"Need at least {min_cluster_size} notes to generate MOCs"
            }
        
        # Analyze notes and extract features for clustering
        note_features = []
        for note_path in notes_files:
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, main_content = FileUtils.extract_frontmatter(content)
                analysis = content_analyzer.analyze_content(main_content)
                
                note_features.append({
                    "file_path": note_path,
                    "title": frontmatter.get("title", os.path.basename(note_path)),
                    "tags": frontmatter.get("tags", []),
                    "domain": frontmatter.get("domain", ""),
                    "analysis": analysis,
                    "content_preview": main_content[:200] + "..." if len(main_content) > 200 else main_content
                })
                
            except Exception as e:
                logger.warning(f"Could not analyze note {note_path}: {str(e)}")
                continue
        
        # Perform clustering based on tags, domain, and content similarity
        clusters = await _cluster_notes_for_moc(note_features, min_cluster_size, similarity_threshold, target_clusters)
        
        # Generate MOCs for each cluster
        generated_mocs = []
        moc_path = os.path.join(vault_path, "2 - MOCs")
        os.makedirs(moc_path, exist_ok=True)
        
        for cluster in clusters:
            if len(cluster["notes"]) >= min_cluster_size:
                try:
                    moc_content = await _generate_moc_content(cluster, vault_path)
                    moc_filename = f"{cluster['name'].lower().replace(' ', '-')}-moc.md"
                    moc_filepath = os.path.join(moc_path, moc_filename)
                    
                    # Check if MOC already exists
                    if os.path.exists(moc_filepath):
                        # Update existing MOC
                        moc_content = await _update_existing_moc(moc_filepath, cluster, moc_content)
                        action = "updated"
                    else:
                        action = "created"
                    
                    # Write MOC file
                    with open(moc_filepath, 'w', encoding='utf-8') as f:
                        f.write(moc_content)
                    
                    generated_mocs.append({
                        "moc_name": cluster["name"],
                        "moc_path": moc_filepath,
                        "note_count": len(cluster["notes"]),
                        "primary_domain": cluster["primary_domain"],
                        "action": action,
                        "confidence": cluster["confidence"]
                    })
                    
                    # Log MOC generation
                    await _log_moc_generation(moc_filepath, cluster, action)
                    
                except Exception as e:
                    logger.error(f"Error generating MOC for cluster {cluster['name']}: {str(e)}")
                    continue
        
        return {
            "success": True,
            "vault_path": vault_path,
            "notes_analyzed": len(note_features),
            "clusters_found": len(clusters),
            "mocs_generated": len(generated_mocs),
            "generated_mocs": generated_mocs,
            "clustering_params": {
                "min_cluster_size": min_cluster_size,
                "similarity_threshold": similarity_threshold,
                "target_clusters": target_clusters
            },
            "message": f"Generated {len(generated_mocs)} MOCs from {len(clusters)} clusters"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_moc_from_clusters: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate MOCs from clusters"
        }

# Helper functions for Phase 3 tools

async def _auto_process_inbox_file(file_path: str, content: str, analysis: Dict, vault_path: str, auto_approve: bool) -> Dict[str, Any]:
    """Auto-process a high-confidence inbox file"""
    try:
        # Generate INMPARA-compliant note
        frontmatter, main_content = FileUtils.extract_frontmatter(content)
        
        # If no frontmatter, create it
        if not frontmatter:
            frontmatter = await _generate_frontmatter_from_analysis(analysis, content)
        
        # Improve frontmatter with learned patterns
        improved_frontmatter = await _improve_frontmatter_with_patterns(frontmatter, analysis)
        
        # Create properly formatted note
        formatted_content = template_engine.create_note_content(
            title=improved_frontmatter.get("title", "Untitled"),
            content=main_content,
            frontmatter=improved_frontmatter
        )
        
        # Determine target location
        target_folder = improved_frontmatter.get("stage", "1-notes").replace("-", " - ").title()
        target_filename = f"{improved_frontmatter.get('created', datetime.now().strftime('%Y-%m-%d'))}-{improved_frontmatter.get('title', 'untitled').lower().replace(' ', '-')}.md"
        target_path = os.path.join(vault_path, target_folder, target_filename)
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Write formatted note
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Remove from inbox if auto_approve is True
        if auto_approve:
            os.remove(file_path)
            action = "moved"
        else:
            action = "copied"
        
        return {
            "success": True,
            "action": action,
            "target_path": target_path,
            "generated_frontmatter": improved_frontmatter,
            "message": f"Successfully {action} to {target_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to auto-process {file_path}"
        }

async def _generate_processing_suggestions(file_path: str, content: str, analysis: Dict, vault_path: str) -> Dict[str, Any]:
    """Generate processing suggestions for medium-confidence files"""
    try:
        # Generate suggested frontmatter
        suggested_frontmatter = await _generate_frontmatter_from_analysis(analysis, content)
        
        # Suggest multiple possible locations
        possible_locations = await _suggest_possible_locations(analysis, vault_path)
        
        # Get improvement suggestions from patterns
        pattern_suggestions = pattern_learner.get_suggested_improvements(analysis)
        
        return {
            "suggested_frontmatter": suggested_frontmatter,
            "possible_locations": possible_locations,
            "pattern_suggestions": pattern_suggestions,
            "content_preview": content[:300] + "..." if len(content) > 300 else content
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to generate suggestions for {file_path}"
        }

async def _log_inbox_processing_action(file_path: str, file_result: Dict, confidence: float):
    """Log inbox processing action to database"""
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT INTO processing_log 
                (action, source_path, destination_path, confidence, reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "process_inbox",
                file_path,
                file_result.get("target_path", ""),
                confidence,
                json.dumps(file_result.get("analysis", {}).to_dict() if hasattr(file_result.get("analysis", {}), "to_dict") else {}),
                datetime.now().isoformat()
            ))
    except Exception as e:
        logger.error(f"Error logging inbox processing action: {str(e)}")

async def _generate_frontmatter_from_analysis(analysis: Dict, content: str) -> Dict[str, Any]:
    """Generate INMPARA-compliant frontmatter from content analysis"""
    try:
        # Extract title from content or generate one
        lines = content.strip().split('\n')
        title = None
        for line in lines:
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                break
        
        if not title:
            # Generate title from analysis
            title = analysis.get('title_suggestion', 'Untitled Note')
        
        # Generate frontmatter based on analysis
        frontmatter = {
            "title": title,
            "type": "note",
            "tags": analysis.get('suggested_tags', ['uncategorized']),
            "created": datetime.now().strftime('%Y-%m-%d'),
            "updated": datetime.now().strftime('%Y-%m-%d'),
            "status": "active",
            "stage": "1-notes",
            "domain": analysis.get('domain', 'general'),
            "permalink": f"1-notes/{title.lower().replace(' ', '-').replace('/', '-')}"
        }
        
        return frontmatter
        
    except Exception as e:
        logger.error(f"Error generating frontmatter: {str(e)}")
        return {
            "title": "Untitled Note",
            "type": "note",
            "created": datetime.now().strftime('%Y-%m-%d'),
            "updated": datetime.now().strftime('%Y-%m-%d')
        }

# Additional helper functions would continue here...
# This file is getting long, so I'll create the remaining helpers in a separate file

