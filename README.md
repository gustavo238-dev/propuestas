# Sistema de Gestion de Importaciones Maritimas

Plataforma web empresarial para automatizar procesos logisticos y documentales de importaciones maritimas.

## Alcance funcional

- Autenticacion JWT con roles: Cliente, Agente Comercial, Sales Support y Administrador.
- Gestion de clientes, empresas y contactos.
- Solicitudes, aprobacion, rechazo y seguimiento de cotizaciones.
- Administracion de embarques directos y consolidados.
- Tracking logistico con ETA, DTA, motonave, contenedores y estado de carga.
- Gestion documental con carga, visualizacion, historial y almacenamiento.
- OCR de PDFs con Tesseract, pdfplumber y OpenCV.
- Extraccion automatica de MBL, HBL, ETA, DTA, contenedores, naviera, puertos, cliente y mercancia.
- Generacion de PDFs empresariales.
- Exportacion XLSX.
- Notificaciones por correo con historial.

## Tecnologias

Backend: Python 3.12, FastAPI, SQLAlchemy, Pydantic, PostgreSQL, JWT.

Frontend: React, Next.js, TypeScript, TailwindCSS.

Documentos/OCR: Tesseract OCR, pdfplumber, OpenCV, ReportLab.

Infraestructura: Docker y Docker Compose.

## Estructura

```text
backend/src/
  domain/
  application/
  infrastructure/
  presentation/
  shared/
frontend/src/
docs/
docker-compose.yml
```

## Ejecucion local

```bash
docker compose up --build
```

Backend: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

Frontend: `http://localhost:3000`

## Flujo documental operativo

1. Abrir `http://localhost:3000`.
2. Entrar a `Documentos`.
3. Cargar un PDF con `Cargar PDF`.
4. Seleccionar el documento en el historial.
5. Revisar el PDF en el visor embebido.
6. Ejecutar `OCR`.
7. Comparar los campos extraidos contra el PDF visible.
8. Usar `Crear factura` para generar una factura PDF almacenada.
9. Seleccionar la factura generada en el historial y descargarla o visualizarla.

Endpoints involucrados:

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents/{document_id}/download`
- `POST /api/v1/documents/{document_id}/ocr`
- `GET /api/v1/documents/{document_id}/ocr`
- `POST /api/v1/pdf/invoices/store`

## Pruebas unitarias

```bash
docker compose --profile test run --rm backend-test
```

Las pruebas usan SQLite en memoria y no requieren PostgreSQL.

## Documentacion

- [Arquitectura](docs/ARCHITECTURE.md)
- [Modelo de datos](docs/DATABASE_MODEL.md)
- [API REST](docs/API_REST.md)
- [Casos de uso e historias](docs/REQUIREMENTS.md)
- [UML y flujos](docs/UML.md)
- [Roadmap tecnico](docs/ROADMAP.md)
