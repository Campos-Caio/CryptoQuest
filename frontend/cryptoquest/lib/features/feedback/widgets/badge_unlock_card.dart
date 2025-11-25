import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';

/// Widget de card de badge com animação de desbloqueio
///
/// Exibe um badge conquistado com animação de flip/revelação
/// e efeitos visuais baseados na raridade
class BadgeUnlockCard extends StatefulWidget {
  final BadgeData badge;
  final Duration delay;
  final VoidCallback? onTap;

  const BadgeUnlockCard({
    super.key,
    required this.badge,
    this.delay = Duration.zero,
    this.onTap,
  });

  @override
  State<BadgeUnlockCard> createState() => _BadgeUnlockCardState();
}

class _BadgeUnlockCardState extends State<BadgeUnlockCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _flipController;
  late Animation<double> _flipAnimation;

  @override
  void initState() {
    super.initState();

    _flipController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _flipAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _flipController,
      curve: Curves.easeInOut,
    ));

    // Iniciar animação após delay
    Future.delayed(widget.delay, () {
      if (mounted) {
        _flipController.forward();
      }
    });
  }

  @override
  void dispose() {
    _flipController.dispose();
    super.dispose();
  }

  Color _getRarityColor() {
    final colorHex = widget.badge.rarityColor;
    return Color(
      int.parse(colorHex.replaceFirst('#', '0xFF')),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Calcular tamanho responsivo baseado na largura da tela
    final screenWidth = MediaQuery.of(context).size.width;
    final cardWidth = (screenWidth * 0.22).clamp(90.0, 110.0);
    final cardHeight = cardWidth * 1.2;

    return GestureDetector(
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _flipAnimation,
        builder: (context, child) {
          final angle = _flipAnimation.value * 3.14159;
          final isBack = angle < 1.5708;

          return Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
              ..setEntry(3, 2, 0.001)
              ..rotateY(angle),
            child: isBack
                ? _buildBackCard(cardWidth, cardHeight)
                : _buildFrontCard(cardWidth, cardHeight),
          );
        },
      ),
    );
  }

  /// Card de trás (antes de revelar)
  Widget _buildBackCard(double width, double height) {
    final iconSize = (width * 0.4).clamp(32.0, 48.0);

    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary.withOpacity(0.8),
            AppColors.primary.withOpacity(0.6),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Center(
        child: Icon(
          Icons.help_outline,
          size: iconSize,
          color: Colors.white,
        ),
      ),
    );
  }

  /// Card da frente (badge revelado)
  Widget _buildFrontCard(double width, double height) {
    final rarityColor = _getRarityColor();
    final iconSize = (width * 0.4).clamp(32.0, 48.0);
    final nameFontSize = (width * 0.11).clamp(10.0, 12.0);
    final rarityFontSize = (width * 0.08).clamp(7.0, 9.0);
    final spacing = (height * 0.06).clamp(6.0, 10.0);

    return Transform(
      alignment: Alignment.center,
      transform: Matrix4.identity()..rotateY(3.14159),
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: rarityColor,
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: rarityColor.withOpacity(0.4),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Ícone do badge
            Text(
              widget.badge.icon,
              style: TextStyle(fontSize: iconSize),
            ),
            SizedBox(height: spacing),

            // Nome do badge
            Padding(
              padding: EdgeInsets.symmetric(horizontal: width * 0.08),
              child: Text(
                widget.badge.name,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: nameFontSize,
                  fontWeight: FontWeight.bold,
                  color: AppColors.onSurface,
                ),
              ),
            ),

            // Indicador de raridade
            Container(
              margin: EdgeInsets.only(top: spacing * 0.5),
              padding: EdgeInsets.symmetric(
                horizontal: width * 0.06,
                vertical: height * 0.015,
              ),
              decoration: BoxDecoration(
                color: rarityColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                widget.badge.rarity.toUpperCase(),
                style: TextStyle(
                  fontSize: rarityFontSize,
                  fontWeight: FontWeight.bold,
                  color: rarityColor,
                ),
              ),
            ),
          ],
        ),
      )
          .animate(
            delay: widget.delay + const Duration(milliseconds: 800),
          )
          .shimmer(
            duration: const Duration(milliseconds: 1500),
            color: Colors.white.withOpacity(0.5),
          ),
    );
  }
}

/// Grid de badges desbloqueados
class BadgeUnlockGrid extends StatelessWidget {
  final List<BadgeData> badges;
  final Function(BadgeData)? onBadgeTap;

  const BadgeUnlockGrid({
    super.key,
    required this.badges,
    this.onBadgeTap,
  });

  @override
  Widget build(BuildContext context) {
    if (badges.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Badges Conquistados',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: AppColors.onSurface,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: badges.asMap().entries.map((entry) {
            final index = entry.key;
            final badge = entry.value;
            return BadgeUnlockCard(
              badge: badge,
              delay: Duration(milliseconds: index * 200),
              onTap: onBadgeTap != null ? () => onBadgeTap!(badge) : null,
            );
          }).toList(),
        ),
      ],
    );
  }
}
