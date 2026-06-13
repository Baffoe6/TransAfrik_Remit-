import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_client.dart';
import 'transfer_detail_screen.dart';

class TransfersScreen extends StatefulWidget {
  const TransfersScreen({super.key});

  @override
  State<TransfersScreen> createState() => _TransfersScreenState();
}

class _TransfersScreenState extends State<TransfersScreen> {
  List<dynamic> _transfers = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final res = await ApiClient.get('/transfers');
    if (res.statusCode == 200) setState(() => _transfers = jsonDecode(res.body) as List);
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _transfers.length,
        itemBuilder: (_, i) {
          final t = _transfers[i];
          return Card(
            child: ListTile(
              title: Text(t['reference'] ?? ''),
              subtitle: Text('R${t['send_amount_zar']} → GHS ${t['receive_amount_ghs']}'),
              trailing: Chip(label: Text((t['status'] as String).replaceAll('_', ' '), style: const TextStyle(fontSize: 10))),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => TransferDetailScreen(transferId: t['id'])),
              ),
            ),
          );
        },
      ),
    );
  }
}
