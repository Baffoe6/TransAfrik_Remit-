import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const TransAfrikApp());
}

class TransAfrikApp extends StatelessWidget {
  const TransAfrikApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TransAfrik Remit',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1B5E3B)),
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
