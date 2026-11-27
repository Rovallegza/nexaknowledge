"""Genera la ESTRUCTURA BASE del informe (fase de avance) en un archivo aparte.

ATENCIÓN: este script NO reproduce el informe final entregado.
El documento final, documentacion/Informe_NexaKnowledge.docx, incorpora
secciones y cifras añadidas después de esta fase: 7.7 control de acceso,
9.6 mejoras revisadas, 9.7 auditoría en producción, las métricas del catálogo
de 67 documentos y la revisión de coherencia. Esas se mantienen en el propio
.docx, no aquí.

Por eso la salida va a Informe_NexaKnowledge_base.docx: ejecutarlo nunca
sobrescribe el entregable.
"""
from __future__ import annotations
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'documentacion'/'Informe_NexaKnowledge_base.docx'
NAVY='10243A'; TEAL='0D8796'; LIGHT='EAF5F8'; MID='527187'; WHITE='FFFFFF'; SOFT='F3F7FA'; DARK='23344A'

def rgb(x): return RGBColor.from_string(x)

def shading(cell,color):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),color); tcPr.append(sh)

def cellmargin(cell, top=110, start=120, bottom=110, end=120):
    tc=cell._tc; tcPr=tc.get_or_add_tcPr()
    m=tcPr.first_child_found_in('w:tcMar')
    if m is None: m=OxmlElement('w:tcMar'); tcPr.append(m)
    for edge,val in (('top',top),('start',start),('bottom',bottom),('end',end)):
        el=m.find(qn('w:'+edge))
        if el is None: el=OxmlElement('w:'+edge); m.append(el)
        el.set(qn('w:w'),str(val)); el.set(qn('w:type'),'dxa')

def keep_together(p):
    p.paragraph_format.keep_together=True

def keep_with_next(p):
    p.paragraph_format.keep_with_next=True

def page(): pass  # el título siguiente lleva page_break_before, sin páginas vacías

def body(text='', bold_prefix=None):
    p=doc.add_paragraph(style='Body Text')
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold=True; p.add_run(text[len(bold_prefix):])
    else: p.add_run(text)
    return p

def title(text):
    p=doc.add_paragraph(style='Heading 1');p.paragraph_format.page_break_before=True;p.add_run(text);return p

def sub(text):
    p=doc.add_paragraph(style='Heading 2');p.add_run(text);return p

def bullet(text):
    p=doc.add_paragraph(style='List Bullet'); p.add_run(text);return p

def numbered(text):
    p=doc.add_paragraph(style='List Number');p.add_run(text);return p

def note(text):
    p=doc.add_paragraph(style='Nota');p.add_run(text);return p

def code(text):
    p=doc.add_paragraph(style='Formula');p.add_run(text);return p

def figure(path, caption, width=6.6):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ROOT/'recursos'/path),width=Inches(width))
    p.paragraph_format.space_after=Pt(2)
    cap=doc.add_paragraph(style='Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    cap.add_run(caption)
    return p

def make_table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.style='Table Grid'
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i];c.text=str(h);shading(c,NAVY);cellmargin(c)
        for run in c.paragraphs[0].runs: run.bold=True;run.font.color.rgb=rgb(WHITE);run.font.size=Pt(9)
    trPr=t.rows[0]._tr.get_or_add_trPr();tblHeader=OxmlElement('w:tblHeader');tblHeader.set(qn('w:val'),'true');trPr.append(tblHeader)
    for idx,row in enumerate(rows):
        cells=t.add_row().cells
        for j,v in enumerate(row):
            c=cells[j];c.text=str(v)
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;cellmargin(c)
            if idx%2==1: shading(c,SOFT)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(1)
                for run in par.runs:run.font.size=Pt(8.6);run.font.color.rgb=rgb(DARK)
    if widths:
        t.autofit=False
        for row in t.rows:
            for i,c in enumerate(row.cells): c.width=Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

doc=Document()
sec=doc.sections[0]
sec.top_margin=Inches(.76);sec.bottom_margin=Inches(.70)
sec.left_margin=Inches(.85);sec.right_margin=Inches(.85)
sec.header_distance=Inches(.31);sec.footer_distance=Inches(.35)
sec.page_height=Inches(11.69);sec.page_width=Inches(8.27) # A4

styles=doc.styles
styles['Normal'].font.name='Aptos';styles['Normal'].font.size=Pt(9.6);styles['Normal'].font.color.rgb=rgb(DARK)
styles['Normal'].paragraph_format.space_after=Pt(5)
styles['Body Text'].font.name='Aptos';styles['Body Text'].font.size=Pt(9.4)
styles['Body Text'].font.color.rgb=rgb(DARK)
styles['Body Text'].paragraph_format.line_spacing=1.14
styles['Body Text'].paragraph_format.space_after=Pt(5)
styles['Heading 1'].font.name='Aptos Display';styles['Heading 1'].font.size=Pt(19);styles['Heading 1'].font.bold=True
styles['Heading 1'].font.color.rgb=rgb(NAVY);styles['Heading 1'].paragraph_format.space_before=Pt(2);styles['Heading 1'].paragraph_format.space_after=Pt(11)
styles['Heading 2'].font.name='Aptos';styles['Heading 2'].font.size=Pt(11.8);styles['Heading 2'].font.bold=True
styles['Heading 2'].font.color.rgb=rgb(TEAL);styles['Heading 2'].paragraph_format.space_before=Pt(10);styles['Heading 2'].paragraph_format.space_after=Pt(4)
styles['Caption'].font.name='Aptos';styles['Caption'].font.size=Pt(8.5);styles['Caption'].font.italic=True;styles['Caption'].font.color.rgb=rgb(MID)
styles['List Bullet'].font.name='Aptos';styles['List Bullet'].font.size=Pt(9.4);styles['List Bullet'].paragraph_format.space_after=Pt(3)
styles['List Number'].font.name='Aptos';styles['List Number'].font.size=Pt(9.4);styles['List Number'].paragraph_format.space_after=Pt(3)
for name in ('Nota','Formula'):
    if name not in styles: styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
styles['Nota'].font.name='Aptos';styles['Nota'].font.size=Pt(8.7);styles['Nota'].font.color.rgb=rgb(MID);styles['Nota'].font.italic=True
styles['Nota'].paragraph_format.space_after=Pt(7)
styles['Formula'].font.name='Consolas';styles['Formula'].font.size=Pt(9.3);styles['Formula'].font.color.rgb=rgb(NAVY)
styles['Formula'].paragraph_format.left_indent=Inches(.19);styles['Formula'].paragraph_format.space_after=Pt(6)

# header/footer
header=sec.header.paragraphs[0]; header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
run=header.add_run('NEXAKNOWLEDGE  /  INFORME ACADÉMICO');run.font.name='Aptos';run.font.size=Pt(8);run.font.bold=True;run.font.color.rgb=rgb(MID)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('NexaSoft Solutions  •  Prototipo académico  |  Página ');r.font.size=Pt(8);r.font.color.rgb=rgb(MID)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

# Page 1 cover
p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(85)
r=p.add_run('TECNOLOGÍAS DE INTELIGENCIA ARTIFICIAL');r.font.size=Pt(10);r.font.bold=True;r.font.color.rgb=rgb(TEAL)
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(13)
r=p.add_run('NexaKnowledge');r.font.name='Aptos Display';r.font.size=Pt(38);r.font.bold=True;r.font.color.rgb=rgb(NAVY)
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(0)
r=p.add_run('Sistema inteligente de gestión del conocimiento');r.font.size=Pt(17);r.font.color.rgb=rgb(TEAL)
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(18)
r=p.add_run('Clasificación automática de documentos y recuperación semántica básica con TF-IDF');r.font.size=Pt(12);r.font.color.rgb=rgb(DARK)
figp=doc.add_paragraph();figp.alignment=WD_ALIGN_PARAGRAPH.CENTER;figp.paragraph_format.space_before=Pt(30)
figp.add_run().add_picture(str(ROOT/'recursos'/'arquitectura.png'),width=Inches(6.45))
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(28)
r=p.add_run('ORGANIZACIÓN FICTICIA');r.font.size=Pt(9);r.font.bold=True;r.font.color.rgb=rgb(MID)
p=doc.add_paragraph();r=p.add_run('NexaSoft Solutions  |  Empresa tecnológica');r.bold=True;r.font.size=Pt(13);r.font.color.rgb=rgb(NAVY)
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(17)
r=p.add_run('Informe técnico y documentación de progreso del prototipo');r.font.color.rgb=rgb(DARK);r.font.size=Pt(10.5)
p=doc.add_paragraph();r=p.add_run('9 de noviembre de 2026  ·  Versión 1.0');r.font.color.rgb=rgb(MID);r.font.size=Pt(9)

page()
# Page 2 executive

title('1. Resumen ejecutivo y alcance')
body('Se diseñó e implementó NexaKnowledge, un prototipo local para capturar, clasificar, organizar y recuperar conocimiento técnico en NexaSoft Solutions. Su finalidad es disminuir el tiempo necesario para localizar políticas, manuales y soluciones previas, así como reducir la dispersión del conocimiento entre departamentos.')
body('El sistema contiene 60 documentos ficticios y etiquetados, distribuidos entre seis tipos y siete áreas. Incluye un motor de búsqueda TF-IDF con similitud del coseno, expansión de consultas con equivalencias de una ontología, clasificador supervisado y una interfaz web de demostración con Streamlit.')
sub('Objetivo general')
body('Desarrollar un prototipo de sistema de gestión del conocimiento que use técnicas de inteligencia artificial para clasificar documentos automáticamente y recuperar información a partir de consultas en lenguaje natural.')
sub('Objetivos específicos')
for txt in [
 'Caracterizar una organización tecnológica y los documentos que produce.',
 'Representar las seis etapas del ciclo de vida del conocimiento.',
 'Modelar un dominio documental con ontología, conjuntos y lógica de primer orden.',
 'Vectorizar consultas y documentos con TF-IDF y jerarquizar resultados por similitud coseno.',
 'Implementar clasificación supervisada para seis tipos y comprobar su comportamiento con pruebas automatizadas.'
]:bullet(txt)
sub('Alcance funcional de esta entrega')
make_table(['Componente','Evidencia disponible','Estado'],[
 ('Empresa ficticia','Descripción de áreas, actividades y tipos documentales','Completado'),
 ('Mapa de ciclo de vida','Seis etapas enlazadas y retroalimentación','Completado'),
 ('Ontología','Clases, instancias, relaciones y equivalencias','Completado'),
 ('Búsqueda','Consulta → TF-IDF → coseno → clasificación de resultados','Completado'),
 ('Clasificador','TF-IDF + regresión logística de seis categorías','Completado'),
 ('Interfaz y pruebas','Aplicación local y 9 pruebas automatizadas','Completado'),
])
note('Todos los documentos usados como ejemplos son sintéticos. El prototipo no integra bases de datos corporativas ni controla permisos de acceso.')

page()
# Page 3 org

title('2. Definición de la empresa ficticia')
sub('2.1 Perfil organizacional')
body('Nombre: NexaSoft Solutions. Tipo: empresa tecnológica B2B que desarrolla soluciones de software y presta servicios de infraestructura, ciberseguridad, analítica y soporte a otras organizaciones. La empresa dispone de equipos distribuidos; parte importante de sus decisiones queda registrada en documentos, tickets y repositorios técnicos.')
sub('2.2 Actividades principales')
make_table(['Área','Actividades y conocimiento que produce'],[
 ('Desarrollo','Diseño de aplicaciones web, APIs, integración, control de versiones y revisión de código.'),
 ('DevOps','Integración y despliegue continuo, automatización, monitoreo de entregas y configuración de entornos.'),
 ('Infraestructura','Administración de servidores, respaldo, disponibilidad, continuidad y recuperación.'),
 ('Ciberseguridad','Control de acceso, protección de datos, gestión de credenciales y auditoría.'),
 ('Analítica de Datos','Limpieza de datos, indicadores, informes, análisis y cuadros de mando.'),
 ('Soporte','Atención de incidencias, escalamiento y gestión de niveles de servicio.'),
 ('Gestión de Proyectos','Planificación ágil, retrospectivas, asignación de responsabilidades y seguimiento.'),
])
sub('2.3 Tipos de documentos y conocimiento')
make_table(['Tipo','Ejemplo dentro del prototipo','Uso'],[
 ('Manual','Manual de uso: Respaldo y recuperación','Explicar la operación de herramientas.'),
 ('Informe','Informe de resultados: Análisis de indicadores','Comunicar hallazgos y métricas.'),
 ('Política','Política corporativa: Protección de datos personales','Establecer obligaciones y controles.'),
 ('Documentación técnica','Especificación técnica: Servicios API REST','Describir arquitectura e interfaces.'),
 ('Procedimiento','Procedimiento operativo: Atención de incidentes','Estandarizar pasos y evidencias.'),
 ('Lección aprendida','Lección aprendida: Despliegue CI/CD','Reutilizar experiencia y prevenir errores.'),
])

page()
# Page 4 cycle

title('3. Mapa del ciclo de vida del conocimiento')
figure('ciclo_conocimiento.png','Figura 1. Proceso iterativo de seis etapas para NexaSoft Solutions.',width=6.55)
sub('Actividades y responsables por etapa')
make_table(['Etapa','Actividad concreta','Responsable típico'],[
 ('1. Crear / adquirir','Generar resultados de proyectos, investigar tecnologías y registrar incidentes.','Especialistas y líderes'),
 ('2. Almacenar','Guardar documentos con ID, área, tipo, versión y fecha.','Autor y responsable documental'),
 ('3. Clasificar','Asignar tipo automáticamente y etiquetar conceptos vinculados.','Motor IA + validador'),
 ('4. Compartir','Consultar por preguntas, revisar resultados y difundir recursos aprobados.','Colaboradores'),
 ('5. Aplicar','Resolver incidencias, desarrollar software o respaldar una decisión.','Equipos operativos'),
 ('6. Actualizar','Corregir documentos, sustituir versiones y registrar aprendizajes nuevos.','Dueño de conocimiento'),
])
note('El circuito se cierra cuando el uso del documento genera nueva experiencia y dispara una revisión o una publicación adicional.')

page()
# Page 5 graph

title('4. Ontología y gráfico conceptual')
body('La ontología define qué entidades existen en el dominio, cuáles son sus categorías y cómo se relacionan. Se construyó un esquema pequeño, legible y ampliable, conectado con el catálogo documental.')
figure('ontologia.png','Figura 2. Instancias de conocimiento y relaciones semánticas (extracto de la ontología).',width=6.6)
note('El diagrama muestra tres documentos de ejemplo. El archivo datos/ontologia.json contiene más áreas, tipos, conceptos y equivalencias para búsqueda.')
sub('Lectura del gráfico')
body('Por ejemplo: el documento NX-0102 pertenece al área Infraestructura, tiene tipo Manual y trata sobre el concepto Respaldo; el concepto Respaldo se relaciona con Continuidad. Estas relaciones permiten conectar una necesidad operativa con fuentes documentales relevantes.')

page()
# Page 6 sets

title('5. Formalización: teoría de conjuntos')
body('Se definen conjuntos y relaciones para que la estructura conceptual pueda expresarse de forma verificable, en vez de conservarse únicamente como un diagrama.')
sub('5.1 Conjuntos base')
code('D = {d₁, d₂, …, d₆₀}                        documentos registrados')
code('T = {Manual, Informe, Política, Doc. técnica, Procedimiento, Lección aprendida}')
code('A = {Desarrollo, DevOps, Infraestructura, Ciberseguridad, Analítica, Soporte, Proyectos}')
code('C = {seguridad, respaldo, API, recuperación, privacidad, …}   33 conceptos')
code('P = {p₁, p₂, …}                            proyectos (extensión futura)')
code('U = {u₁, u₂, …}                            autores o usuarios (extensión futura)')
sub('5.2 Funciones, relaciones e intersecciones')
code('tipo : D → T               cada documento tiene exactamente un tipo')
code('area : D → A               cada documento se adscribe a un área')
code('trataSobre ⊆ D × C        un documento puede abordar varios conceptos')
code('relacionadoCon ⊆ C × C    conceptos que guardan relación contextual')
code('actualiza ⊆ D × D         una versión documental sustituye a otra')
body('Ejemplos de operaciones de conjuntos:')
code('D_seguridad = {d ∈ D | seguridad ∈ conceptos(d)}')
code('D_politicas = {d ∈ D | tipo(d) = Política}')
code('D_seguridad ∩ D_politicas = políticas que tratan sobre seguridad')
code('D_Infraestructura ∪ D_DevOps = documentos de ambas áreas')
sub('5.3 Instancias específicas')
body('NX-0307 ∈ D_politicas, trataSobre(NX-0307, privacidad) y area(NX-0307) = Ciberseguridad. NX-0102 ∈ D_manuales, trataSobre(NX-0102, respaldo) y area(NX-0102) = Infraestructura.')
sub('5.4 Reglas de integridad conceptual')
for x in [
 'Todo documento necesita identificador, título, contenido, tipo y área.',
 'El identificador debe ser único; un documento puede tener múltiples conceptos.',
 'Los metadatos de categoría producidos por IA se revisan antes de su uso institucional.',
 'Las futuras versiones deberán enlazarse con el documento que actualizan.'
]:bullet(x)

page()
# Page 7 FOL

title('6. Ontología con lógica de primer orden')
body('La lógica de primer orden permite representar restricciones y consultar inferencias sobre las relaciones. Se emplea la notación Documento(x), Tipo(t), Concepto(c), TieneTipo(x,t), TrataSobre(x,c), PerteneceA(x,a), Actualiza(y,x).')
sub('6.1 Reglas fundamentales')
code('R1: ∀d [Documento(d) → ∃t (Tipo(t) ∧ TieneTipo(d,t))]')
body('Cada documento tiene, al menos, un tipo. Para exigir unicidad se complementa con R2:')
code('R2: ∀d∀t₁∀t₂ [(TieneTipo(d,t₁) ∧ TieneTipo(d,t₂)) → t₁ = t₂]')
code('R3: ∀d [Documento(d) → ∃c (Concepto(c) ∧ TrataSobre(d,c))]')
body('Los documentos del corpus inicial tienen uno o más conceptos asignados.')
code('R4: ∀d∀c [(TrataSobre(d,c) ∧ Concepto(c)) → RecuperablePor(d,c)]')
body('Si un documento trata sobre un concepto, el concepto puede usarse como pista para localizarlo (sin garantizar relevancia perfecta).')
code('R5: ∀d∀e [Actualiza(d,e) → (Documento(d) ∧ Documento(e))]')
body('Las relaciones de actualización conectan documentos válidos. El prototipo todavía no aplica reglas de versionado automáticamente.')
sub('6.2 Hechos y ejemplo de consulta conceptual')
code('Documento(NX-0102)')
code('TieneTipo(NX-0102, Manual)')
code('PerteneceA(NX-0102, Infraestructura)')
code('TrataSobre(NX-0102, respaldo)')
code('RelacionadoCon(respaldo, continuidad)')
body('Pregunta formal de ejemplo: ¿qué manuales tratan sobre respaldo?')
code('Q(d) = Documento(d) ∧ TieneTipo(d, Manual) ∧ TrataSobre(d, respaldo)')
body('La evaluación de Q(d) incluye NX-0102. En el prototipo, estos hechos se expresan en los campos tipo, area y conceptos del JSON y en el diccionario conceptual; no se implementó un razonador lógico completo.')
note('El gráfico conceptual representa semántica explícita. TF-IDF y el coseno constituyen el mecanismo de recuperación; los dos subsistemas son complementarios, no equivalentes.')

page()
# Page 8 architecture and steps

title('7. Implementación del prototipo')
figure('arquitectura.png','Figura 3. Arquitectura del prototipo: repositorio de datos, componentes de procesamiento, capa de control de acceso, servicios del motor, interfaz de interacción y salidas al usuario.',width=6.60)
sub('7.1 Estructura del corpus')
body('Cada registro JSON tiene los campos id, titulo, tipo, area, conceptos, contenido, version, estado, fecha_actualizacion y origen. Se generaron 10 temas organizacionales por cada uno de los seis tipos de documento: 60 registros en total. El texto indexado combina título, contenido, área y conceptos, mientras el clasificador aprende únicamente a partir del contenido.')
sub('7.2 Búsqueda: procedimiento implementado')
for x in [
 'El usuario introduce una pregunta en lenguaje natural y, de forma opcional, un filtro por tipo.',
 'La ontología extiende la consulta con equivalencias conocidas como «backup» ↔ «respaldo».',
 'El vectorizador TF-IDF entrenado sobre el catálogo transforma la consulta usando el mismo vocabulario.',
 'Se calcula la similitud coseno entre la consulta y los 60 vectores de documentos.',
 'Se ordenan los resultados por puntaje descendente y se excluyen coincidencias con puntuación cero.'
]:numbered(x)
sub('7.3 Clasificación: procedimiento implementado')
body('Se entrena un pipeline con TfidfVectorizer (unigramas y bigramas) y LogisticRegression multiclase. Cuando se introduce un nuevo texto, el sistema calcula la probabilidad estimada para cada tipo y propone la categoría de mayor valor. La interfaz permite incorporar ese texto al catálogo durante la sesión, con estado «Pendiente de revisión».')

page()
# page 9 formulas and demo

title('8. TF-IDF, coseno y demostración')
sub('8.1 Representación numérica')
body('TF-IDF pondera los términos según su frecuencia en un documento y su escasez relativa en el corpus. Se usan unigramas y bigramas, normalización de acentos y frecuencia sublineal. El vectorizador se ajusta al catálogo antes de transformar las consultas.')
code('TF-IDF(t,d) = TF(t,d) × IDF(t)')
code('IDF(t) = ln[(1 + N) / (1 + df(t))] + 1     [suavizado estándar]')
body('La similitud del coseno compara orientaciones de vectores; en una matriz TF-IDF no negativa, valores más altos indican mayor coincidencia ponderada de términos. No son porcentajes de certeza ni probabilidades de relevancia.')
code('sim(q,d) = (q · d) / (||q||₂ × ||d||₂)')
sub('8.2 Ejemplo ejecutado en el corpus')
body('Consulta: «Cómo recuperar archivos después de un fallo de servidor». Con expansión de equivalencias habilitada, la ejecución local produjo los siguientes primeros resultados:')
make_table(['Posición','Documento','Similitud'],[
 ('1','NX-0102  ·  Manual de uso: Respaldo y recuperación','0.22519'),
 ('2','NX-0202  ·  Informe de resultados: Respaldo y recuperación','0.21405'),
 ('3','NX-0302  ·  Política corporativa: Respaldo y recuperación','0.21350'),
])
body('Interpretación: los tres documentos comparten el tema respaldo y recuperación, pero difieren en intención: enseñar a usar una herramienta, informar resultados o fijar obligaciones. El usuario puede filtrar por el tipo que necesite.')
sub('8.3 Clasificación automática')
body('Nuevo texto de prueba: «Esta política corporativa establece responsabilidades obligatorias, requisitos de cumplimiento y controles de acceso para los usuarios». El clasificador propuso Política, con probabilidad estimada cercana a 0.351. Esta cifra no es una confianza calibrada y evidencia la necesidad de revisión humana.')

page()
# Page 10 test and progress

title('9. Progreso, pruebas y evaluación')
sub('9.1 Estado de los entregables')
make_table(['Actividad','Producto entregado','Estado'],[
 ('Definición organizacional','Empresa, actividades y seis tipos documentales','Finalizado'),
 ('Ciclo de vida','Diagrama de seis etapas con retroalimentación','Finalizado'),
 ('Ontología','JSON, gráfico, conjuntos y reglas de primer orden','Finalizado'),
 ('Conjunto documental','60 documentos ficticios reproducibles','Finalizado'),
 ('Implementación','motor.py, app.py y pruebas','Finalizado'),
 ('Validación sobre datos reales','Corpus independiente etiquetado por expertos','Pendiente'),
 ('Producción','Autorizaciones, auditoría y persistencia','Pendiente'),
])
sub('9.2 Pruebas funcionales')
body('Se ejecutaron nueve pruebas con pytest: tamaño del corpus, distribución por tipos, ordenamiento de resultados, filtros, consultas vacías o sin coincidencia, expansión de sinónimos, predicción de categoría, incorporación temporal de documentos y normalización textual. Resultado de la ejecución: 9 pruebas aprobadas.')
sub('9.3 Validación del clasificador')
body('La validación cruzada estratificada con cinco pliegues sobre los 60 textos de demostración arrojó accuracy medio = 1.00 (desviación = 0.00). Esta puntuación NO demuestra precisión fuera del prototipo: los textos se redactaron a partir de plantillas repetidas por tipo documental, de modo que el modelo puede aprender su estructura artificial. Se recomienda evaluación externa con documentos reales de distintos autores y formatos, sin frases de plantilla compartidas entre entrenamiento y prueba.')
sub('9.4 Riesgos y limitaciones')
for x in [
 'TF-IDF identifica principalmente similitud léxica; paráfrasis profundas y sinónimos no declarados pueden fallar.',
 'Los sinónimos se ampliaron manualmente y pueden introducir falsos positivos.',
 'La incorporación de nuevos documentos es temporal y no dispone de revisión ni trazabilidad editorial completa.',
 'El prototipo no implementa OCR, bases de datos, permisos por rol ni inferencia formal de reglas.',
 'El resultado no debe usarse como sistema empresarial sin seguridad, pruebas y gobernanza adicionales.'
]:bullet(x)

page()
# Page 11 instructions

title('10. Ejecución, conclusiones y fuentes')
sub('10.1 Requisitos y ejecución')
body('Se necesita Python 3.10 o superior. Los archivos se encuentran en la carpeta del proyecto; la aplicación funciona en una máquina local. Comandos recomendados:')
code('python -m venv .venv')
code('python -m pip install -r requirements.txt')
code('streamlit run app.py')
code('python motor.py --consulta "¿Cómo restaurar archivos?" --top 5')
code('python motor.py --clasificar "Esta política exige controles de acceso"')
code('python -m pytest -q')
sub('10.2 Conclusión')
body('NexaKnowledge articula una organización ficticia, el ciclo del conocimiento, una ontología explícita y un motor operativo de búsqueda y clasificación. Demuestra cómo un esquema conceptual puede apoyar una recuperación TF-IDF más flexible mediante equivalencias de términos y cómo un clasificador supervisado facilita el ordenamiento inicial del repositorio. El producto es un prototipo académico reproducible, no una solución de producción ni un sistema de comprensión semántica profunda.')
sub('10.3 Próximas mejoras priorizadas')
for t in ['Recolectar documentos reales anonimizados y acordar criterios de etiquetado.',
          'Medir macro-F1, matriz de confusión y Recall@k con un conjunto externo.',
          'Añadir almacenamiento persistente, flujos de aprobación y control de versiones.',
          'Aplicar perfiles de acceso, auditoría y políticas de conservación.',
          'Comparar TF-IDF con embeddings y recuperación híbrida.']:
    numbered(t)
sub('10.4 Referencias técnicas')
body('scikit-learn. Feature extraction: TF-IDF y representación de documentos. https://scikit-learn.org/stable/modules/feature_extraction.html')
body('scikit-learn. Pairwise metrics: cosine similarity. https://scikit-learn.org/stable/modules/metrics.html')
body('scikit-learn. LogisticRegression (clasificación supervisada). https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html')
body('Manning, C. D., Raghavan, P. y Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press.')

# core props
props=doc.core_properties
props.title='NexaKnowledge - Sistema inteligente de gestión del conocimiento'
props.subject='Prototipo de clasificación documental y recuperación TF-IDF'
props.keywords='gestión del conocimiento; ontología; TF-IDF; similitud coseno; clasificación'
props.author='Proyecto académico - NexaSoft Solutions'
props.comments='Documentos y organización ficticios. Uso académico.'
OUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUT)
print('AVISO: esto es la estructura base de la fase de avance, no el informe final.')
print('El entregable vive en documentacion/Informe_NexaKnowledge.docx y no se ha tocado.')
print(OUT)
