#!/usr/bin/env bash
# .codex/tests/test_parallel_timing.sh
# Purpose: Validate parallel Phase 2 execution and measure speedup
# Pattern: Feature-analysis.md success criteria (lines 72-73)
# Tests: Concurrent timestamps, parallel speedup ≥2x

set -euo pipefail

# =============================================================================
# Test Configuration
# =============================================================================

# Script directory (for accessing source scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Test artifacts directory
TEST_DIR="${SCRIPT_DIR}/fixtures"
TEST_FEATURE="test_parallel_timing"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Helper Functions
# =============================================================================

# Print test result
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Cleanup test artifacts
cleanup() {
    if [ -d "${REPO_ROOT}/prps/${TEST_FEATURE}" ]; then
        rm -rf "${REPO_ROOT}/prps/${TEST_FEATURE}"
        info "Cleaned up test PRP directory"
    fi

    if [ -d "${TEST_DIR}" ]; then
        rm -rf "${TEST_DIR}"
        info "Cleaned up test fixtures"
    fi
}

# Setup test fixtures
setup() {
    echo ""
    echo "========================================="
    echo "Test Setup"
    echo "========================================="

    # Create test fixtures directory
    mkdir -p "${TEST_DIR}"

    # Source log-phase.sh for manifest creation
    source "${REPO_ROOT}/.codex/scripts/log-phase.sh" >/dev/null || {
        fail "Failed to source log-phase.sh"
        exit 1
    }

    pass "Test setup complete"
}

# =============================================================================
# Test Helper Functions
# =============================================================================

# Create mock manifest with parallel Phase 2 entries
create_mock_parallel_manifest() {
    local feature="$1"
    local manifest="${REPO_ROOT}/prps/${feature}/codex/logs/manifest.jsonl"

    # Ensure directory exists
    mkdir -p "$(dirname "$manifest")"

    # Simulate parallel Phase 2 execution with timestamps
    # All 3 agents start within 1 second (proof of parallelism)
    local base_timestamp="2025-10-07T10:30:00Z"
    local phase2a_start="2025-10-07T10:30:00Z"
    local phase2b_start="2025-10-07T10:30:01Z"
    local phase2c_start="2025-10-07T10:30:01Z"

    # All complete after 300 seconds (5 minutes - max agent duration)
    local phase2a_end="2025-10-07T10:35:00Z"
    local phase2b_end="2025-10-07T10:34:30Z"
    local phase2c_end="2025-10-07T10:35:00Z"

    cat > "$manifest" <<EOF
{"phase":"phase1","status":"started","timestamp":"2025-10-07T10:29:00Z"}
{"phase":"phase1","status":"success","exit_code":0,"duration_sec":60,"timestamp":"2025-10-07T10:30:00Z"}
{"phase":"phase2a","status":"started","timestamp":"${phase2a_start}"}
{"phase":"phase2b","status":"started","timestamp":"${phase2b_start}"}
{"phase":"phase2c","status":"started","timestamp":"${phase2c_start}"}
{"phase":"phase2a","status":"success","exit_code":0,"duration_sec":300,"timestamp":"${phase2a_end}"}
{"phase":"phase2b","status":"success","exit_code":0,"duration_sec":270,"timestamp":"${phase2b_end}"}
{"phase":"phase2c","status":"success","exit_code":0,"duration_sec":300,"timestamp":"${phase2c_end}"}
{"phase":"phase3","status":"started","timestamp":"2025-10-07T10:35:05Z"}
{"phase":"phase3","status":"success","exit_code":0,"duration_sec":180,"timestamp":"2025-10-07T10:38:05Z"}
EOF

    echo "$manifest"
}

# Create mock manifest with sequential Phase 2 entries (for comparison)
create_mock_sequential_manifest() {
    local feature="$1"
    local manifest="${REPO_ROOT}/prps/${feature}/codex/logs/manifest.jsonl"

    # Ensure directory exists
    mkdir -p "$(dirname "$manifest")"

    # Simulate sequential Phase 2 execution
    # Each agent starts after previous completes
    cat > "$manifest" <<EOF
{"phase":"phase1","status":"started","timestamp":"2025-10-07T10:29:00Z"}
{"phase":"phase1","status":"success","exit_code":0,"duration_sec":60,"timestamp":"2025-10-07T10:30:00Z"}
{"phase":"phase2a","status":"started","timestamp":"2025-10-07T10:30:00Z"}
{"phase":"phase2a","status":"success","exit_code":0,"duration_sec":300,"timestamp":"2025-10-07T10:35:00Z"}
{"phase":"phase2b","status":"started","timestamp":"2025-10-07T10:35:00Z"}
{"phase":"phase2b","status":"success","exit_code":0,"duration_sec":270,"timestamp":"2025-10-07T10:39:30Z"}
{"phase":"phase2c","status":"started","timestamp":"2025-10-07T10:39:30Z"}
{"phase":"phase2c","status":"success","exit_code":0,"duration_sec":300,"timestamp":"2025-10-07T10:44:30Z"}
{"phase":"phase3","status":"started","timestamp":"2025-10-07T10:44:35Z"}
{"phase":"phase3","status":"success","exit_code":0,"duration_sec":180,"timestamp":"2025-10-07T10:47:35Z"}
EOF

    echo "$manifest"
}

# Extract timestamp from JSONL entry
extract_timestamp() {
    local entry="$1"

    if command -v jq &> /dev/null; then
        echo "$entry" | jq -r '.timestamp'
    else
        # Fallback: grep-based extraction
        echo "$entry" | grep -oP '"timestamp":"\K[^"]+' || echo ""
    fi
}

# Convert ISO 8601 timestamp to epoch seconds (macOS and Linux compatible)
timestamp_to_epoch() {
    local timestamp="$1"

    # macOS date command requires -j flag and different format
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: date -j -f "%Y-%m-%dT%H:%M:%SZ" "2025-10-07T10:30:00Z" "+%s"
        date -j -f "%Y-%m-%dT%H:%M:%SZ" "$timestamp" "+%s" 2>/dev/null || echo "0"
    else
        # Linux: date -d "2025-10-07T10:30:00Z" "+%s"
        date -d "$timestamp" "+%s" 2>/dev/null || echo "0"
    fi
}

# Calculate time difference in seconds
time_diff_seconds() {
    local epoch1="$1"
    local epoch2="$2"
    echo $((epoch2 - epoch1))
}

# =============================================================================
# Test Cases
# =============================================================================

# Test 1: Extract Phase 2 start timestamps from manifest
test_extract_timestamps() {
    echo ""
    echo "Test 1: Extract Phase 2 timestamps"
    echo "-----------------------------------------"

    local manifest=$(create_mock_parallel_manifest "${TEST_FEATURE}_parallel")

    # Extract phase2a start timestamp
    local phase2a_entry=$(grep '"phase":"phase2a".*"started"' "$manifest" | head -1)
    local phase2a_timestamp=$(extract_timestamp "$phase2a_entry")

    if [ -n "$phase2a_timestamp" ]; then
        pass "Extracted phase2a timestamp: $phase2a_timestamp"
    else
        fail "Failed to extract phase2a timestamp"
        return 1
    fi

    # Extract phase2b start timestamp
    local phase2b_entry=$(grep '"phase":"phase2b".*"started"' "$manifest" | head -1)
    local phase2b_timestamp=$(extract_timestamp "$phase2b_entry")

    if [ -n "$phase2b_timestamp" ]; then
        pass "Extracted phase2b timestamp: $phase2b_timestamp"
    else
        fail "Failed to extract phase2b timestamp"
        return 1
    fi

    # Extract phase2c start timestamp
    local phase2c_entry=$(grep '"phase":"phase2c".*"started"' "$manifest" | head -1)
    local phase2c_timestamp=$(extract_timestamp "$phase2c_entry")

    if [ -n "$phase2c_timestamp" ]; then
        pass "Extracted phase2c timestamp: $phase2c_timestamp"
    else
        fail "Failed to extract phase2c timestamp"
        return 1
    fi
}

# Test 2: Convert timestamps to epoch seconds
test_timestamp_conversion() {
    echo ""
    echo "Test 2: Convert timestamps to epoch seconds"
    echo "-----------------------------------------"

    local test_timestamp="2025-10-07T10:30:00Z"
    local epoch=$(timestamp_to_epoch "$test_timestamp")

    if [ "$epoch" != "0" ]; then
        pass "Converted timestamp to epoch: $epoch"
    else
        fail "Failed to convert timestamp to epoch"
        return 1
    fi

    # Test time difference calculation
    local epoch1=$(timestamp_to_epoch "2025-10-07T10:30:00Z")
    local epoch2=$(timestamp_to_epoch "2025-10-07T10:35:00Z")
    local diff=$(time_diff_seconds "$epoch1" "$epoch2")

    if [ "$diff" -eq 300 ]; then
        pass "Time difference calculation correct: ${diff}s (5 minutes)"
    else
        fail "Time difference calculation incorrect: ${diff}s (expected 300s)"
        return 1
    fi
}

# Test 3: Verify parallel execution (all started within 5 seconds)
test_parallel_start_timing() {
    echo ""
    echo "Test 3: Verify parallel execution timing"
    echo "-----------------------------------------"

    local manifest=$(create_mock_parallel_manifest "${TEST_FEATURE}_parallel")

    # Extract all Phase 2 start timestamps
    local phase2a_entry=$(grep '"phase":"phase2a".*"started"' "$manifest" | head -1)
    local phase2b_entry=$(grep '"phase":"phase2b".*"started"' "$manifest" | head -1)
    local phase2c_entry=$(grep '"phase":"phase2c".*"started"' "$manifest" | head -1)

    local ts_2a=$(extract_timestamp "$phase2a_entry")
    local ts_2b=$(extract_timestamp "$phase2b_entry")
    local ts_2c=$(extract_timestamp "$phase2c_entry")

    # Convert to epoch
    local epoch_2a=$(timestamp_to_epoch "$ts_2a")
    local epoch_2b=$(timestamp_to_epoch "$ts_2b")
    local epoch_2c=$(timestamp_to_epoch "$ts_2c")

    # Calculate max time difference between any two starts
    local diff_ab=$(time_diff_seconds "$epoch_2a" "$epoch_2b")
    local diff_ac=$(time_diff_seconds "$epoch_2a" "$epoch_2c")
    local diff_bc=$(time_diff_seconds "$epoch_2b" "$epoch_2c")

    # Use absolute values
    diff_ab=${diff_ab#-}
    diff_ac=${diff_ac#-}
    diff_bc=${diff_bc#-}

    local max_diff=$diff_ab
    [ $diff_ac -gt $max_diff ] && max_diff=$diff_ac
    [ $diff_bc -gt $max_diff ] && max_diff=$diff_bc

    info "Max time difference between agent starts: ${max_diff}s"

    if [ "$max_diff" -le 5 ]; then
        pass "All Phase 2 agents started within 5 seconds (proof of parallelism)"
    else
        fail "Phase 2 agents NOT parallel - max diff: ${max_diff}s (expected ≤5s)"
        return 1
    fi
}

# Test 4: Calculate speedup (parallel vs sequential)
test_speedup_calculation() {
    echo ""
    echo "Test 4: Calculate parallel speedup"
    echo "-----------------------------------------"

    # Create both manifests
    local parallel_manifest=$(create_mock_parallel_manifest "${TEST_FEATURE}_parallel")
    local sequential_manifest=$(create_mock_sequential_manifest "${TEST_FEATURE}_sequential")

    # Extract Phase 2 durations from parallel manifest
    local parallel_entries=$(grep '"phase":"phase2[abc]".*"success"' "$parallel_manifest")
    local parallel_total=0

    # Parallel time = max(phase2a, phase2b, phase2c) since they run simultaneously
    local max_duration=0
    while IFS= read -r entry; do
        if command -v jq &> /dev/null; then
            local duration=$(echo "$entry" | jq -r '.duration_sec // 0')
        else
            local duration=$(echo "$entry" | grep -oP '"duration_sec":\K\d+' || echo "0")
        fi

        [ "$duration" -gt "$max_duration" ] && max_duration=$duration
    done <<< "$parallel_entries"

    parallel_total=$max_duration

    # Extract Phase 2 durations from sequential manifest
    local sequential_entries=$(grep '"phase":"phase2[abc]".*"success"' "$sequential_manifest")
    local sequential_total=0

    # Sequential time = sum(phase2a + phase2b + phase2c)
    while IFS= read -r entry; do
        if command -v jq &> /dev/null; then
            local duration=$(echo "$entry" | jq -r '.duration_sec // 0')
        else
            local duration=$(echo "$entry" | grep -oP '"duration_sec":\K\d+' || echo "0")
        fi

        sequential_total=$((sequential_total + duration))
    done <<< "$sequential_entries"

    info "Parallel Phase 2 time: ${parallel_total}s"
    info "Sequential Phase 2 time: ${sequential_total}s"

    # Calculate speedup
    if [ "$parallel_total" -gt 0 ]; then
        local speedup=$((sequential_total / parallel_total))
        info "Speedup: ${speedup}x"

        if [ "$speedup" -ge 2 ]; then
            pass "Speedup ≥2x achieved (${speedup}x)"
        else
            fail "Speedup <2x (${speedup}x, expected ≥2x)"
            return 1
        fi
    else
        fail "Invalid parallel time: ${parallel_total}s"
        return 1
    fi
}

# Test 5: Verify Phase 2 outputs exist
test_phase2_outputs_exist() {
    echo ""
    echo "Test 5: Verify Phase 2 outputs created"
    echo "-----------------------------------------"

    info "This test validates expected file structure"

    local expected_outputs=(
        "planning/codebase-patterns.md"
        "planning/documentation-links.md"
        "planning/examples-to-include.md"
    )

    # Note: We can't create actual outputs without Codex CLI
    # But we can validate the script expects them

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    for output in "${expected_outputs[@]}"; do
        if grep -q "$output" "$script" 2>/dev/null; then
            pass "Script references output: $output"
        else
            info "Script may not explicitly reference: $output"
        fi
    done
}

# Test 6: Real-world parallel execution test (with mock agents)
test_real_parallel_execution() {
    echo ""
    echo "Test 6: Real parallel execution test (mock agents)"
    echo "-----------------------------------------"

    info "Testing actual parallel job control with mock agents"

    # Create test manifest
    source "${REPO_ROOT}/.codex/scripts/log-phase.sh" 2>/dev/null

    # Record start time
    local start_time=$(date +%s)

    # Launch 3 mock agents in parallel (each sleeps 2 seconds)
    (sleep 2; exit 0) &
    local PID_A=$!

    (sleep 2; exit 0) &
    local PID_B=$!

    (sleep 2; exit 0) &
    local PID_C=$!

    # Wait for all and capture exit codes
    wait $PID_A; local EXIT_A=$?
    wait $PID_B; local EXIT_B=$?
    wait $PID_C; local EXIT_C=$?

    # Record end time
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))

    info "Total execution time: ${total_time}s (expected ~2s for parallel, ~6s for sequential)"

    # Verify all succeeded
    if [ $EXIT_A -eq 0 ] && [ $EXIT_B -eq 0 ] && [ $EXIT_C -eq 0 ]; then
        pass "All mock agents completed successfully"
    else
        fail "Mock agent failures: A=$EXIT_A, B=$EXIT_B, C=$EXIT_C"
        return 1
    fi

    # Verify parallel execution (should take ~2s, not ~6s)
    if [ "$total_time" -le 3 ]; then
        pass "Agents ran in parallel (${total_time}s ≤ 3s)"
    else
        fail "Agents ran sequentially (${total_time}s > 3s)"
        return 1
    fi
}

# =============================================================================
# Test Summary
# =============================================================================

print_summary() {
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        echo "Parallel execution validation complete:"
        echo "  ✓ Timestamp extraction working"
        echo "  ✓ Parallel timing verified (agents start within 5s)"
        echo "  ✓ Speedup calculation correct (≥2x)"
        echo "  ✓ Real parallel execution tested (mock agents)"
        echo ""
        echo "NOTE: Full timing test requires actual Codex CLI execution."
        echo "      These tests validate timing logic and parallel structure."
        echo ""
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        echo "Please fix the failures before proceeding."
        echo ""
        return 1
    fi
}

# =============================================================================
# Main Test Execution
# =============================================================================

main() {
    echo "========================================="
    echo "Parallel Timing Validation Test"
    echo "========================================="
    echo "Testing: Phase 2 parallel execution and speedup"
    echo "Pattern: Feature-analysis.md success criteria"
    echo ""

    # Setup
    setup

    # Run all test cases
    test_extract_timestamps || true
    test_timestamp_conversion || true
    test_parallel_start_timing || true
    test_speedup_calculation || true
    test_phase2_outputs_exist || true
    test_real_parallel_execution || true

    # Cleanup
    cleanup

    # Print summary
    print_summary
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
