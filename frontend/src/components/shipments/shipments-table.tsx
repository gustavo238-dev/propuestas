import { shipments } from "@/lib/mock-data";
import { StatusBadge } from "@/components/ui/status-badge";

export function ShipmentsTable() {
  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Embarques activos</h2>
          <p className="text-sm text-slate-500">Seguimiento operativo de MBL, HBL, ETA y DTA</p>
        </div>
        <button className="rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" type="button">
          Nuevo embarque
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-line bg-slate-50 text-left text-xs uppercase text-slate-500">
              <th className="px-5 py-3">Embarque</th>
              <th className="px-5 py-3">Cliente</th>
              <th className="px-5 py-3">MBL / HBL</th>
              <th className="px-5 py-3">Ruta</th>
              <th className="px-5 py-3">ETA / DTA</th>
              <th className="px-5 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            {shipments.map((shipment) => (
              <tr key={shipment.id} className="border-b border-line last:border-0">
                <td className="px-5 py-4">
                  <p className="font-semibold text-ink">{shipment.id}</p>
                  <p className="text-xs text-slate-500">{shipment.type} · {shipment.containers} cont.</p>
                </td>
                <td className="px-5 py-4 text-slate-700">{shipment.client}</td>
                <td className="px-5 py-4">
                  <p className="font-medium text-slate-800">{shipment.mbl}</p>
                  <p className="text-xs text-slate-500">{shipment.hbl}</p>
                </td>
                <td className="px-5 py-4">
                  <p className="text-slate-800">{shipment.origin} -> {shipment.destination}</p>
                  <p className="text-xs text-slate-500">{shipment.vessel}</p>
                </td>
                <td className="px-5 py-4 text-slate-700">
                  <p>ETA {shipment.eta}</p>
                  <p className="text-xs text-slate-500">DTA {shipment.dta}</p>
                </td>
                <td className="px-5 py-4">
                  <StatusBadge status={shipment.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
