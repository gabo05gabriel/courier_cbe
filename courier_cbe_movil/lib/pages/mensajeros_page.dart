import 'dart:convert';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';

// Importaciones de tus otras páginas
import 'home_page.dart';
import 'rutas_page.dart';
import 'envios_page.dart';
import 'entregados_page.dart';
import 'envios_pendientes_page.dart';

class MensajerosPage extends StatefulWidget {
  const MensajerosPage({super.key});

  @override
  State<MensajerosPage> createState() => _MensajerosPageState();
}

class _MensajerosPageState extends State<MensajerosPage> {
  GoogleMapController? _mapController;
  List<dynamic> _mensajeros = [];
  bool _loading = true;
  final Set<Marker> _markers = {};
  LatLng _center = const LatLng(-16.5, -68.15); // La Paz por defecto

  @override
  void initState() {
    super.initState();
    _fetchMensajeros();
    _obtenerUbicacionActual();
  }

  @override
  void dispose() {
    _mapController?.dispose();
    super.dispose();
  }

  // 🎨 Ícono con nombre — versión compacta y estética
  Future<BitmapDescriptor> _crearIconoConNombre(String nombre) async {
    const double ancho = 150;
    const double altoEtiqueta = 32;
    const double altoTotal = altoEtiqueta + 30;

    final recorder = ui.PictureRecorder();
    final canvas = Canvas(recorder);
    final paint = Paint();

    // === Etiqueta superior minimalista ===
    final etiquetaRect = RRect.fromLTRBR(
      0,
      0,
      ancho,
      altoEtiqueta,
      const Radius.circular(8),
    );

    paint.color = Colors.white;
    canvas.drawRRect(etiquetaRect, paint);

    // Sombra suave
    canvas.drawShadow(Path()..addRRect(etiquetaRect), Colors.black26, 2, false);

    // Texto del nombre (adaptable)
    double fontSize = 14;
    if (nombre.length > 12) fontSize = 13;
    if (nombre.length > 18) fontSize = 12;

    final textPainter = TextPainter(
      text: TextSpan(
        text: nombre,
        style: TextStyle(
          color: Colors.black87,
          fontSize: fontSize,
          fontWeight: FontWeight.w600,
        ),
      ),
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    );

    textPainter.layout(maxWidth: ancho - 10);
    textPainter.paint(canvas, Offset((ancho - textPainter.width) / 2, 7));

    // === Línea conectora ===
    paint.color = Colors.grey.shade400;
    paint.strokeWidth = 1.3;
    canvas.drawLine(
      Offset(ancho / 2, altoEtiqueta),
      Offset(ancho / 2, altoEtiqueta + 8),
      paint,
    );

    // === Marcador circular naranja pequeño ===
    paint.color = const Color(0xFFD47B2C);
    canvas.drawCircle(Offset(ancho / 2, altoEtiqueta + 16), 8, paint);
    paint.color = Colors.white;
    canvas.drawCircle(Offset(ancho / 2, altoEtiqueta + 16), 3, paint);

    final picture = recorder.endRecording();
    final image = await picture.toImage(ancho.toInt(), altoTotal.toInt());
    final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
    final bytes = byteData!.buffer.asUint8List();

    return BitmapDescriptor.fromBytes(bytes);
  }

  Future<void> _fetchMensajeros() async {
    try {
      final url = Uri.parse('http://127.0.0.1:8000/usuarios/mensajeros-json/');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _mensajeros = data;
        });

        _markers.clear();
        for (var m in _mensajeros) {
          final nombre = m['usuario_nombre'] ?? 'Sin nombre';
          final lat = double.tryParse(m['latitud'].toString()) ?? 0.0;
          final lon = double.tryParse(m['longitud'].toString()) ?? 0.0;

          final icono = await _crearIconoConNombre(nombre);

          if (!mounted) return;
          setState(() {
            _markers.add(
              Marker(
                markerId: MarkerId(nombre),
                position: LatLng(lat, lon),
                icon: icono,
                infoWindow: InfoWindow(
                  title: nombre,
                  snippet:
                      '(${lat.toStringAsFixed(5)}, ${lon.toStringAsFixed(5)})',
                ),
              ),
            );
          });
        }

        if (mounted) setState(() => _loading = false);
      } else {
        print('❌ Error cargando mensajeros: ${response.statusCode}');
      }
    } catch (e) {
      print('⚠️ Error de conexión: $e');
    }
  }

  Future<void> _obtenerUbicacionActual() async {
    try {
      bool servicioHabilitado = await Geolocator.isLocationServiceEnabled();
      if (!servicioHabilitado) return;

      LocationPermission permiso = await Geolocator.checkPermission();
      if (permiso == LocationPermission.denied) {
        permiso = await Geolocator.requestPermission();
        if (permiso == LocationPermission.denied) return;
      }

      final posicion = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high);

      if (!mounted) return;
      setState(() {
        _center = LatLng(posicion.latitude, posicion.longitude);
      });

      _mapController?.animateCamera(
        CameraUpdate.newLatLngZoom(_center, 14),
      );
    } catch (e) {
      print('⚠️ Error obteniendo ubicación: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFD47B2C),
        title: const Text('Mensajeros - Courier Bolivian Express'),
      ),
      drawer: _buildDrawer(context),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.orange))
          : Stack(
              children: [
                GoogleMap(
                  onMapCreated: (controller) => _mapController = controller,
                  initialCameraPosition: CameraPosition(
                    target: _center,
                    zoom: 12,
                  ),
                  markers: _markers,
                  myLocationEnabled: true,
                  myLocationButtonEnabled: false,
                  zoomControlsEnabled: false,
                  mapType: MapType.normal,
                ),
                Positioned(
                  right: 16,
                  bottom: 16,
                  child: FloatingActionButton(
                    backgroundColor: const Color(0xFFD47B2C),
                    onPressed: _obtenerUbicacionActual,
                    child: const Icon(Icons.my_location, color: Colors.white),
                  ),
                ),
              ],
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
            tileColor: Colors.teal.withOpacity(0.1),
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
            leading:
                const Icon(Icons.check_circle_outline, color: Colors.green),
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
                MaterialPageRoute(
                    builder: (_) => const EnviosPendientesPage()),
              );
            },
          ),
        ],
      ),
    );
  }
}
