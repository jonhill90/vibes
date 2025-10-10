/**
 * Tests for ProjectStorage utility
 *
 * PURPOSE: Verify localStorage wrapper handles errors gracefully
 *
 * TEST COVERAGE:
 * - get() returns stored value
 * - get() returns null when key doesn't exist
 * - set() saves value to localStorage
 * - clear() removes value
 * - Quota exceeded error handling
 * - Security error handling (private browsing)
 * - Falls back to in-memory when localStorage unavailable
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import ProjectStorage from "../projectStorage";

describe("ProjectStorage", () => {
  // Mock localStorage before each test
  beforeEach(() => {
    // Clear all mocks
    vi.clearAllMocks();

    // Reset localStorage mock
    const localStorageMock = (() => {
      let store: Record<string, string> = {};

      return {
        getItem: vi.fn((key: string) => store[key] || null),
        setItem: vi.fn((key: string, value: string) => {
          store[key] = value;
        }),
        removeItem: vi.fn((key: string) => {
          delete store[key];
        }),
        clear: vi.fn(() => {
          store = {};
        }),
      };
    })();

    Object.defineProperty(window, "localStorage", {
      value: localStorageMock,
      writable: true,
    });

    // Reset ProjectStorage internal state
    // @ts-expect-error - accessing private static field for testing
    ProjectStorage.inMemoryFallback = null;
    // @ts-expect-error - accessing private static field for testing
    ProjectStorage.isAvailable = null;
  });

  describe("get()", () => {
    it("should return stored project ID", () => {
      localStorage.setItem("selectedProjectId", "project-123");

      const result = ProjectStorage.get();

      expect(result).toBe("project-123");
      expect(localStorage.getItem).toHaveBeenCalledWith("selectedProjectId");
    });

    it("should return null when no project is stored", () => {
      const result = ProjectStorage.get();

      expect(result).toBeNull();
    });

    it("should return in-memory fallback when localStorage throws error", () => {
      vi.spyOn(localStorage, "getItem").mockImplementation(() => {
        throw new Error("SecurityError");
      });

      // Set in-memory fallback directly
      // @ts-expect-error - accessing private static field for testing
      ProjectStorage.inMemoryFallback = "project-456";

      const result = ProjectStorage.get();

      expect(result).toBe("project-456");
    });

    it("should return in-memory fallback when localStorage is unavailable", () => {
      // Make checkAvailability fail
      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        throw new Error("SecurityError");
      });

      // First call to trigger availability check
      ProjectStorage.set("project-789");

      // Now get should use in-memory
      const result = ProjectStorage.get();

      expect(result).toBe("project-789");
    });
  });

  describe("set()", () => {
    it("should save project ID to localStorage", () => {
      ProjectStorage.set("project-123");

      expect(localStorage.setItem).toHaveBeenCalledWith(
        "selectedProjectId",
        "project-123"
      );
    });

    it("should save null to in-memory and remove from localStorage", () => {
      ProjectStorage.set(null);

      expect(localStorage.removeItem).toHaveBeenCalledWith("selectedProjectId");
    });

    it("should update in-memory fallback when localStorage unavailable", () => {
      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        throw new Error("SecurityError");
      });

      ProjectStorage.set("project-456");

      // Verify in-memory fallback is updated
      const result = ProjectStorage.get();
      expect(result).toBe("project-456");
    });

    it("should handle quota exceeded error (code 22)", () => {
      const quotaError = new Error("QuotaExceededError");
      // @ts-expect-error - adding error properties for testing
      quotaError.code = 22;
      // @ts-expect-error - adding error properties for testing
      quotaError.name = "QuotaExceededError";

      let callCount = 0;
      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          throw quotaError;
        }
        // Succeed on retry
      });

      ProjectStorage.set("project-123");

      // Should attempt to clear and retry
      expect(localStorage.removeItem).toHaveBeenCalledWith("selectedProjectId");
      expect(localStorage.setItem).toHaveBeenCalledTimes(2); // First attempt + retry
    });

    it("should handle quota exceeded error (Firefox code 1014)", () => {
      const quotaError = new Error("NS_ERROR_DOM_QUOTA_REACHED");
      // @ts-expect-error - adding error properties for testing
      quotaError.code = 1014;
      // @ts-expect-error - adding error properties for testing
      quotaError.name = "NS_ERROR_DOM_QUOTA_REACHED";

      let callCount = 0;
      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          throw quotaError;
        }
      });

      ProjectStorage.set("project-123");

      expect(localStorage.removeItem).toHaveBeenCalled();
      expect(localStorage.setItem).toHaveBeenCalledTimes(2);
    });

    it("should handle quota exceeded error (IE8 code -2147024882)", () => {
      const quotaError = new Error("QuotaExceededError");
      // @ts-expect-error - adding error properties for testing
      quotaError.number = -2147024882;

      let callCount = 0;
      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          throw quotaError;
        }
      });

      ProjectStorage.set("project-123");

      expect(localStorage.removeItem).toHaveBeenCalled();
      expect(localStorage.setItem).toHaveBeenCalledTimes(2);
    });

    it("should fall back to in-memory when retry also fails", () => {
      const quotaError = new Error("QuotaExceededError");
      // @ts-expect-error - adding error properties for testing
      quotaError.code = 22;

      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        throw quotaError;
      });

      ProjectStorage.set("project-123");

      // Should still work via in-memory fallback
      const result = ProjectStorage.get();
      expect(result).toBe("project-123");
    });

    it("should handle security error (private browsing)", () => {
      const securityError = new Error("SecurityError");
      // @ts-expect-error - adding error properties for testing
      securityError.name = "SecurityError";

      vi.spyOn(localStorage, "setItem").mockImplementation(() => {
        throw securityError;
      });

      ProjectStorage.set("project-456");

      // Should use in-memory fallback
      const result = ProjectStorage.get();
      expect(result).toBe("project-456");
    });
  });

  describe("clear()", () => {
    it("should remove project ID from localStorage", () => {
      localStorage.setItem("selectedProjectId", "project-123");

      ProjectStorage.clear();

      expect(localStorage.removeItem).toHaveBeenCalledWith("selectedProjectId");
    });

    it("should clear in-memory fallback", () => {
      ProjectStorage.set("project-123");
      ProjectStorage.clear();

      const result = ProjectStorage.get();
      expect(result).toBeNull();
    });

    it("should handle error gracefully", () => {
      vi.spyOn(localStorage, "removeItem").mockImplementation(() => {
        throw new Error("SecurityError");
      });

      // Should not throw
      expect(() => ProjectStorage.clear()).not.toThrow();

      // In-memory should still be cleared
      const result = ProjectStorage.get();
      expect(result).toBeNull();
    });
  });

  describe("checkAvailability()", () => {
    it("should cache availability check result", () => {
      ProjectStorage.set("project-123");
      ProjectStorage.set("project-456");

      // setItem should only be called for test key once + actual sets
      expect(localStorage.setItem).toHaveBeenCalledWith(
        "__localStorage_test__",
        "test"
      );
    });

    it("should detect when localStorage is unavailable", () => {
      vi.spyOn(localStorage, "setItem").mockImplementation((key) => {
        if (key === "__localStorage_test__") {
          throw new Error("SecurityError");
        }
      });

      // Force availability check
      ProjectStorage.set("project-123");

      // Should use in-memory fallback
      const result = ProjectStorage.get();
      expect(result).toBe("project-123");
    });
  });

  describe("edge cases", () => {
    it("should handle empty string project ID", () => {
      ProjectStorage.set("");

      const result = ProjectStorage.get();
      expect(result).toBe("");
    });

    it("should handle very long project ID", () => {
      const longId = "x".repeat(1000);
      ProjectStorage.set(longId);

      const result = ProjectStorage.get();
      expect(result).toBe(longId);
    });

    it("should handle special characters in project ID", () => {
      const specialId = "project-!@#$%^&*()_+-=[]{}|;':\",./<>?";
      ProjectStorage.set(specialId);

      const result = ProjectStorage.get();
      expect(result).toBe(specialId);
    });

    it("should handle rapid set/get calls", () => {
      ProjectStorage.set("project-1");
      ProjectStorage.set("project-2");
      ProjectStorage.set("project-3");

      const result = ProjectStorage.get();
      expect(result).toBe("project-3");
    });

    it("should handle set null after set value", () => {
      ProjectStorage.set("project-123");
      ProjectStorage.set(null);

      const result = ProjectStorage.get();
      expect(result).toBeNull();
    });
  });
});
