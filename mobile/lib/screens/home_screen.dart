import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import 'beneficiaries_screen.dart';
import 'kyc_screen.dart';
import 'login_screen.dart';
import 'profile_screen.dart';
import 'transfers_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;
  Map<String, dynamic>? _user;

  @override
  void initState() {
    super.initState();
    AuthService.me().then((u) => setState(() => _user = u));
  }

  final _screens = const [
    TransfersScreen(),
    BeneficiariesScreen(),
    KycScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TransAfrik Remit'),
        backgroundColor: const Color(0xFF1B5E3B),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await AuthService.logout();
              if (!context.mounted) return;
              Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
            },
          ),
        ],
      ),
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.send), label: 'Transfers'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Beneficiaries'),
          NavigationDestination(icon: Icon(Icons.verified_user), label: 'KYC'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
