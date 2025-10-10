// Source: infra/archon/archon-ui-main/src/features/projects/tasks/components/TaskEditModal.tsx
// Lines: 1-210 (full component, key sections highlighted)
// Pattern: Form field integration in modal with local state
// Extracted: 2025-10-10
// Relevance: 8/10 - Shows exact pattern for integrating TaskColorPicker into modal

/**
 * TaskEditModal - FORM FIELD INTEGRATION PATTERN
 *
 * This shows the EXACT pattern for:
 * 1. Local state management with setLocalTask
 * 2. FormGrid for 2-column layout
 * 3. Memoized change handlers
 * 4. Integration with save mutation
 * 5. Null-safety with optional fields
 */

import { memo, useCallback, useEffect, useState } from "react";
import {
  Button,
  ComboBox,
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  FormField,
  FormGrid,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  TextArea,
} from "../../../ui/primitives";
import { useTaskEditor } from "../hooks";
import { type Assignee, COMMON_ASSIGNEES, type Task, type TaskPriority } from "../types";

interface TaskEditModalProps {
  isModalOpen: boolean;
  editingTask: Task | null;
  projectId: string;
  onClose: () => void;
  onSaved?: () => void;
  onOpenChange?: (open: boolean) => void;
}

export const TaskEditModal = memo(
  ({ isModalOpen, editingTask, projectId, onClose, onSaved, onOpenChange }: TaskEditModalProps) => {
    // KEY PATTERN #1: Local state for form data
    // This holds all changes until save is clicked
    const [localTask, setLocalTask] = useState<Partial<Task> | null>(null);

    // Use business logic hook
    const { projectFeatures, saveTask, isLoadingFeatures, isSaving: isSavingTask } = useTaskEditor(projectId);

    // KEY PATTERN #2: Sync local state with editing task
    useEffect(() => {
      if (editingTask) {
        setLocalTask(editingTask);
      } else {
        // Reset for new task
        setLocalTask({
          title: "",
          description: "",
          status: "todo",
          assignee: "User" as Assignee,
          feature: "",
          priority: "medium" as TaskPriority,
          // ADD NEW FIELD HERE:
          // taskColor: undefined, // Optional color field
        });
      }
    }, [editingTask]);

    // KEY PATTERN #3: Memoized change handlers
    // These prevent unnecessary re-renders
    const handleTitleChange = useCallback((value: string) => {
      setLocalTask((prev) => (prev ? { ...prev, title: value } : null));
    }, []);

    const handleDescriptionChange = useCallback((value: string) => {
      setLocalTask((prev) => (prev ? { ...prev, description: value } : null));
    }, []);

    // KEY PATTERN #4: Handler for optional fields (like taskColor)
    // Shows null-safety pattern: prev ? { ...prev } : null
    const handleFeatureChange = useCallback((value: string) => {
      setLocalTask((prev) => (prev ? { ...prev, feature: value } : null));
    }, []);

    // ADD TASKCOLOR HANDLER HERE:
    // const handleTaskColorChange = useCallback((color: string | undefined) => {
    //   setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null));
    // }, []);

    const handleSave = useCallback(() => {
      saveTask(localTask, editingTask, () => {
        onSaved?.();
        onClose();
      });
    }, [localTask, editingTask, saveTask, onSaved, onClose]);

    return (
      <Dialog open={isModalOpen} onOpenChange={onOpenChange || ((open) => !open && onClose())}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingTask?.id ? "Edit Task" : "New Task"}</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Single column fields */}
            <FormField>
              <Label required>Title</Label>
              <Input
                value={localTask?.title || ""}
                onChange={(e) => handleTitleChange(e.target.value)}
                placeholder="Enter task title"
              />
            </FormField>

            <FormField>
              <Label>Description</Label>
              <TextArea
                value={localTask?.description || ""}
                onChange={(e) => handleDescriptionChange(e.target.value)}
                rows={5}
                placeholder="Enter task description"
              />
            </FormField>

            {/* KEY PATTERN #5: FormGrid for 2-column layout */}
            {/* First row: Status and Priority */}
            <FormGrid columns={2}>
              <FormField>
                <Label>Status</Label>
                <Select
                  value={localTask?.status || "todo"}
                  onValueChange={(value) =>
                    setLocalTask((prev) => (prev ? { ...prev, status: value as Task["status"] } : null))
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todo">Todo</SelectItem>
                    <SelectItem value="doing">Doing</SelectItem>
                    <SelectItem value="review">Review</SelectItem>
                    <SelectItem value="done">Done</SelectItem>
                  </SelectContent>
                </Select>
              </FormField>

              <FormField>
                <Label>Priority</Label>
                <Select
                  value={localTask?.priority || "medium"}
                  onValueChange={(value) =>
                    setLocalTask((prev) => (prev ? { ...prev, priority: value as TaskPriority } : null))
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="low">Low</SelectItem>
                  </SelectContent>
                </Select>
              </FormField>
            </FormGrid>

            {/* KEY PATTERN #6: Second row for optional styling fields */}
            {/* This is WHERE to add TaskColorPicker */}
            <FormGrid columns={2}>
              <FormField>
                <Label>Assignee</Label>
                <ComboBox
                  options={ASSIGNEE_OPTIONS}
                  value={localTask?.assignee || "User"}
                  onValueChange={(value) => setLocalTask((prev) => (prev ? { ...prev, assignee: value } : null))}
                  placeholder="Select or type assignee..."
                  searchPlaceholder="Search or enter custom..."
                  emptyMessage="Type a custom assignee name"
                  className="w-full"
                  allowCustomValue={true}
                />
              </FormField>

              <FormField>
                <Label>Feature</Label>
                <FeatureSelect
                  value={localTask?.feature || ""}
                  onChange={handleFeatureChange}
                  projectFeatures={projectFeatures}
                  isLoadingFeatures={isLoadingFeatures}
                  placeholder="Select or create feature..."
                  className="w-full"
                />
              </FormField>
            </FormGrid>

            {/* ADD THIRD ROW HERE FOR TASKCOLOR: */}
            {/*
            <FormGrid columns={2}>
              <FormField>
                <Label>Task Color</Label>
                <TaskColorPicker
                  value={localTask?.taskColor}
                  onChange={(color) =>
                    setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
                  }
                  disabled={isSavingTask}
                />
              </FormField>

              <FormField>
                // Could add another field here or leave empty
                // Empty FormField maintains 2-column layout
              </FormField>
            </FormGrid>
            */}
          </div>

          <DialogFooter>
            <Button onClick={onClose} variant="outline" disabled={isSavingTask}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              variant="cyan"
              loading={isSavingTask}
              disabled={isSavingTask || !localTask?.title}
            >
              {editingTask?.id ? "Update Task" : "Create Task"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  },
);

TaskEditModal.displayName = "TaskEditModal";

// CRITICAL PATTERNS TO MIMIC:
//
// 1. Local State Management:
//    - useState<Partial<Task> | null>(null)
//    - Synced with editingTask via useEffect
//    - All changes stored locally until save
//
// 2. Change Handler Pattern:
//    - Always use: setLocalTask((prev) => (prev ? { ...prev, field: value } : null))
//    - Null safety: check prev before spreading
//    - Memoize with useCallback if complex
//
// 3. FormGrid Layout:
//    - FormGrid columns={2} for side-by-side fields
//    - Each field wrapped in FormField
//    - Label component for accessibility
//
// 4. Optional Fields:
//    - Use value={localTask?.field || defaultValue}
//    - Handle undefined with || operator
//    - No need for complex null checks
//
// 5. Integration Steps:
//    a. Add taskColor?: string to Task type
//    b. Add to initial state in useEffect (undefined)
//    c. Create memoized handler (optional, inline is fine)
//    d. Add FormField in FormGrid
//    e. Wire up onChange to update localTask
//    f. Save handler automatically includes taskColor
//
// WHAT TO ADAPT FOR TASKCOLORPICKER:
//
// 1. Placement:
//    - Add AFTER Feature field (around line 187)
//    - Create new FormGrid row or add to existing
//    - Logical grouping: visual customization together
//
// 2. Label:
//    - "Task Color" or just "Color"
//    - Not required (no asterisk)
//
// 3. onChange Handler:
//    - Receives: color: string | undefined
//    - Sets: taskColor field
//    - Inline is fine (no need to memoize)
//
// 4. disabled Prop:
//    - Pass isSavingTask to disable during save
//    - Prevents changes during mutation
//
// 5. Value Prop:
//    - Pass localTask?.taskColor
//    - Undefined is valid (no color selected)
//
// EXAMPLE INTEGRATION:
//
// <FormGrid columns={2}>
//   <FormField>
//     <Label>Task Color</Label>
//     <TaskColorPicker
//       value={localTask?.taskColor}
//       onChange={(color) =>
//         setLocalTask((prev) => (prev ? { ...prev, taskColor: color } : null))
//       }
//       disabled={isSavingTask}
//     />
//   </FormField>
//
//   {/* Leave second column empty or add another field */}
//   <div />
// </FormGrid>
