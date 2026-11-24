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
  'Sentence Completion': Color(0xFF185FA5),
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
      _dark(c) ? AppTheme.darkCardBg : const Color(0xFFF1F5F9);
  static Color track(BuildContext c) =>
      _dark(c) ? AppTheme.darkBorderSubtle : const Color(0xFFEEF2F7);
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
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: PanelColors.border(context)),
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
        color: PanelColors.tile(context),
        borderRadius: BorderRadius.circular(10),
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
        : (dark ? const Color(0xFF172554) : const Color(0xFFEFF6FF));
    final fg = warning
        ? (dark ? const Color(0xFFFDE68A) : const Color(0xFF92400E))
        : (dark ? const Color(0xFFBFDBFE) : const Color(0xFF1E40AF));
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
