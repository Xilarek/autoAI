"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"
import type { ComponentProps } from "react"

// Берём все свойства от Button компонента
type ButtonProps = ComponentProps<typeof Button>

export interface BaseButtonProps extends ButtonProps {
  /** Загрузка (показывает спиннер) */
  loading?: boolean
  /** Иконка слева от текста */
  icon?: React.ReactNode
  /** Иконка справа от текста */
  iconRight?: React.ReactNode
  /** Растянуть на всю ширину */
  fullWidth?: boolean
}

export function BaseButton({ 
  children, 
  loading = false, 
  icon, 
  iconRight,
  fullWidth = false,
  className,
  ...props 
}: BaseButtonProps) {
  return (
    <Button
      className={cn(
        "cursor-pointer transition-all duration-200",
        fullWidth && "w-full",
        className
      )}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
      {!loading && icon && <span className="mr-2">{icon}</span>}
      {children}
      {!loading && iconRight && <span className="ml-2">{iconRight}</span>}
    </Button>
  )
}
