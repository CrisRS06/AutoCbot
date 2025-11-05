/**
 * Utility functions for formatting and styling
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format number as currency (USD)
 */
export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "$0.00"
  }

  // For large numbers, use abbreviated format
  if (Math.abs(value) >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`
  }
  if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`
  }
  if (Math.abs(value) >= 1_000) {
    return `$${(value / 1_000).toFixed(2)}K`
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Format number as percentage
 */
export function formatPercent(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "0.00%"
  }

  return `${value.toFixed(decimals)}%`
}

/**
 * Get color class based on change value
 */
export function getChangeColor(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "text-muted-foreground"
  }

  if (value > 0) {
    return "text-success"
  } else if (value < 0) {
    return "text-danger"
  } else {
    return "text-muted-foreground"
  }
}

/**
 * Format large numbers with abbreviations
 */
export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "0"
  }

  if (Math.abs(value) >= 1_000_000_000_000) {
    return `${(value / 1_000_000_000_000).toFixed(decimals)}T`
  }
  if (Math.abs(value) >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(decimals)}B`
  }
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(decimals)}M`
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(decimals)}K`
  }

  return value.toFixed(decimals)
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, length: number = 50): string {
  if (text.length <= length) {
    return text
  }
  return text.slice(0, length) + "..."
}

/**
 * Sleep/delay utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Get status color based on string value
 */
export function getStatusColor(status: string): string {
  const statusLower = status.toLowerCase()

  if (statusLower.includes('success') || statusLower.includes('active') || statusLower.includes('healthy')) {
    return 'text-success'
  }
  if (statusLower.includes('warning') || statusLower.includes('pending')) {
    return 'text-warning'
  }
  if (statusLower.includes('error') || statusLower.includes('failed') || statusLower.includes('danger')) {
    return 'text-danger'
  }

  return 'text-muted-foreground'
}
