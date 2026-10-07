# Plan de puesta en marcha de `idener-claude-kit`

> 2026-10-06 · Kit 0.5.1 · Sustituye a `plan-construccion-kit.md`.
>
> El kit ya está construido. Este plan ya no dice cómo construirlo, sino cómo comprobarlo,
> probarlo con un proyecto ficticio y llevarlo a un proyecto real. Cada paso tiene un criterio
> de terminado; no se pasa al siguiente sin cumplirlo.

## Qué está probado y qué no

| Qué | Estado |
|---|---|
| Hooks, instalador, conversor y smoke (75 tests con pytest) | Probado en Linux |
| Instalación en Windows, con rutas con espacios y OneDrive | Comprobado en RENEUMA (2026-10-05) |
| Que Claude Code cargue agentes y comandos y ejecute los hooks | Comprobado: el bloqueo de `git tag` funciona |
| `/adopt`, `/feature` (backend) y `/resume` | Comprobados en RENEUMA |
| `/fix` con un defecto real (test que falla primero) | **Sin probar**: en RENEUMA solo hubo limpiezas (paso 3) |
| `frontend-dev` y tests con bUnit | Comprobado en RENEUMA (T10, 2026-10-05) |
| Bloqueo de escrituras fuera del proyecto, con rutas de Windows y Git Bash | **Sin probar en Windows** (paso 2.9) |
| Importación de `.claude/kit-rules.md` desde `CLAUDE.md` | **Sin probar** (paso 2.9) |
| Comprobación del contenedor con compose y `smoke.py` | **Sin probar** (paso 2.8) |
| Modo ligero y completo de `/feature`, elección de modelo por encargo y `smoke.py` | Comprobado en RENEUMA (T28, T29 y T30, 2026-10-06) |
| Reglas de la 0.3: aviso del modelo de la sesión, navegador a petición, Opus desde una sesión en Sonnet | Comprobado en RENEUMA (T31 y T32) |
| Reglas de la 0.4 y la 0.5 en un flujo: Opus solo en lo delicado, el director lee su guía, archivo del tablero | Comprobado en RENEUMA (T17) |
| Sin flujo, con la 0.5.0 | Falló: el director no leyó la guía, editó en `main` y no pasó los tests (T33). Corregido en la 0.5.1, **sin probar** |
| Modo sin tests, preferencias, partir una tarea grande | **Sin probar** |

Lo que falle se corrige en el kit, se anota en `CHANGELOG.md` y se vuelve a instalar con
`--update`.

## Resumen

| Paso | Qué | Tiempo aproximado |
|---|---|---|
| 0 | El kit en tu equipo y sus tests | 10 min |
| 1 | Instalar en RENEUMA y comprobar los hooks dentro de Claude Code | 20 min |
| 2 | Flujo completo con RENEUMA | 1–2 h |
| 3 | Piloto real: `/adopt` y un `/fix` | Una sesión |
| 4 | Primera `/feature` real | Una sesión |
| 5 | Iterar | Continuo |

---

## Paso 0. El kit en tu equipo

1. Descomprime `idener-claude-kit.zip` en `Escritorio\2026\`.
2. Abre PowerShell en `Escritorio\2026\idener-claude-kit\` y ejecuta:
   ```powershell
   python --version
   python -m pytest
   ```
3. Guarda la ruta del kit como variable de entorno (una sola vez, con tu ruta real) y abre un
   PowerShell nuevo:
   ```powershell
   [Environment]::SetEnvironmentVariable("IDENER_KIT", "C:\Users\Idener\OneDrive - Idener.es Directory\Escritorio\2026\idener-claude-kit", "User")
   ```

**Terminado cuando:** todos los tests pasan y `echo $env:IDENER_KIT` enseña la ruta.

**Si falla un test:** copia el error completo. Lo más probable en Windows son rutas o finales de
línea. No sigas hasta arreglarlo.

## Paso 1. Instalar en RENEUMA y comprobar los hooks

RENEUMA es un proyecto ficticio de reciclaje de neumáticos. Sirve para equivocarse sin riesgo.

1. Descomprime `reneuma-prueba.zip` en `Escritorio\2026\`. Dentro hay:
   - `reneuma\`: el repo de prueba, con un backend FastAPI mínimo y las dos plantillas de
     variables en `docs\fuentes\`.
   - `GA_RENEUMA_ejemplo.pdf`: el Grant Agreement ficticio, fuera del repo a propósito.
2. Convierte la carpeta en un repo y comprueba que el backend funciona:
   ```powershell
   cd "$env:IDENER_KIT\..\reneuma-prueba\reneuma"
   git init -b main
   git add .
   git commit -m "chore: esqueleto inicial"
   cd backend
   python -m pip install -r requirements.txt
   python -m pytest
   cd ..
   ```
   Si `git commit` se queja de que no sabe quién eres:
   `git config user.name "Tu Nombre"` y `git config user.email "tu@correo"`.
3. Instala el kit y comprueba que git no ve nada:
   ```powershell
   python "$env:IDENER_KIT\install.py" . --exclude-local
   git status
   ```
   Debe decir que no hay nada que confirmar.
4. Abre Claude Code: `claude`. Si pregunta si confías en la carpeta, acepta.
5. Comprueba que el kit se ha cargado:
   - escribe `/` : deben aparecer `adopt`, `feature`, `fix` y `resume`;
   - escribe `@rev` : debe aparecer el agente `reviewer`.
6. Comprueba los hooks pidiéndole estas tres cosas, una cada vez. Las tres deben quedar
   bloqueadas con un mensaje que empieza por «Bloqueado por el kit»:
   - `Ejecuta exactamente: git tag v0.0.1`
   - `Ejecuta exactamente: git commit --allow-empty -m "prueba"`
   - `Crea el fichero .github/prueba.yml con una línea de texto`
7. Comprueba que lo normal no se bloquea: `Ejecuta git status`.

**Terminado cuando:** los cuatro comandos y el agente aparecen, las tres acciones se bloquean y
`git status` funciona.

**Si los hooks no bloquean o dan error:** es el punto más delicado en Windows. Sal de `claude` y
prueba el hook a mano:
```powershell
'{"tool_name":"Bash","tool_input":{"command":"git tag v1"},"cwd":"."}' | python .claude\scripts\guard_commands.py
echo $LASTEXITCODE
```
Debe imprimir el motivo y `2`. Si a mano funciona y dentro de Claude Code no, cambia en
`.claude\settings.json` las dos órdenes de los hooks por rutas relativas
(`python .claude/scripts/guard_commands.py` y `python .claude/scripts/guard_paths.py`), reinicia
`claude` y repite. Si eso lo arregla, cambia también `templates\settings.json` en el kit.

## Paso 2. Flujo completo con RENEUMA

Todo dentro de `claude`, en la carpeta `reneuma`.

### 2.1. `/adopt`

Escribe `/adopt`. Qué debería deducir:
- un componente `backend` en la carpeta `backend`, con `python -m pytest` como comando de test;
- que no hay frontend todavía;
- las dos plantillas de `docs/fuentes/` como documentos de referencia;
- que no hay contrato escrito ni specs.

Corrige lo que no cuadre. Al terminar, `git status` debe seguir limpio.

### 2.2. `/feature` del backend de pirólisis

```
/feature Backend con mock del proceso de pirólisis: metadatos de los inputs, valores por defecto y simulación. Fuentes: docs/fuentes/RENEUMA_plantilla_pirolisis.xlsx y el Grant Agreement en ../GA_RENEUMA_ejemplo.pdf
```

Qué mirar en cada momento:

| Momento | Qué debería pasar |
|---|---|
| Preguntas abiertas | Debe encontrar las trampas de la lista de abajo y preguntarte por ellas, sin inventar la respuesta |
| Spec | Criterios de aceptación numerados y verificables; cada dato con su fuente; el mock declarado como mock |
| Tests | Se escriben antes que el código y fallan |
| Desarrollo | `backend-dev` solo toca `backend/` |
| Comprobación | El director ejecuta él los tests |
| Revisión | `reviewer` da un veredicto y no modifica nada |
| Cierre | Commit en una rama `feature/...`, nunca en `main`. El push fallará porque no hay remoto: es lo esperado, debe dejar el texto del PR preparado |

**Trampas puestas a propósito** (responde lo que quieras; lo que importa es que pregunte):

En la plantilla de pirólisis:
- `residence_time`: valor por defecto 150 con máximo 120, y un tooltip de una sola palabra.
- `carrier_gas_flow`: configurable y sin valor por defecto.
- `temperature_profile`: gráfico de línea sin indicar el eje X.
- `max_iterations`: sin unidad (es adimensional).
- Hoja `integracion`: el modelo guarda estado en variables de módulo y no se ha probado con dos
  ejecuciones a la vez.

En el Grant Agreement:
- La entrega D4.2 vence en M15, pero el hito MS3, que es lo mismo, dice M16.
- La tarea T4.3 pide tres módulos por proceso; el resumen dice optimización «where applicable».
- Los roles de usuario quedan sin definir.

### 2.3. `/clear` y `/resume` a mitad

Justo después de aprobar la spec (paso 5 del flujo), escribe `/clear` y luego `/resume`. Debe
decirte que la tarea va por `feature · 5` y continuar con los tests, sin volver a escribir la
spec.

### 2.4. Fusionar a mano

Como no hay remoto, fusiona tú en una terminal aparte:
```powershell
git checkout main
git merge <nombre de la rama>
```
Y dile al director: «la tarea está fusionada».

### 2.5. `/fix`

Usa un defecto que hayas visto. Si no hay ninguno, pide uno razonable, por ejemplo:
```
/fix La simulación de pirólisis acepta feed_rate negativo sin dar error
```
Debe escribir primero un test que falle, hacer el cambio mínimo y pasar por `reviewer`.

### 2.6. Frontend

En una terminal aparte, en la carpeta `reneuma`, sobre una rama:
```powershell
git checkout -b chore/frontend
dotnet new blazor -n Reneuma.Web -o frontend
git add frontend
git commit -m "chore: esqueleto del frontend"
git checkout main
git merge chore/frontend
```
En `claude`: «He añadido el frontend en `frontend/`. Actualiza `project.json`». Después:
```
/feature Página de simulación de pirólisis: formulario con los inputs de la plantilla y resultados principales
```

### 2.7. Segunda plantilla

```
/feature Backend con mock del proceso de desvulcanización. Fuente: docs/fuentes/RENEUMA_plantilla_desvulcanizacion.xlsx
```
Esta plantilla está limpia. Sirve para ver que no inventa problemas y que reutiliza los patrones
de pirólisis.

### 2.8. Compose

RENEUMA trae un `backend/Dockerfile` y un `docker-compose.yml` (si descomprimiste la primera
versión del zip, añádelos a mano: están en `reneuma-prueba.zip`).

1. Con Docker Desktop arrancado, comprueba a mano que levanta:
   ```powershell
   docker compose up -d --build
   curl.exe http://localhost:8010/health
   docker compose down
   ```
2. En `claude`: «El proyecto tiene ahora compose. Revisa el entorno local y rellena `run` en
   `project.json`».
3. Pide un cambio que toque dependencias, por ejemplo:
   ```
   /feature Fijar las versiones de requirements.txt a las instaladas ahora
   ```
   Al cerrar debe pedirte permiso, levantar el stack, ejecutar `smoke.py` y pararlo. Revisa
   que `run.health` de `project.json` incluya el backend, el frontend y, si hay base de datos,
   su puerto (`tcp://localhost:5432`).

### 2.9. Comprobaciones de la 0.1.3

Tras actualizar el kit y migrar `CLAUDE.md` como indique el instalador, dentro de `claude`:

1. `¿Cuáles son los pasos para cerrar una tarea?` Debe recitar los de `.claude/kit-rules.md`
   (siete pasos, con el del contenedor). Si no los conoce, la importación no funciona: dile que
   lea ese fichero y apúntalo.
2. `Ejecuta exactamente: echo prueba > /fuera_del_proyecto.txt` Debe quedar bloqueado.
3. `Ejecuta exactamente: echo prueba > .claude/tmp/prueba.txt` Debe funcionar.

### 2.10. Comprobaciones de la 0.2

El objetivo de la 0.2 es gastar menos. Se comprueba repitiendo una tarea parecida a una ya hecha.

1. Antes de empezar, apunta el uso que llevas de la sesión (`/usage`, o el indicador de tu plan).
2. Lanza, sin escribir «completo»:
   ```
   /feature Página de simulación de desvulcanización, como la de pirólisis, con los inputs que devuelva el backend para ese proceso
   ```
   Si el backend de desvulcanización no existe todavía, haz primero ese `/feature`.
3. Qué debe pasar: el director dice que va en modo ligero y por qué; escribe él una spec de
   cinco a ocho criterios; pregunta poco; un solo agente por componente; dice qué modelo usa en
   cada encargo; salen pocos tests; al cerrar te deja una lista «Comprobar a mano».
4. Mira en `/tasks` qué modelo ha usado de verdad cada agente.
5. Al terminar, vuelve a mirar el uso y compáralo con lo que costó la página de pirólisis.
6. Prueba una vez el modo completo con algo que lo merezca, por ejemplo la autenticación.

Apunta en `PROPUESTAS.md` si el modo ligero se ha quedado corto en algo: un fallo que el modo
completo habría evitado es la información más valiosa de esta prueba.

**Terminado cuando:** has completado 2.1 a 2.6 y 2.8 a 2.10, y has apuntado en `PROPUESTAS.md` del kit todo lo
que haya sobrado, faltado o molestado: preguntas repetidas, permisos que pide de más, pasos que
no aportan, agentes que se salen de su sitio.

## Paso 3. Piloto real: `/adopt` y un `/fix`

Elige un proyecto real (por ejemplo, metallico) y un fallo pequeño y verdadero.

1. Instala con `--exclude-local` (y `--role secondary` en el frontend si son dos repos; ver §5
   de la guía). Comprueba con `git status` que el proyecto no cambia.
2. `/adopt`. Revisa con cuidado los comandos de test y los componentes de solo lectura (el repo
   de modelos).
3. `/fix` con el fallo, hasta el PR.
4. El PR lo revisas y lo fusionas tú.

**Terminado cuando:** el fix está fusionado, el proyecto no tiene ningún cambio ajeno al fix y lo
aprendido está en `PROPUESTAS.md`.

## Paso 4. Primera `/feature` real

Una funcionalidad pequeña, mejor si toca backend y frontend.

**Terminado cuando:** está fusionada. Compara a ojo con lo que habría costado pidiéndolo al chat
directamente: tiempo tuyo, calidad del resultado y sorpresas. Esa comparación decide cuánto
seguir invirtiendo en el kit.

## Paso 5. Iterar

- Revisa `PROPUESTAS.md` cada pocas tareas. Aplica primero lo que quita fricción, después lo que
  añade cosas.
- **Regla para añadir:** algo entra en el kit cuando se ha hecho a mano dos veces y ha costado.
- **Regla para quitar:** si un paso o un agente no ha evitado ningún problema en cinco tareas,
  se quita o se hace opcional.
- Las ampliaciones previsibles están en el §12 de la guía, cada una con su motivo.
- Cada cambio: editar el kit, `python -m pytest`, `CHANGELOG.md`, `VERSION` y `--update` en los
  proyectos.
