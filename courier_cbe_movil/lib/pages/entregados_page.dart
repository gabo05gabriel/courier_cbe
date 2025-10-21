import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Importaciones de tus otras páginas
import 'home_page.dart';
import 'rutas_page.dart';
import 'mensajeros_page.dart';
import 'envios_page.dart';
import 'envios_pendientes_page.dart';

class EntregadosPage extends StatefulWidget {
  const EntregadosPage({super.key});

  @override
  State<EntregadosPage> createState() => _EntregadosPageState();
}

class _EntregadosPageState extends State<EntregadosPage> {
  List<dynamic> _entregas = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchEntregas();
  }

  Future<void> _fetchEntregas() async {
    final url = Uri.parse('http://127.0.0.1:8000/api/entregas-json/');
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        setState(() {
          _entregas = jsonDecode(response.body);
          _loading = false;
        });
      } else {
        print('❌ Error cargando entregas: ${response.statusCode}');
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
        title: const Text('Entregas - Courier Bolivian Express'),
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            const DrawerHeader(
              decoration: BoxDecoration(
                color: Color(0xFFD47B2C),
              ),
              child: Text(
                'Menú',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                ),
              ),
            ),
            // 🔸 Dashboard
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
            // 🔸 Rutas
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
            // 🔸 Mensajeros
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
            // 🔸 Envíos
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
            // 🔸 Entregados (página actual)
            ListTile(
              leading: const Icon(Icons.check_circle_outline, color: Colors.green),
              title: const Text('Entregados'),
              tileColor: Colors.green.withOpacity(0.1),
              onTap: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (_) => const EntregadosPage()),
                );
              },
            ),
            // 🔸 Envíos Pendientes
            ListTile(
              leading: const Icon(Icons.pending_actions, color: Colors.grey),
              title: const Text('Envíos Pendientes'),
              onTap: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                      builder: (_) => const EnviosPendientesPage()),
                );
              },
            ),
          ],
        ),
      ),
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(color: Colors.orange),
            )
          : _entregas.isEmpty
              ? const Center(child: Text('No hay entregas registradas.'))
              : RefreshIndicator(
                  onRefresh: _fetchEntregas,
                  child: ListView.builder(
                    itemCount: _entregas.length,
                    itemBuilder: (context, index) {
                      final entrega = _entregas[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 6),
                        child: ListTile(
                          title: Text('Entrega #${entrega['id']}'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Envío ID: ${entrega['envio']}'),
                              Text('Mensajero: ${entrega['mensajero']}'),
                              Text(
                                  'Fecha: ${entrega['fecha_entrega'] ?? "Sin fecha"}'),
                            ],
                          ),
                          trailing: Chip(
                            label: Text(
                              entrega['estado'],
                              style: const TextStyle(color: Colors.white),
                            ),
                            backgroundColor:
                                entrega['estado'] == 'Entregado'
                                    ? Colors.green
                                    : Colors.grey,
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
