/**
 * App - Root application component
 *
 * PURPOSE: Main app entry with DndProvider for drag-and-drop
 *
 * GOTCHAS ADDRESSED:
 * - Wrap App in <DndProvider backend={HTML5Backend}> (Gotcha #9)
 *
 * PATTERN: DndProvider at root enables react-dnd throughout the app
 */

import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { KanbanPage } from "./pages/KanbanPage";

// Create QueryClient instance for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Global query defaults
      staleTime: 30000, // 30s default stale time
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

function App() {
  return (
    // CRITICAL: DndProvider wraps entire app for drag-and-drop functionality
    // Must use HTML5Backend for browser-based drag-and-drop
    <DndProvider backend={HTML5Backend}>
      <QueryClientProvider client={queryClient}>
        <KanbanPage />
      </QueryClientProvider>
    </DndProvider>
  );
}

export default App;
