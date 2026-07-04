export type TaskStatus = "planned" | "in_progress" | "done" | "skipped";

export interface Task {
  id: string;
  title: string;
  status: TaskStatus;
  occurred_at: string;
  due_at: string | null;
  estimated_minutes: number | null;
  importance: number;
}

export interface CreateTaskInput {
  title: string;
  estimated_minutes?: number;
  importance?: number;
}

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Chronos API error ${response.status} on ${path}`);
  }
  return (await response.json()) as T;
}

export const api = {
  listToday: () => request<Task[]>("/events/today"),
  createTask: (input: CreateTaskInput) =>
    request<Task>("/events/tasks", { method: "POST", body: JSON.stringify(input) }),
  completeTask: (id: string) =>
    request<Task>(`/events/tasks/${id}/complete`, { method: "POST" }),
};
