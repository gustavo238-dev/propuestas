"use client";

import {
  Bell,
  Building2,
  CheckCircle2,
  Download,
  FileCheck2,
  FileText,
  LayoutDashboard,
  PackageCheck,
  Plus,
  RefreshCw,
  ReceiptText,
  ScanLine,
  Send,
  Ship,
  Upload,
  Users,
  X,
  type LucideIcon
} from "lucide-react";
import type { FormEvent, ReactNode, RefObject } from "react";
import { useEffect, useMemo, useRef, useState } from "react";

import { DocumentItem, Shipment } from "@/types/logistics";

type Section =
  | "Dashboard"
  | "Clientes"
  | "Empresas"
  | "Cotizaciones"
  | "Embarques"
  | "Documentos"
  | "Tracking"
  | "Notificaciones";

type Quotation = {
  id: string;
  clientId: string;
  client: string;
  origin: string;
  destination: string;
  cargo: string;
  incoterm: string;
  status: "Solicitada" | "Aprobada" | "Rechazada";
};

type ApiClient = {
  id: string;
  name: string;
  tax_id: string;
  email: string;
  phone?: string | null;
  status: string;
};

type ApiUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

type ApiCompany = {
  id: string;
  legal_name: string;
  tax_id: string;
  address?: string | null;
  phone?: string | null;
  created_at: string;
};

type ApiQuotation = {
  id: string;
  client_id: string;
  origin_port: string;
  destination_port: string;
  cargo_description: string;
  incoterm: string;
  status: "REQUESTED" | "IN_REVIEW" | "APPROVED" | "REJECTED";
};

type ApiShipment = {
  id: string;
  client_id: string;
  shipment_type: "DIRECT" | "CONSOLIDATED";
  mbl_number: string;
  vessel_name: string;
  origin_port: string;
  destination_port: string;
  eta?: string | null;
  dta?: string | null;
  cargo_status: Shipment["status"];
  goods_description: string;
  containers: { container_number: string }[];
  hbls: { hbl_number: string }[];
};

type ApiDocument = {
  id: string;
  shipment_id?: string | null;
  document_type: string;
  file_name: string;
  storage_path: string;
  status: "UPLOADED" | "OCR_PENDING" | "OCR_PROCESSED" | "VALIDATED" | "GENERATED";
  created_at: string;
};

type ApiOcrExtraction = {
  id: string;
  document_id: string;
  raw_text: string;
  extracted_data: Record<string, string | string[] | null>;
  confidence?: string | number | null;
  validation_status: string;
  created_at: string;
};

type ApiGeneratedPdf = {
  document: ApiDocument;
  download_url: string;
};

type ApiNotification = {
  id: string;
  subject: string;
  body: string;
  status: "PENDING" | "SENT" | "FAILED";
  created_at: string;
};

type NotificationItem = {
  id: string;
  subject: string;
  detail: string;
  status: "Pendiente" | "Enviado";
};

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Clientes", icon: Users },
  { label: "Empresas", icon: Building2 },
  { label: "Cotizaciones", icon: ReceiptText },
  { label: "Embarques", icon: Ship },
  { label: "Documentos", icon: FileText },
  { label: "Tracking", icon: PackageCheck },
  { label: "Notificaciones", icon: Bell }
] satisfies { label: Section; icon: LucideIcon }[];

const statusLabel: Record<Shipment["status"], string> = {
  CREATED: "Creado",
  DOCUMENT_REVIEW: "Revision documental",
  IN_TRANSIT: "En transito",
  ARRIVED: "Arribado",
  RELEASED: "Liberado"
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

function mapQuotation(item: ApiQuotation, clients: ApiClient[]): Quotation {
  const client = clients.find((current) => current.id === item.client_id);
  const statusMap: Record<ApiQuotation["status"], Quotation["status"]> = {
    REQUESTED: "Solicitada",
    IN_REVIEW: "Solicitada",
    APPROVED: "Aprobada",
    REJECTED: "Rechazada"
  };
  return {
    id: item.id,
    clientId: item.client_id,
    client: client?.name ?? item.client_id,
    origin: item.origin_port,
    destination: item.destination_port,
    cargo: item.cargo_description,
    incoterm: item.incoterm,
    status: statusMap[item.status]
  };
}

function mapShipment(item: ApiShipment, clients: ApiClient[]): Shipment {
  const client = clients.find((current) => current.id === item.client_id);
  return {
    id: item.id,
    client: client?.name ?? item.client_id,
    mbl: item.mbl_number,
    hbl: item.hbls.map((hbl) => hbl.hbl_number).join(", ") || "Sin HBL",
    type: item.shipment_type === "CONSOLIDATED" ? "Consolidado" : "Directo",
    vessel: item.vessel_name,
    origin: item.origin_port,
    destination: item.destination_port,
    eta: item.eta ?? "Sin ETA",
    dta: item.dta ?? "Sin DTA",
    containers: item.containers.length,
    status: item.cargo_status
  };
}

function mapDocument(item: ApiDocument): DocumentItem {
  const statusMap: Record<ApiDocument["status"], DocumentItem["status"]> = {
    UPLOADED: "OCR pendiente",
    OCR_PENDING: "OCR pendiente",
    OCR_PROCESSED: "OCR procesado",
    VALIDATED: "Validado",
    GENERATED: "Generado"
  };
  return {
    id: item.id,
    name: item.file_name,
    type: item.document_type,
    shipment: item.shipment_id ?? "Sin embarque",
    status: statusMap[item.status],
    updatedAt: new Date(item.created_at).toLocaleString("es-CO"),
    downloadUrl: `${apiBaseUrl}/documents/${item.id}/download`
  };
}

function mapNotification(item: ApiNotification): NotificationItem {
  const statusMap: Record<ApiNotification["status"], NotificationItem["status"]> = {
    PENDING: "Pendiente",
    SENT: "Enviado",
    FAILED: "Pendiente"
  };
  return {
    id: item.id,
    subject: item.subject,
    detail: item.body,
    status: statusMap[item.status]
  };
}

export function ImportsWorkspace() {
  const [section, setSection] = useState<Section>("Dashboard");
  const [clients, setClients] = useState<ApiClient[]>([]);
  const [companies, setCompanies] = useState<ApiCompany[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [ocrExtraction, setOcrExtraction] = useState<ApiOcrExtraction | null>(null);
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [currentUser, setCurrentUser] = useState<ApiUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [modal, setModal] = useState<"quotation" | "shipment" | "client" | "company" | "login" | null>(null);
  const [toast, setToast] = useState("Conectando con API");
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const storedToken = window.localStorage.getItem("imports_access_token");
    if (storedToken) {
      setAccessToken(storedToken);
      void loadCurrentUser(storedToken);
    }
    void loadOperationalData();
  }, []);

  async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...(options?.headers ?? {})
      }
    });
    if (!response.ok) {
      let message = `Error HTTP ${response.status}`;
      try {
        const payload = (await response.json()) as { detail?: unknown };
        if (typeof payload.detail === "string") {
          message = payload.detail;
        } else if (Array.isArray(payload.detail)) {
          message = payload.detail
            .map((item) => {
              if (typeof item === "object" && item !== null && "msg" in item) {
                return String((item as { msg: unknown }).msg);
              }
              return String(item);
            })
            .join(", ");
        }
      } catch {
        message = await response.text();
      }
      throw new Error(message || `Error HTTP ${response.status}`);
    }
    return response.json() as Promise<T>;
  }

  async function loadCurrentUser(token: string) {
    try {
      const response = await fetch(`${apiBaseUrl}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) throw new Error("Sesion invalida");
      setCurrentUser((await response.json()) as ApiUser);
    } catch {
      window.localStorage.removeItem("imports_access_token");
      setAccessToken(null);
      setCurrentUser(null);
    }
  }

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    const data = new FormData(event.currentTarget);
    try {
      const body = new URLSearchParams();
      body.set("username", String(data.get("email")));
      body.set("password", String(data.get("password")));
      const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body
      });
      if (!response.ok) throw new Error("Credenciales invalidas");
      const tokenResponse = (await response.json()) as { access_token: string };
      window.localStorage.setItem("imports_access_token", tokenResponse.access_token);
      setAccessToken(tokenResponse.access_token);
      await loadCurrentUser(tokenResponse.access_token);
      setModal(null);
      setToast("Sesion iniciada");
    } catch {
      setToast("No se pudo iniciar sesion");
    } finally {
      setIsSaving(false);
    }
  }

  async function loadOperationalData() {
    try {
      const [apiClients, apiCompanies, apiQuotations, apiShipments, apiDocuments, apiNotifications] = await Promise.all([
        apiRequest<ApiClient[]>("/clients"),
        apiRequest<ApiCompany[]>("/companies"),
        apiRequest<ApiQuotation[]>("/quotations"),
        apiRequest<ApiShipment[]>("/shipments"),
        apiRequest<ApiDocument[]>("/documents"),
        apiRequest<ApiNotification[]>("/notifications")
      ]);
      setClients(apiClients);
      setCompanies(apiCompanies);
      setQuotations(apiQuotations.map((item) => mapQuotation(item, apiClients)));
      setShipments(apiShipments.map((item) => mapShipment(item, apiClients)));
      const mappedDocuments = apiDocuments.map(mapDocument);
      setDocuments(mappedDocuments);
      setSelectedDocumentId(mappedDocuments[0]?.id ?? null);
      setNotifications(apiNotifications.map(mapNotification));
      setToast("Datos cargados desde PostgreSQL");
    } catch (error) {
      setToast("API no disponible, usando datos locales");
    }
  }

  const metrics = useMemo(
    () => [
      { label: "Embarques activos", value: String(shipments.length), detail: "Tracking logistico", icon: Ship },
      {
        label: "Cotizaciones",
        value: String(quotations.length),
        detail: "Solicitudes comerciales",
        icon: ReceiptText
      },
      { label: "PDFs", value: String(documents.length), detail: "OCR y generados", icon: FileText },
      {
        label: "Alertas",
        value: String(notifications.length),
        detail: "Eventos notificados",
        icon: PackageCheck
      }
    ],
    [documents.length, notifications.length, quotations.length, shipments.length]
  );

  async function addNotification(
    subject: string,
    detail: string,
    status: NotificationItem["status"] = "Pendiente",
  ) {
    try {
      const created = await apiRequest<ApiNotification>("/notifications/send", {
        method: "POST",
        body: JSON.stringify({
          notification_type: "STATUS_ALERT",
          subject,
          body: detail,
          recipients: []
        })
      });
      setNotifications((current) => [mapNotification(created), ...current]);
    } catch {
      setNotifications((current) => [
        { id: `LOCAL-${String(current.length + 1).padStart(3, "0")}`, subject, detail, status },
        ...current
      ]);
    }
  }

  async function createClientFromForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    const data = new FormData(event.currentTarget);
    try {
      const created = await apiRequest<ApiClient>("/clients", {
        method: "POST",
        body: JSON.stringify({
          name: String(data.get("client")),
          tax_id: String(data.get("taxId")),
          email: String(data.get("clientEmail")),
          phone: String(data.get("phone") || ""),
          status: "ACTIVE"
        })
      });
      setClients((current) => [created, ...current]);
      await addNotification("Cliente creado", `${created.name} quedo registrado`);
      setModal(null);
      setSection("Clientes");
      setToast("Cliente guardado en PostgreSQL");
    } catch {
      setToast("No se pudo guardar el cliente");
    } finally {
      setIsSaving(false);
    }
  }

  async function createCompanyFromForm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    const data = new FormData(event.currentTarget);
    try {
      const created = await apiRequest<ApiCompany>("/companies", {
        method: "POST",
        body: JSON.stringify({
          legal_name: String(data.get("company")),
          tax_id: String(data.get("taxId")),
          address: String(data.get("address") || ""),
          phone: String(data.get("phone") || "")
        })
      });
      setCompanies((current) => [created, ...current.filter((company) => company.id !== created.id)]);
      await addNotification("Empresa creada", `${created.legal_name} quedo registrada`);
      setModal(null);
      setSection("Empresas");
      setToast("Empresa guardada en PostgreSQL");
    } catch (error) {
      setToast(error instanceof Error ? `Empresa: ${error.message}` : "No se pudo guardar la empresa");
    } finally {
      setIsSaving(false);
    }
  }

  async function ensureClient(data: FormData): Promise<ApiClient> {
    const email = String(data.get("clientEmail") || "operaciones@cliente-demo.com");
    const existing = clients.find((client) => client.email === email);
    if (existing) return existing;
    const [found] = await apiRequest<ApiClient[]>(`/clients?email=${encodeURIComponent(email)}`);
    if (found) {
      setClients((current) => [found, ...current.filter((client) => client.id !== found.id)]);
      return found;
    }
    try {
      const created = await apiRequest<ApiClient>("/clients", {
        method: "POST",
        body: JSON.stringify({
          name: String(data.get("client")),
          tax_id: String(data.get("taxId") || `NIT-${Date.now()}`),
          email,
          phone: String(data.get("phone") || ""),
          status: "ACTIVE"
        })
      });
      setClients((current) => [created, ...current]);
      return created;
    } catch (error) {
      const refreshed = await apiRequest<ApiClient[]>("/clients");
      setClients(refreshed);
      const fallback = refreshed.find((client) => client.email === email);
      if (fallback) return fallback;
      throw error;
    }
  }

  async function handleQuotationSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    const data = new FormData(event.currentTarget);
    try {
      const client = await ensureClient(data);
      const created = await apiRequest<ApiQuotation>("/quotations", {
        method: "POST",
        body: JSON.stringify({
          client_id: client.id,
          origin_port: String(data.get("origin")),
          destination_port: String(data.get("destination")),
          cargo_description: String(data.get("cargo")),
          incoterm: String(data.get("incoterm")),
          estimated_cost: null,
          currency: "USD"
        })
      });
      const quotation = mapQuotation(created, [client, ...clients]);
      setQuotations((current) => [quotation, ...current.filter((item) => item.id !== quotation.id)]);
      await addNotification("Nueva cotizacion", `${quotation.client} solicito ${quotation.origin} -> ${quotation.destination}`);
      void loadOperationalData();
      setModal(null);
      setSection("Cotizaciones");
      setToast("Cotizacion guardada en PostgreSQL");
    } catch (error) {
      setToast(error instanceof Error ? `Cotizacion: ${error.message}` : "No se pudo guardar la cotizacion");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleShipmentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    const data = new FormData(event.currentTarget);
    try {
      const client = await ensureClient(data);
      const containerCount = Number(data.get("containers") || 1);
      const created = await apiRequest<ApiShipment>("/shipments", {
        method: "POST",
        body: JSON.stringify({
          client_id: client.id,
          shipment_type: String(data.get("type")) === "Consolidado" ? "CONSOLIDATED" : "DIRECT",
          mbl_number: String(data.get("mbl")),
          vessel_name: String(data.get("vessel")),
          origin_port: String(data.get("origin")),
          destination_port: String(data.get("destination")),
          eta: String(data.get("eta")),
          dta: String(data.get("dta")),
          cargo_status: "CREATED",
          goods_description: String(data.get("goods") || "Carga de importacion maritima"),
          containers: Array.from({ length: containerCount }, (_, index) => ({
            container_number: `${String(data.get("containerPrefix") || "MSCU")}${1234567 + index}`,
            container_type: "40HC",
            seal_number: `SL-${8892 + index}`,
            weight_kg: "18000.00",
            status: "CREATED"
          })),
          hbls: [
            {
              hbl_number: String(data.get("hbl")),
              consignee: client.name,
              notify_party: "Agente Aduanero",
              goods_description: String(data.get("goods") || "Carga de importacion maritima")
            }
          ]
        })
      });
      const shipment = mapShipment(created, [client, ...clients]);
      setShipments((current) => [shipment, ...current.filter((item) => item.id !== shipment.id)]);
      await addNotification("Nuevo embarque", `${shipment.id} creado para ${shipment.client}`);
      setModal(null);
      setSection("Embarques");
      setToast("Embarque guardado en PostgreSQL");
    } catch (error) {
      setToast("No se pudo guardar el embarque");
    } finally {
      setIsSaving(false);
    }
  }

  async function uploadRequest(path: string, formData: FormData): Promise<ApiDocument> {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      method: "POST",
      body: formData
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json() as Promise<ApiDocument>;
  }

  async function handleUpload(fileList: FileList | null) {
    const file = fileList?.item(0);
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (shipments[0]?.id) formData.append("shipment_id", shipments[0].id);
      formData.append("document_type", "EXTERNAL_PDF");
      const uploaded = await uploadRequest("/documents/upload", formData);
      const document = mapDocument(uploaded);
      setDocuments((current) => [document, ...current]);
      setSelectedDocumentId(document.id);
      setOcrExtraction(null);
      setSection("Documentos");
      setToast("PDF cargado y almacenado");
    } catch {
      setToast("No se pudo cargar el PDF");
    }
  }

  async function runOcr() {
    if (!selectedDocumentId) {
      setToast("Selecciona un PDF para ejecutar OCR");
      return;
    }
    try {
      const extraction = await apiRequest<ApiOcrExtraction>(`/documents/${selectedDocumentId}/ocr`, {
        method: "POST"
      });
      setOcrExtraction(extraction);
      setDocuments((current) =>
        current.map((document) =>
          document.id === selectedDocumentId
            ? { ...document, status: "OCR procesado", updatedAt: new Date().toLocaleString("es-CO") }
            : document
        )
      );
      await addNotification("OCR procesado", "Extraccion automatica disponible para comparacion");
      setToast("OCR real ejecutado sobre el PDF");
    } catch {
      setToast("No se pudo ejecutar OCR sobre el PDF");
    }
  }

  async function generatePdf() {
    const shipment = shipments[0];
    if (!shipment) {
      setToast("Crea o carga un embarque antes de facturar");
      return;
    }
    try {
      const payload = {
        cliente: shipment.client,
        mbl: shipment.mbl,
        hbl: shipment.hbl,
        motonave: shipment.vessel,
        origen: shipment.origin,
        destino: shipment.destination,
        eta: shipment.eta,
        dta: shipment.dta,
        mercancia: ocrExtraction?.extracted_data.goods ?? "Carga de importacion maritima",
        estado: statusLabel[shipment.status],
        valor: "Pendiente de liquidacion"
      };
      const generated = await apiRequest<ApiGeneratedPdf>(`/pdf/invoices/store?shipment_id=${shipment.id}`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      const document = mapDocument(generated.document);
      setDocuments((current) => [document, ...current]);
      setSelectedDocumentId(document.id);
      await addNotification("Factura generada", `${document.name} disponible para comparar y descargar`);
      setToast("Factura PDF generada y almacenada");
    } catch {
      setToast("No se pudo generar la factura PDF");
    }
  }

  async function selectDocument(documentId: string) {
    setSelectedDocumentId(documentId);
    try {
      const extraction = await apiRequest<ApiOcrExtraction>(`/documents/${documentId}/ocr`);
      setOcrExtraction(extraction);
    } catch {
      setOcrExtraction(null);
    }
  }

  async function sendEmail() {
    try {
      const created = await apiRequest<ApiNotification>("/notifications/send", {
        method: "POST",
        body: JSON.stringify({
          notification_type: "PDF_AVAILABLE",
          subject: "PDF disponible",
          body: "Documento disponible para descarga y revision documental.",
          recipients: ["operaciones@cliente-demo.com"]
        })
      });
      setNotifications((current) => [mapNotification(created), ...current]);
      setSection("Notificaciones");
      setToast("Notificacion enviada por API");
    } catch {
      setToast("No se pudo enviar la notificacion");
    }
  }

  async function exportShipments() {
    try {
      const response = await fetch(`${apiBaseUrl}/exports/shipments/xlsx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          shipments.map((shipment) => ({
            mbl_number: shipment.mbl,
            client: shipment.client,
            origin_port: shipment.origin,
            destination_port: shipment.destination,
            eta: shipment.eta,
            dta: shipment.dta,
            cargo_status: shipment.status
          }))
        )
      });
      if (!response.ok) throw new Error("No se pudo exportar");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "embarques.xlsx";
      link.click();
      URL.revokeObjectURL(url);
      setToast("XLSX de embarques descargado");
    } catch {
      setToast("No se pudo exportar XLSX");
    }
  }

  async function exportOcr() {
    if (!ocrExtraction) {
      setToast("Ejecuta OCR antes de exportar");
      return;
    }
    try {
      const response = await fetch(`${apiBaseUrl}/exports/documents/pdf-to-xlsx`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(ocrExtraction.extracted_data)
      });
      if (!response.ok) throw new Error("No se pudo exportar");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "extraccion_ocr.xlsx";
      link.click();
      URL.revokeObjectURL(url);
      setToast("XLSX de OCR descargado");
    } catch {
      setToast("No se pudo exportar OCR");
    }
  }

  return (
    <main className="min-h-screen bg-surface">
      <div className="flex">
        <aside className="hidden min-h-screen w-72 border-r border-line bg-white px-4 py-5 lg:block">
          <div className="mb-8 px-2">
            <p className="text-sm font-semibold uppercase tracking-wider text-harbor">Logistica maritima</p>
            <h1 className="mt-2 text-xl font-bold text-ink">Importaciones</h1>
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <button
                key={item.label}
                className={`flex h-11 w-full items-center gap-3 rounded px-3 text-left text-sm font-medium ${
                  section === item.label ? "bg-harbor text-white" : "text-slate-600 hover:bg-slate-100"
                }`}
                onClick={() => setSection(item.label)}
                type="button"
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
          </nav>
        </aside>

        <div className="min-w-0 flex-1">
          <header className="border-b border-line bg-white px-5 py-4 lg:px-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wider text-harbor">Operacion activa</p>
                <h1 className="mt-1 text-2xl font-bold text-ink">{section}</h1>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                  {toast}
                </span>
                <button
                  className="flex h-10 w-10 items-center justify-center rounded border border-line bg-white"
                  onClick={() => void loadOperationalData()}
                  title="Refrescar datos"
                  type="button"
                >
                  <RefreshCw className="h-4 w-4 text-ink" />
                </button>
                <button
                  className="flex h-10 w-10 items-center justify-center rounded border border-line bg-white"
                  onClick={() => setSection("Notificaciones")}
                  title="Notificaciones"
                  type="button"
                >
                  <Bell className="h-4 w-4 text-ink" />
                </button>
                <button
                  className="rounded border border-line px-4 py-2 text-sm font-semibold text-ink"
                  onClick={() => setModal("shipment")}
                  type="button"
                >
                  Nuevo embarque
                </button>
                <button
                  className="rounded border border-line px-4 py-2 text-sm font-semibold text-ink"
                  onClick={() => setModal("login")}
                  type="button"
                >
                  {currentUser ? currentUser.full_name : "Login"}
                </button>
                <button
                  className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white"
                  onClick={() => setModal("quotation")}
                  type="button"
                >
                  Solicitar cotizacion
                </button>
              </div>
            </div>
          </header>

          <div className="grid gap-5 px-5 py-6 lg:px-8">
            {section === "Dashboard" && (
              <>
                <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {metrics.map((metric) => (
                    <section key={metric.label} className="rounded border border-line bg-white p-4 shadow-panel">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-slate-500">{metric.label}</p>
                        <metric.icon className="h-5 w-5 text-harbor" />
                      </div>
                      <p className="mt-3 text-2xl font-bold text-ink">{metric.value}</p>
                      <p className="mt-1 text-sm text-slate-500">{metric.detail}</p>
                    </section>
                  ))}
                </section>
                <section className="grid gap-5 xl:grid-cols-[1fr_380px]">
                  <ShipmentsView shipments={shipments} onExport={exportShipments} onNew={() => setModal("shipment")} />
                  <DocumentPanel
                    documents={documents}
                    fileInputRef={fileInputRef}
                    onGeneratePdf={generatePdf}
                    onRunOcr={runOcr}
                    onSendEmail={sendEmail}
                    onUpload={handleUpload}
                    onExportOcr={exportOcr}
                    ocrExtraction={ocrExtraction}
                    onSelectDocument={selectDocument}
                    selectedDocumentId={selectedDocumentId}
                  />
                </section>
              </>
            )}

            {section === "Cotizaciones" && (
              <QuotationsView
                quotations={quotations}
                onNew={() => setModal("quotation")}
                onApprove={async (id) => {
                  try {
                    const updated = await apiRequest<ApiQuotation>(`/quotations/${id}/approve`, {
                      method: "POST"
                    });
                    setQuotations((current) =>
                      current.map((quotation) =>
                        quotation.id === id ? mapQuotation(updated, clients) : quotation
                      )
                    );
                    setToast("Cotizacion aprobada en PostgreSQL");
                    void loadOperationalData();
                  } catch {
                    setToast("No se pudo aprobar la cotizacion");
                  }
                }}
                onReject={async (id) => {
                  try {
                    const updated = await apiRequest<ApiQuotation>(`/quotations/${id}/reject`, {
                      method: "POST"
                    });
                    setQuotations((current) =>
                      current.map((quotation) =>
                        quotation.id === id ? mapQuotation(updated, clients) : quotation
                      )
                    );
                    setToast("Cotizacion rechazada en PostgreSQL");
                  } catch {
                    setToast("No se pudo rechazar la cotizacion");
                  }
                }}
              />
            )}

            {section === "Embarques" && <ShipmentsView shipments={shipments} onExport={exportShipments} onNew={() => setModal("shipment")} />}

            {section === "Documentos" && (
              <DocumentPanel
                documents={documents}
                fileInputRef={fileInputRef}
                onGeneratePdf={generatePdf}
                onRunOcr={runOcr}
                onSendEmail={sendEmail}
                onUpload={handleUpload}
                onExportOcr={exportOcr}
                ocrExtraction={ocrExtraction}
                onSelectDocument={selectDocument}
                selectedDocumentId={selectedDocumentId}
              />
            )}

            {section === "Tracking" && <TrackingView shipments={shipments} />}
            {section === "Notificaciones" && <NotificationsView notifications={notifications} />}
            {section === "Clientes" && (
              <ClientsView clients={clients} onNew={() => setModal("client")} />
            )}
            {section === "Empresas" && (
              <CompaniesView companies={companies} onNew={() => setModal("company")} />
            )}
          </div>
        </div>
      </div>

      {modal === "quotation" && (
        <Modal title="Solicitud de cotizacion" onClose={() => setModal(null)}>
          <form className="grid gap-3" onSubmit={handleQuotationSubmit}>
            <TextInput label="Cliente" name="client" placeholder="Andes Import S.A.S." />
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="Puerto origen" name="origin" placeholder="Shanghai" />
              <TextInput label="Puerto destino" name="destination" placeholder="Cartagena" />
            </div>
            <TextInput label="Mercancia" name="cargo" placeholder="Repuestos industriales" />
            <TextInput label="Incoterm" name="incoterm" placeholder="FOB" />
            <div className="grid gap-3 md:grid-cols-3">
              <TextInput label="NIT" name="taxId" placeholder="900123456-7" />
              <TextInput label="Correo cliente" name="clientEmail" placeholder="operaciones@cliente.com" type="email" />
              <TextInput label="Telefono" name="phone" placeholder="+57 601 555 0101" />
            </div>
            <button className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white" disabled={isSaving} type="submit">
              {isSaving ? "Guardando..." : "Registrar cotizacion"}
            </button>
          </form>
        </Modal>
      )}

      {modal === "login" && (
        <Modal title="Login JWT" onClose={() => setModal(null)}>
          <form className="grid gap-3" onSubmit={handleLoginSubmit}>
            <TextInput label="Correo" name="email" placeholder="admin@empresa-logistica.com" type="email" />
            <TextInput label="Contrasena" name="password" placeholder="Admin123*" type="password" />
            <button className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white" disabled={isSaving} type="submit">
              {isSaving ? "Validando..." : "Iniciar sesion"}
            </button>
          </form>
        </Modal>
      )}

      {modal === "client" && (
        <Modal title="Nuevo cliente" onClose={() => setModal(null)}>
          <form className="grid gap-3" onSubmit={createClientFromForm}>
            <TextInput label="Cliente" name="client" placeholder="Andes Import S.A.S." />
            <div className="grid gap-3 md:grid-cols-3">
              <TextInput label="NIT" name="taxId" placeholder="900123456-7" />
              <TextInput label="Correo cliente" name="clientEmail" placeholder="operaciones@cliente.com" type="email" />
              <TextInput label="Telefono" name="phone" placeholder="+57 601 555 0101" />
            </div>
            <button className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white" disabled={isSaving} type="submit">
              {isSaving ? "Guardando..." : "Guardar cliente"}
            </button>
          </form>
        </Modal>
      )}

      {modal === "company" && (
        <Modal title="Nueva empresa" onClose={() => setModal(null)}>
          <form className="grid gap-3" onSubmit={createCompanyFromForm}>
            <TextInput label="Razon social" name="company" placeholder="Empresa Logistica Maritima S.A.S." />
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="NIT" name="taxId" placeholder="901555777-1" />
              <TextInput label="Telefono" name="phone" placeholder="+57 601 555 0101" />
            </div>
            <TextInput label="Direccion" name="address" placeholder="Zona franca / oficina principal" />
            <button className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white" disabled={isSaving} type="submit">
              {isSaving ? "Guardando..." : "Guardar empresa"}
            </button>
          </form>
        </Modal>
      )}

      {modal === "shipment" && (
        <Modal title="Nuevo embarque maritimo" onClose={() => setModal(null)}>
          <form className="grid gap-3" onSubmit={handleShipmentSubmit}>
            <TextInput label="Cliente" name="client" placeholder="Pacific Trading Ltda." />
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="MBL" name="mbl" placeholder="HLCU7719200" />
              <TextInput label="HBL" name="hbl" placeholder="HBL-CO-99118" />
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="Motonave" name="vessel" placeholder="Hapag Bremen" />
              <label className="grid gap-1 text-sm font-medium text-slate-700">
                Tipo
                <select className="rounded border border-line px-3 py-2" name="type" required>
                  <option>Directo</option>
                  <option>Consolidado</option>
                </select>
              </label>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <TextInput label="Origen" name="origin" placeholder="Ningbo" />
              <TextInput label="Destino" name="destination" placeholder="Buenaventura" />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <TextInput label="ETA" name="eta" type="date" />
              <TextInput label="DTA" name="dta" type="date" />
              <TextInput label="Contenedores" name="containers" placeholder="1" type="number" />
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <TextInput label="NIT" name="taxId" placeholder="900123456-7" />
              <TextInput label="Correo cliente" name="clientEmail" placeholder="operaciones@cliente.com" type="email" />
              <TextInput label="Prefijo contenedor" name="containerPrefix" placeholder="MSCU" />
            </div>
            <TextInput label="Mercancia" name="goods" placeholder="Repuestos industriales" />
            <button className="rounded bg-harbor px-4 py-2 text-sm font-semibold text-white" disabled={isSaving} type="submit">
              {isSaving ? "Guardando..." : "Crear embarque"}
            </button>
          </form>
        </Modal>
      )}
    </main>
  );
}

function ShipmentsView({
  shipments,
  onExport,
  onNew
}: {
  shipments: Shipment[];
  onExport: () => void | Promise<void>;
  onNew: () => void;
}) {
  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Embarques activos</h2>
          <p className="text-sm text-slate-500">Seguimiento operativo de MBL, HBL, ETA y DTA</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm font-semibold text-ink" onClick={onExport} type="button">
            <Download className="h-4 w-4" />
            XLSX
          </button>
          <button className="flex items-center gap-2 rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" onClick={onNew} type="button">
            <Plus className="h-4 w-4" />
            Nuevo
          </button>
        </div>
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
                  <p className="text-slate-800">{shipment.origin} -&gt; {shipment.destination}</p>
                  <p className="text-xs text-slate-500">{shipment.vessel}</p>
                </td>
                <td className="px-5 py-4 text-slate-700">
                  <p>ETA {shipment.eta}</p>
                  <p className="text-xs text-slate-500">DTA {shipment.dta}</p>
                </td>
                <td className="px-5 py-4">
                  <span className="rounded bg-sky-100 px-2.5 py-1 text-xs font-semibold text-sky-800">
                    {statusLabel[shipment.status]}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DocumentPanel({
  documents,
  fileInputRef,
  onGeneratePdf,
  onRunOcr,
  onSendEmail,
  onUpload,
  onExportOcr,
  selectedDocumentId,
  onSelectDocument,
  ocrExtraction
}: {
  documents: DocumentItem[];
  fileInputRef: RefObject<HTMLInputElement | null>;
  onGeneratePdf: () => void | Promise<void>;
  onRunOcr: () => void | Promise<void>;
  onSendEmail: () => void;
  onUpload: (fileList: FileList | null) => void;
  onExportOcr: () => void | Promise<void>;
  selectedDocumentId: string | null;
  onSelectDocument: (documentId: string) => void | Promise<void>;
  ocrExtraction: ApiOcrExtraction | null;
}) {
  const selectedDocument = documents.find((document) => document.id === selectedDocumentId) ?? documents[0];
  const extractedRows = ocrExtraction ? Object.entries(ocrExtraction.extracted_data) : [];

  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <input
        ref={fileInputRef}
        className="hidden"
        accept="application/pdf"
        onChange={(event) => onUpload(event.target.files)}
        type="file"
      />
      <div className="flex flex-col gap-3 border-b border-line px-5 py-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-base font-semibold text-ink">Centro documental</h2>
          <p className="text-sm text-slate-500">Visualizacion PDF, OCR, comparacion y facturacion</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm font-semibold text-ink" onClick={() => fileInputRef.current?.click()} type="button">
            <Upload className="h-4 w-4" />
            Cargar PDF
          </button>
          <button className="flex items-center gap-2 rounded bg-signal px-3 py-2 text-sm font-semibold text-white" onClick={onRunOcr} type="button">
            <ScanLine className="h-4 w-4" />
            OCR
          </button>
          <button className="flex items-center gap-2 rounded bg-cargo px-3 py-2 text-sm font-semibold text-white" onClick={onGeneratePdf} type="button">
            <FileCheck2 className="h-4 w-4" />
            Crear factura
          </button>
          <button className="flex items-center gap-2 rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" onClick={onSendEmail} type="button">
            <Send className="h-4 w-4" />
            Enviar
          </button>
          <button className="flex items-center gap-2 rounded border border-line px-3 py-2 text-sm font-semibold text-ink" onClick={onExportOcr} type="button">
            <Download className="h-4 w-4" />
            OCR XLSX
          </button>
        </div>
      </div>

      <div className="grid gap-0 xl:grid-cols-[320px_1fr_360px]">
        <div className="border-b border-line p-4 xl:border-b-0 xl:border-r">
          <h3 className="mb-3 text-sm font-semibold uppercase text-slate-500">Historial documental</h3>
          <div className="max-h-[680px] space-y-3 overflow-auto pr-1">
            {documents.length === 0 && (
              <div className="rounded border border-dashed border-line p-4 text-sm text-slate-500">
                No hay PDFs cargados.
              </div>
            )}
            {documents.map((document) => (
              <button
                key={document.id}
                className={`w-full rounded border p-3 text-left ${
                  selectedDocument?.id === document.id ? "border-harbor bg-sky-50" : "border-line bg-white hover:bg-slate-50"
                }`}
                onClick={() => onSelectDocument(document.id)}
                type="button"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate font-semibold text-ink">{document.name}</p>
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
              </button>
            ))}
          </div>
        </div>

        <div className="min-h-[680px] border-b border-line bg-slate-100 p-4 xl:border-b-0 xl:border-r">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold uppercase text-slate-500">Visor PDF</h3>
              <p className="text-sm font-medium text-ink">{selectedDocument?.name ?? "Sin documento seleccionado"}</p>
            </div>
            {selectedDocument?.downloadUrl && (
              <a
                className="rounded border border-line bg-white px-3 py-2 text-sm font-semibold text-ink"
                href={selectedDocument.downloadUrl}
                rel="noreferrer"
                target="_blank"
              >
                Descargar
              </a>
            )}
          </div>
          {selectedDocument?.downloadUrl ? (
            <iframe
              className="h-[620px] w-full rounded border border-line bg-white"
              src={selectedDocument.downloadUrl}
              title={`PDF ${selectedDocument.name}`}
            />
          ) : (
            <div className="grid h-[620px] place-items-center rounded border border-dashed border-line bg-white text-sm text-slate-500">
              Carga un PDF para visualizarlo aqui.
            </div>
          )}
        </div>

        <div className="p-4">
          <h3 className="text-sm font-semibold uppercase text-slate-500">Comparacion OCR</h3>
          <div className="mt-3 rounded border border-line">
            <div className="grid grid-cols-2 border-b border-line bg-slate-50 px-3 py-2 text-xs font-semibold uppercase text-slate-500">
              <span>Campo</span>
              <span>Valor extraido</span>
            </div>
            {extractedRows.length === 0 ? (
              <div className="p-4 text-sm text-slate-500">
                Ejecuta OCR para comparar MBL, HBL, ETA, DTA, contenedores, naviera, puertos, cliente y mercancia.
              </div>
            ) : (
              extractedRows.map(([field, value]) => (
                <div key={field} className="grid grid-cols-2 gap-3 border-b border-line px-3 py-2 text-sm last:border-0">
                  <span className="font-semibold text-ink">{field.toUpperCase()}</span>
                  <span className="break-words text-slate-700">{Array.isArray(value) ? value.join(", ") : value ?? "No detectado"}</span>
                </div>
              ))
            )}
          </div>

          <div className="mt-4 rounded border border-line p-3">
            <h4 className="font-semibold text-ink">Datos para factura</h4>
            <p className="mt-2 text-sm text-slate-500">
              La factura se genera desde el embarque activo y los datos OCR disponibles. El PDF generado queda almacenado y aparece en el historial documental.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function QuotationsView({
  quotations,
  onNew,
  onApprove,
  onReject
}: {
  quotations: Quotation[];
  onNew: () => void;
  onApprove: (id: string) => void | Promise<void>;
  onReject: (id: string) => void | Promise<void>;
}) {
  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Cotizaciones</h2>
          <p className="text-sm text-slate-500">Aprobacion, rechazo y seguimiento comercial</p>
        </div>
        <button className="flex items-center gap-2 rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" onClick={onNew} type="button">
          <Plus className="h-4 w-4" />
          Nueva
        </button>
      </div>
      <div className="grid gap-3 p-5">
        {quotations.length === 0 && (
          <div className="rounded border border-dashed border-line p-4 text-sm text-slate-500">
            No hay cotizaciones registradas.
          </div>
        )}
        {quotations.map((quotation) => (
          <div key={quotation.id} className="grid gap-3 rounded border border-line p-4 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <p className="font-semibold text-ink">{quotation.id} · {quotation.client}</p>
              <p className="text-sm text-slate-500">{quotation.origin} -&gt; {quotation.destination} · {quotation.incoterm}</p>
              <p className="text-sm text-slate-700">{quotation.cargo}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">{quotation.status}</span>
              <button className="rounded bg-signal px-3 py-2 text-sm font-semibold text-white" onClick={() => onApprove(quotation.id)} type="button">
                Aprobar
              </button>
              <button className="rounded bg-slate-700 px-3 py-2 text-sm font-semibold text-white" onClick={() => onReject(quotation.id)} type="button">
                Rechazar
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function TrackingView({ shipments }: { shipments: Shipment[] }) {
  return (
    <section className="rounded border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Tracking logistico</h2>
      <div className="mt-4 grid gap-4">
        {shipments.map((shipment) => (
          <div key={shipment.id} className="rounded border border-line p-4">
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-semibold text-ink">{shipment.id} · {shipment.vessel}</p>
                <p className="text-sm text-slate-500">{shipment.origin} -&gt; {shipment.destination}</p>
              </div>
              <span className="rounded bg-sky-100 px-2.5 py-1 text-xs font-semibold text-sky-800">
                {statusLabel[shipment.status]}
              </span>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-4">
              <TrackStep label="MBL registrado" done />
              <TrackStep label="OCR validado" done={shipment.status !== "CREATED"} />
              <TrackStep label="ETA confirmada" done={shipment.status === "IN_TRANSIT" || shipment.status === "ARRIVED" || shipment.status === "RELEASED"} />
              <TrackStep label="Carga liberada" done={shipment.status === "RELEASED"} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function TrackStep({ label, done }: { label: string; done: boolean }) {
  return (
    <div className={`rounded border px-3 py-2 text-sm ${done ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-line bg-slate-50 text-slate-500"}`}>
      <div className="flex items-center gap-2">
        <CheckCircle2 className="h-4 w-4" />
        {label}
      </div>
    </div>
  );
}

function NotificationsView({ notifications }: { notifications: NotificationItem[] }) {
  return (
    <section className="rounded border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Centro de notificaciones</h2>
      <div className="mt-4 grid gap-3">
        {notifications.map((notification) => (
          <div key={notification.id} className="rounded border border-line p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-ink">{notification.subject}</p>
                <p className="text-sm text-slate-500">{notification.detail}</p>
              </div>
              <span className="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
                {notification.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ClientsView({ clients, onNew }: { clients: ApiClient[]; onNew: () => void }) {
  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Clientes</h2>
          <p className="text-sm text-slate-500">Registros conectados a PostgreSQL</p>
        </div>
        <button className="flex items-center gap-2 rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" onClick={onNew} type="button">
          <Plus className="h-4 w-4" />
          Nuevo
        </button>
      </div>
      <div className="grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-3">
        {clients.length === 0 && (
          <div className="rounded border border-dashed border-line p-4 text-sm text-slate-500">
            No hay clientes registrados.
          </div>
        )}
        {clients.map((client) => (
          <div key={client.id} className="rounded border border-line p-4">
            <p className="font-semibold text-ink">{client.name}</p>
            <p className="text-sm text-slate-500">{client.tax_id}</p>
            <p className="mt-2 text-sm text-slate-700">{client.email}</p>
            <p className="text-sm text-slate-500">{client.phone || "Sin telefono"}</p>
            <span className="mt-3 inline-flex rounded bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">
              {client.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function CompaniesView({ companies, onNew }: { companies: ApiCompany[]; onNew: () => void }) {
  return (
    <section className="rounded border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Empresas</h2>
          <p className="text-sm text-slate-500">Empresas y datos fiscales</p>
        </div>
        <button className="flex items-center gap-2 rounded bg-harbor px-3 py-2 text-sm font-semibold text-white" onClick={onNew} type="button">
          <Plus className="h-4 w-4" />
          Nueva
        </button>
      </div>
      <div className="grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-3">
        {companies.length === 0 && (
          <div className="rounded border border-dashed border-line p-4 text-sm text-slate-500">
            No hay empresas registradas.
          </div>
        )}
        {companies.map((company) => (
          <div key={company.id} className="rounded border border-line p-4">
            <p className="font-semibold text-ink">{company.legal_name}</p>
            <p className="text-sm text-slate-500">{company.tax_id}</p>
            <p className="mt-2 text-sm text-slate-700">{company.address || "Sin direccion"}</p>
            <p className="text-sm text-slate-500">{company.phone || "Sin telefono"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/35 p-4">
      <section className="w-full max-w-2xl rounded border border-line bg-white p-5 shadow-panel">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-ink">{title}</h2>
          <button className="flex h-9 w-9 items-center justify-center rounded border border-line" onClick={onClose} title="Cerrar" type="button">
            <X className="h-4 w-4" />
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}

function TextInput({
  label,
  name,
  placeholder,
  type = "text"
}: {
  label: string;
  name: string;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="grid gap-1 text-sm font-medium text-slate-700">
      {label}
      <input className="rounded border border-line px-3 py-2" name={name} placeholder={placeholder} required type={type} />
    </label>
  );
}
