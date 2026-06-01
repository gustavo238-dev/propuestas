# Roadmap Tecnico

## Fase 1 - Base empresarial

- Monorepo con backend, frontend e infraestructura.
- Clean Architecture backend.
- Modelo relacional base.
- API REST inicial.
- Dashboard operativo frontend.

## Fase 2 - Flujo comercial

- Login JWT real con hash de contrasenas.
- CRUD clientes, empresas y contactos.
- Cotizaciones con aprobacion, rechazo y notificaciones.

## Fase 3 - Operacion maritima

- Embarques directos y consolidados.
- MBL, HBL, contenedores, ETA, DTA, motonave y tracking.
- Estados visuales en frontend.

## Fase 4 - Automatizacion documental

- Carga y visualizacion PDF.
- OCR con pdfplumber, OpenCV y Tesseract.
- Validacion manual y persistencia de datos extraidos.

## Fase 5 - Salidas empresariales

- PDFs profesionales con ReportLab.
- Exportacion XLSX.
- Correos HTML con adjuntos.
- Historial documental y notificaciones.

## Fase 6 - Endurecimiento

- Pruebas unitarias y de integracion.
- Observabilidad operativa.
- Optimizacion de consultas.
- Politicas de auditoria y retencion documental.

## Fase 7 - Gobierno de requerimientos

- Matriz de trazabilidad completa entre requerimientos, historias, endpoints, pantallas y pruebas.
- Criterios de aceptacion por historia de usuario.
- Catalogo de reglas de negocio versionado.
- Control de cambios de alcance.
- Priorizacion MoSCoW: obligatorio, deberia tener, podria tener, fuera de alcance.

## Fase 8 - Seguridad y auditoria avanzada

- Permisos por accion y no solo por modulo.
- Bitacora de cambios por usuario, entidad y fecha.
- Politicas de retencion documental.
- Recuperacion de contrasena y bloqueo por intentos fallidos.
- Configuracion productiva con HTTPS, secretos seguros y respaldos programados.
