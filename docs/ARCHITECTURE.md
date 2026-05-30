# Arquitectura

## Estilo

El sistema usa Clean Architecture estricta para aislar reglas de negocio, casos de uso, adaptadores externos y entrada HTTP.

```text
src/
  domain/          Entidades, enums, reglas e interfaces de repositorio
  application/     Casos de uso, DTOs y puertos de servicios externos
  infrastructure/  SQLAlchemy, OCR, PDF, SMTP, storage y repositorios concretos
  presentation/    FastAPI, routers, dependencias y seguridad HTTP
  shared/          Configuracion y utilidades transversales
```

## Principios aplicados

- SOLID.
- Separacion de responsabilidades.
- Dependencias hacia adentro: presentation -> application -> domain.
- Infraestructura implementa puertos definidos por application/domain.
- Tipado fuerte con Pydantic y TypeScript.
- Persistencia desacoplada mediante repositorios.
- Procesamiento documental desacoplado mediante servicios OCR, PDF, storage y correo.

## Modulos funcionales

- Autenticacion y roles.
- Clientes, empresas y contactos.
- Cotizaciones.
- Embarques maritimos.
- Documentos y OCR.
- Exportacion XLSX.
- Generacion PDF.
- Notificaciones.
- Auditoria operativa y trazabilidad.

## Flujo principal

Cliente solicita cotizacion. El agente comercial revisa y gestiona la solicitud. Al recibir documentos de naviera, Sales Support carga PDFs, el sistema ejecuta OCR, extrae datos logisticos, permite validacion manual y almacena la informacion. Luego el embarque queda disponible para tracking, generacion documental, notificacion al cliente y exportacion XLSX.

## Decisiones tecnicas

- PostgreSQL como fuente transaccional.
- SQLAlchemy 2.x para persistencia.
- FastAPI para API REST versionada.
- Pydantic para contratos HTTP y DTOs.
- ReportLab para PDFs empresariales programaticos.
- Tesseract, pdfplumber y OpenCV para OCR de PDFs escaneados o digitales.
- SMTP como adaptador base de correo, sustituible por SendGrid o Amazon SES.
