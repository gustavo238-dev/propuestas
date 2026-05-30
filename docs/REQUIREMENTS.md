# Requerimientos

## Casos de uso

### UC-01 Login empresarial

Actor: Usuario interno o cliente.

Resultado: token JWT valido con rol para controlar acceso a operaciones.

### UC-02 Solicitar cotizacion

Actor: Cliente.

Resultado: cotizacion creada en estado `REQUESTED` y notificacion al agente comercial.

### UC-03 Aprobar o rechazar cotizacion

Actor: Agente Comercial.

Resultado: cotizacion en estado `APPROVED` o `REJECTED`, historial operativo y correo al cliente.

### UC-04 Crear embarque

Actor: Agente Comercial.

Resultado: embarque directo o consolidado con MBL, HBL, contenedores, ETA, DTA, naviera y puertos.

### UC-05 Procesar PDF externo

Actor: Sales Support.

Resultado: documento almacenado, OCR ejecutado y datos extraidos listos para validacion.

### UC-06 Validar OCR

Actor: Sales Support.

Resultado: datos corregidos y persistidos sobre embarque, MBL, HBL y contenedores.

### UC-07 Generar documentos PDF

Actor: Agente Comercial o Sales Support.

Resultado: factura, cotizacion, guia logistica, reporte, draft, comprobante o resumen de embarque generado, almacenado y disponible para envio.

### UC-08 Notificar cliente

Actor: Sistema.

Resultado: correo HTML empresarial con estado, datos logisticos, enlaces y PDFs adjuntos cuando aplique.

## Historias de usuario

- Como Cliente, quiero solicitar cotizaciones para iniciar operaciones de importacion maritima.
- Como Cliente, quiero consultar el estado de mis embarques para dar seguimiento a ETA, DTA y carga.
- Como Agente Comercial, quiero aprobar o rechazar cotizaciones para controlar el flujo comercial.
- Como Agente Comercial, quiero administrar embarques directos y consolidados para reflejar la operacion real.
- Como Sales Support, quiero cargar PDFs de naviera para extraer automaticamente datos logisticos.
- Como Sales Support, quiero validar datos OCR antes de guardarlos para reducir errores documentales.
- Como Administrador, quiero controlar usuarios y roles para proteger operaciones empresariales.
- Como usuario interno, quiero generar PDFs profesionales para compartir documentacion formal.
- Como usuario interno, quiero exportar datos XLSX para analisis y reportes operativos.
