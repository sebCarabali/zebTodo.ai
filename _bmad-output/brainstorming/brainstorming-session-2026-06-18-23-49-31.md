---
stepsCompleted: [1, 2, 3, 4]
session_active: false
workflow_completed: true
inputDocuments: []
session_topic: 'App de alarmas de medicación — MVP para familias/cuidadores que comparten el seguimiento de un mismo paciente, con notificaciones multicanal'
session_goals: 'Generar ideas de funcionalidades y de modelos de negocio para el MVP'
selected_approach: 'ai-recommended'
techniques_used: ['Role Playing', 'SCAMPER Method (partial)', 'Six Thinking Hats (partial)']
ideas_generated: [20]
context_file: ''
---

# Brainstorming Session Results

**Facilitator:** SEBASTIANDAVIDCARABA
**Date:** 2026-06-18

## Session Overview

**Topic:** App de alarmas de medicación — MVP para familias/cuidadores que comparten el seguimiento de un mismo paciente (sin enfoque clínico/profesional por ahora), con notificaciones multicanal (canales a explorar durante la sesión).

**Goals:** Generar ideas de funcionalidades (features) y de modelos de negocio para este MVP.

### Context Guidance

_No se proporcionó archivo de contexto adicional._

### Session Setup

Sesión enfocada exclusivamente en el caso de uso de familias/cuidadores compartiendo el seguimiento de medicación de un mismo paciente (se descartó explícitamente el caso de clínicas/cuidadores profesionales con múltiples pacientes para esta ronda). Notificaciones multicanal se mantienen abiertas como área de exploración.

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** App de alarmas de medicación (MVP familias/cuidadores) con foco en funcionalidades y modelos de negocio

**Recommended Techniques:**

- **Role Playing:** Encarnar distintos stakeholders (paciente, cuidador principal, familiar a distancia, médico) para anclar las ideas de funcionalidades en necesidades reales antes de expandir.
- **SCAMPER Method:** Expandir sistemáticamente las funcionalidades crudas de la Fase 1 a través de sus 7 lentes (Sustituir, Combinar, Adaptar, Modificar, Otros usos, Eliminar, Invertir).
- **Six Thinking Hats:** Generar y estresar ideas de modelo de negocio desde 6 ángulos complementarios (hechos, emociones, beneficios, riesgos, creatividad, proceso).

**AI Rationale:** El tema combina dos objetivos distintos (features de producto y modelo de negocio) sobre un caso de uso concreto (familia/cuidadores). Se eligió una secuencia que primero ancla en necesidades reales de usuarios (collaborative), luego expande sistemáticamente el catálogo de funcionalidades (structured), y finalmente aplica una técnica estructurada distinta para explorar modelos de negocio sin caer en debate prematuro.

## Technique Execution Results

### Role Playing — Cuidador Principal

- **[Cuidador #1]**: Alarma con Confirmación de Toma — la app cierra el ciclo registrando si la toma ocurrió a la hora real, no solo si sonó la alarma.
- **[Cuidador #2]**: Inventario Inteligente de Medicamentos — cuenta dosis restantes y avisa con anticipación para comprar/tramitar con la EPS.
- **[Cuidador #3]**: Calendario de Medicación Compartido y Visible — horario único visible para todos los cuidadores, no solo el paciente.
- **[Cuidador #4]**: Notificación de Confirmación Cruzada — al marcar "tomado", se notifica automáticamente a todos los demás cuidadores en tiempo real.
- **[Cuidador #5]**: Escalada de Notificaciones por Criticidad — velocidad y canal de escalada (push → SMS → llamada) según si el medicamento es crítico o no.
- **[Cuidador #6]**: Protocolo de Última Línea — Contacto de Emergencia — si nadie responde tras la escalada completa (incluyendo llamada al paciente), se activa un contacto de emergencia designado.

### Role Playing — Paciente

- **[Paciente #1]**: Cuidadores por Invitación y Consentimiento — el paciente decide quién entra a su red de cuidado; nadie se "autoagrega".
- **[Paciente #2]**: Compartición de Datos por Niveles (Mínimo Necesario) — cada cuidador ve solo lo que su rol requiere, no todo el historial médico por defecto.
- **[Paciente #3]**: Testamento Digital de Cuidado — al crear la cuenta, el paciente designa un cuidador de respaldo que asume control si pierde capacidad de decisión; si ya hay una condición previa, un cuidador puede crear la cuenta y registrarlo directamente.

**Insight clave emergente:** La app debe resolver la tensión entre **vigilancia útil** y **autonomía/dignidad del paciente**, con mecanismos de consentimiento explícito y transferencia de control anticipada — y entre **recordatorio simple** y **red de seguridad real** ante el silencio total (escalada hasta contacto de emergencia).

### Role Playing — Familiar a Distancia

- **[Familiar Distante #1]**: Panel de Adherencia Histórica — vista de tendencia/cumplimiento en el tiempo, no solo el estado de la toma del día.
- **[Familiar Distante #2]**: Alerta de Patrón vs. Alerta Puntual — una notificación olvidada es "suave"; varios días consecutivos de incumplimiento dispara una alerta distinta, más insistente, que sugiere un problema más serio que el simple olvido.

**Resumen Role Playing (11 ideas):** El recorrido por los tres roles (Cuidador Principal, Paciente, Familiar a Distancia) reveló que el MVP necesita resolver simultáneamente: visibilidad compartida del horario, confirmación cruzada de tomas, escalada de notificaciones proporcional a criticidad/tiempo, autonomía y consentimiento del paciente, y diferenciación entre alertas puntuales vs. patrones preocupantes — todo esto sobre una base de notificaciones multicanal.

### SCAMPER Method (parcial: Sustituir, Combinar, Adaptar)

- **[SCAMPER-S #1]**: Sonido Distintivo por Medicamento + Notificación Visual — cada medicamento con su propio sonido reconocible y una tarjeta visual clara, reduciendo carga cognitiva.
- **[SCAMPER-C #1]**: Dispensador Inteligente Compañero (Hardware Complementario) — integración con dispensadores inteligentes existentes, con visión a futuro de un dispensador propio exclusivo de la app; abre una posible línea de ingresos de hardware.
- **[SCAMPER-A #1]**: Rachas Resilientes de Adherencia — gamificación adaptada de apps de fitness, pero con reinicio rápido y sin castigo duro, ajustada a la realidad emocional de la salud.

**Nota de continuidad:** SCAMPER quedó pausado tras la lente "Adaptar" (faltan Modificar, Otros usos, Eliminar, Invertir) para priorizar la exploración de modelo de negocio con Six Thinking Hats. Se puede retomar SCAMPER más adelante en la sesión si hay tiempo/energía.

### Six Thinking Hats — Modelo de Negocio (parcial: Blanco, Amarillo, Negro, Verde)

- **[Hechos #1]**: Pago Directo B2C con Puerta Abierta a Convenios B2B2C — pago de bolsillo de paciente/cuidador, sin cerrar la puerta a convenios futuros con EPS/aseguradoras.
- **[Amarillo #1]**: Suscripción Mensual como Modelo Principal — cobro por círculo familiar/de cuidado, no por usuario individual.
- **[Amarillo #2]**: Freemium con Funciones Críticas como Gancho de Conversión — la capa gratuita cubre lo básico; lo de pago desbloquea calendario compartido, escalada multicanal, inventario inteligente y panel de adherencia histórica.
- **[Negro #1]**: Riesgo Regulatorio de Datos de Salud Sensibles — exposición a Habeas Data/HIPAA/GDPR; mitigado por el diseño de mínimo dato necesario ya explorado en Role Playing.
- **[Verde #1]**: Alianza con Farmacias para Reabastecimiento Automático — cuando el inventario está bajo, la app genera un pedido automático a una farmacia aliada.
- **[Verde #2]**: Comisión por Pedido a Farmacia Aliada — línea de ingresos transaccional y variable, complementaria a la suscripción.

**Nota de continuidad:** Six Thinking Hats quedó pausado antes de los sombreros Rojo (emociones) y Azul (proceso) por decisión del usuario para pasar a organización de ideas.

**Total de ideas generadas en la sesión: 20**

## Idea Organization and Prioritization

**Organización Temática:**

- **Tema 1 — Visibilidad y Coordinación Familiar Compartida:** Calendario de Medicación Compartido, Notificación de Confirmación Cruzada, Alarma con Confirmación de Toma, Panel de Adherencia Histórica, Alerta de Patrón vs. Puntual.
- **Tema 2 — Seguridad y Escalada ante Riesgo:** Escalada de Notificaciones por Criticidad, Protocolo de Última Línea (Contacto de Emergencia).
- **Tema 3 — Autonomía, Consentimiento y Privacidad del Paciente:** Cuidadores por Invitación y Consentimiento, Compartición de Datos por Niveles, Testamento Digital de Cuidado, Riesgo Regulatorio de Datos de Salud Sensibles.
- **Tema 4 — Gestión de Suministro:** Inventario Inteligente de Medicamentos, Alianza con Farmacias, Comisión por Pedido, Dispensador Inteligente Compañero.
- **Tema 5 — Experiencia y Engagement:** Sonido Distintivo por Medicamento + Notificación Visual, Rachas Resilientes de Adherencia.
- **Tema 6 — Modelo de Negocio Base:** Pago Directo B2C con Puerta Abierta a Convenios, Suscripción Mensual, Freemium con Funciones Críticas como Gancho.

**Resultados de Priorización:**

El usuario seleccionó los **Temas 1, 2 y 3** como núcleo funcional del MVP (dejando Suministro y Modelo de Negocio para fases posteriores de monetización), priorizando específicamente:

- **Prioridad 1 (a atacar primero):** Notificaciones a Cuidadores — Calendario Compartido + Confirmación Cruzada + Alarma con Confirmación de Toma
- **Prioridad 2:** Vigilancia ante Descuido del Paciente — Escalada por Criticidad + Protocolo de Última Línea + Alerta de Patrón
- **Prioridad 3:** Privacidad de los Datos — Compartición por Niveles + Cuidadores por Invitación + Riesgo Regulatorio

**Conceptos de Mayor Impacto (Breakthrough):** Testamento Digital de Cuidado, Protocolo de Última Línea, Comisión por Pedido a Farmacia Aliada.

**Planeación de Acción:**

**Prioridad 1 — Notificaciones a Cuidadores**
- Próximos pasos: definir modelo de datos (paciente → medicamentos → horarios → cuidadores → estado de toma); diseñar flujo de confirmación cruzada con push notification; prototipar calendario compartido y validar con 1-2 familias reales.
- Recursos: stack de push multicanal con SMS de respaldo; acceso a familias para validación; definición de roles de cuidador.
- Obstáculos: sincronización en tiempo real sin duplicar confirmaciones; decidir límite de cuidadores por paciente en v1.
- Éxito: visibilidad total del horario sin preguntar a nadie; confirmaciones reflejadas en segundos para todos los cuidadores.

**Prioridad 2 — Vigilancia ante Descuido del Paciente**
- Próximos pasos: definir criticidad por medicamento; diseñar cadena de escalada (tiempo → canal → destinatario); definir umbral de "patrón preocupante".
- Recursos: proveedor de SMS/llamadas automatizadas; lógica backend de tracking de tiempo; campo de contacto de emergencia con consentimiento.
- Obstáculos: evitar falsos positivos; claridad legal de que la app es una ayuda, no un servicio de emergencia garantizado.
- Éxito: ningún medicamento crítico sin notificación multicanal dentro de un umbral definido; contacto de emergencia activado solo en silencio real.

**Prioridad 3 — Privacidad de los Datos**
- Próximos pasos: diseñar modelo de permisos por rol (mínimo necesario); construir flujo de invitación/consentimiento; consultar a un asesor legal sobre Habeas Data en Colombia.
- Recursos: asesoría legal puntual; políticas de privacidad definidas desde el día 1.
- Obstáculos: balancear privacidad con simplicidad para usuarios mayores; mecanismos legales de respaldo para el Testamento Digital.
- Éxito: todo acceso de un cuidador queda respaldado por consentimiento explícito registrado; cumplimiento básico de Habeas Data antes del lanzamiento.

## Session Summary and Insights

**Key Achievements:**

- 20 ideas generadas colaborativamente a través de 3 técnicas (Role Playing completa, SCAMPER y Six Thinking Hats parciales)
- 6 temas organizados, con 3 priorizados como núcleo del MVP
- 3 planes de acción concretos y secuenciados, empezando por Notificaciones a Cuidadores

**Session Reflections:**

La sesión reveló que el verdadero valor del producto no está en la alarma en sí, sino en la **visibilidad compartida entre múltiples cuidadores** y en la tensión productiva entre **vigilancia útil** y **autonomía del paciente**. El concepto de Testamento Digital de Cuidado resolvió elegantemente esa tensión. El modelo de negocio quedó esbozado (freemium + suscripción familiar, con una línea futura de comisiones por farmacia) pero se decidió priorizar primero las funcionalidades core del MVP antes de profundizar más en monetización.
