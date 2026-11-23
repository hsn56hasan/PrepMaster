import 'package:flutter/material.dart';

import '../models/university.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import 'forgot_password_dialog.dart';
import 'web_page_screen.dart';

/// Uygulamanın giriş kapısı: oturum açmadan içerik görülmez (web sitesiyle aynı hesap).
class AuthScreen extends StatefulWidget {
  final VoidCallback onAuthenticated;

  const AuthScreen({super.key, required this.onAuthenticated});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _loginIdent = TextEditingController();
  final _loginPass = TextEditingController();
  final _regName = TextEditingController();
  final _regUser = TextEditingController();
  final _regEmail = TextEditingController();
  final _regPass = TextEditingController();

  bool _busy = false;
  bool _termsAccepted = false;
  bool _explicitConsent = false;
  String? _error;
  List<University> _universities = [];
  String _regUniId = 'itu';

  @override
  void initState() {
    super.initState();
    ApiService().getUniversities().then((list) {
      if (!mounted) return;
      setState(() {
        _universities = list.where((u) => u.id != 'general').toList();
        if (_universities.isNotEmpty && !_universities.any((u) => u.id == _regUniId)) {
          _regUniId = _universities.first.id;
        }
      });
    });
  }

  @override
  void dispose() {
    for (final c in [_loginIdent, _loginPass, _regName, _regUser, _regEmail, _regPass]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _login() async {
    final ident = _loginIdent.text.trim();
    final pass = _loginPass.text;
    if (ident.isEmpty || pass.isEmpty) {
      setState(() => _error = 'Kullanıcı adı/e-posta ve şifrenizi girin.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final res = await ApiService().login(identifier: ident, password: pass);
    if (!mounted) return;
    setState(() => _busy = false);
    if (res['success'] == true) {
      widget.onAuthenticated();
    } else {
      setState(() => _error = res['message']?.toString() ?? 'Giriş yapılamadı.');
    }
  }

  Future<void> _register() async {
    final name = _regName.text.trim();
    final user = _regUser.text.trim();
    final email = _regEmail.text.trim();
    final pass = _regPass.text;
    if (name.isEmpty || user.isEmpty || email.isEmpty || pass.isEmpty) {
      setState(() => _error = 'Lütfen tüm alanları doldurun.');
      return;
    }
    if (!_termsAccepted) {
      setState(() => _error = "Kayıt için Kullanıcı Sözleşmesi'ni kabul etmelisiniz.");
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final res = await ApiService().register(
      email: email,
      username: user,
      password: pass,
      fullName: name,
      universityId: _regUniId,
      termsAccepted: _termsAccepted,
      explicitConsent: _explicitConsent,
    );
    if (!mounted) return;
    setState(() => _busy = false);
    if (res['success'] == true) {
      widget.onAuthenticated();
    } else {
      setState(() => _error = res['message']?.toString() ?? 'Kayıt yapılamadı.');
    }
  }

  void _openLegal(String anchor, String title) {
    WebPageScreen.open(context, title: title, url: '${ApiService().baseUrl}/kvkk#$anchor');
  }

  InputDecoration _dec(String label, IconData icon) => InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, size: 20),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      );

  Widget _loginTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        TextField(
          key: const Key('auth_login_ident'),
          controller: _loginIdent,
          keyboardType: TextInputType.emailAddress,
          decoration: _dec('Kullanıcı adı veya e-posta', Icons.person_outline),
        ),
        const SizedBox(height: 12),
        TextField(
          key: const Key('auth_login_pass'),
          controller: _loginPass,
          obscureText: true,
          decoration: _dec('Şifre', Icons.lock_outline),
          onSubmitted: (_) => _login(),
        ),
        FutureBuilder<bool>(
          future: ApiService().isPasswordResetAvailable(),
          builder: (context, snap) => snap.data == true
              ? Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    key: const Key('btn_forgot_password'),
                    onPressed: () => ForgotPasswordDialog.show(context, initialEmail: _loginIdent.text.trim()),
                    child: const Text('Şifremi unuttum?'),
                  ),
                )
              : const SizedBox(height: 16),
        ),
        ElevatedButton(
          key: const Key('auth_login_submit'),
          onPressed: _busy ? null : _login,
          style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(48)),
          child: _busy
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Giriş Yap'),
        ),
        const SizedBox(height: 12),
        Text(
          'Web sitesindeki hesabınızla giriş yapabilirsiniz; ilerlemeniz iki tarafta da aynıdır.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
        ),
      ],
    );
  }

  Widget _registerTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        TextField(key: const Key('auth_reg_name'), controller: _regName, decoration: _dec('Ad Soyad', Icons.badge_outlined)),
        const SizedBox(height: 10),
        TextField(key: const Key('auth_reg_user'), controller: _regUser, decoration: _dec('Kullanıcı adı', Icons.alternate_email)),
        const SizedBox(height: 10),
        TextField(
          key: const Key('auth_reg_email'),
          controller: _regEmail,
          keyboardType: TextInputType.emailAddress,
          decoration: _dec('E-posta', Icons.mail_outline),
        ),
        const SizedBox(height: 10),
        TextField(
          key: const Key('auth_reg_pass'),
          controller: _regPass,
          obscureText: true,
          decoration: _dec('Şifre', Icons.lock_outline),
        ),
        const SizedBox(height: 10),
        if (_universities.isNotEmpty)
          DropdownButtonFormField<String>(
            initialValue: _regUniId,
            isExpanded: true,
            decoration: _dec('Hedef üniversite', Icons.school_outlined),
            items: _universities
                .map((u) => DropdownMenuItem(value: u.id, child: Text(u.name, overflow: TextOverflow.ellipsis)))
                .toList(),
            onChanged: (v) => setState(() => _regUniId = v ?? _regUniId),
          ),
        const SizedBox(height: 6),
        CheckboxListTile(
          key: const Key('reg_terms'),
          value: _termsAccepted,
          onChanged: (v) => setState(() => _termsAccepted = v ?? false),
          controlAffinity: ListTileControlAffinity.leading,
          contentPadding: EdgeInsets.zero,
          dense: true,
          title: const Text(
            "Kullanıcı Sözleşmesi'ni kabul ediyorum ve KVKK Aydınlatma Metni'ni okudum (zorunlu).",
            style: TextStyle(fontSize: 12),
          ),
        ),
        CheckboxListTile(
          key: const Key('reg_explicit'),
          value: _explicitConsent,
          onChanged: (v) => setState(() => _explicitConsent = v ?? false),
          controlAffinity: ListTileControlAffinity.leading,
          contentPadding: EdgeInsets.zero,
          dense: true,
          title: const Text("Açık Rıza Beyanı'nı kabul ediyorum (isteğe bağlı).", style: TextStyle(fontSize: 12)),
        ),
        Wrap(
          spacing: 4,
          children: [
            TextButton(onPressed: () => _openLegal('kullanici-sozlesmesi', 'Kullanıcı Sözleşmesi'), child: const Text('Sözleşmeyi oku')),
            TextButton(onPressed: () => _openLegal('kvkk-aydinlatma', 'KVKK Aydınlatma Metni'), child: const Text('KVKK metnini oku')),
          ],
        ),
        const SizedBox(height: 6),
        ElevatedButton(
          key: const Key('auth_reg_submit'),
          onPressed: _busy ? null : _register,
          style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(48)),
          child: _busy
              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Kayıt Ol'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        body: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 28),
              const Icon(Icons.school_rounded, size: 48, color: AppTheme.brandBlue),
              const SizedBox(height: 8),
              const Text('PrepKampüs', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
              const SizedBox(height: 4),
              Text(
                'Devam etmek için giriş yapın veya hesap oluşturun',
                style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 16),
              const TabBar(tabs: [Tab(text: 'Giriş Yap'), Tab(text: 'Kayıt Ol')]),
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
                  child: Text(
                    _error!,
                    key: const Key('auth_error'),
                    style: TextStyle(color: Colors.red.shade700, fontWeight: FontWeight.w600),
                  ),
                ),
              Expanded(child: TabBarView(children: [_loginTab(), _registerTab()])),
            ],
          ),
        ),
      ),
    );
  }
}
