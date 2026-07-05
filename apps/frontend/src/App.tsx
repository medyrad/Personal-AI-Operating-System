import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import {
  api,
  type DayPlan,
  type ExtractedEvent,
  type KnowledgeEdgeSummary,
  type Person,
  type Routine,
  type RoutineOccurrence,
  type Task,
} from "./api";
import { copy, directionFor, LANGUAGES, localeFor, THEMES, type Language, type Theme } from "./i18n";

const LANGUAGE_KEY = "chronos.language";
const THEME_KEY = "chronos.theme";

function readStoredLanguage(): Language {
  const stored = window.localStorage.getItem(LANGUAGE_KEY);
  return stored === "fa" || stored === "en" ? stored : "en";
}

function readStoredTheme(): Theme {
  const stored = window.localStorage.getItem(THEME_KEY);
  return stored === "light" || stored === "dark" ? stored : "dark";
}

function dayProgressPercent(now: Date): number {
  const minutesIntoDay = now.getHours() * 60 + now.getMinutes();
  return (minutesIntoDay / (24 * 60)) * 100;
}

function ImportanceDots({ label, level }: { label: string; level: number }) {
  return (
    <span className="task__importance" aria-label={label}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= level ? "lit" : ""} />
      ))}
    </span>
  );
}

export default function App() {
  const [language, setLanguage] = useState<Language>(() => readStoredLanguage());
  const [theme, setTheme] = useState<Theme>(() => readStoredTheme());
  const [tasks, setTasks] = useState<Task[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [now] = useState(() => new Date());

  const [journalDraft, setJournalDraft] = useState("");
  const [journalEvents, setJournalEvents] = useState<ExtractedEvent[]>([]);
  const [journalStatus, setJournalStatus] = useState<"idle" | "sending" | "sent">("idle");

  const [plan, setPlan] = useState<DayPlan | null>(null);
  const [planStatus, setPlanStatus] = useState<"idle" | "loading" | "unavailable">("idle");
  const [planMessage, setPlanMessage] = useState<string | null>(null);

  const [routines, setRoutines] = useState<Routine[]>([]);
  const [occurrences, setOccurrences] = useState<Record<string, RoutineOccurrence | null>>({});
  const [routineName, setRoutineName] = useState("");
  const [routineCategory, setRoutineCategory] = useState("");

  const [people, setPeople] = useState<Person[]>([]);
  const [personName, setPersonName] = useState("");
  const [relationshipLabel, setRelationshipLabel] = useState("");
  const [edges, setEdges] = useState<KnowledgeEdgeSummary[]>([]);

  const t = copy[language];
  const locale = localeFor(language);
  const direction = directionFor(language);
  const dayName = useMemo(
    () => new Intl.DateTimeFormat(locale, { weekday: "long" }).format(now),
    [locale, now],
  );
  const dayDate = useMemo(
    () => new Intl.DateTimeFormat(locale, { month: "long", day: "numeric" }).format(now),
    [locale, now],
  );
  const clock = useMemo(
    () => new Intl.DateTimeFormat(locale, { hour: "2-digit", minute: "2-digit" }).format(now),
    [locale, now],
  );
  const numberFormat = useMemo(() => new Intl.NumberFormat(locale), [locale]);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = direction;
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(LANGUAGE_KEY, language);
    window.localStorage.setItem(THEME_KEY, theme);
  }, [direction, language, locale, theme]);

  const refreshLifeContext = useCallback(async () => {
    try {
      const [routineList, peopleList, edgeList] = await Promise.all([
        api.listRoutines(),
        api.listPeople(),
        api.listKnowledgeSummary(),
      ]);
      const todayOccurrences = await api.listTodayOccurrences();
      setRoutines(routineList);
      setPeople(peopleList);
      setEdges(edgeList);
      setOccurrences(
        Object.fromEntries(todayOccurrences.map((occurrence) => [occurrence.routine_id, occurrence])),
      );
    } catch {
      setError(t.errors.lifeContext);
    }
  }, [t.errors.lifeContext]);

  useEffect(() => {
    api
      .listToday()
      .then(setTasks)
      .catch(() => setError(t.errors.backend));
    queueMicrotask(() => {
      void refreshLifeContext();
    });
  }, [refreshLifeContext, t.errors.backend]);

  const progress = useMemo(() => dayProgressPercent(now), [now]);
  const progressPositionStyle =
    direction === "rtl" ? ({ right: `${progress}%` } as const) : ({ left: `${progress}%` } as const);
  const progressFillStyle =
    direction === "rtl"
      ? ({ width: `${progress}%`, right: 0 } as const)
      : ({ width: `${progress}%`, left: 0 } as const);
  const dayBoundaryLabels =
    direction === "rtl"
      ? [t.time.dusk, `${t.time.now} · ${clock}`, t.time.dawn]
      : [t.time.dawn, `${t.time.now} · ${clock}`, t.time.dusk];

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const title = draft.trim();
    if (!title) return;
    setDraft("");
    try {
      const created = await api.createTask({ title });
      setTasks((prev) => [...prev, created]);
    } catch {
      setError(t.errors.taskSave);
      setDraft(title);
    }
  }

  async function toggleComplete(task: Task) {
    if (task.status === "done") return;
    try {
      const updated = await api.completeTask(task.id);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch {
      setError(t.errors.taskUpdate);
    }
  }

  async function handleJournalSubmit(event: React.FormEvent) {
    event.preventDefault();
    const text = journalDraft.trim();
    if (!text) return;
    setJournalStatus("sending");
    try {
      const result = await api.submitJournal(text);
      setJournalEvents((prev) => [...result.extracted_events, ...prev]);
      setJournalDraft("");
      setJournalStatus("sent");
      void refreshLifeContext();
    } catch {
      setJournalStatus("idle");
      setError(t.errors.journalSave);
    }
  }

  async function handlePlanTomorrow() {
    setPlanStatus("loading");
    setPlanMessage(null);
    try {
      const result = await api.planTomorrow();
      setPlan(result);
      setPlanStatus("idle");
    } catch (err) {
      setPlanStatus("unavailable");
      setPlanMessage(err instanceof Error ? err.message : t.planner.unavailable);
    }
  }

  async function handleRoutineSubmit(event: React.FormEvent) {
    event.preventDefault();
    const name = routineName.trim();
    if (!name) return;
    setRoutineName("");
    setRoutineCategory("");
    try {
      const created = await api.createRoutine({
        name,
        category: routineCategory.trim(),
        schedule_rule: "FREQ=DAILY",
      });
      setRoutines((prev) => [...prev, created]);
      const occurrence = await api.ensureRoutineToday(created.id);
      setOccurrences((prev) => ({ ...prev, [created.id]: occurrence }));
    } catch {
      setError(t.errors.routineSave);
      setRoutineName(name);
    }
  }

  async function prepareRoutine(routine: Routine) {
    try {
      const occurrence = await api.ensureRoutineToday(routine.id);
      setOccurrences((prev) => ({ ...prev, [routine.id]: occurrence }));
    } catch {
      setError(t.errors.routinePrepare);
    }
  }

  async function fulfillRoutine(routine: Routine) {
    const occurrence = occurrences[routine.id] ?? (await api.ensureRoutineToday(routine.id));
    if (!occurrence) return;
    try {
      const updated = await api.fulfillOccurrence(occurrence.id);
      setOccurrences((prev) => ({ ...prev, [routine.id]: updated }));
      const taskLikeEvent: ExtractedEvent = {
        id: updated.id,
        type: "habit_check",
        title: routine.name,
        mood_valence: null,
      };
      setJournalEvents((prev) => [taskLikeEvent, ...prev]);
    } catch {
      setError(t.errors.routineFulfill);
    }
  }

  async function skipRoutine(routine: Routine) {
    const occurrence = occurrences[routine.id] ?? (await api.ensureRoutineToday(routine.id));
    if (!occurrence) return;
    const reason = window.prompt(t.routines.reasonPrompt);
    if (reason == null) return;
    try {
      const updated = await api.skipOccurrence(occurrence.id, reason.trim());
      setOccurrences((prev) => ({ ...prev, [routine.id]: updated }));
    } catch {
      setError(t.errors.routineSkip);
    }
  }

  async function handlePersonSubmit(event: React.FormEvent) {
    event.preventDefault();
    const display_name = personName.trim();
    if (!display_name) return;
    setPersonName("");
    setRelationshipLabel("");
    try {
      const created = await api.createPerson({
        display_name,
        relationship_label: relationshipLabel.trim(),
      });
      setPeople((prev) => [...prev.filter((person) => person.id !== created.id), created]);
    } catch {
      setError(t.errors.personSave);
      setPersonName(display_name);
    }
  }

  async function editPersonLabel(person: Person) {
    const nextLabel = window.prompt(t.relationships.labelPrompt, person.relationship_label);
    if (nextLabel == null) return;
    try {
      const updated = await api.updatePerson(person.id, {
        relationship_label: nextLabel.trim(),
        aliases: person.aliases,
      });
      setPeople((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch {
      setError(t.errors.personSave);
    }
  }

  const routineStatusLabel = (occurrence: RoutineOccurrence | null | undefined) =>
    occurrence ? t.routines.status[occurrence.status] : t.routines.notPrepared;

  const predicateLabel = (predicate: string) =>
    predicate === "involves" ? t.relationships.predicate.involves : predicate;

  return (
    <div className="page">
      <div className="sheet">
        <div className="app-controls" aria-label={`${t.controls.language} / ${t.controls.theme}`}>
          <div className="segmented" aria-label={t.controls.language}>
            {LANGUAGES.map((option) => (
              <button
                key={option}
                type="button"
                className={option === language ? "segmented__button active" : "segmented__button"}
                onClick={() => setLanguage(option)}
                aria-pressed={option === language}
              >
                {option === "en" ? t.controls.english : t.controls.persian}
              </button>
            ))}
          </div>
          <div className="segmented" aria-label={t.controls.theme}>
            {THEMES.map((option) => (
              <button
                key={option}
                type="button"
                className={option === theme ? "segmented__button active" : "segmented__button"}
                onClick={() => setTheme(option)}
                aria-pressed={option === theme}
              >
                {option === "dark" ? t.controls.dark : t.controls.light}
              </button>
            ))}
          </div>
        </div>

        <p className="eyebrow">{t.time.today}</p>
        <h1 className="date-heading">
          {dayName}, {dayDate}
        </h1>

        <div className="day-progress">
          <div className="day-progress__track">
            <div className="day-progress__fill" style={progressFillStyle} />
            <div className="day-progress__marker" style={progressPositionStyle} />
          </div>
          <div className="day-progress__label">
            <span>{dayBoundaryLabels[0]}</span>
            <strong>{dayBoundaryLabels[1]}</strong>
            <span>{dayBoundaryLabels[2]}</span>
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {tasks.length === 0 ? (
          <p className="empty-state">{t.task.empty}</p>
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
                    task.status === "done"
                      ? t.task.doneAria(task.title)
                      : t.task.markDoneAria(task.title)
                  }
                />
                <div className="task__body">
                  <div className={`task__title ${task.status === "done" ? "task__title--done" : ""}`}>
                    {task.title}
                  </div>
                  <div className="task__meta">
                    {task.estimated_minutes != null && (
                      <span>{t.time.minutes(numberFormat.format(task.estimated_minutes))}</span>
                    )}
                    <ImportanceDots
                      label={t.task.importanceAria(numberFormat.format(task.importance))}
                      level={task.importance}
                    />
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
              placeholder={t.task.addPlaceholder}
              aria-label={t.task.addAria}
            />
          </div>
          <p className="capture__hint">{t.task.hint}</p>
        </form>

        <section className="section">
          <p className="eyebrow">{t.journal.eyebrow}</p>
          <h2 className="section-heading">{t.journal.heading}</h2>
          <form onSubmit={handleJournalSubmit}>
            <textarea
              className="journal-textarea"
              value={journalDraft}
              onChange={(event) => setJournalDraft(event.target.value)}
              placeholder={t.journal.placeholder}
              rows={4}
            />
            <button
              type="submit"
              className="btn"
              disabled={journalStatus === "sending" || !journalDraft.trim()}
            >
              {journalStatus === "sending" ? t.journal.saving : t.journal.save}
            </button>
          </form>

          {journalEvents.length > 0 && (
            <ul className="chip-list">
              {journalEvents.map((ev) => (
                <li className="chip" key={ev.id}>
                  <span className={`chip__dot chip__dot--${ev.type}`} />
                  {ev.title}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="section">
          <p className="eyebrow">{t.planner.eyebrow}</p>
          <h2 className="section-heading">{t.planner.heading}</h2>
          <button
            type="button"
            className="btn"
            onClick={handlePlanTomorrow}
            disabled={planStatus === "loading"}
          >
            {planStatus === "loading" ? t.planner.loading : t.planner.action}
          </button>

          {planStatus === "unavailable" && (
            <p className="plan-message">
              {planMessage ?? t.planner.unavailable}
            </p>
          )}

          {plan && (
            <ol className="plan-list">
              {plan.blocks.map((block, i) => (
                <li className="plan-block" key={i}>
                  <span className="plan-block__time">
                    {block.start}–{block.end}
                  </span>
                  <div>
                    <div className="plan-block__activity">{block.activity}</div>
                    <div className="plan-block__reason">{block.reason}</div>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="section">
          <p className="eyebrow">{t.routines.eyebrow}</p>
          <h2 className="section-heading">{t.routines.heading}</h2>
          <form className="inline-form" onSubmit={handleRoutineSubmit}>
            <input
              className="inline-input"
              value={routineName}
              onChange={(event) => setRoutineName(event.target.value)}
              placeholder={t.routines.namePlaceholder}
              aria-label={t.routines.nameAria}
            />
            <input
              className="inline-input inline-input--compact"
              value={routineCategory}
              onChange={(event) => setRoutineCategory(event.target.value)}
              placeholder={t.routines.categoryPlaceholder}
              aria-label={t.routines.categoryAria}
            />
            <button type="submit" className="btn btn--inline" disabled={!routineName.trim()}>
              {t.routines.add}
            </button>
          </form>

          <ul className="routine-list">
            {routines.map((routine) => {
              const occurrence = occurrences[routine.id];
              return (
                <li className="routine" key={routine.id}>
                  <div className="routine__body">
                    <div className="routine__name">{routine.name}</div>
                    <div className="routine__meta">
                      {routine.category || t.routines.daily} · {routineStatusLabel(occurrence)}
                    </div>
                  </div>
                  <div className="routine__actions">
                    <button type="button" className="mini-btn" onClick={() => prepareRoutine(routine)}>
                      {t.routines.today}
                    </button>
                    <button
                      type="button"
                      className="mini-btn"
                      onClick={() => fulfillRoutine(routine)}
                      disabled={occurrence?.status === "fulfilled"}
                    >
                      {t.routines.done}
                    </button>
                    <button
                      type="button"
                      className="mini-btn"
                      onClick={() => skipRoutine(routine)}
                      disabled={occurrence?.status === "skipped"}
                    >
                      {t.routines.skip}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>

        <section className="section">
          <p className="eyebrow">{t.relationships.eyebrow}</p>
          <h2 className="section-heading">{t.relationships.heading}</h2>
          <form className="inline-form" onSubmit={handlePersonSubmit}>
            <input
              className="inline-input"
              value={personName}
              onChange={(event) => setPersonName(event.target.value)}
              placeholder={t.relationships.personPlaceholder}
              aria-label={t.relationships.personAria}
            />
            <input
              className="inline-input inline-input--compact"
              value={relationshipLabel}
              onChange={(event) => setRelationshipLabel(event.target.value)}
              placeholder={t.relationships.relationshipPlaceholder}
              aria-label={t.relationships.relationshipAria}
            />
            <button type="submit" className="btn btn--inline" disabled={!personName.trim()}>
              {t.relationships.add}
            </button>
          </form>

          {people.length > 0 && (
            <ul className="people-list">
              {people.map((person) => (
                <li className="person" key={person.id}>
                  <span>{person.display_name}</span>
                  {person.relationship_label && <small>{person.relationship_label}</small>}
                  <button
                    type="button"
                    className="person__edit"
                    onClick={() => editPersonLabel(person)}
                  >
                    {t.relationships.editLabel}
                  </button>
                </li>
              ))}
            </ul>
          )}

          {edges.length > 0 && (
            <ol className="edge-list">
              {edges.map((edge) => (
                <li className="edge" key={edge.id}>
                  <span>{edge.subject_label}</span>
                  <strong>{predicateLabel(edge.predicate)}</strong>
                  <span>{edge.object_label}</span>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>
    </div>
  );
}
