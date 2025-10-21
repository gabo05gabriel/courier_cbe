import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'home_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F2),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 5,
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    "Courier Bolivian Express",
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: "Correo electrónico",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: "Contraseña",
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFD47B2C),
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 50),
                    ),
                    onPressed: _loading
                        ? null
                        : () async {
                            setState(() => _loading = true);
                            final success = await authProvider.login(
                              _emailController.text.trim(),
                              _passwordController.text.trim(),
                            );
                            setState(() => _loading = false);

                            if (!context.mounted) return;

                            if (success) {
                              // ✅ Aquí se asegura de reemplazar la pantalla y no apilarla
                              Navigator.pushReplacement(
                                context,
                                MaterialPageRoute(builder: (_) => const HomePage()),
                              );
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text("Credenciales inválidas o servidor no disponible"),
                                  backgroundColor: Colors.redAccent,
                                ),
                              );
                            }
                          },
                    child: _loading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text("Iniciar Sesión"),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
