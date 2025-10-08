from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Usuario
from .forms import UsuarioForm, LoginForm
from envios.models import Envio, Entrega
import json


# ------------------------------------------------------------------------------
# 🔹 CRUD de usuarios
# ------------------------------------------------------------------------------

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})


def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})


def ver_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'usuarios/ver_usuario.html', {'usuario': usuario})


def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})


def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})


# ------------------------------------------------------------------------------
# 🔹 Cerrar sesión (para interfaz web)
# ------------------------------------------------------------------------------
def cerrar_sesion(request):
    logout(request)
    return redirect('usuarios:login')


# ------------------------------------------------------------------------------
# 🔹 Login general (web + API JSON)
# ------------------------------------------------------------------------------
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # 👈 Permite login desde Flutter (sin CSRF)
def login_view(request):
    """
    Maneja login tanto desde web (HTML) como desde API (JSON para Flutter)
    """
    if request.method == 'POST':
        # Detectar si la petición es JSON (Flutter) o form-data (web)
        is_json = request.content_type == 'application/json'

        if is_json:
            # ✅ Login desde Flutter (API)
            try:
                data = json.loads(request.body.decode('utf-8'))
                email = data.get('email')
                contrasena = data.get('contrasena')

                if not email or not contrasena:
                    return JsonResponse({'error': 'Faltan credenciales'}, status=400)

                usuario = Usuario.objects.filter(email=email).first()
                if usuario and usuario.check_password(contrasena):
                    return JsonResponse({
                        'id': usuario.id,
                        'nombre': usuario.nombre,
                        'email': usuario.email,
                        'rol': usuario.rol.nombre,
                        'is_active': usuario.is_active,
                        'status': 'success'
                    }, status=200)
                else:
                    return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON inválido'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

        else:
            # ✅ Login desde formulario HTML (web)
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                contrasena = form.cleaned_data['contrasena']
                try:
                    usuario = Usuario.objects.get(email=email)
                    if usuario.check_password(contrasena):
                        request.session['usuario_id'] = usuario.id
                        return redirect('usuarios:home')
                    else:
                        messages.error(request, "Contraseña incorrecta")
                except Usuario.DoesNotExist:
                    messages.error(request, "El usuario con este correo no existe")
            return render(request, 'usuarios/login.html', {'form': form})

    else:
        form = LoginForm()
        return render(request, 'usuarios/login.html', {'form': form})


# ------------------------------------------------------------------------------
# 🔹 Página principal (Dashboard)
# ------------------------------------------------------------------------------
def home(request):
    usuarios_count = Usuario.objects.count()
    envios_pendientes = Envio.objects.filter(estado="Pendiente").count()
    mensajeros_activos = Usuario.objects.filter(rol__nombre__iexact="mensajero").count()
    entregados = Entrega.objects.filter(estado="Entregado").count()
    total_envios = Envio.objects.count()
    porcentaje_entregados = (entregados / total_envios * 100) if total_envios > 0 else 0

    context = {
        "usuarios_count": usuarios_count,
        "envios_pendientes": envios_pendientes,
        "mensajeros_activos": mensajeros_activos,
        "porcentaje_entregados": round(porcentaje_entregados, 2),
    }
    return render(request, "usuarios/home.html", context)


# ------------------------------------------------------------------------------
# 🔹 Vista de mensajeros (mapa / ubicación)
# ------------------------------------------------------------------------------
def mensajeros_view(request):
    mensajeros = Usuario.objects.filter(rol__nombre="Mensajero").select_related("perfil_mensajero")

    mensajeros_data = []
    for m in mensajeros:
        if m.perfil_mensajero and m.perfil_mensajero.latitud and m.perfil_mensajero.longitud:
            mensajeros_data.append({
                "nombre": m.nombre,
                "lat": float(m.perfil_mensajero.latitud),
                "lng": float(m.perfil_mensajero.longitud),
            })

    return render(request, "usuarios/mensajeros.html", {
        "mensajeros_json": json.dumps(mensajeros_data)
    })


# ------------------------------------------------------------------------------
# 🔹 API login separado (si quieres usar otra ruta /usuarios/api/login/)
# ------------------------------------------------------------------------------
@csrf_exempt
def api_login(request):
    """
    Endpoint alternativo solo para Flutter (POST JSON)
    Ruta: /usuarios/api/login/
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            contrasena = data.get('contrasena')

            usuario = Usuario.objects.filter(email=email).first()
            if usuario and usuario.check_password(contrasena):
                return JsonResponse({
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "rol": usuario.rol.nombre,
                    "status": "success"
                }, status=200)
            else:
                return JsonResponse({"error": "Credenciales inválidas"}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)

from django.http import JsonResponse

def home_data(request):
    usuarios_count = Usuario.objects.count()
    envios_pendientes = Envio.objects.filter(estado="Pendiente").count()
    mensajeros_activos = Usuario.objects.filter(rol__nombre__iexact="mensajero").count()
    entregados = Entrega.objects.filter(estado="Entregado").count()
    total_envios = Envio.objects.count()
    porcentaje_entregados = (entregados / total_envios * 100) if total_envios > 0 else 0

    return JsonResponse({
        "usuarios_count": usuarios_count,
        "envios_pendientes": envios_pendientes,
        "mensajeros_activos": mensajeros_activos,
        "porcentaje_entregados": round(porcentaje_entregados, 2)
    })