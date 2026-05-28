export function TrackingPanel() {
  const events = [
    ["Recepcion PDF naviera", "OCR procesado y datos extraidos", "09:30"],
    ["Actualizacion ETA", "SHP-24051 ETA confirmada 2026-06-14", "08:50"],
    ["Cotizacion aprobada", "Pacific Trading Ltda.", "08:10"],
    ["Factura generada", "SHP-24053 disponible para envio", "Ayer"]
  ];

  return (
    <section className="rounded border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Trazabilidad operativa</h2>
      <div className="mt-4 space-y-4">
        {events.map(([title, detail, time]) => (
          <div key={`${title}-${time}`} className="flex gap-3">
            <div className="mt-1 h-2.5 w-2.5 rounded-full bg-harbor" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-3">
                <p className="font-medium text-ink">{title}</p>
                <span className="text-xs text-slate-500">{time}</span>
              </div>
              <p className="text-sm text-slate-500">{detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
