import { useEffect, useState, type ReactNode } from "react";
import { Code } from "./Code";
import { useItemDone, useProgress } from "../lib/progress";

/** Normalize free-typed answers: trim, collapse whitespace, lowercase. */
function norm(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

/* ================================ Quiz ================================ */

interface QuizProps {
  id: string;
  prompt: ReactNode;
  options: ReactNode[];
  /** Index of the correct option. */
  answer: number;
  explain: ReactNode;
}

/** Multiple-choice quiz; stays open until answered correctly. */
export function Quiz({ id, prompt, options, answer, explain }: QuizProps) {
  const [done, markDone] = useItemDone(id);
  const [picked, setPicked] = useState<number | null>(null);
  const correct = picked === answer;

  return (
    <div className={`card ${done ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag">Check yourself</span>
        {done && <span className="donechip">Solved ✓</span>}
      </div>
      <div className="q-prompt">{prompt}</div>
      <div className="q-opts">
        {options.map((o, i) => {
          const cls =
            picked === null ? "" : i === answer ? "ok" : i === picked ? "bad" : "";
          return (
            <button
              key={i}
              disabled={done}
              className={`qopt ${cls}`}
              onClick={() => {
                setPicked(i);
                if (i === answer) markDone();
              }}
            >
              <span className="ql">{String.fromCharCode(65 + i)}</span>
              <span>{o}</span>
            </button>
          );
        })}
      </div>
      {picked !== null && (
        <div className={`q-explain ${correct ? "ok" : "bad"}`}>
          {correct ? "Correct. " : "Not quite — try again. "}
          {explain}
        </div>
      )}
    </div>
  );
}

/* =========================== Predict output =========================== */

interface PredictOutputProps {
  id: string;
  prompt: ReactNode;
  /** Shown above the answer box when provided. */
  code?: string;
  codeTitle?: string;
  /** Acceptable outputs (compared case-insensitively, whitespace-collapsed). */
  accept: string[];
  explain: ReactNode;
}

/** "What does this print?" — student types the exact console output. */
export function PredictOutput({
  id,
  prompt,
  code,
  codeTitle,
  accept,
  explain,
}: PredictOutputProps) {
  const [done, markDone] = useItemDone(id);
  const [val, setVal] = useState("");
  const [state, setState] = useState<"idle" | "ok" | "bad">("idle");

  const check = () => {
    if (accept.some((a) => norm(a) === norm(val))) {
      setState("ok");
      markDone();
    } else {
      setState("bad");
    }
  };

  return (
    <div className={`card ${done ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag a">Predict the output</span>
        {done && <span className="donechip">Solved ✓</span>}
      </div>
      <div className="q-prompt">{prompt}</div>
      {code && <Code title={codeTitle} code={code} bare />}
      <textarea
        className="pred-input"
        rows={2}
        placeholder="Type the exact output the program prints…"
        value={val}
        disabled={done}
        onChange={(e) => {
          setVal(e.target.value);
          setState("idle");
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            check();
          }
        }}
      />
      <div className="btnrow">
        <button className="btn primary" onClick={check} disabled={done || !val.trim()}>
          Check output
        </button>
      </div>
      {state === "bad" && !done && (
        <div className="q-explain bad">
          Not exactly — watch whitespace, newlines and case, then try again.
        </div>
      )}
      {done && <div className="q-explain ok">{explain}</div>}
    </div>
  );
}

/* ============================= Loop tracer ============================= */

export interface TraceRow {
  /** Current value per column. */
  values: Record<string, string>;
  /** 1-based line of the program that is executing (highlighted). */
  line?: number;
  /** Explanatory note for this step. */
  note?: string;
}

interface LoopTracerProps {
  id: string;
  title: string;
  code: string;
  cols: string[];
  rows: TraceRow[];
}

/** Step-through simulator: watch variables change as the loop executes. */
export function LoopTracer({ id, title, code, cols, rows }: LoopTracerProps) {
  const [done, markDone] = useItemDone(id);
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const last = rows.length - 1;
  const cur = rows[Math.min(step, last)];
  const atEnd = step >= last;

  useEffect(() => {
    if (!playing) return;
    if (atEnd) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setStep((s) => s + 1), 1200);
    return () => clearTimeout(t);
  }, [playing, atEnd]);

  useEffect(() => {
    if (atEnd) markDone();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [atEnd]);

  return (
    <div className={`card ${done ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag g">Execute step by step</span>
        {done && <span className="donechip">Traced ✓</span>}
      </div>
      <div className="q-prompt">{title}</div>
      <div className="tracer-controls">
        <button
          className="btn"
          onClick={() => {
            setPlaying(false);
            setStep(0);
          }}
        >
          ⏮ Reset
        </button>
        <button
          className="btn"
          disabled={step === 0}
          onClick={() => {
            setPlaying(false);
            setStep((s) => Math.max(0, s - 1));
          }}
        >
          ◀ Back
        </button>
        <button
          className="btn primary"
          onClick={() => {
            if (atEnd && !playing) setStep(0);
            setPlaying((p) => !p);
          }}
        >
          {playing ? "❚❚ Pause" : "▶ Play"}
        </button>
        <button
          className="btn"
          disabled={atEnd}
          onClick={() => {
            setPlaying(false);
            setStep((s) => Math.min(last, s + 1));
          }}
        >
          Step ▶
        </button>
        <span className="stepinfo">
          step {Math.min(step, last) + 1} / {rows.length}
        </span>
      </div>
      <Code code={code} highlightLines={cur.line ? [cur.line] : undefined} bare />
      <table className="trace-table">
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {cols.map((c) => (
              <td key={c}>{cur.values[c] ?? ""}</td>
            ))}
          </tr>
        </tbody>
      </table>
      <div className="tracer-note">{cur.note ?? ""}</div>
    </div>
  );
}

/* ============================ Code challenge ============================ */

export interface Req {
  /** Tested against the student's full code. */
  pattern: RegExp;
  message: string;
}

interface CodeChallengeProps {
  id: string;
  prompt: ReactNode;
  /** Starter code in the editor. */
  starter: string;
  requirements: Req[];
  hints?: ReactNode[];
  /** Revealed after two failed checks. */
  solution: string;
}

/** Student edits real code; checks run structural requirements on it. */
export function CodeChallenge({
  id,
  prompt,
  starter,
  requirements,
  hints,
  solution,
}: CodeChallengeProps) {
  const [done, markDone] = useItemDone(id);
  const [val, setVal] = useState(starter);
  const [results, setResults] = useState<boolean[] | null>(null);
  const [fails, setFails] = useState(0);
  const [hintOpen, setHintOpen] = useState(false);
  const [solutionOpen, setSolutionOpen] = useState(false);

  const check = () => {
    const r = requirements.map((req) => req.pattern.test(val));
    setResults(r);
    if (r.every(Boolean)) {
      markDone();
    } else {
      setFails((f) => f + 1);
    }
  };

  return (
    <div className={`card ${done ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag g">Coding challenge</span>
        {done && <span className="donechip">Solved ✓</span>}
      </div>
      <div className="q-prompt">{prompt}</div>
      <textarea
        className="editor"
        rows={11}
        spellCheck={false}
        value={val}
        disabled={done}
        onChange={(e) => setVal(e.target.value)}
      />
      <ul className="reqlist">
        {requirements.map((r, i) => (
          <li key={i} className={results ? (results[i] ? "pass" : "fail") : ""}>
            <span className="rmark">
              {results ? (results[i] ? "✓" : "✗") : "•"}
            </span>
            <span>{r.message}</span>
          </li>
        ))}
      </ul>
      <div className="btnrow" style={{ marginTop: 12 }}>
        <button className="btn primary" onClick={check} disabled={done}>
          Check my code
        </button>
        {hints && hints.length > 0 && !hintOpen && (
          <button className="btn" onClick={() => setHintOpen(true)}>
            Show a hint
          </button>
        )}
        {hintOpen && <div className="q-explain ok">{hints?.[0]}</div>}
        {fails >= 2 && !solutionOpen && !done && (
          <button className="btn" onClick={() => setSolutionOpen(true)}>
            I'm stuck — show solution
          </button>
        )}
      </div>
      {solutionOpen && (
        <div style={{ marginTop: 12 }}>
          <h3>One possible solution</h3>
          <Code code={solution} />
        </div>
      )}
    </div>
  );
}

/* =============================== Fill code =============================== */

interface FillCodeProps {
  id: string;
  prompt: ReactNode;
  /** Full program; each `___` placeholder (one per line) must be filled. */
  code: string;
  /** Expected answer per placeholder (case-insensitive, whitespace-collapsed). */
  expected: string[];
  hint?: string;
}

/** Complete the missing source lines in context. */
export function FillCode({ id, prompt, code, expected, hint }: FillCodeProps) {
  const [done, markDone] = useItemDone(id);
  const [vals, setVals] = useState<string[]>(() => expected.map(() => ""));
  const [states, setStates] = useState<("idle" | "ok" | "bad")[]>(() =>
    expected.map(() => "idle"),
  );
  const [hintOpen, setHintOpen] = useState(false);

  const lines = code.replace(/\n$/, "").split("\n");
  let blank = -1;

  const check = () => {
    const next = vals.map((v, i) => (norm(v) === norm(expected[i]) ? "ok" : "bad"));
    setStates(next);
    if (next.every((s) => s === "ok")) markDone();
  };

  return (
    <div className={`card ${done ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag">Fill in the blanks</span>
        {done && <span className="donechip">Solved ✓</span>}
      </div>
      <div className="q-prompt">{prompt}</div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 13.5, background: "var(--bg2)", border: "1px solid var(--line)", borderRadius: 10, padding: "12px 14px" }}>
        {lines.map((l, i) => {
          if (!l.includes("___")) {
            return (
              <div key={i} style={{ whiteSpace: "pre", color: "#9fb3cf" }}>
                {l}
              </div>
            );
          }
          blank += 1;
          const bi = blank;
          return (
            <div className="fillline" key={i}>
              <input
                value={vals[bi]}
                disabled={done}
                className={states[bi]}
                placeholder="type the missing line here"
                onChange={(e) => {
                  const v = [...vals];
                  v[bi] = e.target.value;
                  setVals(v);
                  const s = [...states];
                  s[bi] = "idle";
                  setStates(s);
                }}
              />
            </div>
          );
        })}
      </div>
      <div className="btnrow" style={{ marginTop: 10 }}>
        <button className="btn primary" onClick={check} disabled={done}>
          Check
        </button>
        {hint && !hintOpen && (
          <button className="btn" onClick={() => setHintOpen(true)}>
            Hint
          </button>
        )}
      </div>
      {hintOpen && <div className="q-explain ok" style={{ marginTop: 10 }}>{hint}</div>}
    </div>
  );
}

/* =============================== Checklist =============================== */

interface ChecklistProps {
  id: string;
  items: string[];
}

/** Persistent to-do checklist (each item can be toggled). */
export function Checklist({ id, items }: ChecklistProps) {
  const { map, sectionId, setKey } = useProgress();
  const keyFor = (i: number) => `${sectionId}/${id}:${i}`;
  const on = items.map((_, i) => !!map[keyFor(i)]);
  const count = on.filter(Boolean).length;

  return (
    <div className={`card ${count === items.length ? "done" : ""}`}>
      <div className="card-label">
        <span className="tag a">Project checklist</span>
        {count === items.length && <span className="donechip">Complete ✓</span>}
      </div>
      <div className="checklist">
        {items.map((item, i) => (
          <div
            key={i}
            className={`chkrow ${on[i] ? "on" : ""}`}
            onClick={() => setKey(keyFor(i), !on[i])}
          >
            <span className="box">✓</span>
            <span className="txt">{item}</span>
          </div>
        ))}
      </div>
      <div className="chkfoot">
        {count} of {items.length} completed — your progress is saved in this browser.
      </div>
    </div>
  );
}
