# Qué se prueba

Depende de la preferencia `tests` del proyecto y de lo que pida el usuario en el encargo.

## `critical` (por defecto): lo crítico, no todo
Un test por criterio no es la regla.

| Qué | Tests automáticos |
|---|---|
| Cada ruta del backend | El caso normal, un error de validación con su campo y la forma de la respuesta (nombres de campos) |
| Integración de un modelo científico real | Conversión de unidades, valores por defecto y aislamiento entre dos peticiones seguidas con configuraciones distintas |
| Seguridad | Sin sesión se rechaza; con un rol que no corresponde se rechaza |
| Cada pantalla del frontend | Como mucho dos o tres, de lo que ya ha fallado o es fácil que falle: un error 422 en su campo, decimales con coma, la llamada al backend con los datos correctos |
| Un fix | El test que reproduce el defecto |

- No se escriben tests de etiquetas, textos, atributos, menús, tipos de control ni casos
  exóticos (NaN, precisión extrema), salvo que la spec lo pida.
- No montes infraestructura de tests nueva si la que existe sirve.
- La conectividad (frontend, backend, base de datos) no se prueba con tests unitarios: se
  comprueba con el stack levantado y `python .claude/scripts/smoke.py`.
- Lo demás va a la lista "Comprobar a mano" del PR.

## `none`, o "sin tests" en el encargo
- No se escriben tests nuevos y no se lanza test-writer. Los criterios de la spec se marcan
  como "manual".
- Los tests que ya existen en los componentes tocados se siguen ejecutando al cerrar, y si
  alguno falla se arregla el código, no el test.
- El PR lo dice: "Sin tests nuevos, a petición".
- En un /fix, el test que reproduce el defecto se escribe igualmente, salvo que el usuario lo
  excluya de forma expresa.
- Si la tarea toca seguridad o un modelo real, el director avisa una vez del riesgo antes de
  seguir; si el usuario lo confirma, se hace sin tests.

## `full`
Un test por criterio de aceptación marcado como "test", además de lo de `critical`.

## Qué tests se ejecutan
- Mientras trabaja, cada agente ejecuta los tests de su componente.
- Al cerrar, el director ejecuta los de los componentes tocados (`close_tests: touched`) o los
  de todos (`all`). Un cambio solo de frontend no necesita pasar los tests del backend.
