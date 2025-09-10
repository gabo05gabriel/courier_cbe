from django.shortcuts import redirect

class AutenticacionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si el usuario está autenticado
        if 'usuario_id' not in request.session:
            # Si no está autenticado, redirigir al login
            if not request.path.startswith('/usuarios/login/'):
                return redirect('usuarios:login')  # Redirigir solo si no estamos en la página de login
        else:
            # Si está autenticado, redirigir a la página de inicio si ya está en la página de login
            if request.path.startswith('/usuarios/login/'):
                return redirect('usuarios:home')  # Redirigir a home si ya está autenticado

        # Continuar con la respuesta normal si no hay redirección
        response = self.get_response(request)
        return response
