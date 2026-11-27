"""Evaluación reproducible de Precision@K y Recall@K para NexaKnowledge."""
from __future__ import annotations

from motor import SistemaConocimiento, normalizar

CASOS_CONSULTA = [
    ("¿Cómo restaurar archivos después de una falla de servidor?", {"respaldo", "recuperacion", "servidor"}),
    ("Política de contraseñas y autenticación de usuarios", {"credenciales", "autenticacion", "acceso", "seguridad"}),
    ("Pipeline de despliegue continuo y automatización de releases", {"despliegue", "cicd", "automatizacion"}),
    ("Gestión de incidentes críticos y escalamiento de soporte", {"incidentes", "soporte", "escalamiento"}),
    ("Protección de datos personales y privacidad", {"privacidad", "datos", "cifrado", "cumplimiento"}),
    ("Control de versiones con git y revisión de código", {"git", "codigo", "versiones"}),
    ("Monitoreo de servicios y alertas de disponibilidad", {"monitoreo", "alertas", "disponibilidad"}),
    ("A cuánto es la comida?", set()),  # Caso fuera de dominio para observar falsos positivos
]


def es_relevante_consulta(doc: dict, terminos_esperados: set[str]) -> bool:
    if not terminos_esperados:
        return False
    texto_doc = normalizar(f"{doc['titulo']} {doc['area']} {doc['tipo']} {' '.join(doc['conceptos'])} {doc['contenido']}")
    tokens_doc = set(texto_doc.split())
    return any(normalizar(t) in tokens_doc for t in terminos_esperados)


def evaluar_busqueda(sistema: SistemaConocimiento, k: int = 5, expansion: bool = True) -> dict:
    precisions, recalls = [], []
    detalle = []

    for consulta, esperados in CASOS_CONSULTA:
        relevantes_totales = [d for d in sistema.documentos if es_relevante_consulta(d, esperados)]
        recuperados = sistema.buscar(consulta, limite=k, expansion=expansion)
        aciertos = sum(1 for d in recuperados if es_relevante_consulta(d, esperados))

        p = aciertos / k if k > 0 else 0.0
        r = (aciertos / len(relevantes_totales)) if relevantes_totales else (1.0 if aciertos == 0 else 0.0)
        precisions.append(p)
        recalls.append(r)
        detalle.append({
            "consulta": consulta,
            "aciertos": aciertos,
            "recuperados": len(recuperados),
            "relevantes_totales": len(relevantes_totales),
            "precision@k": round(p, 4),
            "recall@k": round(r, 4),
            "top_similitud": recuperados[0]["similitud"] if recuperados else 0.0,
        })

    return {
        "k": k,
        "expansion": expansion,
        "precision_media": round(sum(precisions) / len(precisions), 4),
        "recall_media": round(sum(recalls) / len(recalls), 4),
        "detalle": detalle,
    }


def evaluar_recomendacion_documento(sistema: SistemaConocimiento, k: int = 4) -> dict:
    precisions, recalls = [], []

    for doc_base in sistema.documentos:
        conceptos_base = set(doc_base.get("conceptos", []))
        relevantes_posibles = [
            d for d in sistema.documentos
            if d["id"] != doc_base["id"] and (
                bool(conceptos_base & set(d.get("conceptos", [])))
                or d["area"] == doc_base["area"]
            )
        ]
        recs = sistema.recomendar_por_documento(doc_base["id"], limite=k)
        aciertos = sum(
            1 for r in recs
            if bool(conceptos_base & set(r.get("conceptos", []))) or r["area"] == doc_base["area"]
        )
        p = aciertos / k
        r = (aciertos / len(relevantes_posibles)) if relevantes_posibles else 1.0
        precisions.append(p)
        recalls.append(r)

    return {
        "k": k,
        "n_documentos": len(sistema.documentos),
        "precision_media": round(sum(precisions) / len(precisions), 4),
        "recall_media": round(sum(recalls) / len(recalls), 4),
    }


if __name__ == "__main__":
    s = SistemaConocimiento()
    con_exp = evaluar_busqueda(s, k=5, expansion=True)
    sin_exp = evaluar_busqueda(s, k=5, expansion=False)
    rec_eval = evaluar_recomendacion_documento(s, k=4)

    print("Búsqueda CON expansión ontológica:", con_exp["precision_media"], con_exp["recall_media"])
    print("Búsqueda SIN expansión ontológica:", sin_exp["precision_media"], sin_exp["recall_media"])
    print("Recomendación por documento (top-4):", rec_eval)
    for fila in con_exp["detalle"]:
        print(" ", fila)