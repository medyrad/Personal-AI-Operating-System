import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { api, type Task } from "./api";

const DAY_NAME = new Intl.DateTimeFormat(undefined, { weekday: "long" });
const DAY_DATE = new Intl.DateTimeFormat(undefined, { month: "long", day: "numeric" });
const CLOCK = new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" });

function dayProgressPercent(now: Date): number {
  const minutesIntoDay = now.getHours() * 60 + now.getMinutes();
  return (minutesIntoDay / (24 * 60)) * 100;
}

function ImportanceDots({ level }: { level: number }) {
  return (
    <span className="task__importance" aria-label={`Importance ${level} of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= level ? "lit" : ""} />
      ))}
    </span>
  );
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [now] = useState(() => new Date());

  useEffect(() => {
    api
      .listToday()
      .then(setTasks)
      .catch(() => setError("Could not reach Chronos — is the backend running?"));
  }, []);

  const progress = useMemo(() => dayProgressPercent(now), [now]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const title = draft.trim();
    if (!title) return;
    setDraft("");
    try {
      const created = await api.createTask({ title });
      setTasks((prev) => [...prev, created]);
    } catch {
      setError("Couldn't save that task. It's still in the box below — try again.");
      setDraft(title);
    }
  }

  async function toggleComplete(task: Task) {
    if (task.status === "done") return;
    try {
      const updated = await api.completeTask(task.id);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch {
      setError("Couldn't update that task — try again in a moment.");
    }
  }

  return (
    <div className="page">
      <div className="sheet">
        <p className="eyebrow">Today</p>
        <h1 className="date-heading">
          {DAY_NAME.format(now)}, {DAY_DATE.format(now)}
        </h1>

        <div className="day-progress">
          <div className="day-progress__track">
            <div className="day-progress__fill" style={{ width: `${progress}%` }} />
            <div className="day-progress__marker" style={{ left: `${progress}%` }} />
          </div>
          <div className="day-progress__label">
            <span>Dawn</span>
            <strong>Now · {CLOCK.format(now)}</strong>
            <span>Dusk</span>
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {tasks.length === 0 ? (
          <p className="empty-state">Nothing logged yet — begin your day below.</p>
        ) : (
          <ul className="tasks">
            {tasks.map((task) => (
              <li className="task" key={task.id}>
                <button
                  type="button"
                  className={`task__dot ${task.status === "done" ? "task__dot--done" : ""}`}
                  onClick={() => toggleComplete(task)}
                  aria-pressed={task.status === "done"}
                  aria-label={
                    task.status === "done" ? `${task.title} — done` : `Mark ${task.title} done`
                  }
                />
                <div className="task__body">
                  <div className={`task__title ${task.status === "done" ? "task__title--done" : ""}`}>
                    {task.title}
                  </div>
                  <div className="task__meta">
                    {task.estimated_minutes != null && <span>{task.estimated_minutes} min</span>}
                    <ImportanceDots level={task.importance} />
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}

        <form className="capture" onSubmit={handleSubmit}>
          <div className="capture__form">
            <span className="capture__prompt">+</span>
            <input
              className="capture__input"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Add something to today…"
              aria-label="Add a task to today"
            />
          </div>
          <p className="capture__hint">Press Enter to add</p>
        </form>
      </div>
    </div>
  );
}
