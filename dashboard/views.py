import json
from collections import Counter

import requests
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
# Create your views here.
def dashboard(request):
    # return HttpResponse("¡Bienvenido a la aplicación Django!")
    return render(request, "dashboard/base.html")



@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
def index(request):
    """
    Vista principal que obtiene datos de una API, los procesa y los renderiza en la plantilla del dashboard.
    """
    posts = []
    error_message = None

    try:
        response = requests.get(settings.API_URL, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de error (4xx o 5xx)
        posts = response.json()
    except requests.exceptions.RequestException as e:
        # Maneja errores de conexión, timeouts, etc.
        error_message = f"Error al contactar la API: {e}"
        # Se podría registrar el error en un log aquí

    # 1. --- Calcular Indicadores ---
    total_responses = len(posts)

    if posts:
        # Calcular número de usuarios únicos
        unique_user_ids = set(post["userId"] for post in posts)
        total_unique_users = len(unique_user_ids)

        # Calcular longitud promedio del título
        total_title_length = sum(len(post["title"]) for post in posts)
        avg_title_length = round(total_title_length / total_responses, 2)

        # 2. --- Preparar datos para el Gráfico (Posts por Usuario) ---
        user_post_counts = Counter(post["userId"] for post in posts)
        # Ordenar por userId para un gráfico consistente
        sorted_user_counts = sorted(user_post_counts.items())
        chart_labels = [f"Usuario {item[0]}" for item in sorted_user_counts]
        chart_data = [item[1] for item in sorted_user_counts]
    else:
        # Valores por defecto si no hay datos
        total_unique_users = 0
        avg_title_length = 0
        chart_labels = []
        chart_data = []

    # 3. --- Crear el Contexto para la Plantilla ---
    context = {
        "title": "Dashboard de Datos de la API 📈",
        "posts": posts[:20],  # Limitar a 20 posts para la tabla para no saturar la UI
        "total_responses": total_responses,
        "total_unique_users": total_unique_users,
        "avg_title_length": avg_title_length,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "error_message": error_message,
    }

    return render(request, "dashboard/index.html", context)

