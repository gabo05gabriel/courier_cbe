from django.shortcuts import render, get_object_or_404
from .models import Ruta
from usuarios.models import Usuario, PerfilMensajero
from envios.models import Envio

import json
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


# ============================
# Vista: Lista de sobres/rutas
# ============================
def lista_rutas(request):
    # ✅ Solo traer usuarios que son mensajeros
    mensajeros = Usuario.objects.filter(
        id__in=PerfilMensajero.objects.values("usuario_id")
    )

    mensajero_id = request.POST.get("mensajero_id")
    sobres = []

    # ✅ Filtrar sobres según el mensajero seleccionado
    if mensajero_id:
        sobres_qs = Envio.objects.filter(mensajero_id=mensajero_id)
    else:
        sobres_qs = Envio.objects.none()  # vacío si no hay selección

    # ✅ Convertir sobres válidos a JSON con TODOS los campos
    for envio in sobres_qs:
        sobres.append({
            "id": envio.id,
            "origen_direccion": envio.origen_direccion,
            "destino_direccion": envio.destino_direccion,
            "destinatario_nombre": envio.destinatario_nombre,
            "destinatario_telefono": envio.destinatario_telefono,
            "peso": str(envio.peso) if envio.peso is not None else None,
            "tipo_servicio": envio.tipo_servicio,
            "estado": envio.estado,
            "observaciones": envio.observaciones,
            "creado_en": envio.creado_en.strftime("%Y-%m-%d %H:%M:%S") if envio.creado_en else None,
            "ruta_id": envio.ruta_id,
            "remitente_id": envio.remitente_id,
            "latitud_destino": float(envio.latitud_destino) if envio.latitud_destino else None,
            "latitud_origen": float(envio.latitud_origen) if envio.latitud_origen else None,
            "longitud_destino": float(envio.longitud_destino) if envio.longitud_destino else None,
            "longitud_origen": float(envio.longitud_origen) if envio.longitud_origen else None,
            "monto_pago": str(envio.monto_pago) if envio.monto_pago else None,
            "tipo": envio.tipo,
            "tipo_pago": envio.tipo_pago,
            "mensajero_id": envio.mensajero_id,
            "remitente_nombre": getattr(envio, "remitente_nombre", None),
            "remitente_telefono": getattr(envio, "remitente_telefono", None),

            # Datos para el mapa
            "origen": {
                "lat": float(envio.latitud_origen) if envio.latitud_origen else None,
                "lng": float(envio.longitud_origen) if envio.longitud_origen else None,
            },
            "destino": {
                "lat": float(envio.latitud_destino) if envio.latitud_destino else None,
                "lng": float(envio.longitud_destino) if envio.longitud_destino else None,
            },
        })

    return render(request, "rutas/lista_rutas.html", {
        "mensajeros": mensajeros,
        "sobres_json": json.dumps(sobres, ensure_ascii=False),
    })


# ============================
# Vista: Optimizar y predecir rutas
# ============================
def optimizar_y_predecir_view(request, mensajero_id):
    # ✅ Verificar que el mensajero existe
    mensajero = get_object_or_404(Usuario, id=mensajero_id)

    # ✅ Filtrar rutas solo de este mensajero
    rutas_data = Ruta.objects.filter(mensajero_id=mensajero_id).values(
        'id',
        'latitud_inicio', 'longitud_inicio',
        'latitud_fin', 'longitud_fin',
        'duracion_estimada', 'duracion_real'
    )

    df = pd.DataFrame(rutas_data)

    if df.empty:
        return render(request, "rutas/optimizar_rutas.html", {
            "mensajero": mensajero,
            "rutas": [],
            "accuracy": 0,
            "mensaje": f"⚠ El mensajero {mensajero.nombre} no tiene rutas registradas."
        })

    # ================================
    # 1. Clustering con KMeans
    # ================================
    df = df.dropna(subset=['latitud_inicio', 'longitud_inicio', 'latitud_fin', 'longitud_fin'])
    coordenadas = df[['latitud_inicio', 'longitud_inicio', 'latitud_fin', 'longitud_fin']].astype(float).values

    if len(coordenadas) > 1:  # evitar error si hay solo una ruta
        kmeans = KMeans(n_clusters=min(3, len(coordenadas)), random_state=42)
        kmeans.fit(coordenadas)
        df['zona_asignada'] = kmeans.labels_

        # ✅ Guardar zona asignada en la DB
        for idx, row in df.iterrows():
            ruta = Ruta.objects.get(id=row['id'])
            ruta.zona_asignada = row['zona_asignada']
            ruta.save()

    # ================================
    # 2. Árbol de decisión para predecir retrasos
    # ================================
    df['duracion_estimada'] = df['duracion_estimada'].fillna(0)
    df['duracion_real'] = df['duracion_real'].fillna(0)

    X = df[['duracion_estimada', 'latitud_inicio', 'longitud_inicio', 'latitud_fin', 'longitud_fin']].astype(float)
    y = (df['duracion_real'] > df['duracion_estimada']).astype(int)

    if len(df) < 2 or y.nunique() == 1:
        accuracy = 1.0
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        clf = DecisionTreeClassifier(random_state=42)
        clf.fit(X_train, y_train)
        accuracy = clf.score(X_test, y_test)

        # ✅ Predecir retrasos en todas las rutas
        for idx, row in df.iterrows():
            X_new = [[
                row['duracion_estimada'],
                row['latitud_inicio'],
                row['longitud_inicio'],
                row['latitud_fin'],
                row['longitud_fin']
            ]]
            pred = clf.predict(X_new)
            ruta = Ruta.objects.get(id=row['id'])
            ruta.retraso_estimado = "Retraso estimado" if pred[0] == 1 else "Entrega a tiempo"
            ruta.save()

    # ================================
    # Renderizar resultados
    # ================================
    return render(request, "rutas/optimizar_rutas.html", {
        "mensajero": mensajero,
        "rutas": df.to_dict(orient="records"),
        "accuracy": accuracy,
        "mensaje": f"✅ Optimización realizada para el mensajero {mensajero.nombre}"
    })


# ============================
# Vista: Ver ruta específica
# ============================
def ver_ruta(request, ruta_id):
    ruta = get_object_or_404(Ruta, id=ruta_id)
    return render(request, "rutas/ver_ruta.html", {"ruta": ruta})
