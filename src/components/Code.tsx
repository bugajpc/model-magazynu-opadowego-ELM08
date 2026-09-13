import { useMemo, useState } from "react";
import { tokenize } from "../lib/highlight";

interface CodeProps {
  /** Filename shown in the header bar. */
  title?: string;
  /** C++ source, one program statement per line. */
  code: string;
  /** 1-based line numbers to highlight (used by the loop tracer). */
  highlightLines?: number[];
  /** Compact mode: no window chrome. */
  bare?: boolean;
}

/** Syntax-highlighted C++ code block with line numbers and a copy button. */
export function Code({ title, code, highlightLines, bare }: CodeProps) {
  const lines = useMemo(() => code.replace(/\n$/, "").split("\n"), [code]);
  const tokens = useMemo(() => lines.map((l) => tokenize(l)), [lines]);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="codeblock">
      {!bare && (
        <div className="codehead">
          <span className="dots">
            <i />
            <i />
            <i />
          </span>
          <span className="codetitle">{title ?? "main.cpp"}</span>
          <button className="copybtn" onClick={copy}>
            {copied ? "Copied ✓" : "Copy"}
          </button>
        </div>
      )}
      <div className="codebody">
        {lines.map((_, i) => (
          <div key={i} className={`cl ${highlightLines?.includes(i + 1) ? "hl" : ""}`}>
            <span className="ln">{i + 1}</span>
            <span className="lt">
              {tokens[i].map((t, j) => (
                <span key={j} className={t.cls}>
                  {t.text}
                </span>
              ))}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
