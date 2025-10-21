import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/shared/widgets/animated_lottie_widget.dart';
import 'package:cryptoquest/shared/widgets/enhanced_confetti_widget.dart';

/// Tela especializada para desbloqueio de badges
///
/// Tela dedicada para celebrar badges conquistados
/// com layout otimizado para múltiplos badges
class BadgeUnlockScreen extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;
  final VoidCallback? onViewBadges;

  const BadgeUnlockScreen({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
    this.onViewBadges,
  });

  /// Exibe a tela de Badge Unlock
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
    VoidCallback? onViewBadges,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black.withOpacity(0.7),
      builder: (context) => BadgeUnlockScreen(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
        onViewBadges: onViewBadges,
      ),
    );
  }

  @override
  State<BadgeUnlockScreen> createState() => _BadgeUnlockScreenState();
}

class _BadgeUnlockScreenState extends State<BadgeUnlockScreen>
    with TickerProviderStateMixin {
  late EnhancedConfettiController _confettiController;
  late AnimationController _lottieController;

  @override
  void initState() {
    super.initState();

    _confettiController = EnhancedConfettiController();
    _lottieController = AnimationController(vsync: this);

    _triggerCelebration();
  }

  void _triggerCelebration() {
    // Haptic feedback baseado na raridade dos badges
    final hasLegendary = widget.rewardData.badgesEarned
        .any((badge) => badge.rarity == 'legendary');

    if (hasLegendary) {
      HapticFeedback.heavyImpact();
    } else {
      HapticFeedback.mediumImpact();
    }

    // Confetti após delay
    Future.delayed(const Duration(milliseconds: 600), () {
      if (mounted) {
        if (hasLegendary) {
          _confettiController.showLegendary();
        } else {
          _confettiController.showStandard();
        }
      }
    });
  }

  @override
  void dispose() {
    _confettiController.dispose();
    _lottieController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;

    // Tela adaptável baseada no número de badges
    final badgeCount = widget.rewardData.badgesEarned.length;
    final maxHeight = badgeCount > 2
        ? (screenHeight * 0.85).toDouble()
        : (screenHeight * 0.75).toDouble();
    final maxWidth =
        screenWidth > 600 ? 500.0 : (screenWidth * 0.95).toDouble();

    return Stack(
      children: [
        // Confetti de fundo
        Align(
          alignment: Alignment.topCenter,
          child: EnhancedConfettiWidget(
            controller: _confettiController.controller,
            type: _getConfettiType(),
            numberOfParticles: badgeCount > 2 ? 25 : 20,
          ),
        ),

        // Conteúdo principal
        Center(
          child: Container(
            constraints: BoxConstraints(
              maxHeight: maxHeight,
              maxWidth: maxWidth,
            ),
            margin: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(28),
              boxShadow: [
                BoxShadow(
                  color: AppColors.gold.withOpacity(0.3),
                  blurRadius: 25,
                  spreadRadius: 8,
                ),
                BoxShadow(
                  color: Colors.black.withOpacity(0.4),
                  blurRadius: 15,
                  spreadRadius: 3,
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Conteúdo scrollável
                Flexible(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(28),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Animação Lottie de Badge
                        _buildBadgeAnimation(),

                        const SizedBox(height: 24),

                        // Título principal
                        _buildMainTitle(),

                        const SizedBox(height: 20),

                        // Badges conquistados
                        _buildBadgesSection(),

                        const SizedBox(height: 24),

                        // Estatísticas adicionais
                        if (widget.rewardData.xpGained > 0 ||
                            widget.rewardData.pointsGained > 0)
                          _buildAdditionalStats(),

                        const SizedBox(height: 20),

                        // Botões de ação
                        _buildActionButtons(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          )
              .animate()
              .scale(
                begin: const Offset(0.4, 0.4),
                end: const Offset(1.0, 1.0),
                duration: 500.ms,
                curve: Curves.elasticOut,
              )
              .fadeIn(duration: 300.ms),
        ),
      ],
    );
  }

  /// Animação Lottie de Badge
  Widget _buildBadgeAnimation() {
    return Center(
      child: LottieAnimations.badgeUnlock(
        size: 160,
        controller: _lottieController,
      ),
    ).animate().fadeIn(duration: 400.ms).scale(
          begin: const Offset(0.3, 0.3),
          end: const Offset(1.0, 1.0),
          curve: Curves.elasticOut,
          duration: 700.ms,
        );
  }

  /// Título principal da tela
  Widget _buildMainTitle() {
    final badgeCount = widget.rewardData.badgesEarned.length;
    final title = badgeCount == 1
        ? 'Badge Desbloqueado!'
        : '$badgeCount Badges Desbloqueados!';

    final subtitle = badgeCount == 1
        ? 'Parabéns pela conquista!'
        : 'Incrível! Múltiplas conquistas!';

    return Column(
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.bold,
            color: AppColors.white,
            letterSpacing: 1,
          ),
        ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.3, end: 0.0),
        const SizedBox(height: 8),
        Text(
          subtitle,
          style: TextStyle(
            fontSize: 16,
            color: AppColors.onSurfaceVariant,
            fontWeight: FontWeight.w500,
          ),
        ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2, end: 0.0),
      ],
    );
  }

  /// Seção de badges conquistados
  Widget _buildBadgesSection() {
    final badges = widget.rewardData.badgesEarned;

    if (badges.length == 1) {
      // Badge único - layout centralizado
      return _buildSingleBadge(badges.first);
    } else if (badges.length <= 3) {
      // Poucos badges - layout em grid
      return _buildBadgeGrid(badges);
    } else {
      // Muitos badges - layout em scroll horizontal
      return _buildBadgeScroll(badges);
    }
  }

  /// Badge único centralizado
  Widget _buildSingleBadge(BadgeData badge) {
    return Center(
      child: Container(
        width: 200,
        height: 200,
        decoration: BoxDecoration(
          gradient: _getBadgeGradient(badge.rarity),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: _getBadgeColor(badge.rarity).withOpacity(0.4),
              blurRadius: 20,
              spreadRadius: 5,
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              badge.icon,
              style: const TextStyle(fontSize: 64),
            ).animate().scale(
                  begin: const Offset(0.0, 0.0),
                  end: const Offset(1.0, 1.0),
                  delay: 600.ms,
                  curve: Curves.elasticOut,
                ),
            const SizedBox(height: 12),
            Text(
              badge.name,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.white,
              ),
              textAlign: TextAlign.center,
            ).animate().fadeIn(delay: 800.ms).slideY(begin: 0.2, end: 0.0),
            const SizedBox(height: 4),
            Text(
              badge.description,
              style: TextStyle(
                fontSize: 12,
                color: AppColors.white.withOpacity(0.8),
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ).animate().fadeIn(delay: 1000.ms),
          ],
        ),
      ),
    );
  }

  /// Grid de badges (2-3 badges)
  Widget _buildBadgeGrid(List<BadgeData> badges) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: badges.length == 2 ? 2 : 3,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.0,
      ),
      itemCount: badges.length,
      itemBuilder: (context, index) {
        final badge = badges[index];
        return _buildBadgeCard(badge, index);
      },
    );
  }

  /// Scroll horizontal de badges (4+ badges)
  Widget _buildBadgeScroll(List<BadgeData> badges) {
    return SizedBox(
      height: 180,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: badges.length,
        separatorBuilder: (context, index) => const SizedBox(width: 16),
        itemBuilder: (context, index) {
          final badge = badges[index];
          return SizedBox(
            width: 140,
            child: _buildBadgeCard(badge, index),
          );
        },
      ),
    );
  }

  /// Card individual de badge
  Widget _buildBadgeCard(BadgeData badge, int index) {
    return Container(
      decoration: BoxDecoration(
        gradient: _getBadgeGradient(badge.rarity),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: _getBadgeColor(badge.rarity).withOpacity(0.3),
            blurRadius: 12,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            badge.icon,
            style: const TextStyle(fontSize: 40),
          ).animate().scale(
                begin: const Offset(0.0, 0.0),
                end: const Offset(1.0, 1.0),
                delay: Duration(milliseconds: 600 + (index * 200)),
                curve: Curves.elasticOut,
              ),
          const SizedBox(height: 8),
          Text(
            badge.name,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          )
              .animate()
              .fadeIn(delay: Duration(milliseconds: 800 + (index * 200))),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              badge.rarity.toUpperCase(),
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: AppColors.white,
              ),
            ),
          )
              .animate()
              .fadeIn(delay: Duration(milliseconds: 1000 + (index * 200))),
        ],
      ),
    )
        .animate()
        .fadeIn(delay: Duration(milliseconds: 400 + (index * 150)))
        .slideY(begin: 0.3, end: 0.0);
  }

  /// Estatísticas adicionais (XP, pontos)
  Widget _buildAdditionalStats() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.primary.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          if (widget.rewardData.xpGained > 0) ...[
            _buildStatRow(
              icon: FontAwesomeIcons.coins,
              label: 'XP Ganho',
              value: '+${widget.rewardData.xpGained}',
              color: AppColors.success,
              animation: LottieAnimations.coins(size: 20, repeat: true),
            ),
            if (widget.rewardData.pointsGained > 0) const SizedBox(height: 12),
          ],
          if (widget.rewardData.pointsGained > 0)
            _buildStatRow(
              icon: FontAwesomeIcons.star,
              label: 'Pontos Ganhos',
              value: '+${widget.rewardData.pointsGained}',
              color: AppColors.gold,
              animation: LottieAnimations.stars(size: 20, repeat: true),
            ),
        ],
      ),
    ).animate().fadeIn(delay: 1200.ms).slideY(begin: 0.2, end: 0.0);
  }

  /// Linha de estatística
  Widget _buildStatRow({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    Widget? animation,
  }) {
    return Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: animation ??
              FaIcon(
                icon,
                color: color,
                size: 16,
              ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ).animate().scale(
              begin: const Offset(0.0, 0.0),
              end: const Offset(1.0, 1.0),
              delay: 1400.ms,
              curve: Curves.elasticOut,
            ),
      ],
    );
  }

  /// Botões de ação
  Widget _buildActionButtons() {
    return Row(
      children: [
        // Botão principal (Continuar)
        Expanded(
          flex: 2,
          child: Container(
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.4),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ElevatedButton(
              onPressed: () {
                HapticFeedback.lightImpact();
                Navigator.of(context).pop();
                widget.onContinue?.call();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                foregroundColor: AppColors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: const Text(
                'Continuar',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),

        // Botões secundários
        if (widget.onViewProfile != null) ...[
          const SizedBox(width: 8),
          _buildSecondaryButton(
            icon: FontAwesomeIcons.user,
            onPressed: widget.onViewProfile!,
            color: AppColors.primary,
          ),
        ],

        if (widget.onViewBadges != null) ...[
          const SizedBox(width: 8),
          _buildSecondaryButton(
            icon: FontAwesomeIcons.trophy,
            onPressed: widget.onViewBadges!,
            color: AppColors.gold,
          ),
        ],
      ],
    ).animate().fadeIn(delay: 1600.ms).slideY(begin: 0.3, end: 0.0);
  }

  /// Botão secundário
  Widget _buildSecondaryButton({
    required IconData icon,
    required VoidCallback onPressed,
    required Color color,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: IconButton(
        onPressed: () {
          HapticFeedback.selectionClick();
          Navigator.of(context).pop();
          onPressed();
        },
        icon: FaIcon(icon, size: 18),
        color: color,
      ),
    );
  }

  /// Determina o tipo de confetti baseado na raridade dos badges
  ConfettiType _getConfettiType() {
    final hasLegendary = widget.rewardData.badgesEarned
        .any((badge) => badge.rarity == 'legendary');

    if (hasLegendary) {
      return ConfettiType.legendary;
    } else if (widget.rewardData.badgesEarned.length >= 3) {
      return ConfettiType.gold;
    } else {
      return ConfettiType.standard;
    }
  }

  /// Retorna gradiente baseado na raridade do badge
  LinearGradient _getBadgeGradient(String rarity) {
    final color = _getBadgeColor(rarity);
    return LinearGradient(
      colors: [
        color,
        color.withOpacity(0.7),
      ],
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
    );
  }

  /// Retorna cor baseada na raridade do badge
  Color _getBadgeColor(String rarity) {
    switch (rarity.toLowerCase()) {
      case 'legendary':
        return AppColors.gold;
      case 'epic':
        return AppColors.badgeEpic;
      case 'rare':
        return AppColors.badgeRare;
      case 'uncommon':
        return AppColors.success;
      default:
        return AppColors.badgeCommon;
    }
  }
}
