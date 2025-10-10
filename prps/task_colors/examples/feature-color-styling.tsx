// Source: infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskCard.tsx
// Lines: 171-182
// Pattern: Color styling with alpha transparency
// Extracted: 2025-10-10
// Relevance: 10/10 - EXACT pattern for applying taskColor to TaskCard

/**
 * Feature Color Pattern - HOW TO APPLY COLORS WITH ALPHA TRANSPARENCY
 *
 * This is the EXACT pattern from TaskCard that shows how featureColor is applied.
 * TaskColor will use the SAME pattern but applied to the main card container.
 *
 * KEY INSIGHTS:
 * 1. Hex colors with alpha suffix (e.g., "20" = ~12.5% opacity)
 * 2. Applied via inline styles (not Tailwind classes)
 * 3. Uses template literals for dynamic colors
 * 4. Three properties: backgroundColor, color, boxShadow
 * 5. Works with existing glassmorphism
 */

import { Tag } from "lucide-react";
import type { Task } from "../types";

// EXAMPLE 1: Feature Tag Badge (from TaskCard lines 171-182)
// This shows the EXACT pattern for color with alpha transparency
export function FeatureColorBadgeExample({ task }: { task: Task }) {
  return (
    <>
      {task.feature && (
        <div
          className="px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 backdrop-blur-md"
          style={{
            // KEY PATTERN: Background with 20% opacity (hex "20" suffix)
            backgroundColor: `${task.featureColor}20`,

            // KEY PATTERN: Text color with full opacity (no suffix)
            color: task.featureColor,

            // KEY PATTERN: Box shadow with 20% opacity for glow effect
            boxShadow: `0 0 10px ${task.featureColor}20`,
          }}
        >
          <Tag className="w-3 h-3" />
          {task.feature}
        </div>
      )}
    </>
  );
}

// EXAMPLE 2: How to Apply Same Pattern to Task Card Container
// This is what you'll do for taskColor on the main card (lines 159-161)
export function TaskCardWithColorExample({ task }: { task: Task }) {
  // Base glassmorphism classes (keep these!)
  const cardBaseStyles =
    "bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30 border border-gray-200 dark:border-gray-700 rounded-lg backdrop-blur-md";

  return (
    <div
      className={`${cardBaseStyles} w-full min-h-[140px] h-full`}
      style={{
        // CRITICAL: Use conditional inline styles when taskColor is present
        // This preserves base styles and adds color overlay
        ...(task.taskColor && {
          backgroundColor: `${task.taskColor}10`, // 10% opacity for subtle tint
          borderColor: `${task.taskColor}30`,     // 30% opacity for border accent
          boxShadow: `0 0 10px ${task.taskColor}20`, // 20% opacity for glow
        }),
      }}
    >
      {/* Card content here */}
      <div className="p-3">
        <h4>{task.title}</h4>
      </div>
    </div>
  );
}

// EXAMPLE 3: Hex Alpha Transparency Reference
// CSS hex colors with alpha channel suffix:
const ALPHA_REFERENCE = {
  "10": "6.25% opacity",   // Very subtle - good for card backgrounds
  "20": "12.5% opacity",   // Subtle - good for badges and glows
  "30": "18.75% opacity",  // Visible - good for borders
  "40": "25% opacity",     // Medium - good for hover states
  "50": "31.25% opacity",  // Half transparent
  "80": "50% opacity",     // Strong
  "FF": "100% opacity",    // Full color
};

// EXAMPLE 4: Complete Pattern for TaskColorPicker Integration
interface TaskWithColor extends Task {
  taskColor?: string; // New field: hex string like "#ef4444"
}

export function TaskCardFull({ task }: { task: TaskWithColor }) {
  const cardBaseStyles =
    "bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30 border border-gray-200 dark:border-gray-700 rounded-lg backdrop-blur-md";

  const transitionStyles = "transition-all duration-200 ease-in-out";

  return (
    <div
      className={`${cardBaseStyles} ${transitionStyles} w-full min-h-[140px] h-full`}
      // KEY PATTERN: Conditional inline styles
      style={{
        // Only apply when taskColor exists
        ...(task.taskColor && {
          // Background tint (very subtle)
          backgroundColor: `${task.taskColor}10`,

          // Border accent (more visible)
          borderColor: `${task.taskColor}30`,

          // Glow effect for depth
          boxShadow: `0 0 10px ${task.taskColor}20`,
        }),
      }}
    >
      {/* Priority indicator (left border) - PRESERVE THIS */}
      <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-blue-500 rounded-l-lg" />

      {/* Header with feature tag */}
      <div className="flex items-center gap-2 mb-2 pl-1.5">
        {/* Feature color badge - KEEP THIS SEPARATE from taskColor */}
        {task.feature && (
          <div
            className="px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1 backdrop-blur-md"
            style={{
              backgroundColor: `${task.featureColor}20`,
              color: task.featureColor,
              boxShadow: `0 0 10px ${task.featureColor}20`,
            }}
          >
            <Tag className="w-3 h-3" />
            {task.feature}
          </div>
        )}
      </div>

      {/* Task content */}
      <div className="p-3">
        <h4 className="text-xs font-medium">{task.title}</h4>
        {task.description && (
          <p className="text-xs text-gray-600 dark:text-gray-400">{task.description}</p>
        )}
      </div>
    </div>
  );
}

// CRITICAL PATTERNS TO MIMIC:
//
// 1. Inline Styles NOT Tailwind Classes:
//    - Tailwind doesn't support dynamic colors
//    - Must use style={{ }} prop
//    - Template literals for dynamic values
//
// 2. Alpha Transparency:
//    - Hex suffix "10" = 6.25% opacity
//    - Hex suffix "20" = 12.5% opacity
//    - Hex suffix "30" = 18.75% opacity
//    - Applied to BOTH background and boxShadow
//
// 3. Conditional Application:
//    - Use spread operator: ...(condition && { styles })
//    - Only apply when color exists
//    - Preserves base glassmorphism styles
//
// 4. Three Properties:
//    - backgroundColor: Subtle background tint
//    - borderColor: Border accent (more visible)
//    - boxShadow: Glow effect for depth
//
// 5. Opacity Guidelines:
//    - Background: 10% (very subtle, doesn't overpower)
//    - Border: 30% (visible accent)
//    - Shadow: 20% (soft glow)
//
// WHAT TO ADAPT:
//
// 1. Apply to Main Card Container:
//    - Not to a badge or tag
//    - To the div at lines 159-161 in TaskCard.tsx
//
// 2. Preserve Existing Styles:
//    - Keep glassmorphism gradient
//    - Keep priority indicator (left border)
//    - Keep feature color badge (separate from taskColor)
//
// 3. Test in Dark Mode:
//    - All 8 preset colors should be visible
//    - Should work with dark glassmorphism
//    - Glow should be visible but not garish
//
// 4. Validation:
//    - taskColor is optional (undefined by default)
//    - Must be valid hex format: /^#[0-9A-Fa-f]{6}$/
//    - No RGB or named colors
