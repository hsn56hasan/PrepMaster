import 'package:flutter/material.dart';

import '../services/api_service.dart';

/// "Şifremi unuttum" penceresi: önce e-posta, sonra e-postayla gelen 6 haneli kod + yeni şifre.
/// Sunucu, adres kayıtlı olsun olmasın aynı yanıtı verir; kod asla yanıtta dönmez.
class ForgotPasswordDialog extends StatefulWidget {
  final String initialEmail;
  const ForgotPasswordDialog({super.key, this.initialEmail = ''});

  static Future<void> show(BuildContext context, {String initialEmail = ''}) {
    return showDialog(
      context: context,
      builder: (_) => ForgotPasswordDialog(initialEmail: initialEmail),
    );
  }

  @override
  State<ForgotPasswordDialog> createState() => _ForgotPasswordDialogState();
}

class _ForgotPasswordDialogState extends State<ForgotPasswordDialog> {
  late final TextEditingController _emailCtrl;
  final _codeCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _pass2Ctrl = TextEditingController();
  bool _codeStep = false;
  bool _busy = false;
  String? _message;
  bool _messageOk = false;

  @override
  void initState() {
    super.initState();
    _emailCtrl = TextEditingController(text: widget.initialEmail.contains('@') ? widget.initialEmail : '');
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _codeCtrl.dispose();
    _passCtrl.dispose();
    _pass2Ctrl.dispose();
    super.dispose();
  }

  void _show(String msg, {bool ok = false}) => setState(() {
        _message = msg;
        _messageOk = ok;
      });

  Future<void> _sendCode() async {
    final email = _emailCtrl.text.trim();
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(email)) {
      _show('Lütfen geçerli bir e-posta adresi girin.');
      return;
    }
    setState(() => _busy = true);
    final res = await ApiService().requestPasswordReset(email);
    if (!mounted) return;
    setState(() {
      _busy = false;
      if (res['success'] == true) {
        _codeStep = true;
        _message = res['message']?.toString();
        _messageOk = true;
      } else {
        _message = res['message']?.toString() ?? 'Kod gönderilemedi.';
        _messageOk = false;
      }
    });
  }

  Future<void> _reset() async {
    final code = _codeCtrl.text.replaceAll(RegExp(r'\D'), '');
    if (code.length != 6) return _show('Kod 6 haneli olmalı.');
    if (_passCtrl.text.length < 6) return _show('Yeni şifre en az 6 karakter olmalı.');
    if (_passCtrl.text != _pass2Ctrl.text) return _show('Şifreler aynı değil.');
    setState(() => _busy = true);
    final res = await ApiService().confirmPasswordReset(
      email: _emailCtrl.text.trim(),
      code: code,
      newPassword: _passCtrl.text,
    );
    if (!mounted) return;
    setState(() => _busy = false);
    if (res['success'] == true) {
      _show('✓ Şifreniz değişti. Yeni şifrenizle giriş yapabilirsiniz.', ok: true);
      await Future.delayed(const Duration(milliseconds: 1400));
      if (mounted) Navigator.of(context).pop();
    } else {
      _show(res['message']?.toString() ?? 'Şifre değiştirilemedi.');
    }
  }

  InputDecoration _dec(String label) => InputDecoration(
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      );

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Şifremi Unuttum'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (!_codeStep) ...[
              const Text('Hesabınızın e-posta adresini girin. Kayıtlı bir hesap varsa 6 haneli bir kod göndereceğiz.'),
              const SizedBox(height: 12),
              TextField(
                key: const Key('forgot_email'),
                controller: _emailCtrl,
                keyboardType: TextInputType.emailAddress,
                decoration: _dec('E-posta'),
              ),
            ] else ...[
              TextField(
                key: const Key('forgot_code'),
                controller: _codeCtrl,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: _dec('6 haneli kod'),
              ),
              TextField(
                key: const Key('forgot_new_password'),
                controller: _passCtrl,
                obscureText: true,
                decoration: _dec('Yeni şifre (en az 6 karakter)'),
              ),
              const SizedBox(height: 10),
              TextField(
                key: const Key('forgot_new_password2'),
                controller: _pass2Ctrl,
                obscureText: true,
                decoration: _dec('Yeni şifre (tekrar)'),
              ),
              TextButton(
                onPressed: _busy ? null : () => setState(() => _codeStep = false),
                child: const Text('Kod gelmedi mi? Tekrar gönder'),
              ),
            ],
            if (_message != null) ...[
              const SizedBox(height: 8),
              Text(
                _message!,
                key: const Key('forgot_message'),
                style: TextStyle(color: _messageOk ? Colors.green.shade700 : Colors.red.shade700, fontSize: 13),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Kapat')),
        ElevatedButton(
          key: const Key('forgot_submit'),
          onPressed: _busy ? null : (_codeStep ? _reset : _sendCode),
          child: Text(_codeStep ? 'Şifreyi Değiştir' : 'Kod Gönder'),
        ),
      ],
    );
  }
}
