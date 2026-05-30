import { ShipmentStatus } from "@/types/logistics";

const statusLabels: Record<ShipmentStatus, string> = {
  CREATED: "Creado",
  DOCUMENT_REVIEW: "Revision documental",
  IN_TRANSIT: "En transito",
  ARRIVED: "Arribado",
  RELEASED: "Liberado"
};

const statusClasses: Record<ShipmentStatus, string> = {
  CREATED: "bg-slate-100 text-slate-700",
  DOCUMENT_REVIEW: "bg-amber-100 text-amber-800",
  IN_TRANSIT: "bg-sky-100 text-sky-800",
  ARRIVED: "bg-teal-100 text-teal-800",
  RELEASED: "bg-emerald-100 text-emerald-800"
};

export function StatusBadge({ status }: { status: ShipmentStatus }) {
  return (
    <span className={`inline-flex min-w-28 items-center justify-center rounded px-2.5 py-1 text-xs font-semibold ${statusClasses[status]}`}>
      {statusLabels[status]}
    </span>
  );
}
