# Requerimientos

## Objetivo

El sistema debe centralizar la gestion comercial, logistica y documental de importaciones maritimas, garantizando trazabilidad desde la solicitud de cotizacion hasta la generacion de documentos, tracking del embarque, OCR documental y notificacion al cliente.

## Alcance por rol

| Rol | Funciones permitidas |
| --- | --- |
| Cliente | Solicitar cotizaciones, consultar embarques propios, revisar tracking y descargar documentos autorizados. |
| Agente Comercial | Crear clientes, gestionar cotizaciones, aprobar o rechazar solicitudes y consultar operaciones asignadas. |
| Sales Support | Cargar PDFs, ejecutar OCR, validar datos extraidos, generar documentos y apoyar seguimiento documental. |
| Administrador | Gestionar usuarios, roles, permisos, catalogos, auditoria y configuracion general del sistema. |

## Casos de uso

### UC-01 Login empresarial

Actor: Usuario interno o cliente.

Resultado: token JWT valido con rol para controlar acceso a operaciones.

Criterios:

- El sistema rechaza credenciales invalidas.
- El token incluye identificador de usuario, correo y rol.
- El endpoint `/auth/me` devuelve la informacion del usuario autenticado.

### UC-02 Solicitar cotizacion

Actor: Cliente.

Resultado: cotizacion creada en estado `REQUESTED` y notificacion al agente comercial.

Criterios:

- La cotizacion exige cliente, origen, destino, mercancia e incoterm.
- La cotizacion queda visible en el listado comercial.
- El sistema conserva fecha de creacion y estado.

### UC-03 Aprobar o rechazar cotizacion

Actor: Agente Comercial.

Resultado: cotizacion en estado `APPROVED` o `REJECTED`, historial operativo y correo al cliente.

Criterios:

- Solo usuarios autorizados pueden decidir una cotizacion.
- La aprobacion registra fecha de decision.
- Una cotizacion rechazada no debe convertirse en embarque.

### UC-04 Crear embarque

Actor: Agente Comercial.

Resultado: embarque directo o consolidado con MBL, HBL, contenedores, ETA, DTA, naviera y puertos.

Criterios:

- El embarque exige cliente, tipo, MBL, motonave, origen, destino y mercancia.
- Un embarque consolidado puede asociar multiples HBL.
- Los contenedores quedan vinculados al embarque correcto.

### UC-05 Procesar PDF externo

Actor: Sales Support.

Resultado: documento almacenado, OCR ejecutado y datos extraidos listos para validacion.

Criterios:

- El PDF cargado queda en historial documental.
- El archivo puede visualizarse o descargarse.
- El OCR guarda texto bruto, campos extraidos y nivel de confianza cuando este disponible.

### UC-06 Validar OCR

Actor: Sales Support.

Resultado: datos corregidos y persistidos sobre embarque, MBL, HBL y contenedores.

Criterios:

- La validacion cambia el documento a estado `VALIDATED`.
- Los campos criticos deben compararse contra el PDF visible.
- Si el OCR no encuentra campos minimos, el documento debe quedar pendiente de revision manual.

### UC-07 Generar documentos PDF

Actor: Agente Comercial o Sales Support.

Resultado: factura, cotizacion, guia logistica, reporte, draft, comprobante o resumen de embarque generado, almacenado y disponible para envio.

Criterios:

- Todo PDF generado queda registrado como documento del sistema.
- El documento generado queda disponible para descarga.
- La plantilla debe incluir datos logisticos clave del embarque.

### UC-08 Notificar cliente

Actor: Sistema.

Resultado: correo HTML empresarial con estado, datos logisticos, enlaces y PDFs adjuntos cuando aplique.

Criterios:

- La notificacion conserva estado `PENDING`, `SENT`, `FAILED` o `RETRIED`.
- El historial permite auditar asunto, cuerpo, fecha y operacion relacionada.
- Los adjuntos deben corresponder a documentos autorizados para el destinatario.

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

## Reglas de negocio

- Una cotizacion aprobada puede originar un embarque; una rechazada o vencida no.
- Una cotizacion en revision no debe perder la trazabilidad de quien la solicito y quien la gestiona.
- Un embarque debe manejar estados controlados: `CREATED`, `DOCUMENT_REVIEW`, `IN_TRANSIT`, `ARRIVED`, `NATIONALIZATION`, `RELEASED`, `CLOSED`.
- Un documento externo cargado inicia como `OCR_PENDING` cuando requiere extraccion automatica.
- Un documento con OCR ejecutado pasa a `OCR_PROCESSED` y solo debe usarse como fuente oficial despues de validacion.
- Un documento puede rechazarse si el archivo no corresponde, esta danado o los datos extraidos no son confiables.
- Los documentos generados por el sistema deben marcarse como `GENERATED`.
- Las notificaciones fallidas deben poder reintentarse y conservar historial.

## Validaciones funcionales

| Campo/Proceso | Validacion |
| --- | --- |
| MBL/HBL | No debe estar vacio y debe conservar formato alfanumerico. |
| Contenedor | Debe registrar numero, tipo y relacion con un embarque. |
| ETA/DTA | Deben ser fechas validas y coherentes con el flujo operativo. |
| PDF | Debe almacenarse con nombre seguro y ruta controlada. |
| OCR | Debe guardar texto bruto aunque no logre extraer todos los campos. |
| Cotizacion | Debe tener cliente, ruta, mercancia e incoterm. |
| Factura PDF | Debe asociarse a un embarque o payload operativo valido. |

## Requerimientos no funcionales

- Seguridad: control de acceso por rol, tokens JWT, contrasenas cifradas y secretos seguros en produccion.
- Auditoria: registrar usuario, fecha, accion, entidad afectada y valores relevantes.
- Rendimiento: consultas operativas comunes deben responder en tiempos aptos para trabajo administrativo diario.
- Disponibilidad: el entorno local debe levantarse con Docker Compose.
- Mantenibilidad: respetar separacion entre dominio, aplicacion, infraestructura y presentacion.
- Integridad: documentos y base de datos deben respaldarse como una unidad logica.
- Observabilidad: errores de OCR, correo, storage y base de datos deben registrarse con suficiente contexto.

## Matriz de trazabilidad

| ID | Necesidad | Caso de uso | Modulo | Prueba/Evidencia |
| --- | --- | --- | --- | --- |
| RF-01 | Acceso seguro | UC-01 | Auth | `test_auth_api.py` |
| RF-02 | Gestionar clientes | UC-02/UC-04 | Clientes | `test_clients_api.py` |
| RF-03 | Control comercial | UC-02/UC-03 | Cotizaciones | `test_quotations_use_cases.py` |
| RF-04 | Operacion maritima | UC-04 | Embarques | `test_shipments_api.py` |
| RF-05 | Gestion documental | UC-05 | Documentos | `test_documents_api.py` |
| RF-06 | OCR y validacion | UC-05/UC-06 | OCR | `test_document_services.py` |
| RF-07 | Generacion PDF | UC-07 | PDFs | Historial documental |
| RF-08 | Exportacion | UC-07 | Exportaciones | `test_exports_api.py` |
| RF-09 | Notificaciones | UC-08 | Notificaciones | Historial de envio |

## Riesgos y supuestos

- La precision OCR puede variar por calidad, orientacion, idioma y estructura del PDF.
- Los formatos de navieras pueden requerir reglas de extraccion especificas.
- La operacion real puede necesitar integracion con ERP, correo corporativo, aduana o proveedores logisticos.
- Los documentos contienen informacion sensible y requieren controles de acceso antes de produccion.
- El proyecto asume que el almacenamiento local de documentos se respalda junto con la base de datos.
