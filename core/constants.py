"""Constants, demo data, standardized benchmark, and chaos engineering definitions."""

# ── Demo Knowledge Base (Benchmark Estandarizado) ───────────────────────────
# Documentos de una empresa ficticia "TechCorp" que cubren seguridad,
# acceso, datos personales, teletrabajo e incidentes.
# Incluyen versiones vigentes/obsoletas, excepciones, referencias cruzadas
# y datos numericos concretos para evaluar precision del modelo.

KB_DEMO: dict[str, str] = {
    "SEC-001": (
        "Politica de Contrasenas v1 (Enero 2023): Las contrasenas de todos los empleados "
        "deben rotarse cada 90 dias. Longitud minima de 8 caracteres. Se permite reutilizar "
        "contrasenas anteriores despues de 3 ciclos. No se requiere autenticacion multifactor. "
        "Aplica a todos los sistemas internos. [DESACTUALIZADO]"
    ),
    "SEC-002": (
        "Politica de Contrasenas v2 (Febrero 2025): Las contrasenas deben rotarse cada 60 dias. "
        "Longitud minima de 12 caracteres, incluyendo al menos 1 mayuscula, 1 numero y 1 simbolo. "
        "Prohibido reutilizar las ultimas 10 contrasenas. Autenticacion multifactor (MFA) obligatoria "
        "para todos los empleados. Los contratistas externos tienen un ciclo de rotacion de 30 dias. "
        "Excepcion: cuentas de servicio automatizadas se excluyen del MFA pero requieren rotacion "
        "cada 15 dias y aprobacion del CISO. Referencia: ver SEC-005 para procedimiento de "
        "restablecimiento. [VIGENTE]"
    ),
    "SEC-003": (
        "Politica de Control de Acceso (Marzo 2024): El acceso a sistemas criticos requiere "
        "aprobacion del jefe directo y del area de seguridad (doble aprobacion). Bloqueo automatico "
        "de cuenta tras 5 intentos fallidos consecutivos en un periodo de 15 minutos. El desbloqueo "
        "debe solicitarse al Help Desk con verificacion de identidad (pregunta de seguridad + "
        "confirmacion por correo corporativo). Los permisos de acceso se revisan trimestralmente. "
        "Usuarios inactivos por mas de 45 dias son desactivados automaticamente. Prohibido compartir "
        "credenciales bajo cualquier circunstancia; la violacion resulta en sancion disciplinaria "
        "segun el Codigo de Conducta CC-012. [VIGENTE]"
    ),
    "SEC-004": (
        "Politica de Proteccion de Datos Personales (Junio 2024): Toda informacion personal "
        "identificable (PII) debe almacenarse cifrada en reposo (AES-256) y en transito (TLS 1.3). "
        "Los datos de clientes se retienen por un maximo de 5 anos despues de la ultima interaccion. "
        "Los datos de empleados se retienen por 3 anos despues de la fecha de desvinculacion. "
        "Las solicitudes de eliminacion de datos (derecho al olvido) deben procesarse en un plazo "
        "maximo de 30 dias calendario. El acceso a bases de datos con PII requiere nivel de "
        "autorizacion 3 o superior y registro en el log de auditoria. Incumplimiento puede resultar "
        "en multas de hasta 200 salarios minimos segun la Ley 1581 de 2012. El DPO (Data Protection "
        "Officer) es la Dra. Maria Torres (maria.torres@techcorp.co). [VIGENTE]"
    ),
    "SEC-005": (
        "Procedimiento de Restablecimiento de Contrasena (Febrero 2025): Paso 1: El usuario "
        "solicita restablecimiento via portal de autoservicio o llamada al Help Desk (ext. 4500). "
        "Paso 2: Verificacion de identidad mediante MFA o, si MFA no esta disponible, verificacion "
        "con 3 preguntas de seguridad. Paso 3: Se genera una contrasena temporal valida por 24 horas. "
        "Paso 4: El usuario debe cambiar la contrasena temporal en su primer inicio de sesion. "
        "Nota: si se sospecha compromiso de la cuenta, se debe escalar al equipo de Respuesta a "
        "Incidentes (ver INC-001) antes de restablecer. Tiempo maximo de respuesta del Help Desk: "
        "30 minutos en horario laboral (8:00-18:00 L-V), 2 horas fuera de horario. [VIGENTE]"
    ),
    "INC-001": (
        "Protocolo de Respuesta a Incidentes de Seguridad (Agosto 2024): Los incidentes se "
        "clasifican en 3 niveles. Nivel 1 (Critico): brecha de datos confirmada, ransomware, "
        "acceso no autorizado a sistemas criticos. Tiempo de reporte: inmediato (maximo 15 minutos). "
        "Notificar al CISO, al DPO y al Comite de Crisis. Nivel 2 (Alto): intentos de phishing "
        "exitosos, malware detectado, filtracion potencial. Tiempo de reporte: maximo 2 horas. "
        "Notificar al CISO y al jefe de area. Nivel 3 (Medio): intentos de acceso fallidos "
        "sospechosos, vulnerabilidades detectadas en escaneo. Tiempo de reporte: maximo 24 horas. "
        "Notificar al equipo de seguridad. Todos los incidentes deben documentarse en el sistema "
        "JIRA proyecto SEC-INCIDENTS. La autoridad nacional de proteccion de datos debe ser "
        "notificada en maximo 72 horas para incidentes Nivel 1 que involucren PII "
        "(segun Ley 1581 Art. 17). [VIGENTE]"
    ),
    "TW-001": (
        "Politica de Teletrabajo y Acceso Remoto (Enero 2025): El acceso remoto requiere "
        "conexion VPN corporativa (Cisco AnyConnect) con MFA activo. Prohibido el uso de redes "
        "WiFi publicas sin VPN. Los equipos personales deben cumplir los requisitos minimos de "
        "seguridad: antivirus actualizado, sistema operativo con parches al dia, disco cifrado. "
        "El horario de acceso remoto a sistemas criticos esta restringido de 6:00 a 22:00 hora "
        "local, excepto para el equipo de operaciones (24/7 con aprobacion del gerente). "
        "Las sesiones VPN inactivas se desconectan automaticamente tras 30 minutos. "
        "Maximo 3 dispositivos registrados por empleado. Referencia: los requisitos de "
        "contrasena aplican segun SEC-002. [VIGENTE]"
    ),
}

# ── Preguntas del Benchmark Estandarizado ───────────────────────────────────
# Bateria de preguntas organizadas por nivel de dificultad.
# Cada pregunta tiene: texto, nivel, que aspecto evalua, y la respuesta esperada
# (para que el juez pueda comparar).

BENCHMARK_QUESTIONS: list[dict] = [
    # ── Nivel 1: Recall directo (dato puntual de un doc) ─────────────
    {
        "id": "Q01",
        "pregunta": "Cada cuantos dias deben rotar las contrasenas los empleados?",
        "nivel": "Basico",
        "categoria": "Recall directo",
        "doc_clave": "SEC-002",
        "respuesta_esperada": (
            "Cada 60 dias segun SEC-002 (vigente). Los contratistas externos "
            "cada 30 dias. Las cuentas de servicio cada 15 dias."
        ),
    },
    {
        "id": "Q02",
        "pregunta": "Cual es la longitud minima de contrasena y que caracteres debe incluir?",
        "nivel": "Basico",
        "categoria": "Recall directo",
        "doc_clave": "SEC-002",
        "respuesta_esperada": (
            "Minimo 12 caracteres, incluyendo al menos 1 mayuscula, 1 numero "
            "y 1 simbolo (SEC-002)."
        ),
    },
    {
        "id": "Q03",
        "pregunta": "Cuantos intentos fallidos de login bloquean una cuenta?",
        "nivel": "Basico",
        "categoria": "Recall directo",
        "doc_clave": "SEC-003",
        "respuesta_esperada": (
            "5 intentos fallidos consecutivos en un periodo de 15 minutos (SEC-003)."
        ),
    },
    # ── Nivel 2: Discriminacion de versiones ─────────────────────────
    {
        "id": "Q04",
        "pregunta": "Se permite reutilizar contrasenas anteriores?",
        "nivel": "Intermedio",
        "categoria": "Discriminacion de versiones",
        "doc_clave": "SEC-002",
        "respuesta_esperada": (
            "No se pueden reutilizar las ultimas 10 contrasenas (SEC-002 vigente). "
            "La politica anterior (SEC-001, desactualizada) permitia reutilizar despues "
            "de 3 ciclos, pero eso ya no aplica."
        ),
    },
    {
        "id": "Q05",
        "pregunta": "Es obligatorio usar autenticacion multifactor (MFA)?",
        "nivel": "Intermedio",
        "categoria": "Discriminacion de versiones",
        "doc_clave": "SEC-002",
        "respuesta_esperada": (
            "Si, MFA es obligatorio para todos los empleados (SEC-002 vigente). "
            "Excepcion: cuentas de servicio automatizadas se excluyen del MFA "
            "pero requieren rotacion cada 15 dias y aprobacion del CISO."
        ),
    },
    # ── Nivel 3: Razonamiento multi-documento ────────────────────────
    {
        "id": "Q06",
        "pregunta": "Si sospecho que alguien accedio a mi cuenta, que debo hacer paso a paso?",
        "nivel": "Avanzado",
        "categoria": "Razonamiento multi-documento",
        "doc_clave": "SEC-005, INC-001",
        "respuesta_esperada": (
            "1) Reportar como incidente de seguridad. Si es acceso no autorizado confirmado "
            "a sistema critico es Nivel 1 (reportar en 15 min al CISO, DPO y Comite de Crisis). "
            "Si es sospecha, es Nivel 2 (reportar en 2 horas al CISO y jefe de area). "
            "2) NO restablecer la contrasena directamente: SEC-005 indica que si se sospecha "
            "compromiso, se debe escalar primero al equipo de Respuesta a Incidentes (INC-001). "
            "3) Documentar en JIRA proyecto SEC-INCIDENTS."
        ),
    },
    {
        "id": "Q07",
        "pregunta": "Que requisitos necesito cumplir para trabajar desde casa?",
        "nivel": "Avanzado",
        "categoria": "Razonamiento multi-documento",
        "doc_clave": "TW-001, SEC-002",
        "respuesta_esperada": (
            "Segun TW-001: VPN corporativa (Cisco AnyConnect) con MFA activo, no usar WiFi "
            "publico sin VPN, equipo con antivirus actualizado, SO parcheado, disco cifrado. "
            "Horario de acceso a sistemas criticos: 6:00-22:00 (excepto operaciones 24/7 con "
            "aprobacion). Sesiones VPN inactivas se desconectan a los 30 min. Maximo 3 dispositivos. "
            "Contrasena segun SEC-002 (12 chars, MFA, rotacion 60 dias)."
        ),
    },
    # ── Nivel 4: Excepciones y casos borde ───────────────────────────
    {
        "id": "Q08",
        "pregunta": (
            "Soy contratista externo y manejo una cuenta de servicio automatizada. "
            "Cada cuanto debo cambiar la contrasena y necesito MFA?"
        ),
        "nivel": "Experto",
        "categoria": "Excepciones y casos borde",
        "doc_clave": "SEC-002",
        "respuesta_esperada": (
            "Hay dos reglas que aplican segun SEC-002: Como contratista externo, el ciclo "
            "es cada 30 dias. Pero como cuenta de servicio automatizada, el ciclo es cada "
            "15 dias (mas restrictivo, aplica este). Las cuentas de servicio se excluyen del "
            "MFA pero requieren aprobacion del CISO."
        ),
    },
    {
        "id": "Q09",
        "pregunta": (
            "Un cliente solicita que eliminemos todos sus datos personales. "
            "Cual es el plazo, que ley aplica, y a quien contacto?"
        ),
        "nivel": "Experto",
        "categoria": "Excepciones y casos borde",
        "doc_clave": "SEC-004",
        "respuesta_esperada": (
            "Plazo maximo de 30 dias calendario para procesar la solicitud de eliminacion "
            "(derecho al olvido) segun SEC-004. Ley aplicable: Ley 1581 de 2012. "
            "Contactar a la DPO: Dra. Maria Torres (maria.torres@techcorp.co). "
            "Los datos de clientes se retienen maximo 5 anos despues de la ultima interaccion."
        ),
    },
    {
        "id": "Q10",
        "pregunta": (
            "Hubo una brecha de datos que expuso informacion personal de clientes. "
            "Que clasificacion tiene, a quien notifico, en cuanto tiempo, y que ley debo cumplir?"
        ),
        "nivel": "Experto",
        "categoria": "Razonamiento multi-documento + legal",
        "doc_clave": "INC-001, SEC-004",
        "respuesta_esperada": (
            "Clasificacion: Nivel 1 (Critico) segun INC-001 por ser brecha confirmada. "
            "Notificar: inmediato (max 15 min) al CISO, al DPO (Dra. Maria Torres) y al "
            "Comite de Crisis. Documentar en JIRA SEC-INCIDENTS. "
            "Notificar a la autoridad nacional de proteccion de datos en maximo 72 horas "
            "(Ley 1581 Art. 17). Datos cifrados segun SEC-004 (AES-256 reposo, TLS 1.3 transito). "
            "Multas potenciales: hasta 200 salarios minimos."
        ),
    },
]

# Pregunta por defecto para el modo simple
PREGUNTA_DEMO = BENCHMARK_QUESTIONS[0]["pregunta"]

# ── Chaos Engineering Types ─────────────────────────────────────────────────

CHAOS_TYPES: dict[str, dict] = {
    "Documento obsoleto": {
        "desc": "El agente recibe primero el documento desactualizado y lo usa como referencia principal.",
        "impact": "Stale Document - Grounded detecta CONTRADICTED, Safety dice BLOCK",
        "deltas": {"grounded": -0.65, "behavioral": -0.55, "safety": -0.75, "debate": -0.60},
        "color": "#f97316",
        "is_bias": False,
    },
    "Fuentes conflictivas": {
        "desc": "Dos documentos en la KB tienen datos opuestos. El agente no puede reconciliarlos.",
        "impact": "Reasoning Drift - Debate dice REVISE, incertidumbre distribuida en todos los jueces",
        "deltas": {"grounded": -0.40, "behavioral": -0.30, "safety": -0.20, "debate": -0.70},
        "color": "#a855f7",
        "is_bias": False,
    },
    "Tool failure": {
        "desc": "El retriever devuelve vacio. El agente responde sin documentos de respaldo.",
        "impact": "Delegation Gap - Behavioral detecta INCOMPLETE, Grounded sin evidencia",
        "deltas": {"grounded": -0.55, "behavioral": -0.70, "safety": -0.15, "debate": -0.25},
        "color": "#ef4444",
        "is_bias": False,
    },
    "Contexto truncado": {
        "desc": "El contexto se corta a la mitad por limite de tokens. La politica vigente queda fuera.",
        "impact": "Error Cascade - todos los jueces caen, el agente trabaja con info incompleta",
        "deltas": {"grounded": -0.50, "behavioral": -0.60, "safety": -0.45, "debate": -0.50},
        "color": "#eab308",
        "is_bias": False,
    },
    "Sesgo del juez LLM": {
        "desc": (
            "El juez LLM evalua respuestas bien formateadas y con tono confiado como 'correctas', "
            "aunque contengan errores factuales."
        ),
        "impact": (
            "Style Bias - Safety y Grounded dan scores INFLADOS. "
            "El sistema cree que todo esta bien cuando no lo esta."
        ),
        "deltas": {"grounded": +0.12, "behavioral": +0.08, "safety": +0.18, "debate": -0.06},
        "color": "#06b6d4",
        "is_bias": True,
    },
}
