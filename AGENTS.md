# Reglas del proyecto

Estas reglas aplican a todo lo que se genere de aquí en adelante en este repositorio.

1. **Todo en español.** Nombres de archivos, variables, funciones, comentarios y mensajes al usuario.
2. **Las funciones que usan internet son `async`.** Cualquier función que haga una petición HTTP o consulte un servicio externo se declara con `async def`.
3. **Toda llamada por red tiene un timeout explícito.** Ninguna petición puede quedar esperando para siempre; siempre se indica un `timeout` en segundos.
4. **Si algo no responde, el error se muestra en una sola línea entendible, sin stack trace.** Se captura la excepción y se informa qué falló y dónde, en lenguaje claro.
5. **Contrato de los agentes.** Cada agente cumple dos cosas:
   - Expone una función `responder(texto, context_id)` que devuelve un texto. Es el contrato que todos cumplen.
   - Se puede correr desde la terminal sin servidor, igual que en el Curso 1: `python main.py {agente} "pregunta"`. Con `--saltos` muestra por qué nodos y herramientas pasó; con `--diagrama` imprime su estructura en Mermaid sin ejecutarlo.
