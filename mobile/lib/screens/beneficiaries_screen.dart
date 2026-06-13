import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_client.dart';

class BeneficiariesScreen extends StatefulWidget {
  const BeneficiariesScreen({super.key});

  @override
  State<BeneficiariesScreen> createState() => _BeneficiariesScreenState();
}

class _BeneficiariesScreenState extends State<BeneficiariesScreen> {
  List<dynamic> _items = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final res = await ApiClient.get('/beneficiaries');
    if (res.statusCode == 200) setState(() => _items = jsonDecode(res.body) as List);
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _items.length,
      itemBuilder: (_, i) {
        final b = _items[i];
        return Card(
          child: ListTile(
            title: Text(b['full_name'] ?? ''),
            subtitle: Text('${b['mobile_money_provider']} · ${b['mobile_wallet_number']}'),
            trailing: Text(b['status'] ?? '', style: const TextStyle(fontSize: 12)),
          ),
        );
      },
    );
  }
}
