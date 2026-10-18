import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/university.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../main.dart';
import 'exam_runner_screen.dart';
import 'university_picker_dialog.dart';
import 'listening_screen.dart';
import 'writing_screen.dart';
import 'speaking_screen.dart';
import '../services/sync_service.dart';

class DashboardScreen extends StatefulWidget {
  final University currentUniversity;
  final String currentLevel;
  final Function(University) onUniversityChange;
  final Function(String) onLevelChange;
  final Function(int) onTabSwitch;

  const DashboardScreen({
    super.key,
    required this.currentUniversity,
    required this.currentLevel,
    required this.onUniversityChange,
    required this.onLevelChange,
    required this.onTabSwitch,
  });

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<University> _universities = [];
  Map<String, dynamic>? _stats;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final unis = await ApiService().getUniversities();
    final stats = await ApiService().getStats();
    if (mounted) {
      setState(() {
        _universities = unis;
        _stats = stats;
      });
    }
  }

  void _openUniPicker() {
    if (_universities.isEmpty) return;
    showDialog(
      context: context,
      builder: (_) => UniversityPickerDialog(
        universities: _universities,
        selectedUniversity: widget.currentUniversity,
        onSelect: (uni) {
          widget.onUniversityChange(uni);
        },
      ),
    );
  }

  Future<void> _performCloudSync() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Row(
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
            ),
            SizedBox(width: 12),
            Text('Bulut verileri eşitleniyor...'),
          ],
        ),
        duration: Duration(seconds: 1),
      ),
    );

    final syncData = await SyncService().pullSync();
    await _loadData();

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(syncData != null ? '✓ Bulut senkronizasyonu tamamlandı!' : 'Senkronizasyon çevrimdışı modda saklandı.'),
        backgroundColor: syncData != null ? Colors.green.shade700 : Colors.blueGrey,
      ),
    );
  }

  void _openVerificationDialog() {
    final messenger = ScaffoldMessenger.of(context);
    final emailCtrl = TextEditingController(text: 'ogrenci@${widget.currentUniversity.id}.edu.tr');
    final numCtrl = TextEditingController(text: '040220199');
    final otpCtrl = TextEditingController();

    bool isOtpStep = false;
    bool isLoading = false;
    String statusMessage = '';
    bool isError = false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (dlgCtx, setDialogState) => AlertDialog(

          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Row(
            children: [
              Icon(isOtpStep ? Icons.mark_email_read_outlined : Icons.verified_user, color: Colors.green.shade700),
              const SizedBox(width: 8),
              Text(
                isOtpStep ? 'E-Posta OTP Doğrulama' : 'Öğrenci Doğrulama',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!isOtpStep) ...[
                const Text(
                  'Üniversite .edu.tr e-posta ve öğrenci numaranızı girerek 6 haneli doğrulama kodunu talep edin.',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: emailCtrl,
                  decoration: InputDecoration(
                    labelText: 'Edu E-posta',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: numCtrl,
                  decoration: InputDecoration(
                    labelText: 'Öğrenci Numarası',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ] else ...[
                Text(
                  '${emailCtrl.text.trim()} adresine gönderilen 6 haneli doğrulama kodunu girin (Geçerlilik: 5 dk):',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: otpCtrl,
                  maxLength: 6,
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: 8),
                  decoration: InputDecoration(
                    counterText: '',
                    hintText: '000000',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Kod gelmedi mi?', style: TextStyle(fontSize: 11, color: Colors.grey)),
                    TextButton(
                      onPressed: isLoading ? null : () async {
                        setDialogState(() {
                          isLoading = true;
                          statusMessage = 'Yeni kod talep ediliyor...';
                          isError = false;
                        });
                        final res = await SyncService().requestStudentOtp(
                          email: emailCtrl.text.trim(),
                          studentNumber: numCtrl.text.trim(),
                        );
                        setDialogState(() {
                          isLoading = false;
                          statusMessage = res['message'] ?? 'Kod tekrar gönderildi!';
                          isError = res['status'] == 'error';
                        });
                      },
                      child: const Text('Tekrar Gönder', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ],
              if (statusMessage.isNotEmpty) ...[
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isError ? Colors.red.shade50 : Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: isError ? Colors.red.shade200 : Colors.green.shade200),
                  ),
                  child: Text(
                    statusMessage,
                    style: TextStyle(
                      fontSize: 11,
                      color: isError ? Colors.red.shade800 : Colors.green.shade800,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('İptal'),
            ),
            if (!isOtpStep)
              ElevatedButton(
                onPressed: isLoading ? null : () async {
                  final email = emailCtrl.text.trim();
                  final num = numCtrl.text.trim();
                  if (email.isEmpty || num.isEmpty) {
                    setDialogState(() {
                      statusMessage = 'Lütfen tüm alanları doldurun.';
                      isError = true;
                    });
                    return;
                  }

                  setDialogState(() {
                    isLoading = true;
                    statusMessage = '';
                  });

                  final res = await SyncService().requestStudentOtp(
                    email: email,
                    studentNumber: num,
                  );

                  setDialogState(() {
                    isLoading = false;
                    if (res['status'] == 'error') {
                      statusMessage = res['message'] ?? 'Kod gönderilemedi.';
                      isError = true;
                    } else {
                      isOtpStep = true;
                      statusMessage = res['message'] ?? 'Doğrulama kodu gönderildi!';
                      isError = false;
                    }
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.brandBlue,
                  foregroundColor: Colors.white,
                ),
                child: isLoading
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Kod Gönder'),
              )
            else
              ElevatedButton(
                onPressed: isLoading ? null : () async {
                  final code = otpCtrl.text.trim();
                  if (code.length != 6) {
                    setDialogState(() {
                      statusMessage = 'Lütfen 6 haneli kodu giriniz.';
                      isError = true;
                    });
                    return;
                  }

                  setDialogState(() {
                    isLoading = true;
                    statusMessage = '';
                  });

                  final res = await SyncService().verifyStudentOtp(
                    email: emailCtrl.text.trim(),
                    otpCode: code,
                  );

                  if (!mounted) return;

                  if (res['is_verified'] == true) {
                    if (ctx.mounted) {
                      Navigator.pop(ctx);
                    }
                    messenger.showSnackBar(
                      SnackBar(
                        content: Text(res['message'] ?? 'Öğrenci hesabınız başarıyla doğrulandı!'),
                        backgroundColor: Colors.green.shade700,
                      ),
                    );
                    _loadData();

                  } else {
                    setDialogState(() {
                      isLoading = false;
                      statusMessage = res['message'] ?? 'Doğrulama başarısız.';
                      isError = true;
                    });
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green.shade700,
                  foregroundColor: Colors.white,
                ),
                child: isLoading
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Doğrula'),
              ),
          ],
        ),
      ),
    );
  }

  void _startFullMockExam() async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resmi muafiyet deneme sınavı hazırlanıyor...'),
        duration: Duration(seconds: 1),
      ),
    );
    final mockData = await ApiService().getMockExam(widget.currentUniversity.id);
    if (!mounted) return;
    final List<Question> questions = (mockData['parsed_questions'] as List<dynamic>?)?.cast<Question>() ?? [];
    if (questions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Soru havuzu yüklenemedi.')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExamRunnerScreen(
          questions: questions,
          university: widget.currentUniversity,
          level: widget.currentLevel,
        ),
      ),
    ).then((_) => _loadData());
  }

  void _showReportSummaryDialog() async {
    final report = await ApiService().getReportSummary();
    if (!mounted) return;

    final studentNo = report['student_profile']?['student_number'] ?? '040220199';
    final avgScore = report['average_score'] ?? 0;
    final passingScore = report['passing_score'] ?? 60;
    final totalExams = report['total_exams_taken'] ?? 0;
    final readiness = report['readiness_status'] ?? 'Geliştirilmeli';
    final isReady = (report['readiness_color'] == 'emerald');
    final vocabLearned = report['mastered_vocabulary_count'] ?? 0;
    final vocabTotal = report['total_vocabulary_count'] ?? 64;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.brandLightBlue,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.description, color: AppTheme.brandBlue, size: 20),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Hazırlık Muafiyet Karnesi', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                  Text('${widget.currentUniversity.shortName} • No: $studentNo', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                ],
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isReady ? Colors.green.shade50 : Colors.amber.shade50,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: isReady ? Colors.green.shade200 : Colors.amber.shade200),
              ),
              child: Row(
                children: [
                  Icon(isReady ? Icons.check_circle : Icons.info, color: isReady ? Colors.green.shade700 : Colors.amber.shade800),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      readiness,
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: isReady ? Colors.green.shade900 : Colors.amber.shade900),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: AppTheme.surfaceBg, borderRadius: BorderRadius.circular(14)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Ortalama Not', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                        Text('%$avgScore', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.brandBlue)),
                        Text('Baraj: %$passingScore', style: const TextStyle(fontSize: 9, color: AppTheme.textMuted)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: AppTheme.surfaceBg, borderRadius: BorderRadius.circular(14)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Denemeler', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                        Text('$totalExams', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
                        const Text('Tamamlandı', style: TextStyle(fontSize: 9, color: AppTheme.textMuted)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: AppTheme.surfaceBg, borderRadius: BorderRadius.circular(14)),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Akademik AWL Kelime:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                  Text('$vocabLearned / $vocabTotal', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Colors.indigo)),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Kapat'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('✓ Rapor PDF çıktısı ve karneniz hazırlandı!'), backgroundColor: Colors.green),
              );
            },
            icon: const Icon(Icons.print, size: 16),
            label: const Text('PDF / Yazdır'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.brandBlue,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  void _toggleTheme() async {
    final isDark = themeModeNotifier.value == ThemeMode.dark;
    final newMode = isDark ? ThemeMode.light : ThemeMode.dark;
    themeModeNotifier.value = newMode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme_mode', newMode == ThemeMode.dark ? 'dark' : 'light');
    setState(() {});
  }

  void _openAccountDialog() async {
    final user = await ApiService().loadSavedUser();
    if (!mounted) return;
    final messenger = ScaffoldMessenger.of(context);

    if (user != null && user['id'] != null) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.person, color: AppTheme.brandBlue, size: 22),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Text('Öğrenci Hesabı', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _profileRow('Ad Soyad', user['full_name'] ?? '-'),
              _profileRow('Kullanıcı Adı', user['username'] ?? '-'),
              _profileRow('E-Posta', user['email'] ?? '-'),
              _profileRow('Üniversite', (user['university_id'] ?? '').toString().toUpperCase()),
              _profileRow('Öğrenci No', user['student_number'] ?? '-'),
              const Divider(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Doğrulama:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: user['is_verified_student'] == 1 ? Colors.green.shade50 : Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: user['is_verified_student'] == 1 ? Colors.green : Colors.amber),
                    ),
                    child: Text(
                      user['is_verified_student'] == 1 ? '✓ Doğrulanmış' : 'Doğrulanmadı',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: user['is_verified_student'] == 1 ? Colors.green.shade800 : Colors.amber.shade900,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Kapat'),
            ),
            ElevatedButton.icon(
              onPressed: () async {
                await ApiService().clearSavedUser();
                if (ctx.mounted) Navigator.pop(ctx);
                if (mounted) {
                  setState(() {});
                  messenger.showSnackBar(
                    const SnackBar(content: Text('Oturum kapatıldı.')),
                  );
                }
              },
              icon: const Icon(Icons.logout, size: 16),
              label: const Text('Çıkış Yap'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.accentRose,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      );
    } else {
      final loginIdentCtrl = TextEditingController();
      final loginPassCtrl = TextEditingController();
      final regNameCtrl = TextEditingController();
      final regUserCtrl = TextEditingController();
      final regEmailCtrl = TextEditingController();
      final regPassCtrl = TextEditingController();
      final regNumCtrl = TextEditingController();
      final regUniId = widget.currentUniversity.id;

      showDialog(
        context: context,
        builder: (ctx) => StatefulBuilder(
          builder: (dialogCtx, setDialogState) {
            return DefaultTabController(
              length: 2,
              child: AlertDialog(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                title: Column(
                  children: [
                    const Text('PrepMaster Hesabı', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.grey.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: TabBar(
                        indicator: BoxDecoration(
                          color: AppTheme.brandBlue,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        labelColor: Colors.white,
                        unselectedLabelColor: Colors.grey.shade700,
                        tabs: const [
                          Tab(text: 'Giriş Yap'),
                          Tab(text: 'Kayıt Ol'),
                        ],
                      ),
                    ),
                  ],
                ),
                content: SizedBox(
                  width: double.maxFinite,
                  child: TabBarView(
                    children: [
                      SingleChildScrollView(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const SizedBox(height: 10),
                            TextField(
                              controller: loginIdentCtrl,
                              decoration: InputDecoration(
                                labelText: 'Kullanıcı Adı veya E-Posta',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 10),
                            TextField(
                              controller: loginPassCtrl,
                              obscureText: true,
                              decoration: InputDecoration(
                                labelText: 'Şifre',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 16),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () async {
                                  final ident = loginIdentCtrl.text.trim();
                                  final pass = loginPassCtrl.text.trim();
                                  if (ident.isEmpty || pass.isEmpty) {
                                    messenger.showSnackBar(
                                      const SnackBar(content: Text('Lütfen bilgilerinizi eksiksiz girin.')),
                                    );
                                    return;
                                  }
                                  final res = await ApiService().login(identifier: ident, password: pass);
                                  if (res['success'] == true) {
                                    if (ctx.mounted) Navigator.pop(ctx);
                                    if (mounted) {
                                      setState(() {});
                                      messenger.showSnackBar(
                                        SnackBar(
                                          content: Text('✓ Hoş geldin, ${res['user']['full_name']}!'),
                                          backgroundColor: Colors.green.shade700,
                                        ),
                                      );
                                    }
                                  } else {
                                    messenger.showSnackBar(
                                      SnackBar(
                                        content: Text(res['message'] ?? 'Giriş yapılamadı.'),
                                        backgroundColor: Colors.red.shade700,
                                      ),
                                    );
                                  }
                                },
                                child: const Text('Giriş Yap'),
                              ),
                            ),
                          ],
                        ),
                      ),
                      SingleChildScrollView(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const SizedBox(height: 10),
                            TextField(
                              controller: regNameCtrl,
                              decoration: InputDecoration(
                                labelText: 'Ad Soyad',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 8),
                            TextField(
                              controller: regUserCtrl,
                              decoration: InputDecoration(
                                labelText: 'Kullanıcı Adı',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 8),
                            TextField(
                              controller: regEmailCtrl,
                              decoration: InputDecoration(
                                labelText: 'E-Posta (.edu.tr)',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 8),
                            TextField(
                              controller: regNumCtrl,
                              decoration: InputDecoration(
                                labelText: 'Öğrenci No (İsteğe Bağlı)',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 8),
                            TextField(
                              controller: regPassCtrl,
                              obscureText: true,
                              decoration: InputDecoration(
                                labelText: 'Şifre',
                                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                            const SizedBox(height: 14),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: () async {
                                  final name = regNameCtrl.text.trim();
                                  final user = regUserCtrl.text.trim();
                                  final email = regEmailCtrl.text.trim();
                                  final pass = regPassCtrl.text.trim();
                                  final num = regNumCtrl.text.trim();

                                  if (name.isEmpty || user.isEmpty || email.isEmpty || pass.isEmpty) {
                                    messenger.showSnackBar(
                                      const SnackBar(content: Text('Lütfen zorunlu alanları doldurun.')),
                                    );
                                    return;
                                  }

                                  final res = await ApiService().register(
                                    email: email,
                                    username: user,
                                    password: pass,
                                    fullName: name,
                                    universityId: regUniId,
                                    studentNumber: num,
                                  );

                                  if (res['success'] == true) {
                                    if (ctx.mounted) Navigator.pop(ctx);
                                    if (mounted) {
                                      setState(() {});
                                      messenger.showSnackBar(
                                        SnackBar(
                                          content: Text('✓ Hesabınız oluşturuldu. Hoş geldin, ${res['user']['full_name']}!'),
                                          backgroundColor: Colors.green.shade700,
                                        ),
                                      );
                                    }
                                  } else {
                                    messenger.showSnackBar(
                                      SnackBar(
                                        content: Text(res['message'] ?? 'Kayıt yapılamadı.'),
                                        backgroundColor: Colors.red.shade700,
                                      ),
                                    );
                                  }
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.accentEmerald,
                                ),
                                child: const Text('Hesap Oluştur'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('İptal'),
                  ),
                ],
              ),
            );
          },
        ),
      );
    }
  }

  Widget _profileRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final uni = widget.currentUniversity;
    final streak = _stats?['profile']?['streak_days'] ?? 1;
    final totalExams = _stats?['total_exams_taken'] ?? 0;
    final avgScore = _stats?['average_exam_score'] ?? 0;
    final masteredVocab = _stats?['mastered_vocab'] ?? 0;
    final totalVocab = _stats?['total_vocab'] ?? 0;
    final mistakeCount = _stats?['unresolved_mistakes'] ?? 0;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [AppTheme.brandBlue, AppTheme.brandNavy]),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.school, size: 18, color: Colors.white),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text('PrepMaster', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                      decoration: BoxDecoration(
                        color: AppTheme.brandLightBlue,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text('HAZIRLIK', style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: AppTheme.brandBlue)),
                    ),
                  ],
                ),
                InkWell(
                  onTap: _openUniPicker,
                  child: Row(
                    children: [
                      Text(uni.shortName, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
                      const Text(' (Değiştir)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue)),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              themeModeNotifier.value == ThemeMode.dark ? Icons.light_mode : Icons.dark_mode,
              color: themeModeNotifier.value == ThemeMode.dark ? Colors.amber : AppTheme.brandNavy,
            ),
            onPressed: _toggleTheme,
            tooltip: 'Karanlık / Aydınlık Mod',
          ),
          IconButton(
            icon: const Icon(Icons.account_circle_outlined, color: AppTheme.brandBlue),
            onPressed: _openAccountDialog,
            tooltip: 'Öğrenci Hesabı',
          ),
          IconButton(
            icon: const Icon(Icons.assessment_outlined, color: AppTheme.brandBlue),
            onPressed: _showReportSummaryDialog,
            tooltip: 'Muafiyet Karnesi (PDF)',
          ),
          IconButton(
            icon: const Icon(Icons.verified_user_outlined, color: Colors.green),
            onPressed: _openVerificationDialog,
            tooltip: 'Öğrenci Doğrulama',
          ),
          IconButton(
            icon: const Icon(Icons.cloud_sync_outlined, color: AppTheme.brandBlue),
            onPressed: _performCloudSync,
            tooltip: 'Bulut Eşitle',
          ),
          IconButton(
            icon: const Icon(Icons.account_balance_outlined, color: AppTheme.textMain),
            onPressed: _openUniPicker,
            tooltip: 'Üniversite Değiştir',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Level Selector Bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Çalışma Kuru (CEFR):', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
                  Row(
                    children: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'].map((lvl) {
                      final isSel = widget.currentLevel == lvl;
                      return Padding(
                        padding: const EdgeInsets.only(left: 4),
                        child: InkWell(
                          onTap: () => widget.onLevelChange(lvl),
                          borderRadius: BorderRadius.circular(10),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                            decoration: BoxDecoration(
                              color: isSel ? AppTheme.brandBlue : Colors.white,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: isSel ? AppTheme.brandBlue : AppTheme.borderSubtle),
                            ),
                            child: Text(
                              lvl,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                color: isSel ? Colors.white : AppTheme.textMain,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Hero Card
              Container(
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E3A8A), Color(0xFF1E1B4B)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.brandNavy.withValues(alpha: 0.3),
                      blurRadius: 16,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white24,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '${uni.shortName} Hazırlık',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.white),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.3),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
                          ),
                          child: Text(
                            '%${uni.passingScore} Baraj Puanı',
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Colors.greenAccent),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    Text(
                      uni.examName,
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      uni.description,
                      style: const TextStyle(fontSize: 12, color: Colors.white70, height: 1.4),
                    ),
                    const SizedBox(height: 18),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _startFullMockExam,
                            icon: const Icon(Icons.play_arrow_rounded, size: 18),
                            label: const Text('Resmi Deneme Başlat'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.white,
                              foregroundColor: AppTheme.brandNavy,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton.icon(
                          onPressed: _showReportSummaryDialog,
                          icon: const Icon(Icons.description_outlined, size: 16),
                          label: const Text('Karne (PDF)', style: TextStyle(fontWeight: FontWeight.w700)),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.white,
                            side: const BorderSide(color: Colors.white38),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Stat Cards
              SizedBox(
                height: 100,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: [
                    _statCard(
                      icon: Icons.local_fire_department,
                      iconColor: AppTheme.accentAmber,
                      title: 'Seri',
                      value: '$streak Gün',
                      subtitle: 'Her gün pratik',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.assignment_turned_in,
                      iconColor: AppTheme.brandBlue,
                      title: 'Denemeler',
                      value: '$totalExams',
                      subtitle: 'Tamamlanan',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.trending_up,
                      iconColor: AppTheme.accentEmerald,
                      title: 'Ortalama',
                      value: '%$avgScore',
                      subtitle: 'Başarı notu',
                    ),
                    const SizedBox(width: 10),
                    _statCard(
                      icon: Icons.menu_book,
                      iconColor: Colors.indigo,
                      title: 'Kelimeler',
                      value: '$masteredVocab/$totalVocab',
                      subtitle: 'Öğrenilen',
                    ),
                    const SizedBox(width: 10),
                    InkWell(
                      onTap: () => widget.onTabSwitch(2), // Mistakes tab
                      borderRadius: BorderRadius.circular(20),
                      child: _statCard(
                        icon: Icons.shield_outlined,
                        iconColor: AppTheme.accentRose,
                        title: 'Hata Defterim',
                        value: '$mistakeCount',
                        subtitle: 'Yanlışları Çöz →',
                        borderColor: Colors.red.shade200,
                        isHighlighted: true,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Exam Sections Distribution
              const Text(
                'Sınav Formatı & Soru Dağılımı',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textMain),
              ),
              const SizedBox(height: 10),

              ...uni.sections.map((sec) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: AppTheme.borderSubtle),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(sec.name, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.textMain)),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: AppTheme.brandLightBlue,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                'Ağırlık: %${sec.weightPercent}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(sec.description, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.4)),
                      ],
                    ),
                  ),
                );
              }),
              const SizedBox(height: 18),
              const Text(
                'Akademik Atölyeler & Pratik',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
              ),
              const SizedBox(height: 10),

              Row(
                children: [
                  Expanded(
                    child: InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => ListeningScreen(currentLevel: widget.currentLevel)),
                        );
                      },
                      borderRadius: BorderRadius.circular(18),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppTheme.borderSubtle),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.headphones, size: 20, color: AppTheme.brandBlue),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'Sesli Dinleme',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Note-Taking Simülatörü',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: InkWell(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const WritingScreen()),
                        );
                      },
                      borderRadius: BorderRadius.circular(18),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: AppTheme.borderSubtle),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withValues(alpha: 0.02),
                              blurRadius: 8,
                              offset: const Offset(0, 3),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.indigo.shade50,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(Icons.auto_awesome, size: 20, color: Colors.indigo),
                            ),
                            const SizedBox(height: 10),
                            const Text(
                              'AI Essay Puanlama',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                            ),
                            const SizedBox(height: 2),
                            const Text(
                              'Writing Rehberi & Not',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => SpeakingScreen(currentLevel: widget.currentLevel)),
                  );
                },
                borderRadius: BorderRadius.circular(18),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: const Color(0xFFE0E7FF)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.02),
                        blurRadius: 8,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEEF2FF),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.mic, size: 22, color: Color(0xFF4F46E5)),
                      ),
                      const SizedBox(width: 14),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Speaking & Sözlü Mülakat Simülatörü',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: AppTheme.brandNavy),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Boğaziçi, ODTÜ ve Bilkent mülakatları için canlı süre & yapay zeka analizi',
                              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: Colors.grey),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _statCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
    required String subtitle,
    Color? borderColor,
    bool isHighlighted = false,
  }) {
    return Container(
      width: 125,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isHighlighted ? Colors.red.shade50.withValues(alpha: 0.4) : Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: borderColor ?? AppTheme.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted)),
              Icon(icon, size: 16, color: iconColor),
            ],
          ),
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppTheme.textMain)),
          Text(subtitle, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: iconColor)),
        ],
      ),
    );
  }
}
