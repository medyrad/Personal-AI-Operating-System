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

export interface Routine {
  id: string;
  name: string;
  category: string;
  schedule_rule: string;
  expected_duration_minutes: number | null;
  active: boolean;
}

export interface CreateRoutineInput {
  name: string;
  category?: string;
  schedule_rule?: string;
  expected_duration_minutes?: number;
}

export interface RoutineOccurrence {
  id: string;
  routine_id: string;
  expected_date: string;
  status: "pending" | "fulfilled" | "skipped";
  skip_reason: string;
}

export interface Person {
  id: string;
  display_name: string;
  relationship_label: string;
  aliases: string[];
}

export interface CreatePersonInput {
  display_name: string;
  relationship_label?: string;
  aliases?: string[];
}

export interface KnowledgeEdgeSummary {
  id: string;
  subject_type: string;
  subject_id: string;
  subject_label: string;
  predicate: string;
  object_type: string;
  object_id: string;
  object_label: string;
  confidence: number;
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
  listRoutines: () => request<Routine[]>("/routines/"),
  listTodayOccurrences: () => request<RoutineOccurrence[]>("/routines/occurrences/today"),
  createRoutine: (input: CreateRoutineInput) =>
    request<Routine>("/routines/", { method: "POST", body: JSON.stringify(input) }),
  ensureRoutineToday: (id: string) =>
    request<RoutineOccurrence | null>(`/routines/${id}/today`, { method: "POST" }),
  fulfillOccurrence: (id: string) =>
    request<RoutineOccurrence>(`/routines/occurrences/${id}/fulfill`, { method: "POST" }),
  skipOccurrence: (id: string, reason: string) =>
    request<RoutineOccurrence>(`/routines/occurrences/${id}/skip`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  listPeople: () => request<Person[]>("/people/"),
  createPerson: (input: CreatePersonInput) =>
    request<Person>("/people/", { method: "POST", body: JSON.stringify(input) }),
  updatePerson: (id: string, input: Omit<CreatePersonInput, "display_name">) =>
    request<Person>(`/people/${id}`, { method: "PATCH", body: JSON.stringify(input) }),
  listKnowledgeSummary: () => request<KnowledgeEdgeSummary[]>("/knowledge/summary"),
};
