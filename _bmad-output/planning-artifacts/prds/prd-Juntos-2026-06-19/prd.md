---
title: Juntos (App de Alarmas de Medicación)
status: draft
created: 2026-06-19
updated: 2026-06-21
---

# PRD: Juntos

## 0. Document Purpose

Este PRD define el MVP de una app de alarmas de medicación para familias y cuidadores que comparten el seguimiento de un mismo paciente. Está dirigido al equipo de producto/desarrollo que construirá el piloto y a cualquier stakeholder que necesite entender el alcance antes de pasar a UX y arquitectura. El documento agrupa funcionalidades por feature, anida los requerimientos funcionales (FR) con IDs globales estables, usa un Glosario cuyos términos se reutilizan literalmente en todo el texto, y marca inline con `[ASSUMPTION]` cada inferencia que el usuario aún no ha confirmado explícitamente. Este PRD nace de una sesión de brainstorming previa (`_bmad-output/brainstorming/brainstorming-session-2026-06-18-23-49-31.md`); no la duplica, sino que organiza y formaliza sus 20 ideas en requerimientos verificables. No existen aún documentos de UX o arquitectura — este PRD es el primer artefacto formal del producto.

## 1. Vision

Cuando una familia cuida a un paciente que toma medicamentos regularmente, el problema real no es "olvidar poner una alarma" — es que **varias personas distintas necesitan saber, en tiempo real y sin tener que preguntarse entre sí, si la toma ocurrió**. Hoy esa coordinación se hace por grupos de WhatsApp, llamadas y memoria, y se cae exactamente cuando más importa: cuando el paciente no responde y nadie sabe si ya tomó el medicamento, si simplemente se le olvidó revisar el teléfono, o si necesita ayuda urgente.

Esta app resuelve esa coordinación. Un calendario de medicación único y compartido reemplaza al grupo de WhatsApp. Cada toma confirmada se refleja en segundos para todos los cuidadores del círculo de cuidado. Cuando el paciente no confirma, la app escala de forma proporcional — desde un recordatorio suave hasta, en el peor caso, un contacto de emergencia — en lugar de depender de que alguien note el silencio.

Lo que diferencia a esta app de un simple recordatorio es que resuelve la tensión entre **vigilancia útil** y **autonomía del paciente**: el paciente decide quién entra a su red de cuidado, qué ve cada cuidador, y puede dejar instrucciones anticipadas (su "testamento digital de cuidado") sobre quién toma el control si llega a perder capacidad de decisión. La app no vigila al paciente; le da a su círculo de cuidado la visibilidad que antes solo conseguían preguntando, y una red de seguridad real cuando el silencio se vuelve preocupante.

## 2. Target User

### 2.1 Jobs To Be Done

- **Como cuidador principal**, quiero saber sin preguntar si mi familiar tomó su medicamento hoy, para no tener que llamarlo o visitarlo solo para confirmarlo.
- **Como cuidador principal**, quiero que la app me avise con tiempo suficiente para reaccionar si un medicamento crítico no se tomó, no después de que ya sea tarde.
- **Como familiar a distancia**, quiero ver si hay un patrón de incumplimiento (no solo el día de hoy), para detectar un problema de salud o de ánimo antes de que se agrave.
- **Como paciente**, quiero mantener control sobre quién ve mi información de salud y qué tan detallada es, sin sentir que estoy bajo vigilancia constante.
- **Como paciente**, quiero dejar instrucciones claras de antemano sobre quién puede tomar decisiones por mí si llego a perder la capacidad de hacerlo, en lugar de que mi familia tenga que improvisar en un momento de crisis.
- **Como cualquier miembro del círculo de cuidado**, quiero un único lugar con el horario de medicación, no una mezcla de mensajes de WhatsApp, notas de papel y memoria.

### 2.2 Non-Users (v1)

- **Clínicas y cuidadores profesionales con múltiples pacientes.** Esta ronda se enfoca exclusivamente en el caso familiar/doméstico (un círculo de cuidado alrededor de un paciente). El caso profesional/clínico fue explícitamente descartado durante el brainstorming y queda fuera de este PRD.
- **Pacientes o familias sin ningún cuidador adicional.** El valor central del producto es la coordinación entre múltiples personas; un uso puramente individual (una persona gestionando solo su propia medicación, sin nadie más viendo el calendario) no es el caso de uso principal del MVP, aunque la app no lo bloquea técnicamente. `[ASSUMPTION: la app permite un único usuario sin cuidadores adicionales, pero no se optimiza la UX para ese caso en v1.]`

### 2.3 Key User Journeys

- **UJ-1. Marta confirma la toma de su padre y toda la familia se entera al instante.**
  - **Persona + contexto:** Marta es la cuidadora principal de su padre, que vive con ella y toma medicación para hipertensión tres veces al día. Sus dos hermanos viven en otras ciudades.
  - **Entry state:** Marta tiene la app abierta tras recibir la notificación push de la dosis de las 8am. Está autenticada desde una sesión previa.
  - **Path:** Ve la notificación con el sonido distintivo del medicamento → abre la app → ve la tarjeta de la dosis pendiente en el Calendario Compartido → le da el medicamento a su padre → toca "Confirmar toma".
  - **Climax:** Al confirmar, la app marca la dosis como tomada en el calendario y envía una notificación de Confirmación Cruzada a sus dos hermanos en tiempo real — ninguno tiene que preguntar.
  - **Resolution:** Marta sigue con su día sabiendo que el resto de la familia ya está al tanto, sin necesidad de escribir en el grupo de WhatsApp.
  - **Edge case:** Si Marta confirma la toma fuera de la ventana de tiempo esperada (ej. una hora tarde), la app registra la hora real, no la hora programada, para que el Panel de Adherencia Histórica sea preciso.

- **UJ-2. Don Carlos no responde a su alarma y la app escala hasta activar el contacto de emergencia.**
  - **Persona + contexto:** Don Carlos, 78 años, vive solo y toma un anticoagulante (medicamento crítico) dos veces al día. Su hija Marta es su cuidadora principal; su sobrino es el contacto de emergencia designado.
  - **Entry state:** Don Carlos no está autenticado en ese momento (la alarma suena en su teléfono en segundo plano). Ha pasado la hora de la dosis de la tarde.
  - **Path:** La alarma suena y no la confirma → tras N minutos sin confirmación, la app envía push a Marta (cuidadora principal) → Marta no responde en M minutos → la app escala a SMS a Marta → sigue sin respuesta → la app intenta una llamada automatizada al propio Don Carlos.
  - **Climax:** Si tampoco hay respuesta a la llamada a Don Carlos, se activa el Protocolo de Última Línea: se notifica al contacto de emergencia (su sobrino) por todos los canales disponibles, indicando que es una alerta de medicamento crítico sin confirmar.
  - **Resolution:** El sobrino llama a Don Carlos o se acerca a verificar. Cuando alguien finalmente confirma la situación (toma tardía, o intervención), la app cierra el ciclo de escalada y registra lo ocurrido para el historial.
  - **Edge case:** Si Don Carlos confirma la toma en cualquier punto de la cadena (incluso después del push inicial), la escalada se detiene de inmediato y no se notifica a nadie más — evita falsos positivos y alarmar innecesariamente al círculo de cuidado.

- **UJ-3. Don Carlos decide quién entra a su círculo de cuidado y qué puede ver cada uno.**
  - **Persona + contexto:** Don Carlos crea su cuenta por primera vez, acompañado por su hija Marta, antes de cualquier deterioro cognitivo.
  - **Entry state:** Cuenta nueva, sin cuidadores asociados todavía.
  - **Path:** Completa su perfil y medicamentos → invita a Marta como cuidadora principal (ella acepta la invitación desde su propio teléfono) → invita a su sobrino con un rol más limitado (solo ve alertas de emergencia, no el historial completo) → en la misma sesión, designa a Marta como su "testamento digital de cuidado": quien asumirá el control de la cuenta si él pierde la capacidad de decisión.
  - **Climax:** Cada cuidador ve únicamente lo que su rol define — Marta ve todo, el sobrino solo ve alertas críticas — y ambos saben que fueron invitados explícitamente, no que se "autoagregaron".
  - **Resolution:** Don Carlos mantiene el control de su red de cuidado, y la familia ya tiene claridad anticipada sobre quién decide si él no puede.
  - **Edge case:** Si Don Carlos ya tuviera una condición que le impide crear la cuenta él mismo (ej. un evento de salud reciente), un cuidador puede crear la cuenta en su nombre y registrar el consentimiento de forma asistida. `[ASSUMPTION: el flujo asistido requiere un mecanismo de consentimiento documentado distinto al de autoinvitación; se detalla en FR-12.]`

## 3. Glosario

- **Paciente** — La persona cuya medicación se rastrea. Es el dueño de su Círculo de Cuidado y de los permisos sobre sus datos.
- **Cuidador** — Cualquier persona invitada por el Paciente (o por su Cuidador de Respaldo) para ver y/o actuar sobre el seguimiento de medicación. Puede ser Cuidador Principal o tener un rol con permisos más limitados.
- **Cuidador Principal** — El Cuidador con el nivel de acceso más alto dentro del Círculo de Cuidado (ej. confirma tomas en nombre del Paciente, ve el historial completo). Puede haber más de uno.
- **Cuidador de Respaldo** — El Cuidador designado en el Testamento Digital de Cuidado para asumir control de la cuenta si el Paciente pierde capacidad de decisión.
- **Círculo de Cuidado** — El conjunto de Cuidadores asociados a un Paciente (máximo 5 en v1), cada uno con su Nivel de Compartición de Datos.
- **Calendario de Medicación Compartido** — La vista única del horario de medicamentos, horarios y estado de toma, visible (con los filtros de Nivel de Compartición que correspondan) a todos los miembros del Círculo de Cuidado.
- **Confirmación de Toma** — El registro de que una dosis fue efectivamente tomada, con la hora real en que se confirmó (no necesariamente la hora programada).
- **Confirmación Cruzada** — La notificación automática que reciben los demás miembros del Círculo de Cuidado cuando alguien marca una Confirmación de Toma.
- **Medicamento Crítico** — Un medicamento marcado por el Paciente o Cuidador Principal como de alto riesgo si se omite (ej. anticoagulantes), lo que activa tiempos de Escalada de Notificaciones más agresivos.
- **Escalada de Notificaciones** — La secuencia ordenada de canales (push → SMS → llamada automatizada) y destinatarios que se activa cuando una dosis no se confirma dentro del tiempo esperado, con velocidad proporcional a si el medicamento es Crítico.
- **Protocolo de Última Línea** — El paso final de la Escalada de Notificaciones: si nadie en el Círculo de Cuidado responde (incluyendo el intento de llamada al propio Paciente), se notifica al Contacto de Emergencia.
- **Contacto de Emergencia** — La persona designada por el Paciente (o su Cuidador de Respaldo) que se notifica únicamente cuando se activa el Protocolo de Última Línea.
- **Alerta de Patrón** — Una notificación distinta a la Alerta Puntual, disparada cuando se detecta incumplimiento en varios días consecutivos (no solo una dosis aislada), dirigida a Cuidadores con visibilidad de adherencia histórica.
- **Panel de Adherencia Histórica** — La vista de tendencia de cumplimiento de un Paciente en el tiempo, distinta de la vista del día actual.
- **Nivel de Compartición de Datos** — El rol que define qué subconjunto de información del Paciente puede ver cada Cuidador ("mínimo necesario" por defecto, no acceso total).
- **Testamento Digital de Cuidado** — La designación anticipada, hecha por el Paciente, de su Cuidador de Respaldo y de las condiciones bajo las cuales este asume control de la cuenta.
- **Invitación y Consentimiento** — El mecanismo por el cual un Cuidador solo se une al Círculo de Cuidado mediante invitación explícita del Paciente (o de su Cuidador de Respaldo, si ya está activo), nunca por autoagregado.

## 4. Features

### 4.1 Calendario de Medicación Compartido

**Descripción:** Vista única, en tiempo real, del horario de medicación de un Paciente, visible para todos los miembros del Círculo de Cuidado según su Nivel de Compartición de Datos. Reemplaza la coordinación informal por WhatsApp/llamadas. Realiza UJ-1, UJ-3.

**Requerimientos Funcionales:**

#### FR-1: Crear y editar el horario de medicación

El Paciente o un Cuidador Principal puede crear, editar y eliminar medicamentos y sus horarios de toma.

**Consecuencias (verificables):**
- Cada medicamento tiene nombre, dosis, horario(s) de toma y un flag de Medicamento Crítico (sí/no).
- Un cambio de horario hecho por cualquier Cuidador Principal se refleja para todos los miembros del Círculo de Cuidado en menos de 5 segundos `[ASSUMPTION: umbral de 5s a confirmar con NFR de sincronización; ver §Cross-Cutting NFRs]`.

#### FR-2: Vista compartida del calendario filtrada por Nivel de Compartición

Cualquier miembro del Círculo de Cuidado puede ver el calendario de medicación, mostrando únicamente los medicamentos y detalles que su Nivel de Compartición de Datos permite.

**Consecuencias (verificables):**
- Un Cuidador con rol limitado (ej. solo alertas) no ve el detalle de dosis/medicamento, solo el estado general ("al día" / "alerta activa").
- Un Cuidador Principal ve el detalle completo: medicamento, dosis, hora programada, hora real de confirmación.

**Notas:** El diseño visual del calendario (sonido distintivo por medicamento, tarjeta visual) quedó esbozado en el brainstorming (SCAMPER-S #1) pero se trata como detalle de UX, no como FR de este PRD — se delega a un futuro spec de UX.

### 4.2 Confirmación de Toma y Confirmación Cruzada

**Descripción:** Cierra el ciclo de cada dosis: registra si la toma ocurrió a la hora real (no solo si la alarma sonó) y notifica automáticamente a los demás cuidadores. Realiza UJ-1.

**Requerimientos Funcionales:**

#### FR-3: Confirmar una toma

El Paciente o un Cuidador Principal puede marcar una dosis programada como tomada, registrando la hora real de confirmación.

**Consecuencias (verificables):**
- Una dosis confirmada cambia de estado "pendiente" a "tomada" en el Calendario Compartido para todos los miembros del Círculo de Cuidado.
- La hora real de confirmación se almacena por separado de la hora programada, y es la que alimenta el Panel de Adherencia Histórica (FR-9).

#### FR-4: Notificación de Confirmación Cruzada

Cuando se registra una Confirmación de Toma, el sistema notifica automáticamente a todos los demás miembros del Círculo de Cuidado con permiso para verla.

**Consecuencias (verificables):**
- La notificación de Confirmación Cruzada llega a los demás Cuidadores en menos de 10 segundos desde la confirmación `[ASSUMPTION: umbral a validar contra el proveedor de push elegido]`.
- Un Cuidador con Nivel de Compartición limitado recibe únicamente un estado agregado ("dosis de la tarde: tomada"), no el detalle del medicamento, si su rol no lo permite.

### 4.3 Panel de Adherencia Histórica y Alerta de Patrón

**Descripción:** Da visibilidad de tendencia (no solo del día) a los Cuidadores que la necesitan — especialmente al familiar a distancia que no puede verificar presencialmente — y distingue una omisión puntual de un patrón preocupante. Realiza UJ-3.

**Requerimientos Funcionales:**

#### FR-5: Panel de Adherencia Histórica

Un Cuidador con Nivel de Compartición que incluya historial puede ver la tasa de cumplimiento de un Paciente en un rango de tiempo (ej. últimos 7/30 días).

**Consecuencias (verificables):**
- El panel muestra, como mínimo, % de dosis confirmadas a tiempo, % confirmadas tarde, y % no confirmadas, por rango de fechas seleccionado.

#### FR-6: Alerta de Patrón vs. Alerta Puntual

El sistema distingue una dosis aislada no confirmada (Alerta Puntual, manejada por la Escalada de Notificaciones de §4.4) de un patrón de incumplimiento en días consecutivos (Alerta de Patrón).

**Consecuencias (verificables):**
- Tras N días consecutivos con al menos una dosis no confirmada (umbral configurable, default `[ASSUMPTION: 3 días consecutivos]`), el sistema dispara una Alerta de Patrón a los Cuidadores con visibilidad de adherencia histórica, distinta visualmente y en el copy de la notificación de una Alerta Puntual.
- La Alerta de Patrón no reemplaza la Escalada de Notificaciones de la dosis individual — ambas pueden coexistir.

**Notas:** `[NOTE FOR PM]` El umbral exacto de "patrón preocupante" (días consecutivos, qué cuenta como "incumplimiento parcial" vs. total) quedó como obstáculo abierto en el brainstorming y debería validarse con las familias del piloto antes de fijarlo en producción. Ver Open Questions.

### 4.4 Escalada de Notificaciones por Criticidad

**Descripción:** Cuando una dosis no se confirma dentro del tiempo esperado, el sistema escala por canal y destinatario, con velocidad proporcional a si el medicamento es Crítico. Es el mecanismo central de "vigilancia útil" sin necesitar que un humano esté monitoreando activamente. Realiza UJ-2.

**Requerimientos Funcionales:**

#### FR-7: Configurar criticidad por medicamento

El Paciente o Cuidador Principal puede marcar cualquier medicamento como Crítico al crearlo o editarlo (ver FR-1).

**Consecuencias (verificables):**
- Marcar/desmarcar un medicamento como Crítico cambia inmediatamente los tiempos de espera de la cadena de escalada (FR-8) para ese medicamento, sin necesidad de reiniciar nada.

#### FR-8: Cadena de Escalada de Notificaciones

Si una dosis no se confirma dentro de la ventana de tiempo esperada, el sistema escala automáticamente: push al Paciente → push a Cuidadores Principales → SMS a Cuidadores Principales → llamada automatizada al Paciente, deteniéndose en cualquier punto si se registra la Confirmación de Toma.

**Consecuencias (verificables):**
- Para un medicamento Crítico, el tiempo entre cada paso de la cadena es menor que para uno no Crítico `[ASSUMPTION: tiempos exactos (ej. 15min vs 60min por paso) a definir con el piloto, no fijos en este PRD]`.
- En cualquier punto de la cadena, una Confirmación de Toma detiene inmediatamente los pasos restantes y no se notifica a nadie más por esa dosis.
- Cada paso ejecutado de la cadena queda registrado (timestamp, canal, destinatario) para auditoría y para el Panel de Adherencia Histórica.

**Requerimientos no funcionales específicos de la feature:**
- La entrega de la notificación inicial (push) debe iniciarse en menos de 60 segundos desde que se detecta la dosis no confirmada.
- El sistema debe evitar duplicar el envío del mismo paso de escalada si dos procesos lo detectan simultáneamente (idempotencia).

### 4.5 Protocolo de Última Línea — Contacto de Emergencia

**Descripción:** El paso final de seguridad: si la Escalada de Notificaciones completa no obtiene respuesta de nadie (incluyendo el intento de contacto directo al Paciente), se notifica a un Contacto de Emergencia designado. Realiza UJ-2.

**Requerimientos Funcionales:**

#### FR-9: Designar Contacto de Emergencia

El Paciente (o su Cuidador de Respaldo, si ya tiene control de la cuenta) puede designar uno o más Contactos de Emergencia, distintos de los Cuidadores del día a día.

**Consecuencias (verificables):**
- Un Contacto de Emergencia no recibe ninguna notificación del Calendario Compartido ni de Confirmaciones Cruzadas — únicamente se le notifica si se activa el Protocolo de Última Línea.
- El Contacto de Emergencia debe aceptar/confirmar su rol antes de quedar activo (consistente con Invitación y Consentimiento, FR-12).

#### FR-10: Activación del Protocolo de Última Línea

Si la Cadena de Escalada (FR-8) se completa sin ninguna Confirmación de Toma, el sistema notifica a todos los Contactos de Emergencia por todos los canales disponibles.

**Consecuencias (verificables):**
- La notificación al Contacto de Emergencia indica explícitamente que se trata de una alerta de "última línea" (medicamento sin confirmar tras escalada completa), no una alerta genérica.
- El evento de activación del Protocolo de Última Línea queda registrado y visible para los Cuidadores Principales, incluso después de resuelto.

**Out of Scope:**
- Esta función no sustituye un servicio de emergencias médicas. La app no garantiza tiempos de respuesta de terceros (ver Constraints and Guardrails — Safety).

### 4.6 Gestión de Cuidadores: Invitación, Consentimiento y Niveles de Compartición

**Descripción:** Da al Paciente control sobre quién entra a su Círculo de Cuidado y qué ve cada persona, resolviendo la tensión entre vigilancia útil y autonomía/dignidad. Realiza UJ-3.

**Requerimientos Funcionales:**

#### FR-11: Definir Niveles de Compartición de Datos por rol

El sistema ofrece al menos dos Niveles de Compartición predefinidos (ej. "Completo" y "Solo alertas") que el Paciente o Cuidador Principal asigna a cada Cuidador al invitarlo.

**Consecuencias (verificables):**
- Por defecto, ningún Cuidador nuevo recibe acceso "Completo" sin que el Paciente (o quien tenga control de la cuenta) lo asigne explícitamente — el nivel mínimo es el default.
- Cambiar el Nivel de Compartición de un Cuidador existente se refleja en la siguiente vista que ese Cuidador abra, sin requerir reinvitación.

#### FR-12: Invitación y Consentimiento explícito

Un Cuidador solo se asocia a un Paciente mediante una invitación enviada por el Paciente (o su Cuidador de Respaldo activo) que el invitado debe aceptar explícitamente.

**Consecuencias (verificables):**
- No existe ningún mecanismo de "autoagregado" — un Cuidador no puede unirse a un Círculo de Cuidado sin una invitación pendiente y aceptada.
- El Círculo de Cuidado tiene un máximo de 5 Cuidadores en v1; al llegar al límite, el sistema bloquea nuevas invitaciones y muestra un mensaje claro.
- Si el Paciente no puede crear la cuenta por sí mismo (ej. condición de salud previa), un Cuidador puede crearla en su nombre, pero el flujo registra explícitamente quién la creó y bajo qué consentimiento asistido — distinto del flujo de autoinvitación estándar.

**Feature-specific NFRs:**
- Toda acción de cambio de permisos (invitar, cambiar nivel, remover cuidador) debe quedar en un registro auditable, ver Constraints and Guardrails — Privacy.

### 4.7 Testamento Digital de Cuidado

**Descripción:** Mecanismo de continuidad: el Paciente designa anticipadamente quién asume el control de su cuenta si pierde capacidad de decisión, evitando que la familia tenga que improvisar en una crisis. Realiza UJ-3.

**Requerimientos Funcionales:**

#### FR-13: Designar Cuidador de Respaldo

El Paciente puede designar, en cualquier momento, a un Cuidador existente como su Cuidador de Respaldo.

**Consecuencias (verificables):**
- Solo puede haber un Cuidador de Respaldo activo a la vez por Paciente.
- El Paciente puede cambiar de Cuidador de Respaldo en cualquier momento mientras conserve capacidad de decisión.

#### FR-14: Transferencia de control al Cuidador de Respaldo

El sistema ofrece un mecanismo explícito (no automático ni silencioso) por el cual el Cuidador de Respaldo puede solicitar asumir el control de la cuenta del Paciente.

**Consecuencias (verificables):**
- La transferencia de control no ocurre automáticamente por inactividad del Paciente; requiere una acción explícita del Cuidador de Respaldo `[ASSUMPTION: el mecanismo exacto de verificación/aprobación de esa transferencia (ej. requiere confirmación de un segundo Cuidador Principal, o solo del Cuidador de Respaldo) no está definido — ver Open Questions]`.
- Una vez transferido el control, el Cuidador de Respaldo puede gestionar Cuidadores, Niveles de Compartición y Contacto de Emergencia en nombre del Paciente.
- El evento de transferencia de control queda registrado de forma permanente y visible para todo el Círculo de Cuidado.

**Notas:** `[NOTE FOR PM]` Este es uno de los conceptos de mayor impacto identificados en el brainstorming. El mecanismo legal/técnico exacto de verificación (qué evita un abuso de esta función) necesita validación con asesoría legal antes de construirse — ver §Compliance and Regulatory y Open Questions.

## 5. Non-Goals (Explicit)

- Esta app **no es** una herramienta para clínicas, hospitales o cuidadores profesionales que gestionan múltiples pacientes simultáneamente. Ese caso de uso fue explícitamente descartado para esta ronda.
- Esta app **no es** un dispensador de medicamentos ni se integra con hardware de dispensado en el MVP (Tema 4 del brainstorming, diferido).
- Esta app **no ofrece** gamificación, rachas de adherencia ni mecánicas de engagement en el MVP (Tema 5, diferido).
- Esta app **no incluye** ningún modelo de monetización, suscripción, freemium ni integración con farmacias en este PRD (Temas 4 y 6, diferidos a un PRD futuro de fase 2/monetización).
- Esta app **no sustituye** un servicio de emergencias médicas ni garantiza tiempos de respuesta ante una alerta del Protocolo de Última Línea — es una ayuda de coordinación familiar, no un servicio de emergencia profesional.
- Esta app **no ofrece** asesoría médica ni valida la corrección clínica de dosis u horarios — el contenido de medicamentos y horarios es responsabilidad del Paciente/Cuidador, no del sistema.

## 6. MVP Scope

### 6.1 In Scope

- Calendario de Medicación Compartido (crear/editar medicamentos y horarios, vista filtrada por rol).
- Confirmación de Toma y Confirmación Cruzada en tiempo real.
- Panel de Adherencia Histórica y Alerta de Patrón vs. Alerta Puntual.
- Escalada de Notificaciones por Criticidad (push → SMS → llamada automatizada).
- Protocolo de Última Línea con Contacto de Emergencia.
- Gestión de Cuidadores: invitación y consentimiento explícito, Niveles de Compartición de Datos, límite de 5 Cuidadores por Círculo de Cuidado.
- Testamento Digital de Cuidado (designación de Cuidador de Respaldo y transferencia de control).
- Plataforma: app móvil (iOS/Android) como superficie principal + panel web complementario `[ASSUMPTION: el panel web cubre al menos el Panel de Adherencia Histórica y la gestión de Cuidadores; el detalle de qué vive en web vs. móvil se define en UX]`.
- Piloto inicial en Colombia, con el marco de Habeas Data colombiano (Ley 1581 de 2012) como referencia regulatoria mínima.

### 6.2 Out of Scope for MVP

- Inventario inteligente de medicamentos, alianzas con farmacias, reabastecimiento automático, comisiones por pedido (Tema 4 — diferido a fase de monetización/suministro).
- Dispensador inteligente propio o integración con dispensadores de terceros (Tema 4 — diferido).
- Gamificación / rachas de adherencia (Tema 5 — diferido, valor de engagement no crítico para validar la coordinación core).
- Sonido distintivo por medicamento y pulido visual del calendario — se trata como detalle de UX a definir en un spec separado, no como FR de este PRD.
- Cualquier modelo de negocio, pricing, freemium o suscripción (Tema 6 — diferido a un PRD de fase 2; `[NOTE FOR PM]` el brainstorming ya esbozó freemium + suscripción familiar como dirección probable, vale la pena revisitar una vez validada la adopción del MVP).
- Soporte multi-país / multi-marco regulatorio simultáneo — el piloto se valida en Colombia primero.
- Casos de uso clínicos/profesionales con múltiples pacientes por cuidador.

## 7. Cross-Cutting NFRs

- **Sincronización en tiempo real:** Un cambio de estado (Confirmación de Toma, cambio de horario, cambio de permisos) debe reflejarse para todos los miembros conectados del Círculo de Cuidado en segundos, no minutos — es el requisito que sostiene la promesa central de "visibilidad compartida sin preguntar".
- **Confiabilidad de notificaciones multicanal:** El sistema depende de proveedores externos de push/SMS/llamada; debe tolerar la falla de un canal individual sin detener la Cadena de Escalada completa (ej. si SMS falla, igual debe intentar el siguiente paso).
- **Disponibilidad:** El servicio de Escalada de Notificaciones y Protocolo de Última Línea es la función de mayor criticidad de seguridad del producto; debe tener disponibilidad más alta que el resto de la app `[ASSUMPTION: objetivo numérico de disponibilidad (ej. 99.9%) pendiente de definir con el equipo de infraestructura]`.
- **Auditabilidad:** Toda acción sobre permisos, Contacto de Emergencia, Testamento Digital de Cuidado y cada paso de la Cadena de Escalada debe quedar registrada con timestamp y actor, de forma inmutable.

## 8. Constraints and Guardrails

**Privacy**
- Mínimo dato necesario por defecto: ningún Cuidador nuevo ve el historial completo de salud sin que se le asigne explícitamente ese Nivel de Compartición (ver FR-11).
- Los datos de salud del Paciente (medicamentos, horarios, adherencia) se tratan como datos sensibles bajo el régimen de Habeas Data colombiano.

**Safety**
- La app debe comunicar claramente, dentro del producto (no solo en términos legales), que el Protocolo de Última Línea es una ayuda de coordinación familiar y no un servicio de emergencias garantizado — para evitar que las familias depositen una confianza de "red de seguridad infalible" que el producto no puede sostener.
- La función de transferencia de control del Testamento Digital de Cuidado debe diseñarse para minimizar el riesgo de abuso (ej. un Cuidador de Respaldo tomando control sin que el Paciente realmente haya perdido capacidad) — mecanismo exacto pendiente (ver Open Questions).

## 9. Compliance and Regulatory

- El tratamiento de datos de salud sensibles del Paciente debe cumplir con la Ley 1581 de 2012 (Habeas Data, Colombia) como marco mínimo para el piloto.
- `[NOTE FOR PM]` Se recomienda una consulta legal puntual antes del lanzamiento del piloto, específicamente sobre: (a) la validez del Testamento Digital de Cuidado como mecanismo de transferencia de control dentro de una app (no un documento legal formal), y (b) el lenguaje de disclaimer necesario para el Protocolo de Última Línea (ver Constraints and Guardrails — Safety).
- Este PRD no asume cumplimiento con HIPAA o GDPR — el piloto está acotado a Colombia; si el producto se expande a otros mercados, el marco regulatorio debe revisarse de nuevo.

## 10. Success Metrics

**Primary**
- **SM-1**: % de dosis confirmadas dentro de la ventana esperada (sin necesidad de escalar más allá del push inicial) sobre el total de dosis programadas, por Paciente. Objetivo del piloto: validar tendencia ascendente semana a semana. Valida FR-3, FR-4.
- **SM-2**: Tiempo entre la falta de confirmación y la notificación de Confirmación Cruzada / push inicial — objetivo < 60 segundos. Valida FR-4, FR-8.
- **SM-3**: % de familias piloto con al menos 2 Cuidadores activos en el Círculo de Cuidado (evidencia de que la coordinación compartida, no solo la alarma individual, se está usando). Valida FR-12.

**Secondary**
- **SM-4**: % de Alertas de Patrón que el Cuidador receptor marca como "útil" / relevante (vs. ruido). Valida FR-6.
- **SM-5**: Tiempo desde la activación del Protocolo de Última Línea hasta la resolución registrada (alguien confirma la situación). Valida FR-10.

**Counter-metrics (no optimizar directamente)**
- **SM-C1**: Tasa de desactivación de notificaciones o de abandono de la app tras una Escalada de Notificaciones — si sube, indica fatiga de alertas, no éxito del producto. Contrarresta SM-1 y SM-2 (no se debe optimizar "más alertas, más rápido" a costa de fatigar a las familias).
- **SM-C2**: Tasa de falsos positivos del Protocolo de Última Línea (activaciones donde el Paciente estaba bien y simplemente no vio el teléfono). Contrarresta SM-5 (resolver rápido no es éxito si la alerta nunca debió dispararse).

## 11. Open Questions

1. ¿Cuáles son los tiempos exactos (en minutos) de cada paso de la Cadena de Escalada, para medicamentos Críticos vs. no Críticos? (FR-8)
2. ¿Cuál es el umbral exacto de "patrón preocupante" para la Alerta de Patrón — días consecutivos, dosis parciales vs. totales? (FR-6)
3. ¿Qué mecanismo de verificación/aprobación protege la Transferencia de Control del Testamento Digital de Cuidado contra abuso? (FR-14)
4. ¿Qué proveedor(es) de push/SMS/llamada automatizada se usarán, y qué garantías de entrega ofrecen en Colombia? (Cross-Cutting NFRs)
5. ¿Qué lenguaje de disclaimer legal exacto se necesita para el Protocolo de Última Línea, y la validez del Testamento Digital de Cuidado dentro de la app? (Compliance and Regulatory) — requiere asesoría legal puntual.
6. ¿Qué vive en el panel web vs. la app móvil? (alcance de Plataforma, §6.1) — pendiente de definición en UX.
7. ¿Cómo se valida el piloto con familias reales — cuántas familias, por cuánto tiempo, qué criterio de éxito/fracaso del piloto antes de decidir si se invierte en fase 2 (monetización/suministro)?

## 12. Assumptions Index

- §2.2 — La app no bloquea un uso sin Cuidadores adicionales, pero no optimiza esa UX en v1.
- §2.3 (UJ-3, edge case) — El flujo de creación asistida de cuenta (cuando el Paciente no puede crearla él mismo) requiere un mecanismo de consentimiento documentado distinto al de autoinvitación estándar; detallado en FR-12.
- FR-1 — Umbral de sincronización del calendario (~5s) propuesto, pendiente de validar como NFR formal.
- FR-4 — Umbral de entrega de Confirmación Cruzada (~10s) propuesto, pendiente de validar contra el proveedor de push elegido.
- FR-6 — Umbral default de Alerta de Patrón (3 días consecutivos) propuesto, pendiente de validación con familias del piloto (ver Open Questions #2).
- FR-8 — Los tiempos exactos por paso de la Cadena de Escalada (Crítico vs. no Crítico) no están fijados en este PRD (ver Open Questions #1).
- FR-14 — El mecanismo exacto de verificación/aprobación de la Transferencia de Control no está definido (ver Open Questions #3).
- §6.1 — El alcance exacto del panel web (qué funciones vive ahí vs. en móvil) es una suposición inicial, pendiente de UX (ver Open Questions #6).
- §7 — Objetivo numérico de disponibilidad del servicio de Escalada/Última Línea no está fijado.
