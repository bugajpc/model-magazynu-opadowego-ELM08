/**
 * Small, dependency-free C++ syntax tokenizer used by the Code component.
 * One line at a time; good enough for teaching snippets.
 */
export interface Token {
  text: string;
  cls: string;
}

const KEYWORDS = new Set([
  "if", "else", "for", "while", "do", "switch", "case", "default",
  "break", "continue", "return", "goto", "class", "struct", "union",
  "public", "private", "protected", "virtual", "override", "final",
  "new", "delete", "try", "catch", "throw", "template", "typename",
  "namespace", "using", "constexpr", "const", "static", "extern",
  "inline", "noexcept", "this", "nullptr", "true", "false", "and",
  "or", "not", "operator", "friend", "nullptr_t", "size_t",
]);

const TYPES = new Set([
  "int", "float", "double", "char", "bool", "void", "auto", "long",
  "short", "unsigned", "signed", "string", "vector", "map", "list",
  "set", "pair", "array", "size_t", "wstring",
]);

/** tokenize a single line of C++ (multi-line block comments are not tracked) */
export function tokenize(line: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  const n = line.length;

  const push = (text: string, cls: string) => {
    if (text) out.push({ text, cls });
  };
  const isIdentStart = (c: string) => /[A-Za-z_]/.test(c);
  const isIdentChar = (c: string) => /[A-Za-z0-9_]/.test(c);
  const isDigit = (c: string) => c >= "0" && c <= "9";

  // preprocessor: '#include', '#define', ... whole line
  const m = line.match(/^(\s*)(#\s*[\w\s]*)/);
  if (m && line.trimStart().startsWith("#")) {
    const rest = line.slice(0);
    push(line, "tk-preproc");
    return out;
  }

  while (i < n) {
    const c = line[i];

    // whitespace
    if (c === " " || c === "\t") {
      let j = i;
      while (j < n && (line[j] === " " || line[j] === "\t")) j++;
      push(line.slice(i, j), "tk-ident");
      i = j;
      continue;
    }

    // line comment
    if (c === "/" && line[i + 1] === "/") {
      push(line.slice(i), "tk-comment");
      break;
    }

    // block comment (single-line handling)
    if (c === "/" && line[i + 1] === "*") {
      const end = line.indexOf("*/", i + 2);
      const stop = end === -1 ? n : end + 2;
      push(line.slice(i, stop), "tk-comment");
      i = stop;
      continue;
    }

    // string literal
    if (c === '"') {
      let j = i + 1;
      while (j < n && line[j] !== '"') {
        if (line[j] === "\\") j++;
        j++;
      }
      j = Math.min(j + 1, n);
      push(line.slice(i, j), "tk-string");
      i = j;
      continue;
    }

    // char literal
    if (c === "'") {
      let j = i + 1;
      while (j < n && line[j] !== "'") {
        if (line[j] === "\\") j++;
        j++;
      }
      j = Math.min(j + 1, n);
      push(line.slice(i, j), "tk-char");
      i = j;
      continue;
    }

    // number (dec, hex, float-ish)
    if (isDigit(c) || (c === "." && isDigit(line[i + 1] ?? ""))) {
      let j = i;
      if (line[j] === "0" && (line[j + 1] === "x" || line[j + 1] === "X")) j += 2;
      while (j < n && /[A-Za-z0-9._xXa-fA-F]/.test(line[j])) j++;
      push(line.slice(i, j), "tk-number");
      i = j;
      continue;
    }

    // identifier / keyword / type / function
    if (isIdentStart(c)) {
      let j = i;
      while (j < n && isIdentChar(line[j])) j++;
      const word = line.slice(i, j);
      let k = j;
      while (k < n && (line[k] === " " || line[k] === "\t")) k++;
      let cls = "tk-ident";
      if (word === "std" || word === "using") cls = "tk-type";
      else if (KEYWORDS.has(word)) cls = "tk-keyword";
      else if (TYPES.has(word)) cls = "tk-type";
      else if (line[k] === "(") cls = "tk-func";
      push(word, cls);
      i = j;
      continue;
    }

    // operators & punctuation
    if ("=+-*/%<>!&|^~?:,;(){}[]".includes(c)) {
      push(c, "tk-op");
      i++;
      continue;
    }

    // fallback: plain
    push(c, "tk-ident");
    i++;
  }

  return out;
}
