import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Web paneliyle aynı sade tasarım dilinin parçaları: kutucuk, uyarı satırı,
/// ilerleme satırı, sekmeli ilerleme kartı ve günün planı.

/// Bölüm (soru kategorisi) renkleri: web ile aynı.
const Map<String, Color> categoryColors = {
  'Grammar': Color(0xFF534AB7),
  'Vocabulary': Color(0xFF1D9E75),
  'Reading': Color(0xFFD85A30),
  'Restatement': Color(0xFFBA7517),
  'Cloze Test': Color(0xFFD4537E),
  'Sentence Completion': Color(0xFF475569),
  'Paragraph Completion': Color(0xFF0F6E56),
  'Dialogue': Color(0xFF993556),
};

Color categoryColor(String category) =>
    categoryColors[category] ?? const Color(0xFF64748B);

class PanelColors {
  static bool _dark(BuildContext c) =>
      Theme.of(c).brightness == Brightness.dark;
  static Color card(BuildContext c) =>
      _dark(c) ? AppTheme.darkCardBg : Colors.white;
  static Color border(BuildContext c) =>
      _dark(c) ? AppTheme.darkBorderSubtle : AppTheme.borderSubtle;
  static Color text(BuildContext c) =>
      _dark(c) ? AppTheme.darkTextMain : AppTheme.textMain;
  static Color muted(BuildContext c) =>
      _dark(c) ? AppTheme.darkTextMuted : AppTheme.textMuted;
  static Color tile(BuildContext c) =>
      _dark(c) ? AppTheme.darkCardBg : const Color(0xFFE6F2EC);
  static Color track(BuildContext c) =>
      _dark(c) ? AppTheme.darkBorderSubtle : const Color(0xFFE1EEE7);
  static List<BoxShadow> cardShadow(BuildContext c) => _dark(c)
      ? const []
      : const [
          BoxShadow(
            color: Color(0x0A0F172A),
            blurRadius: 2,
            offset: Offset(0, 1),
          ),
          BoxShadow(
            color: Color(0x140F172A),
            blurRadius: 24,
            spreadRadius: -12,
            offset: Offset(0, 10),
          ),
        ];
}

class PanelCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;

  const PanelCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(14),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: PanelColors.card(context),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: PanelColors.border(context)),
        boxShadow: PanelColors.cardShadow(context),
      ),
      child: child,
    );
  }
}

class KpiTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String label;
  final String value;

  const KpiTile({
    super.key,
    required this.icon,
    required this.iconColor,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: PanelColors.card(context),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: PanelColors.border(context)),
        boxShadow: PanelColors.cardShadow(context),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: iconColor),
              const SizedBox(width: 5),
              Expanded(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: PanelColors.muted(context),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: PanelColors.text(context),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 2x2 özet kutucukları.
class KpiGrid extends StatelessWidget {
  final List<KpiTile> tiles;

  const KpiGrid({super.key, required this.tiles});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, box) {
        final w = (box.maxWidth - 8) / 2;
        return Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [for (final t in tiles) SizedBox(width: w, child: t)],
        );
      },
    );
  }
}

enum AlertTone { warning, info }

class AlertRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final String actionLabel;
  final AlertTone tone;
  final VoidCallback onTap;

  const AlertRow({
    super.key,
    required this.icon,
    required this.text,
    required this.actionLabel,
    required this.onTap,
    this.tone = AlertTone.warning,
  });

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final warning = tone == AlertTone.warning;
    final bg = warning
        ? (dark ? const Color(0xFF451A03) : const Color(0xFFFFFBEB))
        : (dark ? const Color(0xFF172554) : const Color(0xFFECFDF5));
    final fg = warning
        ? (dark ? const Color(0xFFFDE68A) : const Color(0xFF92400E))
        : (dark ? const Color(0xFFA7F3D0) : const Color(0xFF065F46));
    return Material(
      color: bg,
      borderRadius: BorderRadius.circular(10),
      child: InkWell(
        borderRadius: BorderRadius.circular(10),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: Row(
            children: [
              Icon(icon, size: 18, color: fg),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  text,
                  style: TextStyle(
                    fontSize: 12.5,
                    fontWeight: FontWeight.w600,
                    color: fg,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                actionLabel,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: fg,
                ),
              ),
              Icon(Icons.chevron_right, size: 18, color: fg),
            ],
          ),
        ),
      ),
    );
  }
}

class ProgressLine extends StatelessWidget {
  final double value;
  final Color color;

  const ProgressLine({super.key, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(99),
      child: LinearProgressIndicator(
        value: value.clamp(0.0, 1.0),
        minHeight: 5,
        backgroundColor: PanelColors.track(context),
        valueColor: AlwaysStoppedAnimation(color),
      ),
    );
  }
}

class NumberDot extends StatelessWidget {
  final int number;
  final Color color;

  const NumberDot({super.key, required this.number, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 26,
      height: 26,
      alignment: Alignment.center,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      child: Text(
        '$number',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

/// Bölüm/kur/hata satırı: solda numara, ortada ad + sağda sayı, altında ilerleme çubuğu.
class ProgressRow extends StatelessWidget {
  final Widget leading;
  final String title;
  final String trailingText;
  final Color trailingColor;
  final double? progress;
  final Color color;
  final Widget? action;
  final VoidCallback? onTap;
  final bool showDivider;

  const ProgressRow({
    super.key,
    required this.leading,
    required this.title,
    required this.trailingText,
    required this.color,
    this.trailingColor = AppTheme.textMuted,
    this.progress,
    this.action,
    this.onTap,
    this.showDivider = true,
  });

  @override
  Widget build(BuildContext context) {
    final row = Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        children: [
          leading,
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: PanelColors.text(context),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      trailingText,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: trailingColor,
                      ),
                    ),
                  ],
                ),
                if (progress != null) ...[
                  const SizedBox(height: 6),
                  ProgressLine(value: progress!, color: color),
                ],
              ],
            ),
          ),
          if (action != null) ...[const SizedBox(width: 6), action!],
        ],
      ),
    );
    return DecoratedBox(
      decoration: BoxDecoration(
        border: showDivider
            ? Border(bottom: BorderSide(color: PanelColors.border(context)))
            : null,
      ),
      child: onTap == null ? row : InkWell(onTap: onTap, child: row),
    );
  }
}

/// Bugünün planı: sunucunun önerdiği 2-3 görev ve ilerlemeleri.
class TodayPlanCard extends StatelessWidget {
  final List<Map<String, dynamic>> plan;
  final void Function(Map<String, dynamic> item) onAction;

  const TodayPlanCard({super.key, required this.plan, required this.onAction});

  @override
  Widget build(BuildContext context) {
    final doneCount = plan
        .where((p) => (p['done'] ?? 0) >= (p['target'] ?? 1))
        .length;
    return PanelCard(
      key: const Key('dashboard_plan'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Bugünün planı',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: PanelColors.text(context),
                  ),
                ),
              ),
              Text(
                '$doneCount/${plan.length} tamam',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: PanelColors.muted(context),
                ),
              ),
            ],
          ),
          for (var i = 0; i < plan.length; i++)
            Builder(
              builder: (context) {
                final p = plan[i];
                final done = (p['done'] as num?)?.toInt() ?? 0;
                final target = (p['target'] as num?)?.toInt() ?? 1;
                final complete = done >= target;
                return ProgressRow(
                  key: Key('plan_${p['id']}'),
                  leading: Icon(
                    complete
                        ? Icons.check_circle
                        : Icons.radio_button_unchecked,
                    size: 22,
                    color: complete
                        ? AppTheme.accentEmerald
                        : PanelColors.border(context),
                  ),
                  title: '${p['title']}',
                  trailingText: '$done/$target',
                  progress: target == 0 ? 0 : done / target,
                  color: complete ? AppTheme.accentEmerald : AppTheme.brandBlue,
                  action: Icon(
                    Icons.chevron_right,
                    size: 18,
                    color: PanelColors.muted(context),
                  ),
                  showDivider: i < plan.length - 1,
                  onTap: () => onAction(p),
                );
              },
            ),
        ],
      ),
    );
  }
}

/// Sekmeli ilerleme kartı: Bölümler / Kurlar / Hatalar.
class ProgressTabsCard extends StatefulWidget {
  final Map<String, dynamic> overview;
  final String poolLabel;
  final void Function(String category) onPractice;
  final void Function(String level) onLevel;
  final VoidCallback onMistakes;

  const ProgressTabsCard({
    super.key,
    required this.overview,
    required this.poolLabel,
    required this.onPractice,
    required this.onLevel,
    required this.onMistakes,
  });

  @override
  State<ProgressTabsCard> createState() => _ProgressTabsCardState();
}

class _ProgressTabsCardState extends State<ProgressTabsCard> {
  int _tab = 0;

  Widget _tabs() {
    const labels = ['Bölümler', 'Kurlar', 'Hatalar'];
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: PanelColors.tile(context),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          for (var i = 0; i < labels.length; i++)
            Expanded(
              child: InkWell(
                key: Key('progress_tab_$i'),
                borderRadius: BorderRadius.circular(8),
                onTap: () => setState(() => _tab = i),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 7),
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: _tab == i ? PanelColors.card(context) : null,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    labels[i],
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: _tab == i
                          ? PanelColors.text(context)
                          : PanelColors.muted(context),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  List<Widget> _sections() {
    final level = '${widget.overview['level']}';
    final list = (widget.overview['sections'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    if (list.isEmpty) return [_empty('Bu kurda soru bulunamadı.')];
    return [
      _note('${widget.poolLabel} · $level · doğru çözülen / toplam'),
      for (var i = 0; i < list.length; i++)
        ProgressRow(
          key: Key('section_row_$i'),
          leading: NumberDot(
            number: i + 1,
            color: categoryColor('${list[i]['category']}'),
          ),
          title: '${list[i]['category']}',
          trailingText: '${list[i]['correct']}/${list[i]['total']}',
          progress: (list[i]['total'] ?? 0) == 0
              ? 0
              : (list[i]['correct'] as num) / (list[i]['total'] as num),
          color: categoryColor('${list[i]['category']}'),
          showDivider: i < list.length - 1,
          action: IconButton(
            key: Key('section_play_$i'),
            visualDensity: VisualDensity.compact,
            tooltip: '${list[i]['category']} sorularını çöz',
            icon: const Icon(Icons.play_arrow_rounded, size: 22),
            color: PanelColors.muted(context),
            onPressed: () => widget.onPractice('${list[i]['category']}'),
          ),
        ),
    ];
  }

  List<Widget> _levels() {
    final current = '${widget.overview['level']}';
    final list = (widget.overview['levels'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>();
    return [
      _note('${widget.poolLabel} · kur seçmek için dokun'),
      for (var i = 0; i < list.length; i++)
        Builder(
          builder: (context) {
            final l = list[i];
            final isCurrent = l['level'] == current;
            final color = isCurrent
                ? AppTheme.brandBlue
                : const Color(0xFF94A3B8);
            return ProgressRow(
              key: Key('level_row_${l['level']}'),
              leading: NumberDot(number: i + 1, color: color),
              title: isCurrent ? '${l['level']} · seçili' : '${l['level']}',
              trailingText: '${l['correct']}/${l['total']}',
              progress: (l['total'] ?? 0) == 0
                  ? 0
                  : (l['correct'] as num) / (l['total'] as num),
              color: color,
              showDivider: i < list.length - 1,
              action: Icon(
                Icons.chevron_right,
                size: 18,
                color: PanelColors.muted(context),
              ),
              onTap: () => widget.onLevel('${l['level']}'),
            );
          },
        ),
    ];
  }

  List<Widget> _mistakes() {
    final map = (widget.overview['mistakes_by_category'] as Map?) ?? {};
    if (map.isEmpty) {
      return [
        _empty('Hata Kasası boş. Yanlış yaptığın sorular burada toplanır.'),
      ];
    }
    final entries = map.entries.toList();
    final maxN = entries
        .map((e) => (e.value as num).toInt())
        .reduce((a, b) => a > b ? a : b);
    return [
      _note('Hata Kasası\'nda çözülmeyi bekleyenler'),
      for (var i = 0; i < entries.length; i++)
        ProgressRow(
          key: Key('mistake_row_$i'),
          leading: NumberDot(
            number: i + 1,
            color: categoryColor('${entries[i].key}'),
          ),
          title: '${entries[i].key}',
          trailingText: '${entries[i].value} hata',
          trailingColor: AppTheme.accentRose,
          progress: (entries[i].value as num) / maxN,
          color: categoryColor('${entries[i].key}'),
          showDivider: i < entries.length - 1,
          action: Icon(
            Icons.chevron_right,
            size: 18,
            color: PanelColors.muted(context),
          ),
          onTap: widget.onMistakes,
        ),
    ];
  }

  Widget _note(String text) => Padding(
    padding: const EdgeInsets.only(top: 10, bottom: 2),
    child: Text(
      text,
      style: TextStyle(fontSize: 11, color: PanelColors.muted(context)),
    ),
  );

  Widget _empty(String text) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 14),
    child: Text(
      text,
      style: TextStyle(fontSize: 12, color: PanelColors.muted(context)),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final body = switch (_tab) {
      0 => _sections(),
      1 => _levels(),
      _ => _mistakes(),
    };
    return PanelCard(
      key: const Key('dashboard_progress'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [_tabs(), ...body],
      ),
    );
  }
}

/// Basınca hafifçe küçülen, bırakınca yükselen gölgeli düğme (premium his).
class LiftButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final bool primary;
  final EdgeInsetsGeometry padding;

  const LiftButton({
    super.key,
    required this.child,
    required this.onPressed,
    this.primary = false,
    this.padding = const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
  });

  @override
  State<LiftButton> createState() => _LiftButtonState();
}

class _LiftButtonState extends State<LiftButton> {
  bool _down = false;

  @override
  Widget build(BuildContext context) {
    final primary = widget.primary;
    final shadow = primary
        ? [
            BoxShadow(
              color: AppTheme.brandBlue.withValues(alpha: _down ? 0.25 : 0.45),
              blurRadius: _down ? 6 : 16,
              spreadRadius: -4,
              offset: Offset(0, _down ? 2 : 8),
            ),
          ]
        : [
            BoxShadow(
              color: const Color(0xFF0F172A)
                  .withValues(alpha: _down ? 0.04 : 0.10),
              blurRadius: _down ? 2 : 12,
              spreadRadius: -4,
              offset: Offset(0, _down ? 1 : 6),
            ),
          ];
    return GestureDetector(
      onTapDown: (_) => setState(() => _down = true),
      onTapCancel: () => setState(() => _down = false),
      onTapUp: (_) => setState(() => _down = false),
      onTap: widget.onPressed,
      child: AnimatedScale(
        scale: _down ? 0.96 : 1,
        duration: const Duration(milliseconds: 120),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          padding: widget.padding,
          decoration: BoxDecoration(
            gradient: primary
                ? const LinearGradient(
                    colors: [
                      Color(0xFF10B981),
                      Color(0xFF059669),
                      Color(0xFF047857),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  )
                : null,
            color: primary ? null : PanelColors.card(context),
            borderRadius: BorderRadius.circular(10),
            border: primary
                ? null
                : Border.all(color: PanelColors.border(context)),
            boxShadow: shadow,
          ),
          child: DefaultTextStyle.merge(
            style: TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w700,
              color: primary ? Colors.white : PanelColors.text(context),
            ),
            child: IconTheme.merge(
              data: IconThemeData(
                size: 16,
                color: primary ? Colors.white : PanelColors.text(context),
              ),
              child: widget.child,
            ),
          ),
        ),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final IconData? icon;
  final String text;
  final Color bg;
  final Color fg;

  const _Pill({
    this.icon,
    required this.text,
    required this.bg,
    required this.fg,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(99),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: fg),
            const SizedBox(width: 4),
          ],
          Text(
            text,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }
}

const Map<String, IconData> _taskIcons = {
  'layers': Icons.layers_outlined,
  'trending-up': Icons.trending_up,
  'target': Icons.track_changes,
  'shield-alert': Icons.shield_outlined,
};

Widget _gradientBar() => Container(
  height: 3,
  decoration: const BoxDecoration(
    gradient: LinearGradient(
      colors: [Color(0xFF10B981), Color(0xFF6FA287), Color(0xFF10B981)],
    ),
  ),
);

/// Günlük görevler: seviye tespitinden önce kilitli; sonra seri, haftalık takvim ve görev listesi.
class DailyTasksCard extends StatelessWidget {
  final Map<String, dynamic> daily;
  final VoidCallback onStartPlacement;
  final void Function(Map<String, dynamic> task) onTask;

  const DailyTasksCard({
    super.key,
    required this.daily,
    required this.onStartPlacement,
    required this.onTask,
  });

  @override
  Widget build(BuildContext context) {
    final text = PanelColors.text(context);
    final muted = PanelColors.muted(context);
    if (daily['locked'] == true) {
      return PanelCard(
        key: const Key('daily_locked'),
        padding: EdgeInsets.zero,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _gradientBar(),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: AppTheme.brandBlue,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(
                            Icons.insights_rounded,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Günlük görevlerin seviye tespitinden sonra açılır',
                            style: TextStyle(
                              fontSize: 14.5,
                              fontWeight: FontWeight.w800,
                              color: text,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '5 dakikalık uyarlamalı sınavla seviyeni belirle; sana her gün kelime, soru ve hata görevleri verelim, ilerlemeni seri ve kur yolculuğuyla takip et.',
                      style: TextStyle(fontSize: 12, height: 1.4, color: muted),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: LiftButton(
                        key: const Key('daily_start_placement'),
                        primary: true,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        onPressed: onStartPlacement,
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.play_arrow_rounded),
                            SizedBox(width: 6),
                            Text('Seviye tespitine başla'),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    }

    final placement = (daily['placement'] as Map?) ?? {};
    final tasks = ((daily['tasks'] as List?) ?? [])
        .cast<Map<String, dynamic>>();
    final week = ((daily['week'] as List?) ?? []).cast<Map<String, dynamic>>();
    final mastered = placement['mastered'];
    final masteredText = mastered != null ? '$mastered geçildi · ' : '';
    final allDone = daily['all_done'] == true;
    return PanelCard(
      key: const Key('daily_tasks'),
      padding: EdgeInsets.zero,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _gradientBar(),
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 14, 14, 6),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'Günlük görevler',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w800,
                            color: text,
                          ),
                        ),
                      ),
                      _Pill(
                        icon: Icons.local_fire_department,
                        text: '${daily['streak'] ?? 0} gün',
                        bg: const Color(0xFFFFF7ED),
                        fg: const Color(0xFFC2410C),
                      ),
                      const SizedBox(width: 6),
                      _Pill(
                        text: '${daily['xp_today'] ?? 0} XP',
                        bg: const Color(0xFFEEF5F1),
                        fg: const Color(0xFF4A775F),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Seviye tespiti: $masteredText'
                    'önerilen ${placement['level']}',
                    style: TextStyle(fontSize: 11, color: muted),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    key: const Key('daily_week'),
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      for (final w in week) _weekDot(context, w, muted),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    allDone
                        ? 'Bugünün görevleri tamam! +20 bonus XP kazandın.'
                        : '${daily['tasks_done'] ?? 0}/${daily['tasks_total'] ?? tasks.length} görev tamam',
                    key: const Key('daily_summary'),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: allDone ? AppTheme.accentEmerald : muted,
                    ),
                  ),
                  for (var i = 0; i < tasks.length; i++)
                    _taskRow(context, tasks[i], i < tasks.length - 1),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _weekDot(BuildContext context, Map<String, dynamic> w, Color muted) {
    final completed = w['completed'] == true;
    final today = w['today'] == true;
    return Column(
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: completed
                ? AppTheme.accentEmerald
                : w['active'] == true
                ? const Color(0xFFD1FAE5)
                : PanelColors.tile(context),
            border: today
                ? Border.all(color: AppTheme.brandBlue, width: 2)
                : null,
          ),
          child: completed
              ? const Icon(Icons.check, size: 15, color: Colors.white)
              : null,
        ),
        const SizedBox(height: 3),
        Text(
          '${w['label']}',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w600,
            color: today ? AppTheme.brandBlue : muted,
          ),
        ),
      ],
    );
  }

  Widget _taskRow(BuildContext context, Map<String, dynamic> t, bool divider) {
    final done = (t['done'] as num?)?.toInt() ?? 0;
    final target = (t['target'] as num?)?.toInt() ?? 1;
    final complete = done >= target;
    return DecoratedBox(
      key: Key('task_${t['id']}'),
      decoration: BoxDecoration(
        border: divider
            ? Border(bottom: BorderSide(color: PanelColors.border(context)))
            : null,
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: complete
                    ? AppTheme.accentEmerald
                    : AppTheme.brandLightBlue,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                complete
                    ? Icons.check
                    : (_taskIcons[t['icon']] ?? Icons.circle_outlined),
                size: 18,
                color: complete ? Colors.white : AppTheme.brandBlue,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          '${t['title']}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: complete
                                ? PanelColors.muted(context)
                                : PanelColors.text(context),
                            decoration: complete
                                ? TextDecoration.lineThrough
                                : null,
                          ),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        '$done/$target',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: PanelColors.muted(context),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 5),
                  ProgressLine(
                    value: target == 0 ? 0 : done / target,
                    color: complete
                        ? AppTheme.accentEmerald
                        : AppTheme.brandBlue,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            complete
                ? _Pill(
                    text: '+${t['xp'] ?? 10} XP',
                    bg: const Color(0xFFECFDF5),
                    fg: const Color(0xFF047857),
                  )
                : LiftButton(
                    key: Key('task_start_${t['id']}'),
                    onPressed: () => onTask(t),
                    child: const Text('Başla'),
                  ),
          ],
        ),
      ),
    );
  }
}

/// Kur yolculuğu: seçili kurdaki doğru oranı ve üst kura hazır olma.
class JourneyCard extends StatelessWidget {
  final Map<String, dynamic> journey;
  final void Function(String level) onNextLevel;

  const JourneyCard({
    super.key,
    required this.journey,
    required this.onNextLevel,
  });

  @override
  Widget build(BuildContext context) {
    final pct = (journey['pct'] as num?)?.toInt() ?? 0;
    final readyPct = (journey['ready_pct'] as num?)?.toInt() ?? 70;
    final next = journey['next_level'];
    final ready = journey['ready'] == true;
    final subtitle = next != null
        ? '${journey['level']} · hedef $next · %$readyPct doğruda üst kura hazırsın'
        : '${journey['level']} · en üst kur';
    return PanelCard(
      key: const Key('journey_card'),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: const Color(0xFFEEF5F1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(
                  Icons.landscape_outlined,
                  size: 19,
                  color: Color(0xFF4A775F),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Kur yolculuğu',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: PanelColors.text(context),
                      ),
                    ),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 11,
                        color: PanelColors.muted(context),
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '%$pct',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: PanelColors.text(context),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, box) => Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  height: 10,
                  decoration: BoxDecoration(
                    color: PanelColors.track(context),
                    borderRadius: BorderRadius.circular(99),
                  ),
                ),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 700),
                  curve: Curves.easeOutCubic,
                  height: 10,
                  width: box.maxWidth * (pct.clamp(0, 100) / 100),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [
                        Color(0xFF6FA287),
                        Color(0xFF10B981),
                        Color(0xFF10B981),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(99),
                  ),
                ),
                Positioned(
                  left: box.maxWidth * readyPct / 100 - 1,
                  top: -4,
                  child: Container(
                    width: 2,
                    height: 18,
                    color: PanelColors.text(context).withValues(alpha: 0.35),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: Text(
                  '${journey['correct']}/${journey['total']} soru doğru',
                  style: TextStyle(
                    fontSize: 11,
                    color: PanelColors.muted(context),
                  ),
                ),
              ),
              if (ready && next != null)
                LiftButton(
                  key: const Key('journey_next'),
                  primary: true,
                  onPressed: () => onNextLevel('$next'),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.rocket_launch_outlined),
                      const SizedBox(width: 6),
                      Text('$next kuruna geç'),
                    ],
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
