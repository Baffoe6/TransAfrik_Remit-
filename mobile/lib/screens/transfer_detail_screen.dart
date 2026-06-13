import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_client.dart';
import 'voucher_screen.dart';

class TransferDetailScreen extends StatefulWidget {
  final int transferId;
  const TransferDetailScreen({super.key, required this.transferId});

  @override
  State<TransferDetailScreen> createState() => _TransferDetailScreenState();
}

class _TransferDetailScreenState extends State<TransferDetailScreen> {
  Map<String, dynamic>? _transfer;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final res = await ApiClient.get('/transfers/${widget.transferId}');
    if (res.statusCode == 200) setState(() => _transfer = jsonDecode(res.body));
  }

  @override
  Widget build(BuildContext context) {
    if (_transfer == null) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    final t = _transfer!;
    final timeline = (t['timeline'] as List?) ?? [];
    final payRef = t['payment_reference'];

    return Scaffold(
      appBar: AppBar(title: Text(t['reference'] ?? 'Transfer'), backgroundColor: const Color(0xFF1B5E3B), foregroundColor: Colors.white),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Status: ${t['status']}', style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text('Send: R${t['send_amount_zar']} · Fee: R${t['fee_zar']} · Total: R${t['total_amount_zar']}'),
          Text('Receive: GHS ${t['receive_amount_ghs']}'),
          if (payRef != null) ...[
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => VoucherScreen(paymentRef: payRef))),
              child: const Text('View Payment Voucher'),
            ),
          ],
          const SizedBox(height: 24),
          const Text('Tracking Timeline', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          ...timeline.map((e) => ListTile(
                dense: true,
                leading: const Icon(Icons.circle, size: 8, color: Color(0xFF1B5E3B)),
                title: Text(e['label'] ?? ''),
                subtitle: Text(e['timestamp'] ?? ''),
              )),
        ],
      ),
    );
  }
}
