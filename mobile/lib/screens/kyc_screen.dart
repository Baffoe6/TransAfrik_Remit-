import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_client.dart';

class KycScreen extends StatefulWidget {
  const KycScreen({super.key});

  @override
  State<KycScreen> createState() => _KycScreenState();
}

class _KycScreenState extends State<KycScreen> {
  List<dynamic> _docs = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final res = await ApiClient.get('/kyc/documents');
    if (res.statusCode == 200) setState(() => _docs = jsonDecode(res.body) as List);
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('KYC Documents', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        if (_docs.isEmpty)
          const Text('No documents uploaded. Upload ID, proof of address, and selfie via the web portal.')
        else
          ..._docs.map((d) => Card(
                child: ListTile(
                  title: Text(d['document_type'] ?? ''),
                  subtitle: Text('Status: ${d['status']}'),
                ),
              )),
      ],
    );
  }
}
