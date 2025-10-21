import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:courier_cbe_movil/main.dart';

void main() {
  testWidgets('Courier CBE smoke test', (WidgetTester tester) async {
    // Construye la app principal
    await tester.pumpWidget(const CourierApp());

    // Espera a que la interfaz inicial cargue completamente
    await tester.pumpAndSettle();

    // Verifica que aparezca el texto esperado en la pantalla de inicio o login
    expect(find.text('Courier Bolivian Express'), findsOneWidget);
  });
}
