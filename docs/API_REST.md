# API REST

Base path: `/api/v1`

## Autenticacion

- `POST /auth/login`
- `GET /auth/me`

## Clientes y empresas

- `GET /clients`
- `POST /clients`
- `GET /clients/{client_id}`
- `PUT /clients/{client_id}`
- `DELETE /clients/{client_id}`
- `GET /companies`
- `POST /companies`
- `GET /companies/{company_id}/contacts`
- `POST /companies/{company_id}/contacts`

## Cotizaciones

- `GET /quotations`
- `POST /quotations`
- `GET /quotations/{quotation_id}`
- `POST /quotations/{quotation_id}/approve`
- `POST /quotations/{quotation_id}/reject`
- `GET /quotations/{quotation_id}/tracking`
- `POST /quotations/{quotation_id}/pdf`

## Embarques

- `GET /shipments`
- `POST /shipments`
- `GET /shipments/{shipment_id}`
- `PUT /shipments/{shipment_id}`
- `POST /shipments/{shipment_id}/containers`
- `POST /shipments/{shipment_id}/hbls`
- `POST /shipments/{shipment_id}/tracking-events`
- `PATCH /shipments/{shipment_id}/eta`
- `PATCH /shipments/{shipment_id}/dta`

## Documentos y OCR

- `GET /documents`
- `POST /documents/upload`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/download`
- `POST /documents/{document_id}/ocr`
- `GET /documents/{document_id}/ocr`
- `POST /documents/{document_id}/ocr/validate`

## PDFs, reportes y exportacion

- `POST /exports/shipments/xlsx`
- `POST /exports/documents/pdf-to-xlsx`
- `POST /pdf/invoices`
- `POST /pdf/quotations`
- `POST /pdf/logistics-guides`
- `POST /pdf/reports`
- `POST /pdf/drafts`
- `POST /pdf/receipts`
- `POST /pdf/shipment-summaries`

## Notificaciones

- `GET /notifications`
- `POST /notifications/send`
- `GET /notifications/history`
