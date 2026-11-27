import pytest
from motor import SistemaConocimiento, normalizar

@pytest.fixture(scope='module')
def sistema():
    return SistemaConocimiento()

def test_total_y_tipos(sistema):
    assert sistema.estadisticas()['documentos'] == 60
    assert len(sistema.estadisticas()['tipos']) == 6
    assert all(v == 10 for v in sistema.estadisticas()['tipos'].values())

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
    assert len(copia.documentos) == 61
    assert len(sistema.documentos) == 60

def test_validacion_cruzada(sistema):
    resultado = sistema.evaluar_clasificador()
    assert len(resultado['valores']) == 5
    assert 0.0 <= resultado['accuracy_media'] <= 1.0

def test_normalizacion():
    assert normalizar('CÓDIGO, de Acceso!') == 'codigo de acceso'
