export type ShipmentStatus = "CREATED" | "DOCUMENT_REVIEW" | "IN_TRANSIT" | "ARRIVED" | "RELEASED";

export type Shipment = {
  id: string;
  client: string;
  mbl: string;
  hbl: string;
  type: "Directo" | "Consolidado";
  vessel: string;
  origin: string;
  destination: string;
  eta: string;
  dta: string;
  containers: number;
  status: ShipmentStatus;
};

export type DocumentItem = {
  id: string;
  name: string;
  type: string;
  shipment: string;
  status: "OCR pendiente" | "OCR procesado" | "Validado" | "Generado";
  updatedAt: string;
  downloadUrl?: string;
};
