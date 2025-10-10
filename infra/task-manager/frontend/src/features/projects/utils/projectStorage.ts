/**
 * ProjectStorage - Type-safe localStorage wrapper for project selection persistence
 *
 * Handles localStorage quota exceeded, security errors (private browsing),
 * and browser compatibility issues with graceful fallback to in-memory storage.
 *
 * Key features:
 * - Cross-browser quota detection (error codes 22, 1014, -2147024882)
 * - In-memory fallback when localStorage unavailable
 * - Automatic retry after clearing storage on quota exceeded
 * - Comprehensive error handling prevents app crashes
 *
 * @example
 * // Save selected project
 * ProjectStorage.set('project-123');
 *
 * // Retrieve selected project
 * const projectId = ProjectStorage.get(); // Returns 'project-123' or null
 *
 * // Clear selection
 * ProjectStorage.clear();
 */
class ProjectStorage {
  private static readonly KEY = 'selectedProjectId';
  private static inMemoryFallback: string | null = null;
  private static isAvailable: boolean | null = null;

  /**
   * Check if localStorage is available and accessible
   *
   * Handles:
   * - SecurityError in private browsing mode (Safari)
   * - DOMException when cookies disabled
   * - QuotaExceededError in restricted environments
   *
   * @returns true if localStorage is available, false otherwise
   */
  private static checkAvailability(): boolean {
    // Return cached result if already checked
    if (this.isAvailable !== null) {
      return this.isAvailable;
    }

    try {
      const testKey = '__localStorage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      this.isAvailable = true;
      return true;
    } catch (e) {
      console.warn(
        'localStorage not available, using in-memory fallback',
        e
      );
      this.isAvailable = false;
      return false;
    }
  }

  /**
   * Cross-browser quota exceeded detection
   *
   * Different browsers use different error codes:
   * - Standard: code 22, name 'QuotaExceededError'
   * - Firefox: code 1014, name 'NS_ERROR_DOM_QUOTA_REACHED'
   * - Internet Explorer 8: number -2147024882
   *
   * @param e - Error object from localStorage operation
   * @returns true if error is quota exceeded, false otherwise
   */
  private static isQuotaExceeded(e: any): boolean {
    if (!e) return false;

    // Check for error code (most browsers)
    if (e.code) {
      switch (e.code) {
        case 22: // Standard quota exceeded
          return true;
        case 1014: // Firefox
          return e.name === 'NS_ERROR_DOM_QUOTA_REACHED';
      }
    }

    // Internet Explorer 8
    if (e.number === -2147024882) {
      return true;
    }

    // Check error name (some browsers)
    return e.name === 'QuotaExceededError';
  }

  /**
   * Get selected project ID from localStorage with error handling
   *
   * Falls back to in-memory storage if localStorage is unavailable.
   * Returns null if no project is selected or on any error.
   *
   * @returns Selected project ID or null
   */
  static get(): string | null {
    if (!this.checkAvailability()) {
      return this.inMemoryFallback;
    }

    try {
      return localStorage.getItem(this.KEY);
    } catch (e) {
      console.error('Failed to read from localStorage:', e);
      return this.inMemoryFallback;
    }
  }

  /**
   * Set selected project ID with quota handling
   *
   * Updates in-memory fallback first (always succeeds), then attempts
   * localStorage write. If quota exceeded, clears old data and retries.
   *
   * @param projectId - Project ID to save, or null to clear
   */
  static set(projectId: string | null): void {
    // Update in-memory fallback first (always succeeds)
    this.inMemoryFallback = projectId;

    if (!this.checkAvailability()) {
      return; // Gracefully degrade to in-memory only
    }

    try {
      if (projectId === null) {
        localStorage.removeItem(this.KEY);
      } else {
        localStorage.setItem(this.KEY, projectId);
      }
    } catch (e) {
      if (this.isQuotaExceeded(e)) {
        console.warn(
          'localStorage quota exceeded, clearing old data and retrying'
        );
        // Try to free up space by clearing our data
        try {
          localStorage.removeItem(this.KEY);
          if (projectId !== null) {
            localStorage.setItem(this.KEY, projectId);
          }
        } catch (retryError) {
          console.error('Failed to save even after clearing:', retryError);
          // Fall back to in-memory (already set above)
        }
      } else {
        console.error('Failed to write to localStorage:', e);
        // Fall back to in-memory (already set above)
      }
    }
  }

  /**
   * Clear stored project ID from both localStorage and in-memory fallback
   */
  static clear(): void {
    this.inMemoryFallback = null;

    if (!this.checkAvailability()) {
      return;
    }

    try {
      localStorage.removeItem(this.KEY);
    } catch (e) {
      console.error('Failed to clear localStorage:', e);
    }
  }
}

export default ProjectStorage;
