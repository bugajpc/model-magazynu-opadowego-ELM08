import type { NavTarget } from "../components/ui";

/** Props shared by every section component. */
export interface SectionProps {
  /** Navigate to another section (or "roadmap"). */
  go: (id: string) => void;
  prev?: NavTarget;
  next?: NavTarget;
}
