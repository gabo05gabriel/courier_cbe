import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'login_page.dart';
import 'rutas_page.dart';
import 'mensajeros_page.dart';
import 'envios_page.dart';
import 'entregados_page.dart';
import 'envios_pendientes_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final storage = const FlutterSecureStorage();
  Map<String, dynamic>? usuario;
  Map<String, dynamic>? dashboardData;
  bool _loading = true;
  Timer? _ubicacionTimer;
  bool _compartiendoUbicacion = false; // 👈 Estado actual del botón

  @override
  void initState() {
    super.initState();
    _cargarUsuario();
  }

  @override
  void dispose() {
    _ubicacionTimer?.cancel();
    super.dispose();
  }

  Future<void> _cargarUsuario() async {
    final data = await storage.readAll();
    if (data.containsKey('id')) {
      usuario = {
        'id': int.tryParse(data['id'] ?? '0') ?? 0,
        'nombre': data['nombre'],
        'email': data['email'],
        'rol': data['rol'],
        'is_active': data['is_active'] == 'true',
      };
      if (usuario?['rol'] == 'Administrador') {
        await _fetchDashboardData();
      } else {
        setState(() => _loading = false);
      }
    } else {
      setState(() => _loading = false);
    }
  }

  Future<void> _fetchDashboardData() async {
    try {
      final url = Uri.parse('http://127.0.0.1:8000/usuarios/home_data/');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        setState(() {
          dashboardData = jsonDecode(response.body);
          _loading = false;
        });
      }
    } catch (e) {
      print('⚠️ Error al cargar dashboard: $e');
    }
  }

  /// 🔁 Inicia o detiene el rastreo automático
  void _toggleTracking() {
    if (_compartiendoUbicacion) {
      _detenerTracking();
    } else {
      _iniciarTracking();
    }
  }

  void _iniciarTracking() {
    _ubicacionTimer?.cancel();
    _mandarUbicacion(auto: true); // envía una vez inmediatamente
    _ubicacionTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _mandarUbicacion(auto: true);
    });

    setState(() => _compartiendoUbicacion = true);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('🟢 Compartiendo ubicación cada 5 segundos')),
    );
  }

  void _detenerTracking() {
    _ubicacionTimer?.cancel();
    setState(() => _compartiendoUbicacion = false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('🔴 Dejó de compartir ubicación')),
    );
  }

  /// 📡 Envía la ubicación del mensajero
  Future<void> _mandarUbicacion({bool auto = false}) async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (!auto) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Activa la ubicación')),
          );
        }
        return;
      }

      LocationPermission permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        if (!auto) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Permiso de ubicación denegado')),
          );
        }
        return;
      }

      Position pos = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.best);

      final url =
          Uri.parse('http://127.0.0.1:8000/usuarios/actualizar_ubicacion/');
      final int usuarioId = usuario?['id'] ?? 0;

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'usuario_id': usuarioId,
          'latitud': pos.latitude,
          'longitud': pos.longitude,
        }),
      );

      if (response.statusCode == 200 && !auto) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📍 Ubicación enviada correctamente')),
        );
      } else if (response.statusCode != 200) {
        print('❌ Error al enviar ubicación: ${response.body}');
      }
    } catch (e) {
      print('⚠️ Error al mandar ubicación: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final rol = usuario?['rol'] ?? '';

    return Scaffold(
      backgroundColor: const Color(0xFFF8F8F8),
      appBar: AppBar(
        backgroundColor: const Color(0xFFD47B2C),
        title: Text(
          rol == 'Administrador'
              ? 'Dashboard - Courier Bolivian Express'
              : 'Panel del Mensajero',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await storage.deleteAll();
              _ubicacionTimer?.cancel();
              if (!context.mounted) return;
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const LoginPage()),
              );
            },
          )
        ],
      ),
      drawer: _buildDrawer(context, rol),
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(color: Colors.orange),
            )
          : rol == 'Administrador'
              ? _buildDashboard()
              : _buildMensajero(),
    );
  }

  /// 🔹 Menú lateral (Drawer)
  Widget _buildDrawer(BuildContext context, String rol) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          DrawerHeader(
            decoration: const BoxDecoration(color: Color(0xFFD47B2C)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const CircleAvatar(
                  backgroundColor: Colors.white,
                  radius: 28,
                  child: Icon(Icons.person, color: Color(0xFFD47B2C), size: 40),
                ),
                const SizedBox(height: 10),
                Text(
                  usuario?['nombre'] ?? 'Usuario',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold),
                ),
                Text(
                  usuario?['email'] ?? '',
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ],
            ),
          ),
          if (rol == 'Administrador') ...[
            _menuItem(
              icon: Icons.dashboard,
              title: 'Dashboard',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const HomePage()),
              ),
            ),
            _menuItem(
              icon: Icons.route,
              title: 'Rutas',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const RutasPage()),
              ),
            ),
            _menuItem(
              icon: Icons.person_pin_circle,
              title: 'Mensajeros',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const MensajerosPage()),
              ),
            ),
            _menuItem(
              icon: Icons.local_shipping,
              title: 'Envíos',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const EnviosPage()),
              ),
            ),
            _menuItem(
              icon: Icons.check_circle_outline,
              title: 'Entregados',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const EntregadosPage()),
              ),
            ),
            _menuItem(
              icon: Icons.pending_actions,
              title: 'Envíos Pendientes',
              onTap: () => Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                    builder: (_) => const EnviosPendientesPage()),
              ),
            ),
          ] else ...[
            _menuItem(
              icon: _compartiendoUbicacion
                  ? Icons.stop_circle
                  : Icons.play_circle_fill,
              title: _compartiendoUbicacion
                  ? 'Dejar de compartir ubicación'
                  : 'Compartir ubicación',
              onTap: _toggleTracking,
            ),
          ],
        ],
      ),
    );
  }

  /// 🔹 Item reutilizable del menú
  Widget _menuItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFFD47B2C)),
      title: Text(title),
      onTap: onTap,
    );
  }

  /// 🔹 Vista del mensajero
  Widget _buildMensajero() {
    return Center(
      child: ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor:
              _compartiendoUbicacion ? Colors.redAccent : Colors.orange,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        onPressed: _toggleTracking,
        icon: Icon(
          _compartiendoUbicacion ? Icons.stop_circle : Icons.my_location,
          color: Colors.white,
        ),
        label: Text(
          _compartiendoUbicacion
              ? 'Dejar de compartir ubicación'
              : 'Compartir ubicación',
          style: const TextStyle(color: Colors.white, fontSize: 18),
        ),
      ),
    );
  }

  /// 🔹 Vista del Dashboard (solo Admin)
  Widget _buildDashboard() {
    return RefreshIndicator(
      onRefresh: _fetchDashboardData,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Resumen general',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildCard('Usuarios',
                    dashboardData?['usuarios_count']?.toString() ?? '0',
                    Icons.people, Colors.blueAccent),
                _buildCard('Envíos Pendientes',
                    dashboardData?['envios_pendientes']?.toString() ?? '0',
                    Icons.local_shipping, Colors.orangeAccent),
                _buildCard('Mensajeros Activos',
                    dashboardData?['mensajeros_activos']?.toString() ?? '0',
                    Icons.delivery_dining, Colors.green),
                _buildCard('% Entregados',
                    '${dashboardData?['porcentaje_entregados'] ?? 0}%',
                    Icons.check_circle, Colors.teal),
              ],
            ),
            const SizedBox(height: 32),
            Center(
              child: Text(
                'Actualizado ${DateTime.now().toLocal()}',
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 🔹 Tarjeta individual del Dashboard
  Widget _buildCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 40),
            const SizedBox(height: 10),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.grey, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }
}
