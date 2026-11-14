import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/sync_service.dart';
import 'student_document_scan_sheet.dart';

/// Kilitli üniversite ekranı (canlı sürüm).
///
/// Mobil uygulama içinde ödeme ALINMAZ: Google Play, dijital içerik satışında Play Billing
/// dışındaki ödeme yollarına yönlendirmeyi (bağlantı, fiyat, "web'den al" çağrısı) yasaklıyor.
/// Paket hesaba başka bir yoldan tanımlandığında (ör. web'den satın alma, öğrenci belgesi)
/// "Yenile" ile eşitlenir ve burada açılır.
class LockedUniversitySheet extends StatefulWidget {
  final String universityId;
  final String universityName;
  final VoidCallback? onUnlockSuccess;

  const LockedUniversitySheet({
    super.key,
    required this.universityId,
    required this.universityName,
    this.onUnlockSuccess,
  });

  @override
  State<LockedUniversitySheet> createState() => _LockedUniversitySheetState();
}

class _LockedUniversitySheetState extends State<LockedUniversitySheet> {
  bool _busy = false;
  String? _message;

  Future<void> _refresh() async {
    setState(() {
      _busy = true;
      _message = null;
    });
    final synced = await SyncService().syncNow();
    final unlocked = await ApiService().checkUniversityAccess(universityId: widget.universityId);
    if (!mounted) return;
    setState(() => _busy = false);
    if (unlocked) {
      widget.onUnlockSuccess?.call();
      Navigator.of(context).pop(true);
      return;
    }
    setState(() {
      _message = synced == null
          ? 'Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edip tekrar deneyin.'
          : 'Bu paket hesabınızda henüz açık değil.';
    });
  }

  void _openStudentScan() {
    Navigator.of(context).pop();
    StudentDocumentScanSheet.show(
      context,
      onScanComplete: (_) => widget.onUnlockSuccess?.call(),
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
                  style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                ),
              ),
              IconButton(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.close),
                tooltip: 'Kapat',
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Bu üniversitenin deneme paketi hesabınızda açık değil. '
            'Paket hesabınıza tanımlandığında "Yenile"ye basın; burada otomatik açılır.',
            key: Key('locked_message'),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            key: const Key('btn_locked_refresh'),
            onPressed: _busy ? null : _refresh,
            icon: _busy
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.refresh),
            label: const Text('Yenile'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            key: const Key('btn_locked_student_scan'),
            onPressed: _busy ? null : _openStudentScan,
            icon: const Icon(Icons.badge_outlined),
            label: const Text('Bu okulun öğrencisiyim: belgemi doğrula'),
          ),
          if (_message != null) ...[
            const SizedBox(height: 12),
            Text(
              _message!,
              key: const Key('locked_status'),
              style: TextStyle(color: Colors.red.shade700),
            ),
          ],
        ],
      ),
    );
  }
}
