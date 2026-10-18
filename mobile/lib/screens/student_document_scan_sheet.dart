import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class StudentDocumentScanSheet extends StatefulWidget {
  final Function(String matchedUniId)? onScanComplete;
  final Function(String uniId, String uniName)? onUniversityVerified;

  const StudentDocumentScanSheet({
    super.key,
    this.onScanComplete,
    this.onUniversityVerified,
  });

  static Future<String?> show(
    BuildContext context, {
    Function(String matchedUniId)? onScanComplete,
    Function(String uniId, String uniName)? onUniversityVerified,
  }) {
    return showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => StudentDocumentScanSheet(
        onScanComplete: onScanComplete,
        onUniversityVerified: onUniversityVerified,
      ),
    );
  }

  @override
  State<StudentDocumentScanSheet> createState() => _StudentDocumentScanSheetState();
}

class _StudentDocumentScanSheetState extends State<StudentDocumentScanSheet>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final textPasteController = TextEditingController();

  bool isScanning = false;
  String? matchedUni;
  String? matchedUniName;
  String? barcode;
  String? studentNo;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    textPasteController.dispose();
    super.dispose();
  }

  Future<void> _selectTemplate(String uniId) async {
    setState(() {
      isScanning = true;
      errorMessage = null;
    });

    final res = await ApiService().scanStudentDocument(sampleKey: uniId);

    if (!mounted) return;

    if (res['success'] == true) {
      final detected = res['matched_university_id']?.toString() ?? uniId;
      final name = res['matched_university_name']?.toString() ?? detected.toUpperCase();
      final code = res['document_barcode']?.toString() ?? 'EDEVLET-${detected.toUpperCase()}-2026';
      final sNo = res['student_number']?.toString() ?? '221049102';

      setState(() {
        isScanning = false;
        matchedUni = detected;
        matchedUniName = name;
        barcode = code;
        studentNo = sNo;
      });

      widget.onScanComplete?.call(detected);
      widget.onUniversityVerified?.call(detected, name);
    } else {
      setState(() {
        isScanning = false;
        errorMessage = res['message']?.toString() ?? 'Belge doğrulanamadı.';
      });
    }
  }

  Future<void> _verifyPastedText() async {
    final text = textPasteController.text.trim();
    if (text.isEmpty) {
      setState(() {
        errorMessage = 'Lütfen E-Devlet belge metnini yapıştırınız.';
      });
      return;
    }

    setState(() {
      isScanning = true;
      errorMessage = null;
    });

    final res = await ApiService().scanStudentDocument(documentText: text);

    if (!mounted) return;

    if (res['success'] == true) {
      final detected = res['matched_university_id']?.toString() ?? 'itu';
      final name = res['matched_university_name']?.toString() ?? detected.toUpperCase();
      final code = res['document_barcode']?.toString() ?? 'EDEVLET-PASTE-2026';
      final sNo = res['student_number']?.toString() ?? '221049102';

      setState(() {
        isScanning = false;
        matchedUni = detected;
        matchedUniName = name;
        barcode = code;
        studentNo = sNo;
      });

      widget.onScanComplete?.call(detected);
      widget.onUniversityVerified?.call(detected, name);
    } else {
      setState(() {
        isScanning = false;
        errorMessage = res['message']?.toString() ?? 'Belge metninde tanınan bir üniversite tespit edilemedi.';
      });
    }
  }

  void _fillSamplePasteText() {
    textPasteController.text = '''
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
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 520,
      padding: EdgeInsets.only(
        top: 16,
        left: 16,
        right: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: Column(
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.teal.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.document_scanner_rounded, color: Colors.teal, size: 24),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'E-Devlet Öğrenci Belgesi Tarama',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                    ),
                    Text(
                      'Barkodlu belgenizi doğrulayarak okulunuza ÜCRETSİZ erişin',
                      style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close, size: 20),
                onPressed: () => Navigator.pop(context, matchedUni),
              ),
            ],
          ),

          const SizedBox(height: 12),

          TabBar(
            controller: _tabController,
            labelColor: Colors.teal.shade800,
            unselectedLabelColor: AppTheme.textMuted,
            indicatorColor: Colors.teal,
            tabs: const [
              Tab(key: Key('tab_1click_templates'), text: '1-Tık Test Şablonları'),
              Tab(key: Key('tab_paste_edevlet'), text: 'E-Devlet Belgesi Yapıştır'),
            ],
          ),

          if (errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(8),
              margin: const EdgeInsets.only(top: 8),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Text(
                errorMessage!,
                style: TextStyle(color: Colors.red.shade800, fontSize: 11, fontWeight: FontWeight.w600),
              ),
            ),
          ],

          const SizedBox(height: 8),

          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // Tab 1: 1-Click Templates
                ListView(
                  children: [
                    ListTile(
                      key: const Key('template_hacettepe'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.red,
                        radius: 16,
                        child: Text('HU', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Hacettepe Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('Hacettepe Üniversitesi YDYO Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('hacettepe'),
                    ),
                    ListTile(
                      key: const Key('template_koc'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.amber,
                        radius: 16,
                        child: Text('KU', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Koç Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('Koç Üniversitesi KUEPE Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('koc'),
                    ),
                    ListTile(
                      key: const Key('template_sabanci'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.indigo,
                        radius: 16,
                        child: Text('SU', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Sabancı Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('Sabancı Üniversitesi ELAE Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('sabanci'),
                    ),
                    ListTile(
                      key: const Key('template_ankara'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.blue,
                        radius: 16,
                        child: Text('AÜ', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Ankara Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('Ankara Üniversitesi YDYO Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('ankara'),
                    ),
                    ListTile(
                      key: const Key('template_boun'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.blueAccent,
                        radius: 16,
                        child: Text('BÜ', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Boğaziçi Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('Boğaziçi Üniversitesi BUEPT Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('boun'),
                    ),
                    ListTile(
                      key: const Key('template_itu'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.teal,
                        radius: 16,
                        child: Text('İTÜ', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('İstanbul Teknik Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('İTÜ Hazırlık Muafiyet', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('itu'),
                    ),
                    ListTile(
                      key: const Key('template_metu'),
                      leading: const CircleAvatar(
                        backgroundColor: Colors.redAccent,
                        radius: 16,
                        child: Text('ODTÜ', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                      title: const Text('Orta Doğu Teknik Üniversitesi Öğrenci Belgesi', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      subtitle: const Text('ODTÜ EPE Hazırlık', style: TextStyle(fontSize: 11)),
                      trailing: const Icon(Icons.arrow_forward_ios, size: 14),
                      onTap: () => _selectTemplate('metu'),
                    ),
                  ],
                ),

                // Tab 2: Paste E-Devlet Text
                SingleChildScrollView(
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Belge Metni', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                          TextButton.icon(
                            onPressed: _fillSamplePasteText,
                            icon: const Icon(Icons.content_paste, size: 14),
                            label: const Text('Örnek Metin Yapıştır', style: TextStyle(fontSize: 11)),
                          ),
                        ],
                      ),
                      TextField(
                        key: const Key('input_edevlet_paste'),
                        controller: textPasteController,
                        maxLines: 4,
                        decoration: InputDecoration(
                          hintText: 'E-Devlet barkodlu öğrenci belgesi metnini buraya yapıştırın...',
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: const EdgeInsets.all(12),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          key: const Key('btn_verify_paste'),
                          onPressed: isScanning ? null : _verifyPastedText,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.teal.shade700,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: isScanning
                              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Text('Belgeyi Doğrula ve Okulu Tanımla', style: TextStyle(fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Scan Success Result Box
          if (matchedUni != null) ...[
            const SizedBox(height: 8),
            Container(
              key: const Key('box_scan_success'),
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green, size: 28),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Onaylandı: ${matchedUni!.toUpperCase()} (Barkod: $barcode)',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.green.shade900),
                        ),
                        Text(
                          'Öğrenci No: $studentNo • Aktif Öğrenci (ÜCRETSİZ Erişim Tanımlandı)',
                          style: TextStyle(fontSize: 11, color: Colors.green.shade800),
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context, matchedUni),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    child: const Text('Tamam', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
