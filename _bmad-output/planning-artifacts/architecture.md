---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Juntos-2026-06-19/prd.md
  - _bmad-output/brainstorming/brainstorming-session-2026-06-18-23-49-31.md
workflowType: 'architecture'
project_name: 'Juntos'
user_name: 'SEBASTIANDAVIDCARABA'
date: '2026-06-19'
lastStep: 8
status: 'complete'
completedAt: '2026-06-21'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

El PRD define 14 FRs (FR-1 a FR-14) organizados en 7 features:

- **Calendario de Medicación Compartido** (FR-1, FR-2): CRUD de medicamentos/horarios con vista filtrada por rol.
- **Confirmación de Toma y Confirmación Cruzada** (FR-3, FR-4): registro de toma real + notificación en tiempo real a otros cuidadores.
- **Panel de Adherencia Histórica y Alerta de Patrón** (FR-5, FR-6): agregación de tendencia + detección de incumplimiento consecutivo.
- **Escalada de Notificaciones por Criticidad** (FR-7, FR-8): máquina de estados multicanal (push → SMS → llamada) con idempotencia.
- **Protocolo de Última Línea** (FR-9, FR-10): notificación a Contacto de Emergencia tras escalada agotada.
- **Gestión de Cuidadores** (FR-11, FR-12): niveles de compartición de datos + invitación/consentimiento explícito (máx. 5 cuidadores).
- **Testamento Digital de Cuidado** (FR-13, FR-14): designación y transferencia explícita de Cuidador de Respaldo.

Arquitectónicamente, el núcleo no es CRUD simple: es coordinación de estado compartido en tiempo real entre múltiples dispositivos/usuarios alrededor de un mismo Paciente.

**Non-Functional Requirements:**

- **Sincronización en tiempo real:** cambios de estado reflejados en segundos (no minutos) para todos los miembros conectados del Círculo de Cuidado.
- **Confiabilidad multicanal con degradación parcial:** la falla de un canal (ej. SMS) no debe detener la Cadena de Escalada completa.
- **Idempotencia explícita:** dos procesos detectando la misma dosis no confirmada no deben duplicar el paso de escalada.
- **Disponibilidad diferenciada:** el subsistema de Escalada/Última Línea requiere disponibilidad más alta que el resto de la app (objetivo numérico aún no definido — Open Question).
- **Auditabilidad inmutable:** toda acción sobre permisos, Contacto de Emergencia, Testamento Digital y cada paso de escalada queda registrada con timestamp y actor.
- **Privacidad por defecto ("mínimo dato necesario"):** el filtrado por Nivel de Compartición de Datos debe aplicarse de forma consistente en cada vista/consulta, no como excepción.
- **Cumplimiento regulatorio:** Ley 1581 de 2012 (Habeas Data, Colombia) como marco mínimo para datos de salud sensibles; sin alcance HIPAA/GDPR en esta fase.

**Scale & Complexity:**

- Primary domain: full-stack (app móvil iOS/Android + panel web complementario + backend con orquestación de estado y tiempo real)
- Complexity level: media-alta (rica en estado y reglas, pero acotada en volumen: un solo país piloto, máx. 5 cuidadores por paciente)
- Estimated architectural components: backend de dominio (medicación/adherencia), motor de sincronización en tiempo real, orquestador de escalada de notificaciones (stateful), capa de permisos/filtrado por rol, registro de auditoría, integraciones con proveedores externos de push/SMS/llamada, apps cliente (móvil + web)

### Technical Constraints & Dependencies

- Dependencia de proveedores externos de push, SMS y llamada automatizada — proveedor exacto aún no decidido (Open Question del PRD).
- Piloto exclusivo en Colombia; el marco regulatorio de datos de salud (Habeas Data) condiciona el diseño de almacenamiento y acceso a datos sensibles desde el día 1.
- No hay UX spec ni documento de arquitectura previo — este es el primer artefacto técnico formal del proyecto.
- Varios umbrales de negocio (tiempos de escalada por criticidad, umbral de Alerta de Patrón, mecanismo de aprobación de transferencia de control) están marcados como `[ASSUMPTION]` u Open Questions en el PRD — la arquitectura debe mantenerlos configurables, no hardcodeados.

### Cross-Cutting Concerns Identified

- **Sincronización en tiempo real multi-dispositivo:** afecta Calendario Compartido, Confirmación Cruzada y cambios de permisos por igual.
- **Orquestación de escalada con estado e idempotencia:** lógica central de negocio que debe sobrevivir reinicios/fallos parciales y no duplicar notificaciones.
- **Filtrado por Nivel de Compartición de Datos:** regla transversal aplicada en cada lectura (calendario, notificaciones, panel de adherencia), no una feature aislada.
- **Auditoría inmutable:** requerida en Gestión de Cuidadores, Testamento Digital y Cadena de Escalada — sugiere un mecanismo de logging de eventos compartido en lugar de implementaciones ad-hoc por feature.
- **Resiliencia ante proveedores externos:** push/SMS/llamada son puntos de falla externos que la arquitectura debe aislar para no comprometer la Cadena de Escalada completa.
- **Privacidad y cumplimiento por diseño:** Habeas Data colombiano condiciona decisiones de almacenamiento, acceso y retención de datos de salud desde el inicio, no como capa añadida después.

## Starter Template Evaluation

### Primary Technology Domain

Full-stack .NET (app móvil + panel web + backend con orquestación de estado y tiempo real), sobre **.NET 10** (versión LTS vigente).

### Technical Preferences Discovered

- **Mobile/Frontend:** .NET MAUI (preferencia explícita del usuario).
- **Backend:** .NET Core / ASP.NET Core (preferencia explícita del usuario).
- **Cloud/Deploy:** sin preferencia previa — se recomienda Azure por alineación nativa con el stack .NET (ver Rationale).

### Starter Options Considered

- **.NET Aspire Starter Application** (`dotnet new aspire-starter`) + proyecto .NET MAUI añadido a la solución — seleccionado.
- Alternativa descartada: solución .NET "a mano" (Web API + MAUI sin Aspire) — viable, pero exige reconstruir manualmente orquestación local, telemetría (OpenTelemetry/health checks) y service discovery que Aspire ya provee de fábrica; no aporta ninguna ventaja dado que el equipo ya trabaja 100% en .NET.

### Selected Starter: .NET Aspire Starter Application + .NET MAUI

**Rationale for Selection:**

El proyecto necesita coordinar 3 superficies (app móvil para Paciente/Cuidadores, panel web complementario, backend con orquestación de escalada y sincronización en tiempo real) bajo un único stack .NET. .NET Aspire es el patrón vigente de Microsoft para orquestar soluciones .NET multi-proyecto, y .NET MAUI 10 ya genera su propio proyecto de Aspire ServiceDefaults, por lo que se integra de forma nativa sin trabajo adicional de plomería.

**Initialization Command:**

```bash
dotnet new aspire-starter --name Juntos --output .
cd Juntos
dotnet new maui -o Juntos.Mobile -f net10.0
dotnet sln add Juntos.Mobile/Juntos.Mobile.csproj
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
C#/.NET 10 de punta a punta (backend, web, móvil) — un solo lenguaje en toda la solución.

**Styling Solution:**
Razor/CSS en Blazor (`Juntos.Web`); XAML en MAUI (`Juntos.Mobile`). Sin framework de estilos impuesto por el starter — pendiente de decidir en pasos posteriores si aplica.

**Build Tooling:**
MSBuild vía .NET SDK; `Juntos.AppHost` orquesta la ejecución/depuración conjunta de todos los proyectos en local.

**Testing Framework:**
Proyecto xUnit incluido por defecto, con referencia al `AppHost` para pruebas de integración end-to-end de la solución.

**Code Organization:**
Separación por proyecto: `AppHost` (orquestador), `ServiceDefaults` (telemetría/health checks compartidos), `ApiService` (lógica de dominio: medicación, escalada, adherencia, permisos), `Web` (Blazor — Panel de Adherencia Histórica y Gestión de Cuidadores), `Mobile` (MAUI — experiencia principal de Paciente/Cuidadores).

**Development Experience:**
Aspire Dashboard para observar logs/trazas de todos los servicios en una sola corrida local; hot reload en Blazor y MAUI; OpenTelemetry y health checks ya conectados vía `ServiceDefaults`, relevante para los requisitos de auditabilidad y disponibilidad diferenciada del PRD.

**Real-Time & Cloud Direction (a confirmar en decisiones posteriores):**
- **SignalR** sobre `ApiService` para Confirmación Cruzada y cambios de calendario en tiempo real; **Azure SignalR Service** en producción para escalar sin atarse a una sola instancia del backend.
- **Azure** como nube recomendada (sin preferencia previa del usuario): **Azure Container Apps** + `azd` como ruta de despliegue de primera clase para soluciones Aspire; **Azure Communication Services** para SMS/llamada automatizada; **Azure Notification Hubs** para push iOS/Android.

**Note:** La inicialización del proyecto con estos comandos debe ser la primera historia de implementación.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Base de datos: Azure Database for PostgreSQL (Flexible Server)
- Autenticación: ASP.NET Core Identity (self-hosted)
- Autorización: políticas basadas en recursos (Nivel de Compartición por relación Paciente-Cuidador)
- Patrón de API: REST/Minimal API (.NET 10) + SignalR para tiempo real
- Aislamiento de Escalada: `Juntos.EscalationWorker` como hosted service independiente

**Important Decisions (Shape Architecture):**
- Caching: Azure Cache for Redis desde el inicio
- Soporte offline: online-only para el MVP (con riesgo señalado)
- CI/CD: GitHub Actions + `azd`

**Deferred Decisions (Post-MVP):**
- Cifrado a nivel de columna para campos de salud ultra-sensibles — diferido post-piloto, evaluar según hallazgos de la consulta legal del PRD (§9 Compliance and Regulatory)
- Soporte multi-región — fuera de alcance, piloto es Colombia únicamente (§6.2 del PRD)

### Data Architecture

- **DB:** Azure Database for PostgreSQL Flexible Server, vía Npgsql + EF Core 10 (LTS, soportado hasta nov. 2028)
- **Modelado:** EF Core Code-First; entidades alineadas 1:1 con el Glosario del PRD (Paciente, Cuidador, CírculoDeCuidado, Medicamento, ConfirmaciónToma, PasoEscalada, ContactoEmergencia, TestamentoDigitalCuidado)
- **Validación:** validación nativa de Minimal APIs en .NET 10 para shape de request; reglas de negocio (umbrales de escalada, límite de 5 cuidadores) en la capa de dominio, no en el borde HTTP
- **Migraciones:** EF Core Migrations
- **Caching:** Azure Cache for Redis desde el MVP, para Calendario Compartido y Panel de Adherencia Histórica

### Authentication & Security

- **Autenticación:** ASP.NET Core Identity (self-hosted) como almacén de usuarios; emisión de tokens vía los endpoints nativos de Identity (`MapIdentityApi`) para que MAUI/Blazor consuman bearer tokens sin depender de un IdP externo
- **Autorización:** ASP.NET Core policy-based authorization con requirements/handlers personalizados que evalúan el Nivel de Compartición específico de cada par Paciente-Cuidador (no roles fijos globales) — modela fielmente FR-2/FR-11
- **Cifrado:** TLS en tránsito; cifrado en reposo nativo de Azure Database for PostgreSQL Flexible Server
- **Auditoría:** tabla de eventos inmutable (append-only) para cambios de permisos, Testamento Digital y cada paso de escalada — requisito transversal de §7 del PRD

**Implicación a vigilar:** al ser self-hosted, el equipo asume directamente la responsabilidad de MFA, recuperación de cuenta y flujos de invitación/consentimiento (FR-12) — no los provee un IdP externo de fábrica.

### API & Communication Patterns

- **Patrón:** REST vía Minimal API (.NET 10) en `ApiService`
- **Documentación:** OpenAPI nativo de .NET 10
- **Errores:** Problem Details (RFC 9457)
- **Rate limiting:** middleware nativo de ASP.NET Core
- **Tiempo real:** SignalR sobre `ApiService` para Confirmación Cruzada y cambios de calendario; Azure SignalR Service en producción
- **Escalada:** `Juntos.EscalationWorker` (Aspire hosted service independiente) consume eventos de dosis no confirmadas y ejecuta la Cadena de Escalada de forma aislada del tráfico del `ApiService` — satisface el NFR de disponibilidad diferenciada

### Frontend Architecture

- **Mobile (MAUI):** MVVM con `CommunityToolkit.Mvvm`; cliente SignalR para recibir Confirmación Cruzada en tiempo real
- **Web (Blazor):** estado de componente estándar de Blazor (sin librería de estado adicional, dado el alcance acotado del panel)
- **Conectividad:** **online-only para el MVP** — la app requiere conexión activa para programar/confirmar alarmas
  - ⚠️ **Riesgo señalado:** UJ-2 del PRD describe a Don Carlos sin conexión activa cuando suena la alarma en segundo plano; con online-only, una pérdida de conectividad en ese momento podría retrasar el registro de la Confirmación de Toma y disparar una escalada/falso positivo innecesario. El usuario aceptó este trade-off por simplicidad en el MVP; queda como candidato a revisar si el piloto muestra fricción real.

### Infrastructure & Deployment

- **Hosting:** Azure Container Apps, desplegado vía `azd` (ruta de despliegue de primera clase para soluciones .NET Aspire)
- **CI/CD:** GitHub Actions, integrado con `azd` para build/deploy de `AppHost`, `ApiService`, `EscalationWorker`, `Web` y `Mobile`
- **Observabilidad:** OpenTelemetry vía `ServiceDefaults` → Azure Monitor / Application Insights
- **Escalado:** `ApiService` y `EscalationWorker` escalan de forma independiente en Container Apps, permitiendo aislar la disponibilidad del subsistema crítico de escalada

### Decision Impact Analysis

**Implementation Sequence:**
1. Inicialización de la solución (comando del starter, Paso 3)
2. Modelo de datos + EF Core Migrations sobre PostgreSQL
3. ASP.NET Core Identity + políticas de autorización por Nivel de Compartición
4. `ApiService` (Calendario, Confirmación de Toma) + SignalR
5. `EscalationWorker` aislado (Cadena de Escalada + Protocolo de Última Línea)
6. Clientes (`Mobile` MAUI, `Web` Blazor)
7. Pipeline CI/CD (GitHub Actions + `azd`) y despliegue a Azure Container Apps

**Cross-Component Dependencies:**
El modelo de permisos (Nivel de Compartición) atraviesa Calendario, Notificaciones y Panel de Adherencia — debe definirse antes de construir cualquier vista de lectura filtrada.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 6 áreas (idioma/glosario de código, naming de BD, naming de API, formatos JSON/errores, eventos en tiempo real/auditoría, organización de proyecto)

### Glosario de Traducción PRD → Código (fijo, no debe variar)

| Término PRD (español) | Identificador en código (inglés) |
|---|---|
| Paciente | `Patient` |
| Cuidador | `Caregiver` |
| Cuidador Principal | `PrimaryCaregiver` (rol, no clase separada) |
| Cuidador de Respaldo | `BackupCaregiver` (rol) |
| Círculo de Cuidado | `CareCircle` |
| Calendario de Medicación Compartido | `MedicationCalendar` |
| Confirmación de Toma | `DoseConfirmation` |
| Confirmación Cruzada | `CrossConfirmation` (evento, no entidad) |
| Medicamento Crítico | flag `Medication.IsCritical` |
| Escalada de Notificaciones | `NotificationEscalation` |
| Protocolo de Última Línea | `LastLineProtocol` |
| Contacto de Emergencia | `EmergencyContact` |
| Alerta de Patrón | `PatternAlert` |
| Panel de Adherencia Histórica | `AdherenceHistory` |
| Nivel de Compartición de Datos | `DataSharingLevel` |
| Testamento Digital de Cuidado | `DigitalCareDirective` |
| Invitación y Consentimiento | `CaregiverInvitation` |

**Regla:** ningún agente debe inventar una traducción distinta para estos términos; si aparece un concepto nuevo del PRD no listado aquí, debe añadirse a esta tabla antes de usarse en código.

### Naming Patterns

**Database Naming Conventions (PostgreSQL vía EF Core):**
- Tablas y columnas en `snake_case` (convención nativa de Postgres) generadas automáticamente desde las clases C# en PascalCase usando el paquete `EFCore.NamingConventions` — los agentes no deben nombrar tablas/columnas a mano.
- Claves foráneas: `{entidad_singular}_id` (ej. `patient_id`)
- Índices: `ix_{tabla}_{columna(s)}`

**API Naming Conventions (Minimal API, REST):**
- Rutas: recursos en plural, kebab-case (ej. `/api/care-circles/{careCircleId}/caregivers`)
- Parámetros de ruta: `{nombreCamelCase}` (convención de ASP.NET Core)
- Query params: camelCase (ej. `?fromDate=...&toDate=...`)

**Code Naming Conventions (C#):**
- Clases/métodos/propiedades públicas: PascalCase
- Parámetros/variables locales: camelCase
- Campos privados: `_camelCase`
- Nombre de archivo = nombre del tipo público que contiene (1 tipo público por archivo)

### Structure Patterns

**Project Organization:**
Dentro de `ApiService` y `EscalationWorker`, organización por feature (vertical slice), no por capa técnica — cada carpeta mapea 1:1 a una sección §4 del PRD: `MedicationCalendar/`, `DoseConfirmation/`, `AdherenceHistory/`, `NotificationEscalation/`, `LastLineProtocol/`, `CaregiverManagement/`, `DigitalCareDirective/`. Esto evita que un agente disperse el código de un FR en capas separadas y que otro lo concentre por feature.

**Arquitectura Hexagonal (Ports & Adapters) + DDD dentro de cada feature:**
Cada carpeta de feature se subdivide internamente en 3 capas:
- `Domain/` — entidades/agregados, value objects, eventos de dominio. **Sin ninguna dependencia de EF Core, ASP.NET o Azure SDKs.**
- `Application/` — casos de uso (comandos/queries) + **puertos** (interfaces) que el dominio necesita del exterior (ej. `IMedicationRepository`, `ICrossConfirmationNotifier`).
- `Infrastructure/` — **adaptadores** que implementan esos puertos (repositorios EF Core, publishers SignalR, clientes de Azure Communication Services).
- El `*Endpoints.cs` (o Hub de SignalR) en la raíz de la feature es el adaptador "driving" (HTTP/WebSocket → casos de uso de `Application`).

**Regla de dependencia (Dependency Rule):** `Domain` no depende de nada; `Application` depende solo de `Domain` (a través de puertos); `Infrastructure` y `Endpoints` dependen de `Application`/`Domain`, nunca al revés. Ningún agente debe inyectar `DbContext` ni un SDK de Azure directamente en `Domain` o `Application`.

**Agregados DDD (Ubiquitous Language = Glosario del PRD):**
- `Medication` (+ `MedicationSchedule`) — agregado raíz de §4.1
- `DoseConfirmation` — agregado raíz de §4.2; publica el evento de dominio `DoseConfirmed`
- `AdherenceHistory` — **Bounded Context de solo lectura** (read model/proyección), sin agregado transaccional propio; se alimenta de `DoseConfirmed` (mismo proceso) y de `EscalationStepExecuted` (proceso distinto, `EscalationWorker`)
- `CareCircle` (+ `Caregiver`, `DataSharingLevel`, `CaregiverInvitation`) — agregado raíz de §4.6
- `DigitalCareDirective` — agregado raíz de §4.7
- `EscalationChain` (+ `EscalationStep`) — agregado raíz de §4.4/§4.5, en `EscalationWorker`

**Propagación de eventos de dominio:** dentro de `ApiService`, los eventos (ej. `DoseConfirmed`) se despachan **en proceso** vía un despachador simple definido en `SharedKernel/` — no se introduce un message broker, dado el volumen acotado del piloto (máx. 5 cuidadores/paciente). El `AdherenceHistory.Application.DoseConfirmedProjector` se suscribe a ese despachador para actualizar su propia proyección. Los eventos que origina `EscalationWorker` (otro proceso) llegan a `AdherenceHistory` únicamente a través de la tabla compartida `audit_events` — nunca por llamada directa entre procesos, consistente con el límite ya establecido entre `ApiService` y `EscalationWorker`.

**File Structure Patterns:**
Proyecto xUnit con la misma estructura de carpetas que el código que prueba, incluyendo el desglose `Domain/`/`Application/`/`Infrastructure/`; sufijo `Tests` (ej. `DoseConfirmationServiceTests.cs`).

### Format Patterns

**API Response Formats:**
- Respuesta exitosa: recurso directo, sin envoltura `{data: ...}` (convención REST estándar de ASP.NET Core).
- Errores: Problem Details (RFC 9457) con `type` URI propio por error de dominio (ej. `https://juntos.app/errors/care-circle-limit-reached` para el límite de 5 cuidadores de FR-12).

**Data Exchange Formats:**
- JSON: camelCase (comportamiento por defecto de `System.Text.Json` en ASP.NET Core) — no se sobreescribe.
- Fechas/horas: ISO 8601 en UTC siempre (relevante porque FR-3 distingue hora programada vs. hora real de confirmación — ambas deben viajar en UTC sin ambigüedad de zona horaria).

### Communication Patterns

**Event System Patterns:**
- Eventos SignalR: PascalCase, en tiempo pasado, ya que representan hechos de dominio ocurridos (ej. `DoseConfirmed`, `EscalationStepExecuted`, `LastLineProtocolTriggered`) — mismo nombre se usa en el hub y en el registro de auditoría inmutable.
- Registro de auditoría: cada evento se persiste con `(timestamp UTC, actorId, eventType, payload)` — estructura única reutilizada por Gestión de Cuidadores, Testamento Digital y Cadena de Escalada (no implementaciones ad-hoc por feature).

**State Management Patterns:**
- Logging: `ILogger` estructurado vía `ServiceDefaults`; `Information` para eventos de negocio, `Warning` para fallo de un canal individual de escalada (FR-8, no debe detener la cadena), `Error` solo para fallos no recuperables.

### Process Patterns

**Error Handling Patterns:**
- Todo error de API se expresa como Problem Details, nunca un formato custom.
- Idempotencia de escalada (FR-8): cada paso de la Cadena de Escalada se identifica por una clave idempotente `(doseId, stepIndex)` — el `EscalationWorker` debe verificar esta clave antes de ejecutar un paso, nunca asumir que es la única instancia corriendo.

**Loading State Patterns:**
- MAUI (MVVM): todo ViewModel expone `IsBusy: bool` con el mismo nombre para estado de carga; manejo de errores de red muestra mensaje user-facing distinto del log técnico.
- Blazor: mismo patrón, campo `isLoading` en cada componente con llamada async.

### Enforcement Guidelines

**All AI Agents MUST:**
- Usar la tabla de traducción Glosario→Código sin inventar sinónimos
- Seguir la organización por feature (vertical slice), no por capa técnica
- Usar Problem Details para todo error de API, nunca un formato de error custom
- Persistir cualquier acción auditable con la estructura `(timestamp UTC, actorId, eventType, payload)`

**Pattern Enforcement:**
- Cualquier término de dominio nuevo debe añadirse a la tabla de traducción antes de usarse en código.
- Desviaciones de estos patrones se documentan como ADR (Architecture Decision Record) dentro de este mismo documento, no como excepción silenciosa.

### Pattern Examples

**Good Examples:**
- Endpoint: `POST /api/care-circles/{careCircleId}/caregivers` devolviendo `201 Created` con el recurso `Caregiver` directo.
- Evento: `DoseConfirmed { DoseId, ConfirmedAtUtc, ConfirmedByCaregiverId }` publicado vía SignalR y persistido en auditoría con la misma forma.

**Anti-Patterns:**
- Nombrar la misma entidad `Cuidador` en un endpoint y `Caregiver` en otro.
- Envolver una respuesta exitosa en `{ success: true, data: {...} }` en lugar del recurso directo.
- Ejecutar un paso de escalada sin verificar la clave idempotente `(doseId, stepIndex)`.
- Inyectar `JuntosDbContext` directamente en una clase de `Domain/` o `Application/` (viola la regla de dependencia hexagonal).
- Que `AdherenceHistory` consulte directamente el agregado `DoseConfirmation` en vez de leer su propia proyección actualizada por evento.

## Project Structure & Boundaries

### Complete Project Directory Structure

```
Juntos/
├── README.md
├── Juntos.sln
├── .gitignore
├── .editorconfig
├── azure.yaml                              # config de azd para despliegue
├── .github/
│   └── workflows/
│       └── ci-cd.yml                       # build, test, azd deploy
├── Juntos.AppHost/
│   ├── Juntos.AppHost.csproj
│   ├── AppHost.cs                          # orquesta ApiService, EscalationWorker, Web, Postgres, Redis
│   └── appsettings.json
├── Juntos.ServiceDefaults/
│   ├── Juntos.ServiceDefaults.csproj
│   └── Extensions.cs                       # OpenTelemetry, health checks, service discovery
├── Juntos.ApiService/
│   ├── Juntos.ApiService.csproj
│   ├── Program.cs
│   ├── appsettings.json / appsettings.Development.json
│   ├── Data/
│   │   ├── JuntosDbContext.cs
│   │   └── Migrations/
│   ├── SharedKernel/                        # primitivas DDD compartidas entre features
│   │   ├── AggregateRoot.cs
│   │   ├── IDomainEvent.cs
│   │   └── InProcessDomainEventDispatcher.cs
│   ├── Identity/                           # ASP.NET Core Identity, MapIdentityApi
│   │   ├── ApplicationUser.cs
│   │   └── IdentityEndpoints.cs
│   ├── Authorization/                      # políticas resource-based de DataSharingLevel
│   │   ├── DataSharingRequirement.cs
│   │   └── DataSharingHandler.cs
│   ├── MedicationCalendar/                 # FR-1, FR-2 — agregado raíz: Medication
│   │   ├── Domain/
│   │   │   ├── Medication.cs
│   │   │   ├── MedicationSchedule.cs       # value object
│   │   │   └── MedicationCriticalityChanged.cs  # evento de dominio
│   │   ├── Application/
│   │   │   ├── IMedicationRepository.cs    # puerto
│   │   │   ├── CreateMedicationCommand.cs
│   │   │   ├── UpdateMedicationScheduleCommand.cs
│   │   │   └── GetMedicationCalendarQuery.cs
│   │   ├── Infrastructure/
│   │   │   └── EfMedicationRepository.cs   # adaptador del puerto
│   │   └── MedicationCalendarEndpoints.cs  # adaptador driving (HTTP)
│   ├── DoseConfirmation/                   # FR-3, FR-4 — agregado raíz: DoseConfirmation
│   │   ├── Domain/
│   │   │   ├── DoseConfirmation.cs
│   │   │   └── DoseConfirmed.cs            # evento de dominio
│   │   ├── Application/
│   │   │   ├── IDoseConfirmationRepository.cs
│   │   │   ├── ICrossConfirmationNotifier.cs  # puerto hacia SignalR
│   │   │   └── ConfirmDoseCommand.cs
│   │   ├── Infrastructure/
│   │   │   ├── EfDoseConfirmationRepository.cs
│   │   │   └── SignalRCrossConfirmationNotifier.cs  # adaptador del puerto
│   │   ├── CrossConfirmationHub.cs         # SignalR hub (driving adapter)
│   │   └── DoseConfirmationEndpoints.cs
│   ├── AdherenceHistory/                   # FR-5, FR-6 — Bounded Context de solo lectura (read model)
│   │   ├── Domain/
│   │   │   ├── AdherenceSnapshot.cs        # modelo de proyección, no aggregate transaccional
│   │   │   └── PatternAlertPolicy.cs       # lógica de detección de patrón sobre la proyección
│   │   ├── Application/
│   │   │   ├── IAdherenceProjectionRepository.cs  # puerto de lectura
│   │   │   ├── GetAdherenceHistoryQuery.cs
│   │   │   └── DoseConfirmedProjector.cs   # suscriptor de DoseConfirmed (in-process) y de EscalationStepExecuted (vía audit_events)
│   │   ├── Infrastructure/
│   │   │   └── EfAdherenceProjectionRepository.cs
│   │   └── AdherenceHistoryEndpoints.cs
│   ├── CaregiverManagement/                # FR-11, FR-12 — agregado raíz: CareCircle
│   │   ├── Domain/
│   │   │   ├── CareCircle.cs
│   │   │   ├── Caregiver.cs
│   │   │   ├── DataSharingLevel.cs
│   │   │   └── CaregiverInvitation.cs
│   │   ├── Application/
│   │   │   ├── ICareCircleRepository.cs
│   │   │   ├── InviteCaregiverCommand.cs
│   │   │   └── ChangeDataSharingLevelCommand.cs
│   │   ├── Infrastructure/
│   │   │   └── EfCareCircleRepository.cs
│   │   └── CaregiverManagementEndpoints.cs
│   ├── DigitalCareDirective/                # FR-13, FR-14 — agregado raíz propio
│   │   ├── Domain/
│   │   │   ├── DigitalCareDirective.cs
│   │   │   └── ControlTransferred.cs       # evento de dominio
│   │   ├── Application/
│   │   │   ├── IDigitalCareDirectiveRepository.cs
│   │   │   └── RequestControlTransferCommand.cs
│   │   ├── Infrastructure/
│   │   │   └── EfDigitalCareDirectiveRepository.cs
│   │   └── DigitalCareDirectiveEndpoints.cs
│   ├── Audit/                               # log de eventos inmutable, transversal
│   │   ├── AuditEvent.cs
│   │   └── AuditLogger.cs
│   └── Notifications/
│       └── NotificationEvents.cs            # contratos compartidos con EscalationWorker
├── Juntos.EscalationWorker/
│   ├── Juntos.EscalationWorker.csproj
│   ├── Program.cs
│   ├── appsettings.json
│   ├── NotificationEscalation/              # FR-7, FR-8 — agregado raíz: EscalationChain
│   │   ├── Domain/
│   │   │   ├── EscalationChain.cs
│   │   │   ├── EscalationStep.cs
│   │   │   └── EscalationStepExecuted.cs    # evento de dominio, leído por audit_events
│   │   ├── Application/
│   │   │   ├── IEscalationStateRepository.cs
│   │   │   ├── INotificationChannel.cs      # puerto, implementado por cada canal
│   │   │   └── ProcessEscalationStepCommand.cs
│   │   └── Infrastructure/
│   │       ├── EfEscalationStateRepository.cs
│   │       └── IdempotencyStore.cs          # clave (doseId, stepIndex)
│   ├── LastLineProtocol/                    # FR-9, FR-10
│   │   ├── Domain/
│   │   │   └── EmergencyContact.cs
│   │   ├── Application/
│   │   │   └── TriggerLastLineProtocolCommand.cs
│   │   └── Infrastructure/
│   │       └── EfEmergencyContactRepository.cs
│   └── Channels/                            # adaptadores de INotificationChannel
│       ├── PushChannel.cs                   # Azure Notification Hubs
│       ├── SmsChannel.cs                    # Azure Communication Services
│       └── VoiceCallChannel.cs              # Azure Communication Services
├── Juntos.Web/                             # Blazor Web App — panel complementario
│   ├── Juntos.Web.csproj
│   ├── Program.cs
│   ├── Components/
│   │   ├── Pages/
│   │   │   ├── AdherenceDashboard.razor     # FR-5, FR-6
│   │   │   └── CaregiverManagement.razor    # FR-11, FR-12
│   │   └── Layout/
│   └── wwwroot/
├── Juntos.Mobile/                          # .NET MAUI — Paciente/Cuidadores
│   ├── Juntos.Mobile.csproj
│   ├── MauiProgram.cs
│   ├── Views/
│   │   ├── MedicationCalendarPage.xaml      # FR-1, FR-2
│   │   ├── DoseConfirmationPage.xaml        # FR-3, FR-4
│   │   ├── AdherenceHistoryPage.xaml        # FR-5, FR-6
│   │   ├── CaregiverManagementPage.xaml     # FR-11, FR-12
│   │   └── DigitalCareDirectivePage.xaml    # FR-13, FR-14
│   ├── ViewModels/                          # 1:1 con cada Page, sufijo ViewModel
│   └── Platforms/
│       ├── Android/
│       └── iOS/
└── Juntos.Tests/
    ├── Juntos.Tests.csproj
    ├── MedicationCalendar/
    ├── DoseConfirmation/
    ├── AdherenceHistory/
    ├── NotificationEscalation/
    ├── LastLineProtocol/
    ├── CaregiverManagement/
    ├── DigitalCareDirective/
    └── Integration/                         # vía DistributedApplicationTestingBuilder contra AppHost
```

### Architectural Boundaries

**API Boundaries:**
- `Juntos.ApiService` expone únicamente endpoints síncronos (CRUD, consultas) + el hub SignalR `CrossConfirmationHub`. No conoce los proveedores externos de SMS/llamada — solo publica eventos.
- `Juntos.EscalationWorker` es el único componente que habla con Azure Communication Services / Notification Hubs. `ApiService` y `EscalationWorker` se comunican exclusivamente por la tabla de auditoría/eventos en PostgreSQL (o una cola interna), nunca por llamada HTTP directa entre sí — así uno puede caer sin tumbar al otro.

**Component Boundaries:**
- `Juntos.Mobile` y `Juntos.Web` solo conocen `Juntos.ApiService` (REST + SignalR); nunca llaman directamente a `EscalationWorker` ni a proveedores externos.
- Cada carpeta de feature en `ApiService`/`EscalationWorker` expone su propio `*Endpoints.cs` — ningún feature debe importar tipos internos de otro feature; lo compartido vive en `Audit/`, `Notifications/` o `SharedKernel/`.
- **Regla de dependencia hexagonal (dentro de cada feature):** `Domain` no depende de nada; `Application` depende solo de `Domain` (vía puertos); `Infrastructure` y `*Endpoints.cs` dependen de `Application`/`Domain`, nunca al revés. Ningún tipo de `Domain`/`Application` puede referenciar `JuntosDbContext`, SignalR ni un SDK de Azure directamente.
- `AdherenceHistory` es un Bounded Context de solo lectura: no posee agregado transaccional propio y nunca consulta directamente el agregado `DoseConfirmation` — se actualiza exclusivamente por eventos (`DoseConfirmed` en proceso vía `SharedKernel`, `EscalationStepExecuted` entre procesos vía `audit_events`).

**Data Boundaries:**
- Único `JuntosDbContext` en `ApiService`, con todas las tablas (incluida `audit_events`). `EscalationWorker` lee/escribe a la misma base vía su propio `DbContext` ligero (solo las tablas que necesita: dosis, pasos de escalada, idempotencia) — no comparte código de dominio con `ApiService`, solo el esquema.
- Azure Cache for Redis es exclusivo de `ApiService` para las vistas de lectura (`MedicationCalendar`, `AdherenceHistory`); `EscalationWorker` no cachea nada (debe leer siempre el estado más reciente para evitar duplicar pasos).

### Requirements to Structure Mapping

| Feature del PRD | Carpeta(s) |
|---|---|
| §4.1 Calendario Compartido (FR-1, FR-2) | `ApiService/MedicationCalendar/`, `Mobile/Views/MedicationCalendarPage.xaml` |
| §4.2 Confirmación de Toma/Cruzada (FR-3, FR-4) | `ApiService/DoseConfirmation/`, `Mobile/Views/DoseConfirmationPage.xaml` |
| §4.3 Adherencia/Alerta de Patrón (FR-5, FR-6) | `ApiService/AdherenceHistory/`, `Web/Components/Pages/AdherenceDashboard.razor` |
| §4.4 Escalada por Criticidad (FR-7, FR-8) | `EscalationWorker/NotificationEscalation/` |
| §4.5 Protocolo de Última Línea (FR-9, FR-10) | `EscalationWorker/LastLineProtocol/` |
| §4.6 Gestión de Cuidadores (FR-11, FR-12) | `ApiService/CaregiverManagement/`, `Web/Components/Pages/CaregiverManagement.razor` |
| §4.7 Testamento Digital (FR-13, FR-14) | `ApiService/DigitalCareDirective/` |

**Cross-Cutting Concerns:**
- Autenticación/Autorización → `ApiService/Identity/`, `ApiService/Authorization/`
- Auditoría inmutable (§7) → `ApiService/Audit/`, consumida por todas las features anteriores

### Integration Points

**Internal Communication:** REST + SignalR entre clientes y `ApiService`; `ApiService` ↔ `EscalationWorker` solo vía estado compartido en PostgreSQL (tabla de dosis/eventos), nunca llamada directa.

**External Integrations:** Azure Communication Services (SMS, llamada) y Azure Notification Hubs (push) — aislados en `EscalationWorker/Channels/`.

**Data Flow:** Mobile/Web → `ApiService` (REST) → PostgreSQL + evento de auditoría → SignalR notifica a otros clientes en tiempo real. Dosis no confirmada → `EscalationWorker` la detecta por polling/consulta periódica → ejecuta cadena → publica resultado en auditoría → `ApiService` lo refleja vía SignalR.

### File Organization Patterns

**Configuration:** un `appsettings.json` por proyecto ejecutable (`ApiService`, `EscalationWorker`, `Web`), gestionados centralmente por `AppHost` en desarrollo local; en producción, configuración vía Azure App Configuration/Key Vault.

**Tests:** `Juntos.Tests` espeja la estructura de `ApiService`/`EscalationWorker` por feature; `Integration/` usa `DistributedApplicationTestingBuilder` de Aspire para levantar la solución completa en pruebas.

### Development Workflow Integration

**Development Server Structure:** `dotnet run --project Juntos.AppHost` levanta todo (API, Worker, Web, Postgres, Redis) con el Aspire Dashboard para ver logs/trazas de todos a la vez.

**Build Process Structure:** MSBuild estándar de .NET sobre toda la solución (`Juntos.sln`).

**Deployment Structure:** GitHub Actions ejecuta `azd up`/`azd deploy` hacia Azure Container Apps, desplegando cada proyecto ejecutable como un contenedor independiente, permitiendo escalar `EscalationWorker` por separado del resto.

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:** Todas las versiones verificadas son compatibles entre sí — .NET 10 (LTS hasta nov. 2028), EF Core 10, `EFCore.NamingConventions` 10.0.1, .NET Aspire 13, .NET MAUI 10 y ASP.NET Core 10 forman parte de la misma familia de release. La incorporación de Arquitectura Hexagonal + DDD (Domain/Application/Infrastructure por feature) no introduce nueva tecnología — es una reorganización interna que no contradice ninguna decisión previa.

**Pattern Consistency:** La regla de dependencia hexagonal (`Domain` no depende de nada; `Application` solo de `Domain`; `Infrastructure`/`Endpoints` dependen de ambos) es consistente con el resto de patrones (naming, vertical-slice por feature, eventos en pasado). REST/SignalR/EF Core/Azure quedan confinados a `Infrastructure`/`Endpoints`, nunca en `Domain`/`Application`.

**Structure Alignment:** `AdherenceHistory` como Bounded Context de solo lectura es coherente con la decisión ya tomada en el Paso 4 de que `EscalationWorker` y `ApiService` solo se comunican vía la tabla compartida `audit_events` — ese mismo canal ahora también alimenta la proyección de adherencia, sin abrir un canal nuevo.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:** Las 14 FRs (FR-1 a FR-14) siguen mapeadas 1:1 a carpetas de feature; el refinamiento Domain/Application/Infrastructure es interno a cada carpeta y no cambia esa cobertura.

**Non-Functional Requirements Coverage:**
- Sincronización en tiempo real → SignalR + Redis, con `ICrossConfirmationNotifier` como puerto que aísla el dominio del mecanismo de transporte ✅
- Auditabilidad inmutable → reforzada: los eventos de dominio (`DoseConfirmed`, `EscalationStepExecuted`, `ControlTransferred`) son ciudadanos de primera clase del modelo, no solo entradas de log ✅
- Idempotencia (FR-8) → `IdempotencyStore` en `Infrastructure` de `NotificationEscalation`, detrás del puerto `IEscalationStateRepository` ✅
- Habeas Data / mínimo dato necesario → autorización resource-based por `DataSharingLevel`, modelada como parte del agregado `CareCircle` ✅

### Implementation Readiness Validation ✅

Se agregaron ejemplos concretos por feature (entidades, puertos, adaptadores) suficientes para que un agente de IA replique el patrón Domain/Application/Infrastructure en cualquier feature nueva sin ambigüedad, incluyendo el caso especial de `AdherenceHistory` (read model sin agregado transaccional).

### Gap Analysis Results

**Critical Gaps:** Ninguno.

**Important Gaps (no bloquean, pero requieren atención pronto):**
- Los umbrales exactos de la Cadena de Escalada (Open Question #1 del PRD) y el umbral de Alerta de Patrón (#2) quedan como configuración de `EscalationStep`/`PatternAlertPolicy`, pero el valor de negocio falta validarse con el piloto.
- El mecanismo de aprobación de Transferencia de Control del Testamento Digital (Open Question #3, FR-14) ya tiene hogar explícito (`DigitalCareDirective.Application.RequestControlTransferCommand`), pero su lógica de verificación/aprobación exacta sigue sin diseñarse — recomendado resolverlo antes de implementar esa feature específica.
- No existe aún un spec de UX — el reparto exacto de funciones entre `Mobile` y `Web` (Open Question #6) sigue siendo una asunción inicial de este documento.
- No existen épicas/historias formales — se recomienda ejecutar el flujo de creación de épicas para descomponer esta arquitectura en trabajo implementable.

**Nice-to-Have Gaps:**
- Selección final de proveedor de SMS/llamada (Open Question #4) — aislada en `Channels/` detrás del puerto `INotificationChannel`, bajo riesgo si cambia después.
- Lenguaje exacto de disclaimer legal (Open Question #5) — tarea de producto/legal, no arquitectónica.

### Validation Issues Addressed

La incorporación de Arquitectura Hexagonal + DDD (solicitada explícitamente por el usuario) se aplicó sin reabrir ninguna decisión crítica del Paso 4: se mantiene .NET 10/Aspire/PostgreSQL/Redis/ASP.NET Core Identity/REST+SignalR/EscalationWorker aislado. El único ajuste de alcance fue separar `AdherenceHistory` como Bounded Context de solo lectura en vez de un agregado transaccional, decisión tomada explícitamente por el usuario.

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION (los 16 puntos están `[x]`, sin Critical Gaps abiertos)

**Confidence Level:** High

**Key Strengths:**
- Cobertura 1:1 verificable entre cada FR del PRD y un componente físico concreto
- Separación estricta Domain/Application/Infrastructure verificable por una regla de dependencia explícita, no solo por convención implícita
- Aislamiento explícito del subsistema crítico de seguridad (Escalada/Última Línea) acorde al NFR de disponibilidad diferenciada
- Bounded Context de lectura (`AdherenceHistory`) desacoplado del agregado de escritura, evitando un acoplamiento que habría sido fácil de introducir por error
- Glosario de traducción PRD↔código (lenguaje ubicuo DDD) fijado, reduciendo ambigüedad entre agentes de IA
- Todas las versiones tecnológicas verificadas activamente (no asumidas de memoria)

**Areas for Future Enhancement:**
- Definir spec de UX para confirmar reparto Mobile/Web y detalle de pantallas
- Generar épicas/historias para convertir esta arquitectura en plan de implementación
- Resolver Open Questions del PRD (umbrales de escalada, mecanismo de transferencia de control) antes de construir esas features específicas

### Implementation Handoff

**AI Agent Guidelines:** Seguir las decisiones arquitectónicas exactamente como están documentadas; respetar la regla de dependencia hexagonal en cada feature; usar los patrones de implementación de forma consistente; respetar la estructura y los límites de proyecto definidos; consultar este documento ante cualquier duda arquitectónica.

**First Implementation Priority:**
```bash
dotnet new aspire-starter --name Juntos --output .
cd Juntos
dotnet new maui -o Juntos.Mobile -f net10.0
dotnet sln add Juntos.Mobile/Juntos.Mobile.csproj
```
