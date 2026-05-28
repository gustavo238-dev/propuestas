import { DocumentItem, Shipment } from "@/types/logistics";

export const shipments: Shipment[] = [
  {
    id: "SHP-24051",
    client: "Andes Import S.A.S.",
    mbl: "MAEU9283712",
    hbl: "HBL-CO-88421",
    type: "Directo",
    vessel: "Maersk Cartagena",
    origin: "Shanghai",
    destination: "Cartagena",
    eta: "2026-06-14",
    dta: "2026-06-16",
    containers: 1,
    status: "IN_TRANSIT"
  },
  {
    id: "SHP-24052",
    client: "Pacific Trading Ltda.",
    mbl: "HLCU7719200",
    hbl: "3 HBL",
    type: "Consolidado",
    vessel: "Hapag Bremen",
    origin: "Ningbo",
    destination: "Buenaventura",
    eta: "2026-06-22",
    dta: "2026-06-24",
    containers: 4,
    status: "DOCUMENT_REVIEW"
  },
  {
    id: "SHP-24053",
    client: "Grupo Norte Importador",
    mbl: "MSCU6612049",
    hbl: "HBL-CO-99118",
    type: "Directo",
    vessel: "MSC Valeria",
    origin: "Valencia",
    destination: "Cartagena",
    eta: "2026-05-30",
    dta: "2026-06-01",
    containers: 2,
    status: "ARRIVED"
  }
];

export const documents: DocumentItem[] = [
  {
    id: "DOC-9182",
    name: "MBL_MAEU9283712.pdf",
    type: "MBL",
    shipment: "SHP-24051",
    status: "OCR procesado",
    updatedAt: "2026-05-28 09:30"
  },
  {
    id: "DOC-9183",
    name: "Draft_HLCU7719200.pdf",
    type: "Draft",
    shipment: "SHP-24052",
    status: "OCR pendiente",
    updatedAt: "2026-05-28 08:15"
  },
  {
    id: "DOC-9184",
    name: "Factura_SHP-24053.pdf",
    type: "Factura",
    shipment: "SHP-24053",
    status: "Generado",
    updatedAt: "2026-05-27 17:45"
  }
];
