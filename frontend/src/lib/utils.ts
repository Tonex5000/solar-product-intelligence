import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDuration(days: number): string {
  if (days < 30) return `${days} days`
  if (days < 365) return `${(days / 30).toFixed(1)} months`
  const years = days / 365
  return `${years.toFixed(1)} years`
}

export function getHealthColor(health: number): string {
  if (health >= 80) return 'text-success'
  if (health >= 50) return 'text-warning'
  return 'text-danger'
}

export function getHealthBgColor(health: number): string {
  if (health >= 80) return 'bg-success/20'
  if (health >= 50) return 'bg-warning/20'
  return 'bg-danger/20'
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'optimal':
    case 'success':
      return 'text-success'
    case 'normal':
    case 'info':
      return 'text-primary'
    case 'warning':
      return 'text-warning'
    case 'failure':
    case 'danger':
    case 'critical':
      return 'text-danger'
    default:
      return 'text-muted-foreground'
  }
}

export function getNodeGlowClass(status: string): string {
  switch (status) {
    case 'optimal':
      return 'node-glow-optimal'
    case 'normal':
      return 'node-glow-normal'
    case 'warning':
      return 'node-glow-warning'
    case 'failure':
      return 'node-glow-failure'
    default:
      return ''
  }
}
