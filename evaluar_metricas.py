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

    # El universo de documentos relevantes excluye los restringidos, porque la
    # búsqueda tampoco puede devolverlos sin autorización.
    accesibles = [d for d in sistema.documentos if not d.get("confidencial", False)]

    for consulta, esperados in CASOS_CONSULTA:
        relevantes_totales = [d for d in accesibles if es_relevante_consulta(d, esperados)]
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

    # Se evalúa el recomendador tal como lo usa un colaborador sin autorización
    # especial: los documentos restringidos no son base ni candidatos válidos.
    accesibles = [d for d in sistema.documentos if not d.get("confidencial", False)]

    for doc_base in accesibles:
        conceptos_base = set(doc_base.get("conceptos", []))
        relevantes_posibles = [
            d for d in accesibles
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
        "n_evaluados": len(accesibles),
        "n_restringidos": len(sistema.documentos) - len(accesibles),
        "precision_media": round(sum(precisions) / len(precisions), 4),
        "recall_media": round(sum(recalls) / len(recalls), 4),
    }


CONSULTAS_SENSIBLES = [
    "llaves maestras y tokens de acceso de producción",
    "certificados raíz y accesos SSH a clústeres",
    "direcciones IP privadas y bóveda de respaldos",
    "vulnerabilidades críticas sin parchar y pruebas de penetración",
    "tabuladores salariales y proyecciones financieras",
    "tickets con exposición de datos personales de clientes",
    "presupuestos estratégicos y adquisiciones pendientes",
]


def evaluar_control_acceso(sistema: SistemaConocimiento, k: int = 5) -> dict:
    """Comprueba que ningún documento restringido se filtre sin autorización."""
    fugas, recuperables = [], 0

    for consulta in CONSULTAS_SENSIBLES:
        sin_permiso = sistema.buscar(consulta, limite=k)
        fugas += [d["id"] for d in sin_permiso if d.get("confidencial", False)]

        respuesta = sistema.responder_chatbot(consulta, limite_fuentes=k)
        fugas += [f["id"] for f in respuesta["fuentes"] if f.get("confidencial", False)]
        for doc in sistema.documentos:
            if doc.get("confidencial", False) and doc["titulo"] in respuesta["respuesta"]:
                fugas.append(doc["id"])

        con_permiso = sistema.buscar(consulta, limite=k, permitir_confidenciales=True)
        if any(d.get("confidencial", False) for d in con_permiso):
            recuperables += 1

    return {
        "consultas_probadas": len(CONSULTAS_SENSIBLES),
        "fugas_detectadas": len(fugas),
        "ids_filtrados": sorted(set(fugas)),
        "recuperables_con_autorizacion": recuperables,
    }


if __name__ == "__main__":
    s = SistemaConocimiento()
    con_exp = evaluar_busqueda(s, k=5, expansion=True)
    sin_exp = evaluar_busqueda(s, k=5, expansion=False)
    rec_eval = evaluar_recomendacion_documento(s, k=4)
    acceso = evaluar_control_acceso(s, k=5)

    print("Búsqueda CON expansión ontológica:", con_exp["precision_media"], con_exp["recall_media"])
    print("Búsqueda SIN expansión ontológica:", sin_exp["precision_media"], sin_exp["recall_media"])
    print("Recomendación por documento (top-4):", rec_eval)
    print("Control de acceso:", acceso)
    for fila in con_exp["detalle"]:
        print(" ", fila)