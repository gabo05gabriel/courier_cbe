from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from .forms import UsuarioForm

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
            return redirect('lista_usuarios')  # Redirigir a la lista de usuarios
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
            return redirect('lista_usuarios')  # Redirigir a la lista de usuarios
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

# Vista para eliminar un usuario
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)  # Obtener el usuario por su ID
    if request.method == 'POST':
        usuario.delete()
        return redirect('lista_usuarios')  # Redirigir a la lista de usuarios
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
