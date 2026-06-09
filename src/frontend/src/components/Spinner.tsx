export function Spinner({ size = 20 }: { size?: number }) {
  return (
    <div
      className="inline-block animate-spin rounded-full border-2 border-tg-border border-t-tg-accent"
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  )
}
