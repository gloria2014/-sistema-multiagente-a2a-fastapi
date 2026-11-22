# Guía Paso a Paso de Evaluación Local (Para el Equipo Docente)

Esta guía rápida permite instalar, levantar todo el ecosistema multi-agente A2A en **una sola terminal** y comprobar los casos de evaluación en menos de 3 minutos.

> **Dónde están las evidencias visuales:** Las 5 capturas de pantalla de nuestra ejecución local están en la carpeta **[`evidencias/`](evidencias/)** (`01_acceso_rechazado.png` a `05_datos_faltantes_y_limites.png`) y explicadas con sus tablas en la sección 8 del [`README.md`](README.md).

---

## Paso 1: Preparar el entorno virtual e instalar dependencias

Abra una terminal en la carpeta raíz del proyecto:

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**En Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Paso 2: Configurar la clave de Gemini y el Token de acceso (`.env`)

1. Copie el archivo `.env.example` a `.env`:
   - **Windows:** `copy .env.example .env`
   - **Mac / Linux:** `cp .env.example .env`
2. Abra el archivo `.env` y pegue su clave de API de Google Gemini en `GOOGLE_API_KEY`:
   ```env
   GOOGLE_API_KEY=su_clave_gemini_aqui
   MODELO=gemini-2.5-flash
   TOKEN_ACCESO=token-secreto-ejemplo-123
   ```
   *(El `TOKEN_ACCESO` ya viene configurado con `token-secreto-ejemplo-123` para que pueda usarlo directamente en las pruebas).*

---

## Paso 3: Iniciar todos los componentes (Opción recomendada: 1 sola terminal)

Con el entorno virtual activado, ejecute este único comando:

```bash
python scripts/iniciar_nube.py
```

**¿Qué hace este comando automáticamente?**
1. Levanta el **Agente Pastelero** en `http://127.0.0.1:8002`
2. Levanta el **Agente de Música Ochentera** en `http://127.0.0.1:8003`
3. Levanta el **Agente Innovación** en `http://127.0.0.1:8004`
4. Levanta el **Coordinador A2A** en `http://127.0.0.1:8007` (que descubre las fichas A2A de los 3 agentes)
5. Levanta el **Servicio FastAPI Protegido + Canal Web de Chat** en **`http://127.0.0.1:8000`**

*(En esa misma terminal verá en vivo todos los registros de control de acceso y comunicación A2A).*

---

## Paso 4: Comprobar el recorrido completo (Pruebas para copiar y pegar)

Puede probar desde el **Canal Web** (`http://127.0.0.1:8000`), desde **Swagger FastAPI** (`http://127.0.0.1:8000/docs`) o con el **script automático**:

### A. Prueba interactiva en el Canal Web (`http://127.0.0.1:8000`)

1. Abra **`http://127.0.0.1:8000`** en su navegador.
2. **Prueba 1 — Acceso Rechazado (Seguridad):**
   - Deje vacío el campo *Token de acceso* (o escriba una clave incorrecta) y haga clic en **"Verificar acceso"**.
   - **Resultado:** Verá en rojo **`Acceso rechazado (401)`** y en la terminal el log `[ACCESO RECHAZADO]`.
3. **Prueba 2 — Acceso Autorizado y Catálogo A2A:**
   - Ingrese en el campo *Token de acceso* el valor de `.env`:
     ```text
     token-secreto-ejemplo-123
     ```
   - Haga clic en **"Verificar acceso"**.
   - **Resultado:** Cambiará a verde **`Acceso autorizado (200)`** y se cargarán a la izquierda las tarjetas de los 3 agentes descubiertos por protocolo A2A.
4. **Prueba 3 — Colaboración Multi-Agente A2A y Fidelidad de Conclusión:**
   - Copie y envíe en el chat esta consulta que involucra a los **3 agentes**:
     ```text
     Organizo un taller para 16 porciones: necesito escalar la receta de brownie a 16 porciones, 2 canciones de synth-pop de los años 80 y una técnica de ideación en fase de divergencia.
     ```
   - **Resultado:** El Coordinador consultará por A2A a `Agente pastelero`, `Agente de música ochentera` y `Agente Innovacion`, devolviendo los aportes de cada uno y la `[Conclusión integrada del Coordinador]` conservando el factor `2.00` (base 8 porciones), gramos exactos (`400 g chocolate`, `300 g mantequilla`, `6 huevos`, etc.), `175 °C`, canciones de Depeche Mode (`1981` y `1984`) y técnicas de divergencia (*Crazy Eights*, *SCAMPER*, *Brainwriting*).
5. **Prueba 4 — Solicitud de Datos Faltantes antes de calcular:**
   - Copie y envíe en el chat:
     ```text
     Escala la receta de brownie por favor
     ```
   - **Resultado:** Como no se indicó el número de porciones, el Coordinador no inventa una cifra y responde con `Estado: datos_faltantes` solicitando para cuántas porciones o personas se desea preparar.
6. **Prueba 5 — Límites de los agentes (Consulta fuera de alcance):**
   - Copie y envíe en el chat:
     ```text
     ¿Cuál es el pronóstico del clima en Tokio?
     ```
   - **Resultado:** Informa claramente con `Estado: fuera_de_alcance` que no tiene un agente para ese tema e indica las especialidades disponibles.

---

### B. Prueba directa sobre el Servicio FastAPI (`/docs` o script automático)

- **Desde Swagger UI (`http://127.0.0.1:8000/docs`):**
  1. Haga clic en el botón verde **"Authorize"** (arriba a la derecha) e ingrese `token-secreto-ejemplo-123`.
  2. Pruebe los endpoints protegidos **`GET /agentes`** y **`POST /api/consultar`**.
- **Con el script automático de verificación (en otra terminal con `.venv` activado):**
  ```bash
  python scripts/probar_entrega.py
  ```
  *(Ejecuta automáticamente los 5 casos contra la API y muestra en consola las tablas de resultados).*

---

## Paso 5: Cómo detener todos los componentes

En la terminal donde ejecutó `python scripts/iniciar_nube.py`, presione **`Ctrl + C`**. El script cerrará limpiamente el Servicio FastAPI, el Coordinador y los 3 agentes A2A, liberando todos los puertos.
