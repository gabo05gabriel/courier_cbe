import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Courier Bolivian Express'),
        backgroundColor: Colors.orange,
      ),
      body: const Center(
        child: Text(
          'Bienvenido a Courier CBE 🚚',
          style: TextStyle(fontSize: 20),
        ),
      ),
    );
  }
}
