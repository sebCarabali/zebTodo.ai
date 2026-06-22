---
name: Juntos
status: final
sources:
  - "{planning_artifacts}/prds/prd-Juntos-2026-06-19/prd.md"
  - "{planning_artifacts}/architecture.md"
updated: 2026-06-21
---

> `[ASSUMPTION]` — Esta spine asume el reparto móvil/web confirmado en esta sesión (resuelve PRD Open Question #6): móvil completo, web complementario de solo consulta + gestión ligera. Umbral de "Alerta de Patrón" (3 días) y mecanismo de aprobación del Testamento Digital quedan marcados `[ASSUMPTION]` abajo — no validados con el usuario todavía.

## Foundation

Multi-superficie: **móvil nativo** (MAUI, iOS + Android, MVVM con CommunityToolkit.Mvvm) es la superficie completa y principal — el paciente y el cuidador principal viven aquí en el día a día. **Panel web** (Blazor) es complementario: para cuidadores a distancia que consultan adherencia y gestionan el círculo de cuidado desde una laptop, sin confirmar tomas desde ahí. Ningún sistema de UI de terceros — controles nativos de plataforma en móvil, componentes Blazor a medida en web. `DESIGN.md` es la referencia de identidad visual; esta spine es la experiencia.

Tiempo real vía SignalR en ambas superficies — toda pantalla que muestre estado de adherencia o confirmaciones debe reflejar cambios en segundos, no requerir refresh manual como flujo normal.

**Restricción de arquitectura:** MVP es *online-only*. No hay manejo offline de confirmaciones o escalada — ver `State Patterns → Offline` para cómo se comunica esto sin generar pánico.

## Information Architecture

| Superficie | Plataforma | Alcanzable desde | Propósito | Visible para |
|---|---|---|---|---|
| Calendario de Medicación | Móvil | Apertura de la app (home) | Lista de medicamentos de hoy, filtrada por nivel de compartición | Todos los roles, contenido filtrado por permiso |
| Confirmación de Toma | Móvil | Tap en tarjeta de medicamento | Marcar dosis tomada, hora real | Paciente, Cuidador Principal |
| Centro de Alertas | Móvil | Tab/icono de notificaciones | Historial de escaladas, confirmaciones cruzadas recibidas | Todos los roles con acceso a esa dosis |
| Adherencia (móvil) | Móvil | Tab inferior | Versión ligera del panel de adherencia, mismo dispositivo del día a día | Todos los roles con "Acceso Completo" |
| Gestión de Cuidadores | Móvil | Menú/Configuración | Invitar, ver roles, niveles de compartición (máx. 5) | Paciente (control total), Cuidador Principal (lectura) |
| Testamento Digital de Cuidado | Móvil | Menú/Configuración → Cuidado avanzado | Designar Cuidador de Respaldo, transferencia explícita de control | Paciente; Cuidador de Respaldo solo durante flujo de transferencia activado |
| AdherenceDashboard | Web | Login web (home) | Panel de adherencia histórica con gráficos, rango 7/30 días | Cuidadores a distancia con Acceso Completo |
| CaregiverManagement | Web | Nav web | Misma gestión de cuidadores que móvil, vista de consulta + edición de roles | Paciente, Cuidador Principal |

→ Referencia de composición: `mockups/calendario.html` (Calendario, estados a-tiempo/escalada/última-línea), `mockups/confirmacion-toma.html` (Confirmación de Toma, dosis crítica en dos pasos), `mockups/adherence-dashboard.html` (AdherenceDashboard, layout `≥lg`). Centro de Alertas, Adherencia móvil, Gestión de Cuidadores, Testamento Digital y CaregiverManagement quedan especificadas solo por tabla (sin mock) — decisión registrada en `.decision-log.md`. Spine gana en caso de conflicto con cualquier mock.

Navegación móvil: tabs inferiores (Calendario / Alertas / Adherencia), con Gestión de Cuidadores y Testamento Digital anidados en Configuración (son de baja frecuencia, no merecen un tab). Ningún modal se apila sobre otro modal.

Navegación web: barra lateral simple (Adherencia / Cuidadores), sin más superficies — el panel web es deliberadamente pequeño.

## Voice and Tone

Microcopy. La postura de marca vive en `DESIGN.md → Brand & Style`.

| Hacer | Evitar |
|---|---|
| "Aún no se confirma la toma de las 8am." | "¡Alerta! Medicamento no tomado." |
| "Marta confirmó que tu papá tomó su medicina." | "Notificación: evento de confirmación registrado." |
| "Avisamos a Marta por SMS porque no hubo respuesta." | "Escalando a nivel 2." |
| "Esto no sustituye una llamada a emergencias." (siempre visible, nunca solo en términos legales) | Enterrar la advertencia del Protocolo de Última Línea en letra pequeña |
| Lenguaje llano para consentimiento de datos (Habeas Data) | Texto legal sin traducir a lenguaje cotidiano en la pantalla de invitación |
| Hablarle igual al paciente que al cuidador — sin tono "infantilizado" hacia el paciente | Tono distinto/condescendiente cuando el destinatario es el paciente mismo |

## Component Patterns

Comportamiento. Especificación visual en `DESIGN.md → Components`.

| Componente | Uso | Reglas de comportamiento |
|---|---|---|
| Medication Card | Calendario | Tap abre Confirmación de Toma. Si ya confirmada, tap abre detalle (hora real, quién confirmó). |
| Confirm Dose Button | Confirmación de Toma | Confirmación en dos pasos para dosis críticas (tap → confirmar en diálogo) para evitar toques accidentales en algo que dispara una cadena de notificaciones; un paso para no críticas. |
| Status Chip | Calendario, Centro de Alertas, ambos dashboards | Estado se actualiza en vivo vía SignalR — nunca requiere pull-to-refresh para reflejar una confirmación de otro cuidador. |
| Escalation Banner | Calendario (dosis en escalada) | Visible solo mientras la escalada está activa; desaparece automáticamente al confirmarse la dosis, sin acción manual de "descartar". |
| Last-Line Banner | Calendario + Centro de Alertas | Se dispara solo tras agotar push→SMS→llamada sin respuesta. Incluye botón directo para que el Contacto de Emergencia confirme que ya intervino, lo cual cierra el banner para todos. |
| Caregiver Avatar Row | Calendario (header), Gestión de Cuidadores | Tap en avatar abre el detalle de rol/permiso de esa persona; nunca permite auto-agregarse — invitación siempre explícita. |
| Pattern Alert | Centro de Alertas | Distinta de la alerta puntual: aparece solo tras `[ASSUMPTION] 3 días consecutivos` de incumplimiento — copy explícitamente distingue "esto pasó hoy" de "esto es un patrón". |

## State Patterns

| Estado | Superficie | Tratamiento |
|---|---|---|
| Apertura en frío | Calendario móvil | Muestra calendario de hoy (caché si offline). Si no hay caché, skeleton + "Cargando tu calendario." |
| Calendario vacío | Calendario | "Aún no hay medicamentos en tu calendario." + acción para agregar (solo si el rol tiene permiso). |
| Dosis confirmada por otro | Calendario, en vivo | Status Chip cambia a verde sin recargar; no hay notificación push duplicada para quien ya está viendo la pantalla. |
| Escalada en curso | Calendario, Centro de Alertas | Escalation Banner informativo, tono calmado — ver `Voice and Tone`. |
| Última línea activada | Calendario, Centro de Alertas | Last-Line Banner rojo — único momento donde el producto "alza la voz" visualmente. |
| **Offline (online-only MVP)** | Global | Banner persistente y visible (no un toast que desaparece): "Sin conexión — no podremos confirmar tomas ni avisar a tus cuidadores hasta reconectar." `[ASSUMPTION]` Se prioriza la honestidad sobre la calma visual en este caso específico, dado el riesgo real señalado en el PRD. |
| Permiso limitado | Calendario (rol "solo alertas") | Vista filtrada — no oculta con un mensaje de "bloqueado", simplemente no muestra lo que no le corresponde. |
| Invitación pendiente | Gestión de Cuidadores | Chip "Invitación enviada — esperando aceptación" junto al nombre/teléfono invitado. |
| Transferencia de Testamento Digital pendiente | Testamento Digital (Cuidador de Respaldo) | `[ASSUMPTION]` Mecanismo de aprobación no definido en el PRD — se asume que requiere confirmación explícita del paciente (si tiene capacidad) o de un segundo cuidador, nunca automática por inactividad sola. Pendiente de validar. |
| Error de sincronización | Centro de Alertas | Solo se muestra ahí, nunca bloquea la pantalla de Calendario. |

## Interaction Primitives

- Tap para confirmar dosis no crítica (un paso); tap + confirmar en diálogo para dosis crítica (dos pasos) — la fricción extra es deliberada, no un descuido.
- Pull-to-refresh disponible pero nunca necesario para ver cambios — SignalR ya empuja el estado.
- Deep-link desde notificación push/SMS directo a la dosis específica en el Calendario, no a un home genérico.
- **Prohibido:** swipe-to-dismiss en el Last-Line Banner (debe cerrarse solo por la acción explícita de confirmación, no por accidente), cualquier gesto que pueda confirmar una toma sin una acción deliberada.

## Accessibility Floor

Comportamiento. Contraste visual vive en `DESIGN.md`.

- WCAG 2.2 AA como mínimo en ambas superficies — `[ASSUMPTION]` elevado a obligatorio dado el stakes "regulado" confirmado (audiencia incluye adultos mayores).
- Todo Status Chip combina ícono + texto + color — nunca color solo (daltonismo).
- Objetivos táctiles ≥ 56px en acciones primarias de móvil (ver `DESIGN.md.components.confirm-dose-button`).
- Dynamic Type / escalado de fuente del sistema honrado en el 100% de las pantallas; ninguna pantalla trunca contenido en el tamaño de accesibilidad más grande.
- VoiceOver/TalkBack: cada acción de confirmación anuncia rol + estado ("Botón, Confirmar toma de Losartán 8am"); el banner de última línea se anuncia de inmediato al aparecer (`aria-live`/equivalente nativo asertivo).
- Lenguaje llano obligatorio en pantallas de consentimiento (Habeas Data) — nada de bloques legales sin resumen en español cotidiano antes del texto formal.

## Responsive & Platform

| Breakpoint (web) | Comportamiento |
|---|---|
| `≥ lg` (escritorio) | Layout de dos columnas en AdherenceDashboard: lista de medicamentos + gráfico de adherencia lado a lado. |
| `< lg` (tablet) | Una sola columna, gráfico arriba, lista abajo. |
| Móvil web | `[ASSUMPTION]` No es prioridad — el panel web asume uso desde laptop/escritorio (cuidador a distancia revisando desde el trabajo), no desde el navegador de un teléfono. Debe ser usable pero no es superficie optimizada. |

Móvil nativo (MAUI) sigue convenciones de plataforma para navegación y gestos del sistema — sin patrones custom que compitan con el sistema operativo.

## Inspiration & Anti-patterns

- **Rechazado — Gamificación, rachas, insignias por adherencia:** excluido explícitamente del alcance del PRD (Tema 5, fuera de v1). Tomar la medicina no es un logro que se premia, es un cuidado que se confirma.
- **Rechazado — Iconografía de alarma/sirena para recordatorios rutinarios:** rompe la confianza visual reservada para el Protocolo de Última Línea — ver `DESIGN.md`.
- **Rechazado — Auto-agregar cuidadores o transferencias automáticas del Testamento Digital:** todo cambio de quién ve o controla los datos del paciente requiere consentimiento explícito, nunca un default silencioso (coherente con el énfasis del PRD en autonomía/dignidad del paciente).

## Key Flows

### Flujo 1 — Confirmación cruzada (Marta, hija a distancia, hermanos en otra ciudad) — mirror de UJ-1

1. El padre de Marta toma su medicamento de las 8am.
2. Marta abre la app y ve la tarjeta de "Losartán 8am" en su Calendario.
3. Toca la tarjeta, confirma la toma con un tap (no es dosis crítica).
4. El Status Chip cambia a "A tiempo" en verde.
5. **Climax:** En el teléfono de su hermano, a 400km de distancia, el chip cambia a verde en vivo sin que nadie tenga que escribir "¿ya se la dio?" en el chat familiar — la coordinación informal por WhatsApp deja de ser necesaria.

Falla: si la confirmación falla por error de red, el chip permanece en estado anterior y un error se muestra solo en Centro de Alertas — Marta no ve un falso "confirmado".

### Flujo 2 — Escalada completa (Don Carlos, paciente, no responde) — mirror de UJ-2

1. Don Carlos no confirma su dosis crítica de las 8pm.
2. A los 60 segundos, push a Don Carlos y Escalation Banner aparece en el calendario de sus cuidadores — tono informativo, no alarmante.
3. Sin respuesta tras el intervalo definido, SMS a su Cuidador Principal.
4. Sin respuesta, llamada automatizada.
5. **Climax:** Tras agotar la cadena sin confirmación, el Last-Line Banner rojo se activa y notifica al Contacto de Emergencia por todos los canales — con el mensaje explícito de que esto no sustituye una llamada a emergencias reales.

Falla: Don Carlos sí tomó la medicina pero no tuvo el teléfono a mano — al confirmar tarde, toda la cadena se detiene de inmediato y de forma idempotente, sin que el Contacto de Emergencia reciba un aviso tardío innecesario.

### Flujo 3 — Configuración del círculo de cuidado y Testamento Digital (Don Carlos) — mirror de UJ-3

1. Don Carlos configura su Calendario de Medicación por primera vez.
2. Invita a Marta como Cuidadora Principal y a su hermano como Cuidador "solo alertas" — ambos deben aceptar explícitamente, nunca se auto-agregan.
3. Entra a "Cuidado avanzado" y designa a Marta como Cuidadora de Respaldo en su Testamento Digital de Cuidado.
4. **Climax:** Don Carlos ve confirmado, en una pantalla clara y sin jerga legal, quién podría asumir el control de su cuenta si él pierde capacidad — y sabe que esa transferencia nunca ocurre sola, requiere una confirmación explícita (`[ASSUMPTION]`, ver `State Patterns`).

Falla: si Don Carlos alcanza el límite de 5 cuidadores, el botón de invitar se deshabilita con explicación clara, nunca un error técnico genérico.
