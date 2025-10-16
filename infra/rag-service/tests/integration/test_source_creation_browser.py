#!/usr/bin/env python3
"""
Browser automation test for source creation validation.
Tests the fix for Task 2: Source Creation Validation Bug.
"""

import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def test_source_creation():
    """Test source creation flow with browser automation."""
    print("Starting browser validation test for source creation...")

    with sync_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to frontend
            print("Navigating to http://localhost:5173...")
            page.goto("http://localhost:5173", wait_until="networkidle")

            # Take initial snapshot
            print("\nInitial page snapshot:")
            print(page.content()[:500])

            # Wait for and click source management (if in tabs/navigation)
            # Try to find source creation form
            print("\nLooking for source creation form...")

            # Fill in the source creation form
            print("Filling source creation form...")

            # Fill title
            title_input = page.locator('input[id="title"]')
            if title_input.count() > 0:
                print("  - Found title input")
                title_input.fill("Browser Test Source")
            else:
                print("  - WARNING: Title input not found")

            # Select source type
            type_select = page.locator('select[id="source_type"]')
            if type_select.count() > 0:
                print("  - Found source_type select")
                type_select.select_option("upload")
            else:
                print("  - WARNING: source_type select not found")

            # Click create button
            create_button = page.locator('button:has-text("Create Source")')
            if create_button.count() > 0:
                print("  - Found Create Source button")
                create_button.click()

                # Wait for success (either a success message or source appears in table)
                print("\nWaiting for source creation to complete...")
                time.sleep(2)  # Give it time to complete

                # Check if source appears in table
                page_content = page.content()
                if "Browser Test Source" in page_content:
                    print("✅ SUCCESS: Source created and visible in UI")
                    print("✅ Source creation validation FIXED")
                    return True
                elif "Browser Test" in page_content:
                    print("✅ SUCCESS: Source created (partial match found)")
                    return True
                else:
                    # Check for error messages
                    if "error" in page_content.lower() or "failed" in page_content.lower():
                        print("❌ FAILED: Error message detected in UI")
                        print("Page content snippet:", page_content[1000:2000])
                    else:
                        print("⚠️  UNCERTAIN: Source created but not visible yet (may need refresh)")
                        print("Checking backend API...")

                        # Verify via backend API
                        import requests
                        response = requests.get("http://localhost:8003/api/sources")
                        if response.status_code == 200:
                            sources = response.json()
                            if any("Browser Test Source" in str(s.get("title", "")) for s in sources.get("sources", [])):
                                print("✅ SUCCESS: Source found in backend API")
                                return True
                    return False
            else:
                print("❌ FAILED: Create Source button not found")
                return False

        except PlaywrightTimeout as e:
            print(f"❌ FAILED: Timeout - {e}")
            return False
        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Take screenshot for debugging
            try:
                screenshot_path = "/Users/jon/source/vibes/infra/rag-service/source_creation_test.png"
                page.screenshot(path=screenshot_path)
                print(f"\nScreenshot saved to: {screenshot_path}")
            except:
                pass

            browser.close()


if __name__ == "__main__":
    success = test_source_creation()
    sys.exit(0 if success else 1)
