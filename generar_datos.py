"""Genera el corpus DEMOSTRATIVO reproducible de NexaSoft Solutions."""
import json
from pathlib import Path

DIR=Path(__file__).resolve().parent

TEMAS=[
 ('Gestión de credenciales','Ciberseguridad','autenticación multifactor, contraseñas seguras, acceso privilegiado y gestión de identidad',['seguridad','autenticación','credenciales','accesos'], 'La organización reduce el riesgo de cuentas comprometidas y verifica la identidad antes de autorizar servicios.'),
 ('Respaldo y recuperación','Infraestructura','copias de seguridad, retención, almacenamiento redundante y restauración de datos',['respaldo','recuperación','continuidad','datos'], 'Los equipos protegen la continuidad operativa ante errores, pérdidas o fallas de infraestructura.'),
 ('Servicios API REST','Desarrollo','endpoints HTTP, contratos JSON, autenticación de API y manejo de códigos de error',['api','integración','desarrollo','autenticación'], 'Los módulos de software intercambian datos mediante servicios documentados con versionado y validación.'),
 ('Despliegue CI/CD','DevOps','integración continua, pruebas automatizadas, pipelines y despliegue a producción',['devops','despliegue','pruebas','automatización'], 'El equipo publica nuevas versiones con controles de calidad, aprobación y reversión.'),
 ('Atención de incidentes','Soporte','tickets de servicio, prioridades, escalamiento, tiempos SLA y diagnóstico de fallas',['incidentes','soporte','sla','monitoreo'], 'La mesa de ayuda restaura servicios afectados y comunica el estado a los usuarios.'),
 ('Análisis de indicadores','Analítica de Datos','tableros KPI, indicadores de negocio, limpieza de datos y trazabilidad de métricas',['datos','indicadores','calidad','analítica'], 'Los analistas convierten registros operativos en información para decisiones verificables.'),
 ('Protección de datos personales','Ciberseguridad','privacidad, cifrado, consentimiento, acceso mínimo y clasificación de información',['privacidad','seguridad','datos','cumplimiento'], 'La organización minimiza la exposición de datos sensibles durante el tratamiento y almacenamiento.'),
 ('Gestión de versiones','Desarrollo','repositorios Git, ramas de código, revisiones pull request y liberaciones',['git','desarrollo','versionado','calidad'], 'Los desarrolladores conservan trazabilidad de cambios y reducen conflictos al integrar funcionalidades.'),
 ('Monitoreo de servicios','Infraestructura','métricas de disponibilidad, alertas de servidores, logs y observabilidad',['monitoreo','infraestructura','alertas','disponibilidad'], 'Las alertas tempranas ayudan a identificar degradaciones antes de que afecten a los clientes.'),
 ('Gestión de proyectos ágiles','Gestión de Proyectos','historias de usuario, retrospectivas, tablero Kanban, sprints y prioridades',['agilidad','proyectos','colaboración','mejora'], 'Los equipos coordinan entregables y revisan avances para mejorar continuamente la entrega.'),
]
TIPOS=[
 ('Manual', 'Manual de uso', lambda tema,desc,ctx: f'Este manual explica cómo utilizar las herramientas relacionadas con {tema.lower()}. Incluye instrucciones para usuarios y administradores, ejemplos de operación de {desc}, recomendaciones de uso cotidiano y una sección de preguntas frecuentes. {ctx} La guía ofrece rutas de navegación, buenas prácticas y soluciones comunes para personal nuevo.'),
 ('Informe', 'Informe de resultados', lambda tema,desc,ctx: f'Este informe presenta hallazgos del periodo de revisión sobre {tema.lower()}. Analiza evidencias, resultados de indicadores, desviaciones y desempeño en {desc}. {ctx} Se registran riesgos identificados, conclusiones, responsables de seguimiento y recomendaciones de mejora para el próximo periodo.'),
 ('Política', 'Política corporativa', lambda tema,desc,ctx: f'Esta política establece requisitos obligatorios y criterios de cumplimiento para {tema.lower()}. Define las responsabilidades de colaboradores, líderes y auditores respecto a {desc}. {ctx} Incluye reglas de autorización, excepciones aprobadas, controles de supervisión y frecuencia de revisión para asegurar el cumplimiento institucional.'),
 ('Documentación técnica', 'Especificación técnica', lambda tema,desc,ctx: f'Esta documentación técnica describe la arquitectura, componentes e interfaces utilizados en {tema.lower()}. Detalla configuraciones, dependencias, parámetros, estructuras y decisiones de diseño asociadas con {desc}. {ctx} Se especifican requisitos de integración, restricciones técnicas, ejemplos de configuración y criterios de compatibilidad para ingeniería.'),
 ('Procedimiento', 'Procedimiento operativo', lambda tema,desc,ctx: f'Este procedimiento describe el flujo de trabajo estandarizado para {tema.lower()}. Paso 1: verificar los requisitos previos y la solicitud; paso 2: ejecutar los controles vinculados a {desc}; paso 3: registrar evidencia y validar el resultado; paso 4: notificar y cerrar la actividad. {ctx} Define responsables, puntos de control, criterios de aceptación y acciones de contingencia.'),
 ('Lección aprendida', 'Lección aprendida', lambda tema,desc,ctx: f'Esta lección aprendida documenta una experiencia de proyecto relacionada con {tema.lower()}. La situación inicial evidenció dificultades durante actividades de {desc}. El análisis de causa raíz permitió identificar oportunidades de prevención. {ctx} Se describen acciones correctivas implementadas, resultados observados y recomendaciones reutilizables en proyectos futuros.'),
]

def generar():
 docs=[]
 for tid,(tipo,prefijo,creador) in enumerate(TIPOS,1):
  for k,(tema,area,desc,conceptos,contexto) in enumerate(TEMAS,1):
   docid=f'NX-{tid:02d}{k:02d}'
   docs.append({
     'id':docid,
     'titulo':f'{prefijo}: {tema}',
     'tipo':tipo,
     'area':area,
     'conceptos':conceptos,
     'contenido':creador(tema,desc,contexto),
     'version':'1.0',
     'estado':'Vigente',
     'fecha_actualizacion':f'2026-10-{(k%27)+1:02d}',
     'origen':'Corpus ficticio para demostración académica'
   })
 return docs

if __name__=='__main__':
 ruta=DIR/'datos'/'documentos.json'
 ruta.write_text(json.dumps(generar(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(generar())} documentos generados en {ruta}')
