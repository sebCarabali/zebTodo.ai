---
baseline_commit: d30fcaf13bef53d155feb1be285a94233b8de929
---

# Story 1.1: Inicializar la solución del proyecto y el pipeline de CI/CD

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a equipo de desarrollo,
I want tener la solución .NET Aspire + MAUI inicializada y un pipeline de CI/CD funcional,
so that cada historia siguiente se construye, prueba y despliega sobre una base reproducible desde el primer commit.

## Acceptance Criteria

1. **Given** un repositorio vacío del proyecto, **when** se ejecuta `dotnet new aspire-starter --name Juntos --output .` seguido de `dotnet new maui -o Juntos.Mobile -f net10.0` y `dotnet sln add Juntos.Mobile/Juntos.Mobile.csproj`, **then** la solución `Juntos.sln` contiene los proyectos `Juntos.AppHost`, `Juntos.ServiceDefaults`, `Juntos.ApiService`, `Juntos.Web` y `Juntos.Mobile`. [Source: epics.md#Story-1.1]
2. **Given** la solución inicializada, **when** se ejecuta `dotnet run --project Juntos.AppHost`, **then** levanta todos los servicios localmente junto con el Aspire Dashboard mostrando logs/trazas de cada uno. [Source: epics.md#Story-1.1]
3. **Given** la solución inicializada, **when** se configura el pipeline de GitHub Actions, **then** cada push ejecuta build y el proyecto de pruebas xUnit. [Source: epics.md#Story-1.1]
4. **Given** el pipeline configurado, **when** ocurre un push a la rama principal, **then** se ejecuta `azd deploy` hacia Azure Container Apps sin intervención manual. [Source: epics.md#Story-1.1]

## Tasks / Subtasks

- [x] Task 1: Inicializar la solución base con .NET Aspire Starter (AC: #1)
  - [x] Subtask 1.1: En la raíz del repo, ejecutar `dotnet new aspire-starter --name Juntos --output .` — genera `Juntos.sln`, `Juntos.AppHost`, `Juntos.ServiceDefaults`, `Juntos.ApiService`, `Juntos.Web`
  - [x] Subtask 1.2: Verificar que el starter generó su propio `.gitignore` para .NET (bin/, obj/, .vs/) — el repo actualmente no tiene `.gitignore` en la raíz (fue eliminado, ver Dev Notes); confirmar que el generado por el template cubre artefactos de build de los 5 proyectos
  - [x] Subtask 1.3: Confirmar que `azure.yaml` quedó generado en la raíz (lo usará `azd` en Task 4)
- [x] Task 2: Añadir el proyecto Mobile (.NET MAUI) a la solución (AC: #1)
  - [x] Subtask 2.1: Ejecutar `dotnet new maui -o Juntos.Mobile -f net10.0`
  - [x] Subtask 2.2: Ejecutar `dotnet sln add Juntos.Mobile/Juntos.Mobile.csproj`
  - [x] Subtask 2.3: Verificar que `Juntos.Mobile` aparece listado en `dotnet sln Juntos.sln list`
- [x] Task 3: Verificar arranque local orquestado por Aspire (AC: #2)
  - [x] Subtask 3.1: Ejecutar `dotnet run --project Juntos.AppHost`
  - [x] Subtask 3.2: Confirmar que el Aspire Dashboard se abre (URL local mostrada en consola) y expone logs/trazas de `Juntos.ApiService` y `Juntos.Web` corriendo
- [x] Task 4: Crear el proyecto de pruebas xUnit y el job de CI (build + test en cada push) (AC: #3)
  - [x] Subtask 4.1: Confirmar/crear `Juntos.Tests` (xUnit) con referencia a `Juntos.AppHost` para soportar pruebas de integración vía `DistributedApplicationTestingBuilder` (decisión de Architecture.md, no implementar pruebas reales aún — solo el proyecto vacío con la referencia)
  - [x] Subtask 4.2: `dotnet sln add Juntos.Tests/Juntos.Tests.csproj`
  - [x] Subtask 4.3: Crear `.github/workflows/ci-cd.yml` con un job `build-and-test` que se dispare en `push` (todas las ramas) y `pull_request`: `actions/checkout`, `actions/setup-dotnet` (channel `10.0.x`), `dotnet restore`, `dotnet build --no-restore`, `dotnet test --no-build`
- [ ] Task 5: Configurar el despliegue automático a Azure Container Apps en push a `main` (AC: #4)
  - [ ] Subtask 5.1: Ejecutar `azd pipeline config` localmente (requiere Azure Developer CLI instalado y sesión `az login`/`azd auth login` activa) — selecciona proveedor **GitHub**, autenticación **OIDC/federated credentials** (default), y permite que `azd` cree los secrets/variables del repo automáticamente: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ENV_NAME`, `AZURE_LOCATION`
  - [ ] Subtask 5.2: Revisar el workflow que `azd pipeline config` agrega/actualiza en `.github/workflows/azure-dev.yml` (o fusionar su job `deploy` dentro de `ci-cd.yml` si se prefiere un solo archivo) — debe instalar `azd` vía `Azure/setup-azd@v1.0.0` (confirmar última versión en https://github.com/Azure/setup-azd/releases antes de fijar el tag) y ejecutar `azd deploy`
  - [ ] Subtask 5.3: Condicionar el job de deploy a `github.ref == 'refs/heads/main'` y a que dependa (`needs:`) del job `build-and-test` de Task 4 — un push a una rama distinta de `main` nunca debe disparar `azd deploy`
  - [ ] Subtask 5.4: Hacer un push de prueba a una rama feature (debe correr solo build+test) y luego a `main` (debe correr build+test y luego `azd deploy`) para validar el AC #4 end-to-end

## Dev Notes

### Contexto crítico de esta historia

- Esta es la **primera historia de implementación del proyecto completo** — no existe código de aplicación todavía (el repo solo tiene el framework BMad y documentación en `_bmad-output/`, `_bmad/`, `docs/`). No hay historia previa de la cual aprender ni patrones de código establecidos que seguir; esta historia es la que los establece.
- **Alcance estricto:** esta historia es únicamente scaffolding de solución + pipeline CI/CD. NO crear todavía: modelo EF Core/`JuntosDbContext`, ASP.NET Core Identity, carpetas de feature (`MedicationCalendar/`, `CaregiverManagement/`, etc.), SignalR hubs, ni `Juntos.EscalationWorker`. Esos llegan en historias 1.2+ según el Implementation Sequence de Architecture.md (`_bmad-output/planning-artifacts/architecture.md` líneas 189-196). Crear esas piezas ahora sería adelantarse y arriesga que la historia 1.2 (que sí las requiere con contexto de Identity/permisos) las reconstruya de forma inconsistente.
- El comando de inicialización está fijado textualmente en Architecture.md (líneas 92-99, 640-645) y en epics.md (Story 1.1) — no improvisar variantes (ej. no usar `aspire new`, el nuevo CLI de Aspire 13, aunque exista como alternativa válida en general; la decisión arquitectónica ya fijó `dotnet new aspire-starter`).

### Requisitos técnicos (Architecture.md)

- **Stack:** .NET 10 end-to-end (LTS hasta nov. 2028), .NET Aspire 13, ASP.NET Core 10, .NET MAUI 10. [Source: architecture.md líneas 73, 552]
- **Aspire 13 ya NO requiere `dotnet workload install aspire`** — el workload fue descontinuado desde Aspire 9; el starter trae las referencias NuGet necesarias. No agregar ese paso al pipeline ni a instrucciones de setup local. (Verificado vía búsqueda web durante la creación de esta historia, junio 2026 — Aspire.Hosting/Aspire.Cli 13.x en NuGet.)
- **Estructura de proyectos esperada tras esta historia** (subset de la estructura completa en architecture.md líneas 334-492, que se llenará en historias posteriores):
  ```
  Juntos/
  ├── Juntos.sln
  ├── azure.yaml
  ├── .gitignore
  ├── .github/workflows/ci-cd.yml      (y/o azure-dev.yml generado por azd pipeline config)
  ├── Juntos.AppHost/
  ├── Juntos.ServiceDefaults/
  ├── Juntos.ApiService/              (vacío salvo lo que trae el starter; Program.cs base)
  ├── Juntos.Web/                     (Blazor, vacío salvo lo que trae el starter)
  ├── Juntos.Mobile/                  (MAUI, agregado manualmente en Task 2)
  └── Juntos.Tests/                   (xUnit, referencia a AppHost)
  ```
- **CI/CD (architecture.md líneas 180-186, 340-343, 546):** GitHub Actions integrado con `azd`, build/deploy de `AppHost`, `ApiService`, `EscalationWorker` (aún no existe — se agrega en Epic 4), `Web` y `Mobile`; despliegue a Azure Container Apps; `EscalationWorker` debe poder escalar independientemente del resto — esto no se configura todavía en esta historia (no existe el worker aún) pero el pipeline debe quedar estructurado para no requerir un rediseño cuando se agregue.
- **Observabilidad:** OpenTelemetry vía `ServiceDefaults` → Azure Monitor/Application Insights ya viene de fábrica con el starter Aspire; no requiere configuración manual adicional en esta historia.

### Pipeline de GitHub Actions — detalles de implementación

- `azd pipeline config` es el mecanismo recomendado por Microsoft para generar el job de deploy: configura automáticamente OIDC/federated credentials entre GitHub y Azure (no expone client secrets en texto plano) y crea los GitHub Actions secrets/variables necesarios (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ENV_NAME`, `AZURE_LOCATION`). Requiere que el desarrollador tenga `az`/`azd` autenticados localmente — este paso no puede ejecutarse de forma 100% no interactiva desde un agente de IA sin credenciales de Azure; el Dev Agent debe dejar el workflow YAML correctamente armado y documentar el comando exacto a correr, pero la ejecución real de `azd pipeline config` (que crea secrets en GitHub) requiere que un humano con acceso a la suscripción de Azure la ejecute.
- Acción de GitHub recomendada para instalar `azd` en el runner: `Azure/setup-azd@v1.0.0` (verificar tag más reciente en el momento de implementar).
- Separar claramente dos responsabilidades en `ci-cd.yml` (o en dos archivos): (a) `build-and-test` — corre en todo push/PR, no requiere credenciales de Azure; (b) `deploy` — corre solo en push a `main`, requiere `needs: build-and-test` y las credenciales OIDC.
- Ningún secret de Azure debe quedar hardcodeado en el YAML — todo vía `${{ secrets.* }}` / `${{ vars.* }}` que `azd pipeline config` provisiona.

### Project Structure Notes

- Alineado con la estructura unificada de `architecture.md` — esta historia solo crea el "esqueleto" de proyectos y el pipeline; el contenido de dominio de cada proyecto (`ApiService`, `Web`, `Mobile`) llega en historias posteriores.
- No se detectaron conflictos: el repo está vacío de código de aplicación, por lo que no hay riesgo de colisión con trabajo existente.
- Nota sobre estado del repo: `git status` muestra `.gitignore` como eliminado (`D .gitignore`) en el working tree al momento de crear esta historia — probablemente un `.gitignore` genérico previo que será reemplazado por el que genera `dotnet new aspire-starter`. El Dev Agent debe confirmar con el usuario o revisar el historial antes de descartar ese cambio si no está seguro de su origen.

### Testing Requirements

- Proyecto `Juntos.Tests` (xUnit) creado en esta historia pero sin pruebas de negocio todavía (no hay lógica de dominio que probar). Debe incluir referencia a `Juntos.AppHost` para habilitar `DistributedApplicationTestingBuilder` en historias futuras (architecture.md líneas 112-113, 538).
- El AC #3 solo exige que el job de CI ejecute build + el proyecto de pruebas xUnit (aunque esté vacío de tests reales) — el job debe pasar en verde con 0 tests ejecutados, eso es válido para esta historia.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1: Inicializar la solución del proyecto y el pipeline de CI/CD] (líneas 187-203)
- [Source: _bmad-output/planning-artifacts/architecture.md#Selected Starter: .NET Aspire Starter Application + .NET MAUI] (líneas 86-125)
- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure & Deployment] (líneas 180-186)
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision Impact Analysis / Implementation Sequence] (líneas 187-199)
- [Source: _bmad-output/planning-artifacts/architecture.md#Complete Project Directory Structure] (líneas 334-492)
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Handoff] (líneas 635-645)
- Aspire 13 / workload deprecation y `Azure/setup-azd` action: verificado vía búsqueda web (junio 2026) contra learn.microsoft.com/azure/developer/azure-developer-cli/pipeline-github-actions y aspire.dev/whats-new/upgrade-aspire — no hay fuente interna en el repo para este dato, es información externa vigente al momento de creación de esta historia.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Tasks 1-2: `Aspire.ProjectTemplates@13.4.6` (instalado en esta historia, no preinstalado en el SDK) ya **no** genera `azure.yaml` ni `.gitignore` como parte de `dotnet new aspire-starter` — en su lugar genera `aspire.config.json` (manifiesto de Aspire CLI). Se instaló `azd` (vía winget) y se ejecutó `azd init --from-code -e dev --no-prompt` para generar `azure.yaml` correctamente (luego se corrigió el campo `name:` de "zeb-todo" a "juntos", ya que `azd` lo derivó del nombre del directorio del repo). El `.gitignore` que genera `azd init` solo contiene `.azure` (no cubre `bin/`/`obj/`/`.vs/`), por lo que se generó el `.gitignore` estándar de .NET con `dotnet new gitignore` y se le añadió la entrada `.azure` al final.
- Task 2: El paquete `Microsoft.Maui.Templates` distribuido en NuGet (6.0.300-rc.3) está desactualizado y solo soporta hasta `net6.0` (no acepta `-f net10.0`). Se desinstaló ese paquete y se instaló el workload oficial `dotnet workload install maui`, que trae las plantillas MAUI alineadas con el SDK .NET 10 instalado y sí soporta `-f net10.0`.
- Task 2 (build local): `dotnet build Juntos.sln` falló inicialmente solo para el TFM `net10.0-android` de `Juntos.Mobile` por falta del SDK de Android nivel API 36 en la máquina local (`XA5207`). Se resolvió ejecutando `dotnet build -t:InstallAndroidDependencies -f net10.0-android` sobre `Juntos.Mobile.csproj`, tras lo cual la solución completa compila en limpio en los 5 proyectos. Es una dependencia del entorno local de desarrollo, no del código del repo.
- Task 3: En el primer arranque, `webfrontend` (Blazor) nunca llegaba a iniciar su proceso bajo la orquestación de `Juntos.AppHost` (timeout al consultar su endpoint) porque su `WaitFor(apiService)` depende del health-check HTTPS de `apiservice`, y el certificado de desarrollo HTTPS no estaba marcado como de confianza en la máquina (warning "No trusted Aspire development certificate was found"). Se ejecutó `dotnet dev-certs https --trust` y se reinició el AppHost; tras esto ambos servicios (`apiservice` puerto 7432, `webfrontend` puerto 7249) y el Aspire Dashboard (puerto 17173) respondieron correctamente y los 3 procesos (`Juntos.AppHost`, `Juntos.ApiService`, `Juntos.Web`) quedaron confirmados corriendo simultáneamente. Cualquier desarrollador que clone el repo deberá ejecutar `dotnet dev-certs https --trust` una vez en su máquina (paso estándar de cualquier proyecto ASP.NET Core con HTTPS local, no específico de esta historia).
- Task 4: Se eliminó el `UnitTest1.cs` placeholder que genera por defecto la plantilla `xunit` (un `[Fact]` vacío), para que el proyecto quede sin pruebas reales tal como exige el Dev Notes ("sin pruebas de negocio todavía"). Se confirmó que `dotnet test` sobre el proyecto vacío termina con exit code 0 ("No hay ninguna prueba disponible..." es solo un mensaje informativo, no una falla).
- Task 4 (decisión de diseño de CI): el job `build-and-test` de `ci-cd.yml` ejecuta `dotnet restore/build/test` apuntando a `Juntos.Tests/Juntos.Tests.csproj` (no a `Juntos.sln`). `Juntos.Tests` referencia `Juntos.AppHost`, que a su vez referencia `Juntos.ApiService` y `Juntos.Web` — por lo tanto este único comando ya restaura/compila/prueba esos 4 proyectos transitivamente, cumpliendo el AC #3 ("build y el proyecto de pruebas xUnit"). Se excluyó deliberadamente `Juntos.Mobile` (no es una dependencia de `Juntos.Tests`) porque sus 4 target frameworks (`net10.0-android/ios/maccatalyst/windows10.0`) requieren workloads de MAUI + SDK de Android (nivel API 36) + tooling de Mac/Windows que no están provisionados en el runner `ubuntu-latest` por defecto; provisionar ese tooling en CI es trabajo fuera del alcance de esta historia (que es solo scaffolding) y debería abordarse en una historia dedicada a CI/CD de Mobile.
- Task 5: Se confirmó (verificación en GitHub vía `gh release list`) que la versión más reciente de `Azure/setup-azd` al momento de implementar es `v2.3.0` (tag móvil `v2`), no `v1.0.0` como sugería el Dev Notes original — se fijó `Azure/setup-azd@v2` en el workflow. También se fijaron `actions/checkout@v7` y `actions/setup-dotnet@v5` (últimas versiones mayores verificadas de la misma forma).
- Task 5: El job `deploy` quedó armado en `.github/workflows/ci-cd.yml` (fusionado en el mismo archivo que `build-and-test`, condicionado a `github.ref == 'refs/heads/main'` y `needs: build-and-test`) pero **no puede ejecutarse exitosamente todavía**: requiere que un humano con acceso a la suscripción de Azure ejecute `azd auth login` + `azd pipeline config` desde su máquina (ver Subtask 5.1) para crear los secrets/variables de GitHub (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` como secrets; `AZURE_ENV_NAME`, `AZURE_LOCATION` como variables) que el job consume vía `${{ secrets.* }}`/`${{ vars.* }}`. Sin esos valores, el job `deploy` fallará en el primer push a `main` hasta que se complete ese paso manual.

### File List
