from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout  # Importa el método logout
from .models import Usuario
from .forms import UsuarioForm, LoginForm
from django.contrib import messages
from envios.models import Envio, Entrega
import json

# Vista para listar los usuarios
def lista_usuarios(request):
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios de la base de datos
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

# Vista para crear un nuevo usuario
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')  # Redirigir a la lista de usuarios
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

# Vista para ver los detalles de un usuario
def ver_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtener el usuario por su ID
    return render(request, 'usuarios/ver_usuario.html', {'usuario': usuario})

# Vista para editar un usuario
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtener el usuario por su ID
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios:lista_usuarios')  # Redirigir a la lista de usuarios
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

# Vista para eliminar un usuario
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtener el usuario por su ID
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuarios:lista_usuarios')  # Redirigir a la lista de usuarios
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})

# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('usuarios:login')  # Redirigir al login después de cerrar sesión

# Vista para iniciar sesión
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            contrasena = form.cleaned_data['contrasena']

            try:
                usuario = Usuario.objects.get(email=email)
                if usuario.check_password(contrasena):
                    # Si la contraseña es correcta, almacenar la información en la sesión
                    request.session['usuario_id'] = usuario.id
                    return redirect('usuarios:home')  # Redirigir al home después del login
                else:
                    messages.error(request, "Contraseña incorrecta")
            except Usuario.DoesNotExist:
                messages.error(request, "El usuario con este correo no existe")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

# Vista para la página de inicio
def home(request):
    # Total de usuarios
    usuarios_count = Usuario.objects.count()

    # Envíos pendientes
    envios_pendientes = Envio.objects.filter(estado="Pendiente").count()

    # Mensajeros activos (rol relacionado con nombre = "mensajero")
    mensajeros_activos = Usuario.objects.filter(rol__nombre__iexact="mensajero").count()

    # % de envíos entregados
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

def mensajeros_view(request):
    mensajeros = Usuario.objects.filter(rol__nombre="Mensajero").select_related("perfil_mensajero")

    # Crear lista simple con los datos
    mensajeros_data = []
    for m in mensajeros:
        if m.perfil_mensajero and m.perfil_mensajero.latitud and m.perfil_mensajero.longitud:
            mensajeros_data.append({
                "nombre": m.nombre,
                "lat": float(m.perfil_mensajero.latitud),
                "lng": float(m.perfil_mensajero.longitud),
            })

    return render(request, "usuarios/mensajeros.html", {
        "mensajeros_json": json.dumps(mensajeros_data)  # 🔹 pasamos JSON limpio
    })
