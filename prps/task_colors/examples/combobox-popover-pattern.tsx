// Source: infra/archon/archon-ui-main/src/features/ui/primitives/combobox.tsx
// Lines: 1-375 (full component, key sections highlighted below)
// Pattern: Radix UI Popover with glassmorphism styling
// Extracted: 2025-10-10
// Relevance: 9/10 - Exact pattern for building TaskColorPicker component

/**
 * ComboBox Primitive - COMPLETE REFERENCE IMPLEMENTATION
 *
 * This is the EXACT pattern to follow for TaskColorPicker:
 * 1. Radix Popover structure (Root/Trigger/Portal/Content)
 * 2. Focus management with requestAnimationFrame
 * 3. Keyboard navigation (Enter, Escape, Tab, Arrow keys)
 * 4. Event stopPropagation to prevent bubbling
 * 5. Glassmorphism styling with backdrop-blur
 * 6. ARIA attributes for accessibility
 */

import * as Popover from "@radix-ui/react-popover";
import { Check, Loader2 } from "lucide-react";
import * as React from "react";
import { Button } from "./button";
import { cn } from "./styles";

// KEY PATTERN #1: Popover Structure with State Management
export const ComboBox = React.forwardRef<HTMLButtonElement, ComboBoxProps>(
  (
    {
      options,
      value,
      onValueChange,
      placeholder = "Select option...",
      searchPlaceholder = "Search...",
      disabled = false,
      isLoading = false,
    },
    ref,
  ) => {
    // State management for popover
    const [open, setOpen] = React.useState(false);
    const [search, setSearch] = React.useState("");
    const [highlightedIndex, setHighlightedIndex] = React.useState(0);

    // Refs for DOM elements
    const inputRef = React.useRef<HTMLInputElement>(null);

    // KEY PATTERN #2: Event Handlers with useCallback
    const handleSelect = React.useCallback(
      (optionValue: string) => {
        onValueChange(optionValue);
        setOpen(false);
        setSearch("");
        setHighlightedIndex(0);
      },
      [onValueChange],
    );

    const handleKeyDown = React.useCallback(
      (e: React.KeyboardEvent<HTMLInputElement>) => {
        switch (e.key) {
          case "Enter":
            e.preventDefault();
            // Handle selection
            break;
          case "ArrowDown":
            e.preventDefault();
            // Navigate down
            break;
          case "ArrowUp":
            e.preventDefault();
            // Navigate up
            break;
          case "Escape":
            e.preventDefault();
            setOpen(false);
            break;
          case "Tab":
            // Allow natural tab behavior to close dropdown
            setOpen(false);
            break;
        }
      },
      [/* dependencies */],
    );

    // KEY PATTERN #3: Focus Management with RAF
    React.useEffect(() => {
      if (open) {
        setSearch("");
        setHighlightedIndex(0);
        // Use RAF for more reliable focus
        requestAnimationFrame(() => {
          inputRef.current?.focus();
        });
      }
    }, [open]);

    return (
      // KEY PATTERN #4: Radix Popover Structure
      <Popover.Root open={open} onOpenChange={setOpen}>
        <Popover.Trigger asChild>
          <Button
            ref={ref}
            variant="ghost"
            disabled={disabled || isLoading}
            onClick={(e) => e.stopPropagation()} // CRITICAL: Stop propagation!
            onKeyDown={(e) => {
              e.stopPropagation(); // CRITICAL: Stop propagation!
              // Handle keyboard shortcuts
              if (e.key === " ") {
                e.preventDefault();
                setOpen(true);
              }
            }}
            className={cn(
              "h-auto px-2 py-1 rounded-md text-xs font-medium",
              "bg-gray-100/50 dark:bg-gray-800/50",
              "hover:bg-gray-200/50 dark:hover:bg-gray-700/50",
              "border border-gray-300/50 dark:border-gray-600/50",
              "transition-all duration-200",
              "focus:outline-none focus:ring-1 focus:ring-cyan-400",
            )}
          >
            <span className="truncate">
              {isLoading ? (
                <span className="flex items-center gap-1.5">
                  <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
                  <span className="sr-only">Loading options...</span>
                  Loading...
                </span>
              ) : (
                displayValue || placeholder
              )}
            </span>
          </Button>
        </Popover.Trigger>

        <Popover.Portal>
          {/* KEY PATTERN #5: Glassmorphism Content Styling */}
          <Popover.Content
            className={cn(
              "w-full min-w-[var(--radix-popover-trigger-width)] max-w-[320px]",
              // Glassmorphism background with gradient
              "bg-gradient-to-b from-white/95 to-white/90",
              "dark:from-gray-900/95 dark:to-black/95",
              "backdrop-blur-xl", // CRITICAL: Backdrop blur for glassmorphism
              "border border-gray-200 dark:border-gray-700",
              "rounded-lg shadow-xl",
              "shadow-cyan-500/10 dark:shadow-cyan-400/10",
              "z-50",
              // Animation classes
              "data-[state=open]:animate-in data-[state=closed]:animate-out",
              "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
              "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
            )}
            align="start"
            sideOffset={4}
            onOpenAutoFocus={(e) => e.preventDefault()} // CRITICAL: Prevent auto-focus issues
          >
            <div className="p-1">
              {/* KEY PATTERN #6: Search Input with ARIA */}
              <input
                ref={inputRef}
                type="text"
                role="combobox"
                aria-label="Search options"
                aria-expanded={open}
                aria-autocomplete="list"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setHighlightedIndex(0);
                }}
                onKeyDown={(e) => {
                  e.stopPropagation(); // CRITICAL: Stop propagation first
                  handleKeyDown(e);
                }}
                onClick={(e) => e.stopPropagation()} // CRITICAL: Stop propagation
                placeholder={searchPlaceholder}
                className={cn(
                  "w-full px-2 py-1 text-xs",
                  "bg-white/50 dark:bg-black/50",
                  "border border-gray-200 dark:border-gray-700",
                  "rounded",
                  "text-gray-900 dark:text-white",
                  "placeholder-gray-500 dark:placeholder-gray-400",
                  "focus:outline-none focus:ring-1 focus:ring-cyan-400",
                  "transition-all duration-200",
                )}
              />

              {/* KEY PATTERN #7: Options List with Hover States */}
              <div role="listbox" className="mt-1 overflow-y-auto max-h-[150px]">
                {isLoading ? (
                  <div className="py-3 text-center text-xs text-gray-500 dark:text-gray-400">
                    <Loader2 className="h-3 w-3 animate-spin mx-auto mb-1" aria-hidden="true" />
                    <span>Loading...</span>
                  </div>
                ) : filteredOptions.length === 0 ? (
                  <div className="py-3 text-center text-xs text-gray-500 dark:text-gray-400">
                    No results found.
                  </div>
                ) : (
                  <>
                    {filteredOptions.map((option, index) => {
                      const isSelected = value === option.value;
                      const isHighlighted = highlightedIndex === index;

                      return (
                        <button
                          type="button"
                          key={option.value}
                          role="option"
                          aria-selected={isSelected}
                          data-highlighted={isHighlighted}
                          onClick={() => handleSelect(option.value)}
                          onMouseEnter={() => setHighlightedIndex(index)}
                          className={cn(
                            "relative flex w-full items-center px-2 py-1.5",
                            "text-xs text-left",
                            "transition-colors duration-150",
                            "text-gray-900 dark:text-white",
                            "hover:bg-gray-100/80 dark:hover:bg-white/10",
                            "focus:outline-none focus:bg-gray-100/80 dark:focus:bg-white/10",
                            isSelected && "bg-cyan-50/50 dark:bg-cyan-900/20",
                            isHighlighted && !isSelected && "bg-gray-100/60 dark:bg-white/5",
                          )}
                        >
                          <Check
                            className={cn(
                              "mr-1.5 h-3 w-3 shrink-0",
                              isSelected ? "opacity-100 text-cyan-600 dark:text-cyan-400" : "opacity-0",
                            )}
                            aria-hidden="true"
                          />
                          <span className="truncate">{option.label}</span>
                        </button>
                      );
                    })}
                  </>
                )}
              </div>
            </div>
          </Popover.Content>
        </Popover.Portal>
      </Popover.Root>
    );
  },
);

ComboBox.displayName = "ComboBox";

// CRITICAL PATTERNS TO MIMIC FOR TaskColorPicker:
//
// 1. Popover Structure:
//    - Popover.Root with open/onOpenChange
//    - Popover.Trigger asChild with Button
//    - Popover.Portal > Popover.Content
//
// 2. Event Handling:
//    - ALWAYS use e.stopPropagation() on clicks and key events
//    - Use onOpenAutoFocus={(e) => e.preventDefault()}
//    - Keyboard navigation with Enter/Escape/Tab
//
// 3. Focus Management:
//    - Use requestAnimationFrame for reliable focus
//    - Reset state when popover opens
//
// 4. Glassmorphism Styling:
//    - backdrop-blur-xl for glass effect
//    - Gradient backgrounds (from-white/95 to-white/90)
//    - Subtle shadows with cyan tint
//    - Border with opacity
//
// 5. ARIA Attributes:
//    - role="combobox" on trigger
//    - aria-expanded, aria-label
//    - role="option" on items
//
// 6. State Management:
//    - Local state for open/close
//    - useCallback for handlers
//    - useEffect for side effects
//
// WHAT TO ADAPT FOR TASKCOLORPICKER:
//
// 1. Replace search input with color preset grid (2x4 layout)
// 2. Add HTML5 color input below preset grid
// 3. Add "Clear Color" button at bottom
// 4. Change trigger button to show current color as colored circle
// 5. Simplify keyboard navigation (no arrow keys needed for grid)
// 6. Keep all event stopPropagation, focus management, and glassmorphism
