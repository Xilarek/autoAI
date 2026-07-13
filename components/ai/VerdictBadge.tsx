"use client"

import { Badge } from "@/components/ui/badge"
import { VERDICT_CONFIG } from "@/lib/constants"
import type { ListingOut } from "@/types/api"

interface VerdictBadgeProps {
  verdict: ListingOut["verdict"]
  showLabel?: boolean
}

export function VerdictBadge({ verdict, showLabel = true }: VerdictBadgeProps) {
  const v = verdict || "ДУМАТЬ"
  const config = VERDICT_CONFIG[v] || VERDICT_CONFIG["ДУМАТЬ"]

  return (
    <Badge className={`${config.bg} ${config.color} border-0 text-xs`}>
      {showLabel ? config.label : ""}
    </Badge>
  )
}
