import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'home_page.dart';
import 'rutas_page.dart';
import 'mensajeros_page.dart';
import 'entregados_page.dart';
import 'envios_pendientes_page.dart';

class EnviosPage extends StatefulWidget {
  const EnviosPage({super.key});

  @override
  State<EnviosPage> createState() => _EnviosPageState();
}

class _EnviosPageState extends State<EnviosPage> {
  final String baseUrl = "http://127.0.0.1:8000/api";
  bool _loading = true;
  List<dynamic> _envios = [];

  @override
  void initState() {
    super.initState();
    _fetchEnvios();
  }

  Future<void> _fetchEnvios() async {
    try {
      final url = Uri.parse('$baseUrl/envios-pendientes-json/');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        setState(() {
          _envios = jsonDecode(response.body);
          _loading = false;
        });
      } else {
        print('❌ Error al obtener envíos: ${response.statusCode}');
      }
    } catch (e) {
      print('⚠️ Error conexión: $e');
    }
  }

  Future<void> _abrirDialogEntrega(Map<String, dynamic> envio) async {
    File? firmaFile;
    final picker = ImagePicker();
    final _formKey = GlobalKey<FormState>();
    String? _estado = "Entregado";
    bool _pagado = false;
    String? _tipoIncidencia;
    String? _descripcionIncidencia;

    await showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(builder: (context, setState) {
          return AlertDialog(
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            title: Text("Registrar entrega\n#${envio['id']}"),
            content: SingleChildScrollView(
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<String>(
                      value: _estado,
                      decoration:
                          const InputDecoration(labelText: "Estado del envío"),
                      items: const [
                        DropdownMenuItem(
                            value: "Entregado", child: Text("Entregado")),
                        DropdownMenuItem(
                            value: "No entregado",
                            child: Text("No entregado")),
                      ],
                      onChanged: (val) => setState(() => _estado = val),
                    ),
                    CheckboxListTile(
                      value: _pagado,
                      onChanged: (val) => setState(() => _pagado = val!),
                      title: const Text("Pagado"),
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: () async {
                        final picked = await picker.pickImage(
                            source: ImageSource.camera, imageQuality: 80);
                        if (picked != null) {
                          setState(() => firmaFile = File(picked.path));
                        }
                      },
                      icon: const Icon(Icons.edit_document),
                      label: const Text("Subir firma del cliente"),
                      style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange),
                    ),
                    if (firmaFile != null)
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Image.file(firmaFile!, height: 100),
                      ),
                    const Divider(),
                    TextFormField(
                      decoration:
                          const InputDecoration(labelText: "Tipo de incidencia"),
                      onChanged: (val) => _tipoIncidencia = val,
                    ),
                    TextFormField(
                      decoration:
                          const InputDecoration(labelText: "Descripción"),
                      onChanged: (val) => _descripcionIncidencia = val,
                    ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("Cancelar")),
              ElevatedButton(
                style:
                    ElevatedButton.styleFrom(backgroundColor: Colors.green[700]),
                onPressed: () async {
                  Navigator.pop(context);
                  await _registrarEntrega(envio['id'], _estado!, _pagado,
                      firmaFile, _tipoIncidencia, _descripcionIncidencia);
                },
                child: const Text("Guardar"),
              ),
            ],
          );
        });
      },
    );
  }

  Future<void> _registrarEntrega(
      int envioId,
      String estado,
      bool pagado,
      File? firmaFile,
      String? tipoIncidencia,
      String? descripcionIncidencia) async {
    try {
      final uri = Uri.parse('$baseUrl/entregas/crear/$envioId/');
      final request = http.MultipartRequest('POST', uri);

      request.fields['estado'] = estado;
      request.fields['pagado'] = pagado.toString();
      if (tipoIncidencia != null && tipoIncidencia.isNotEmpty) {
        request.fields['tipo_incidente'] = tipoIncidencia;
        request.fields['descripcion_incidente'] = descripcionIncidencia ?? '';
      }
      if (firmaFile != null) {
        request.files.add(await http.MultipartFile.fromPath(
          'foto_firma',
          firmaFile.path,
        ));
      }

      final response = await request.send();
      if (response.statusCode == 200 || response.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text("Entrega registrada correctamente ✅"),
          backgroundColor: Colors.green,
        ));
        _fetchEnvios();
      } else {
        print("❌ Error al registrar entrega: ${response.statusCode}");
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text("Error al registrar entrega (${response.statusCode})"),
          backgroundColor: Colors.red,
        ));
      }
    } catch (e) {
      print("⚠️ Error en envío: $e");
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
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => const RutasPage()),
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.local_shipping, color: Colors.deepOrange),
            title: const Text('Envíos'),
            tileColor: Colors.orange.withOpacity(0.1),
            onTap: () {},
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
            title: const Text('Pendientes'),
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
        title: const Text('Gestión de Envíos'),
      ),
      drawer: _buildDrawer(context),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Colors.orange))
          : _envios.isEmpty
              ? const Center(
                  child: Text("No hay envíos pendientes"),
                )
              : ListView.builder(
                  itemCount: _envios.length,
                  itemBuilder: (context, index) {
                    final envio = _envios[index];
                    return Card(
                      margin: const EdgeInsets.all(8),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        title: Text(
                          "${envio['tipo']} - ${envio['destinatario_nombre']}",
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                            "Origen: ${envio['origen_direccion']}\nDestino: ${envio['destino_direccion']}"),
                        trailing: IconButton(
                          icon: const Icon(Icons.edit, color: Colors.orange),
                          onPressed: () => _abrirDialogEntrega(envio),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
