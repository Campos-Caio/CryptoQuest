import 'package:flutter/material.dart';
import '../theme/learning_path_colors.dart';

class GlassmorphismCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final VoidCallback? onTap;
  final bool isElevated;
  final Color? backgroundColor;

  const GlassmorphismCard({
    Key? key,
    required this.child,
    this.padding,
    this.margin,
    this.borderRadius = 16.0,
    this.onTap,
    this.isElevated = false,
    this.backgroundColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(borderRadius),
          child: Container(
            padding: padding ?? const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: backgroundColor != null
                  ? null
                  : LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        LearningPathColors.cardBackground.withOpacity(0.8),
                        LearningPathColors.cardBackgroundLight.withOpacity(0.6),
                      ],
                    ),
              color: backgroundColor,
              borderRadius: BorderRadius.circular(borderRadius),
              border: Border.all(
                color: LearningPathColors.primaryPurple.withOpacity(0.1),
                width: 1,
              ),
              boxShadow: isElevated
                  ? LearningPathColors.elevatedShadow
                  : LearningPathColors.cardShadow,
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}
