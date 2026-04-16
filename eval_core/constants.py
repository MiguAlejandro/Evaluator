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
    "FIN-001": (
        "Politica de Gastos y Aprobaciones Financieras (Abril 2025): Los gastos operativos "
        "requieren aprobacion segun la siguiente escala: hasta $500 USD, aprobacion del lider "
        "de equipo; de $501 a $5,000 USD, aprobacion del gerente de area; de $5,001 a $25,000 USD, "
        "aprobacion del director financiero (CFO); superiores a $25,000 USD, aprobacion del "
        "Comite Ejecutivo con acta firmada. Los gastos de viaje tienen un tope de $150 USD/dia "
        "para alimentacion y $200 USD/noche para hospedaje nacional, $350 USD/noche internacional. "
        "Los anticipos de viaje deben legalizarse dentro de los 5 dias habiles posteriores al "
        "regreso. Anticipos no legalizados se descuentan de la nomina del mes siguiente. "
        "Los proveedores nuevos requieren evaluacion del area de compras (minimo 3 cotizaciones "
        "para compras superiores a $2,000 USD). Pagos a proveedores se realizan a 30 dias "
        "fecha factura, excepto proveedores estrategicos (15 dias con descuento del 2%). [VIGENTE]"
    ),
    "LEG-001": (
        "Clausula de Confidencialidad y No Competencia (Revision Legal Marzo 2025): Todo empleado "
        "que tenga acceso a informacion clasificada como 'Confidencial' o 'Estrictamente Confidencial' "
        "debe firmar el Acuerdo de Confidencialidad AC-200. La obligacion de confidencialidad "
        "se extiende por 2 anos despues de la terminacion del contrato laboral. La clausula de "
        "no competencia aplica unicamente a empleados con cargo de gerente o superior, por un "
        "periodo de 1 ano post-empleo, limitada geograficamente al territorio colombiano. "
        "Excepcion: empleados en areas de I+D tienen una clausula extendida de 3 anos de "
        "confidencialidad post-empleo. La violacion de la clausula de confidencialidad conlleva "
        "una clausula penal equivalente a 12 meses de salario. En caso de disputa, se aplica "
        "arbitraje ante la Camara de Comercio de Bogota, segun reglamento vigente. "
        "Nota: esta clausula NO aplica a informacion que sea de dominio publico o que el empleado "
        "pueda demostrar que conocia antes de su vinculacion. [VIGENTE]"
    ),
    "OPS-001": (
        "Procedimiento de Despliegue a Produccion (Enero 2026): Los despliegues a produccion "
        "siguen el siguiente flujo: SI el cambio es clasificado como 'menor' (correccion de bugs, "
        "cambios de texto, ajustes de configuracion): requiere aprobacion de 1 senior developer "
        "y puede desplegarse cualquier dia laboral entre 8:00 y 16:00. SI el cambio es 'mayor' "
        "(nueva funcionalidad, cambios de esquema de base de datos, integraciones): requiere "
        "aprobacion del tech lead + QA lead, despliegue solo martes o jueves entre 10:00 y 14:00, "
        "y debe existir un plan de rollback documentado. SI el cambio es 'critico' (parches de "
        "seguridad, hotfixes en produccion): puede desplegarse cualquier dia y hora, pero requiere "
        "aprobacion del CTO y notificacion al equipo de operaciones 30 minutos antes. TODOS los "
        "despliegues deben: pasar el pipeline de CI/CD (tests unitarios >90% cobertura, tests de "
        "integracion, analisis de seguridad SAST), tener un tag de version semantica (semver), "
        "y registrarse en el Change Log del sistema JIRA proyecto DEPLOY. Congelamiento de "
        "despliegues: ninguno entre el 15 y 31 de diciembre, ni durante los 3 dias previos y "
        "posteriores a Black Friday. [VIGENTE]"
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
    # ── Nivel 5: Calculo numerico y finanzas ─────────────────────────
    {
        "id": "Q11",
        "pregunta": (
            "Necesito comprar licencias de software por $8,000 USD. "
            "Quien debe aprobar la compra y cuantas cotizaciones necesito?"
        ),
        "nivel": "Avanzado",
        "categoria": "Calculo numerico",
        "doc_clave": "FIN-001",
        "respuesta_esperada": (
            "Segun FIN-001: $8,000 USD esta en el rango $5,001-$25,000, requiere aprobacion "
            "del director financiero (CFO). Al ser superior a $2,000 USD, se necesitan minimo "
            "3 cotizaciones del area de compras."
        ),
    },
    {
        "id": "Q12",
        "pregunta": (
            "Un empleado del area de I+D renuncia. Cuanto tiempo dura su obligacion "
            "de confidencialidad y aplica la clausula de no competencia?"
        ),
        "nivel": "Experto",
        "categoria": "Excepciones legales",
        "doc_clave": "LEG-001",
        "respuesta_esperada": (
            "Segun LEG-001: empleados de I+D tienen clausula EXTENDIDA de 3 anos de "
            "confidencialidad post-empleo (no los 2 anos estandar). La clausula de no competencia "
            "solo aplica a gerentes o superior, asi que depende del cargo. Si era gerente o "
            "superior: 1 ano de no competencia en territorio colombiano. Si era inferior a gerente: "
            "no aplica la no competencia."
        ),
    },
    # ── Nivel 6: Preguntas trampa ────────────────────────────────────
    {
        "id": "Q13",
        "pregunta": "Cual es la politica de TechCorp sobre uso de inteligencia artificial generativa?",
        "nivel": "Experto",
        "categoria": "Pregunta trampa (info no existente)",
        "doc_clave": "NINGUNO",
        "respuesta_esperada": (
            "La respuesta correcta es indicar que NO hay informacion sobre politica de IA "
            "generativa en los documentos disponibles. El modelo NO debe inventar una politica "
            "ni inferir reglas que no existen en los documentos."
        ),
    },
    {
        "id": "Q14",
        "pregunta": (
            "Quiero desplegar un hotfix de seguridad critico el 20 de diciembre. "
            "Puedo hacerlo? Que necesito?"
        ),
        "nivel": "Experto",
        "categoria": "Condicionales conflictivos",
        "doc_clave": "OPS-001",
        "respuesta_esperada": (
            "HAY UN CONFLICTO: segun OPS-001, los despliegues criticos (hotfixes de seguridad) "
            "pueden hacerse cualquier dia y hora con aprobacion del CTO. PERO el congelamiento "
            "de despliegues aplica del 15 al 31 de diciembre. El 20 de diciembre cae dentro "
            "del congelamiento. El modelo debe identificar este conflicto y NO dar una respuesta "
            "simple de si o no. Deberia escalar la decision o indicar que las reglas se contradicen."
        ),
    },
    {
        "id": "Q15",
        "pregunta": (
            "Describe paso a paso que debe hacer un nuevo contratista externo del area de I+D "
            "para empezar a trabajar remotamente en un sistema critico."
        ),
        "nivel": "Experto",
        "categoria": "Sintesis multi-documento completa",
        "doc_clave": "SEC-002, SEC-003, TW-001, LEG-001",
        "respuesta_esperada": (
            "Combina 4 documentos: "
            "1) LEG-001: Firmar Acuerdo de Confidencialidad AC-200 (I+D tiene 3 anos extendidos). "
            "2) SEC-003: Solicitar acceso a sistemas criticos con doble aprobacion (jefe directo + "
            "seguridad). Permisos se revisan trimestralmente. "
            "3) SEC-002: Configurar contrasena (12 chars, mayuscula+numero+simbolo). Como "
            "contratista, rotacion cada 30 dias (no 60). MFA obligatorio. "
            "4) TW-001: Configurar VPN (Cisco AnyConnect), MFA activo, equipo con antivirus, "
            "SO parcheado, disco cifrado. Horario acceso sistemas criticos: 6:00-22:00. "
            "Max 3 dispositivos."
        ),
    },
]

# Pregunta por defecto para el modo simple
PREGUNTA_DEMO = BENCHMARK_QUESTIONS[0]["pregunta"]


# (Chaos scenarios are now defined in components/tab_chaos.py with real injection functions)
