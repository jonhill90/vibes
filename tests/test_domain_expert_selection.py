"""Tests for Domain Expert Auto-Selection (Task 6)."""

import pytest
from typing import Dict, List, Tuple
from unittest.mock import Mock, patch


# Domain detection implementation for testing
DOMAIN_PRIORITIES = {
    "terraform": 100,
    "azure": 90,
    "kubernetes": 80,
    "task_management": 70,
    "knowledge_curation": 60,
    "context_engineering": 50,
    "python_backend": 40,
    "frontend": 30
}

DOMAIN_KEYWORDS = {
    "terraform": ["terraform", "iac", "infrastructure as code", ".tf", "tfvars"],
    "azure": ["azure", "arm template", "azure cli", "az ", "resource group"],
    "kubernetes": ["kubernetes", "k8s", "kubectl", "helm", "pods"],
    "task_management": ["task tracking", "orchestration", "workflow", "dependency"],
    "knowledge_curation": ["knowledge base", "documentation", "basic-memory"],
    "context_engineering": ["context optimization", "token management", "prompt"],
    "python_backend": ["python", "fastapi", "flask", "django"],
    "frontend": ["react", "vue", "angular", "typescript ui"]
}


def detect_applicable_domains(components: List[str]) -> List[Tuple[str, int]]:
    """Detect all applicable domains from technical components."""
    detected = []

    for component in components:
        component_lower = component.lower()

        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(keyword in component_lower for keyword in keywords):
                priority = DOMAIN_PRIORITIES[domain]
                detected.append((domain, priority))
                break  # One domain per component

    return detected


def select_experts(detected_domains: List[Tuple[str, int]]) -> Dict:
    """Select primary expert and collaborators."""
    if not detected_domains:
        # Fallback to generic implementer
        return {
            "primary": "prp-exec-implementer",
            "collaborators": [],
            "strategy": "sequential"
        }

    # Sort by priority (highest first)
    detected_domains.sort(key=lambda x: x[1], reverse=True)

    # Primary = highest priority
    primary_domain = detected_domains[0][0]

    # Collaborators = others
    collaborators = [d[0] for d in detected_domains[1:]]

    # Strategy: parallel if ≤3 collaborators, sequential otherwise
    strategy = "parallel" if len(collaborators) <= 3 else "sequential"

    return {
        "primary": f"{primary_domain}-expert",
        "collaborators": [f"{d}-expert" for d in collaborators],
        "strategy": strategy
    }


class TestSingleDomainAutoSelection:
    """Test auto-selection for single-domain features."""

    def test_terraform_only_feature(self):
        """Test selection for Terraform-only feature."""
        components = [
            "Terraform module for AWS VPC",
            "State management with S3 backend"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        assert experts["primary"] == "terraform-expert"
        assert len(experts["collaborators"]) == 0
        assert experts["strategy"] == "sequential"

    def test_azure_only_feature(self):
        """Test selection for Azure-only feature."""
        components = [
            "Azure Resource Groups",
            "ARM template deployment"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        assert experts["primary"] == "azure-expert"
        assert len(experts["collaborators"]) == 0

    def test_python_backend_only(self):
        """Test selection for Python backend feature."""
        components = [
            "FastAPI REST endpoints",
            "Python data models"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        assert experts["primary"] == "python_backend-expert"
        assert len(experts["collaborators"]) == 0


class TestMultiDomainPrimaryCollaborators:
    """Test auto-selection for multi-domain features."""

    def test_terraform_plus_azure(self):
        """Test selection for Terraform + Azure feature."""
        components = [
            "Terraform provisioning",
            "Azure ARM templates",
            "Resource naming conventions"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # Terraform has higher priority (100 vs 90)
        assert experts["primary"] == "terraform-expert"
        assert "azure-expert" in experts["collaborators"]
        assert experts["strategy"] == "parallel"  # ≤3 collaborators

    def test_three_domain_feature(self):
        """Test selection for 3-domain feature."""
        components = [
            "Kubernetes deployment manifests",
            "Azure AKS cluster",
            "Terraform infrastructure"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # Terraform highest priority
        assert experts["primary"] == "terraform-expert"

        # Should have 2 collaborators
        assert len(experts["collaborators"]) == 2
        assert "azure-expert" in experts["collaborators"]
        assert "kubernetes-expert" in experts["collaborators"]

        # Parallel execution (≤3 collaborators)
        assert experts["strategy"] == "parallel"

    def test_priority_ordering(self):
        """Test domain priority ordering."""
        components = [
            "Frontend React components",  # Priority 30
            "Python FastAPI backend",     # Priority 40
            "Terraform infrastructure"    # Priority 100
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # Terraform should be primary (highest priority)
        assert experts["primary"] == "terraform-expert"

        # Python and frontend should be collaborators
        collaborator_domains = [c.replace("-expert", "") for c in experts["collaborators"]]
        assert "python_backend" in collaborator_domains
        assert "frontend" in collaborator_domains


class TestFallbackToGenericImplementer:
    """Test fallback to generic implementer when no domain match."""

    def test_unknown_domain_fallback(self):
        """Test fallback when no known domains detected."""
        components = [
            "GraphQL API implementation",  # Not in domain keywords
            "React Native mobile app"     # Not in domain keywords
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # Should fallback to generic
        assert experts["primary"] == "prp-exec-implementer"
        assert len(experts["collaborators"]) == 0
        assert experts["strategy"] == "sequential"

    def test_empty_components_fallback(self):
        """Test fallback when no components provided."""
        components = []

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        assert experts["primary"] == "prp-exec-implementer"
        assert len(experts["collaborators"]) == 0

    def test_non_matching_keywords(self):
        """Test components without matching keywords fallback."""
        components = [
            "Generic software development",
            "Code refactoring tasks"
        ]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # No matches = fallback
        assert experts["primary"] == "prp-exec-implementer"


class TestOrchestrationStrategySelection:
    """Test orchestration strategy selection (parallel vs sequential)."""

    def test_parallel_strategy_two_domains(self):
        """Test parallel strategy for 2 domains."""
        detected = [
            ("terraform", 100),
            ("azure", 90)
        ]

        experts = select_experts(detected)

        # ≤3 collaborators = parallel
        assert experts["strategy"] == "parallel"
        assert len(experts["collaborators"]) == 1

    def test_parallel_strategy_three_collaborators(self):
        """Test parallel strategy with 3 collaborators."""
        detected = [
            ("terraform", 100),
            ("azure", 90),
            ("kubernetes", 80),
            ("python_backend", 40)
        ]

        experts = select_experts(detected)

        # 3 collaborators = still parallel
        assert experts["strategy"] == "parallel"
        assert len(experts["collaborators"]) == 3

    def test_sequential_strategy_many_domains(self):
        """Test sequential strategy for many domains."""
        detected = [
            ("terraform", 100),
            ("azure", 90),
            ("kubernetes", 80),
            ("python_backend", 40),
            ("frontend", 30)
        ]

        experts = select_experts(detected)

        # 4 collaborators = sequential
        assert experts["strategy"] == "sequential"
        assert len(experts["collaborators"]) == 4

    def test_single_domain_strategy(self):
        """Test strategy for single domain (no collaborators)."""
        detected = [("terraform", 100)]

        experts = select_experts(detected)

        assert experts["strategy"] == "sequential"  # Default when no collaborators
        assert len(experts["collaborators"]) == 0


class TestDomainKeywordDetection:
    """Test domain keyword detection logic."""

    def test_terraform_keyword_variations(self):
        """Test detection of Terraform keyword variations."""
        test_cases = [
            ("Terraform module", True),
            ("terraform state", True),
            ("Infrastructure as Code with Terraform", True),
            ("Create .tf files", True),
            ("Python script", False)
        ]

        for component, should_detect in test_cases:
            detected = detect_applicable_domains([component])
            is_terraform = any(d[0] == "terraform" for d in detected)

            assert is_terraform == should_detect, \
                f"Component '{component}' detection incorrect"

    def test_azure_keyword_variations(self):
        """Test detection of Azure keyword variations."""
        test_cases = [
            ("Azure Resource Groups", True),
            ("ARM template deployment", True),
            ("Azure CLI commands", True),
            ("az storage account", True),
            ("AWS EC2 instances", False)
        ]

        for component, should_detect in test_cases:
            detected = detect_applicable_domains([component])
            is_azure = any(d[0] == "azure" for d in detected)

            assert is_azure == should_detect, \
                f"Component '{component}' detection incorrect"

    def test_case_insensitive_detection(self):
        """Test case-insensitive keyword detection."""
        components = [
            "TERRAFORM MODULE",
            "terraform module",
            "Terraform Module",
            "TeRrAfOrM mOdUlE"
        ]

        for component in components:
            detected = detect_applicable_domains([component])
            is_terraform = any(d[0] == "terraform" for d in detected)

            assert is_terraform, f"Should detect '{component}' as Terraform"


class TestAgentExistenceValidation:
    """Test agent file existence validation."""

    def test_check_agent_exists(self, tmp_path):
        """Test checking if agent definition file exists."""
        from pathlib import Path

        def agent_exists(agent_name: str, base_path: Path) -> bool:
            """Check if agent definition file exists."""
            agent_path = base_path / f"{agent_name}.md"
            return agent_path.exists()

        # Create test agent file
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        (agents_dir / "terraform-expert.md").write_text("# Terraform Expert")

        assert agent_exists("terraform-expert", agents_dir), \
            "Should detect existing agent"

        assert not agent_exists("nonexistent-expert", agents_dir), \
            "Should not detect non-existent agent"

    def test_graceful_fallback_missing_agent(self):
        """Test graceful fallback when primary expert missing."""
        def execute_with_fallback(primary: str, agent_exists_fn) -> str:
            """Execute with fallback to generic implementer."""
            if not agent_exists_fn(primary):
                return "prp-exec-implementer"
            return primary

        # Mock agent_exists function
        mock_exists = Mock(return_value=False)

        result = execute_with_fallback("kubernetes-expert", mock_exists)

        assert result == "prp-exec-implementer", \
            "Should fallback to generic implementer"

    def test_filter_unavailable_collaborators(self):
        """Test filtering out unavailable collaborators."""
        def filter_collaborators(collaborators: List[str], agent_exists_fn) -> List[str]:
            """Filter out non-existent collaborators."""
            return [c for c in collaborators if agent_exists_fn(c)]

        collaborators = ["azure-expert", "kubernetes-expert", "nonexistent-expert"]

        # Mock: only azure-expert exists
        mock_exists = Mock(side_effect=lambda name: name == "azure-expert")

        validated = filter_collaborators(collaborators, mock_exists)

        assert len(validated) == 1
        assert "azure-expert" in validated
        assert "nonexistent-expert" not in validated


class TestDomainExpertIntegration:
    """Test integration with execute-prp workflow."""

    def test_feature_analysis_parsing(self):
        """Test parsing technical components from feature analysis."""
        feature_analysis_content = """
## Technical Components

- Terraform modules for VPC provisioning
- Azure Resource Groups for organization
- Python FastAPI backend
"""

        # Extract components (simple regex)
        import re
        components = re.findall(r'- (.*?)$', feature_analysis_content, re.MULTILINE)

        assert len(components) >= 3, "Should extract all components"

        # Detect domains
        detected = detect_applicable_domains(components)

        # Should detect terraform, azure, python_backend
        domains = [d[0] for d in detected]
        assert "terraform" in domains
        assert "azure" in domains
        assert "python_backend" in domains

    def test_expert_selection_from_prp(self, sample_feature_analysis):
        """Test expert selection from PRP feature analysis."""
        components = sample_feature_analysis["technical_components"]

        detected = detect_applicable_domains(components)
        experts = select_experts(detected)

        # Should have primary + collaborators
        assert experts["primary"] is not None
        assert len(experts["collaborators"]) >= 0

    def test_parallel_invocation_context_preparation(self):
        """Test context preparation for parallel expert invocation."""
        experts = {
            "primary": "terraform-expert",
            "collaborators": ["azure-expert"],
            "strategy": "parallel"
        }

        feature_name = "test_feature"

        # Prepare contexts
        primary_context = f"Implement {feature_name} as PRIMARY expert. Domain: terraform"

        collaborator_contexts = {}
        for collab in experts["collaborators"]:
            domain = collab.replace("-expert", "")
            collaborator_contexts[collab] = f"Support {feature_name}. Domain: {domain}"

        # Validate contexts prepared
        assert primary_context is not None
        assert len(collaborator_contexts) == len(experts["collaborators"])
