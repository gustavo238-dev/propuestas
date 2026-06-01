# Sistema de Gestion de Importaciones Maritimas

Plataforma web empresarial para automatizar procesos logisticos y documentales de importaciones maritimas.

## Objetivo del proyecto

Centralizar la operacion comercial, logistica y documental de importaciones maritimas en una sola plataforma. El sistema permite registrar clientes, cotizar operaciones, administrar embarques, controlar documentos, ejecutar OCR sobre PDFs logisticos, generar documentos empresariales y mantener trazabilidad de notificaciones y estados.

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

## Roles y responsabilidades

| Rol | Responsabilidades principales |
| --- | --- |
| Cliente | Solicitar cotizaciones, consultar sus embarques, revisar estados y descargar documentos autorizados. |
| Agente Comercial | Registrar clientes, crear y revisar cotizaciones, dar seguimiento comercial y consultar embarques asociados. |
| Sales Support | Cargar documentos, ejecutar OCR, validar datos extraidos, generar PDFs y apoyar la operacion documental. |
| Administrador | Gestionar usuarios, permisos, catalogos, auditoria, configuraciones y supervision general del sistema. |

## Reglas de negocio

- Una cotizacion solo puede aprobarse si tiene cliente, origen, destino, descripcion de mercancia, incoterm y costo estimado cuando aplique.
- Una cotizacion aprobada puede convertirse en base para crear un embarque.
- Un embarque debe tener cliente, tipo de embarque, MBL, motonave, puerto de origen, puerto de destino y descripcion de mercancia.
- Un embarque consolidado puede contener varios HBL y contenedores asociados.
- La fecha ETA no debe ser posterior a la DTA cuando ambas fechas existan en el flujo operativo definido por la empresa.
- Un documento cargado debe quedar asociado a un historial documental y conservar su ruta de almacenamiento.
- El OCR debe permitir validacion manual antes de usar los datos extraidos como informacion definitiva.
- Una factura o PDF empresarial generado debe guardarse como documento del sistema y quedar disponible para descarga.
- Las notificaciones deben conservar historial de estado: pendiente, enviada, fallida o reintentada.
- Los documentos sensibles solo deben ser visibles para usuarios autorizados segun rol y relacion con la operacion.

## Estados principales

| Entidad | Estados sugeridos |
| --- | --- |
| Cotizacion | Solicitada, En revision, Aprobada, Rechazada, Vencida |
| Embarque | Creado, Revision documental, En transito, Arribado, Nacionalizacion, Liberado, Cerrado |
| Documento | Cargado, OCR pendiente, OCR procesado, Validado, Rechazado, Generado |
| Notificacion | Pendiente, Enviada, Fallida, Reintentada |

## Requerimientos no funcionales

- Seguridad: autenticacion JWT, contrasenas cifradas, control de acceso por roles y proteccion de endpoints.
- Auditoria: registrar usuario, fecha y accion para cargas documentales, validaciones, cambios de estado y generacion de PDFs.
- Disponibilidad: ejecucion local orquestada con Docker Compose para facilitar despliegue y pruebas.
- Rendimiento: la API debe responder consultas operativas comunes en tiempos aceptables para uso administrativo diario.
- Escalabilidad: separar backend, frontend, base de datos, almacenamiento documental, Redis y correo para permitir crecimiento modular.
- Mantenibilidad: conservar arquitectura por capas y documentacion tecnica en `docs/`.
- Integridad documental: conservar historial, ruta, estado y relacion con embarques para cada archivo cargado o generado.
- Recuperacion: definir politicas de respaldo para base de datos y carpeta de almacenamiento documental.

## Criterios de aceptacion clave

- Dado un usuario valido, cuando inicia sesion, entonces recibe un token JWT y puede consultar su informacion con `/auth/me`.
- Dado un cliente nuevo, cuando se registra una cotizacion, entonces queda almacenada con estado inicial y aparece en el listado de cotizaciones.
- Dado un embarque creado, cuando se agregan contenedores o HBL, entonces quedan asociados al embarque correcto.
- Dado un PDF valido, cuando se carga desde el centro documental, entonces queda almacenado, visible en historial y disponible para descarga.
- Dado un documento cargado, cuando se ejecuta OCR, entonces el sistema extrae campos logisticos y guarda el resultado para consulta.
- Dado un OCR procesado, cuando el usuario revisa los campos extraidos, entonces puede compararlos contra el PDF visible.
- Dado un embarque activo, cuando se genera una factura PDF, entonces el archivo queda almacenado como documento generado.
- Dado un evento operativo, cuando se envia una notificacion, entonces queda registrada en el historial con su estado.

## Matriz de trazabilidad resumida

| Necesidad del negocio | Modulo | Endpoint/Pantalla | Evidencia |
| --- | --- | --- | --- |
| Controlar acceso por usuario | Autenticacion | `/auth/login`, `/auth/me` | Pruebas de autenticacion |
| Administrar clientes | Clientes | `/clients`, pantalla Clientes | Pruebas de clientes |
| Gestionar cotizaciones | Cotizaciones | `/quotations`, pantalla Cotizaciones | Pruebas de cotizaciones |
| Controlar embarques | Embarques | `/shipments`, pantalla Embarques/Tracking | Pruebas de embarques |
| Gestionar documentos | Documentos | `/documents`, pantalla Documentos | Pruebas de documentos |
| Extraer informacion de PDFs | OCR | `/documents/{id}/ocr` | Pruebas de servicios documentales |
| Generar documentos empresariales | PDFs | `/pdf/invoices/store` | Documento generado en historial |
| Exportar informacion | Exportaciones | `/exports/*` | Pruebas de exportacion |

## Riesgos y supuestos

- La precision del OCR depende de la calidad del PDF, resolucion, idioma, orientacion y formato de la naviera.
- Los formatos documentales pueden variar entre navieras, agentes y clientes.
- El almacenamiento documental debe respaldarse junto con la base de datos para evitar perdida de trazabilidad.
- La seguridad debe reforzarse antes de produccion con secretos reales, HTTPS, politicas de contrasenas y auditoria completa.
- Los datos iniciales y algunos flujos pueden requerir integracion posterior con sistemas externos de navieras, aduana, correo o ERP.

## Alcance actual y pendientes

| Area | Estado actual | Mejora pendiente |
| --- | --- | --- |
| Backend | API REST base implementada con FastAPI | Endurecer permisos por accion y auditoria detallada |
| Frontend | Dashboard operativo con modulos principales | Mejorar manejo de sesiones, errores y perfiles por rol |
| Base de datos | Modelo relacional operativo | Agregar migraciones formales y politicas de retencion |
| Documentos | Carga, descarga, historial y OCR | Validacion manual avanzada y versionado documental |
| PDFs | Generacion de documentos empresariales | Plantillas configurables por empresa |
| Notificaciones | Envio e historial local | Reintentos, plantillas y monitoreo de fallos |
| Pruebas | Pruebas unitarias principales | Ampliar pruebas de integracion y seguridad |

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
