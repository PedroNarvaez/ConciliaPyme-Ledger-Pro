UNIVERSIDAD COLUMBIA DEL PARAGUAY


CARRERA DE INGENIERÍA EN INFORMÁTICA

Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada

Línea de Investigación: Tecnología e Innovación
Trabajo de Conclusión de Carrera

Autores
Pedro Pablo Narvaez Benitez
Ariel Torres Romero

Asunción, Paraguay
Setiembre 2026




UNIVERSIDAD COLUMBIA DEL PARAGUAY


CARRERA DE INGENIERÍA EN INFORMÁTICA

Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada

Autores
Pedro Pablo Narvaez Benítez
Ariel Torres Romero
Trabajo de Conclusión de Carrera presentado para optar por el título de: Ingeniero en Informática
Línea de Investigación: Tecnología e Innovación
Tutor: Msc. Roberto Sánchez[1.1]

Asunción, Paraguay
Setiembre 2026
Ficha Catalográfica


Narvaez Benitez, Pedro Pablo; Torres Romero, Ariel[2.1].
Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada / Narvaez Benítez, Pedro Pablo; Torres Romero, Ariel[3.1]. — Asunción, 2026. 200 h. : il., tablas, figuras ; 27,9 cm.

Tutor: Msc. Roberto Sánchez.

Trabajo de Conclusión de Carrera (Ingeniero en Informática) — Carrera de Ingeniería en Informática, Universidad de la Columbia del Paraguay, 2026.
Incluye bibliografía y anexos.

Palabras clave: conciliación financiera; blockchain permisionada; integridad de datos; PYMES; SHA-256

Código de Biblioteca:


 Acta de aprobación TCC
En la ciudad de ____, a los _____ días del mes de  del año ________, el Tribunal Evaluador designado por la Carrera de ________, se reúne para evaluar el Trabajo de Conclusión de Carrera titulado:
«__»
Presentado por el/los estudiante/s: 1.______,
2. ______,
3 _______, para la obtención del título de _______ por la Universidad Columbia del Paraguay
Luego de la revisión del documento escrito, la exposición oral y la correspondiente defensa académica, el Tribunal resuelve:
Estudiante 1: Pedro Pablo Narvaez Benitez
Calificación: _ (______)
Estudiante 2:[4.1]

En consecuencia, el Trabajo de Conclusión de Carrera queda:__
(aprobado, aprobado con observaciones, no aprobado)
No siendo para más, se firma la presente acta en prueba de conformidad.

Nombre y apellido: 	Firma
Presidente

Nombre y apellido: 	Firma
Miembro 1

Nombre y apellido: 	Firma
Miembro 2

Dedicatoria
A nuestras familias,
por su apoyo incondicional
a lo largo de esta carrera.

Y a nuestro tutor,
por su guía y exigencia
en la construcción de este trabajo.










Agradecimientos
En primer lugar, expresamos nuestro sincero agradecimiento a nuestro tutor, el Profesor Roberto Sánchez, por su orientación rigurosa, sus comentarios constructivos y su exigencia académica, que fueron fundamentales para elevar la calidad de este trabajo.
A la Universidad Columbia del Paraguay y a la Carrera de Ingeniería en Informática, por brindarnos la formación académica y el espacio institucional para desarrollar este Trabajo de Conclusión de Carrera.
A los docentes que compartieron sus conocimientos a lo largo de la carrera, en particular aquellos que despertaron nuestro interés por la seguridad informática, las bases de datos y el desarrollo de software.
A nuestras familias, por su apoyo constante, su paciencia y su confianza en nosotros durante todo el proceso de formación académica y, en particular, durante el desarrollo de este trabajo.
Finalmente, a todas las personas e instituciones que, de una u otra forma, contribuyeron a la realización de este proyecto.
 Resumen
El presente Trabajo de Conclusión de Carrera aborda la problemática de la conciliación financiera en pequeñas y medianas empresas (PYMES) del Paraguay, proceso que puede desarrollarse de forma manual y generar costos operativos, errores humanos y dependencia de la confianza entre las partes durante el intercambio de archivos electrónicos. El objetivo general es desarrollar un sistema de conciliación financiera automatizada que integre tecnología blockchain permisionada como mecanismo de notariado digital, utilizando criptografía para verificar que los archivos intercambiados entre la empresa y el banco no hayan sido modificados después de su emisión. La investigación adopta un enfoque aplicado de tipo tecnológico, con alcance propositivo-experimental y diseño orientado al desarrollo de software. Se desarrolló un prototipo funcional compuesto por cuatro aplicaciones web independientes: PYME, Banco, Conciliador y Visor, cada una con su propia base de datos SQLite y una copia de la cadena de sellos. La solución utiliza SHA-256 para verificar la integridad de los archivos y un motor de conciliación de tres niveles progresivos: referencia exacta, monto y fecha cercana, y similitud de descripción con monto aproximado. La validación se realizó mediante un escenario sintético determinista de 60 ventas y 58 movimientos bancarios, alcanzando una tasa de conciliación automática del 91,7 %. Asimismo, un extracto alterado mediante Excel fue rechazado automáticamente por el sistema. Los resultados muestran que la blockchain permisionada puede aportar verificación independiente de integridad entre múltiples partes sin requerir criptomonedas ni redes públicas.[5.1]

Palabras clave: conciliación financiera; blockchain permissionada; integridad de datos; PYMES; SHA-256

 Abstract[6.1]

Keywords: financial reconciliation; permissioned blockchain; data integrity; SMEs; SHA-256

 Índice
Ficha Catalográfica	3
Acta de aprobación TCC	4
Dedicatoria	1
Agradecimientos	2
Resumen	3
Abstract	4
Índice	5
Introducción	1
CAPÍTULO 1. PRESENTACIÓN DE LA INVESTIGACIÓN	3
1.1 Preguntas de investigación	3
1.2 Respuestas fundamentadas a las preguntas de investigación	3
1.3 Objetivos de la Investigación	6
1.3.1 Objetivo General	6
1.3.2 Objetivos Específicos	6
1.4 Justificación de la Investigación	7
1.4.1 Justificación teórica	7
1.4.2 Justificación práctica	7
1.4.3 Justificación social	7
1.4.4 Justificación metodológica	8
CAPÍTULO 2. MARCO TEÓRICO O BASES TEÓRICAS Y ANTECEDENTES	9
2.1 Antecedentes de la Investigación	9
2.2 Bases Teóricas	10
2.2.1 Tecnología Blockchain: Conceptos Fundamentales	10
2.2.2 Blockchain Pública vs. Permissionada	10
2.2.3 Funciones Hash Criptográficas y SHA-256	10
2.2.4 Conciliación Financiera: Proceso y Problemática	11
2.3 Marco Legal	11
CAPÍTULO 3. MARCO METODOLÓGICO	13
3.1 Enfoque y Alcance de la Investigación	13
3.2 Diseño de la Investigación	13
3.3 Metodología de Desarrollo de Software	13
3.4 Población y Muestra	14
3.5 Técnicas de Recolección de Datos	14
3.6 Análisis de Datos	14
3.7 Validación de la Solución	15
CAPÍTULO 4. ESPECIFICACIÓN DE LA SOLUCIÓN TECNOLÓGICA	16
4.1 Descripción General de la Solución	16
4.2 Arquitectura de la Solución	16
4.2.1 Vista general: cuatro aplicaciones independientes	16
4.2.2 Núcleo 1: Cadena de sellos criptográficos	17
4.2.3 Verificación en tres frentes independientes	19
4.2.5 Diseño de la base de datos	20
4.3 Tecnologías Utilizadas	21
4.4 Requisitos Funcionales	22
4.4.1 Requisitos funcionales de la aplicación PYME	22
4.4.2 Requisitos funcionales de la aplicación Banco	23
4.4.3 Requisitos funcionales de la aplicación Conciliador	23
4.4.4 Requisitos funcionales de la aplicación Visor	23
4.5 Requisitos No Funcionales	24
4.5.1 Seguridad	24
4.5.2 Rendimiento	24
4.5.3 Usabilidad	24
4.5.4 Portabilidad	24
4.6 Interfaces de la Solución	25
4.6.1 Interfaz de la PYME	25
4.6.2 Interfaz del Banco	25
4.6.3 Interfaz del Conciliador	25
4.6.4 Interfaz del Visor	25
CAPÍTULO 5. CONCLUSIONES Y RECOMENDACIONES	27
5.1 Conclusiones	27
5.2 Recomendaciones	28
5.2.1 Recomendaciones técnicas	28
5.2.2 Recomendaciones académicas	28
5.2.3 Recomendaciones institucionales	28
Referencias Bibliográficas	30
Declaración de Uso de Inteligencia Artificial (IA)	1
Declaración de Uso de Inteligencia Artificial (IA)	1


Introducción
La conciliación bancaria constituye uno de los procesos de control interno más importantes para cualquier organización económica. Consiste en comparar sistemáticamente los registros contables internos de una empresa con los movimientos reportados por su entidad financiera, a fin de identificar diferencias, verificar la exactitud de los saldos y asegurar la integridad de la información financiera. A pesar de su relevancia, en la práctica de muchas pequeñas y medianas empresas (PYMES) paraguayas, este proceso continúa desarrollándose de forma predominantemente manual, basado en la comparación visual de planillas de cálculo y archivos de texto intercambiados por medios electrónicos.
Esta modalidad operativa presenta limitaciones significativas: consume horas de trabajo administrativo que podrían dedicarse a actividades de mayor valor agregado, es propensa a errores humanos de transcripción o interpretación, y presenta una debilidad fundamental desde el punto de vista de la confianza: cuando una empresa recibe un archivo de extracto bancario por correo electrónico, o cuando el banco recibe un registro de ventas por parte de un cliente corporativo, ninguna de las partes tiene una forma matemáticamente demostrable de verificar que el archivo recibido es idéntico al que fue emitido. La integridad del intercambio depende exclusivamente de la confianza mutua y de la seguridad de los canales de comunicación.
El presente Trabajo de Conclusión de Carrera propone una solución tecnológica a esta problemática mediante el desarrollo de un sistema de conciliación financiera automatizada que integra tecnología blockchain permissionada. Es importante delimitar desde esta introducción que la tecnología no se utiliza como red pública de criptomonedas, sino exclusivamente como notario digital: registra huellas criptográficas y marcas de tiempo de los archivos fuente, garantizando la integridad e inmutabilidad antes de que se produzca la conciliación misma.



El trabajo se estructura en cinco capítulos. El Capítulo 1 presenta la investigación, con las preguntas de investigación, los objetivos y la justificación. El Capítulo 2 desarrolla el marco teórico, incluyendo antecedentes, bases teóricas y marco legal. El Capítulo 3 expone el marco metodológico adoptado. El Capítulo 4 presenta la especificación detallada de la solución tecnológica desarrollada. Finalmente, el Capítulo 5 sintetiza las conclusiones del trabajo y formula recomendaciones.

 Capítulo 1. Presentación de la investigación
2.2	Planteamiento del problema
1.2	Preguntas de investigación
¿De qué manera la tecnología blockchain permissionada delimitada a función de notario digital puede contribuir a automatizar la conciliación financiera y fortalecer la garantía de integridad de los archivos intercambiados entre una PYME y su banco en el contexto paraguayo?
Preguntas específicas:
1. ¿Cuáles son las limitaciones de los métodos tradicionales de verificación de integridad de archivos en el contexto de la conciliación bancaria entre dos partes independientes?
2. ¿Cómo se puede diseñar una arquitectura de sistema que aproveche las propiedades de encadenamiento criptográfico de la tecnología blockchain sin almacenar datos financieros sensibles en la cadena?
3. ¿Qué nivel de efectividad en la automatización de cruces puede alcanzar un motor de conciliación de tres niveles progresivos sobre un escenario sintético representativo de la operativa de una PYME?
4. ¿Es posible detectar automáticamente manipulaciones de archivos posteriores a su emisión mediante la comparación de huellas criptográficas registradas en una cadena de sellos?
1.3	Respuestas fundamentadas a las preguntas de investigación
En respuesta a la pregunta general de investigación, la tecnología blockchain permissionada delimitada estrictamente a la función de notario digital contribuye a la automatización de la conciliación financiera y al fortalecimiento de las garantías de integridad mediante la creación de un registro distribuido, inmutable y verificable de huellas criptográficas SHA-256 y marcas de tiempo de los archivos intercambiados entre la PYME y el banco. Al descentralizar el sellado de lotes e independizar la validación de la confianza ciega entre las partes, el sistema permite que un motor determinista ejecute el cruce de datos con la certeza matemática de que los archivos fuente no han sido alterados unilateralmente posterior a su emisión.
En respuesta a la primera pregunta específica, los métodos tradicionales de verificación de integridad (como bases de datos centralizadas, firmas asimétricas o servicios TSA aislados) presentan serias limitaciones en entornos entre partes independientes. Las bases de datos locales o centralizadas sufren del riesgo de alteración unilateral por administradores con privilegios elevados sin dejar rastro en la cadena de referencias. Por su parte, los sellos de tiempo RFC 3161 tradicionales dependen de una Autoridad de Sellado de Tiempo centralizada y generan evidencias aisladas sin un encadenamiento criptográfico histórico secuencial. Ninguno de estos métodos combina la verificación independiente por múltiples partes con la inmutabilidad que otorga la estructura encadenada de bloques.
En respuesta a la segunda pregunta específica, la arquitectura del sistema logra preservar la confidencialidad de la información mediante una separación estricta entre la capa de datos sensibles y la capa de notariado digital. Los datos financieros detallados (como importes, clientes o descripciones) permanecen almacenados exclusivamente en las bases de datos relacionales SQLite locales e independientes de cada participante (PYME y Banco). La cadena de sellos distribuida guarda únicamente metadatos no sensibles: huellas criptográficas SHA-256 de los archivos e individuales de cada movimiento, marcas de tiempo e identificadores de lote. De este modo, la verificación de integridad se efectúa recalculando y comparando las huellas en tiempo real contra los registros inmutables de la cadena, sin que los datos financieros expongan su privacidad ni transiten por la red blockchain.
En respuesta a la tercera pregunta específica, el motor de conciliación determinista de tres niveles progresivos alcanzó una efectividad del 91,7% de cruces automáticos sobre el escenario sintético probado (60 ventas registradas por la PYME y 58 movimientos informados por el banco). El desglose del rendimiento demuestra que el Nivel 1 (cruce por referencia exacta o número de comprobante) resolvió el 72,7% de los casos; el Nivel 2 (cruce por coincidencia de monto y ventana temporal de hasta 3 días) absorbió un 18,2% adicional correspondiente a acreditaciones diferidas; y el Nivel 3 (cruce por similitud en la descripción y monto aproximado dentro de un margen del 5%) resolvió el 9,1% restante, asociado a transferencias con comisiones bancarias descontadas.
En respuesta a la cuarta pregunta específica, se comprobó la capacidad del sistema para detectar de forma automatizada e infalible cualquier manipulación o alteración de archivos posterior a su emisión. Esto se logra mediante el aprovechamiento de la propiedad del efecto avalancha inherente al algoritmo de hash criptográfico SHA-256. Incluso ante modificaciones mínimas o imperceptibles —como la reestructuración del formato de celdas o saltos de línea producida al abrir y guardar un archivo CSV con Microsoft Excel—, el hash recalculado cambia por completo. El proceso de verificación en el Frente b) detecta esta discrepancia al comparar el hash del archivo físico recibido contra la huella registrada en el sello al momento de su emisión original, rechazando el lote de inmediato y emitiendo la alerta de brecha correspondiente.









1.4	Objetivos de la Investigación
2.2.1	Objetivo General
Desarrollar un sistema de conciliación financiera automatizada para PYMES que integre tecnología blockchain permissionada delimitada a función de notario digital, garantizando mediante criptografía que ninguno de los archivos intercambiados entre la empresa y el banco haya sido modificado después de su emisión.
1.4.1	Objetivos Específicos
1. Analizar críticamente los métodos tradicionales de verificación de la integridad de archivos y sus limitaciones en escenarios de intercambio entre dos partes independientes.
2. Diseñar e implementar una arquitectura de cuatro aplicaciones independientes, con una cadena de sellos criptográficos distribuida y verificación de la integridad en tres frentes.
3. Desarrollar un motor de conciliación determinista de tres niveles progresivos, con una regla de honestidad y una explicación automática de los movimientos pendientes.
4. Validar el funcionamiento del sistema mediante un escenario sintético determinista y pruebas de detección de manipulaciones de archivos.
5. Documentar la solución, sus resultados, sus aportes y sus limitaciones de acuerdo con las normas institucionales para Trabajos de Conclusión de Carrera.
1.5	Justificación de la Investigación
1.5.1	Justificación teórica
Esta investigación contribuye al campo de estudio de las aplicaciones empresariales de la tecnología blockchain permissionada, abordando una brecha identificada en la literatura: la mayoría de los trabajos existentes se orientan a grandes corporaciones, mientras que son escasas las propuestas adaptadas a las capacidades y necesidades de las PYMES en economías emergentes. Asimismo, el trabajo responde explícitamente al debate académico sobre la pertinencia de la tecnología blockchain frente a métodos alternativos más simples, aportando una delimitación conceptual rigurosa y una justificación basada en propiedades técnicas identificables.
1.5.2	 Justificación práctica
Desde el punto de vista práctico, el sistema desarrollado tiene el potencial de reducir los costos operativos de las PYMES asociados al proceso de conciliación, disminuir los errores humanos, fortalecer los controles internos y, fundamentalmente, aportar un mecanismo de evidencia compartida en caso de disputas con entidades financieras o inspecciones tributarias. La solución se diseña deliberadamente para ser accesible: utiliza solo la biblioteca estándar de Python, no requiere licencias costosas ni infraestructura especializada.
2.2.2	Justificación social
Las PYMES son el pilar de la economía paraguaya en términos de generación de empleo y actividad empresarial, constituyendo el 98% del parque empresarial y empleando a aproximadamente el 76,8% de la población ocupada. Cualquier herramienta tecnológica que mejore su gestión financiera y su capacidad de relacionarse con el sistema financiero formal en condiciones de mayor equidad contribuye indirectamente a fortalecer el tejido empresarial del país.




2.2.3	 Justificación metodológica
Metodológicamente, el trabajo adopta un enfoque propositivo-experimental que combina el desarrollo de software con la validación experimental mediante escenarios sintéticos deterministas y pruebas automatizadas. Esta aproximación permite no solo proponer una arquitectura teórica, sino materializarla en un prototipo funcional y evaluar su comportamiento frente a casos diseñados para poner a prueba sus mecanismos de seguridad.

 Capítulo 2. Marco teórico o bases teóricas y antecedentes
2.3	Antecedentes de la Investigación
El campo de los sistemas de conciliación financiera automatizada cuenta con varias décadas de desarrollo industrial, inicialmente orientado a grandes corporaciones a través de módulos dentro de sistemas ERP. En años más recientes han surgido soluciones basadas en la nube orientadas a PYMES, como Nibo en Brasil y Holded en España. Sin embargo, el análisis de estas soluciones muestra que ninguna integra como característica central un mecanismo de garantía de integridad distribuida basado en tecnología blockchain.
En el ámbito académico, Wila Bone y colaboradores (2025) presentan una revisión sistemática de aplicaciones de blockchain en la contabilidad y transparencia de PYMES latinoamericanas, concluyendo que la tecnología ofrece potencial significativo pero que su adopción requiere soluciones adaptadas. Catalini y Gans (2016), desde el NBER, argumentan que el valor fundamental de la blockchain reside en la reducción de los costos de verificación.
El curso Blockchain & Money del MIT Sloan School of Management (Gensler, 2018), específicamente en su sesión 9 dedicada a blockchains permissionadas, analiza explícitamente las diferencias entre estas arquitecturas y las bases de datos tradicionales, proporcionando el marco analítico que este trabajo utiliza para responder a la objeción sobre la pertinencia de la tecnología.
En el contexto nacional paraguayo, los antecedentes sobre aplicaciones tecnológicas específicas para la gestión financiera de PYMES son relativamente escasos. El Régimen SIFEN establecido por la Resolución General 104/2019 de la SET constituye un antecedente normativo relevante que impulsa la digitalización de los comprobantes fiscales electrónicos.




2.4	Marco conceptual
2.2.1	Tecnología Blockchain: Conceptos Fundamentales
Una blockchain o cadena de bloques es una estructura de datos distribuida donde la información se agrupa en bloques que se vinculan criptográficamente entre sí, formando una secuencia cronológica. Cada bloque contiene un conjunto de registros, una marca de tiempo y una referencia criptográfica al bloque anterior. Esta estructura hace que modificar un registro histórico sea computacionalmente detectable, ya que rompería la cadena de referencias criptográficas subsiguientes.
2.2.2	Blockchain Pública vs. Permissionada
Las redes blockchain pueden clasificarse según quién está autorizado a participar. En una red pública, cualquier persona puede participar, enviar transacciones y formar parte del mecanismo de consenso. En una red permissionada, el derecho a participar y validar transacciones está restringido a un conjunto definido de organizaciones previamente autorizadas. La aproximación adoptada en este trabajo corresponde a una red permissionada simplificada: no se utiliza criptomonedas, no hay minería, y la red opera exclusivamente como notario digital
2.2.3	Funciones Hash Criptográficas y SHA-256
Una función hash criptográfica transforma una entrada de longitud arbitraria en una salida de longitud fija con tres propiedades fundamentales: resistencia a la preimagen, resistencia a la segunda preimagen y resistencia a colisiones. El algoritmo SHA-256, estandarizado por el NIST en FIPS 180-4, produce una salida de 256 bits. Una propiedad fundamental es el efecto avalancha: un cambio de un solo bit en la entrada produce, en promedio, el cambio de aproximadamente la mitad de los bits de la salida. Esta propiedad es la que permite detectar incluso modificaciones mínimas.




2.2.4	Conciliación Financiera: Proceso y Problemática
La conciliación financiera es el proceso mediante el cual una organización compara sus registros internos con los movimientos reportados por su entidad bancaria. Cuando este proceso se desarrolla manualmente, genera tres tipos de problemas: operativos (tiempo y errores), de control interno (detección dependiente de la diligencia humana), y de confianza (ninguna parte puede demostrar matemáticamente que el archivo recibido es idéntico al emitido).

2.3	Marco Legal
El desarrollo e implementación de sistemas que procesan información financiera en el Paraguay se enmarca en varios cuerpos normativos. La Ley 6534/2020 de Protección de Datos Personales establece principios de licitud, finalidad, proporcionalidad, seguridad y transparencia. La decisión arquitectónica de NO almacenar datos financieros sensibles en la cadena de sellos responde directamente al principio de minimización de datos.
En el ámbito tributario, la Resolución General 104/2019 de la SET establece el Sistema Integrado de Facturación Electrónica Nacional (SIFEN). El Código Civil Paraguayo reconoce valor probatorio a los documentos electrónicos que permitan demostrar su integridad y origen, punto donde los mecanismos criptográficos de verificación adquieren relevancia jurídica práctica.

 Capítulo 3. Marco metodológico
Enfoque y Alcance de la Investigación
Esta investigación adopta un enfoque aplicado de tipo tecnológico. Se considera aplicada porque su propósito fundamental es resolver un problema práctico concreto. Se califica como tecnológica porque su producto central es el desarrollo de una solución de software con arquitectura definida, algoritmos específicos y validación experimental.
El alcance es propositivo-experimental. Es propositivo porque avanza una propuesta tecnológica concreta y la materializa en un prototipo funcional. Es experimental porque el comportamiento de la solución se evalúa mediante la construcción de escenarios controlados y la observación sistemática de sus resultados.
Diseño de la Investigación
El diseño se estructura en cinco fases sucesivas: Fase I) revisión bibliográfica y definición del problema; Fase II) diseño arquitectónico detallado; Fase III) implementación del prototipo funcional; Fase IV) validación experimental mediante escenarios sintéticos y pruebas automatizadas; Fase V) análisis de resultados y redacción del documento final.
Metodología de Desarrollo de Software
Para el desarrollo del prototipo se adoptó una metodología iterativa incremental. Se adoptaron cinco principios rectores: privacidad por diseño, cada parte con su propia base de datos, verificación antes de acción, honestidad en el cruce, y simplicidad tecnológica.
El lenguaje de programación seleccionado es Python 3.10+, justificado por su disponibilidad, su biblioteca estándar completa (hashlib, sqlite3, http.server, urllib) y su legibilidad. Como motor de base de datos se utiliza SQLite. Para la interfaz web se utiliza HTML5, CSS3 y JavaScript nativo, con Bootstrap 5 incluido localmente.
Población y Muestra
Dado que se trata de un desarrollo tecnológico validado mediante escenario sintético, no se trabaja con población humana en el sentido estadístico tradicional. La unidad de análisis son los registros de transacciones financieras. Para la validación se construyó un escenario sintético determinista compuesto por 60 registros de ventas del lado de la PYME y 58 movimientos del lado del banco.
Técnicas de Recolección de Datos
Las fuentes de datos para la construcción del marco teórico fueron fuentes secundarias bibliográficas y documentales: libros, artículos académicos, normas internacionales, documentos oficiales de instituciones públicas paraguayas y materiales de cursos académicos de instituciones reconocidas internacionalmente como el MIT Sloan School of Management.
Para la validación experimental, la técnica consistió en la ejecución sistemática del software sobre entradas definidas y el registro automático de sus salidas: tasas de cruce por nivel, detección o no de manipulaciones y resultados de las verificaciones de integridad.
Análisis de Datos
El análisis de los resultados se realizó mediante técnicas cuantitativas y cualitativas. Cuantitativamente se calcularon las tasas de cruce automático por cada nivel del motor y la tasa global de éxito. Cualitativamente se evaluó la capacidad del sistema para detectar manipulaciones y para generar explicaciones comprensibles de los movimientos pendientes.
Validación de la Solución
La validación se estructuró en cuatro estrategias complementarias: validación de flujo completo mediante prueba automatizada end-to-end; validación del escenario sintético determinista; prueba de detección de manipulación mediante el caso del archivo alterado por Excel; y análisis de amenazas a la validez y definición de estrategias de mitigación.

 Capítulo 4. Especificación de la solución tecnológica
Descripción General de la Solución
ConciliaChain es un sistema compuesto por cuatro aplicaciones web independientes que colaboran para automatizar la conciliación financiera entre una PYME y su banco, garantizando mediante criptografía que ninguno de los archivos intercambiados haya sido modificado después de su emisión.
El principio fundamental de diseño es que la cadena de sellos funciona exclusivamente como notario digital inalterable. No guarda datos financieros sensibles, no ejecuta la conciliación, no usa criptomonedas, no es red pública. Su única función es registrar huellas criptográficas SHA-256 y marcas de tiempo de los archivos fuente.
El flujo operativo general es el siguiente: la PYME registra sus ventas y al cierre del día emite un lote que es sellado y propagado; el banco emite su extracto oficial que también es sellado y propagado; antes de conciliar, el conciliador verifica la integridad de ambos lotes en tres frentes independientes; si todo es correcto, ejecuta el motor de conciliación de tres niveles; si se detecta alguna brecha, dispara una alerta y rechaza el lote.
Arquitectura de la Solución
Vista general: cuatro aplicaciones independientes
La arquitectura se compone de cuatro aplicaciones independientes, cada una ejecutándose en su propio proceso y escuchando en su propio puerto. Cada actor cuenta con su propia base de datos SQLite y su propia copia de la cadena de sellos.
Aplicación	Puerto	Rol principal	Color de marca
PYME (Sistema de Ventas)	5001	Registrar ventas, emitir lotes sellados	#b0551b (ámbar)
Banco X (Portal Empresas)	5002	Emitir extractos oficiales sellados	#1f5e8e (azul)
Conciliador (Motor de Cruce)	5000	Verificar integridad, conciliar, informar	#0e7668 (verde)
Visor (Monitor en vivo)	5003	Mostrar eventos en tiempo real (solo lectura)	#6b21a8 (púrpura)


Núcleo 1: Cadena de sellos criptográficos
La cadena de sellos se implementa desde cero utilizando la biblioteca estándar de Python. Su estructura física es un archivo JSON Lines donde cada línea representa un bloque completo serializado como objeto JSON.
Campo	Tipo	Descripción
indice	Entero ≥ 1
Número secuencial del bloque
origen	Enumeración	EMPRESA / BANCO / CONCILIA
lote_id	Texto	Identificador único del lote
archivo	Texto	Nombre del archivo físico en el buzón
n_movimientos	Entero	Cantidad de movimientos en el lote
hashes_movimientos	Arreglo	SHA-256 de cada movimiento individual
hash_raiz	Texto (64 hex)	SHA-256 de la concatenación de todos los hashes
hash_archivo	Texto (64 hex)	SHA-256 del archivo físico completo
hash_anterior	Texto (64 hex)	Hash del bloque anterior (encadenamiento)
timestamp	Texto	Marca de tiempo YYYY-MM-DD HH:MM:SS
hash_bloque	Texto (64 hex)	SHA-256 de todo el contenido del bloque

El mecanismo de encadenamiento funciona de la siguiente manera: cada bloque nuevo incluye en su interior el hash_bloque del bloque anterior. Para modificar un registro histórico sería necesario cambiar su hash, lo que rompería el hash_anterior del bloque siguiente, y así sucesivamente hasta el final de la cadena.
Verificación en tres frentes independientes
Antes de cualquier operación de conciliación, el sistema verifica la integridad mediante tres frentes independientes. El Frente a) verifica la cadena: recorre cada bloque, recalcula su hash y confirma el encadenamiento. El Frente b) verifica el archivo físico: recalcula el hash del archivo actual y lo compara con el hash_archivo registrado. El Frente c) verifica la base de datos: recalcula el hash de cada movimiento individual y lo compara con el hashes_movimientos registrado. Si cualquiera falla, el sistema dispara una alerta y rechaza el lote.

4.2.4 Núcleo 2: Motor de conciliación de tres niveles
El motor de cruce es determinista y trabaja en tres niveles progresivos.
Nivel	Criterio de cruce	Casos que resuelve
1	Referencia o comprobante idéntico en ambos lados	Ventas con tarjeta (referencia común)
2	Mismo monto + fechas a no más de 3 días	Depósitos en efectivo que acreditan al día siguiente
3	Palabras en común en descripción + monto ±5%	Transferencias con comisiones bancarias

Se aplica una regla de honestidad fundamental: cada movimiento se cruza como máximo una vez, con el primer candidato encontrado en el mejor nivel posible. Lo que no cruza queda marcado como pendiente y recibe una explicación automática en lenguaje natural.














Diseño de la base de datos
Cada actor cuenta con su propia base de datos SQLite con un esquema idéntico. La tabla principal se denomina movimientos y contiene los campos: id (clave primaria), lote, fecha, monto (entero en guaraníes), referencia y descripción. La elección de una base de datos por actor refuerza el principio de independencia: ninguna parte controla los datos de otra.
Tecnologías Utilizadas
Categoría	Tecnología	Justificación
Lenguaje	Python 3.10+	Biblioteca estándar completa, legibilidad, disponibilidad
Criptografía	SHA-256 (hashlib)	Estándar NIST FIPS 180-4, análisis exhaustivo
Base de datos	SQLite	Sin servidor, contenido en biblioteca, archivo por actor
Servidor web	http.server	Sin dependencias externas, suficiente para el prototipo
Comunicación	urllib	Llamadas HTTP locales entre procesos
Frontend	HTML5, CSS3, JS nativo	Estándares web, sin dependencias de compilación
Estilos	Bootstrap 5 (incluido)	Interfaz consistente y responsive
Serialización	JSON / JSON Lines	Formato legible, ampliamente soportado
Formatos intercambio	CSV, XML	Estándares que los bancos ya envían










Requisitos Funcionales
Requisitos funcionales de la aplicación PYME
RF-EMP-01: Permitir registrar una nueva venta con fecha, monto, referencia opcional y descripción.
RF-EMP-02: Mostrar indicadores de gestión: total de movimientos, pendientes, emitidos y monto total.
RF-EMP-03: Listar los movimientos más recientes con su estado actual.
RF-EMP-04: Cerrar el lote diario: exportar CSV, sellar, agregar bloque a la cadena y propagar.
RF-EMP-05: Mostrar la copia local de la cadena de sellos.
Requisitos funcionales de la aplicación Banco
RF-BAN-01: Emitir extracto oficial en formato CSV.
RF-BAN-02: Emitir extracto oficial en formato XML.
RF-BAN-03: Sellar cada extracto emitido mediante la creación de un bloque en la cadena.
RF-BAN-04: Propagar cada bloque nuevo a las demás copias de la cadena.
Requisitos funcionales de la aplicación Conciliador
RF-CON-01: Mostrar la bandeja de entrada con los lotes disponibles de ambas partes.
RF-CON-02: Para cada lote, indicar el estado de integridad: íntegro o con brecha.
RF-CON-03: Ejecutar verificación de integridad en tres frentes antes de conciliar.
RF-CON-04: Disparar alerta de brecha si cualquiera de los tres frentes falla.
RF-CON-05: Ejecutar el motor de conciliación de tres niveles cuando la integridad esté confirmada.
RF-CON-06: Mostrar los resultados clasificados por nivel de cruce.
RF-CON-07: Mostrar los movimientos pendientes con explicación automática.
RF-CON-08: Permitir descargar el informe completo en formato CSV.
Requisitos funcionales de la aplicación Visor
RF-VIS-01: Mostrar en tiempo real los eventos del ecosistema mediante animaciones visuales.
RF-VIS-02: Operar en modo solo lectura, sin capacidad de modificar datos.
Requisitos No Funcionales
Seguridad
RNF-SEG-01: Privacidad por diseño: ningún dato financiero sensible se almacena en la cadena de sellos.
RNF-SEG-02: Verificación de integridad en tres frentes independientes antes de cualquier operación de conciliación.
RNF-SEG-03: Validación de encadenamiento antes de incorporar cualquier bloque propagado.
Rendimiento
RNF-REN-01: El sistema debe completar el proceso de conciliación de un escenario de 60 × 58 movimientos en menos de 5 segundos en un equipo convencional.
RNF-REN-02: El arranque completo del ecosistema debe completarse en menos de 10 segundos.
Usabilidad
RNF-USA-01: Interfaz web simple y familiar basada en patrones de diseño convencionales.
RNF-USA-02: Explicaciones automáticas en lenguaje natural para los movimientos pendientes.
Portabilidad
RNF-POR-01: Funcionar en cualquier sistema operativo que soporte Python 3.10+.
RNF-POR-02: No requerir instalación de paquetes externos mediante pip para el núcleo funcional.
Interfaces de la Solución
Interfaz de la PYME
La interfaz principal de la aplicación PYME se organiza en tres secciones. En la parte superior se muestran las tarjetas de indicadores clave. En la parte central se ubica el formulario de registro de una nueva venta. En la parte inferior se presenta la tabla de movimientos recientes con su estado. Al final de la página se ubica el botón de acción principal: 'Cerrar lote y exportar'.
Interfaz del Banco
La interfaz del portal del banco presenta los indicadores de movimientos, la lista de movimientos recientes y las opciones de emisión de extracto en formato CSV y XML. Cada opción de emisión es un botón prominente que dispara el proceso completo de exportación, sellado y propagación.
Interfaz del Conciliador
La interfaz del conciliador se organiza alrededor del flujo de trabajo. La bandeja de entrada muestra los lotes disponibles con un indicador cromático de estado de integridad: verde si los tres frentes pasaron, rojo si se detectó alguna brecha. Los resultados se presentan en tres secciones diferenciadas por colores: cruces exitosos en verde, pendientes de la PYME en ámbar, pendientes del banco en azul.
Interfaz del Visor
La interfaz del visor presenta un panel de monitorización en vivo donde se muestran animaciones de cada acción a medida que ocurre en el ecosistema. Se utiliza una paleta de colores consistente con las demás aplicaciones para identificar visualmente cada actor. La interfaz es deliberadamente de solo lectura, sin botones de acción.

 Capítulo 5. Conclusiones y recomendaciones
Conclusiones
En respuesta al objetivo general de desarrollar un sistema de conciliación financiera automatizada que integre tecnología blockchain permissionada como notario digital, se presentan las siguientes conclusiones.
Primera conclusión: la tecnología blockchain permissionada, cuando se delimita estrictamente a función de notario digital de huellas criptográficas, aporta cuatro propiedades diferenciadas que ningún método alternativo simple combina simultáneamente: independencia del verificador, encadenamiento secuencial histórico, reglas de validación que ningún administrador unilateral puede cambiar, y preparación arquitectónica para extensión multi-parte sin rediseño.
Segunda conclusión: es técnicamente viable construir un sistema completo que aproveche estas propiedades utilizando exclusivamente la biblioteca estándar de Python, sin dependencias externas, sin criptomonedas y sin redes públicas. El prototipo desarrollado demuestra que una arquitectura de cuatro aplicaciones independientes, cada una con su propia base de datos y su copia de la cadena, con comunicación por HTTP local y verificación en tres frentes independientes, es factible y funcional.
Tercera conclusión: el motor de conciliación de tres niveles progresivos combinado con la regla de honestidad alcanza una tasa de cruces automáticos del 91,7% sobre un escenario sintético representativo de la operativa de una PYME. El nivel 1 resuelve las ventas con tarjeta por referencia exacta, el nivel 2 resuelve los depósitos en efectivo que acreditan al día siguiente, y el nivel 3 resuelve las transferencias con comisiones.
Cuarta conclusión: el sistema detecta de forma automática y fiable manipulaciones de archivos posteriores a su emisión, incluso cuando estas son sutiles e inadvertidas como las que produce Excel al abrir y guardar un archivo CSV. El mecanismo se basa en el efecto avalancha de SHA-256 y en la verificación independiente del Frente b).
Quinta conclusión: el diseño basado en principios de privacidad por diseño, que almacena solamente huellas criptográficas en la cadena y mantiene los datos financieros sensibles en los sistemas internos de cada actor, hace que la solución sea compatible con normativas de protección de datos personales.
Sexta conclusión: la aproximación permissionada y de consenso reducido representa una elección deliberada alineada con el Trilema de Buterin: se renuncia a la descentralización global para priorizar seguridad de integridad y simplicidad operativa adecuada para el contexto PYME.
Recomendaciones
Recomendaciones técnicas
Primero: se recomienda migrar el núcleo de cadena de sellos del prototipo actual a Hyperledger Fabric para una implementación productiva real. Segundo: se recomienda implementar un módulo de respaldo cifrado de las copias de la cadena y las bases de datos. Tercero: se recomienda agregar soporte nativo para formatos estándar bancarios como MT940 y CAMT.053.
Recomendaciones académicas
Primero: se recomienda extender la validación empírica mediante pruebas piloto con PYMES reales y, si es posible, con la participación de alguna entidad bancaria. Segundo: se recomienda profundizar en el análisis de costos-beneficios comparativos entre esta arquitectura y alternativas centralizadas. Tercero: se recomienda explorar la incorporación de mecanismos de firma digital asimétrica ECDSA para complementar las garantías de integridad con garantías de no repudio.
Recomendaciones institucionales
Primero: se recomienda a las instituciones de fomento empresarial considerar el apoyo a este tipo de soluciones tecnológicas adaptadas a las capacidades de las PYMES. Segundo: se recomienda a la Carrera de Ingeniería en Informática continuar fomentando trabajos de desarrollo tecnológico que combinen rigurosidad conceptual con soluciones prácticas orientadas a problemas del contexto nacional paraguayo.

 Referencias Bibliográficas
Catalini, C., & Gans, J. S. (2016). Some simple economics of the blockchain. NBER Working Paper No. 22952.
Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance of information technology. MIS Quarterly, 13(3), 319-340.
Dirección General de Registros Públicos [DIRGE]. (2024). Anuario estadístico de MIPYMES 2024. Asunción, Paraguay.
Dirección Nacional de Protección de Datos Personales. (2020). Ley 6534/2020 de Protección de Datos Personales. Asunción, Paraguay.
Gensler, G. (2018). Blockchain & Money — Sesión 9: Blockchains Permissionadas y Casos Empresariales. MIT Sloan School of Management, Curso 15.S12. Cambridge, EE.UU.
Hernández Sampieri, R., Fernández Collado, C., & Baptista Lucio, P. (2014). Metodología de la investigación (6ª ed.). México D.F.: McGraw-Hill.
Hyperledger Fabric. (2026). Documentación oficial v2.5. The Linux Foundation.
Instituto Nacional de Estadística [INE]. (2026). Encuesta Permanente de Hogares Continua, Primer Trimestre 2026. Asunción, Paraguay.
ISO/IEC 27000:2018. Information technology — Security techniques — Information security management systems — Overview and vocabulary. Ginebra: Organización Internacional de Normalización.
Jensen, M. C., & Meckling, W. H. (1976). Theory of the firm: Managerial behavior, agency costs and ownership structure. Journal of Financial Economics, 3(4), 305-360.
Lamport, L., Shostak, R., & Pease, M. (1982). The Byzantine Generals Problem. ACM Transactions on Programming Languages and Systems, 4(3), 382-401.
Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system. Documento técnico.
National Institute of Standards and Technology [NIST]. (2015). FIPS 180-4: Secure Hash Standard (SHS). Gaithersburg, EE.UU.
Yaga, D., Mell, P., Roby, N., & Scarfone, K. (2019). Blockchain Technology Overview. NIST IR 8202. Gaithersburg, EE.UU.
Rivest, R. L., Shamir, A., & Adleman, L. (1978). A method for obtaining digital signatures and public-key cryptosystems. Communications of the ACM, 21(2), 120-126.
Shannon, C. E. (1949). Communication theory of secrecy systems. Bell System Technical Journal, 28(4), 656-715.
Subsecretaría de Estado de Tributación [SET]. (2019). Resolución General 104/2019 — Régimen de Facturación Electrónica. Asunción, Paraguay.
Universidad Columbia del Paraguay. (2025). Manual de Orientación General para Trabajo de Conclusión de Carrera. Asunción, Paraguay.
Wila Bone, M., et al. (2025). Blockchain y transparencia contable en PYMES latinoamericanas. Revista Latinoamericana de Sistemas de Información.
Wood, G. (2014). Ethereum: A secure decentralised generalised transaction ledger. Ethereum Yellow Paper.
Declaración de Uso de Inteligencia Artificial (IA)
Estudiante: Pedro Pablo Narvaez Benitez
Carrera:  Ingenieria en Informstica
Título del Trabajo: Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada
Marque la opción correspondiente:
☐No utilicé herramientas de Inteligencia Artificial (IA) en la elaboración de este trabajo.
☑Sí utilicé herramientas de Inteligencia Artificial (IA) como apoyo académico.
En caso afirmativo, indicar:
Herramienta(s) utilizada(s):
Uso principal: [7.1]
☐ Exploración de ideas o enfoques
☐ Organización del contenido
 ☐ Asistencia en la redacción (con revisión propia)
 ☐ Otro:
Declaración de responsabilidad
Declaro que:
●	El trabajo presentado es producto de mi esfuerzo académico.
●	Todo contenido ha sido revisado y validado personalmente.
●	No se han fabricado datos ni simulado resultados o fuentes.
●	El uso de IA, si existió, se ajusta a las normas institucionales.

Fecha: ____ / ____ / ______

Firma del/de la estudiante:

Declaración de Uso de Inteligencia Artificial (IA)
Estudiante: Pedro Pablo Narvaez Benitez
Carrera:  Ingenieria en Informstica
Título del Trabajo: Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permisionada
Marque la opción correspondiente:
☐No utilicé herramientas de Inteligencia Artificial (IA) en la elaboración de este trabajo.
☑Sí utilicé herramientas de Inteligencia Artificial (IA) como apoyo académico.
En caso afirmativo, indicar:
Herramienta(s) utilizada(s):
Uso principal: [8.1]
☐ Exploración de ideas o enfoques
☐ Organización del contenido
 ☐ Asistencia en la redacción (con revisión propia)
 ☐ Otro:
Declaración de responsabilidad
Declaro que:
●	El trabajo presentado es producto de mi esfuerzo académico.
●	Todo contenido ha sido revisado y validado personalmente.
●	No se han fabricado datos ni simulado resultados o fuentes.
●	El uso de IA, si existió, se ajusta a las normas institucionales.

Fecha: ____ / ____ / ______

Firma del/de la estudiante:
Anexos
2.4	Anexo A. Presupuesto estimado de tecnologías
Concepto	Costo estimado (USD)	Observaciones
Licencias de software	0	Todo el núcleo usa biblioteca estándar Python
Lenguaje Python	0	Software libre y de código abierto
Base de datos SQLite	0	Incluida en biblioteca estándar
Framework Bootstrap 5	0	Licencia MIT, incluido localmente
Equipo de desarrollo	1.500	Hardware convencional
Servidor de despliegue (mensual)	15 - 50	Según modalidad: nube o local
Total estimado inicial	~ 1.500	Sin contar costos de personal
2.5	Anexo B. Cronograma de trabajo
Fase	Actividades principales	Semanas
Fase I	Planteamiento del problema y revisión bibliográfica	1 - 4
Fase II	Diseño arquitectónico detallado	5 - 8
Fase III	Implementación del prototipo funcional	9 - 16
Fase IV	Validación experimental y análisis	17 - 20
Fase V	Redacción del documento final y defensa	21 - 24


2.6	Anexo C. Glosario de términos técnicos
Blockchain permissionada. Red de libro mayor distribuido donde la participación está restringida a actores previamente autorizados.
Cadena de sellos. Implementación simplificada de blockchain utilizada en este trabajo, donde cada bloque sella un lote de documentos.
Función hash criptográfica. Función matemática que transforma una entrada en una salida de longitud fija con propiedades de resistencia a colisiones.
Efecto avalancha. Propiedad por la cual un cambio mínimo en la entrada produce un cambio aproximado de la mitad de los bits de salida.
Forma canónica. Representación normalizada que garantiza que el mismo dato produzca el mismo hash independientemente de dónde se calcule.
Encadenamiento criptográfico. Propiedad por la cual cada bloque contiene el hash del bloque anterior, haciendo que cualquier alteración histórica rompa toda la cadena.
Trilema de Buterin. Principio que establece que un sistema blockchain no puede maximizar simultáneamente descentralización, seguridad y escalabilidad.
Verificación en tres frentes. Mecanismo que verifica independientemente la cadena, el archivo físico y la base de datos antes de conciliar.
Regla de honestidad. Principio por el cual cada movimiento se cruza como máximo una vez y nunca se inventan coincidencias.
SHA-256. Algoritmo de hash seguro de 256 bits, estandarizado por el NIST y utilizado como base criptográfica de este trabajo.
