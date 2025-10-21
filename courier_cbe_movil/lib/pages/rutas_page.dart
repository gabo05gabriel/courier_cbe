import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'home_page.dart';
import 'mensajeros_page.dart';
import 'envios_page.dart';
import 'entregados_page.dart';
import 'envios_pendientes_page.dart';

class RutasPage extends StatefulWidget {
  const RutasPage({super.key});

  @override
  State<RutasPage> createState() => _RutasPageState();
}

class _RutasPageState extends State<RutasPage> {
  bool _loading = true;
  String? _selectedMensajeroId;
  List<dynamic> _mensajeros = [];
  Map<String, dynamic>? _rutaData;
  GoogleMapController? _mapController;
  Set<Polyline> _polylines = {};
  Set<Marker> _markers = {};

  final String baseUrl = "http://127.0.0.1:8000/rutas/api"; // 👈 Base API

  @override
  void initState() {
    super.initState();
    _initPage();
  }

  Future<void> _initPage() async {
    final auth = Provider.of<AuthProvider>(context, listen: false);

    if (auth.usuario == null) return;

    final rol = auth.usuario?['rol']?.toString().toLowerCase() ?? '';

    if (rol == 'mensajero') {
      // Mensajero → carga directamente su ruta
      await _fetchRutaMensajero(auth.usuario!['id'].toString());
    } else {
      // Admin → muestra lista de mensajeros
      await _fetchMensajeros();
    }
  }

  Future<void> _fetchMensajeros() async {
    try {
      final url = Uri.parse('$baseUrl/mensajeros-json/');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        setState(() {
          _mensajeros = jsonDecode(response.body);
          _loading = false;
        });
      } else {
        print('❌ Error cargando mensajeros: ${response.statusCode}');
      }
    } catch (e) {
      print('⚠️ Error de conexión: $e');
    }
  }

  Future<void> _fetchRutaMensajero(String mensajeroId) async {
    setState(() => _loading = true);
    try {
      final url = Uri.parse('$baseUrl/rutas-json/$mensajeroId/');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _renderRuta(data);
      } else if (response.statusCode == 404) {
        setState(() {
          _rutaData = null;
          _polylines.clear();
          _markers.clear();
        });
        print('ℹ️ No hay rutas para este mensajero.');
      } else {
        print('❌ Error al obtener ruta: ${response.statusCode}');
      }
    } catch (e) {
      print('⚠️ Error de conexión: $e');
    }
    setState(() => _loading = false);
  }

  void _renderRuta(Map<String, dynamic> data) {
    _rutaData = data;
    final List<dynamic> coords = data['coordenadas'] ?? [];
    final List<LatLng> points =
        coords.map((c) => LatLng(c['lat'], c['lng'])).toList();

    final polyline = Polyline(
      polylineId: const PolylineId('ruta'),
      color: Colors.orange,
      width: 5,
      points: points,
    );

    final markers = <Marker>{};
    if (points.isNotEmpty) {
      markers.add(Marker(
        markerId: const MarkerId('inicio'),
        position: points.first,
        infoWindow: const InfoWindow(title: 'Inicio'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
      ));
      markers.add(Marker(
        markerId: const MarkerId('fin'),
        position: points.last,
        infoWindow: const InfoWindow(title: 'Fin'),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
      ));
    }

    setState(() {
      _polylines = {polyline};
      _markers = markers;
    });

    if (_mapController != null && points.isNotEmpty) {
      _mapController!.animateCamera(CameraUpdate.newLatLngZoom(points.first, 13));
    }
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
              style: TextStyle(color: Colors.white, fontSize: 24),
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
            tileColor: Colors.orange.withOpacity(0.1),
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

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final rol = auth.usuario?['rol']?.toString().toLowerCase() ?? '';
    final esMensajero = rol == 'mensajero';

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFD47B2C),
        title: const Text('Rutas del Mensajero'),
      ),
      drawer: _buildDrawer(context),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.orange))
          : Column(
              children: [
                // 👇 Solo los ADMIN pueden ver el selector
                if (!esMensajero)
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: DropdownButtonFormField<String>(
                      decoration: const InputDecoration(
                        labelText: 'Seleccionar mensajero',
                        border: OutlineInputBorder(),
                      ),
                      value: _selectedMensajeroId,
                      items: _mensajeros
                          .map((m) => DropdownMenuItem<String>(
                                value: m['id'].toString(),
                                child: Text(m['nombre']),
                              ))
                          .toList(),
                      onChanged: (val) {
                        setState(() => _selectedMensajeroId = val);
                        if (val != null) _fetchRutaMensajero(val);
                      },
                    ),
                  ),
                Expanded(
                  child: _rutaData == null
                      ? const Center(
                          child: Text(
                            'No hay ruta disponible para este mensajero',
                            style: TextStyle(fontSize: 16, color: Colors.grey),
                          ),
                        )
                      : GoogleMap(
                          onMapCreated: (controller) => _mapController = controller,
                          polylines: _polylines,
                          markers: _markers,
                          initialCameraPosition: const CameraPosition(
                            target: LatLng(-16.5, -68.13),
                            zoom: 12,
                          ),
                        ),
                ),
              ],
            ),
    );
  }
}
