import * as React from "react"
import { cn } from "@/lib/utils"

export interface ToastProps {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: React.ReactElement
  variant?: "default" | "destructive"
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export type ToastActionElement = React.ReactElement

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>
}

export const ToastViewport: React.FC<{ className?: string }> = ({ className }) => {
  return <div className={cn("fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4", className)} />
}

export const Toast: React.FC<ToastProps & { className?: string }> = ({ className, ...props }) => {
  return <div className={cn("bg-white p-4 rounded shadow", className)} {...props} />
}

export const ToastTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => {
  return <div className={cn("font-semibold", className)}>{children}</div>
}

export const ToastDescription: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => {
  return <div className={cn("text-sm opacity-90", className)}>{children}</div>
}

export const ToastClose: React.FC<{ className?: string }> = ({ className }) => {
  return <button className={cn("absolute right-2 top-2", className)}>×</button>
}

export const ToastAction = ToastClose
