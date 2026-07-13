import { cn } from "@/lib/utils"

type Verdict = "ЗВОНИТЬ" | "ТОРГОВАТЬСЯ" | "ДУМАТЬ" | "БЕЖАТЬ" | string

const VERDICT_STYLES: Record<string, string> = {
  "ЗВОНИТЬ": "bg-green-100 text-green-700 border-green-200",
  "ТОРГОВАТЬСЯ": "bg-blue-100 text-blue-700 border-blue-200",
  "ДУМАТЬ": "bg-yellow-100 text-yellow-700 border-yellow-200",
  "БЕЖАТЬ": "bg-red-100 text-red-700 border-red-200",
}

interface VerdictBadgeProps {
  verdict: Verdict
  className?: string
}

export function VerdictBadge({ verdict, className }: VerdictBadgeProps) {
  const styles = VERDICT_STYLES[verdict] || VERDICT_STYLES["ДУМАТЬ"]
  
  return (
    <span className={cn("px-2.5 py-1 rounded-full text-xs font-semibold border shadow-sm", styles, className)}>
      {verdict}
    </span>
  )
}
