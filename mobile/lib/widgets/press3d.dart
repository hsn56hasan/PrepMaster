import 'package:flutter/material.dart';

/// Basılınca aşağı inen, altında koyu "taban" gölgesi olan 3B düğme (yol düğümleri, ders düğmeleri).
class Press3D extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final Color color;
  final Color baseColor;
  final Color? borderColor;
  final BorderRadius borderRadius;
  final double depth;
  final EdgeInsetsGeometry padding;
  final BoxShape shape;
  final double? width;
  final double? height;
  final String? semanticLabel;

  const Press3D({
    super.key,
    required this.child,
    required this.onTap,
    required this.color,
    required this.baseColor,
    this.borderColor,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.depth = 4,
    this.padding = const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
    this.shape = BoxShape.rectangle,
    this.width,
    this.height,
    this.semanticLabel,
  });

  @override
  State<Press3D> createState() => _Press3DState();
}

class _Press3DState extends State<Press3D> {
  bool _down = false;

  void _set(bool v) {
    if (widget.onTap == null || _down == v) return;
    setState(() => _down = v);
  }

  @override
  Widget build(BuildContext context) {
    final d = widget.depth;
    final circle = widget.shape == BoxShape.circle;
    final face = AnimatedContainer(
      duration: const Duration(milliseconds: 90),
      width: widget.width,
      height: widget.height,
      padding: widget.padding,
      transform: Matrix4.translationValues(0, _down ? d : 0, 0),
      decoration: BoxDecoration(
        color: widget.color,
        shape: widget.shape,
        borderRadius: circle ? null : widget.borderRadius,
        border: widget.borderColor == null ? null : Border.all(color: widget.borderColor!, width: 2),
        boxShadow: [
          BoxShadow(color: widget.baseColor, offset: Offset(0, _down ? 0 : d), blurRadius: 0),
        ],
      ),
      child: widget.child,
    );
    return Semantics(
      button: true,
      enabled: widget.onTap != null,
      label: widget.semanticLabel,
      child: Padding(
        padding: EdgeInsets.only(bottom: d),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: (_) => _set(true),
          onTapCancel: () => _set(false),
          onTapUp: (_) => _set(false),
          onTap: widget.onTap,
          child: face,
        ),
      ),
    );
  }
}
