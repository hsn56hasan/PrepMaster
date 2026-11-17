import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/sync_service.dart';
import 'student_document_scan_sheet.dart';
import 'web_page_screen.dart';

/// Kilitli üniversite ekranı: sitedeki gibi PayTR ile tek seferlik paket satın alma,
/// öğrenci belgesiyle ücretsiz açma ya da başka yerden (web) alınmış paketi "Yenile" ile eşitleme.
///
/// Not: Uygulama sitemizden APK olarak dağıtılıyor. İleride Google Play'e konursa, Play dijital
/// içerik satışında Play Billing dışındaki ödemeyi yasakladığı için bu ödeme bölümü kaldırılmalıdır.
class LockedUniversitySheet extends StatefulWidget {
  final String universityId;
  final String universityName;
  final VoidCallback? onUnlockSuccess;

  /// Testler için sunucu ayarları (verilmezse /api/config'ten okunur).
  @visibleForTesting
  final Map<String, dynamic>? config;

  const LockedUniversitySheet({
    super.key,
    required this.universityId,
    required this.universityName,
    this.onUnlockSuccess,
    this.config,
  });

  @override
  State<LockedUniversitySheet> createState() => _LockedUniversitySheetState();
}

class _LockedUniversitySheetState extends State<LockedUniversitySheet> {
  final _phone = TextEditingController();
  bool _busy = false;
  bool _preInfoAccepted = false;
  bool _configLoaded = false;
  bool _paymentAvailable = false;
  double _price = 50;
  String? _message;
  bool _messageIsError = true;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  @override
  void dispose() {
    _phone.dispose();
    super.dispose();
  }

  Future<void> _loadConfig() async {
    final cfg = widget.config ?? await ApiService().getPublicConfig();
    if (!mounted) return;
    setState(() {
      _paymentAvailable = cfg['paytr_configured'] == true;
      _price = (cfg['membership_price_try'] as num?)?.toDouble() ?? 50;
      _configLoaded = true;
    });
  }

  String get _priceText => _price == _price.roundToDouble()
      ? '${_price.toInt()} TL'
      : '${_price.toStringAsFixed(2)} TL';

  void _show(String msg, {bool error = true}) => setState(() {
    _message = msg;
    _messageIsError = error;
  });

  void _unlocked() {
    widget.onUnlockSuccess?.call();
    if (mounted) Navigator.of(context).pop(true);
  }

  Future<void> _refresh() async {
    setState(() {
      _busy = true;
      _message = null;
    });
    final synced = await SyncService().syncNow();
    final unlocked = await ApiService().checkUniversityAccess(
      universityId: widget.universityId,
    );
    if (!mounted) return;
    setState(() => _busy = false);
    if (unlocked) return _unlocked();
    _show(
      synced == null
          ? 'Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edip tekrar deneyin.'
          : 'Bu paket hesabınızda henüz açık değil.',
    );
  }

  Future<void> _pay() async {
    final phone = _phone.text.replaceAll(RegExp(r'\D'), '');
    if (phone.length < 10) {
      return _show(
        'Geçerli bir cep telefonu girin (örn. 0532 123 45 67). PayTR ödeme için istiyor.',
      );
    }
    if (!_preInfoAccepted) {
      return _show(
        'Ödemeden önce Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi\'ni onaylayın.',
      );
    }
    setState(() {
      _busy = true;
      _message = null;
    });
    final start = await ApiService().startPaytrPayment(
      universityId: widget.universityId,
      phone: phone,
    );
    if (!mounted) return;
    if (start['success'] != true) {
      setState(() => _busy = false);
      return _show(start['message']?.toString() ?? 'Ödeme başlatılamadı.');
    }
    final oid = start['merchant_oid'].toString();
    await WebPageScreen.open(
      context,
      title: 'Güvenli Ödeme (PayTR)',
      url: start['iframe_url'].toString(),
      stopWhenUrlContains: '/odeme-sonuc',
    );
    if (!mounted) return;
    _show('Ödeme sonucu kontrol ediliyor...', error: false);

    // Kilit, PayTR'nin sunucumuza gönderdiği imzalı bildirimle açılır; birkaç saniye sürebilir.
    String? status;
    for (var i = 0; i < 10; i++) {
      status = await ApiService().getPaytrOrderStatus(oid);
      if (status != null && status != 'pending') break;
      await Future.delayed(const Duration(seconds: 2));
      if (!mounted) return;
    }
    if (!mounted) return;
    setState(() => _busy = false);
    if (status == 'success') {
      await SyncService().syncNow();
      if (!mounted) return;
      ScaffoldMessenger.maybeOf(context)?.showSnackBar(
        SnackBar(
          content: Text('✓ ${widget.universityName} paketi açıldı.'),
          backgroundColor: Colors.green.shade700,
        ),
      );
      return _unlocked();
    }
    if (status == 'failed' || status == 'amount_mismatch') {
      return _show(
        'Ödeme tamamlanmadı; kartınızdan çekim yapılmadıysa tekrar deneyebilirsiniz.',
      );
    }
    _show(
      'Ödeme onayı henüz gelmedi. Ödemeyi tamamladıysanız birkaç dakika sonra "Yenile"ye basın.',
    );
  }

  void _openStudentScan() {
    Navigator.of(context).pop();
    StudentDocumentScanSheet.show(
      context,
      onScanComplete: (_) => widget.onUnlockSuccess?.call(),
    );
  }

  void _openLegal(String anchor, String title) {
    WebPageScreen.open(
      context,
      title: title,
      url: '${ApiService().baseUrl}/kvkk#$anchor',
    );
  }

  Widget _paymentSection(ThemeData theme) {
    if (!_configLoaded) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 12),
        child: Center(
          child: SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      );
    }
    if (!_paymentAvailable) {
      return Text(
        'Uygulama içi ödeme şu an kapalı. Paket hesabınıza tanımlandığında "Yenile"ye basın.',
        key: const Key('locked_payment_unavailable'),
        style: TextStyle(color: Colors.grey.shade700),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _priceText,
                key: const Key('locked_price'),
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w900,
                  color: Colors.blue.shade900,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Tek seferlik ödeme • Bu üniversitenin tüm kur sınavları, dinleme ve konuşma denemeleri • Web ve mobilde aynı hesap',
                style: TextStyle(fontSize: 12),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          key: const Key('locked_phone'),
          controller: _phone,
          keyboardType: TextInputType.phone,
          decoration: InputDecoration(
            labelText: 'Cep telefonu (PayTR için)',
            hintText: '0532 123 45 67',
            prefixIcon: const Icon(Icons.phone_outlined, size: 20),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
        CheckboxListTile(
          key: const Key('locked_pre_info'),
          value: _preInfoAccepted,
          onChanged: (v) => setState(() => _preInfoAccepted = v ?? false),
          controlAffinity: ListTileControlAffinity.leading,
          contentPadding: EdgeInsets.zero,
          dense: true,
          title: const Text(
            'Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi\'ni okudum, onaylıyorum. Dijital içerik '
            'anında sunulduğu için cayma hakkının bulunmadığını kabul ediyorum.',
            style: TextStyle(fontSize: 12),
          ),
        ),
        Wrap(
          spacing: 4,
          children: [
            TextButton(
              onPressed: () =>
                  _openLegal('on-bilgilendirme', 'Ön Bilgilendirme Formu'),
              child: const Text('Ön bilgilendirme'),
            ),
            TextButton(
              onPressed: () =>
                  _openLegal('mesafeli-satis', 'Mesafeli Satış Sözleşmesi'),
              child: const Text('Mesafeli satış'),
            ),
            TextButton(
              onPressed: () => _openLegal('iade-cayma', 'İade ve Cayma'),
              child: const Text('İade/cayma'),
            ),
          ],
        ),
        ElevatedButton.icon(
          key: const Key('btn_locked_pay'),
          onPressed: _busy ? null : _pay,
          style: ElevatedButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
          ),
          icon: _busy
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.lock_open_rounded),
          label: Text('$_priceText öde ve paketi aç'),
        ),
        const SizedBox(height: 4),
        Text(
          'Kart bilgileriniz PayTR\'nin güvenli sayfasında girilir; PrepMaster kart bilgisi görmez.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      // Onay kutusu (ListTile) kendi zeminini çizebilsin diye şeffaf Material
      child: Material(
        type: MaterialType.transparency,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Icon(Icons.lock_outline, color: Colors.amber.shade700),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      widget.universityName,
                      key: const Key('locked_title'),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close),
                    tooltip: 'Kapat',
                  ),
                ],
              ),
              const SizedBox(height: 6),
              const Text(
                'Bu üniversitenin deneme paketi hesabınızda açık değil.',
                key: Key('locked_message'),
              ),
              const SizedBox(height: 14),
              _paymentSection(theme),
              const SizedBox(height: 12),
              const Divider(),
              OutlinedButton.icon(
                key: const Key('btn_locked_student_scan'),
                onPressed: _busy ? null : _openStudentScan,
                icon: const Icon(Icons.badge_outlined),
                label: const Text(
                  'Bu okulun öğrencisiyim: belgemi doğrula (ücretsiz)',
                ),
              ),
              const SizedBox(height: 8),
              TextButton.icon(
                key: const Key('btn_locked_refresh'),
                onPressed: _busy ? null : _refresh,
                icon: const Icon(Icons.refresh),
                label: const Text('Web\'den aldım / Yenile'),
              ),
              if (_message != null) ...[
                const SizedBox(height: 8),
                Text(
                  _message!,
                  key: const Key('locked_status'),
                  style: TextStyle(
                    color: _messageIsError
                        ? Colors.red.shade700
                        : Colors.blueGrey.shade700,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
