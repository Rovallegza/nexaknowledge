"""Motor local de conocimiento: clasificación supervisada + recuperación TF-IDF.

Este prototipo NO utiliza embeddings semánticos neuronales: TF-IDF capta coincidencias
léxicas y un vocabulario de equivalencias controladas aporta expansión conceptual.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parent
RUTA_DOCS = BASE / 'datos' / 'documentos.json'
RUTA_ONTOLOGIA = BASE / 'datos' / 'ontologia.json'


def normalizar(texto: str) -> str:
    """Minúsculas, acentos y espacios uniformes; no altera el original almacenado."""
    texto = unicodedata.normalize('NFKD', str(texto).lower())
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[^\w\s]', ' ', texto, flags=re.UNICODE).split())


def cargar_json(ruta: str | Path) -> Any:
    with Path(ruta).open(encoding='utf-8') as entrada:
        return json.load(entrada)


def vectorizador() -> TfidfVectorizer:
    return TfidfVectorizer(strip_accents='unicode', lowercase=True, ngram_range=(1, 2),
                           sublinear_tf=True, max_df=0.98)


class SistemaConocimiento:
    """Instancia local con corpus y ontología explícita."""
    def __init__(self, documentos: list[dict] | None = None, ontologia: dict | None = None):
        self.documentos = list(documentos if documentos is not None else cargar_json(RUTA_DOCS))
        self.ontologia = dict(ontologia if ontologia is not None else cargar_json(RUTA_ONTOLOGIA))
        if not self.documentos:
            raise ValueError('Se requiere al menos un documento.')
        self._verificar_documentos()
        self.entrenar()

    def _verificar_documentos(self):
        ids = []
        for d in self.documentos:
            obligatorios = ('id', 'titulo', 'tipo', 'area', 'contenido', 'conceptos')
            if not all(x in d for x in obligatorios):
                raise ValueError(f'Documento con metadatos incompletos: {d}')
            ids.append(d['id'])
        if len(set(ids)) != len(ids):
            raise ValueError('IDs de documentos repetidos.')

    def texto_indice(self, doc: dict) -> str:
        return ' '.join([doc['titulo'], doc['contenido'], doc['area'],
                         ' '.join(doc['conceptos'])])

    def entrenar(self):
        # La búsqueda siempre usa los documentos almacenados e indexados.
        self.indizador = vectorizador()
        self.matriz = self.indizador.fit_transform([self.texto_indice(d) for d in self.documentos])
        # La clasificación se entrena con descripciones, no con el metadato 'tipo'.
        clases = [doc['tipo'] for doc in self.documentos]
        if len(set(clases)) < 2:
            self.clasificador = None
        else:
            self.clasificador = Pipeline([
                ('tfidf', vectorizador()),
                ('modelo', LogisticRegression(max_iter=1600, class_weight='balanced'))
            ])
            self.clasificador.fit([d['contenido'] for d in self.documentos], clases)

    def expandir_consulta(self, consulta: str) -> str:
        """Expansión controlada de equivalencias de la ontología (no es embedding)."""
        consulta_norm = f' {normalizar(consulta)} '
        nuevos = []
        for concepto, alias in self.ontologia.get('sinonimos_de_consulta', {}).items():
            variantes = [concepto, *alias]
            coincide = any(f' {normalizar(v)} ' in consulta_norm for v in variantes)
            if coincide:
                nuevos.extend([concepto, *alias])
        # No modifica la consulta literal; adjunta únicamente términos conocidos.
        return consulta + (' ' + ' '.join(nuevos) if nuevos else '')

    def _es_accesible(self, doc: dict, permitir_confidenciales: bool = False) -> bool:
        """Control de acceso: un documento restringido solo se expone con autorización."""
        if doc.get('confidencial', False) and not permitir_confidenciales:
            return False
        return True

    def buscar(self, consulta: str, limite: int = 5, tipo: str | None = None,
               expansion: bool = True, permitir_confidenciales: bool = False) -> list[dict]:
        if not consulta or not consulta.strip():
            return []
        if limite < 1:
            raise ValueError('limite debe ser positivo.')
        q = self.expandir_consulta(consulta) if expansion else consulta
        consulta_vector = self.indizador.transform([q])
        puntajes = cosine_similarity(consulta_vector, self.matriz).ravel()
        ordenados = sorted(enumerate(puntajes), key=lambda item: (-float(item[1]), item[0]))
        resultados = []
        for i, score in ordenados:
            doc = self.documentos[i]
            if not self._es_accesible(doc, permitir_confidenciales):
                continue
            if tipo is not None and doc['tipo'] != tipo:
                continue
            if score <= 1e-12:  # jamás mostrar elementos sin coincidencia como «relevantes»
                continue
            resultados.append({**doc, 'similitud': round(float(score), 5)})
            if len(resultados) == limite:
                break
        return resultados

    def clasificar(self, texto: str) -> dict:
        if not texto or not texto.strip():
            raise ValueError('Introduzca el contenido del documento.')
        if self.clasificador is None:
            raise ValueError('Se necesitan al menos dos tipos de documentos para clasificar.')
        probabilidades = self.clasificador.predict_proba([texto])[0]
        clases = self.clasificador.named_steps['modelo'].classes_
        ranking = sorted(zip(clases, probabilidades), key=lambda x: -x[1])
        return {
            'tipo_predicho': ranking[0][0],
            'confianza': round(float(ranking[0][1]), 5),
            'alternativas': [{'tipo': t, 'probabilidad': round(float(p), 5)} for t, p in ranking]
        }

    def incorporar(self, titulo: str, contenido: str, area: str,
                   conceptos: list[str] | None = None,
                   confidencial: bool = False) -> dict:
        if not titulo.strip() or not contenido.strip() or not area.strip():
            raise ValueError('Título, contenido y área son obligatorios.')
        resultado = self.clasificar(contenido)
        docs_adicionales = sum(d['id'].startswith('USR-') for d in self.documentos)
        doc = {
            'id': f'USR-{docs_adicionales + 1:04d}',
            'titulo': titulo.strip(),
            'tipo': resultado['tipo_predicho'],
            'area': area.strip(),
            'conceptos': conceptos or [],
            'contenido': contenido.strip(),
            'version': '1.0',
            'estado': 'Restringido' if confidencial else 'Pendiente de revisión',
            'fecha_actualizacion': 'No asignada',
            'origen': 'Añadido durante la ejecución; no aprobado por experto',
            'confidencial': bool(confidencial),
        }
        self.documentos.append(doc)
        self.entrenar()
        return doc

    def evaluar_clasificador(self, k: int = 5) -> dict:
        y = [doc['tipo'] for doc in self.documentos]
        cuenta = Counter(y)
        if len(cuenta) < 2 or min(cuenta.values()) < k:
            raise ValueError('No hay suficientes documentos por clase para la validación.')
        pipeline = Pipeline([('tfidf', vectorizador()),
                             ('modelo', LogisticRegression(max_iter=1600, class_weight='balanced'))])
        x = [d['contenido'] for d in self.documentos]
        cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
        resultados = cross_val_score(pipeline, x, y, cv=cv, scoring='accuracy')
        return {'metodo': f'{k} pliegues estratificados',
                'accuracy_media': round(float(np.mean(resultados)), 4),
                'desviacion': round(float(np.std(resultados)), 4),
                'valores': [round(float(p), 4) for p in resultados],
                'n_documentos': len(y)}

    def estadisticas(self) -> dict:
        return {'documentos': len(self.documentos),
                'tipos': dict(Counter(d['tipo'] for d in self.documentos)),
                'areas': dict(Counter(d['area'] for d in self.documentos)),
                'conceptos_distintos': len(set(c for d in self.documentos for c in d['conceptos']))}

    # --- Sistema de recomendaciones y chatbot ---


    def _motivo_relacion(self, doc_origen: dict, doc_cand: dict, puntaje: float) -> str:
        conceptos_comunes = sorted(set(doc_origen.get('conceptos', [])) & set(doc_cand.get('conceptos', [])))
        razones = [f'similitud coseno {puntaje:.3f}']
        if conceptos_comunes:
            razones.append('conceptos compartidos: ' + ', '.join(conceptos_comunes))
        if doc_origen.get('area') == doc_cand.get('area'):
            razones.append(f"misma área ({doc_cand.get('area')})")
        if doc_origen.get('tipo') == doc_cand.get('tipo'):
            razones.append(f"mismo tipo ({doc_cand.get('tipo')})")
        return ' · '.join(razones)

    def recomendar_por_documento(self, doc_id: str, limite: int = 4,
                                 permitir_confidenciales: bool = False) -> list[dict]:
        """Recomienda documentos similares a un documento dado."""
        if limite < 1:
            raise ValueError('limite debe ser positivo.')
        idx_base = next((i for i, d in enumerate(self.documentos) if d['id'] == doc_id), None)
        if idx_base is None:
            raise ValueError(f'Documento no encontrado: {doc_id}')

        doc_base = self.documentos[idx_base]
        # El documento base también pasa por el control de acceso: de lo contrario
        # bastaría con pedir recomendaciones de un restringido para leer su título.
        if not self._es_accesible(doc_base, permitir_confidenciales):
            raise PermissionError(
                f'El documento {doc_id} está restringido y requiere un nivel de acceso autorizado.'
            )

        similitudes = cosine_similarity(self.matriz[idx_base], self.matriz).ravel()
        ordenados = sorted(enumerate(similitudes), key=lambda item: (-float(item[1]), item[0]))

        recomendaciones = []
        for i, score in ordenados:
            if i == idx_base or float(score) <= 1e-12:
                continue
            cand = self.documentos[i]
            if not self._es_accesible(cand, permitir_confidenciales):
                continue
            recomendaciones.append({
                **cand,
                'similitud': round(float(score), 5),
                'base_id': doc_base['id'],
                'base_titulo': doc_base['titulo'],
                'motivo': self._motivo_relacion(doc_base, cand, float(score)),
            })
            if len(recomendaciones) == limite:
                break
        return recomendaciones

    def recomendar_por_contexto(self, historial_consultas: list[str], limite: int = 4,
                               excluir_ids: set[str] | None = None,
                               permitir_confidenciales: bool = False) -> list[dict]:
        """Recomienda documentos a partir del historial o contexto de búsqueda."""
        if limite < 1:
            raise ValueError('limite debe ser positivo.')
        consultas_limpias = [c.strip() for c in historial_consultas if c and c.strip()]
        if not consultas_limpias:
            return []

        excluidos = set(excluir_ids or set())
        contexto_texto = ' '.join(self.expandir_consulta(c) for c in consultas_limpias[-5:])
        vec_ctx = self.indizador.transform([contexto_texto])
        puntajes = cosine_similarity(vec_ctx, self.matriz).ravel()
        ordenados = sorted(enumerate(puntajes), key=lambda item: (-float(item[1]), item[0]))

        terminos_ctx = set(normalizar(contexto_texto).split())
        recomendaciones = []
        for i, score in ordenados:
            if float(score) <= 1e-12:
                continue
            doc = self.documentos[i]
            if not self._es_accesible(doc, permitir_confidenciales):
                continue
            if doc['id'] in excluidos:
                continue
            coincidencias = sorted(c for c in doc.get('conceptos', []) if normalizar(c) in terminos_ctx)
            motivo = f'contexto de {len(consultas_limpias[-5:])} consulta(s) · similitud {float(score):.3f}'
            if coincidencias:
                motivo += ' · conceptos afines: ' + ', '.join(coincidencias)
            recomendaciones.append({
                **doc,
                'similitud': round(float(score), 5),
                'contexto_usado': consultas_limpias[-5:],
                'motivo': motivo,
            })
            if len(recomendaciones) == limite:
                break
        return recomendaciones

    def responder_chatbot(self, pregunta: str, limite_fuentes: int = 3,
                          tipo: str | None = None, expansion: bool = True,
                          permitir_confidenciales: bool = False) -> dict:
        """Recupera documentos relevantes y redacta una respuesta basada en ellos."""
        if not pregunta or not pregunta.strip():
            raise ValueError('Escribe una pregunta para consultar al asistente.')

        fuentes = self.buscar(pregunta, limite=limite_fuentes, tipo=tipo, expansion=expansion,
                              permitir_confidenciales=permitir_confidenciales)
        q_expandida = self.expandir_consulta(pregunta) if expansion else pregunta

        if not fuentes:
            # Distingue «no hay nada» de «lo hay pero está restringido», para que el
            # control de acceso sea visible en lugar de parecer una búsqueda vacía.
            bloqueados = 0
            if not permitir_confidenciales:
                sin_filtro = self.buscar(pregunta, limite=limite_fuentes, tipo=tipo,
                                         expansion=expansion, permitir_confidenciales=True)
                bloqueados = sum(1 for d in sin_filtro if d.get('confidencial', False))
            if bloqueados:
                mensaje = (
                    'No se encontraron documentos autorizados para tu nivel de acceso. '
                    'Los registros confidenciales están restringidos '
                    f'({bloqueados} documento(s) coincidente(s) bloqueado(s)).'
                )
            else:
                mensaje = (
                    'No encontré documentos suficientemente relacionados con tu consulta en el catálogo actual. '
                    'Intenta reformularla con términos de NexaSoft Solutions como credenciales, respaldo, API REST, '
                    'despliegue CI/CD, incidentes, indicadores, privacidad, git, monitoreo o proyectos ágiles.'
                )
            return {
                'pregunta': pregunta.strip(),
                'consulta_expandida': q_expandida,
                'respuesta': mensaje,
                'fuentes': [],
                'bloqueados': bloqueados,
            }

        palabras_q = set(normalizar(q_expandida).split())
        extractos = []
        for f in fuentes[:2]:
            oraciones = [s.strip() for s in re.split(r'(?<=[.!?])\s+', f['contenido']) if s.strip()]
            mejor_oracion = max(
                oraciones,
                key=lambda s: sum(1 for tok in normalizar(s).split() if tok in palabras_q),
                default=f['contenido'][:220],
            )
            extractos.append(f"- **{f['titulo']}** ({f['id']}, {f['area']} · similitud {f['similitud']:.3f}): {mejor_oracion}")

        respuesta = (
            f"Con base en los documentos recuperados del repositorio para *«{pregunta.strip()}»*, "
            f"estos son los hallazgos principales:\n\n" + "\n".join(extractos)
        )
        return {
            'pregunta': pregunta.strip(),
            'consulta_expandida': q_expandida,
            'respuesta': respuesta,
            'fuentes': fuentes,
            'bloqueados': 0,
        }
    
    
def main():
    parser = argparse.ArgumentParser(description='Sistema de conocimiento NexaSoft Solutions')
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--consulta', help='Búsqueda TF-IDF y similitud coseno')
    grupo.add_argument('--clasificar', help='Texto para clasificar automáticamente')
    grupo.add_argument('--evaluar', action='store_true', help='Validación cruzada del clasificador')
    grupo.add_argument('--estadisticas', action='store_true', help='Resumen del corpus')
    parser.add_argument('--top', type=int, default=5)
    parser.add_argument('--tipo', help='Restringir tipo de documento')
    parser.add_argument('--sin-expansion', action='store_true', help='Omitir sinónimos de la ontología')
    args = parser.parse_args()
    sistema = SistemaConocimiento()
    if args.consulta is not None:
        resultado = sistema.buscar(args.consulta, limite=args.top, tipo=args.tipo,
                                   expansion=not args.sin_expansion)
    elif args.clasificar is not None:
        resultado = sistema.clasificar(args.clasificar)
    elif args.evaluar:
        resultado = sistema.evaluar_clasificador()
    else:
        resultado = sistema.estadisticas()
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()


