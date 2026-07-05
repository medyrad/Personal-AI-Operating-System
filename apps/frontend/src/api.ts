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

export interface ExtractedEvent {
  id: string;
  type: string;
  title: string;
  mood_valence: number | null;
}

export interface JournalResult {
  id: string;
  entry_date: string;
  raw_text: string;
  extracted_events: ExtractedEvent[];
}

export interface TimeBlock {
  start: string;
  end: string;
  activity: string;
  reason: string;
}

export interface DayPlan {
  blocks: TimeBlock[];
}

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.detail ?? `Chronos API error ${response.status} on ${path}`;
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export const api = {
  listToday: () => request<Task[]>("/events/today"),
  createTask: (input: CreateTaskInput) =>
    request<Task>("/events/tasks", { method: "POST", body: JSON.stringify(input) }),
  completeTask: (id: string) =>
    request<Task>(`/events/tasks/${id}/complete`, { method: "POST" }),
  submitJournal: (raw_text: string) =>
    request<JournalResult>("/journal", { method: "POST", body: JSON.stringify({ raw_text }) }),
  planTomorrow: () => request<DayPlan>("/ai/planner/tomorrow", { method: "POST" }),
};
