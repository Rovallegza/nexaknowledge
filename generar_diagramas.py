"""Genera figuras del proyecto para Word y Streamlit (matplotlib + Graphviz)."""
from pathlib import Path
from math import cos, sin, pi
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT=Path(__file__).resolve().parent
RES=ROOT/'recursos'
RES.mkdir(exist_ok=True)
NAVY='#10243A'; TEAL='#0D8796'; TEXT='#23344A'; LIGHT='#E9F3F8'; GRAY='#5E7388'

fig, ax=plt.subplots(figsize=(16,9.3))
fig.patch.set_facecolor('white'); ax.set_facecolor('white')
ax.set_xlim(-7.3,7.3); ax.set_ylim(-5,5.4); ax.axis('off')
ax.text(-7.1,5.15,'CICLO DE VIDA DEL CONOCIMIENTO',fontsize=21,fontweight='bold',color=NAVY,va='top')
ax.text(-7.1,4.65,'NexaSoft Solutions  |  Flujo de información y aprendizaje',fontsize=11.5,color=GRAY,va='top')
steps=[
 ('1. Creación y adquisición','Proyectos, investigación,\nsoporte y experiencia'),
 ('2. Almacenamiento','Repositorio con metadatos,\nversión y responsable'),
 ('3. Organización','Clasificación automática,\nconceptos y relaciones'),
 ('4. Compartir','Búsqueda, consulta y\nacceso por equipos'),
 ('5. Aplicación','Desarrollo, decisiones\ny resolución de incidentes'),
 ('6. Mejora continua','Validar, actualizar,\nretirar y retroalimentar'),
]
# inicia superior y sigue sentido horario
angles=[90,30,-30,-90,-150,150]
xy=[(4.86*cos(a*pi/180),3.31*sin(a*pi/180)) for a in angles]
for i in range(6):
 a=xy[i]; b=xy[(i+1)%6]
 arrow=FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=22,linewidth=2.5,
   color='#91B1C0',connectionstyle='arc3,rad=-0.12',shrinkA=64,shrinkB=64,zorder=1)
 ax.add_patch(arrow)
for i,((x,y),(name,subtitle)) in enumerate(zip(xy,steps)):
 patch=FancyBboxPatch((x-1.76,y-.64),3.52,1.28,boxstyle='round,pad=.13,rounding_size=.22',
                     edgecolor='#AFD9E3',facecolor='#F0F8FB',linewidth=1.8,zorder=5)
 ax.add_patch(patch)
 ax.text(x,y+.21,name,ha='center',va='center',color=NAVY,fontsize=13.2,fontweight='bold',zorder=6)
 ax.text(x,y-.25,subtitle,ha='center',va='center',color=TEXT,fontsize=10.5,linespacing=1.4,zorder=6)
center=Circle((0,0),1.55,facecolor=NAVY,edgecolor=TEAL,linewidth=3,zorder=4)
ax.add_patch(center)
ax.text(0,.43,'NEXA',color='white',fontsize=22,weight='bold',ha='center',zorder=6)
ax.text(0,-.04,'KNOWLEDGE',color='#75D7E1',fontsize=17,weight='bold',ha='center',zorder=6)
ax.text(0,-.62,'Aprendizaje\norganizacional',color='white',fontsize=11.5,ha='center',va='center',zorder=6)
ax.text(0,-4.80,'La salida de la mejora continua alimenta nuevas experiencias y reinicia el ciclo.',
        fontsize=10.5,color=GRAY,ha='center')
fig.savefig(RES/'ciclo_conocimiento.png',dpi=205,bbox_inches='tight',pad_inches=.18)
plt.close(fig)

ontology=r'''digraph ontology {
  graph [rankdir=LR,bgcolor="white",pad="0.3",nodesep="0.60",ranksep="1.35",splines=polyline,
         fontname="DejaVu Sans",label="NEXAKNOWLEDGE  |  ONTOLOGÍA ORGANIZACIONAL (ejemplos)",labelloc=t,
         fontsize=23,fontcolor="#10243A"];
  node [fontname="DejaVu Sans",fontsize=12,style="rounded,filled",shape=box,margin="0.23,0.14",color="#D3E3EB",penwidth=1.1];
  edge [fontname="DejaVu Sans",fontsize=10,color="#6E879A",fontcolor="#49697C",arrowsize=.75];
  org [label="Organización\nNexaSoft Solutions",fillcolor="#10243A",fontcolor="white",shape=box];

  subgraph cluster_areas { label="ÁREAS Y PROYECTOS"; color="#D5E5EC"; style="rounded"; fontname="DejaVu Sans"; fontsize=12;
    ciber [label="Área\nCiberseguridad",fillcolor="#EAF5FC"];
    infra [label="Área\nInfraestructura",fillcolor="#EAF5FC"];
    desarrollo [label="Área\nDesarrollo",fillcolor="#EAF5FC"];
  }
  subgraph cluster_docs { label="INSTANCIAS DE DOCUMENTO"; color="#BDDFE5"; style="rounded"; fontname="DejaVu Sans"; fontsize=12;
    d1 [label="NX-0307\nPolítica de datos personales",fillcolor="#E4F8F3"];
    d2 [label="NX-0102\nManual de respaldo",fillcolor="#E4F8F3"];
    d3 [label="NX-0403\nEspecificación API REST",fillcolor="#E4F8F3"];
  }
  subgraph cluster_types { label="TIPOS DOCUMENTALES"; color="#EDDDBC"; style="rounded"; fontname="DejaVu Sans"; fontsize=12;
    pol [label="Política",fillcolor="#FFF3DD"];
    man [label="Manual",fillcolor="#FFF3DD"];
    tec [label="Documentación\ntécnica",fillcolor="#FFF3DD"];
  }
  subgraph cluster_concepts { label="CONCEPTOS DEL DOMINIO"; color="#DAD5F5"; style="rounded"; fontname="DejaVu Sans"; fontsize=12;
    privacidad [label="Privacidad",fillcolor="#F1EDFF"];
    seguridad [label="Seguridad",fillcolor="#F1EDFF"];
    respaldo [label="Respaldo",fillcolor="#F1EDFF"];
    continuidad [label="Continuidad",fillcolor="#F1EDFF"];
    api [label="API REST",fillcolor="#F1EDFF"];
    integracion [label="Integración",fillcolor="#F1EDFF"];
  }
  org -> ciber [label="tieneArea"];
  org -> infra [label="tieneArea"];
  org -> desarrollo [label="tieneArea"];
  ciber -> d1 [label="documenta"];
  infra -> d2 [label="documenta"];
  desarrollo -> d3 [label="documenta"];
  d1 -> pol [label="tieneTipo"];
  d2 -> man [label="tieneTipo"];
  d3 -> tec [label="tieneTipo"];
  d1 -> privacidad [label="trataSobre"];
  d2 -> respaldo [label="trataSobre"];
  d3 -> api [label="trataSobre"];
  privacidad -> seguridad [label="relacionadoCon",style=dashed,color="#AA9ADB",constraint=false];
  respaldo -> continuidad [label="relacionadoCon",style=dashed,color="#AA9ADB",constraint=false];
  api -> integracion [label="relacionadoCon",style=dashed,color="#AA9ADB",constraint=false];
}
'''
(RES/'ontologia.dot').write_text(ontology,encoding='utf-8')
subprocess.run(['dot','-Tpng','-Gdpi=180',str(RES/'ontologia.dot'),'-o',str(RES/'ontologia.png')],check=True)
subprocess.run(['dot','-Tsvg',str(RES/'ontologia.dot'),'-o',str(RES/'ontologia.svg')],check=True)

W = 15.3                      # ancho de las bandas
XS = [0.40, 3.37, 6.34, 9.31, 12.28]   # columnas de los cinco servicios
AN = 2.62                     # ancho de cada columna
CEN = [x + AN / 2 for x in XS]

fig, ax = plt.subplots(figsize=(16, 10.8))
fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.axis('off')
ax.set_xlim(-.2, 16.6); ax.set_ylim(-.1, 10.9)

ax.text(0, 10.8, 'ARQUITECTURA DEL PROTOTIPO', fontweight='bold', fontsize=21, color=NAVY, va='top')
ax.text(0, 10.26, 'NexaKnowledge  |  Repositorio, procesamiento, control de acceso, interfaz y salidas',
        fontsize=11.5, color=GRAY, va='top')


def rotulo(y, texto, color=TEAL):
    ax.text(0.28, y, texto, fontsize=10.4, fontweight='bold', color=color, va='center', zorder=5)


def banda(y, h, color='#F6FAFC', borde='#DCE7EE'):
    ax.add_patch(FancyBboxPatch((0, y), W, h, boxstyle='round,pad=.04,rounding_size=.12',
                                facecolor=color, edgecolor=borde, linewidth=1.1, zorder=1))


def caja(x, y, w, h, title, sub, color='#EDF5FA', borde='#B3D1DD'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.07,rounding_size=.15',
                                facecolor=color, edgecolor=borde, linewidth=1.3, zorder=3))
    ax.text(x + w / 2, y + h * .66, title, ha='center', va='center',
            color=NAVY, fontsize=11.5, fontweight='bold', zorder=4)
    ax.text(x + w / 2, y + h * .27, sub, ha='center', va='center',
            color=TEXT, fontsize=9.1, linespacing=1.4, zorder=4)


def flecha(x, y1, y2, color=TEAL, lw=2.0):
    ax.add_patch(FancyArrowPatch((x, y1), (x, y2), arrowstyle='-|>', mutation_scale=14,
                                 color=color, linewidth=lw, zorder=2))


# 1 · REPOSITORIO DE DATOS
banda(8.50, 1.05)
rotulo(9.42, '1  |  REPOSITORIO DE DATOS')
caja(0.80, 8.62, 6.30, .62, 'datos/documentos.json', '67 documentos  ·  60 abiertos y 7 reservados')
caja(8.20, 8.62, 6.30, .62, 'datos/ontologia.json', '36 conceptos  ·  sinónimos y 10 relaciones')
flecha(3.95, 8.45, 7.95); flecha(11.35, 8.45, 7.95)

# 2 · PROCESAMIENTO
banda(6.85, 1.05)
rotulo(7.77, '2  |  COMPONENTES DE PROCESAMIENTO')
caja(0.80, 6.97, 6.30, .62, 'Vectorizador TF-IDF', 'unigramas y bigramas  ·  matriz 67 × V')
caja(8.20, 6.97, 6.30, .62, 'LogisticRegression', 'clasificador supervisado de seis tipos')
flecha(3.95, 6.80, 6.33); flecha(11.35, 6.80, 6.33)

# 3 · CONTROL DE ACCESO
ax.add_patch(FancyBboxPatch((0, 5.40), W, .88, boxstyle='round,pad=.04,rounding_size=.12',
                            facecolor=TEAL, edgecolor='#0A6E7A', linewidth=1.2, zorder=3))
rotulo(6.12, '3  |  CONTROL DE ACCESO', color='#C2EEF3')
ax.text(W / 2, 5.70, '_es_accesible(doc, permitir_confidenciales)   ·   filtro obligatorio previo a toda entrega',
        ha='center', va='center', color='white', fontsize=11.6, fontweight='bold', zorder=4)
for c in CEN:
    flecha(c, 5.35, 4.90, color='#8FB0BF')

# 4 · SERVICIOS DEL MOTOR
banda(3.30, 1.55)
rotulo(4.70, '4  |  SERVICIOS DEL MOTOR  (motor.py)')
servicios = [
    ('Búsqueda', 'TF-IDF y coseno\nexpansión ontológica'),
    ('Clasificación', 'probabilidad\nestimada por tipo'),
    ('Chatbot', 'recuperación y\nredacción extractiva'),
    ('Recomendación', 'por documento\ny por historial'),
    ('Grafo', 'subgrafo dirigido\ncon NetworkX'),
]
for x, (t, s) in zip(XS, servicios):
    caja(x, 3.44, AN, 1.08, t, s)
for c in CEN:
    flecha(c, 3.25, 2.88, color='#8FB0BF')

# 5 · INTERFAZ
ax.add_patch(FancyBboxPatch((0, 1.95), W, .88, boxstyle='round,pad=.04,rounding_size=.12',
                            facecolor=NAVY, edgecolor='#0A1826', linewidth=1.2, zorder=3))
rotulo(2.67, '5  |  INTERFAZ DE INTERACCIÓN', color='#75D7E1')
ax.text(W / 2, 2.25, 'Streamlit  ·  seis pestañas sincronizadas por st.session_state  ·  nexaknowledge.streamlit.app',
        ha='center', va='center', color='white', fontsize=11.4, fontweight='bold', zorder=4)
for c in CEN:
    flecha(c, 1.90, 1.70, color='#8FB0BF')

# 6 · SALIDAS
banda(0.30, 1.35, color='#FFFCF6', borde='#EEDDC2')
rotulo(1.50, '6  |  SALIDAS AL USUARIO', color='#B07A32')
salidas = [
    ('Ranking', 'documentos ordenados\npor similitud'),
    ('Tipo propuesto', 'categoría con\nprobabilidad'),
    ('Respuesta', 'texto redactado\ny fuentes citadas'),
    ('Sugerencias', 'documentos afines\ncon motivo'),
    ('Red visual', 'nodos, aristas\ny tabla de relaciones'),
]
for x, (t, s) in zip(XS, salidas):
    caja(x, 0.44, AN, .88, t, s, color='#FFF8EC', borde='#E8CFA3')

# retroalimentación: un documento incorporado en sesión vuelve al repositorio
ax.add_patch(FancyArrowPatch((15.52, 0.90), (15.52, 8.95), arrowstyle='-|>', mutation_scale=14,
                             color='#C2894A', linewidth=1.8, linestyle=(0, (5, 3)), zorder=2))
ax.text(16.02, 4.9, 'documento incorporado en sesión  →  reindexado', rotation=270,
        ha='center', va='center', fontsize=9.2, color='#9A6B33', zorder=4)

fig.savefig(RES/'arquitectura.png',dpi=175,bbox_inches='tight',pad_inches=.2)
plt.close(fig)
print('Figuras creadas:',*[p.name for p in RES.glob('*.png')])
