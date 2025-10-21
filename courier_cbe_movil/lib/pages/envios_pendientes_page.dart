import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Importaciones de las demás páginas
import 'home_page.dart';
import 'rutas_page.dart';
import 'mensajeros_page.dart';
import 'envios_page.dart';
import 'entregados_page.dart';

class EnviosPendientesPage extends StatefulWidget {
  const EnviosPendientesPage({super.key});

  @override
  State<EnviosPendientesPage> createState() => _EnviosPendientesPageState();
}

class _EnviosPendientesPageState extends State<EnviosPendientesPage> {
  List<dynamic> _envios = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchEnviosPendientes();
  }

  Future<void> _fetchEnviosPendientes() async {
    final url = Uri.parse('http://127.0.0.1:8000/api/envios-pendientes-json/');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        setState(() {
          _envios = jsonDecode(response.body);
          _loading = false;
        });
      } else {
        print('❌ Error cargando envíos pendientes: ${response.statusCode}');
      }
    } catch (e) {
      print('⚠️ Error de conexión: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFD47B2C),
        title: const Text('Envíos Pendientes - Courier Bolivian Express'),
      ),
      drawer: _buildDrawer(context),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.orange))
          : _envios.isEmpty
              ? const Center(
                  child: Text(
                    'No hay envíos pendientes.',
                    style: TextStyle(fontSize: 16, color: Colors.black54),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchEnviosPendientes,
                  child: ListView.builder(
                    itemCount: _envios.length,
                    padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
                    itemBuilder: (context, index) {
                      final envio = _envios[index];
                      return Card(
                        elevation: 3,
                        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: ListTile(
                          contentPadding:
                              const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                          leading: CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.orange.shade200,
                            child: const Icon(Icons.local_shipping,
                                color: Colors.white, size: 26),
                          ),
                          title: Text(
                            envio['destinatario_nombre'] ?? 'Sin nombre',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 4),
                              Text('Origen: ${envio['origen_direccion']}',
                                  style: const TextStyle(fontSize: 13)),
                              Text('Destino: ${envio['destino_direccion']}',
                                  style: const TextStyle(fontSize: 13)),
                              Text('Teléfono: ${envio['destinatario_telefono']}',
                                  style: const TextStyle(fontSize: 13)),
                              Text('Tipo servicio: ${envio['tipo_servicio']}',
                                  style: const TextStyle(fontSize: 13)),
                              Text('Pago: ${envio['tipo_pago']}',
                                  style: const TextStyle(fontSize: 13)),
                            ],
                          ),
                          trailing: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Chip(
                                label: Text(
                                  envio['estado'],
                                  style: const TextStyle(
                                      color: Colors.white, fontSize: 12),
                                ),
                                backgroundColor: Colors.orange,
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }

  Drawer _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          const DrawerHeader(
            decoration: BoxDecoration(color: Color(0xFFD47B2C)),
            child: Text(
              'Menú',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
              ),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard, color: Colors.orange),
            title: const Text('Dashboard'),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const HomePage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.route, color: Colors.blueGrey),
            title: const Text('Rutas'),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const RutasPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.person_pin_circle, color: Colors.teal),
            title: const Text('Mensajeros'),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const MensajerosPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.local_shipping, color: Colors.deepOrange),
            title: const Text('Envíos'),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const EnviosPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.check_circle_outline, color: Colors.green),
            title: const Text('Entregados'),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const EntregadosPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.pending_actions, color: Colors.grey),
            title: const Text('Envíos Pendientes'),
            tileColor: Colors.grey.withOpacity(0.15),
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const EnviosPendientesPage()),
              );
            },
          ),
        ],
      ),
    );
  }
}
