/**
 * Mermaid Rounded Corners Fallback
 * 
 * This script ensures that Mermaid diagrams have rounded corners by:
 * 1. First trying to use CSS rx/ry properties (modern approach)
 * 2. Falling back to setting SVG attributes directly if CSS doesn't work
 * 3. Using MutationObserver to handle dynamically loaded diagrams
 */

(function() {
  'use strict';
  
  const CORNER_RADIUS = 8;
  
  /**
   * Test if the browser supports CSS rx/ry properties on SVG elements
   */
  function testCSSRxRySupport() {
    try {
      const testRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      testRect.style.rx = '10px';
      // If CSS rx works, the style property should be set
      return testRect.style.rx === '10px';
    } catch (e) {
      return false;
    }
  }
  
  /**
   * Apply rounded corners to SVG rectangles using attributes
   */
  function applyRoundedCorners(container) {
    if (!container) return;
    
    // Find all rect elements in the container
    const rects = container.querySelectorAll('rect');
    
    rects.forEach(rect => {
      // Only apply if not already set or if set to 0
      const currentRx = rect.getAttribute('rx');
      const currentRy = rect.getAttribute('ry');
      
      if (!currentRx || currentRx === '0' || parseInt(currentRx) < CORNER_RADIUS) {
        rect.setAttribute('rx', CORNER_RADIUS);
      }
      
      if (!currentRy || currentRy === '0' || parseInt(currentRy) < CORNER_RADIUS) {
        rect.setAttribute('ry', CORNER_RADIUS);
      }
    });
  }
  
  /**
   * Process all existing Mermaid diagrams
   */
  function processExistingDiagrams() {
    const mermaidContainers = document.querySelectorAll('.mermaid');
    
    mermaidContainers.forEach(container => {
      const svg = container.querySelector('svg');
      if (svg) {
        applyRoundedCorners(svg);
      }
    });
  }
  
  /**
   * Initialize the rounded corners functionality
   */
  function initialize() {
    const supportsCSS = testCSSRxRySupport();
    
    if (!supportsCSS) {
      console.log('CSS rx/ry not supported, using attribute fallback for Mermaid rounded corners');
      
      // Add fallback class to body for CSS targeting
      document.body.classList.add('mermaid-rounded-fallback');
    } else {
      console.log('CSS rx/ry supported, but applying attribute fallback as additional insurance');
    }
    
    // Always apply attribute-based rounded corners as insurance
    // This ensures compatibility across all browsers and Mermaid versions
    
    // Process existing diagrams
    processExistingDiagrams();
    
    // Watch for new diagrams being added dynamically
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the added node is a Mermaid container
            if (node.classList && node.classList.contains('mermaid')) {
              const svg = node.querySelector('svg');
              if (svg) {
                applyRoundedCorners(svg);
              }
            }
            
            // Check if the added node contains Mermaid containers
            const mermaidContainers = node.querySelectorAll && node.querySelectorAll('.mermaid');
            if (mermaidContainers) {
              mermaidContainers.forEach(container => {
                const svg = container.querySelector('svg');
                if (svg) {
                  applyRoundedCorners(svg);
                }
              });
            }
            
            // Check if the added node is an SVG inside a Mermaid container
            if (node.tagName === 'svg' && node.closest('.mermaid')) {
              applyRoundedCorners(node);
            }
          }
        });
      });
    });
    
    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    // Also re-process after Mermaid renders (if Mermaid is available)
    if (typeof window.mermaid !== 'undefined') {
      // Hook into Mermaid's callback if possible
      const originalInit = window.mermaid.init;
      if (originalInit) {
        window.mermaid.init = function(...args) {
          const result = originalInit.apply(this, args);
          // Small delay to ensure rendering is complete
          setTimeout(processExistingDiagrams, 100);
          return result;
        };
      }
    }
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    // DOM is already ready
    initialize();
  }
  
  // Also initialize after window load as backup
  window.addEventListener('load', () => {
    setTimeout(processExistingDiagrams, 500);
  });
  
})(); 