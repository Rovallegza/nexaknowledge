"""Interfaz integrada de NexaKnowledge. Ejecutar: streamlit run app.py"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from motor import SistemaConocimiento, normalizar

ROOT = Path(__file__).resolve().parent
st.set_page_config(
    page_title='NexaKnowledge | Gestión del conocimiento',
    page_icon='📚',
    layout='wide',
)

st.markdown('''<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1240px;}
h1, h2, h3 {letter-spacing: -0.03em;}
div[data-testid="stMetric"] {background:#eff6ff; border:1px solid #dbeafe; padding:12px; border-radius:12px;}
</style>''', unsafe_allow_html=True)

if 'sistema' not in st.session_state:
    st.session_state.sistema = SistemaConocimiento()
if 'historial_consultas' not in st.session_state:
    st.session_state.historial_consultas = []
if 'doc_foco_id' not in st.session_state:
    st.session_state.doc_foco_id = 'NX-0102'

sistema: SistemaConocimiento = st.session_state.sistema
stats = sistema.estadisticas()


def registrar_consulta(texto: str) -> None:
    limpio = texto.strip()
    if not limpio:
        return
    hist = st.session_state.historial_consultas
    if not hist or hist[-1] != limpio:
        hist.append(limpio)
    st.session_state.historial_consultas = hist[-10:]


def seleccionar_documento_foco(doc_id: str) -> None:
    st.session_state.doc_foco_id = doc_id
    doc_obj = next((d for d in sistema.documentos if d['id'] == doc_id), None)
    if doc_obj:
        st.session_state.g_foco = f"{doc_obj['id']} — {doc_obj['titulo']}"
        st.session_state.rec_doc_sel = f"{doc_obj['id']} — {doc_obj['titulo']} ({doc_obj['tipo']})"


def construir_subgrafo(area_filtro: str, tipo_filtro: str, concepto_filtro: str,
                       doc_foco_id: str | None) -> tuple[nx.MultiDiGraph, list[dict]]:
    grafo = nx.MultiDiGraph()
    docs_filtrados = []
    for d in sistema.documentos:
        # Los documentos restringidos no se representan como nodos en la red visual.
        if d.get('confidencial', False):
            continue
        if area_filtro != 'Todas' and d['area'] != area_filtro:
            continue
        if tipo_filtro != 'Todos' and d['tipo'] != tipo_filtro:
            continue
        if concepto_filtro != 'Todos' and concepto_filtro not in d.get('conceptos', []):
            continue
        docs_filtrados.append(d)

    # Limitar a 10 documentos visibles para mantener el grafo legible
    docs_visibles = docs_filtrados[:10]
    if doc_foco_id:
        foco_obj = next((d for d in sistema.documentos
                         if d['id'] == doc_foco_id and not d.get('confidencial', False)), None)
        if foco_obj and all(d['id'] != foco_obj['id'] for d in docs_visibles):
            docs_visibles = [foco_obj, *docs_visibles[:9]]

    aristas_tabla: list[dict] = []

    for d in docs_visibles:
        nodo_doc = f"DOC:{d['id']}"
        nodo_area = f"AREA:{d['area']}"
        nodo_tipo = f"TIPO:{d['tipo']}"

        grafo.add_node(nodo_doc, label=f"{d['id']}\n{d['titulo'][:24]}", grupo='Documento')
        grafo.add_node(nodo_area, label=f"Área\n{d['area']}", grupo='Categoría (Área)')
        grafo.add_node(nodo_tipo, label=f"Tipo\n{d['tipo']}", grupo='Categoría (Tipo)')

        grafo.add_edge(nodo_doc, nodo_area, relacion='perteneceA')
        aristas_tabla.append({'Origen': d['id'], 'Relación': 'perteneceA', 'Destino': d['area']})

        grafo.add_edge(nodo_doc, nodo_tipo, relacion='tieneTipo')
        aristas_tabla.append({'Origen': d['id'], 'Relación': 'tieneTipo', 'Destino': d['tipo']})

        for conc in d.get('conceptos', []):
            nodo_conc = f"CONC:{conc}"
            grafo.add_node(nodo_conc, label=conc, grupo='Concepto')
            grafo.add_edge(nodo_doc, nodo_conc, relacion='trataSobre')
            aristas_tabla.append({'Origen': d['id'], 'Relación': 'trataSobre', 'Destino': conc})

    conceptos_presentes = [
        n.split(':', 1)[1] for n, attrs in grafo.nodes(data=True) if attrs.get('grupo') == 'Concepto'
    ]
    for c1 in conceptos_presentes:
        for c2 in conceptos_presentes:
            if c1 < c2 and c2 in sistema.ontologia.get('sinonimos_de_consulta', {}).get(c1, []):
                grafo.add_edge(f"CONC:{c1}", f"CONC:{c2}", relacion='relacionadoCon')
                aristas_tabla.append({'Origen': c1, 'Relación': 'relacionadoCon', 'Destino': c2})

    return grafo, aristas_tabla


def dibujar_grafo(grafo: nx.MultiDiGraph, doc_foco_id: str | None):
    fig, ax = plt.subplots(figsize=(11, 6.2))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.axis('off')

    if grafo.number_of_nodes() == 0:
        ax.text(0.5, 0.5, 'Sin nodos para los filtros seleccionados', ha='center', va='center')
        return fig

    pos = nx.spring_layout(grafo, seed=42, k=1.15)
    colores_grupo = {
        'Documento': '#10243A',
        'Categoría (Área)': '#0D8796',
        'Categoría (Tipo)': '#D97706',
        'Concepto': '#6D28D9',
    }

    vecinos_foco = set()
    nodo_foco = f"DOC:{doc_foco_id}" if doc_foco_id else None
    if nodo_foco and nodo_foco in grafo:
        vecinos_foco = set(grafo.predecessors(nodo_foco)) | set(grafo.successors(nodo_foco)) | {nodo_foco}

    for u, v, data in grafo.edges(data=True):
        es_resaltada = bool(vecinos_foco and (u in vecinos_foco and v in vecinos_foco))
        nx.draw_networkx_edges(
            grafo, pos, edgelist=[(u, v)], ax=ax,
            edge_color='#0D8796' if es_resaltada else '#CBD5E1',
            width=2.2 if es_resaltada else 1.1,
            arrows=True, arrowsize=14,
            connectionstyle='arc3,rad=0.06',
        )

    for grupo, color in colores_grupo.items():
        nodos_g = [n for n, attrs in grafo.nodes(data=True) if attrs.get('grupo') == grupo]
        if not nodos_g:
            continue
        sizes = [1550 if n == nodo_foco else (1150 if n in vecinos_foco else 820) for n in nodos_g]
        nx.draw_networkx_nodes(
            grafo, pos, nodelist=nodos_g, ax=ax,
            node_color=color, node_size=sizes, alpha=0.95,
            edgecolors='#111827', linewidths=1.4,
        )

    etiquetas = {n: attrs.get('label', n) for n, attrs in grafo.nodes(data=True)}
    nx.draw_networkx_labels(
        grafo, pos, labels=etiquetas, ax=ax,
        font_size=8, font_color='white', font_weight='bold',
    )

    for grupo, color in colores_grupo.items():
        ax.scatter([], [], c=color, s=110, label=grupo, edgecolors='#111827', linewidths=1.0)
    ax.legend(loc='upper left', frameon=True, facecolor='#F8FAFC', fontsize=8.5)
    fig.tight_layout()
    return fig


# Encabezado y métricas
st.title('📚 NexaKnowledge')
st.caption('Sistema inteligente de gestión del conocimiento de NexaSoft Solutions · Prototipo integrado')
a, b, c, d = st.columns(4)
a.metric('Documentos en catálogo', stats['documentos'])
b.metric('Tipos documentales', len(stats['tipos']))
c.metric('Áreas de conocimiento', len(stats['areas']))
d.metric('Conceptos identificados', stats['conceptos_distintos'])

buscar_tab, chat_tab, rec_tab, clasificar_tab, grafo_tab, catalogo_tab = st.tabs([
    '🔎 Búsqueda',
    '💬 Chatbot',
    '✨ Recomendaciones',
    '🤖 Clasificación',
    '🕸️ Grafo interactivo',
    '🗂️ Catálogo y ciclo',
])

with buscar_tab:
    st.subheader('Buscar documentos por contenido')
    consulta = st.text_input(
        'Escribe una pregunta o palabra clave',
        placeholder='Ejemplo: ¿Cómo restaurar archivos después de una falla de servidor?',
    )
    x, y, z = st.columns([1, 1, 1])
    with x:
        tipo = st.selectbox('Tipo documental', ['Todos', *sorted(stats['tipos'])])
    with y:
        limite = st.slider('Máximo de resultados', 1, 10, 5)
    with z:
        expansion = st.checkbox(
            'Ampliar con ontología', value=True,
            help='Añade sinónimos y equivalencias registradas antes de vectorizar con TF-IDF.',
        )

    if consulta.strip():
        registrar_consulta(consulta)
        encontrados = sistema.buscar(
            consulta, limite=limite,
            tipo=None if tipo == 'Todos' else tipo,
            expansion=expansion,
        )
        st.write(f'**{len(encontrados)} documentos encontrados** · Ordenados por similitud del coseno')
        if not encontrados:
            st.info('No se encontraron coincidencias para esa consulta y filtros.')
        for pos, doc in enumerate(encontrados, 1):
            with st.container(border=True):
                st.markdown(f'**{pos}. {doc["titulo"]}**')
                st.caption(f'{doc["id"]} · {doc["tipo"]} · {doc["area"]} · Versión {doc["version"]}')
                st.progress(min(doc['similitud'], 1.0), text=f'Similitud: {doc["similitud"]:.5f}')
                st.write('Conceptos: ' + ', '.join(doc['conceptos']))
                c1, c2 = st.columns(2)
                if c1.button('Ver recomendados similares', key=f'rec_b_{doc["id"]}_{pos}'):
                    seleccionar_documento_foco(doc['id'])
                    st.info(f'Documento base actualizado a **{doc["id"]}**. Abre la pestaña **✨ Recomendaciones** para verlo.')
                if c2.button('Centrar en el grafo', key=f'grf_b_{doc["id"]}_{pos}'):
                    seleccionar_documento_foco(doc['id'])
                    st.info(f'Grafo centrado en **{doc["id"]}**. Abre la pestaña **🕸️ Grafo interactivo** para verlo.')
                with st.expander('Ver contenido'):
                    st.write(doc['contenido'])
                    st.caption('Origen: ' + doc.get('origen', 'No especificado'))
    else:
        st.info('Introduce una consulta para convertirla en vector TF-IDF y comparar con el catálogo.')

with chat_tab:
    st.subheader('Asistente de consultas en lenguaje natural')
    st.caption('Recupera información del repositorio documental y redacta respuestas basadas en las fuentes encontradas.')
    pregunta_chat = st.text_input(
        'Haz una pregunta sobre políticas, procesos, respaldo, APIs, incidentes o seguridad',
        placeholder='Ejemplo: ¿Qué pasos sigue un procedimiento de respaldo y recuperación?',
        key='input_chat',
    )
    col_t, col_k, col_e = st.columns([1, 1, 1])
    with col_t:
        tipo_chat = st.selectbox('Filtrar fuentes por tipo', ['Todos', *sorted(stats['tipos'])], key='tipo_chat')
    with col_k:
        fuentes_k = st.slider('Documentos fuente a consultar', 1, 5, 3, key='fuentes_k')
    with col_e:
        exp_chat = st.checkbox('Usar expansión de ontología', value=True, key='exp_chat')

    if pregunta_chat.strip():
        registrar_consulta(pregunta_chat)
        salida_chat = sistema.responder_chatbot(
            pregunta_chat,
            limite_fuentes=fuentes_k,
            tipo=None if tipo_chat == 'Todos' else tipo_chat,
            expansion=exp_chat,
        )
        st.markdown('### Respuesta generada desde el repositorio')
        st.markdown(salida_chat['respuesta'])
        st.caption(f'Consulta procesada con expansión: "{salida_chat["consulta_expandida"]}"')

        if salida_chat['fuentes']:
            st.markdown('### Documentos fuente recuperados')
            for f in salida_chat['fuentes']:
                with st.expander(f"{f['id']} · {f['titulo']} (similitud: {f['similitud']:.5f})"):
                    st.write(f"**Área:** {f['area']} | **Tipo:** {f['tipo']} | **Conceptos:** {', '.join(f['conceptos'])}")
                    st.write(f['contenido'])
                    if st.button('Recomendar relacionados a esta fuente', key=f'rec_c_{f["id"]}'):
                        seleccionar_documento_foco(f['id'])
                        st.info(f'Base de recomendación actualizada a **{f["id"]}**. Revisa **✨ Recomendaciones**.')

with rec_tab:
    st.subheader('Recomendación de documentos relacionados')
    st.caption('Sugerencias basadas en similitud entre documentos y en tu historial o contexto de consultas.')

    st.markdown('#### 1. Por historial y contexto de búsqueda')
    if st.session_state.historial_consultas:
        st.write('**Consultas recientes consideradas:** ' + ' | '.join(
            f'`{q}`' for q in st.session_state.historial_consultas[-5:]
        ))
        recs_ctx = sistema.recomendar_por_contexto(st.session_state.historial_consultas, limite=4)
        if recs_ctx:
            for r in recs_ctx:
                with st.container(border=True):
                    st.markdown(f"**{r['id']} · {r['titulo']}** — Similitud: `{r['similitud']:.5f}`")
                    st.caption(f"Área: {r['area']} · Tipo: {r['tipo']} · Motivo: {r['motivo']}")
        else:
            st.info('Aún no hay suficientes coincidencias contextuales para recomendar.')
    else:
        st.info('Realiza alguna búsqueda o pregunta en el chatbot para activar recomendaciones por historial.')

    st.markdown('#### 2. Por similitud con un documento base')
    opciones_docs = {f"{d['id']} — {d['titulo']} ({d['tipo']})": d['id']
                     for d in sistema.documentos if not d.get('confidencial', False)}
    if 'rec_doc_sel' not in st.session_state or st.session_state.rec_doc_sel not in opciones_docs:
        default_rec = next(
            (k for k, v in opciones_docs.items() if v == st.session_state.doc_foco_id),
            list(opciones_docs.keys())[0],
        )
        st.session_state.rec_doc_sel = default_rec
    etiqueta_sel = st.selectbox('Selecciona un documento base', list(opciones_docs.keys()), key='rec_doc_sel')
    doc_base_id = opciones_docs[etiqueta_sel]
    st.session_state.doc_foco_id = doc_base_id

    recs_doc = sistema.recomendar_por_documento(doc_base_id, limite=4)
    for r in recs_doc:
        with st.container(border=True):
            st.markdown(f"**{r['id']} · {r['titulo']}** — Similitud: `{r['similitud']:.5f}`")
            st.caption(f"Área: {r['area']} · Tipo: {r['tipo']} · Motivo: {r['motivo']}")
            with st.expander('Ver contenido del documento recomendado'):
                st.write(r['contenido'])

with clasificar_tab:
    st.subheader('Identificar automáticamente el tipo de un documento nuevo')
    titulo = st.text_input('Título propuesto', value='', placeholder='Ejemplo: Gestión de accesos')
    contenido = st.text_area(
        'Contenido o extracto del documento', height=180,
        placeholder='Pega el texto del nuevo documento para predecir su categoría documental.',
    )
    area = st.selectbox('Área que lo genera', sorted(stats['areas']))
    marcar_confidencial = st.checkbox(
        'Marcar como documento confidencial (restringido)',
        help='Si lo marcas, el documento queda fuera de la búsqueda, el chatbot, '
             'las recomendaciones y el grafo en cuanto se agregue.',
    )

    if contenido.strip():
        pred = sistema.clasificar(contenido)
        st.success(
            f'Categoría propuesta: **{pred["tipo_predicho"]}** · '
            f'Probabilidad estimada: **{pred["confianza"]:.1%}**'
        )
        st.dataframe(
            [{'Tipo': a['tipo'], 'Probabilidad estimada': a['probabilidad']} for a in pred['alternativas']],
            hide_index=True, use_container_width=True,
        )
        st.warning(
            'La clasificación requiere revisión humana. Las probabilidades no están calibradas '
            'y el modelo se entrenó inicialmente con documentos sintéticos.'
        )
        if st.button('Agregar al catálogo de esta sesión', type='primary', disabled=not titulo.strip()):
            conceptos = [
                c for c in sistema.ontologia.get('conceptos', [])
                if normalizar(c) in normalizar(contenido)
            ]
            doc = sistema.incorporar(titulo, contenido, area, conceptos[:12],
                                     confidencial=marcar_confidencial)
            if doc.get('confidencial'):
                st.warning(
                    f'Se agregó {doc["id"]} como {doc["tipo"]} con estado **Restringido**. '
                    'Queda excluido de la búsqueda, el chatbot, las recomendaciones y el grafo. '
                    'Compruébalo buscando su contenido en la pestaña 🔎 Búsqueda.'
                )
            else:
                seleccionar_documento_foco(doc['id'])
                st.success(
                    f'Se agregó {doc["id"]} como {doc["tipo"]}: disponible en búsqueda, '
                    'recomendaciones y grafo durante esta sesión.'
                )
    else:
        st.info('Introduce contenido para ver la predicción del clasificador supervisado.')

with grafo_tab:
    st.subheader('Exploración interactiva del grafo de conocimiento')
    st.caption('Representa documentos, categorías (áreas y tipos documentales), conceptos y sus relaciones.')

    f1, f2, f3 = st.columns(3)
    with f1:
        area_g = st.selectbox('Filtrar por área', ['Todas', *sorted(stats['areas'])], key='g_area')
    with f2:
        tipo_g = st.selectbox('Filtrar por tipo', ['Todos', *sorted(stats['tipos'])], key='g_tipo')
    with f3:
        conceptos_todos = sorted({c for d in sistema.documentos for c in d.get('conceptos', [])})
        conc_g = st.selectbox('Filtrar por concepto', ['Todos', *conceptos_todos], key='g_conc')

    mapa_docs = {f"{d['id']} — {d['titulo']}": d['id']
                 for d in sistema.documentos if not d.get('confidencial', False)}
    if 'g_foco' not in st.session_state or st.session_state.g_foco not in mapa_docs:
        default_g = next(
            (k for k, v in mapa_docs.items() if v == st.session_state.doc_foco_id),
            list(mapa_docs.keys())[0],
        )
        st.session_state.g_foco = default_g
    foco_label = st.selectbox('Resaltar documento y sus conexiones directas', list(mapa_docs.keys()), key='g_foco')
    foco_id_actual = mapa_docs[foco_label]
    st.session_state.doc_foco_id = foco_id_actual

    subgrafo, tabla_rel = construir_subgrafo(area_g, tipo_g, conc_g, foco_id_actual)
    fig_grafo = dibujar_grafo(subgrafo, foco_id_actual)
    st.pyplot(fig_grafo, use_container_width=True)
    plt.close(fig_grafo)

    st.markdown('#### Relaciones visibles en el subgrafo actual')
    if tabla_rel:
        st.dataframe(tabla_rel, hide_index=True, use_container_width=True, height=240)
    else:
        st.info('No hay relaciones para mostrar con los filtros actuales.')

with catalogo_tab:
    st.subheader('Colección documental')
    filtro = st.selectbox('Filtrar catálogo', ['Todos', *sorted(stats['tipos'])], key='cat_filtro')
    docs = [d for d in sistema.documentos if filtro == 'Todos' or d['tipo'] == filtro]
    st.dataframe(
        [{'ID': d['id'], 'Título': d['titulo'], 'Tipo': d['tipo'],
          'Área': d['area'], 'Estado': d['estado']} for d in docs],
        hide_index=True, use_container_width=True, height=340,
    )
    n_restringidos = sum(1 for d in sistema.documentos if d.get('confidencial', False))
    st.caption(
        f'Documentos ficticios creados para validar la arquitectura. '
        f'{n_restringidos} figuran con estado **Restringido**: el inventario los reconoce, '
        'pero quedan fuera de la búsqueda, el chatbot, las recomendaciones y el grafo.'
    )

    st.markdown('### Diagramas conceptuales del proyecto')
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if (ROOT / 'recursos' / 'ciclo_conocimiento.png').exists():
            st.image(str(ROOT / 'recursos' / 'ciclo_conocimiento.png'), caption='Ciclo de vida del conocimiento', use_container_width=True)
    with d_col2:
        if (ROOT / 'recursos' / 'ontologia.png').exists():
            st.image(str(ROOT / 'recursos' / 'ontologia.png'), caption='Ontología organizacional', use_container_width=True)