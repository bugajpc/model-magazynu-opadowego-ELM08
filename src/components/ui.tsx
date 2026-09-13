import type { ReactNode } from "react";

/** Paragraph */
export function P({ children }: { children: ReactNode }) {
  return <p className="p">{children}</p>;
}

export function H2({ children, id }: { children: ReactNode; id?: string }) {
  return (
    <h2 id={id}>
      {children}
    </h2>
  );
}

export function H3({ children }: { children: ReactNode }) {
  return <h3>{children}</h3>;
}

/** Inline code */
export function IC({ children }: { children: ReactNode }) {
  return <code className="ic">{children}</code>;
}

export type CalloutKind = "info" | "tip" | "warn" | "danger" | "def";

const CALLOUT_ICONS: Record<CalloutKind, string> = {
  info: "ℹ",
  tip: "✓",
  warn: "⚠",
  danger: "✕",
  def: "✦",
};

const CALLOUT_DEFAULT_TITLES: Record<CalloutKind, string> = {
  info: "Good to know",
  tip: "Pro tip",
  warn: "Common pitfall",
  danger: "Danger — undefined behavior",
  def: "Definition",
};

export function Callout({
  kind = "info",
  title,
  children,
}: {
  kind?: CalloutKind;
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className={`callout c-${kind}`}>
      <div className="callout-title">
        <span>{CALLOUT_ICONS[kind]}</span>
        {title ?? CALLOUT_DEFAULT_TITLES[kind]}
      </div>
      <div className="callout-body">{children}</div>
    </div>
  );
}

export interface NavTarget {
  id: string;
  num: string;
  title: string;
}

/** Section header + prev/next navigation footer */
export function SectionShell({
  num,
  phase,
  title,
  tagline,
  skills,
  prev,
  next,
  onNav,
  children,
}: {
  num: string;
  phase: string;
  title: string;
  tagline: string;
  skills?: string[];
  prev?: NavTarget;
  next?: NavTarget;
  onNav: (id: string) => void;
  children: ReactNode;
}) {
  return (
    <div>
      <header className="sec-head">
        <div className="sec-phase">
          {phase} · Unit {num}
        </div>
        <h1 className="sec-title">{title}</h1>
        <p className="sec-tagline">{tagline}</p>
        {skills && skills.length > 0 && (
          <div className="skillrow">
            {skills.map((s) => (
              <span className="skillchip" key={s}>
                <b>◆</b>
                {s}
              </span>
            ))}
          </div>
        )}
      </header>
      {children}
      <nav className="sec-nav">
        {prev ? (
          <button className="sec-navbtn" onClick={() => onNav(prev.id)}>
            <div className="dir">← Previous</div>
            <div className="tt">
              {prev.num}. {prev.title}
            </div>
          </button>
        ) : (
          <span />
        )}
        {next ? (
          <button className="sec-navbtn next" onClick={() => onNav(next.id)}>
            <div className="dir">Next →</div>
            <div className="tt">
              {next.num}. {next.title}
            </div>
          </button>
        ) : (
          <span />
        )}
      </nav>
    </div>
  );
}
