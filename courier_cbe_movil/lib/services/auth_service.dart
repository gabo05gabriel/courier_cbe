import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../api/api.dart'; // ✅ Importa tu archivo con LOGIN_URL y demás

/// Servicio de autenticación para login, sesión y logout
class AuthService {
  final storage = const FlutterSecureStorage();

  // ============================================================
  // 🔐 LOGIN
  // ============================================================
  Future<Map<String, dynamic>?> login(String email, String password) async {
  try {
    final url = Uri.parse(LOGIN_URL);
    print("🌍 Intentando login en: $url");
    print("📧 Email: $email");

    // 🔹 Usa los nombres exactos que Django espera: "email" y "contrasena"
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'email': email.trim(),
        'contrasena': password.trim(), // 👈 CAMBIO CLAVE
      }),
    );

    print('📡 Código de respuesta: ${response.statusCode}');
    print('🧾 Cuerpo recibido: ${response.body}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(response.body);

      // Si la respuesta incluye un campo "usuario", úsalo
      final user = data.containsKey('usuario') ? data['usuario'] : data;

      // ✅ Guarda los datos en almacenamiento seguro
      await storage.write(key: 'id', value: user['id'].toString());
      await storage.write(key: 'nombre', value: user['nombre'] ?? '');
      await storage.write(key: 'email', value: user['email'] ?? '');
      await storage.write(key: 'rol', value: user['rol'] ?? '');
      await storage.write(key: 'is_active', value: (user['is_active'] ?? true).toString());

      print('✅ Login exitoso. Usuario guardado en almacenamiento seguro.');
      return data;
    } else {
      print('❌ Error en login: ${response.body}');
      return null;
    }
  } catch (e) {
    print('⚠️ Error en login: $e');
    return null;
  }
}


  // ============================================================
  // 👤 OBTENER USUARIO LOCAL
  // ============================================================
  Future<Map<String, dynamic>?> getUsuario() async {
    try {
      final idStr = await storage.read(key: 'id');
      if (idStr == null) {
        print('⚠️ No hay usuario guardado localmente.');
        return null;
      }

      final id = int.tryParse(idStr) ?? 0;
      final nombre = await storage.read(key: 'nombre');
      final email = await storage.read(key: 'email');
      final rol = await storage.read(key: 'rol');
      final isActiveStr = await storage.read(key: 'is_active');
      final isActive = isActiveStr == 'true' || isActiveStr == '1';

      final user = {
        'id': id,
        'nombre': nombre,
        'email': email,
        'rol': rol,
        'is_active': isActive,
      };

      print('👤 Usuario cargado desde almacenamiento: $user');
      return user;
    } catch (e) {
      print('⚠️ Error obteniendo usuario: $e');
      return null;
    }
  }

  // ============================================================
  // 🚪 LOGOUT
  // ============================================================
  Future<void> logout() async {
    await storage.deleteAll();
    print('👋 Sesión cerrada y datos locales eliminados.');
  }
}
