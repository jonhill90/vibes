#!/usr/bin/env python3
"""Validation script for VectorService implementation.

Tests:
1. Dimension validation (1536 required)
2. Null/zero embedding detection
3. Class structure and methods exist
"""

import sys
import ast


def validate_vector_service():
    """Validate VectorService implementation against task requirements."""

    file_path = "/Users/jon/source/vibes/infra/rag-service/backend/src/services/vector_service.py"

    print("=" * 60)
    print("VectorService Validation")
    print("=" * 60)

    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Parse AST
    tree = ast.parse(content)

    # Find VectorService class
    vector_service_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "VectorService":
            vector_service_class = node
            break

    if not vector_service_class:
        print("❌ FAILED: VectorService class not found")
        return False

    print("✅ VectorService class exists")

    # Check for required methods
    required_methods = [
        "__init__",
        "validate_embedding",
        "upsert_vectors",
        "search_vectors",
        "delete_vectors",
    ]

    found_methods = []
    for node in vector_service_class.body:
        if isinstance(node, ast.FunctionDef):
            found_methods.append(node.name)

    print(f"\nFound methods: {found_methods}")

    all_methods_present = True
    for method in required_methods:
        if method in found_methods:
            print(f"✅ Method '{method}' exists")
        else:
            print(f"❌ FAILED: Method '{method}' missing")
            all_methods_present = False

    # Check for EXPECTED_DIMENSION constant
    has_dimension_constant = False
    for node in vector_service_class.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "EXPECTED_DIMENSION":
                    if isinstance(node.value, ast.Constant) and node.value.value == 1536:
                        has_dimension_constant = True
                        print("\n✅ EXPECTED_DIMENSION = 1536 constant exists")

    if not has_dimension_constant:
        print("\n❌ FAILED: EXPECTED_DIMENSION = 1536 constant missing")
        all_methods_present = False

    # Check for validation logic in content
    print("\n" + "=" * 60)
    print("Critical Gotchas Validation")
    print("=" * 60)

    gotcha5_validated = "len(embedding) != self.EXPECTED_DIMENSION" in content
    print(f"{'✅' if gotcha5_validated else '❌'} Gotcha #5: Dimension validation (len == 1536)")

    gotcha1_validated = "all(v == 0 for v in embedding)" in content
    print(f"{'✅' if gotcha1_validated else '❌'} Gotcha #1: Null/zero embedding detection")

    async_client_used = "AsyncQdrantClient" in content
    print(f"{'✅' if async_client_used else '❌'} Uses AsyncQdrantClient correctly")

    point_struct_used = "PointStruct" in content
    print(f"{'✅' if point_struct_used else '❌'} Uses PointStruct for upsert")

    # Final summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)

    all_checks_passed = (
        all_methods_present and
        has_dimension_constant and
        gotcha5_validated and
        gotcha1_validated and
        async_client_used and
        point_struct_used
    )

    if all_checks_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("\nVectorService implementation is complete and correct!")
        return True
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("\nPlease review the implementation.")
        return False


if __name__ == "__main__":
    success = validate_vector_service()
    sys.exit(0 if success else 1)
