export default function LoadingSpinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-ink/80">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-tide border-r-transparent" />
      <span>{label}</span>
    </div>
  );
}
