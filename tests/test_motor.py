import pytest
from motor import SistemaConocimiento, normalizar

@pytest.fixture(scope='module')
def sistema():
    return SistemaConocimiento()

def test_total_y_tipos(sistema):
    stats = sistema.estadisticas()
    assert stats['documentos'] == 67
    assert len(stats['tipos']) == 6
    # 60 documentos base (10 por tipo) + 7 confidenciales repartidos entre los tipos.
    assert sum(stats['tipos'].values()) == 67
    assert all(v >= 10 for v in stats['tipos'].values())
    assert sum(1 for d in sistema.documentos if d.get('confidencial')) == 7

def test_consulta_ordenada_con_conceptos(sistema):
    resultados = sistema.buscar('copia de seguridad y recuperación de archivos', limite=5)
    assert len(resultados) == 5
    assert 'Respaldo y recuperación' in resultados[0]['titulo']
    assert resultados[0]['similitud'] >= resultados[1]['similitud']

def test_filtro_tipo(sistema):
    resultados = sistema.buscar('autenticación multifactor y credenciales', tipo='Política')
    assert resultados
    assert all(d['tipo'] == 'Política' for d in resultados)

def test_query_vacia_y_fuera_de_vocabulario(sistema):
    assert sistema.buscar('') == []
    assert sistema.buscar('zzzxxxqqq') == []

def test_expansion_ontologia(sistema):
    ampliada = sistema.expandir_consulta('necesito hacer backup')
    assert 'respaldo' in ampliada

def test_clasificacion(sistema):
    tipo = sistema.clasificar('Esta política define requisitos obligatorios, cumplimiento y responsables.')
    assert tipo['tipo_predicho'] in sistema.estadisticas()['tipos']
    assert 0 <= tipo['confianza'] <= 1

def test_agregar_solo_a_copia(sistema):
    copia = SistemaConocimiento(documentos=sistema.documentos, ontologia=sistema.ontologia)
    nuevo = copia.incorporar('Nueva política de auditoría',
                             'Esta política define controles obligatorios, auditoría, requisitos y excepciones autorizadas.',
                             'Ciberseguridad', ['seguridad'])
    assert nuevo['id'].startswith('USR-')
    assert len(copia.documentos) == len(sistema.documentos) + 1
    assert len(sistema.documentos) == 67

def test_validacion_cruzada(sistema):
    resultado = sistema.evaluar_clasificador()
    assert len(resultado['valores']) == 5
    assert 0.0 <= resultado['accuracy_media'] <= 1.0

def test_normalizacion():
    assert normalizar('CÓDIGO, de Acceso!') == 'codigo de acceso'


# --- Control de acceso a documentos confidenciales ---

CONSULTA_SENSIBLE = 'llaves maestras tokens de acceso y certificados raíz'


def test_busqueda_oculta_confidenciales_por_defecto(sistema):
    resultados = sistema.buscar(CONSULTA_SENSIBLE, limite=10)
    assert resultados, 'la consulta debe devolver documentos públicos'
    assert all(not d.get('confidencial') for d in resultados)


def test_busqueda_expone_confidenciales_con_autorizacion(sistema):
    resultados = sistema.buscar(CONSULTA_SENSIBLE, limite=10, permitir_confidenciales=True)
    assert any(d.get('confidencial') for d in resultados)


def test_chatbot_no_cita_fuentes_confidenciales(sistema):
    salida = sistema.responder_chatbot(CONSULTA_SENSIBLE, limite_fuentes=5)
    assert all(not f.get('confidencial') for f in salida['fuentes'])
    for doc in sistema.documentos:
        if doc.get('confidencial'):
            assert doc['titulo'] not in salida['respuesta']


def test_chatbot_avisa_cuando_todo_lo_relevante_esta_restringido(sistema):
    salida = sistema.responder_chatbot('bóveda de descifrado con llaves privadas JWT',
                                       limite_fuentes=2)
    if not salida['fuentes'] and salida['bloqueados']:
        assert 'nivel de acceso' in salida['respuesta']


def test_recomendaciones_no_sugieren_confidenciales(sistema):
    recs = sistema.recomendar_por_documento('NX-0301', limite=10)
    assert all(not r.get('confidencial') for r in recs)
    ctx = sistema.recomendar_por_contexto([CONSULTA_SENSIBLE], limite=10)
    assert all(not r.get('confidencial') for r in ctx)


def test_documento_base_confidencial_se_rechaza(sistema):
    with pytest.raises(PermissionError):
        sistema.recomendar_por_documento('NX-0701')
    permitido = sistema.recomendar_por_documento('NX-0701', permitir_confidenciales=True)
    assert permitido


def test_incorporar_marcado_como_confidencial_queda_restringido(sistema):
    copia = SistemaConocimiento(documentos=sistema.documentos, ontologia=sistema.ontologia)
    nuevo = copia.incorporar(
        'Secretos de laboratorio',
        'Este procedimiento describe el resguardo de llaves privadas y tokens internos de laboratorio.',
        'Desarrollo', ['credenciales'], confidencial=True)
    assert nuevo['confidencial'] is True
    assert nuevo['estado'] == 'Restringido'
    encontrados = copia.buscar('resguardo de llaves privadas y tokens internos', limite=10)
    assert all(d['id'] != nuevo['id'] for d in encontrados)
    con_permiso = copia.buscar('resguardo de llaves privadas y tokens internos',
                               limite=10, permitir_confidenciales=True)
    assert any(d['id'] == nuevo['id'] for d in con_permiso)
