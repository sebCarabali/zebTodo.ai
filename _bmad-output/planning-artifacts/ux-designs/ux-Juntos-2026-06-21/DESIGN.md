---
name: Juntos
description: Juntos — app de coordinación de medicación para círculos de cuidado familiar. Calmada, confiable, sin alarmismo salvo en escalada real.
status: final
sources:
  - "{planning_artifacts}/prds/prd-Juntos-2026-06-19/prd.md"
  - "{planning_artifacts}/architecture.md"
colors:
  primary: '#2F6F62'
  primary-strong: '#1F4F45'
  accent: '#E08D3C'
  surface-base: '#FAF8F4'
  surface-raised: '#FFFFFF'
  ink-primary: '#232323'
  ink-secondary: '#6B6B63'
  ink-disabled: '#AFA9A0'
  border-hairline: '#E5E1D8'
  status-on-time: '#3A8C5F'
  status-late: '#D98E2B'
  status-pattern: '#B5651D'
  status-critical: '#C0392B'
  surface-base-dark: '#1C1E1C'
  surface-raised-dark: '#262924'
  ink-primary-dark: '#F2EFE9'
  ink-secondary-dark: '#A6A199'
typography:
  display:
    note: 'Plataforma nativa — iOS Title 1 / Android Headline Large. Solo para títulos de pantalla, nunca para listas.'
  title:
    note: 'Plataforma nativa — iOS Title 3 / Android Title Large. Nombre de medicamento, encabezados de tarjeta.'
  body:
    note: 'Plataforma nativa — iOS Body / Android Body Large. Texto general, siempre con Dynamic Type / escalado de fuente del sistema activo.'
  meta:
    note: 'Plataforma nativa — iOS Footnote / Android Body Small. Horas, metadatos secundarios, nunca información de estado crítico.'
rounded:
  sm: 8px
  md: 14px
  lg: 20px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  '7': 48px
components:
  medication-card:
    background: '{colors.surface-raised}'
    radius: '{rounded.md}'
    padding: '{spacing.4}'
  confirm-dose-button:
    background: '{colors.primary}'
    radius: '{rounded.full}'
    minHeight: '56px'
  status-chip:
    radius: '{rounded.full}'
    padding: '{spacing.2}'
  escalation-banner:
    radius: '{rounded.md}'
    padding: '{spacing.4}'
  last-line-banner:
    background: '{colors.status-critical}'
    radius: '{rounded.md}'
  caregiver-avatar:
    radius: '{rounded.full}'
    size: '40px'
updated: 2026-06-21
---

> `[ASSUMPTION]` — Marca y tono no estaban definidos en el PRD; el usuario delegó la propuesta a esta sesión de UX. El nombre de marca **Juntos** fue elegido por el usuario en esta misma sesión, entre varias opciones propuestas. Desde 2026-06-21, "Juntos" es también el nombre en código del repositorio (decisión revertida; ver entrada del 2026-06-21 en `.decision-log.md`).

## Brand & Style

Esta es una app que vive en el momento más íntimo y delicado del cuidado familiar — la duda de "¿ya se tomó la pastilla?" — así que su lenguaje visual evita deliberadamente dos extremos: la frialdad clínica de un software de hospital, y el alarmismo de una app de seguridad que grita ante cualquier desviación. La postura es **calidez confiable**: cálida como una conversación familiar, confiable como algo en lo que se puede apoyar una decisión real sobre la salud de alguien.

El color hace casi todo el trabajo de comunicar "todo está en orden" sin necesidad de texto. El rojo se reserva exclusivamente para el momento que de verdad importa — la escalada real o el Protocolo de Última Línea — nunca para recordatorios rutinarios. Nada de iconografía de alarma (sirenas, signos de exclamación grandes) en el uso diario. Las formas son suaves y redondeadas, no angulosas; el espacio respira, no compite por atención con notificaciones constantes.

`[ASSUMPTION]` Esta identidad asume un producto de consumo familiar cálido, no una herramienta clínica profesional — coherente con que el PRD excluye explícitamente clínicas y cuidadores profesionales multi-paciente del v1.

## Colors

- **Verde Salvia (`{colors.primary}` `#2F6F62`)** — color de marca principal. Comunica salud y calma sin caer en el azul clínico de hospital ni en el verde quirúrgico. Se usa en acciones primarias (confirmar toma, invitar cuidador) y en el estado "a tiempo".
- **Terracota Cálida (`{colors.accent}` `#E08D3C`)** — único acento cromático fuera de la paleta de estado. Señala calidez humana: avatares, ilustraciones de bienvenida, momentos de "círculo de cuidado". Nunca se usa para alertas.
- **Crema (`{colors.surface-base}` `#FAF8F4`)** — lienzo base. Ligeramente cálido para evitar la sensación de pantalla de hospital blanco-frío.
- **Paleta de estado** (`status-on-time` verde, `status-late` ámbar, `status-pattern` ámbar-tierra más oscuro, `status-critical` rojo) — escala de severidad deliberadamente progresiva. El rojo (`#C0392B`) está reservado por contrato para: banner del Protocolo de Última Línea y nada más. Usarlo en cualquier otro contexto rompe su poder de señal.
- **Hairline (`#E5E1D8`)** — separador de menor contraste posible que siga siendo legible; usado entre filas de medicamentos, nunca como borde decorativo.

Evitar: azul clínico como color dominante, rojo/naranja saturado para recordatorios rutinarios, degradados, iconografía de cruz médica o estetoscopio (demasiado clínico para un producto familiar).

## Typography

Se honran las convenciones nativas de cada plataforma (iOS / Android en móvil vía MAUI; tipografía de sistema en el panel web Blazor) en lugar de imponer una tipografía de marca — la prioridad es la legibilidad para una audiencia que incluye adultos mayores, no la diferenciación tipográfica. **Dynamic Type / escalado del sistema debe respetarse en todas las pantallas**: ningún control se trunca ni se corta en el tamaño de accesibilidad más grande.

`display` solo para el encabezado de bienvenida y pantallas vacías. `title` para nombres de medicamento y encabezados de tarjeta — es la jerarquía visual más alta que ve un usuario en el día a día. `body` para todo el contenido operativo. `meta` solo para metadatos secundarios (horas, "hace 2 min") — nunca para comunicar un estado de salud o adherencia, que siempre va en `body` o más grande.

## Layout & Spacing

Escala: 4 / 8 / 12 / 16 / 24 / 32 / 48px — más generosa que el promedio de apps de productividad, deliberadamente, porque la audiencia incluye usuarios mayores y la densidad de información compite con su capacidad de atención en momentos de estrés (alguien revisando si su padre tomó la medicina no debería tener que descifrar una tabla densa).

Móvil: una sola columna siempre; márgenes de plataforma (16pt iOS / 16dp Android). Panel web: layout de dos columnas en escritorio (lista + detalle/gráfico de adherencia) que colapsa a una columna en tablet/móvil — ver `EXPERIENCE.md → Responsive & Platform`.

## Elevation & Depth

Elevación mínima y con propósito. Las tarjetas de medicamento (`surface-raised` sobre `surface-base`) se distinguen por tono, no por sombra pesada — coherente con la calma que el producto busca proyectar. La única elevación marcada (sombra visible, no solo tono) es el **banner de escalada/última línea**, que debe sentirse físicamente "por encima" de todo lo demás porque en ese momento sí es lo más importante de la pantalla.

## Shapes

`{rounded.sm}` (8px) para inputs y chips de estado. `{rounded.md}` (14px) para tarjetas de medicamento, banners y diálogos. `{rounded.full}` para el botón de confirmar toma y los avatares de cuidadores — la forma de píldora/círculo refuerza, sin decir nada literal, la idea de "tomar la pastilla" y "círculo de cuidado". Nada angular o cortante en ningún componente interactivo.

## Components

- **Medication Card** (`{components.medication-card}`) — nombre del medicamento en `title`, hora programada en `meta`, chip de estado (`status-chip`) a la derecha. Flag "crítico" se indica con un borde sutil de `{colors.status-critical}` a 2px, nunca con relleno rojo de la tarjeta completa.
- **Confirm Dose Button** (`{components.confirm-dose-button}`) — botón primario, ancho completo, alto mínimo 56px (objetivo táctil generoso para manos menos firmes). Verbo claro: "Confirmar toma", nunca solo un ícono de check sin texto.
- **Status Chip** — combina siempre ícono + texto + color (nunca solo color, por accesibilidad y por daltonismo): "A tiempo" verde, "Tarde" ámbar, "Sin confirmar" ámbar-tierra, "Última línea activada" rojo.
- **Escalation Banner** — aparece en el calendario cuando una dosis crítica entra en escalada. Tono informativo, no alarmista, hasta el último escalón: "Aún no se confirma — avisamos por SMS a Marta." Solo en el Protocolo de Última Línea sube a `last-line-banner` con fondo rojo sólido.
- **Last-Line Banner** (`{components.last-line-banner}`) — único componente que usa `status-critical` como fondo (no solo borde). Incluye siempre, en texto visible (no solo en letra pequeña): que esto no sustituye una llamada a emergencias.
- **Caregiver Avatar Row** — fila horizontal de `caregiver-avatar` (circulares), con un indicador de "en línea/sincronizado" sutil (punto pequeño, no badge llamativo) para reforzar que los datos están en vivo.
- **Adherence Badge/Chart** — vive principalmente en el panel web (`AdherenceDashboard`); usa la misma paleta de estado, nunca colores adicionales fuera de la escala definida.

## Do's and Don'ts

| Hacer | Evitar |
|---|---|
| Reservar `status-critical` (rojo) exclusivamente para el Protocolo de Última Línea | Usar rojo/naranja saturado para recordatorios rutinarios o dosis simplemente tarde |
| Ícono + texto + color en todo indicador de estado | Comunicar estado solo por color |
| Botones de acción con verbo explícito ("Confirmar toma") | Iconos solos sin texto en acciones críticas |
| Objetivos táctiles ≥ 56px en acciones primarias | Controles pequeños o muy juntos pensando solo en cuidadores jóvenes |
| Tono calmado incluso en estados de alerta intermedios | Iconografía de sirena/alarma en el uso diario |
| Honrar Dynamic Type / escalado del sistema en todas las pantallas | Texto fijo que se trunca en accesibilidad |
| Una sola fuente de calidez (terracota) para momentos humanos | Gamificación, rachas, insignias (excluido explícitamente del PRD) |
