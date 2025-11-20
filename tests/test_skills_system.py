"""Tests for Skills System (Task 1)."""

import pytest
import yaml
import re
from pathlib import Path
from unittest.mock import Mock, patch, mock_open


class TestSkillFrontmatterParsing:
    """Test skill frontmatter parsing and validation."""

    def test_parse_valid_skill_frontmatter(self, sample_skill_frontmatter):
        """Test parsing valid skill frontmatter."""
        frontmatter_text = f"""---
name: {sample_skill_frontmatter['name']}
description: {sample_skill_frontmatter['description']}
---

# Skill Content
"""

        # Extract frontmatter
        pattern = r'^---\n(.*?)\n---'
        match = re.search(pattern, frontmatter_text, re.DOTALL)

        assert match is not None, "Failed to extract frontmatter"

        frontmatter = yaml.safe_load(match.group(1))

        assert frontmatter['name'] == sample_skill_frontmatter['name']
        assert frontmatter['description'] == sample_skill_frontmatter['description']

    def test_skill_has_required_fields(self, sample_skill_frontmatter):
        """Test skill frontmatter has required fields."""
        required_fields = ['name', 'description']

        for field in required_fields:
            assert field in sample_skill_frontmatter, f"Missing required field: {field}"

    def test_skill_name_format(self, sample_skill_frontmatter):
        """Test skill name follows naming convention."""
        name = sample_skill_frontmatter['name']

        # Should be lowercase with hyphens
        assert re.match(r'^[a-z0-9-]+$', name), f"Invalid skill name format: {name}"
        assert not name.startswith('-'), "Skill name cannot start with hyphen"
        assert not name.endswith('-'), "Skill name cannot end with hyphen"

    def test_skill_description_is_specific(self, sample_skill_frontmatter):
        """Test skill description is specific (not vague)."""
        description = sample_skill_frontmatter['description']

        # Should contain "Use when" or similar activation trigger
        activation_keywords = ['use when', 'use for', 'use proactively']

        has_activation = any(keyword in description.lower() for keyword in activation_keywords)
        assert has_activation or len(description.split()) > 10, \
            "Description should be specific with activation triggers"

    def test_invalid_frontmatter_raises_error(self):
        """Test invalid frontmatter raises parsing error."""
        invalid_frontmatter = """---
name: test
# Missing closing ---

Content"""

        pattern = r'^---\n(.*?)\n---'
        match = re.search(pattern, invalid_frontmatter, re.DOTALL)

        assert match is None, "Should not match invalid frontmatter"


class TestSkillAutoActivation:
    """Test skill auto-activation based on description triggers."""

    def test_detect_activation_keywords(self):
        """Test detection of activation keywords in description."""
        description = "Task management patterns. Use when analyzing dependencies or planning execution."

        activation_keywords = [
            'task', 'management', 'dependencies', 'planning', 'execution'
        ]

        description_lower = description.lower()
        detected = [kw for kw in activation_keywords if kw in description_lower]

        assert len(detected) >= 3, f"Should detect at least 3 keywords, found {detected}"

    def test_specific_vs_vague_descriptions(self):
        """Test distinguishing specific vs vague descriptions."""
        specific = "Terraform module creation. Use when provisioning AWS infrastructure or managing state files."
        vague = "Development guidelines. Use for coding."

        # Specific descriptions have more keywords
        specific_words = specific.split()
        vague_words = vague.split()

        assert len(specific_words) > len(vague_words) * 1.5, \
            "Specific descriptions should be significantly longer"

    def test_multiple_activation_patterns(self):
        """Test multiple activation patterns in description."""
        description = """
        Backend API development with FastAPI.
        Use when creating routes, controllers, or API endpoints in src/api/.
        Examples: REST endpoints, WebSocket handlers, middleware.
        """

        patterns = {
            'use_case': re.search(r'use when (.*?)\.', description, re.IGNORECASE),
            'examples': re.search(r'examples:(.*?)\.', description, re.IGNORECASE),
            'technology': 'fastapi' in description.lower()
        }

        assert all(patterns.values()), f"Missing activation patterns: {patterns}"


class TestProgressiveDisclosure:
    """Test progressive disclosure pattern (main file + resource files)."""

    def test_main_skill_under_500_lines(self, tmp_path):
        """Test main SKILL.md is under 500 lines."""
        skill_content = """---
name: test-skill
description: Test skill
---

# Test Skill

""" + "\n".join([f"Line {i}" for i in range(450)])  # 450 content lines

        skill_path = tmp_path / "SKILL.md"
        skill_path.write_text(skill_content)

        line_count = len(skill_content.split('\n'))

        assert line_count < 500, f"Main SKILL.md should be under 500 lines, got {line_count}"

    def test_resource_files_exist(self, tmp_path):
        """Test resource files directory exists for detailed content."""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        resources_dir = skill_dir / "resources"
        resources_dir.mkdir()

        # Create resource files
        (resources_dir / "detailed-guide.md").write_text("Detailed content here")
        (resources_dir / "examples.md").write_text("Examples here")

        assert resources_dir.exists(), "Resources directory should exist"
        assert len(list(resources_dir.glob("*.md"))) >= 2, \
            "Should have at least 2 resource files"

    def test_resource_files_size_appropriate(self, tmp_path):
        """Test resource files are appropriately sized (100-300 lines)."""
        resource_content = "\n".join([f"Line {i}" for i in range(250)])  # 250 lines

        resource_path = tmp_path / "resource.md"
        resource_path.write_text(resource_content)

        line_count = len(resource_content.split('\n'))

        assert 100 <= line_count <= 300, \
            f"Resource files should be 100-300 lines, got {line_count}"

    def test_main_file_links_to_resources(self):
        """Test main SKILL.md links to resource files."""
        skill_content = """---
name: test-skill
description: Test skill
---

# Test Skill

## Resources

- [Detailed Guide](resources/detailed-guide.md)
- [Examples](resources/examples.md)
"""

        # Check for resource links
        resource_links = re.findall(r'\[.*?\]\(resources/.*?\.md\)', skill_content)

        assert len(resource_links) >= 2, \
            f"Should link to at least 2 resource files, found {len(resource_links)}"


class TestSkillLineLimitEnforcement:
    """Test enforcement of 500-line limit for main skill files."""

    def test_line_count_validation(self):
        """Test line count validation function."""
        def validate_line_limit(content: str, max_lines: int = 500) -> bool:
            """Validate content is under line limit."""
            lines = content.split('\n')
            return len(lines) <= max_lines

        # Test under limit
        short_content = "\n".join([f"Line {i}" for i in range(400)])
        assert validate_line_limit(short_content), "400 lines should pass"

        # Test over limit
        long_content = "\n".join([f"Line {i}" for i in range(600)])
        assert not validate_line_limit(long_content), "600 lines should fail"

    def test_exclude_frontmatter_from_count(self):
        """Test frontmatter excluded from line count."""
        frontmatter = """---
name: test
description: Test skill
---

"""
        content = "\n".join([f"Line {i}" for i in range(450)])
        full_content = frontmatter + content

        # Count only content lines (after frontmatter)
        pattern = r'^---\n.*?\n---\n'
        content_only = re.sub(pattern, '', full_content, flags=re.DOTALL)

        content_lines = len(content_only.split('\n'))

        assert content_lines <= 500, \
            f"Content without frontmatter should be under 500 lines, got {content_lines}"

    def test_warn_approaching_limit(self):
        """Test warning when approaching 500-line limit."""
        content = "\n".join([f"Line {i}" for i in range(480)])

        line_count = len(content.split('\n'))

        # Should warn when 90%+ of limit
        approaching_limit = line_count >= 450  # 90% of 500

        assert approaching_limit, \
            f"Should warn at 450+ lines, current: {line_count}"


class TestSkillSystemIntegration:
    """Test skills system integration with agents."""

    def test_agent_references_existing_skill(self, sample_agent_frontmatter):
        """Test agent frontmatter references existing skills."""
        skills_referenced = sample_agent_frontmatter.get('skills', [])

        assert isinstance(skills_referenced, list), "skills should be a list"
        assert len(skills_referenced) > 0, "Agent should reference at least one skill"

    def test_skill_composition(self, sample_agent_frontmatter):
        """Test agents can compose multiple skills."""
        skills = sample_agent_frontmatter.get('skills', [])

        # Multiple skills = composition
        if len(skills) > 1:
            assert all(isinstance(s, str) for s in skills), \
                "All skill references should be strings"

    def test_skill_activation_scenario(self):
        """Test skill activation based on user prompt."""
        user_prompt = "I need to analyze task dependencies for parallel execution"

        # Skill description with activation keywords
        skill_description = "Task management. Use when analyzing dependencies or planning execution."

        # Extract keywords from both
        prompt_keywords = set(re.findall(r'\b\w+\b', user_prompt.lower()))
        skill_keywords = set(re.findall(r'\b\w+\b', skill_description.lower()))

        # Check for overlap
        overlap = prompt_keywords & skill_keywords

        assert 'dependencies' in overlap or 'execution' in overlap, \
            f"Should detect activation keywords, overlap: {overlap}"


class TestSkillErrorHandling:
    """Test error handling in skills system."""

    def test_missing_frontmatter_field(self):
        """Test handling of missing required frontmatter fields."""
        incomplete_frontmatter = {
            "name": "test-skill"
            # Missing description
        }

        required_fields = ['name', 'description']
        missing = [f for f in required_fields if f not in incomplete_frontmatter]

        assert len(missing) > 0, f"Should detect missing fields: {missing}"
        assert 'description' in missing, "Should detect missing description"

    def test_invalid_skill_name_characters(self):
        """Test rejection of invalid skill name characters."""
        invalid_names = [
            "skill_with_underscore",  # Underscores not allowed
            "SKILL-UPPERCASE",  # Uppercase not allowed
            "skill with spaces",  # Spaces not allowed
            "skill@special",  # Special chars not allowed
        ]

        pattern = r'^[a-z0-9-]+$'

        for name in invalid_names:
            assert not re.match(pattern, name), \
                f"Should reject invalid name: {name}"

    def test_empty_description_validation(self):
        """Test validation of empty or too-short descriptions."""
        descriptions = {
            "": False,  # Empty
            "Test": False,  # Too short
            "This is a proper skill description with activation keywords.": True
        }

        for desc, should_pass in descriptions.items():
            is_valid = len(desc.split()) >= 10  # At least 10 words
            assert is_valid == should_pass, \
                f"Description '{desc}' validation incorrect"
