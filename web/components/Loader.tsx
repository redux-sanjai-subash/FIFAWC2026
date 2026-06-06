export default function Loader({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4 text-muted">
      <span className="relative grid h-11 w-11 place-items-center">
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-fg/10 border-t-gold" />
        <span className="h-1.5 w-1.5 rounded-full bg-gold" />
      </span>
      <span className="text-[0.66rem] uppercase tracking-luxe">{label}</span>
    </div>
  );
}
