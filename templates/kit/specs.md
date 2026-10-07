# Cómo se escribe una spec

Plantilla: .claude/templates/spec.md, o el formato que ya use el proyecto.

- Entre cinco y el tope `max_criteria` (ocho por defecto) criterios de aceptación en una tarea
  normal, numerados (CA-01...), verificables, en formato Dado/Cuando/Entonces.
- Un criterio es un comportamiento que al usuario le importaría que fallara: el caso normal,
  los errores que el usuario ve y las reglas de negocio. Uno por comportamiento, no uno por
  campo ni por texto.
- Cada criterio dice cómo se comprueba: test, smoke o manual, según .claude/kit/pruebas.md.
- Los detalles (tipos de control, textos, orden de campos, qué pasa con entradas vacías o mal
  escritas, qué se borra al repetir) se deciden y van a "Notas de implementación". No son
  criterios ni generan tests.
- No son criterios la revisión de código, el build ni que los tests pasen.
- Pregunta solo lo que cambia el resultado o toca la API. En lo demás elige la opción razonable
  y anótala en las notas con su motivo.
- Cada dato lleva su fuente. Si una fuente no se ha podido leer, dilo; no la des por leída.
- Si la spec añade o cambia rutas, campos o errores de la API, va en "Impacto en la API".
- La spec cabe en una pantalla de lectura.
- Tamaño: el número de criterios no mide el trabajo. Si la tarea necesita más de tres encargos
  de desarrollo, o una pantalla nueva y un servicio nuevo a la vez, propón partirla.
