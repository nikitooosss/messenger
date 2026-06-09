import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  children: ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-tg-accent text-white hover:bg-tg-accentHover disabled:opacity-50 disabled:cursor-not-allowed',
  secondary:
    'bg-tg-sidebar text-tg-text hover:bg-tg-sidebarHover disabled:opacity-50 disabled:cursor-not-allowed',
  danger:
    'bg-tg-danger text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed',
  ghost:
    'bg-transparent text-tg-text hover:bg-tg-sidebar disabled:opacity-50 disabled:cursor-not-allowed',
}

export function Button({
  variant = 'primary',
  className = '',
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      {...rest}
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  )
}
