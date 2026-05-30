import { FileCheck2, ScanLine, Send } from "lucide-react";

import { documents } from "@/lib/mock-data";

export function DocumentCenter() {
  return (
    <section className="rounded border border-line bg-white p-5 shadow-panel">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-ink">Centro documental</h2>
          <p className="text-sm text-slate-500">PDFs, OCR, validacion y documentos generados</p>
        </div>
        <button className="rounded border border-line px-3 py-2 text-sm font-semibold text-ink" type="button">
          Cargar PDF
        </button>
      </div>
      <div className="space-y-3">
        {documents.map((document) => (
          <div key={document.id} className="rounded border border-line p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{document.name}</p>
                <p className="text-sm text-slate-500">{document.type} · {document.shipment}</p>
              </div>
              <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
                {document.status}
              </span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
              <FileCheck2 className="h-4 w-4" />
              <span>{document.updatedAt}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-5 grid grid-cols-3 gap-2">
        <button className="flex h-10 items-center justify-center rounded bg-signal text-white" title="Ejecutar OCR" type="button">
          <ScanLine className="h-4 w-4" />
        </button>
        <button className="flex h-10 items-center justify-center rounded bg-cargo text-white" title="Generar PDF" type="button">
          <FileCheck2 className="h-4 w-4" />
        </button>
        <button className="flex h-10 items-center justify-center rounded bg-harbor text-white" title="Enviar por correo" type="button">
          <Send className="h-4 w-4" />
        </button>
      </div>
    </section>
  );
}
