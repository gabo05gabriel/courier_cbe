import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();

  // Datos del usuario autenticado (solo los datos del usuario, no toda la respuesta)
  Map<String, dynamic>? _usuario;

  Map<String, dynamic>? get usuario => _usuario;
  bool get isAuthenticated => _usuario != null;

  /// 🔐 Inicia sesión y guarda solo los datos del usuario
  Future<bool> login(String email, String password) async {
    final data = await _authService.login(email, password);

    if (data != null && data['status'] == 'success') {
      // ✅ Guarda solo el objeto "usuario" dentro del JSON recibido
      if (data.containsKey('usuario')) {
        _usuario = data['usuario'];
      } else {
        // fallback: si la API devuelve los datos directamente
        _usuario = data;
      }

      notifyListeners();
      print('✅ Sesión iniciada correctamente: ${_usuario?['nombre']}');
      return true;
    }

    print('❌ Error en login o credenciales inválidas');
    return false;
  }

  /// 🚪 Cierra sesión y limpia los datos del usuario
  Future<void> logout() async {
    try {
      await _authService.logout();
    } catch (e) {
      print('⚠️ Error al cerrar sesión: $e');
    }
    _usuario = null;
    notifyListeners();
  }

  /// 🔁 Carga el usuario desde el backend (si hay sesión persistida)
  Future<void> cargarUsuario() async {
    try {
      final data = await _authService.getUsuario();
      if (data != null) {
        if (data.containsKey('usuario')) {
          _usuario = data['usuario'];
        } else {
          _usuario = data;
        }
        notifyListeners();
      }
    } catch (e) {
      print('⚠️ Error al cargar usuario: $e');
    }
  }
}