---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Juntos-2026-06-19/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Juntos-2026-06-21/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Juntos-2026-06-21/EXPERIENCE.md
---

# Juntos - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Juntos, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: El Paciente o un Cuidador Principal puede crear, editar y eliminar medicamentos y sus horarios de toma (nombre, dosis, horario(s), flag Medicamento Crítico). Un cambio de horario se refleja a todo el Círculo de Cuidado en menos de ~5s.

FR-2: Cualquier miembro del Círculo de Cuidado puede ver el Calendario de Medicación Compartido, filtrado por su Nivel de Compartición de Datos (rol limitado ve solo estado agregado; Cuidador Principal ve detalle completo).

FR-3: El Paciente o un Cuidador Principal puede confirmar una toma, registrando la hora real de confirmación (separada de la hora programada); el estado cambia de "pendiente" a "tomada" para todo el Círculo de Cuidado.

FR-4: Al registrarse una Confirmación de Toma, el sistema notifica automáticamente (Confirmación Cruzada) a todos los demás miembros del Círculo de Cuidado con permiso para verla, en menos de ~10s, respetando el Nivel de Compartición (detalle completo vs. estado agregado).

FR-5: Un Cuidador con Nivel de Compartición que incluya historial puede ver el Panel de Adherencia Histórica de un Paciente por rango de fechas (ej. 7/30 días), mostrando como mínimo % confirmadas a tiempo, % confirmadas tarde, % no confirmadas.

FR-6: El sistema distingue una Alerta Puntual (dosis aislada no confirmada) de una Alerta de Patrón (incumplimiento en N días consecutivos, default `[ASSUMPTION: 3 días]`), notificando esta última a Cuidadores con visibilidad de adherencia histórica, sin reemplazar la Escalada de Notificaciones de la dosis individual.

FR-7: El Paciente o Cuidador Principal puede marcar/desmarcar cualquier medicamento como Crítico, cambiando inmediatamente los tiempos de espera de la cadena de escalada para ese medicamento.

FR-8: Si una dosis no se confirma dentro de la ventana esperada, el sistema escala automáticamente: push al Paciente → push a Cuidadores Principales → SMS a Cuidadores Principales → llamada automatizada al Paciente, deteniéndose de inmediato ante cualquier Confirmación de Toma; cada paso queda registrado (timestamp, canal, destinatario) de forma idempotente (clave `(doseId, stepIndex)`).

FR-9: El Paciente (o su Cuidador de Respaldo activo) puede designar uno o más Contactos de Emergencia, distintos de los Cuidadores del día a día; el Contacto de Emergencia no recibe notificaciones rutinarias y debe aceptar/confirmar su rol antes de quedar activo.

FR-10: Si la Cadena de Escalada se completa sin ninguna Confirmación de Toma, el sistema activa el Protocolo de Última Línea, notificando a todos los Contactos de Emergencia por todos los canales disponibles, con copy explícito de "última línea"; el evento queda registrado y visible para los Cuidadores Principales incluso después de resuelto.

FR-11: El sistema ofrece al menos dos Niveles de Compartición de Datos predefinidos (ej. "Completo" y "Solo alertas"); el nivel mínimo es el default para cualquier Cuidador nuevo; cambiar el nivel de un Cuidador existente se refleja en la siguiente vista que abra, sin reinvitación.

FR-12: Un Cuidador solo se asocia a un Paciente mediante invitación explícita del Paciente (o su Cuidador de Respaldo activo) que debe aceptarse explícitamente; no existe autoagregado; el Círculo de Cuidado tiene un máximo de 5 Cuidadores (bloqueo claro al límite); existe un flujo de creación asistida de cuenta con consentimiento documentado distinto cuando el Paciente no puede crearla por sí mismo.

FR-13: El Paciente puede designar, en cualquier momento, a un Cuidador existente como su Cuidador de Respaldo (solo uno activo a la vez, puede cambiarlo mientras conserve capacidad de decisión).

FR-14: El sistema ofrece un mecanismo explícito (no automático ni silencioso) por el cual el Cuidador de Respaldo puede solicitar asumir el control de la cuenta del Paciente; el evento de transferencia queda registrado de forma permanente y visible para todo el Círculo de Cuidado; una vez transferido, el Cuidador de Respaldo gestiona Cuidadores, Niveles de Compartición y Contacto de Emergencia en nombre del Paciente.

### NonFunctional Requirements

NFR-1 (Sincronización en tiempo real): Un cambio de estado (Confirmación de Toma, cambio de horario, cambio de permisos) debe reflejarse para todos los miembros conectados del Círculo de Cuidado en segundos, no minutos.

NFR-2 (Confiabilidad multicanal con degradación parcial): El sistema debe tolerar la falla de un canal externo individual (push/SMS/llamada) sin detener la Cadena de Escalada completa.

NFR-3 (Idempotencia): Dos procesos que detecten la misma dosis no confirmada no deben duplicar el mismo paso de la Cadena de Escalada.

NFR-4 (Disponibilidad diferenciada): El subsistema de Escalada de Notificaciones y Protocolo de Última Línea debe tener disponibilidad más alta que el resto de la app (objetivo numérico pendiente — Open Question del PRD).

NFR-5 (Auditabilidad inmutable): Toda acción sobre permisos, Contacto de Emergencia, Testamento Digital de Cuidado y cada paso de la Cadena de Escalada debe quedar registrada con timestamp y actor, de forma inmutable (append-only).

NFR-6 (Privacidad por defecto / mínimo dato necesario): El filtrado por Nivel de Compartición de Datos debe aplicarse de forma consistente en cada vista/consulta (calendario, notificaciones, panel de adherencia), no como excepción.

NFR-7 (Cumplimiento regulatorio): El tratamiento de datos de salud sensibles debe cumplir con la Ley 1581 de 2012 (Habeas Data, Colombia) como marco mínimo para el piloto; sin alcance HIPAA/GDPR en esta fase.

NFR-8 (Latencia de notificación inicial — FR-8): La entrega de la notificación inicial (push) debe iniciarse en menos de 60 segundos desde que se detecta la dosis no confirmada.

NFR-9 (Accesibilidad — WCAG 2.2 AA): Cumplimiento WCAG 2.2 AA como mínimo en móvil y web, dado que la audiencia incluye adultos mayores.

NFR-10 (Accesibilidad — Dynamic Type): El escalado de fuente del sistema (Dynamic Type) debe respetarse en el 100% de las pantallas; ninguna pantalla trunca contenido en el tamaño de accesibilidad más grande.

NFR-11 (Accesibilidad — lectores de pantalla): VoiceOver/TalkBack deben anunciar rol + estado en cada acción de confirmación; el banner de última línea debe anunciarse de inmediato al aparecer (aria-live/equivalente nativo asertivo).

### Additional Requirements

- Inicialización del proyecto con .NET Aspire Starter Application + .NET MAUI debe ser la primera historia de implementación (comando: `dotnet new aspire-starter --name Juntos --output .` + `dotnet new maui -o Juntos.Mobile -f net10.0` + `dotnet sln add ...`).
- Modelo de datos sobre Azure Database for PostgreSQL (Flexible Server) vía EF Core 10 + Npgsql + EFCore.NamingConventions, con EF Core Migrations.
- Autenticación vía ASP.NET Core Identity (self-hosted), emisión de tokens vía `MapIdentityApi`, consumidos por MAUI/Blazor como bearer tokens.
- Autorización basada en políticas resource-based (requirements/handlers personalizados) que evalúan el Nivel de Compartición específico por par Paciente-Cuidador (no roles fijos globales).
- Tiempo real vía SignalR sobre `ApiService` (`CrossConfirmationHub`); Azure SignalR Service en producción para escalar.
- `Juntos.EscalationWorker` como hosted service aislado (Aspire) para la Cadena de Escalada y Protocolo de Última Línea, comunicándose con `ApiService` únicamente vía estado compartido en PostgreSQL (tabla de auditoría/eventos), nunca por llamada HTTP directa.
- Integraciones externas aisladas en `EscalationWorker/Channels/`: Azure Notification Hubs (push), Azure Communication Services (SMS y llamada automatizada).
- Azure Cache for Redis desde el MVP, exclusivo de `ApiService`, para las vistas de lectura de Calendario Compartido y Panel de Adherencia Histórica; `EscalationWorker` no cachea nada.
- Tabla de auditoría inmutable (`audit_events`) con estructura `(timestamp UTC, actorId, eventType, payload)`, reutilizada por Gestión de Cuidadores, Testamento Digital y Cadena de Escalada.
- API REST vía Minimal API (.NET 10) con documentación OpenAPI nativa, errores en formato Problem Details (RFC 9457), rate limiting nativo de ASP.NET Core.
- Organización del código por feature (vertical slice) con arquitectura hexagonal (Domain/Application/Infrastructure) dentro de `ApiService` y `EscalationWorker`, según el glosario de traducción PRD→código fijado en Architecture.md.
- Infraestructura: despliegue en Azure Container Apps vía `azd`; CI/CD con GitHub Actions integrado con `azd` para build/deploy de `AppHost`, `ApiService`, `EscalationWorker`, `Web` y `Mobile`, escalando `EscalationWorker` de forma independiente.
- Observabilidad: OpenTelemetry vía `ServiceDefaults` → Azure Monitor / Application Insights; Aspire Dashboard para desarrollo local.
- Soporte offline: fuera de alcance del MVP (online-only); UX debe comunicar este límite explícitamente (ver UX-DR16).
- Conectividad online-only es un riesgo aceptado explícitamente por el usuario (UJ-2 podría retrasar registro de confirmación si el Paciente pierde conexión); no requiere mitigación técnica en el MVP, solo comunicación clara en UX.

### UX Design Requirements

UX-DR1: Implementar los design tokens de color (Verde Salvia `primary`, Verde Oscuro `primary-strong`, Terracota `accent`, Crema `surface-base`, Blanco `surface-raised`, escala de tinta `ink-*`, `border-hairline`, paleta de estado `status-on-time`/`status-late`/`status-pattern`/`status-critical`, variantes dark) de forma consistente en Mobile (MAUI) y Web (Blazor).

UX-DR2: Reservar `status-critical` (rojo `#C0392B`) exclusivamente para el Last-Line Banner / Protocolo de Última Línea — nunca para recordatorios rutinarios ni dosis simplemente tarde.

UX-DR3: Construir el componente reutilizable **Medication Card** (nombre del medicamento en `title`, hora programada en `meta`, `Status Chip` a la derecha, borde sutil de 2px en `status-critical` para medicamento marcado como crítico, nunca relleno rojo completo).

UX-DR4: Construir el componente reutilizable **Confirm Dose Button** (botón primario ancho completo, alto mínimo 56px, verbo explícito "Confirmar toma"; confirmación en dos pasos — tap + diálogo de confirmación — para dosis críticas, un paso para no críticas).

UX-DR5: Construir el componente reutilizable **Status Chip** (ícono + texto + color, nunca solo color) con los estados: "A tiempo" (verde), "Tarde" (ámbar), "Sin confirmar" (ámbar-tierra), "Última línea activada" (rojo); actualización en vivo vía SignalR sin pull-to-refresh.

UX-DR6: Construir el componente **Escalation Banner** (tono informativo, no alarmista; visible solo mientras la escalada está activa; desaparece automáticamente al confirmarse la dosis, sin acción manual de "descartar").

UX-DR7: Construir el componente **Last-Line Banner** (fondo `status-critical` sólido — único componente que lo usa como fondo; texto visible y permanente de que esto no sustituye una llamada a emergencias; botón directo para que el Contacto de Emergencia confirme que ya intervino, cerrando el banner para todos; prohibido swipe-to-dismiss).

UX-DR8: Construir el componente **Caregiver Avatar Row** (avatares circulares de 40px con indicador sutil de "en línea/sincronizado"; tap abre detalle de rol/permiso; nunca permite autoagregarse).

UX-DR9: Construir el componente **Adherence Badge/Chart** en `AdherenceDashboard` (Web), usando exclusivamente la paleta de estado ya definida, sin colores adicionales.

UX-DR10: Aplicar tipografía nativa de plataforma (`display`/`title`/`body`/`meta`) respetando Dynamic Type / escalado de fuente del sistema en el 100% de las pantallas, sin truncar contenido en el tamaño de accesibilidad más grande.

UX-DR11: Implementar la escala de espaciado (4/8/12/16/24/32/48px) y el layout responsivo: una sola columna siempre en móvil; panel web en dos columnas en escritorio (`≥lg`) colapsando a una columna en tablet/móvil web.

UX-DR12: Aplicar el sistema de formas (`rounded.sm` 8px en inputs/chips, `rounded.md` 14px en tarjetas/banners/diálogos, `rounded.full` en botón de confirmar toma y avatares); ningún componente interactivo angular o cortante.

UX-DR13: Cumplir WCAG 2.2 AA como mínimo en ambas superficies (móvil y web).

UX-DR14: Implementar soporte de lector de pantalla (VoiceOver/TalkBack): cada acción de confirmación anuncia rol + estado (ej. "Botón, Confirmar toma de Losartán 8am"); el Last-Line Banner se anuncia de inmediato al aparecer vía `aria-live` o equivalente nativo asertivo.

UX-DR15: Implementar el microcopy de voz y tono especificado (frases calmadas tipo "Aún no se confirma la toma de las 8am" en lugar de "¡Alerta! Medicamento no tomado") en notificaciones, banners y estados de toda la app.

UX-DR16: Implementar el banner persistente de estado offline ("Sin conexión — no podremos confirmar tomas ni avisar a tus cuidadores hasta reconectar"), visible globalmente y no descartable como un toast, dado que el MVP es online-only.

UX-DR17: Implementar la arquitectura de navegación: tabs inferiores en móvil (Calendario / Alertas / Adherencia) con Gestión de Cuidadores y Testamento Digital de Cuidado anidados en Configuración; barra lateral simple en web (Adherencia / Cuidadores); ningún modal se apila sobre otro modal.

UX-DR18: Implementar deep-link desde notificación push/SMS directo a la dosis específica en el Calendario, nunca a un home genérico.

UX-DR19: Implementar los estados de carga/vacío especificados: apertura en frío con caché o skeleton + "Cargando tu calendario"; calendario vacío con copy y CTA condicionado a permiso de rol; error de sincronización visible únicamente en Centro de Alertas, nunca bloqueando el Calendario.

UX-DR20: Implementar las reglas de interacción: prohibir swipe-to-dismiss en el Last-Line Banner y cualquier gesto que confirme una toma sin una acción deliberada; pull-to-refresh disponible pero nunca necesario (SignalR ya empuja el estado).

UX-DR21: Implementar lenguaje llano (sin jerga legal) en las pantallas de consentimiento de datos (Habeas Data) y de invitación de cuidadores, con resumen en español cotidiano antes de cualquier texto formal.

UX-DR22: Implementar el estado "Invitación pendiente" con chip visible ("Invitación enviada — esperando aceptación") junto al nombre/teléfono del cuidador invitado.

UX-DR23: Implementar el bloqueo de invitación al alcanzar el límite de 5 Cuidadores: botón de invitar deshabilitado con explicación clara, nunca un error técnico genérico.

UX-DR24: Implementar el estado de "Transferencia de Testamento Digital pendiente" para el Cuidador de Respaldo, requiriendo confirmación explícita (del Paciente si tiene capacidad, o de un segundo Cuidador) — nunca automática por inactividad.

### FR Coverage Map

FR-1: Epic 2 - Crear y editar horario de medicación
FR-2: Epic 2 - Vista compartida del calendario filtrada por Nivel de Compartición
FR-3: Epic 3 - Confirmar una toma
FR-4: Epic 3 - Notificación de Confirmación Cruzada
FR-5: Epic 5 - Panel de Adherencia Histórica
FR-6: Epic 5 - Alerta de Patrón vs. Alerta Puntual
FR-7: Epic 4 - Configurar criticidad por medicamento
FR-8: Epic 4 - Cadena de Escalada de Notificaciones
FR-9: Epic 4 - Designar Contacto de Emergencia
FR-10: Epic 4 - Activación del Protocolo de Última Línea
FR-11: Epic 1 - Definir Niveles de Compartición de Datos por rol
FR-12: Epic 1 - Invitación y Consentimiento explícito
FR-13: Epic 6 - Designar Cuidador de Respaldo
FR-14: Epic 6 - Transferencia de control al Cuidador de Respaldo

## Epic List

### Epic 1: Cuenta y Círculo de Cuidado
El Paciente puede crear su cuenta, invitar Cuidadores con un Nivel de Compartición de Datos definido, y cada Cuidador acepta explícitamente su invitación — sentando la base de identidad, autenticación y permisos sobre la que se apoyan todas las épicas siguientes. Incluye, como primeras historias, la inicialización del proyecto (.NET Aspire Starter + MAUI), el modelo de datos base, ASP.NET Core Identity, y el pipeline de CI/CD hacia Azure Container Apps.
**FRs covered:** FR-11, FR-12

### Epic 2: Calendario de Medicación Compartido
El Paciente o Cuidador Principal puede crear y editar el horario de medicamentos, y cualquier miembro del Círculo de Cuidado ve el calendario filtrado según su Nivel de Compartición — reemplazando la coordinación informal por WhatsApp.
**FRs covered:** FR-1, FR-2

### Epic 3: Confirmación de Toma y Confirmación Cruzada
El Paciente o Cuidador Principal puede confirmar una toma con su hora real, y todos los demás Cuidadores con permiso lo ven reflejado en tiempo real sin tener que preguntar — realiza completamente UJ-1.
**FRs covered:** FR-3, FR-4

### Epic 4: Escalada de Notificaciones y Protocolo de Última Línea
Cuando una dosis no se confirma, el sistema escala automáticamente por canal (push → SMS → llamada) con velocidad proporcional a la criticidad del medicamento, y si nadie responde, notifica al Contacto de Emergencia — realiza completamente UJ-2.
**FRs covered:** FR-7, FR-8, FR-9, FR-10

### Epic 5: Panel de Adherencia Histórica y Alerta de Patrón
Los Cuidadores con visibilidad de historial pueden ver la tendencia de cumplimiento de un Paciente en el tiempo, y reciben una Alerta de Patrón distinta de la alerta puntual cuando el incumplimiento se repite varios días — da al familiar a distancia la visibilidad que antes solo conseguía preguntando.
**FRs covered:** FR-5, FR-6

### Epic 6: Testamento Digital de Cuidado
El Paciente puede designar anticipadamente a un Cuidador de Respaldo, y este puede solicitar explícitamente asumir el control de la cuenta si el Paciente pierde capacidad de decisión — completa la promesa de continuidad sin improvisación de UJ-3.
**FRs covered:** FR-13, FR-14

## Epic 1: Cuenta y Círculo de Cuidado

El Paciente puede crear su cuenta, invitar Cuidadores con un Nivel de Compartición de Datos definido, y cada Cuidador acepta explícitamente su invitación — sentando la base de identidad, autenticación y permisos sobre la que se apoyan todas las épicas siguientes.

### Story 1.1: Inicializar la solución del proyecto y el pipeline de CI/CD

As a equipo de desarrollo,
I want tener la solución .NET Aspire + MAUI inicializada y un pipeline de CI/CD funcional,
So that cada historia siguiente se construye, prueba y despliega sobre una base reproducible desde el primer commit.

**Acceptance Criteria:**

**Given** un repositorio vacío del proyecto
**When** se ejecuta `dotnet new aspire-starter --name Juntos --output .` seguido de `dotnet new maui -o Juntos.Mobile -f net10.0` y `dotnet sln add Juntos.Mobile/Juntos.Mobile.csproj`
**Then** la solución `Juntos.sln` contiene los proyectos `AppHost`, `ServiceDefaults`, `ApiService`, `Web` y `Mobile`
**And** `dotnet run --project Juntos.AppHost` levanta todos los servicios localmente junto con el Aspire Dashboard mostrando logs/trazas de cada uno.

**Given** la solución inicializada
**When** se configura el pipeline de GitHub Actions
**Then** cada push ejecuta build y el proyecto de pruebas xUnit
**And** un push a la rama principal ejecuta `azd deploy` hacia Azure Container Apps sin intervención manual.

### Story 1.2: Registro e inicio de sesión del Paciente

As a Paciente,
I want crear mi cuenta e iniciar sesión,
So that pueda acceder a mi información de medicación y gestionar mi Círculo de Cuidado de forma segura.

**Acceptance Criteria:**

**Given** que no tengo una cuenta existente
**When** completo el registro con mis datos básicos (nombre, email/teléfono, contraseña)
**Then** ASP.NET Core Identity crea mi usuario y puedo iniciar sesión inmediatamente
**And** recibo un token vía `MapIdentityApi` que mi app móvil/web usa como bearer token en llamadas subsecuentes.

**Given** una cuenta ya creada
**When** inicio sesión con credenciales correctas
**Then** obtengo acceso autenticado a la app
**And** un intento con credenciales incorrectas muestra un mensaje de error claro sin revelar si el email/teléfono existe.

**Given** la pantalla de registro
**When** se presenta cualquier texto de consentimiento de datos
**Then** se muestra en lenguaje llano (no jerga legal) antes de cualquier texto formal, conforme a UX-DR21.

### Story 1.3: Crear el perfil del Paciente y su Círculo de Cuidado

As a Paciente,
I want completar mi perfil y tener un Círculo de Cuidado vacío asociado a mi cuenta,
So that pueda empezar a invitar Cuidadores en torno a mi seguimiento de medicación.

**Acceptance Criteria:**

**Given** que acabo de registrarme
**When** completo mi perfil (nombre, datos básicos de salud no sensibles)
**Then** el sistema crea automáticamente un Círculo de Cuidado vacío del cual soy el dueño
**And** el evento de creación queda registrado en `audit_events` con `(timestamp UTC, actorId, eventType, payload)` (NFR-5).

**Given** mi perfil completado
**When** abro la pantalla de Gestión de Cuidadores
**Then** veo el Círculo de Cuidado vacío con una invitación a agregar mi primer Cuidador (UX-DR19 estado vacío con CTA).

### Story 1.4: Invitar a un Cuidador con un Nivel de Compartición de Datos

As a Paciente o Cuidador Principal,
I want invitar a una persona a mi Círculo de Cuidado asignándole un Nivel de Compartición de Datos,
So that esa persona pueda ver y/o actuar sobre el seguimiento de medicación según el rol que yo defina.

**Acceptance Criteria:**

**Given** mi Círculo de Cuidado con menos de 5 Cuidadores
**When** invito a una persona por email/teléfono y selecciono un Nivel de Compartición ("Completo" o "Solo alertas")
**Then** se crea una invitación pendiente, no un Cuidador activo (FR-12: no autoagregado)
**And** si no asigno explícitamente un nivel, el sistema usa el nivel mínimo ("Solo alertas") como default (FR-11).

**Given** una invitación recién enviada
**When** veo la lista de Cuidadores
**Then** la persona invitada aparece con el chip "Invitación enviada — esperando aceptación" (UX-DR22)
**And** el evento de invitación queda registrado en `audit_events` (NFR-5).

**Given** uno o más Cuidadores activos en mi Círculo de Cuidado
**When** veo la lista de Cuidadores o el encabezado del Calendario
**Then** se muestra la Caregiver Avatar Row (avatares circulares con indicador sutil de sincronización), donde tocar un avatar abre el detalle de rol/permiso de esa persona (UX-DR8).

### Story 1.5: Aceptar invitación como Cuidador

As a persona invitada,
I want aceptar explícitamente la invitación a un Círculo de Cuidado,
So that quede claro que me uní por mi propia decisión y no por un autoagregado.

**Acceptance Criteria:**

**Given** una invitación pendiente dirigida a mi cuenta
**When** abro la invitación y la acepto explícitamente
**Then** paso a ser Cuidador activo del Círculo de Cuidado con el Nivel de Compartición que el Paciente me asignó
**And** el chip de "Invitación enviada — esperando aceptación" desaparece de la vista del Paciente, reemplazado por mi estado activo.

**Given** una invitación pendiente
**When** la rechazo en lugar de aceptarla
**Then** no se me asocia al Círculo de Cuidado y el Paciente puede ver que fue rechazada.

**Given** que aún no tengo cuenta en la app
**When** recibo una invitación
**Then** se me guía a crear mi cuenta (Story 1.2) antes de poder aceptarla.

### Story 1.6: Cambiar el Nivel de Compartición de un Cuidador existente

As a Paciente o Cuidador Principal,
I want cambiar el Nivel de Compartición de Datos de un Cuidador ya activo,
So that pueda ajustar lo que esa persona ve a medida que cambian las circunstancias, sin tener que reinvitarla.

**Acceptance Criteria:**

**Given** un Cuidador activo en mi Círculo de Cuidado
**When** cambio su Nivel de Compartición de "Solo alertas" a "Completo" (o viceversa)
**Then** el cambio se refleja en la siguiente vista que ese Cuidador abra, sin requerir una nueva invitación
**And** el cambio queda registrado en `audit_events` con el actor que lo realizó (NFR-5).

### Story 1.7: Remover a un Cuidador del Círculo de Cuidado

As a Paciente o Cuidador Principal,
I want remover a un Cuidador de mi Círculo de Cuidado,
So that esa persona deje de tener acceso a mi información de medicación cuando ya no corresponda.

**Acceptance Criteria:**

**Given** un Cuidador activo en mi Círculo de Cuidado
**When** lo remuevo
**Then** pierde inmediatamente acceso al Calendario, notificaciones y Panel de Adherencia de ese Paciente
**And** la remoción queda registrada en `audit_events` con timestamp y actor (NFR-5).

### Story 1.8: Bloquear nuevas invitaciones al alcanzar el límite de 5 Cuidadores

As a Paciente o Cuidador Principal,
I want que el sistema me impida invitar a un sexto Cuidador,
So that se respete el límite de 5 Cuidadores por Círculo de Cuidado definido en el PRD.

**Acceptance Criteria:**

**Given** un Círculo de Cuidado con 5 Cuidadores activos (o invitaciones pendientes que cuentan hacia el límite)
**When** intento invitar a una sexta persona
**Then** el botón de invitar aparece deshabilitado con una explicación clara del límite alcanzado (UX-DR23), nunca un error técnico genérico
**And** ninguna invitación se crea mientras el límite esté alcanzado.

### Story 1.9: Crear cuenta asistida para un Paciente con consentimiento documentado

As a Cuidador,
I want crear la cuenta en nombre de un Paciente que no puede hacerlo por sí mismo,
So that el Paciente quede registrado en el sistema con un consentimiento asistido explícito y distinto del flujo de autoinvitación estándar.

**Acceptance Criteria:**

**Given** que actúo en nombre de un Paciente que no puede completar el registro estándar (ej. condición de salud reciente)
**When** completo el flujo de creación asistida
**Then** el sistema registra explícitamente quién creó la cuenta y bajo qué consentimiento asistido, distinto del registro estándar (FR-12)
**And** ese registro de consentimiento asistido queda en `audit_events` de forma inmutable (NFR-5)
**And** el texto de consentimiento se presenta en lenguaje llano antes de cualquier texto formal (UX-DR21).

## Epic 2: Calendario de Medicación Compartido

El Paciente o Cuidador Principal puede crear y editar el horario de medicamentos, y cualquier miembro del Círculo de Cuidado ve el calendario filtrado según su Nivel de Compartición — reemplazando la coordinación informal por WhatsApp.

### Story 2.1: Crear un medicamento con su horario de toma

As a Paciente o Cuidador Principal,
I want crear un medicamento con su nombre, dosis, horario(s) de toma y un flag de Medicamento Crítico,
So that quede registrado en el Calendario de Medicación Compartido para todo mi Círculo de Cuidado.

**Acceptance Criteria:**

**Given** que soy el Paciente o un Cuidador Principal de un Círculo de Cuidado
**When** creo un medicamento con nombre, dosis, uno o más horarios de toma, y marco o no el flag de Medicamento Crítico
**Then** el medicamento queda guardado y visible en el Calendario de Medicación Compartido
**And** un Cuidador con rol limitado no puede crear medicamentos — la acción de crear solo está disponible para Paciente y Cuidador Principal.

### Story 2.2: Editar el horario o dosis de un medicamento existente

As a Paciente o Cuidador Principal,
I want editar el nombre, dosis u horario de un medicamento existente,
So that el Calendario refleje cambios reales en el tratamiento sin tener que recrear el medicamento.

**Acceptance Criteria:**

**Given** un medicamento existente en el Calendario
**When** edito su dosis, nombre o horario de toma
**Then** los cambios se guardan y el medicamento mantiene su historial de Confirmaciones de Toma previas sin alterarlas.

### Story 2.3: Eliminar un medicamento del Calendario

As a Paciente o Cuidador Principal,
I want eliminar un medicamento que ya no se toma,
So that el Calendario Compartido refleje únicamente el tratamiento vigente.

**Acceptance Criteria:**

**Given** un medicamento existente en el Calendario
**When** lo elimino
**Then** deja de aparecer en las vistas futuras del Calendario para todos los miembros del Círculo de Cuidado
**And** el historial de Confirmaciones de Toma ya registradas para ese medicamento se conserva para el Panel de Adherencia Histórica.

### Story 2.4: Ver el Calendario de Medicación filtrado por Nivel de Compartición de Datos

As a miembro del Círculo de Cuidado,
I want ver el Calendario de Medicación filtrado según mi Nivel de Compartición de Datos,
So that vea exactamente la información que mi rol permite, ni más ni menos.

**Acceptance Criteria:**

**Given** un Cuidador con Nivel de Compartición "Completo"
**When** abre el Calendario de Medicación
**Then** ve el detalle completo: medicamento, dosis, hora programada y hora real de confirmación de cada dosis.

**Given** un Cuidador con Nivel de Compartición "Solo alertas"
**When** abre el Calendario de Medicación
**Then** ve únicamente el estado general por dosis ("al día" / "alerta activa"), sin el detalle del medicamento o la dosis (FR-2, NFR-6).

**Given** un Paciente sin medicamentos aún creados
**When** abre su Calendario
**Then** ve el estado vacío "Aún no hay medicamentos en tu calendario" con una acción para agregar uno, visible solo si su rol tiene permiso de creación (UX-DR19).

**Given** la pantalla del Calendario como home de la app móvil
**When** navego por la app
**Then** encuentro tabs inferiores para Calendario / Alertas / Adherencia, con Gestión de Cuidadores y Testamento Digital de Cuidado anidados en Configuración; en la superficie web encuentro una barra lateral simple con Adherencia / Cuidadores (UX-DR17).

**Given** que pierdo la conexión a internet mientras tengo la app abierta (MVP online-only)
**When** se detecta la pérdida de conectividad
**Then** se muestra un banner persistente y visible (no un toast) indicando "Sin conexión — no podremos confirmar tomas ni avisar a tus cuidadores hasta reconectar" (UX-DR16).

### Story 2.5: Sincronización en tiempo real de cambios del Calendario entre dispositivos del Círculo de Cuidado

As a miembro del Círculo de Cuidado,
I want que cualquier cambio de horario hecho por otro Cuidador se refleje en mi propio dispositivo sin recargar manualmente,
So that toda la familia vea siempre el mismo Calendario actualizado.

**Acceptance Criteria:**

**Given** dos o más miembros del Círculo de Cuidado con la app abierta
**When** un Cuidador Principal crea, edita o elimina un medicamento
**Then** el cambio se refleja en las pantallas de los demás miembros conectados en menos de 5 segundos, sin pull-to-refresh (FR-1, NFR-1)
**And** el filtrado por Nivel de Compartición de cada miembro (Story 2.4) se sigue respetando en la actualización en vivo.

## Epic 3: Confirmación de Toma y Confirmación Cruzada

El Paciente o Cuidador Principal puede confirmar una toma con su hora real, y todos los demás Cuidadores con permiso lo ven reflejado en tiempo real sin tener que preguntar — realiza completamente UJ-1.

### Story 3.1: Confirmar una toma con hora real

As a Paciente o Cuidador Principal,
I want marcar una dosis programada como tomada,
So that quede registrada la hora real en que ocurrió, no solo la hora programada.

**Acceptance Criteria:**

**Given** una dosis pendiente en el Calendario
**When** confirmo la toma
**Then** la dosis cambia de estado "pendiente" a "tomada" para todos los miembros del Círculo de Cuidado
**And** se almacena la hora real de confirmación por separado de la hora programada (FR-3)
**And** la hora real (no la programada) es la que alimentará el Panel de Adherencia Histórica (Epic 5)
**And** el registro de la Confirmación de Toma queda disponible como evento de dominio (`DoseConfirmed`) que otras épicas futuras (Escalada de Notificaciones, Epic 4) pueden consumir para detener procesos en curso, sin que esta historia dependa de que esas épicas existan todavía.

### Story 3.2: Notificación de Confirmación Cruzada en tiempo real

As a Cuidador,
I want recibir una notificación automática cuando otro miembro confirma una toma,
So that sepa que ocurrió sin tener que preguntar o revisar manualmente.

**Acceptance Criteria:**

**Given** que un Paciente o Cuidador Principal confirma una toma
**When** la Confirmación de Toma se registra
**Then** todos los demás miembros del Círculo de Cuidado con permiso para verla reciben la notificación de Confirmación Cruzada en menos de 10 segundos (FR-4)
**And** el Status Chip de su Calendario cambia a "A tiempo" en vivo vía SignalR, sin necesidad de pull-to-refresh (UX-DR5).

**Given** que el propio Cuidador que confirmó la toma sigue viendo la pantalla
**When** se procesa la Confirmación Cruzada
**Then** no recibe una notificación push duplicada para una acción que él mismo acaba de realizar.

### Story 3.3: Confirmación en dos pasos para dosis críticas

As a Paciente o Cuidador Principal,
I want que confirmar una dosis marcada como Crítica requiera un paso adicional de confirmación,
So that no se dispare accidentalmente el cierre de una cadena de notificaciones importante con un toque accidental.

**Acceptance Criteria:**

**Given** una dosis de un medicamento marcado como Crítico
**When** toco el botón de confirmar toma
**Then** se presenta un diálogo de confirmación adicional antes de registrar la toma (UX-DR4)
**And** solo tras confirmar explícitamente en ese diálogo se registra la Confirmación de Toma.

**Given** una dosis de un medicamento no Crítico
**When** toco el botón de confirmar toma
**Then** la toma se confirma con un solo paso, sin diálogo adicional.

**Given** que uso VoiceOver/TalkBack
**When** interactúo con el botón de Confirmar Toma
**Then** se anuncia rol + estado de la acción (ej. "Botón, Confirmar toma de Losartán 8am") (UX-DR14, NFR-11).

### Story 3.4: Confirmación Cruzada filtrada por Nivel de Compartición

As a Cuidador con Nivel de Compartición limitado,
I want recibir solo un estado agregado de la Confirmación Cruzada,
So that no vea el detalle de medicamento o dosis si mi rol no me lo permite.

**Acceptance Criteria:**

**Given** un Cuidador con Nivel de Compartición "Solo alertas"
**When** se registra una Confirmación de Toma de otro miembro
**Then** recibe únicamente un estado agregado (ej. "dosis de la tarde: tomada"), sin el nombre del medicamento o la dosis exacta (FR-4, NFR-6).

**Given** un Cuidador con Nivel de Compartición "Completo"
**When** se registra una Confirmación de Toma
**Then** recibe el detalle completo: medicamento, dosis, hora real de confirmación y quién confirmó.

## Epic 4: Escalada de Notificaciones y Protocolo de Última Línea

Cuando una dosis no se confirma, el sistema escala automáticamente por canal (push → SMS → llamada) con velocidad proporcional a la criticidad del medicamento, y si nadie responde, notifica al Contacto de Emergencia — realiza completamente UJ-2.

### Story 4.1: Marcar/desmarcar un medicamento como Crítico

As a Paciente o Cuidador Principal,
I want marcar o desmarcar un medicamento como Crítico,
So that la velocidad de la Cadena de Escalada se ajuste automáticamente al riesgo real de omitirlo.

**Acceptance Criteria:**

**Given** un medicamento existente en el Calendario
**When** marco o desmarco su flag de Medicamento Crítico
**Then** el cambio se aplica inmediatamente a los tiempos de espera de la Cadena de Escalada para ese medicamento, sin reiniciar nada (FR-7)
**And** el medicamento marcado como Crítico muestra un borde sutil de 2px en `status-critical`, nunca relleno rojo completo (UX-DR3).

### Story 4.2: Iniciar la Cadena de Escalada con push al Paciente y a Cuidadores Principales

As a sistema,
I want detectar una dosis no confirmada dentro de la ventana esperada e iniciar la Cadena de Escalada con notificaciones push,
So that el Paciente y sus Cuidadores Principales se enteren proactivamente sin que nadie tenga que monitorear manualmente.

**Acceptance Criteria:**

**Given** una dosis cuya ventana de tiempo esperada de confirmación ya pasó sin registro
**When** el `EscalationWorker` la detecta
**Then** envía push al Paciente en menos de 60 segundos desde la detección (NFR-8)
**And**, si no hay confirmación tras el intervalo definido, envía push a los Cuidadores Principales
**And** para un medicamento Crítico, el tiempo entre cada paso es menor que para uno no Crítico (FR-7, FR-8)
**And** el Escalation Banner aparece en el Calendario de los Cuidadores con tono informativo, no alarmista (UX-DR6)
**And** la notificación push incluye un deep-link que abre directamente la dosis específica en el Calendario, no un home genérico (UX-DR18).

**Given** que dos instancias del `EscalationWorker` evalúan la misma dosis no confirmada simultáneamente
**When** ambas intentan ejecutar el mismo paso de push
**Then** la clave idempotente `(doseId, stepIndex)` garantiza que el paso se ejecuta una sola vez (FR-8, NFR-3).

**Given** que `EscalationWorker` corre como hosted service aislado del `ApiService`
**When** se despliega a Azure Container Apps
**Then** puede escalar de forma independiente del resto de la app, satisfaciendo el requisito de disponibilidad diferenciada del subsistema de Escalada/Última Línea (NFR-4).

### Story 4.3: Escalar a SMS a Cuidadores Principales

As a sistema,
I want escalar a SMS cuando el push a los Cuidadores Principales no obtiene confirmación,
So that el siguiente canal de la Cadena de Escalada se intente sin depender de que alguien vea la notificación push.

**Acceptance Criteria:**

**Given** que el push a los Cuidadores Principales no resultó en una Confirmación de Toma dentro del intervalo definido
**When** el `EscalationWorker` avanza al siguiente paso
**Then** envía SMS a los Cuidadores Principales vía Azure Communication Services
**And** cada paso ejecutado (timestamp, canal, destinatario) queda registrado para auditoría y para el Panel de Adherencia Histórica (FR-8).

**Given** que el proveedor de SMS falla al enviar
**When** se detecta la falla
**Then** el fallo se registra como `Warning` (no detiene la cadena) y el `EscalationWorker` continúa con el siguiente paso (NFR-2).

### Story 4.4: Escalar a llamada automatizada al Paciente

As a sistema,
I want escalar a una llamada automatizada al propio Paciente cuando el SMS no obtiene confirmación,
So that se intente un último contacto directo antes de notificar al Contacto de Emergencia.

**Acceptance Criteria:**

**Given** que el SMS a los Cuidadores Principales no resultó en una Confirmación de Toma dentro del intervalo definido
**When** el `EscalationWorker` avanza al siguiente paso
**Then** ejecuta una llamada automatizada al propio Paciente vía Azure Communication Services
**And** este es el último paso de la Cadena de Escalada (FR-8) antes de evaluar el Protocolo de Última Línea (Epic 4, Story 4.7).

### Story 4.5: Detener la Cadena de Escalada ante cualquier Confirmación de Toma

As a Paciente,
I want que confirmar mi toma en cualquier punto detenga inmediatamente la Cadena de Escalada,
So that no se siga notificando a mi familia por una dosis que ya tomé, evitando falsos positivos.

**Acceptance Criteria:**

**Given** una Cadena de Escalada en curso para una dosis (en cualquier paso: push, SMS o llamada)
**When** se registra una Confirmación de Toma para esa dosis
**Then** todos los pasos restantes se detienen de inmediato y no se notifica a nadie más por esa dosis (FR-8)
**And** el Escalation Banner desaparece automáticamente del Calendario sin acción manual de "descartar" (UX-DR6).

### Story 4.6: Designar Contacto(s) de Emergencia

As a Paciente o Cuidador de Respaldo activo,
I want designar uno o más Contactos de Emergencia distintos de mis Cuidadores del día a día,
So that exista alguien a quien notificar únicamente si la Escalada completa no obtiene respuesta.

**Acceptance Criteria:**

**Given** que designo a una persona como Contacto de Emergencia
**When** la invitación se envía
**Then** esa persona debe aceptar/confirmar su rol antes de quedar activa (consistente con FR-12)
**And** un Contacto de Emergencia activo no recibe ninguna notificación del Calendario Compartido ni de Confirmaciones Cruzadas — únicamente se le notifica si se activa el Protocolo de Última Línea (FR-9).

### Story 4.7: Activar el Protocolo de Última Línea tras agotar la Cadena de Escalada

As a Contacto de Emergencia,
I want ser notificado por todos los canales disponibles cuando la Cadena de Escalada se agota sin ninguna Confirmación de Toma,
So that pueda intervenir cuando nadie más en el círculo de cuidado ha respondido.

**Acceptance Criteria:**

**Given** que la Cadena de Escalada (push → SMS → llamada) se completó sin ninguna Confirmación de Toma
**When** el `EscalationWorker` agota el último paso
**Then** notifica a todos los Contactos de Emergencia por todos los canales disponibles (FR-10)
**And** la notificación indica explícitamente que se trata de una alerta de "última línea" (medicamento sin confirmar tras escalada completa), no una alerta genérica
**And** el Last-Line Banner se muestra con fondo `status-critical` sólido, con el texto visible de que esto no sustituye una llamada a emergencias, y sin permitir swipe-to-dismiss (UX-DR7)
**And** el Last-Line Banner se anuncia de inmediato al aparecer vía `aria-live` o equivalente nativo asertivo para VoiceOver/TalkBack (UX-DR14, NFR-11).

**Given** que el Protocolo de Última Línea ya se activó
**When** el Contacto de Emergencia confirma desde el banner que ya intervino
**Then** el evento de resolución se registra de forma permanente y visible para los Cuidadores Principales, incluso después de resuelto (FR-10, NFR-5)
**And** el Last-Line Banner se cierra para todos los miembros del Círculo de Cuidado.

## Epic 5: Panel de Adherencia Histórica y Alerta de Patrón

Los Cuidadores con visibilidad de historial pueden ver la tendencia de cumplimiento de un Paciente en el tiempo, y reciben una Alerta de Patrón distinta de la alerta puntual cuando el incumplimiento se repite varios días — da al familiar a distancia la visibilidad que antes solo conseguía preguntando.

### Story 5.1: Ver el Panel de Adherencia Histórica por rango de fechas

As a Cuidador con Nivel de Compartición que incluya historial,
I want ver la tasa de cumplimiento de un Paciente en un rango de fechas (ej. últimos 7/30 días),
So that pueda detectar un problema de salud o de ánimo antes de que se agrave, sin tener que estar presente físicamente.

**Acceptance Criteria:**

**Given** un Paciente con historial de Confirmaciones de Toma
**When** abro el Panel de Adherencia Histórica y selecciono un rango de fechas
**Then** veo, como mínimo, % de dosis confirmadas a tiempo, % confirmadas tarde, y % no confirmadas para ese rango (FR-5)
**And** el panel usa la misma paleta de estado definida en `DESIGN.md`, sin colores adicionales (UX-DR9).

**Given** un Cuidador con Nivel de Compartición "Solo alertas" (sin acceso a historial)
**When** intenta acceder al Panel de Adherencia Histórica
**Then** no ve esta vista, consistente con el filtrado por Nivel de Compartición (NFR-6).

**Given** el AdherenceDashboard en la superficie web en una pantalla `≥lg`
**When** se carga el panel
**Then** se muestra en layout de dos columnas (lista de medicamentos + gráfico de adherencia lado a lado), colapsando a una columna en tablet/móvil web (UX-DR11).

### Story 5.2: Detectar y notificar una Alerta de Patrón tras días consecutivos de incumplimiento

As a Cuidador con visibilidad de adherencia histórica,
I want recibir una Alerta de Patrón cuando un Paciente acumula incumplimiento en varios días consecutivos,
So that pueda detectar un problema antes de que se agrave, no solo una omisión aislada.

**Acceptance Criteria:**

**Given** un Paciente con al menos una dosis no confirmada por N días consecutivos (umbral configurable, default `[ASSUMPTION: 3 días]`)
**When** se alcanza ese umbral
**Then** el sistema dispara una Alerta de Patrón a los Cuidadores con visibilidad de adherencia histórica (FR-6)
**And** esta Alerta de Patrón no reemplaza la Escalada de Notificaciones de la dosis individual (Epic 4) — ambas coexisten.

**Given** que el umbral de días consecutivos es un valor configurable
**When** se ejecuta la lógica de detección de patrón
**Then** el valor se lee de configuración (`PatternAlertPolicy`), nunca hardcodeado en el código.

### Story 5.3: Distinguir visualmente la Alerta de Patrón de la Alerta Puntual en el Centro de Alertas

As a Cuidador,
I want que la Alerta de Patrón se vea y se lea distinta de una alerta puntual de una sola dosis,
So that entienda inmediatamente si se trata de un problema recurrente o de un evento aislado.

**Acceptance Criteria:**

**Given** una Alerta de Patrón activa
**When** la veo en el Centro de Alertas
**Then** se distingue visualmente (color/copy) de una Alerta Puntual, con un mensaje que distingue explícitamente "esto pasó hoy" de "esto es un patrón" (UX-DR6, Voice and Tone)
**And** el copy usa un tono calmado, nunca alarmista, consistente con el resto de notificaciones de la app (UX-DR15).

## Epic 6: Testamento Digital de Cuidado

El Paciente puede designar anticipadamente a un Cuidador de Respaldo, y este puede solicitar explícitamente asumir el control de la cuenta si el Paciente pierde capacidad de decisión — completa la promesa de continuidad sin improvisación de UJ-3.

### Story 6.1: Designar Cuidador de Respaldo

As a Paciente,
I want designar a un Cuidador existente como mi Cuidador de Respaldo,
So that quede claro de antemano quién asumiría el control de mi cuenta si llego a perder capacidad de decisión.

**Acceptance Criteria:**

**Given** un Cuidador ya activo en mi Círculo de Cuidado
**When** lo designo como mi Cuidador de Respaldo desde "Cuidado avanzado"
**Then** queda registrado como mi único Cuidador de Respaldo activo (FR-13)
**And** la designación queda registrada en `audit_events` con timestamp y actor (NFR-5)
**And** la pantalla de designación se presenta en lenguaje claro, sin jerga legal (UX-DR21).

### Story 6.2: Cambiar de Cuidador de Respaldo

As a Paciente,
I want cambiar a mi Cuidador de Respaldo en cualquier momento mientras conservo capacidad de decisión,
So that mi designación anticipada siga reflejando a la persona en la que realmente confío.

**Acceptance Criteria:**

**Given** que ya tengo un Cuidador de Respaldo designado
**When** designo a otro Cuidador existente como mi nuevo Cuidador de Respaldo
**Then** el anterior deja de tener ese rol y solo el nuevo queda activo — nunca hay más de un Cuidador de Respaldo activo a la vez (FR-13)
**And** el cambio queda registrado en `audit_events` (NFR-5).

### Story 6.3: Solicitar y aprobar la Transferencia de Control de la cuenta

As a Cuidador de Respaldo,
I want solicitar explícitamente asumir el control de la cuenta del Paciente,
So that mi familia tenga un mecanismo claro de continuidad en lugar de tener que improvisar en una crisis, sin que ocurra de forma automática o silenciosa.

**Acceptance Criteria:**

**Given** que soy el Cuidador de Respaldo designado de un Paciente
**When** inicio una solicitud de Transferencia de Control
**Then** la transferencia NO ocurre automáticamente por inactividad del Paciente — requiere mi acción explícita como solicitante (FR-14)
**And** la solicitud queda en estado "pendiente" mostrando el chip correspondiente hasta que se apruebe (UX-DR24).

**Given** una solicitud de Transferencia de Control pendiente
**When** se evalúa la aprobación
**Then** `[ASSUMPTION]` se requiere confirmación explícita del Paciente (si conserva capacidad) o de un segundo Cuidador Principal — nunca se aprueba sola por el solo paso del tiempo; este mecanismo exacto queda pendiente de validación legal (PRD Open Question #3) antes de construirse en producción.

**Given** que la Transferencia de Control fue aprobada
**When** se completa
**Then** el Cuidador de Respaldo puede gestionar Cuidadores, Niveles de Compartición y Contacto de Emergencia en nombre del Paciente (FR-14)
**And** el evento de transferencia queda registrado de forma permanente y visible para todo el Círculo de Cuidado, incluso después de ocurrida (NFR-5).
