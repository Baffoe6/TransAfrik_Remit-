import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_client.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _profile;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final res = await ApiClient.get('/profile');
    if (res.statusCode == 200) setState(() => _profile = jsonDecode(res.body));
  }

  @override
  Widget build(BuildContext context) {
    if (_profile == null) return const Center(child: CircularProgressIndicator());
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        ListTile(title: const Text('Name'), subtitle: Text('${_profile!['first_name']} ${_profile!['last_name']}')),
        ListTile(title: const Text('KYC Status'), subtitle: Text(_profile!['kyc_status'] ?? 'unknown')),
        ListTile(title: const Text('Country'), subtitle: Text(_profile!['country'] ?? 'ZA')),
      ],
    );
  }
}
