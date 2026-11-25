import 'package:flutter/material.dart';

import '../models/lesson_path.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/panel_widgets.dart';
import '../widgets/press3d.dart';
import 'lesson_screen.dart';

typedef PathLoader = Future<PathResponse> Function({String? level});

/// Konu Yolu: seviyeye göre sırayla açılan gündelik hayat dersleri (web ile aynı API ve ilerleme).
class PathScreen extends StatefulWidget {
  /// Testler sunucu yerine bunu verir.
  final PathLoader? loader;
  const PathScreen({super.key, this.loader});

  @override
  State<PathScreen> createState() => _PathScreenState();
}

const _nodeOffsets = [0.0, 36.0, 60.0, 36.0, 0.0, -36.0, -60.0, -36.0];

const _iconMap = <String, IconData>{
  'hand': Icons.waving_hand_rounded, 'user': Icons.person_rounded, 'users': Icons.groups_rounded,
  'hash': Icons.tag_rounded, 'palette': Icons.palette_rounded, 'shirt': Icons.checkroom_rounded,
  'utensils': Icons.restaurant_rounded, 'coffee': Icons.local_cafe_rounded, 'home': Icons.home_rounded,
  'sun': Icons.wb_sunny_rounded, 'cloud-sun': Icons.wb_cloudy_rounded, 'clock': Icons.schedule_rounded,
  'calendar': Icons.calendar_month_rounded, 'school': Icons.school_rounded, 'map-pin': Icons.place_rounded,
  'map': Icons.map_rounded, 'shopping-cart': Icons.shopping_cart_rounded, 'shopping-bag': Icons.shopping_bag_rounded,
  'heart-pulse': Icons.monitor_heart_rounded, 'pill': Icons.medication_rounded,
  'stethoscope': Icons.medical_services_rounded, 'music': Icons.music_note_rounded, 'dog': Icons.pets_rounded,
  'bus': Icons.directions_bus_rounded, 'train': Icons.train_rounded, 'plane': Icons.flight_rounded,
  'briefcase': Icons.work_rounded, 'smile': Icons.sentiment_satisfied_rounded,
  'party-popper': Icons.celebration_rounded, 'phone': Icons.call_rounded, 'smartphone': Icons.smartphone_rounded,
  'laptop': Icons.laptop_rounded, 'banknote': Icons.payments_rounded, 'wallet': Icons.account_balance_wallet_rounded,
  'package': Icons.inventory_2_rounded, 'gift': Icons.card_giftcard_rounded, 'dumbbell': Icons.fitness_center_rounded,
  'bed': Icons.hotel_rounded, 'key': Icons.key_rounded, 'building': Icons.apartment_rounded,
  'book-open': Icons.menu_book_rounded, 'library': Icons.local_library_rounded, 'film': Icons.movie_rounded,
  'chef-hat': Icons.soup_kitchen_rounded, 'leaf': Icons.eco_rounded, 'recycle': Icons.recycling_rounded,
  'globe': Icons.public_rounded, 'newspaper': Icons.newspaper_rounded, 'message-circle': Icons.chat_bubble_rounded,
  'mail': Icons.mail_rounded, 'scale': Icons.balance_rounded, 'gavel': Icons.gavel_rounded,
  'handshake': Icons.handshake_rounded, 'lightbulb': Icons.lightbulb_rounded, 'brain': Icons.psychology_rounded,
  'mic': Icons.mic_rounded, 'presentation': Icons.co_present_rounded, 'trending-up': Icons.trending_up_rounded,
  'landmark': Icons.account_balance_rounded, 'shield': Icons.shield_rounded, 'sparkles': Icons.auto_awesome_rounded,
  'feather': Icons.edit_note_rounded, 'pen-line': Icons.edit_rounded, 'compass': Icons.explore_rounded,
  'target': Icons.track_changes_rounded, 'megaphone': Icons.campaign_rounded, 'camera': Icons.photo_camera_rounded,
  'tree-pine': Icons.park_rounded, 'umbrella': Icons.beach_access_rounded,
  'ticket': Icons.confirmation_number_rounded, 'baby': Icons.child_care_rounded, 'wrench': Icons.build_rounded,
};

IconData pathIcon(String? name) => _iconMap[name] ?? Icons.menu_book_rounded;

const _unitColors = [
  [Color(0xFF047857), Color(0xFF059669), Color(0xFF065F46)],
  [Color(0xFF4A775F), Color(0xFF6FA287), Color(0xFF3D624E)],
  [Color(0xFF065F46), Color(0xFF0F766E), Color(0xFF064E3B)],
  [Color(0xFF3D624E), Color(0xFF059669), Color(0xFF2F4C3D)],
];

class _PathScreenState extends State<PathScreen> with SingleTickerProviderStateMixin {
  Map<String, dynamic>? _ov;
  String? _error;
  bool _loading = true;
  String? _level;
  late final AnimationController _pulse =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 1800))..repeat(reverse: true);

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // "Animasyonları kaldır" açıksa BAŞLA düğümü nabız atmaz
    if (MediaQuery.of(context).disableAnimations) {
      _pulse.stop();
    } else if (!_pulse.isAnimating) {
      _pulse.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  Future<void> _load([String? level]) async {
    setState(() {
      _loading = _ov == null;
      _error = null;
    });
    final loader = widget.loader ?? ApiService().getPathOverview;
    final res = await loader(level: level ?? _level);
    if (!mounted) return;
    setState(() {
      _loading = false;
      if (res.ok) {
        _ov = res.data;
        _level = res.data!['selected_level'] as String?;
      } else {
        _error = res.error;
      }
    });
  }

  Future<void> _open(String kind, String? id) async {
    final result = await Navigator.of(context).push<Map<String, dynamic>>(
      MaterialPageRoute(fullscreenDialog: true, builder: (_) => LessonScreen(kind: kind, id: id)),
    );
    if (!mounted) return;
    await _load();
    final next = result?['next'] as String?;
    if (next != null && mounted) _open('topic', next);
  }

  void _toast(String msg) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(msg), behavior: SnackBarBehavior.floating));
  }

  @override
  Widget build(BuildContext context) {
    final ov = _ov;
    Widget body;
    if (_loading) {
      body = const Center(child: CircularProgressIndicator());
    } else if (ov == null) {
      body = ListView(padding: const EdgeInsets.all(24), children: [
        const SizedBox(height: 80),
        Icon(Icons.cloud_off_rounded, size: 48, color: PanelColors.muted(context)),
        const SizedBox(height: 12),
        Text(_error ?? 'Konu yolu yüklenemedi.', textAlign: TextAlign.center,
            style: TextStyle(color: PanelColors.text(context), fontWeight: FontWeight.w600)),
        const SizedBox(height: 16),
        Center(
          child: Press3D(
            key: const Key('path_retry'),
            onTap: () => _load(),
            color: AppTheme.brandBlue,
            baseColor: const Color(0xFF047857),
            child: const Text('Tekrar dene', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
          ),
        ),
      ]);
    } else {
      body = _content(ov);
    }
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(onRefresh: () => _load(), child: body),
      ),
    );
  }

  Widget _content(Map<String, dynamic> ov) {
    final stats = (ov['stats'] as Map?)?.cast<String, dynamic>() ?? const {};
    final levels = ((ov['levels'] as List?) ?? const []).cast<Map<String, dynamic>>();
    final units = ((ov['units'] as List?) ?? const []).cast<Map<String, dynamic>>();
    final selected = levels.firstWhere((l) => l['level'] == ov['selected_level'],
        orElse: () => {'level': ov['selected_level'], 'title': '', 'done': 0, 'total': 0, 'unlocked': true});
    final current = ov['current_topic'] as String?;

    return ListView(
      key: const Key('path_list'),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 28),
      children: [
        _header(stats),
        const SizedBox(height: 14),
        _hero(current),
        const SizedBox(height: 14),
        _levelCard(levels, selected, stats['review_available'] == true),
        const SizedBox(height: 18),
        if (selected['unlocked'] == true)
          for (var i = 0; i < units.length; i++) _unit(units[i], i, current, '${ov['selected_level']}')
        else
          _lockedLevel(levels, selected),
      ],
    );
  }

  Widget _header(Map<String, dynamic> stats) {
    Widget pill(IconData icon, Color color, String text, String label) => Semantics(
          label: label,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: PanelColors.card(context),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: PanelColors.border(context)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 4),
              Text(text, style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: PanelColors.text(context))),
            ]),
          ),
        );
    return Row(children: [
      Expanded(
        child: Text('Konu Yolu',
            overflow: TextOverflow.ellipsis,
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: PanelColors.text(context))),
      ),
      pill(Icons.bolt_rounded, AppTheme.accentAmber, '${stats['xp_total'] ?? 0}', 'Toplam XP'),
      const SizedBox(width: 6),
      pill(Icons.check_circle_rounded, AppTheme.brandBlue, '${stats['completed'] ?? 0}/${stats['total'] ?? 0}',
          'Biten ders'),
    ]);
  }

  Widget _hero(String? current) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(22),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF064E3B), Color(0xFF047857), Color(0xFF6FA287)],
        ),
        boxShadow: const [BoxShadow(color: Color(0x40047857), blurRadius: 24, offset: Offset(0, 10), spreadRadius: -8)],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Gündelik İngilizceyi adım adım öğren',
            style: TextStyle(color: Colors.white, fontSize: 19, fontWeight: FontWeight.w900, height: 1.2)),
        const SizedBox(height: 6),
        Text('Her ders kısa bir anlatım ve 13 alıştırma. Bitirince sıradaki açılır; yanlışların dersin sonunda yeniden gelir.',
            style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 13, height: 1.35)),
        if (current != null) ...[
          const SizedBox(height: 14),
          Press3D(
            key: const Key('path_continue'),
            onTap: () => _open('topic', current),
            color: Colors.white,
            baseColor: const Color(0x33000000),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
            child: const Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.play_arrow_rounded, color: Color(0xFF065F46), size: 20),
              SizedBox(width: 6),
              Flexible(
                child: Text('Kaldığın yerden devam',
                    style: TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.w900)),
              ),
            ]),
          ),
        ],
      ]),
    );
  }

  Widget _levelCard(List<Map<String, dynamic>> levels, Map<String, dynamic> selected, bool reviewAvailable) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: PanelColors.card(context),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: PanelColors.border(context)),
        boxShadow: PanelColors.cardShadow(context),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('${selected['level']} · ${selected['title']}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontWeight: FontWeight.w900, color: PanelColors.text(context))),
              Text('${selected['done']}/${selected['total']} ders tamamlandı',
                  style: TextStyle(fontSize: 12, color: PanelColors.muted(context))),
            ]),
          ),
          const SizedBox(width: 8),
          Press3D(
            key: const Key('path_review'),
            onTap: reviewAvailable ? () => _open('review', _level) : () => _toast('Tekrar için önce bir ders bitir.'),
            color: PanelColors.card(context),
            baseColor: PanelColors.border(context),
            borderColor: PanelColors.border(context),
            depth: 3,
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.refresh_rounded, size: 16, color: reviewAvailable ? AppTheme.brandBlue : PanelColors.muted(context)),
              const SizedBox(width: 4),
              Text('Tekrar',
                  style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: reviewAvailable ? PanelColors.text(context) : PanelColors.muted(context))),
            ]),
          ),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          for (var i = 0; i < levels.length; i++) ...[
            if (i > 0) const SizedBox(width: 6),
            Expanded(child: _levelChip(levels[i], levels[i]['level'] == selected['level'])),
          ],
        ]),
      ]),
    );
  }

  Widget _levelChip(Map<String, dynamic> l, bool active) {
    final unlocked = l['unlocked'] == true;
    final total = (l['total'] as num?)?.toInt() ?? 0;
    final done = (l['done'] as num?)?.toInt() ?? 0;
    return Semantics(
      button: true,
      selected: active,
      label: '${l['level']} ${unlocked ? '$done/$total' : 'kilitli'}',
      child: InkWell(
        key: Key('path_level_${l['level']}'),
        borderRadius: BorderRadius.circular(12),
        onTap: () => _load('${l['level']}'),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: active ? AppTheme.brandLightBlue : PanelColors.tile(context).withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: active ? AppTheme.brandBlue : PanelColors.border(context), width: active ? 2 : 1),
          ),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('${l['level']}',
                style: TextStyle(
                    fontWeight: FontWeight.w900,
                    fontSize: 13,
                    color: active ? const Color(0xFF047857) : (unlocked ? PanelColors.text(context) : PanelColors.muted(context)))),
            const SizedBox(height: 4),
            if (unlocked)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(9),
                  child: LinearProgressIndicator(
                    value: total == 0 ? 0 : done / total,
                    minHeight: 4,
                    color: AppTheme.brandBlue,
                    backgroundColor: PanelColors.track(context),
                  ),
                ),
              )
            else
              Icon(Icons.lock_rounded, size: 12, color: PanelColors.muted(context)),
          ]),
        ),
      ),
    );
  }

  Widget _lockedLevel(List<Map<String, dynamic>> levels, Map<String, dynamic> selected) {
    final idx = levels.indexWhere((l) => l['level'] == selected['level']);
    final prev = idx > 0 ? levels[idx - 1] : null;
    final need = prev == null ? 0 : (((prev['total'] as num?) ?? 0) * 0.8).ceil();
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: PanelColors.card(context),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: PanelColors.border(context)),
      ),
      child: Column(children: [
        Icon(Icons.lock_rounded, size: 40, color: PanelColors.muted(context)),
        const SizedBox(height: 10),
        Text('${selected['level']} henüz kilitli',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: PanelColors.text(context))),
        const SizedBox(height: 6),
        Text(
          prev == null
              ? 'Seviye tespitine girersen kurun ve altındaki seviyeler açılır.'
              : 'Açmak için ${prev['level']} seviyesinde en az $need ders bitir (şu an ${prev['done']}/${prev['total']}). '
                  'Seviye tespitine girersen kurun ve altındaki seviyeler hemen açılır.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: PanelColors.muted(context), height: 1.4),
        ),
        if (prev != null) ...[
          const SizedBox(height: 14),
          Press3D(
            onTap: () => _load('${prev['level']}'),
            color: AppTheme.brandBlue,
            baseColor: const Color(0xFF047857),
            child: Text('${prev['level']} seviyesine git',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
          ),
        ],
      ]),
    );
  }

  Widget _unit(Map<String, dynamic> u, int i, String? current, String level) {
    final colors = _unitColors[i % _unitColors.length];
    final done = (u['done'] as num?)?.toInt() ?? 0;
    final total = (u['total'] as num?)?.toInt() ?? 0;
    final topics = ((u['topics'] as List?) ?? const []).cast<Map<String, dynamic>>();
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Container(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(18),
          gradient: LinearGradient(colors: [colors[0], colors[1]]),
          boxShadow: [BoxShadow(color: colors[2], offset: const Offset(0, 5))],
        ),
        child: Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('$level · ÜNİTE ${u['index']}',
                  style: TextStyle(
                      color: Colors.white.withValues(alpha: 0.85),
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.6)),
              const SizedBox(height: 2),
              Text('${u['title_tr']}',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w900)),
            ]),
          ),
          const SizedBox(width: 10),
          Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
            Text('$done/$total',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 13)),
            const SizedBox(height: 6),
            SizedBox(
              width: 64,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(9),
                child: LinearProgressIndicator(
                  value: total == 0 ? 0 : done / total,
                  minHeight: 6,
                  color: Colors.white,
                  backgroundColor: Colors.white.withValues(alpha: 0.25),
                ),
              ),
            ),
          ]),
        ]),
      ),
      const SizedBox(height: 26),
      for (var j = 0; j < topics.length; j++) _node(topics[j], j, topics[j]['id'] == current),
      _reviewNode(u),
      const SizedBox(height: 28),
    ]);
  }

  Widget _node(Map<String, dynamic> t, int j, bool isCurrent) {
    final status = t['status'] as String? ?? 'locked';
    final stars = (t['stars'] as num?)?.toInt() ?? 0;
    final locked = status == 'locked';
    final face = locked ? PanelColors.track(context) : AppTheme.brandBlue;
    final base = locked ? PanelColors.border(context) : const Color(0xFF047857);
    final icon = locked
        ? Icons.lock_rounded
        : (status == 'done' && stars >= 3 ? Icons.workspace_premium_rounded : pathIcon(t['icon'] as String?));

    Widget circle = Press3D(
      key: Key('path_node_${t['id']}'),
      semanticLabel: '${t['title_tr']}${locked ? ', kilitli' : ''}',
      onTap: locked ? () => _toast('Bu ders kilitli. Önce sıradaki dersi bitir.') : () => _open('topic', '${t['id']}'),
      color: face,
      baseColor: base,
      shape: BoxShape.circle,
      depth: 6,
      width: 70,
      height: 70,
      padding: EdgeInsets.zero,
      child: Center(child: Icon(icon, size: 30, color: locked ? PanelColors.muted(context) : Colors.white)),
    );

    if (isCurrent) {
      circle = AnimatedBuilder(
        animation: _pulse,
        builder: (context, child) => DecoratedBox(
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppTheme.brandBlue.withValues(alpha: 0.22 - 0.14 * _pulse.value),
                spreadRadius: 5 + 7 * _pulse.value,
              ),
            ],
          ),
          child: child,
        ),
        child: circle,
      );
    }

    return Transform.translate(
      offset: Offset(_nodeOffsets[j % _nodeOffsets.length], 0),
      child: Padding(
        padding: EdgeInsets.only(top: isCurrent ? 34 : 0, bottom: 14),
        child: Column(children: [
          Stack(clipBehavior: Clip.none, alignment: Alignment.topCenter, children: [
            circle,
            if (isCurrent)
              Positioned(
                top: -34,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: PanelColors.card(context),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppTheme.brandLightBlue, width: 2),
                  ),
                  child: const Text('BAŞLA',
                      style: TextStyle(
                          color: Color(0xFF047857), fontSize: 11, fontWeight: FontWeight.w900, letterSpacing: 1)),
                ),
              ),
          ]),
          if (status == 'done')
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Row(mainAxisSize: MainAxisSize.min, children: [
                for (var s = 1; s <= 3; s++)
                  Icon(Icons.star_rounded,
                      size: 16, color: s <= stars ? AppTheme.accentAmber : PanelColors.border(context)),
              ]),
            ),
          const SizedBox(height: 4),
          SizedBox(
            width: 140,
            child: Text('${t['title_tr']}',
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: locked ? PanelColors.muted(context) : PanelColors.text(context))),
          ),
        ]),
      ),
    );
  }

  Widget _reviewNode(Map<String, dynamic> u) {
    final open = u['review_unlocked'] == true;
    final stars = (u['review_stars'] as num?)?.toInt() ?? 0;
    return Column(children: [
      Press3D(
        key: Key('path_unit_${u['id']}'),
        semanticLabel: 'Ünite tekrarı${open ? '' : ', kilitli'}',
        onTap: open
            ? () => _open('unit', '${u['id']}')
            : () => _toast('Ünite tekrarı, ünitedeki bütün dersleri bitirince açılır.'),
        color: open ? const Color(0xFFF59E0B) : PanelColors.track(context),
        baseColor: open ? const Color(0xFFB45309) : PanelColors.border(context),
        borderRadius: BorderRadius.circular(20),
        depth: 6,
        width: 62,
        height: 62,
        padding: EdgeInsets.zero,
        child: Center(
          child: Icon(open ? Icons.emoji_events_rounded : Icons.lock_rounded,
              size: 28, color: open ? Colors.white : PanelColors.muted(context)),
        ),
      ),
      const SizedBox(height: 4),
      Text(stars > 0 ? 'Ünite tekrarı ${'★' * stars}' : 'Ünite tekrarı',
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: PanelColors.muted(context))),
    ]);
  }
}
