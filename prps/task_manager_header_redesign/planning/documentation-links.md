# Documentation Resources: Task Manager Header Redesign

## Overview
Comprehensive official documentation has been curated for all technologies required for the task manager header redesign. This includes Tailwind CSS dark mode configuration, React Context API patterns, Radix UI Select component, localStorage persistence, and testing approaches. All sources are official documentation or high-quality community resources with working code examples.

---

## Primary Framework Documentation

### Tailwind CSS - Dark Mode
**Official Docs**: https://tailwindcss.com/docs/dark-mode
**Version**: v3.4.1+ (Selector strategy introduced)
**Archon Source**: Not in Archon
**Relevance**: 10/10 - Critical for fixing theme toggle functionality

**Sections to Read**:

1. **Dark Mode Configuration**: https://tailwindcss.com/docs/dark-mode#toggling-dark-mode-manually
   - **Why**: Shows how to configure `darkMode: 'selector'` or `darkMode: 'class'` in tailwind.config.js
   - **Key Concepts**:
     - Default uses `prefers-color-scheme` media query
     - Selector/class strategy enables manual dark mode toggling
     - Modern approach uses `darkMode: 'selector'` (v3.4.1+)
     - Legacy approach uses `darkMode: 'class'` (still supported)

2. **Using Dark Variants**: https://tailwindcss.com/docs/dark-mode#customizing-the-class-name
   - **Why**: Explains how to apply `dark:` prefix to utility classes
   - **Key Concepts**:
     - Prefix any utility with `dark:` (e.g., `dark:bg-gray-800`)
     - Can customize selector with array syntax: `['selector', '[data-theme="dark"]']`
     - Dark classes only apply when `dark` class exists in HTML tree

**Code Examples from Docs**:

```css
/* Tailwind v4 CSS Configuration (Modern) */
@custom-variant dark (&:where(.dark, .dark *));

/* Or with data attribute */
@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));
```

```javascript
// JavaScript Theme Management Pattern
// Source: https://tailwindcss.com/docs/dark-mode
document.documentElement.classList.toggle(
  "dark",
  localStorage.theme === "dark" ||
  (!("theme" in localStorage) &&
   window.matchMedia("(prefers-color-scheme: dark)").matches)
);

// Manually set theme
localStorage.theme = "light";  // Force light mode
localStorage.theme = "dark";   // Force dark mode
localStorage.removeItem("theme"); // Respect system preference
```

```javascript
// Tailwind Config v3 (tailwind.config.js)
// Source: https://tailwindcss.com/docs/dark-mode
module.exports = {
  darkMode: 'selector', // Modern approach (v3.4.1+)
  // OR
  darkMode: 'class',    // Legacy approach (still works)

  // Custom selector
  darkMode: ['selector', '[data-theme="dark"]'],

  theme: {
    extend: {},
  },
  plugins: [],
}
```

```html
<!-- Using Dark Variants in HTML -->
<!-- Source: https://tailwindcss.com/docs/dark-mode -->
<div class="bg-white dark:bg-gray-800">
  <h1 class="text-gray-900 dark:text-white">Dark Mode Heading</h1>
  <p class="text-gray-600 dark:text-gray-300">Supporting text</p>
</div>
```

**Gotchas from Documentation**:
- **Missing config = no dark mode**: Without `darkMode: 'class'` or `darkMode: 'selector'`, dark variants won't work
- **Build must recompile**: After adding darkMode config, Tailwind must rebuild CSS (restart dev server)
- **Class must be on parent**: The `dark` class must be on the `<html>` element or a parent element
- **v3.4.1 breaking change**: `darkMode: 'class'` deprecated in favor of `darkMode: 'selector'` but both work

---

### Tailwind CSS - Responsive Design
**Official Docs**: https://tailwindcss.com/docs/responsive-design
**Version**: v3.x
**Archon Source**: Not in Archon
**Relevance**: 8/10 - Important for ensuring layout works on all devices

**Sections to Read**:

1. **Default Breakpoints**: https://tailwindcss.com/docs/responsive-design#overview
   - **Why**: Understanding mobile-first responsive system
   - **Key Concepts**:
     - sm: 640px
     - md: 768px
     - lg: 1024px
     - xl: 1280px
     - 2xl: 1536px
     - Mobile-first approach (unprefixed utilities apply to all sizes)

2. **Customizing Breakpoints**: https://tailwindcss.com/docs/screens
   - **Why**: Reference for customizing breakpoints if needed
   - **Key Concepts**:
     - Define in `theme.screens` section
     - Can use min/max modifiers for custom breakpoints

**Code Examples from Docs**:

```html
<!-- Responsive Utilities -->
<!-- Source: https://tailwindcss.com/docs/responsive-design -->
<div class="text-sm md:text-base lg:text-lg">
  Responsive text sizing
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Mobile: 1 col, Tablet: 2 cols, Desktop: 3 cols -->
</div>
```

**Gotchas from Documentation**:
- **Mobile-first mindset**: Base styles apply to mobile, breakpoints apply upward
- **min-width not max-width**: Breakpoints use min-width media queries
- **Custom breakpoints**: Use `min-[320px]:` syntax for arbitrary breakpoints

---

### React - useContext Hook
**Official Docs**: https://react.dev/reference/react/useContext
**Version**: React 18+
**Archon Source**: Not in Archon
**Relevance**: 9/10 - Essential for understanding theme context pattern

**Sections to Read**:

1. **useContext Reference**: https://react.dev/reference/react/useContext
   - **Why**: Complete API reference for useContext hook
   - **Key Concepts**:
     - Call at top level of component
     - Returns context value from nearest provider
     - Automatically re-renders when context changes
     - Context value determined by closest provider above

2. **Passing Data Deeply with Context**: https://react.dev/learn/passing-data-deeply-with-context
   - **Why**: Step-by-step guide on implementing context
   - **Key Concepts**:
     - Use for deeply nested data (theme, auth, routing)
     - Three steps: Create, Provide, Consume
     - Prefer props and composition first
     - Context is for truly global data

3. **createContext Reference**: https://react.dev/reference/react/createContext
   - **Why**: How to create context objects
   - **Key Concepts**:
     - Accepts optional default value
     - Default only used if no provider above
     - Can pass any value type

**Code Examples from Docs**:

```typescript
// Creating Context
// Source: https://react.dev/reference/react/createContext
import { createContext } from 'react';

export const ThemeContext = createContext('light'); // Default value
```

```typescript
// Providing Context
// Source: https://react.dev/learn/passing-data-deeply-with-context
import { useState } from 'react';
import { ThemeContext } from './ThemeContext';

function App() {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={theme}>
      <Page />
    </ThemeContext.Provider>
  );
}
```

```typescript
// Consuming Context
// Source: https://react.dev/reference/react/useContext
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

function Button() {
  const theme = useContext(ThemeContext);
  return <button className={`button-${theme}`}>Click me</button>;
}
```

```typescript
// Optimized Context Value with useMemo
// Source: https://react.dev/reference/react/useContext
import { useMemo, useCallback } from 'react';

function MyApp() {
  const [currentUser, setCurrentUser] = useState(null);

  const login = useCallback((response) => {
    setCurrentUser(response.user);
  }, []);

  const contextValue = useMemo(() => ({
    currentUser,
    login
  }), [currentUser, login]);

  return (
    <AuthContext.Provider value={contextValue}>
      <App />
    </AuthContext.Provider>
  );
}
```

**Gotchas from Documentation**:
- **Provider must be above consumer**: useContext() looks upward in tree
- **Forgetting value prop**: Provider without value prop returns undefined
- **Symlink issues**: Build tools with symlinks can break context if contexts aren't same object
- **Re-render performance**: Context changes re-render all consumers (use useMemo/useCallback for objects)

---

## Library Documentation

### 1. Radix UI - Select Component
**Official Docs**: https://www.radix-ui.com/primitives/docs/components/select
**Purpose**: Accessible dropdown component for project selector
**Archon Source**: Not in Archon
**Relevance**: 7/10 - Reference for Select component API

**Key Pages**:

- **Select Component Overview**: https://www.radix-ui.com/primitives/docs/components/select
  - **Use Case**: Understanding component parts and composition
  - **Example**: Installation, component structure, accessibility features

**Installation**:
```bash
npm install @radix-ui/react-select
```

**Component Parts**:

```typescript
// Core Component Structure
// Source: https://www.radix-ui.com/primitives/docs/components/select
import * as Select from '@radix-ui/react-select';

<Select.Root>              // Contains all parts
  <Select.Trigger>         // Button that toggles select
    <Select.Value />       // Displays selected item
    <Select.Icon />        // Icon in trigger
  </Select.Trigger>

  <Select.Portal>          // Renders content outside DOM hierarchy
    <Select.Content>       // Dropdown container
      <Select.Viewport>    // Scrollable area
        <Select.Item>      // Individual option
          <Select.ItemText />
          <Select.ItemIndicator />
        </Select.Item>
      </Select.Viewport>
    </Select.Content>
  </Select.Portal>
</Select.Root>
```

**API Reference**:

- **Select.Root**:
  - **Props**: `defaultValue`, `value`, `onValueChange`, `disabled`, `name`
  - **Use**: Container for all select parts

- **Select.Trigger**:
  - **Props**: `asChild`, `disabled`
  - **Use**: Button that opens the select

- **Select.Content**:
  - **Props**: `position="item-aligned" | "popper"`, `side`, `align`, `sideOffset`
  - **Use**: Dropdown menu container

- **Select.Item**:
  - **Props**: `value` (required), `disabled`, `textValue`
  - **Use**: Individual selectable option

**Code Example**:

```tsx
// Complete Select Example
// Source: https://www.radix-ui.com/primitives/docs/components/select
import * as Select from '@radix-ui/react-select';

function ProjectSelector() {
  return (
    <Select.Root>
      <Select.Trigger className="SelectTrigger">
        <Select.Value placeholder="Select a project..." />
        <Select.Icon className="SelectIcon">
          <ChevronDownIcon />
        </Select.Icon>
      </Select.Trigger>

      <Select.Portal>
        <Select.Content className="SelectContent">
          <Select.Viewport className="SelectViewport">
            <Select.Item value="project-1">
              <Select.ItemText>Project 1</Select.ItemText>
              <Select.ItemIndicator className="SelectItemIndicator">
                <CheckIcon />
              </Select.ItemIndicator>
            </Select.Item>
            <Select.Item value="project-2">
              <Select.ItemText>Project 2</Select.ItemText>
            </Select.Item>
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  );
}
```

**Accessibility Features**:
- Follows WAI-ARIA ListBox design pattern
- Full keyboard navigation (Arrow keys, Enter, Escape)
- Screen reader support
- Focus management
- Type-ahead search

**Gotchas from Documentation**:
- **Portal escapes stacking context**: Select.Portal renders outside normal DOM (already handled in codebase - Gotcha #6)
- **Position modes**: Default "item-aligned" vs "popper" positioning
- **Controlled vs uncontrolled**: Use `value` + `onValueChange` for controlled, `defaultValue` for uncontrolled
- **Custom styling**: Requires custom CSS, no default styles provided

---

### 2. Lucide React - Icons
**Official Docs**: https://lucide.dev/guide/packages/lucide-react
**Purpose**: Sun and Moon icons for theme toggle
**Archon Source**: Not in Archon
**Relevance**: 6/10 - Icon library reference

**Key Pages**:

- **Lucide React Guide**: https://lucide.dev/guide/packages/lucide-react
  - **Use Case**: How to import and use icons
  - **Example**: Icon customization with props

- **Moon Icon**: https://lucide.dev/icons/moon
- **Sun Icon**: https://lucide.dev/icons/sun

**Installation**:
```bash
npm install lucide-react
```

**Usage Example**:

```tsx
// Importing Icons
// Source: https://lucide.dev/guide/packages/lucide-react
import { Sun, Moon } from 'lucide-react';

// Using Icons with Props
function ThemeToggle() {
  return (
    <button>
      {theme === 'dark' ? (
        <Sun size={20} color="currentColor" />
      ) : (
        <Moon size={20} color="currentColor" />
      )}
    </button>
  );
}
```

**Icon Props**:
- `size`: Number or string (default: 24)
- `color`: String (default: "currentColor")
- `strokeWidth`: Number (default: 2)
- All standard SVG attributes

**Key Features**:
- Tree-shakeable (only imported icons included in bundle)
- TypeScript support (type: `LucideIcon`)
- Renders inline SVG elements
- Accepts all SVG props

---

## Browser APIs

### localStorage API
**Official Docs**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
**Purpose**: Persist theme preference across sessions
**Archon Source**: Not in Archon
**Relevance**: 9/10 - Essential for theme persistence

**Key Pages**:

- **localStorage Property**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
  - **Use Case**: Complete API reference for localStorage
  - **Example**: setItem, getItem, removeItem, clear

- **Using Web Storage API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
  - **Use Case**: Best practices and error handling
  - **Example**: Feature detection and availability testing

**API Methods**:

```javascript
// Basic localStorage Operations
// Source: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

// Set item
localStorage.setItem("theme", "dark");

// Get item
const theme = localStorage.getItem("theme");

// Remove specific item
localStorage.removeItem("theme");

// Clear all items
localStorage.clear();

// Check if key exists
if (localStorage.getItem("theme")) {
  // Theme preference exists
}
```

**Error Handling Pattern**:

```javascript
// Recommended Try-Catch Pattern
// Source: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
function saveTheme(theme) {
  try {
    localStorage.setItem("theme", theme);
  } catch (error) {
    // Handle errors
    if (error instanceof DOMException) {
      if (error.name === 'QuotaExceededError') {
        console.warn('localStorage quota exceeded');
      } else if (error.name === 'SecurityError') {
        console.warn('localStorage access denied');
      }
    }
  }
}

// Feature Detection
function isLocalStorageAvailable() {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}
```

**Browser Compatibility**:
- Chrome: ✅ Full support (since July 2015)
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Edge: ✅ Full support
- IE 8+: ✅ Full support (legacy)

**Storage Characteristics**:
- **Capacity**: ~5-10 MB per origin (varies by browser)
- **Scope**: Specific to protocol (HTTP vs HTTPS)
- **Data Type**: Stores only strings (use JSON.stringify/parse for objects)
- **Persistence**: Data survives browser restarts
- **Synchronous**: Blocking operations

**Exceptions**:

1. **SecurityError**:
   - Origin is invalid scheme/host/port tuple
   - User configured browser to prevent data persistence
   - Cookies blocked or private browsing mode

2. **QuotaExceededError**:
   - Storage quota exceeded (~5MB)
   - Unlikely for single theme value

**Gotchas from Documentation**:
- **Private browsing**: May give empty localStorage with quota of zero
- **file:// protocol**: Behavior varies by browser
- **SSR incompatibility**: localStorage not available on server (Node.js)
- **String only**: Must use JSON.stringify() for objects
- **Synchronous blocking**: Can impact performance if used heavily

---

## Integration Guides

### React Theme Toggle with localStorage Pattern
**Guide URL**: Multiple sources (Stack Overflow, DEV Community, Medium)
**Source Type**: Community Best Practices
**Quality**: 8/10
**Archon Source**: Not in Archon

**What it covers**:
- useState + useEffect pattern for localStorage sync
- Custom useLocalStorage hook pattern
- useSyncExternalStore pattern (React 18+)
- Flash prevention techniques
- TypeScript implementation

**Code examples**:

```typescript
// Pattern 1: useState + useEffect
// Source: Multiple community resources
import { useState, useEffect } from 'react';

function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Initialize from localStorage
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark' ? 'dark' : 'light';
  });

  useEffect(() => {
    // Sync to localStorage on change
    localStorage.setItem('theme', theme);

    // Apply to document
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return { theme, toggleTheme };
}
```

```typescript
// Pattern 2: Custom useLocalStorage Hook
// Source: https://www.freecodecamp.org/news/how-to-use-localstorage-with-react-hooks-to-set-and-get-items/
import { useState, useEffect } from 'react';

function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
}

// Usage
function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return <button onClick={toggleTheme}>Toggle Theme</button>;
}
```

```typescript
// Pattern 3: useSyncExternalStore (React 18+)
// Source: https://oakhtar147.medium.com/sync-local-storage-state-across-tabs-in-react-using-usesyncexternalstore-613d2c22819e
import { useSyncExternalStore } from 'react';

function useLocalStorageSync(key: string, initialValue: string) {
  const subscribe = (callback: () => void) => {
    window.addEventListener('storage', callback);
    return () => window.removeEventListener('storage', callback);
  };

  const getSnapshot = () => {
    return localStorage.getItem(key) ?? initialValue;
  };

  const getServerSnapshot = () => {
    return initialValue;
  };

  const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const setValue = (newValue: string) => {
    localStorage.setItem(key, newValue);
    window.dispatchEvent(new Event('storage'));
  };

  return [value, setValue] as const;
}
```

**Applicable patterns**:
- Initialize state from localStorage in useState initializer (avoid useEffect for initial read)
- Use useEffect to sync state to localStorage on changes
- Apply dark class to document.documentElement
- Wrap in try-catch for error handling
- Use custom hook for reusability
- Consider useSyncExternalStore for cross-tab sync

**Flash Prevention**:
```html
<!-- Inline script to prevent flash of wrong theme -->
<!-- Source: https://css-tricks.com/easy-dark-mode-and-multiple-color-themes-in-react/ -->
<script>
  // Run before React hydrates
  (function() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    }
  })();
</script>
```

---

## Testing Documentation

### React Testing Library - Theme Toggle Testing
**Resource**: https://medium.com/@Galaxy-Trek/how-to-create-a-dark-mode-toggle-for-your-website-with-tests-5ec1adc1df0a
**Type**: Community Tutorial
**Relevance**: 7/10

**Key Practices**:

1. **Test Toggle Functionality**:
   - Verify button is in document
   - Simulate click with fireEvent
   - Assert state changes (checked/unchecked)

2. **Test Side Effects**:
   - Check document.documentElement has 'dark' class
   - Verify localStorage is updated
   - Test persistence across re-renders

3. **Test Context Provider**:
   - Wrap components with ThemeProvider in tests
   - Create custom render function
   - Test context value changes

**Test Examples**:

```typescript
// Theme Toggle Component Test
// Source: Community best practices
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from './ThemeContext';
import ThemeToggle from './ThemeToggle';

describe('ThemeToggle', () => {
  // Custom render with provider
  const renderWithTheme = (ui: React.ReactElement) => {
    return render(
      <ThemeProvider>
        {ui}
      </ThemeProvider>
    );
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Remove dark class
    document.documentElement.classList.remove('dark');
  });

  it('toggles theme when clicked', () => {
    renderWithTheme(<ThemeToggle />);

    const toggleButton = screen.getByRole('button', { name: /theme/i });

    // Initial state - light mode
    expect(document.documentElement.classList.contains('dark')).toBe(false);

    // Click to dark mode
    fireEvent.click(toggleButton);
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem('theme')).toBe('dark');

    // Click back to light mode
    fireEvent.click(toggleButton);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(localStorage.getItem('theme')).toBe('light');
  });

  it('initializes from localStorage', () => {
    localStorage.setItem('theme', 'dark');

    renderWithTheme(<ThemeToggle />);

    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('displays correct icon based on theme', () => {
    renderWithTheme(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');

    // Light mode shows moon icon
    expect(toggleButton.querySelector('[data-icon="moon"]')).toBeInTheDocument();

    fireEvent.click(toggleButton);

    // Dark mode shows sun icon
    expect(toggleButton.querySelector('[data-icon="sun"]')).toBeInTheDocument();
  });
});
```

**Vitest Configuration**:
```typescript
// vitest.config.ts
// Source: Vitest documentation
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
});
```

---

## Best Practices Documentation

### Tailwind CSS + React Dark Mode Best Practices
**Resource**: https://prismic.io/blog/tailwind-css-darkmode-tutorial
**Type**: Official Tutorial
**Relevance**: 8/10

**Key Practices**:

1. **Configuration First**:
   - Always set `darkMode: 'selector'` or `darkMode: 'class'` in config
   - Restart dev server after config changes
   - Use modern 'selector' strategy over legacy 'class'

2. **Class Management**:
   - Add/remove 'dark' class on `document.documentElement`
   - Don't add to body or individual components
   - Use classList.toggle() for cleaner code

3. **localStorage Strategy**:
   - Read in useState initializer, not useEffect
   - Write in useEffect to sync changes
   - Wrap in try-catch for safety
   - Use JSON.parse for objects, direct string for simple values

4. **Performance**:
   - Use useMemo for context values with objects
   - Use useCallback for handler functions
   - Avoid unnecessary re-renders with React.memo
   - Keep dark: variants to minimum necessary

5. **Accessibility**:
   - Provide aria-label for theme toggle button
   - Announce theme changes to screen readers
   - Ensure focus visible states
   - Maintain color contrast in both modes

**Example**:

```typescript
// Complete Theme Context Implementation
// Source: Community best practices
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  // Initialize from localStorage
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const savedTheme = localStorage.getItem('theme');
      return savedTheme === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  });

  // Sync to localStorage and document
  useEffect(() => {
    try {
      localStorage.setItem('theme', theme);
    } catch (error) {
      console.warn('Failed to save theme preference:', error);
    }

    // Apply dark class
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => ({ theme, toggleTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

---

## Additional Resources

### Tutorials with Code

1. **Tailwind CSS Dark Mode Tutorial**: https://prismic.io/blog/tailwind-css-darkmode-tutorial
   - **Format**: Blog post with complete code
   - **Quality**: 9/10
   - **What makes it useful**: Step-by-step walkthrough with Next.js integration, covers configuration, implementation, and testing

2. **React Dark Mode with Tests**: https://medium.com/@Galaxy-Trek/how-to-create-a-dark-mode-toggle-for-your-website-with-tests-5ec1adc1df0a
   - **Format**: Blog post with testing examples
   - **Quality**: 8/10
   - **What makes it useful**: Includes complete testing strategy with React Testing Library

3. **Easy Dark Mode in React**: https://css-tricks.com/easy-dark-mode-and-multiple-color-themes-in-react/
   - **Format**: Blog post
   - **Quality**: 9/10
   - **What makes it useful**: Covers flash prevention, multiple themes, and accessibility

4. **React Toggle Theme with Hooks**: https://dev.to/email2vimalraj/toggle-theme-using-react-hooks-2ibe
   - **Format**: Tutorial with full code
   - **Quality**: 7/10
   - **What makes it useful**: Simple implementation with testing section

### API References

1. **Tailwind CSS Configuration**: https://tailwindcss.com/docs/configuration
   - **Coverage**: Complete config file reference
   - **Examples**: Yes, extensive examples

2. **React Hooks Reference**: https://react.dev/reference/react
   - **Coverage**: All React hooks including useState, useEffect, useContext
   - **Examples**: Yes, interactive examples

3. **Web Storage API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API
   - **Coverage**: Complete localStorage/sessionStorage API
   - **Examples**: Yes, with error handling

### Community Resources

1. **Stack Overflow - React Theme Toggle**: https://stackoverflow.com/questions/72561602/how-do-i-test-theme-toggler-with-react-testing-library-and-jest
   - **Type**: Q&A with working solutions
   - **Why included**: Real-world testing examples and common pitfalls

2. **GitHub - React Dark Mode Example**: https://github.com/alexeagleson/react-dark-mode
   - **Type**: Complete working repository
   - **Why included**: Full implementation with tests

3. **CodeSandbox - Radix UI Select Demo**: https://codesandbox.io/s/radix-ui-select-demo-vco4mr
   - **Type**: Interactive code sandbox
   - **Why included**: Live examples of Radix Select component

---

## Documentation Gaps

**Not found in Archon or Web**:
- None - All required documentation is well-documented and available

**Outdated or Incomplete**:
- **Tailwind v2 docs**: Some tutorials reference old `darkMode: 'class'` only - updated to 'selector' strategy in v3.4.1
  - **Recommendation**: Prefer modern 'selector' strategy but 'class' still works
- **React 17 patterns**: Some older tutorials don't show useSyncExternalStore pattern
  - **Recommendation**: Stick with useState + useEffect pattern for this project (simpler)

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - Tailwind CSS Dark Mode: https://tailwindcss.com/docs/dark-mode
  - Tailwind Responsive: https://tailwindcss.com/docs/responsive-design
  - React useContext: https://react.dev/reference/react/useContext
  - React Context Guide: https://react.dev/learn/passing-data-deeply-with-context

Library Docs:
  - Radix UI Select: https://www.radix-ui.com/primitives/docs/components/select
  - Lucide React: https://lucide.dev/guide/packages/lucide-react
  - Lucide Icons (Moon): https://lucide.dev/icons/moon
  - Lucide Icons (Sun): https://lucide.dev/icons/sun

Browser APIs:
  - localStorage API: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
  - Web Storage Guide: https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API

Integration Guides:
  - Tailwind Dark Mode Tutorial: https://prismic.io/blog/tailwind-css-darkmode-tutorial
  - React Theme Toggle Guide: https://css-tricks.com/easy-dark-mode-and-multiple-color-themes-in-react/

Testing Docs:
  - Testing Theme Toggle: https://medium.com/@Galaxy-Trek/how-to-create-a-dark-mode-toggle-for-your-website-with-tests-5ec1adc1df0a
  - React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
```

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include these URLs** in "Documentation & References" section:
   - Tailwind dark mode configuration (PRIMARY - critical fix)
   - React useContext reference (for understanding existing pattern)
   - Radix Select API (for component reference)
   - localStorage MDN (for error handling)

2. **Extract code examples** shown above into PRP context:
   - tailwind.config.js with darkMode: 'selector'
   - document.documentElement.classList.toggle pattern
   - Theme context pattern with useMemo
   - localStorage error handling try-catch

3. **Highlight gotchas** from documentation in "Known Gotchas" section:
   - Missing darkMode config prevents dark mode from working
   - Dev server must restart after config change
   - dark class must be on document.documentElement
   - localStorage may throw SecurityError in private browsing

4. **Reference specific sections** in implementation tasks:
   - Task 1: "Add darkMode config - see Tailwind docs: https://tailwindcss.com/docs/dark-mode#toggling-dark-mode-manually"
   - Task 2: "Verify dark class applied - see Theme toggle pattern examples above"
   - Task 3: "Test localStorage persistence - see MDN error handling: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage"

5. **Note gaps** so implementation can compensate:
   - No gaps identified - all technologies are well-documented
   - Existing codebase already has correct patterns (ThemeContext, ProjectSelector)

---

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:

1. **Tailwind CSS Official Docs**: https://tailwindcss.com/docs
   - **Why valuable**: Extremely common CSS framework, referenced in nearly every modern web PRP
   - **Priority**: HIGH
   - **Scope**: Dark mode, configuration, responsive design, utility classes

2. **React Official Docs (react.dev)**: https://react.dev
   - **Why valuable**: Official React documentation with modern patterns and hooks
   - **Priority**: HIGH
   - **Scope**: Hooks reference (useState, useEffect, useContext), Context guide, best practices

3. **Radix UI Primitives Docs**: https://www.radix-ui.com/primitives/docs
   - **Why valuable**: Popular accessible component library, frequently used in React projects
   - **Priority**: MEDIUM
   - **Scope**: All primitive components (Select, Dropdown, Dialog, etc.)

4. **MDN Web APIs**: https://developer.mozilla.org/en-US/docs/Web/API
   - **Why valuable**: Comprehensive browser API reference, essential for web development
   - **Priority**: HIGH
   - **Scope**: Web Storage API, DOM APIs, Fetch API, etc.

5. **React Testing Library Docs**: https://testing-library.com/docs/react-testing-library/intro
   - **Why valuable**: Standard testing library for React, used in most modern React projects
   - **Priority**: MEDIUM
   - **Scope**: Testing patterns, best practices, API reference

---

## Implementation Checklist

Use this checklist when implementing based on this documentation:

### Configuration
- [ ] Add `darkMode: 'selector'` to tailwind.config.js
- [ ] Restart dev server to rebuild Tailwind CSS
- [ ] Verify dark: classes appear in compiled CSS

### Theme Toggle
- [ ] Verify ThemeContext uses localStorage in useState initializer
- [ ] Verify useEffect applies 'dark' class to document.documentElement
- [ ] Verify toggleTheme function updates both state and localStorage
- [ ] Add try-catch around localStorage operations
- [ ] Test theme toggle button click functionality

### Layout Changes
- [ ] Move ProjectSelector from header to board section
- [ ] Remove "Kanban Board" h2 header
- [ ] Keep ThemeToggle in upper right of header
- [ ] Verify responsive breakpoints work (sm, md, lg)

### Testing
- [ ] Create/update ThemeToggle test file
- [ ] Test toggle functionality with fireEvent.click
- [ ] Test localStorage persistence
- [ ] Test document.documentElement.classList
- [ ] Test icon switching (Moon/Sun)
- [ ] Run accessibility audit

### Documentation
- [ ] Update README if needed
- [ ] Add comments referencing official docs
- [ ] Document any deviations from standard patterns

---

## Summary

This documentation hunt successfully located official documentation for all technologies:

**Primary Sources** (Official):
- Tailwind CSS dark mode configuration ✅
- React useContext and Context API ✅
- Radix UI Select component ✅
- localStorage Web API ✅
- Lucide React icons ✅

**Code Examples**: ✅ Complete working examples extracted
- tailwind.config.js configuration
- Theme context implementation
- localStorage error handling
- Testing patterns

**Gotchas Identified**: ✅ All documented
- Missing darkMode config (root cause of bug)
- Dev server restart requirement
- localStorage error handling
- Flash prevention techniques

**Coverage**: 10/10 - All technologies have comprehensive official documentation with working examples

**Archon Status**: None of these sources currently in Archon - all found via web search. Recommend ingesting Tailwind, React, Radix UI, and MDN docs for future PRPs.

**Next Steps**: PRP Assembler should use these URLs and code examples to create comprehensive implementation guide with specific documentation references for each task.
