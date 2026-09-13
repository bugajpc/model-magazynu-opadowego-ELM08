import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

/**
 * Lightweight progress store (localStorage-backed).
 * Keys are `${sectionId}/${itemId}`.
 */
const STORAGE_KEY = "cpp-fundamentals-progress-v1";

export type ProgressMap = Record<string, true>;

interface ProgressCtx {
  map: ProgressMap;
  sectionId: string;
  /** mark an interactive item of the current section complete */
  markDone: (itemId: string) => void;
  /** set an absolute key (used by checklists) */
  setKey: (key: string, on: boolean) => void;
  resetAll: () => void;
}

const Ctx = createContext<ProgressCtx | null>(null);

function load(): ProgressMap {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ProgressMap) : {};
  } catch {
    return {};
  }
}

export function ProgressProvider({
  sectionId,
  children,
}: {
  sectionId: string;
  children: ReactNode;
}) {
  const [map, setMap] = useState<ProgressMap>(load);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
    } catch {
      /* storage unavailable — ignore */
    }
  }, [map]);

  const value = useMemo<ProgressCtx>(
    () => ({
      map,
      sectionId,
      markDone: (itemId: string) =>
        setMap((m) => {
          const key = `${sectionId}/${itemId}`;
          return m[key] ? m : { ...m, [key]: true };
        }),
      setKey: (key: string, on: boolean) =>
        setMap((m) => {
          if (on) return m[key] ? m : { ...m, [key]: true };
          const next = { ...m };
          delete next[key];
          return next;
        }),
      resetAll: () => setMap({}),
    }),
    [map, sectionId]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useProgress(): ProgressCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useProgress must be used inside ProgressProvider");
  return ctx;
}

/** done-state + completer for one interactive item of the current section */
export function useItemDone(itemId: string): [boolean, () => void] {
  const { map, sectionId, markDone } = useProgress();
  const key = `${sectionId}/${itemId}`;
  return [!!map[key], () => markDone(itemId)];
}
