import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Seviye seçici (A1–C2 + "Tümü"): seçenekler ekran genişliğine eşit bölünür, yan yana sığar.
/// Kaydırmalı çip şeridinin yerine kullanılır; dar telefonda son düğme yarım görünmez,
/// büyük yazı tipinde yazı kesilmek yerine hafifçe küçülür.
class LevelSelector extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onSelected;

  /// Öğrencinin kendi seviyesi (yanına ★ konur).
  final String? highlight;
  final bool includeAll;
  final Color selectedColor;
  final EdgeInsetsGeometry padding;

  const LevelSelector({
    super.key,
    required this.selected,
    required this.onSelected,
    this.highlight,
    this.includeAll = true,
    this.selectedColor = AppTheme.brandBlue,
    this.padding = const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  });

  static const levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

  @override
  Widget build(BuildContext context) {
    final options = [...levels, if (includeAll) 'all'];
    return Padding(
      padding: padding,
      child: Row(
        children: options.map((lvl) {
          final isSel = selected == lvl;
          final label = lvl == 'all'
              ? 'Tümü'
              : (lvl == highlight ? '$lvl★' : lvl);
          return Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Material(
                color: isSel ? selectedColor : Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: BorderSide(
                    color: isSel ? selectedColor : AppTheme.borderSubtle,
                  ),
                ),
                child: InkWell(
                  key: Key('level_$lvl'),
                  borderRadius: BorderRadius.circular(10),
                  onTap: isSel ? null : () => onSelected(lvl),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: 9,
                      horizontal: 2,
                    ),
                    child: FittedBox(
                      fit: BoxFit.scaleDown,
                      child: Text(
                        label,
                        maxLines: 1,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w800,
                          color: isSel ? Colors.white : AppTheme.textMain,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
