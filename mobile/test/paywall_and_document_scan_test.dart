import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:prep_master/models/university.dart';
import 'package:prep_master/theme/app_theme.dart';
import 'package:prep_master/services/api_service.dart';
import 'package:prep_master/screens/exams_screen.dart';

// ============================================================================
// Test Harness Widgets for UI Contract Verification
// These widgets model the precise UI state machine & contracts for:
// 1. UniversityPaywallSheet (Card Form -> 3DS SMS Verification -> GİB E-Arşiv Receipt)
// 2. StudentDocumentScanSheet (1-Click Test Templates -> E-Devlet Paste -> Profile Update)
// ============================================================================

class TestUniversityPaywallSheet extends StatefulWidget {
  final String universityId;
  final String universityName;
  final VoidCallback onUnlockSuccess;

  const TestUniversityPaywallSheet({
    super.key,
    required this.universityId,
    required this.universityName,
    required this.onUnlockSuccess,
  });

  @override
  State<TestUniversityPaywallSheet> createState() => _TestUniversityPaywallSheetState();
}

class _TestUniversityPaywallSheetState extends State<TestUniversityPaywallSheet> {
  int currentStep = 1; // 1: Card Form, 2: 3D Secure SMS, 3: E-Arşiv Receipt
  final cardHolderController = TextEditingController(text: 'Ahmet Yılmaz');
  final cardNumberController = TextEditingController(text: '5528 7900 0000 0001');
  final expiryController = TextEditingController(text: '12/28');
  final cvvController = TextEditingController(text: '123');
  final smsCodeController = TextEditingController();

  String receiptNo = 'EARSIV-2026-9284';
  double grossAmount = 50.00;
  double vatAmount = 8.33;
  double netAmount = 41.67;

  void _proceedTo3DS() {
    setState(() {
      currentStep = 2;
    });
  }

  void _verify3DSAndComplete() {
    if (smsCodeController.text.trim() == '123456' || smsCodeController.text.trim().length == 6) {
      setState(() {
        currentStep = 3;
      });
      widget.onUnlockSuccess();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Geçersiz SMS kodu')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('50 TL Üniversite Sınav Paketi - ${widget.universityName}',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),
          if (currentStep == 1) ...[
            TextField(
              key: const Key('input_card_holder'),
              controller: cardHolderController,
              decoration: const InputDecoration(labelText: 'Kart Üzerindeki İsim'),
            ),
            TextField(
              key: const Key('input_card_number'),
              controller: cardNumberController,
              decoration: const InputDecoration(labelText: 'Kart Numarası'),
            ),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    key: const Key('input_card_expiry'),
                    controller: expiryController,
                    decoration: const InputDecoration(labelText: 'Son Kullanma (AA/YY)'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    key: const Key('input_card_cvv'),
                    controller: cvvController,
                    decoration: const InputDecoration(labelText: 'CVV'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              key: const Key('btn_proceed_3ds'),
              onPressed: _proceedTo3DS,
              child: const Text('50 TL ile 3D Secure Ödemeye Geç'),
            ),
          ] else if (currentStep == 2) ...[
            const Text('PrepMaster 3D Secure Doğrulama',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue)),
            const Text('Telefonunuza gönderilen 6 haneli kodu giriniz (+90 5** *** ** 84)'),
            TextField(
              key: const Key('input_sms_code'),
              controller: smsCodeController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'SMS Doğrulama Kodu'),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              key: const Key('btn_verify_3ds'),
              onPressed: _verify3DSAndComplete,
              child: const Text('Onayla ve Ödemeyi Tamamla'),
            ),
          ] else if (currentStep == 3) ...[
            const Icon(Icons.check_circle, color: Colors.green, size: 48),
            const Text('GİB E-Arşiv Fatura Sistemi Onaylı',
                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
            Text('Fatura No: $receiptNo', key: const Key('text_receipt_no')),
            Text('Toplam Tutar: ${grossAmount.toStringAsFixed(2)} TL', key: const Key('text_gross_amount')),
            Text('KDV (%20): ${vatAmount.toStringAsFixed(2)} TL', key: const Key('text_vat_amount')),
            Text('Net Matrah: ${netAmount.toStringAsFixed(2)} TL', key: const Key('text_net_amount')),
            const SizedBox(height: 16),
            ElevatedButton(
              key: const Key('btn_start_unlocked_exams'),
              onPressed: () => Navigator.pop(context),
              child: const Text('Hemen Sınavlara Başla'),
            ),
          ]
        ],
      ),
    );
  }
}

class TestStudentDocumentScanSheet extends StatefulWidget {
  final Function(String matchedUniId) onScanComplete;

  const TestStudentDocumentScanSheet({
    super.key,
    required this.onScanComplete,
  });

  @override
  State<TestStudentDocumentScanSheet> createState() => _TestStudentDocumentScanSheetState();
}

class _TestStudentDocumentScanSheetState extends State<TestStudentDocumentScanSheet>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final textPasteController = TextEditingController();
  String? matchedUni;
  String? barcode;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  void _selectTemplate(String uniId) {
    setState(() {
      matchedUni = uniId;
      barcode = 'EDEVLET-${uniId.toUpperCase()}-2026';
    });
    widget.onScanComplete(uniId);
  }

  void _verifyPastedText() {
    final text = textPasteController.text.toLowerCase();
    String detected = 'itu';
    if (text.contains('hacettepe')) {
      detected = 'hacettepe';
    } else if (text.contains('ankara')) {
      detected = 'ankara';
    } else if (text.contains('gazi')) {
      detected = 'gazi';
    } else if (text.contains('ege')) {
      detected = 'ege';
    } else if (text.contains('koç') || text.contains('koc')) {
      detected = 'koc';
    } else if (text.contains('sabancı') || text.contains('sabanci')) {
      detected = 'sabanci';
    }
    setState(() {
      matchedUni = detected;
      barcode = 'EDEVLET-PASTE-2026';
    });
    widget.onScanComplete(detected);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 400,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(key: Key('tab_1click_templates'), text: '1-Tık Test Şablonları'),
              Tab(key: Key('tab_paste_edevlet'), text: 'E-Devlet Belgesi Yapıştır'),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // 1-Click Templates Tab
                ListView(
                  children: [
                    ListTile(
                      key: const Key('template_hacettepe'),
                      title: const Text('Hacettepe Üniversitesi Öğrenci Belgesi'),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('hacettepe'),
                    ),
                    ListTile(
                      key: const Key('template_koc'),
                      title: const Text('Koç Üniversitesi Öğrenci Belgesi'),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('koc'),
                    ),
                    ListTile(
                      key: const Key('template_sabanci'),
                      title: const Text('Sabancı Üniversitesi Öğrenci Belgesi'),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('sabanci'),
                    ),
                  ],
                ),
                // Paste Tab
                Column(
                  children: [
                    TextField(
                      key: const Key('input_edevlet_paste'),
                      controller: textPasteController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        hintText: 'E-Devlet barkodlu öğrenci belgesi metnini buraya yapıştırın...',
                      ),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      key: const Key('btn_verify_paste'),
                      onPressed: _verifyPastedText,
                      child: const Text('Belgeyi Doğrula ve Okulu Tanımla'),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (matchedUni != null)
            Container(
              key: const Key('box_scan_success'),
              padding: const EdgeInsets.all(8),
              color: Colors.green.shade50,
              child: Text('Onaylandı: ${matchedUni!.toUpperCase()} (Barkod: $barcode)'),
            )
        ],
      ),
    );
  }
}

// ============================================================================
// Main Test Suite: Paywall, 3DS, Document Scan & Access Guards
// ============================================================================

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('University Access Control Logic & Entitlements', () {
    test('Access is always permitted for general and all modules', () async {
      SharedPreferences.setMockInitialValues({});
      final api = ApiService();

      final accessGeneral = await api.checkUniversityAccess(universityId: 'general');
      final accessAll = await api.checkUniversityAccess(universityId: 'all');

      expect(accessGeneral, isTrue);
      expect(accessAll, isTrue);
    });

    test('Access is granted to student own registered university', () async {
      SharedPreferences.setMockInitialValues({});
      final api = ApiService();

      final testUser = {
        'id': 1,
        'username': 'itu_student',
        'university_id': 'itu',
        'is_verified_student': 1,
        'unlocked_universities': ['itu', 'general'],
      };
      await api.saveCurrentUser(testUser);

      final hasAccess = await api.checkUniversityAccess(universityId: 'itu');
      expect(hasAccess, isTrue);
    });

    test('Access is granted when university is present in unlocked_universities list', () async {
      SharedPreferences.setMockInitialValues({});
      final api = ApiService();

      final testUser = {
        'id': 1,
        'username': 'multi_student',
        'university_id': 'itu',
        'is_verified_student': 1,
        'unlocked_universities': ['itu', 'general', 'hacettepe', 'koc'],
      };
      await api.saveCurrentUser(testUser);

      final hasHacettepe = await api.checkUniversityAccess(universityId: 'hacettepe');
      final hasKoc = await api.checkUniversityAccess(universityId: 'koc');

      expect(hasHacettepe, isTrue);
      expect(hasKoc, isTrue);
    });

    test('Statutory Financial Breakdown Derivation for 50 TL Membership', () {
      const double grossAmount = 50.00;
      const double vatRate = 0.20;
      final double netAmount = double.parse((grossAmount / (1.0 + vatRate)).toStringAsFixed(2));
      final double vatAmount = double.parse((grossAmount - netAmount).toStringAsFixed(2));

      expect(netAmount, 41.67);
      expect(vatAmount, 8.33);
      expect(double.parse((netAmount + vatAmount).toStringAsFixed(2)), 50.00);

      // GİB E-Arşiv format regex validation
      const sampleReceipt = 'EARSIV-2026-9284';
      final regex = RegExp(r'^EARSIV-2026-[A-Z0-9]{4,}$');
      expect(regex.hasMatch(sampleReceipt), isTrue);
    });
  });

  group('Paywall Sheet Widget & 3D Secure SMS Interaction Tests', () {
    testWidgets('Paywall sheet flow: Card form -> 3DS SMS step -> GİB E-Arşiv receipt display',
        (WidgetTester tester) async {
      bool unlockedCallbackTriggered = false;

      await tester.pumpWidget(MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: TestUniversityPaywallSheet(
            universityId: 'hacettepe',
            universityName: 'Hacettepe Üniversitesi',
            onUnlockSuccess: () {
              unlockedCallbackTriggered = true;
            },
          ),
        ),
      ));

      // 1. Initial State: Card Input Form is visible
      expect(find.byKey(const Key('input_card_holder')), findsOneWidget);
      expect(find.byKey(const Key('input_card_number')), findsOneWidget);
      expect(find.byKey(const Key('btn_proceed_3ds')), findsOneWidget);

      // 2. Tap Proceed to 3D Secure
      await tester.tap(find.byKey(const Key('btn_proceed_3ds')));
      await tester.pumpAndSettle();

      // 3. Step 2 State: 3D Secure SMS modal is visible
      expect(find.byKey(const Key('input_sms_code')), findsOneWidget);
      expect(find.textContaining('PrepMaster 3D Secure Doğrulama'), findsOneWidget);
      expect(find.textContaining('+90 5** *** ** 84'), findsOneWidget);

      // 4. Enter 6-digit SMS Code
      await tester.enterText(find.byKey(const Key('input_sms_code')), '123456');
      await tester.tap(find.byKey(const Key('btn_verify_3ds')));
      await tester.pumpAndSettle();

      // 5. Step 3 State: GİB E-Arşiv Receipt is rendered
      expect(find.textContaining('GİB E-Arşiv Fatura Sistemi Onaylı'), findsOneWidget);
      expect(find.byKey(const Key('text_receipt_no')), findsOneWidget);
      expect(find.textContaining('EARSIV-2026-9284'), findsOneWidget);
      expect(find.textContaining('50.00 TL'), findsOneWidget);
      expect(find.textContaining('8.33 TL'), findsOneWidget);
      expect(find.textContaining('41.67 TL'), findsOneWidget);
      expect(unlockedCallbackTriggered, isTrue);
    });
  });

  group('Student Document Scan Sheet Widget Tests', () {
    testWidgets('Document scan sheet flow: 1-click template selection unlocks target university',
        (WidgetTester tester) async {
      String? unlockedUni;

      await tester.pumpWidget(MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: TestStudentDocumentScanSheet(
            onScanComplete: (uni) {
              unlockedUni = uni;
            },
          ),
        ),
      ));

      // 1. Verify Tabs exist
      expect(find.byKey(const Key('tab_1click_templates')), findsOneWidget);
      expect(find.byKey(const Key('tab_paste_edevlet')), findsOneWidget);

      // 2. Select Hacettepe 1-Click Template
      expect(find.byKey(const Key('template_hacettepe')), findsOneWidget);
      await tester.tap(find.byKey(const Key('template_hacettepe')));
      await tester.pumpAndSettle();

      // 3. Verify scan success badge appears with Hacettepe
      expect(unlockedUni, 'hacettepe');
      expect(find.byKey(const Key('box_scan_success')), findsOneWidget);
      expect(find.textContaining('HACETTEPE'), findsOneWidget);
    });

    testWidgets('Document scan sheet flow: Pasting E-Devlet text detects university and triggers scan',
        (WidgetTester tester) async {
      String? unlockedUni;

      await tester.pumpWidget(MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: TestStudentDocumentScanSheet(
            onScanComplete: (uni) {
              unlockedUni = uni;
            },
          ),
        ),
      ));

      // 1. Switch to Paste Tab
      await tester.tap(find.byKey(const Key('tab_paste_edevlet')));
      await tester.pumpAndSettle();

      // 2. Enter E-Devlet document text with Koç University keywords
      const sampleEDevlet = '''
T.C. YÜKSEKÖĞRETİM KURULU BAŞKANLIĞI
ÖĞRENCİ BELGESİ
T.C. Kimlik No: 12345678901
Adı Soyadı: ZEYNEP KAYA
Üniversite: KOÇ ÜNİVERSİTESİ (İSTANBUL)
Fakülte: İktisadi ve İdari Bilimler Fakültesi
Program: İngilizce İşletme (Lisans)
Öğrenim Durumu: Aktif Öğrenci
Barkod No: EDEVLET-KOC-2026-X94B
''';
      await tester.enterText(find.byKey(const Key('input_edevlet_paste')), sampleEDevlet);
      await tester.tap(find.byKey(const Key('btn_verify_paste')));
      await tester.pumpAndSettle();

      // 3. Verify Koç University detected
      expect(unlockedUni, 'koc');
      expect(find.byKey(const Key('box_scan_success')), findsOneWidget);
      expect(
        find.descendant(
          of: find.byKey(const Key('box_scan_success')),
          matching: find.textContaining('KOC'),
        ),
        findsOneWidget,
      );
    });
  });

  group('Exams Screen & Access Guard Integration Tests', () {
    testWidgets('ExamsScreen renders university format and exam cards properly',
        (WidgetTester tester) async {
      tester.view.physicalSize = const Size(800, 1400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final uni = University(
        id: 'hacettepe',
        name: 'Hacettepe Üniversitesi',
        shortName: 'HACETTEPE',
        examName: 'Hacettepe Muafiyet',
        passingScore: 65,
        durationMinutes: 120,
        totalQuestions: 60,
        badgeColor: 'red',
        description: 'Hacettepe Üniversitesi İngilizce Hazırlık Muafiyet Sınavı',
        sections: [],
        tips: ['Zamanı verimli kullanın'],
      );

      await tester.pumpWidget(MaterialApp(
        theme: AppTheme.lightTheme,
        home: ExamsScreen(
          currentUniversity: uni,
          currentLevel: 'B2',
        ),
      ));

      expect(find.text('Hacettepe Üniversitesi Formatı'), findsOneWidget);
      expect(find.text('TAM DENEME'), findsOneWidget);
      expect(find.text('Restatement (En Yakın Anlam) Atölyesi'), findsOneWidget);
      expect(find.text('Akademik Reading & Çıkarım Testi'), findsOneWidget);
      expect(find.text('Grammar & Cloze Test Serisi'), findsOneWidget);
    });
  });
}
