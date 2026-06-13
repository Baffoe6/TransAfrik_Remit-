import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

class VoucherScreen extends StatelessWidget {
  final Map<String, dynamic> paymentRef;
  const VoucherScreen({super.key, required this.paymentRef});

  @override
  Widget build(BuildContext context) {
    final ref = paymentRef['reference_number'] ?? '';
    final voucher = paymentRef['voucher_number'] ?? '';
    final qr = paymentRef['qr_data'] ?? ref;
    final barcode = paymentRef['barcode_data'] ?? '';

    return Scaffold(
      appBar: AppBar(title: const Text('Payment Voucher'), backgroundColor: const Color(0xFF1B5E3B), foregroundColor: Colors.white),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            QrImageView(data: qr, size: 200, backgroundColor: Colors.white),
            const SizedBox(height: 24),
            Text('Reference', style: Theme.of(context).textTheme.labelLarge),
            Text(ref, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text('Voucher: $voucher'),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              color: Colors.grey.shade100,
              width: double.infinity,
              child: Text(barcode, style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
            ),
            const Spacer(),
            const Text('Present this voucher at a Pay@ or EasyPay outlet', textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}
