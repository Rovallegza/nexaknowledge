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

fig, ax=plt.subplots(figsize=(15,5.9)); fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.axis('off')
ax.set_xlim(-.15,15.15); ax.set_ylim(0,6)
ax.text(0,5.6,'ARQUITECTURA DEL PROTOTIPO',fontweight='bold',fontsize=20,color=NAVY,va='top')
ax.text(0,5.07,'Dos flujos de inteligencia artificial con un corpus documental compartido',fontsize=11,color=GRAY,va='top')

def box(x,y,w,h,title,sub,color='#EDF5FA'):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.1,rounding_size=.16',facecolor=color,edgecolor='#B3D1DD',linewidth=1.2))
 ax.text(x+w/2,y+h*.63,title,ha='center',va='center',color=NAVY,fontsize=12.2,fontweight='bold')
 ax.text(x+w/2,y+h*.30,sub,ha='center',va='center',color=TEXT,fontsize=9.5)

def arrow(x1,y1,x2,y2):
 ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=15,color=TEAL,linewidth=2))

ax.text(0,4.35,'A  |  RECUPERACIÓN SEMÁNTICA BÁSICA',fontsize=11.6,fontweight='bold',color=TEAL)
items=[('Consulta','Lenguaje natural'),('Ontología','Sinónimos conocidos'),('Vectorización','TF-IDF'),('Comparación','Coseno'),('Resultados','Ranking + puntaje')]
xs=[0,3.15,6.3,9.45,12.6]
for i,(t,s) in enumerate(items):
 box(xs[i],3.12,2.35,.88,t,s)
 if i<4: arrow(xs[i]+2.42,3.55,xs[i+1]-.12,3.55)
ax.text(0,2.45,'B  |  CLASIFICACIÓN AUTOMÁTICA',fontsize=11.6,fontweight='bold',color=TEAL)
items2=[('Documento nuevo','Contenido libre'),('Preparación','Texto y TF-IDF'),('Modelo de IA','Regresión logística'),('Predicción','Tipo + confianza')]
xs2=[0,3.75,7.5,11.25]
for i,(t,s) in enumerate(items2):
 box(xs2[i],1.16,3.02,.9,t,s,color='#F4F7FB')
 if i<3: arrow(xs2[i]+3.08,1.61,xs2[i+1]-.12,1.61)
ax.text(0,.38,'Ambos flujos usan los documentos ficticios; la búsqueda incorpora título, contenido y conceptos.',
       fontsize=10.2,color=GRAY)
fig.savefig(RES/'arquitectura.png',dpi=190,bbox_inches='tight',pad_inches=.2)
plt.close(fig)
print('Figuras creadas:',*[p.name for p in RES.glob('*.png')])
