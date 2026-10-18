import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'student_document_scan_sheet.dart';

class UniversityPaywallSheet extends StatefulWidget {
  final String universityId;
  final String universityName;
  final VoidCallback? onUnlockSuccess;

  const UniversityPaywallSheet({
    super.key,
    required this.universityId,
    required this.universityName,
    this.onUnlockSuccess,
  });

  static Future<bool?> show(
    BuildContext context, {
    required String universityId,
    required String universityName,
    VoidCallback? onUnlockSuccess,
  }) {
    return showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => UniversityPaywallSheet(
        universityId: universityId,
        universityName: universityName,
        onUnlockSuccess: onUnlockSuccess,
      ),
    );
  }

  @override
  State<UniversityPaywallSheet> createState() => _UniversityPaywallSheetState();
}

class _UniversityPaywallSheetState extends State<UniversityPaywallSheet> {
  int currentStep = 1; // 1: Card Form, 2: 3D Secure SMS, 3: E-Arşiv Receipt
  bool isLoading = false;
  String? errorMessage;

  final cardHolderController = TextEditingController(text: 'Ahmet Yılmaz');
  final cardNumberController = TextEditingController(text: '5528 7900 0000 0001');
  final expiryController = TextEditingController(text: '12/28');
  final cvvController = TextEditingController(text: '123');
  final smsCodeController = TextEditingController();

  String sessionId = '';
  String maskedPhone = '+90 5** *** ** 84';
  String receiptNo = 'EARSIV-2026-9284';
  double grossAmount = 50.00;
  double vatAmount = 8.33;
  double netAmount = 41.67;

  @override
  void dispose() {
    cardHolderController.dispose();
    cardNumberController.dispose();
    expiryController.dispose();
    cvvController.dispose();
    smsCodeController.dispose();
    super.dispose();
  }

  void _fillTestCard() {
    setState(() {
      cardHolderController.text = 'Ahmet Yılmaz';
      cardNumberController.text = '5528 7900 0000 0001';
      expiryController.text = '12/28';
      cvvController.text = '123';
      errorMessage = null;
    });
  }

  void _fillTestSms() {
    setState(() {
      smsCodeController.text = '123456';
      errorMessage = null;
    });
  }

  Future<void> _proceedTo3DS() async {
    final holder = cardHolderController.text.trim();
    final number = cardNumberController.text.trim();
    final expiry = expiryController.text.trim();
    final cvv = cvvController.text.trim();

    if (holder.isEmpty || number.isEmpty || expiry.isEmpty || cvv.isEmpty) {
      setState(() {
        errorMessage = 'Lütfen tüm kart bilgilerini eksiksiz doldurunuz.';
      });
      return;
    }

    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    final expParts = expiry.split('/');
    final expMonth = expParts.isNotEmpty ? expParts[0].trim() : '12';
    final expYear = expParts.length > 1 ? expParts[1].trim() : '28';

    final res = await ApiService().initiate3DSecurePayment(
      universityId: widget.universityId,
      cardHolder: holder,
      cardNumber: number,
      expireMonth: expMonth,
      expireYear: expYear,
      cvv: cvv,
      amountTry: 50.0,
    );

    if (!mounted) return;

    setState(() {
      isLoading = false;
      sessionId = res['session_id']?.toString() ?? '3DS-SESSION-${DateTime.now().millisecondsSinceEpoch}';
      maskedPhone = res['masked_phone']?.toString() ?? '+90 5** *** ** 84';
      currentStep = 2;
    });
  }

  Future<void> _verify3DSAndComplete() async {
    final code = smsCodeController.text.trim();
    if (code.length != 6) {
      setState(() {
        errorMessage = 'Geçersiz SMS kodu: Lütfen 6 haneli doğrulama kodunu giriniz.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Geçersiz SMS kodu')),
      );
      return;
    }

    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    final res = await ApiService().unlockUniversityMembership(
      universityId: widget.universityId,
      cardHolder: cardHolderController.text.trim(),
      cardNumber: cardNumberController.text.trim(),
      sessionId: sessionId.isNotEmpty ? sessionId : null,
      smsCode: code,
    );

    if (!mounted) return;

    if (res['success'] == true || res['status'] == 'success') {
      final receipt = res['receipt'] as Map<String, dynamic>?;
      setState(() {
        isLoading = false;
        if (receipt != null) {
          receiptNo = receipt['receipt_no']?.toString() ?? receiptNo;
          grossAmount = (receipt['gross_amount'] as num?)?.toDouble() ?? 50.00;
          vatAmount = (receipt['vat_amount'] as num?)?.toDouble() ?? 8.33;
          netAmount = (receipt['net_amount'] as num?)?.toDouble() ?? 41.67;
        }
        currentStep = 3;
      });
      widget.onUnlockSuccess?.call();
    } else {
      setState(() {
        isLoading = false;
        errorMessage = res['message']?.toString() ?? 'Ödeme doğrulanamadı.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(res['message']?.toString() ?? 'Geçersiz SMS kodu')),
      );
    }
  }

  void _openStudentScan() {
    Navigator.pop(context);
    StudentDocumentScanSheet.show(
      context,
      onScanComplete: (uni) {
        widget.onUnlockSuccess?.call();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),

            // Sheet Title
            Text(
              '50 TL Üniversite Sınav Paketi - ${widget.universityName}',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: AppTheme.textMain,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              '50.00 TL (Tek Seferlik • Sınırsız Sınav Erişimi)',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: AppTheme.brandBlue,
              ),
            ),
            const SizedBox(height: 8),

            // Free Student Document Alternative Link
            if (currentStep == 1)
              Center(
                child: TextButton.icon(
                  onPressed: _openStudentScan,
                  icon: const Icon(Icons.school_outlined, size: 16, color: Colors.teal),
                  label: const Text(
                    'Bu üniversitede mi okuyorsunuz? E-Devlet Belgesi ile Ücretsiz Doğrulayın →',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.teal),
                  ),
                ),
              ),

            if (errorMessage != null) ...[
              Container(
                padding: const EdgeInsets.all(10),
                margin: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Text(
                  errorMessage!,
                  style: TextStyle(color: Colors.red.shade800, fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ),
            ],

            const SizedBox(height: 12),

            // STEP 1: Card Input Form
            if (currentStep == 1) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Kart Bilgileri', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  TextButton.icon(
                    onPressed: _fillTestCard,
                    icon: const Icon(Icons.flash_on, size: 14),
                    label: const Text('Test Kartını Doldur', style: TextStyle(fontSize: 11)),
                  ),
                ],
              ),
              TextField(
                key: const Key('input_card_holder'),
                controller: cardHolderController,
                decoration: InputDecoration(
                  labelText: 'Kart Üzerindeki İsim',
                  prefixIcon: const Icon(Icons.person_outline, size: 20),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                key: const Key('input_card_number'),
                controller: cardNumberController,
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Kart Numarası',
                  prefixIcon: const Icon(Icons.credit_card, size: 20),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      key: const Key('input_card_expiry'),
                      controller: expiryController,
                      decoration: InputDecoration(
                        labelText: 'Son Kullanma (AA/YY)',
                        hintText: '12/28',
                        prefixIcon: const Icon(Icons.date_range, size: 20),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      key: const Key('input_card_cvv'),
                      controller: cvvController,
                      keyboardType: TextInputType.number,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: 'CVV',
                        hintText: '123',
                        prefixIcon: const Icon(Icons.lock_outline, size: 20),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              ElevatedButton(
                key: const Key('btn_proceed_3ds'),
                onPressed: isLoading ? null : _proceedTo3DS,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.brandBlue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: isLoading
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text(
                        '50 TL ile 3D Secure Ödemeye Geç',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      ),
              ),
            ]

            // STEP 2: 3D Secure Bank SMS Verification
            else if (currentStep == 2) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.security_rounded, color: Colors.blue, size: 36),
                    const SizedBox(height: 6),
                    const Text(
                      'PrepMaster 3D Secure Doğrulama',
                      style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue, fontSize: 15),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Telefonunuza gönderilen 6 haneli kodu giriniz ($maskedPhone)',
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 12, color: Colors.black87),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Doğrulama Kodu', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  TextButton.icon(
                    onPressed: _fillTestSms,
                    icon: const Icon(Icons.flash_on, size: 14),
                    label: const Text('123456 Doldur', style: TextStyle(fontSize: 11)),
                  ),
                ],
              ),
              TextField(
                key: const Key('input_sms_code'),
                controller: smsCodeController,
                keyboardType: TextInputType.number,
                textAlign: TextAlign.center,
                maxLength: 6,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 8),
                decoration: InputDecoration(
                  counterText: '',
                  labelText: 'SMS Doğrulama Kodu',
                  hintText: '123456',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 8),
              const Center(
                child: Text(
                  'Kalan Süre: 02:45 • Test sandbox onay kodu: 123456',
                  style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                ),
              ),
              const SizedBox(height: 18),
              ElevatedButton(
                key: const Key('btn_verify_3ds'),
                onPressed: isLoading ? null : _verify3DSAndComplete,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: isLoading
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text(
                        'Onayla ve Ödemeyi Tamamla',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      ),
              ),
            ]

            // STEP 3: E-Arşiv Receipt & Success
            else if (currentStep == 3) ...[
              const Center(child: Icon(Icons.check_circle, color: Colors.green, size: 52)),
              const SizedBox(height: 8),
              const Center(
                child: Text(
                  'GİB E-Arşiv Fatura Sistemi Onaylı',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 16),
                ),
              ),
              const SizedBox(height: 4),
              Center(
                child: Text(
                  '${widget.universityName} muafiyet sınavları ve modülleri süresiz olarak açıldı.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Fatura No: $receiptNo', key: const Key('text_receipt_no'), style: const TextStyle(fontWeight: FontWeight.bold)),
                    const Divider(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Net Matrah:', style: TextStyle(color: Colors.black87)),
                        Text('Net Matrah: ${netAmount.toStringAsFixed(2)} TL', key: const Key('text_net_amount')),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('KDV Oranı & Tutarı (%20):', style: TextStyle(color: Colors.black87)),
                        Text('KDV (%20): ${vatAmount.toStringAsFixed(2)} TL', key: const Key('text_vat_amount')),
                      ],
                    ),
                    const Divider(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Toplam Tutar:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        Text(
                          'Toplam Tutar: ${grossAmount.toStringAsFixed(2)} TL',
                          key: const Key('text_gross_amount'),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.green),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                key: const Key('btn_start_unlocked_exams'),
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: const Text(
                  'Hemen Sınavlara Başla',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
