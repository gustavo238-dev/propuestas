import {
  Bell,
  Building2,
  FileText,
  LayoutDashboard,
  PackageCheck,
  ReceiptText,
  Ship,
  Users
} from "lucide-react";

const items = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Clientes", icon: Users },
  { label: "Empresas", icon: Building2 },
  { label: "Cotizaciones", icon: ReceiptText },
  { label: "Embarques", icon: Ship },
  { label: "Documentos", icon: FileText },
  { label: "Tracking", icon: PackageCheck },
  { label: "Notificaciones", icon: Bell }
];

export function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-72 border-r border-line bg-white px-4 py-5 lg:block">
      <div className="mb-8 px-2">
        <p className="text-sm font-semibold uppercase tracking-wider text-harbor">Logistica maritima</p>
        <h1 className="mt-2 text-xl font-bold text-ink">Importaciones</h1>
      </div>
      <nav className="space-y-1">
        {items.map((item) => (
          <button
            key={item.label}
            className={`flex h-11 w-full items-center gap-3 rounded px-3 text-left text-sm font-medium ${
              item.active ? "bg-harbor text-white" : "text-slate-600 hover:bg-slate-100"
            }`}
            type="button"
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
