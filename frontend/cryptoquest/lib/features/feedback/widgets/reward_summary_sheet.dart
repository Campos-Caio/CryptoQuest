import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:confetti/confetti.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/feedback/models/reward_feedback_model.dart';
import 'package:cryptoquest/features/feedback/widgets/badge_unlock_card.dart';

/// Bottom sheet para exibir resumo de recompensas
///
/// Componente principal do sistema de feedback visual.
/// Exibe XP ganho, pontos, badges conquistados e outras informações
/// relevantes com animações e efeitos visuais apropriados.
class RewardSummarySheet extends StatefulWidget {
  final RewardFeedbackModel rewardData;
  final VoidCallback? onContinue;
  final VoidCallback? onViewProfile;
  final VoidCallback? onViewBadges;

  const RewardSummarySheet({
    super.key,
    required this.rewardData,
    this.onContinue,
    this.onViewProfile,
    this.onViewBadges,
  });

  /// Exibe o dialog centralizado com animação
  static Future<void> show({
    required BuildContext context,
    required RewardFeedbackModel rewardData,
    VoidCallback? onContinue,
    VoidCallback? onViewProfile,
    VoidCallback? onViewBadges,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false, // Impede fechar clicando fora
      builder: (context) => RewardSummarySheet(
        rewardData: rewardData,
        onContinue: onContinue,
        onViewProfile: onViewProfile,
        onViewBadges: onViewBadges,
      ),
    );
  }

  @override
  State<RewardSummarySheet> createState() => _RewardSummarySheetState();
}

class _RewardSummarySheetState extends State<RewardSummarySheet> {
  late ConfettiController _confettiController;

  @override
  void initState() {
    super.initState();

    _confettiController = ConfettiController(
      duration: const Duration(seconds: 3),
    );

    // Haptic feedback baseado no tipo de conquista
    _triggerHapticFeedback();

    // Iniciar confetti se for uma conquista significativa
    if (_shouldShowConfetti()) {
      Future.delayed(const Duration(milliseconds: 500), () {
        if (mounted) {
          _confettiController.play();
        }
      });
    }
  }

  void _triggerHapticFeedback() {
    if (widget.rewardData.isSuccess) {
      if (widget.rewardData.leveledUp) {
        // Feedback forte para level up
        HapticFeedback.heavyImpact();
      } else if (widget.rewardData.quizPercentage >= 90) {
        // Feedback médio para excelente desempenho
        HapticFeedback.mediumImpact();
      } else {
        // Feedback leve para sucesso
        HapticFeedback.lightImpact();
      }
    } else {
      // Feedback de erro
      HapticFeedback.vibrate();
    }
  }

  @override
  void dispose() {
    _confettiController.dispose();
    super.dispose();
  }

  bool _shouldShowConfetti() {
    final type = widget.rewardData.celebrationType;
    return type == CelebrationType.major ||
        type == CelebrationType.levelUp ||
        type == CelebrationType.legendary ||
        type == CelebrationType.multiple;
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final screenHeight = screenSize.height;
    final screenWidth = screenSize.width;
    final maxHeight = screenHeight * 0.85;

    // Calcular padding responsivo
    final horizontalPadding = (screenWidth * 0.05).clamp(16.0, 24.0);
    final verticalPadding = (screenHeight * 0.03).clamp(20.0, 28.0);

    return Stack(
      children: [
        // Confetti overlay
        Align(
          alignment: Alignment.topCenter,
          child: ConfettiWidget(
            confettiController: _confettiController,
            blastDirection: pi / 2,
            blastDirectionality: BlastDirectionality.explosive,
            emissionFrequency: 0.06,
            numberOfParticles: 15, // Reduzido de 20 para 15
            gravity: 0.3,
            colors: const [
              Color(0xFF2D5A3D), // Verde suave
              Color(0xFF6926C4), // Roxo principal
              Color(0xFF7F5AF0), // Roxo secundário
              Color(0xFF4A7C59), // Verde mais claro
              Color(0xFF8B6914), // Dourado suave
            ],
          ),
        ),

        // Conteúdo principal centralizado
        Center(
          child: Container(
            constraints: BoxConstraints(
              maxHeight: maxHeight,
              maxWidth: screenWidth > 600 ? 400 : screenWidth * 0.9,
            ),
            margin: EdgeInsets.symmetric(
              horizontal: horizontalPadding,
              vertical: verticalPadding,
            ),
            decoration: BoxDecoration(
              color: AppColors.background,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Conteúdo scrollável
                Flexible(
                  child: SingleChildScrollView(
                    padding: EdgeInsets.all(horizontalPadding),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Header compacto
                        _buildCompactHeader(),
                        const SizedBox(height: 20),

                        // Quiz + Level em linha (se aplicável)
                        if (widget.rewardData.quizPercentage > 0 ||
                            widget.rewardData.leveledUp)
                          _buildQuizLevelRow(),

                        const SizedBox(height: 16),

                        // XP + Pontos unificados
                        if (widget.rewardData.xpGained > 0 ||
                            widget.rewardData.pointsGained > 0)
                          _buildUnifiedStatsCard(),

                        const SizedBox(height: 16),

                        // Badges em scroll horizontal
                        if (widget.rewardData.badgesEarned.isNotEmpty)
                          _buildHorizontalBadges(),

                        const SizedBox(height: 16),

                        // Streak indicator compacto
                        if (widget.rewardData.streakDays > 0)
                          _buildCompactStreakCard(),

                        const SizedBox(height: 20),

                        // Botões de ação compactos
                        _buildCompactActionButtons(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          )
              .animate()
              .slideY(
                begin: 1.0,
                end: 0.0,
                duration: 400.ms,
                curve: Curves.easeOutCubic,
              )
              .fadeIn(duration: 300.ms),
        ),
      ],
    );
  }

  /// Header compacto sem card, apenas texto + ícone
  Widget _buildCompactHeader() {
    final isSuccess = widget.rewardData.isSuccess;
    final title = isSuccess ? 'Parabéns!' : 'Continue Tentando!';

    final screenWidth = MediaQuery.of(context).size.width;
    final iconSize = (screenWidth * 0.08).clamp(28.0, 36.0);
    final titleSize = (screenWidth * 0.06).clamp(22.0, 26.0);

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        FaIcon(
          isSuccess
              ? FontAwesomeIcons.champagneGlasses
              : FontAwesomeIcons.rotateRight,
          size: iconSize,
          color: isSuccess ? AppColors.success : AppColors.primary,
        )
            .animate(
              onPlay: (controller) => controller.repeat(
                reverse: true,
                period: const Duration(milliseconds: 1000),
                min: 0,
                max: 2,
              ),
            )
            .scale(
              begin: const Offset(1.0, 1.0),
              end: const Offset(1.15, 1.15),
            ),
        SizedBox(width: screenWidth * 0.03),
        Text(
          title,
          style: TextStyle(
            fontSize: titleSize,
            fontWeight: FontWeight.bold,
            color: AppColors.white,
            decoration: TextDecoration.none,
          ),
        ).animate().fadeIn(delay: 200.ms).slideX(
              begin: 0.3,
              end: 0.0,
            ),
      ],
    ).animate().fadeIn(duration: 300.ms);
  }

  /// Quiz e Level lado a lado
  Widget _buildQuizLevelRow() {
    final screenWidth = MediaQuery.of(context).size.width;
    final hasQuiz = widget.rewardData.quizPercentage > 0;
    final hasLevelUp = widget.rewardData.leveledUp;

    return Row(
      children: [
        if (hasQuiz)
          Expanded(
            child: _buildCompactQuizCard(),
          ),
        if (hasQuiz && hasLevelUp) SizedBox(width: screenWidth * 0.03),
        if (hasLevelUp)
          Expanded(
            child: _buildCompactLevelCard(),
          ),
      ],
    ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0.0);
  }

  /// Card compacto de resultado do quiz
  Widget _buildCompactQuizCard() {
    final percentage = widget.rewardData.quizPercentage;
    final isGood = percentage >= 70;
    final color = isGood ? AppColors.success : AppColors.warning;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          FaIcon(
            isGood
                ? FontAwesomeIcons.circleCheck
                : FontAwesomeIcons.triangleExclamation,
            size: 32,
            color: color,
          ),
          const SizedBox(height: 8),
          Text(
            '${percentage.toStringAsFixed(0)}%',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
              decoration: TextDecoration.none,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            isGood ? 'Excelente!' : 'Tente novamente',
            style: TextStyle(
              fontSize: 12,
              color: AppColors.onSurfaceVariant,
            ),
          ),
        ],
      ),
    ).animate().scale(delay: 150.ms);
  }

  /// Card compacto de level up
  Widget _buildCompactLevelCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          const FaIcon(
            FontAwesomeIcons.chartLine,
            size: 32,
            color: AppColors.white,
          ),
          const SizedBox(height: 8),
          Text(
            'Level ${widget.rewardData.currentLevel}',
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
              decoration: TextDecoration.none,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Subiu de nível!',
            style: TextStyle(
              fontSize: 12,
              color: AppColors.white,
            ),
          ),
        ],
      ),
    ).animate().scale(delay: 150.ms, curve: Curves.elasticOut).then().shimmer(
          duration: const Duration(milliseconds: 1500),
          color: Colors.white.withOpacity(0.3),
        );
  }

  /// Card unificado com XP e Pontos
  Widget _buildUnifiedStatsCard() {
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
          // XP Section
          if (widget.rewardData.xpGained > 0) ...[
            _buildXPRow(),
            const SizedBox(height: 12),
            _buildAnimatedXPBar(),
            const SizedBox(height: 16),
          ],

          // Pontos Section
          if (widget.rewardData.pointsGained > 0) _buildPointsRow(),
        ],
      ),
    ).animate().fadeIn(delay: 200.ms).scale(
          begin: const Offset(0.95, 0.95),
          end: const Offset(1.0, 1.0),
        );
  }

  /// Row de XP com valor atual e ganho
  Widget _buildXPRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            const FaIcon(
              FontAwesomeIcons.bolt,
              size: 20,
              color: AppColors.accent,
            ),
            const SizedBox(width: 8),
            Text(
              'XP',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.white,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${widget.rewardData.currentXP}/${_calculateXPForNextLevel()}',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.onSurfaceVariant,
                decoration: TextDecoration.none,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF2D5A3D), Color(0xFF4A7C59)],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '+${widget.rewardData.xpGained}',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
            ),
          ),
        )
            .animate(
              onPlay: (controller) => controller.repeat(
                reverse: true,
                period: const Duration(milliseconds: 800),
                min: 0,
                max: 2,
              ),
            )
            .scale(
              begin: const Offset(1.0, 1.0),
              end: const Offset(1.05, 1.05),
            ),
      ],
    );
  }

  /// Barra de progresso de XP animada
  Widget _buildAnimatedXPBar() {
    final progress = (widget.rewardData.currentXP / _calculateXPForNextLevel())
        .clamp(0.0, 1.0);
    final percentage = (progress * 100).toInt();

    return Column(
      children: [
        Stack(
          children: [
            // Barra de fundo
            Container(
              height: 8,
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            // Barra de progresso
            FractionallySizedBox(
              widthFactor: progress,
              child: Container(
                height: 8,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2D5A3D), Color(0xFF4A7C59)],
                  ),
                  borderRadius: BorderRadius.circular(4),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF4A7C59).withOpacity(0.5),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
              ),
            )
                .animate()
                .scaleX(
                  duration: const Duration(milliseconds: 1200),
                  curve: Curves.easeOutCubic,
                )
                .then()
                .shimmer(
                  duration: const Duration(milliseconds: 800),
                  color: Colors.white.withOpacity(0.3),
                ),
          ],
        ),
        const SizedBox(height: 6),
        Align(
          alignment: Alignment.centerRight,
          child: Text(
            '$percentage%',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.primary,
            ),
          ),
        ),
      ],
    );
  }

  /// Row de Pontos
  Widget _buildPointsRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            const FaIcon(
              FontAwesomeIcons.star,
              size: 20,
              color: AppColors.gold,
            ),
            const SizedBox(width: 8),
            Text(
              'Pontos',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.white,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${widget.rewardData.currentXP + widget.rewardData.pointsGained}',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.onSurfaceVariant,
                decoration: TextDecoration.none,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF8B6914), Color(0xFFB8860B)],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            '+${widget.rewardData.pointsGained}',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppColors.white,
            ),
          ),
        )
            .animate(
              onPlay: (controller) => controller.repeat(
                reverse: true,
                period: const Duration(milliseconds: 800),
                min: 0,
                max: 2,
              ),
            )
            .scale(
              begin: const Offset(1.0, 1.0),
              end: const Offset(1.05, 1.05),
            ),
      ],
    );
  }

  // Método antigo - não usado mais
  // ignore: unused_element
  Widget _buildQuizResult() {
    final percentage = widget.rewardData.quizPercentage;
    final isGood = percentage >= 70;
    // Usar cores mais suaves para melhor legibilidade
    final gradient = isGood
        ? const LinearGradient(
            colors: [Color(0xFF2D5A3D), Color(0xFF4A7C59)], // Verde mais suave
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          )
        : AppColors.primaryGradient;

    final screenWidth = MediaQuery.of(context).size.width;
    final resultPadding = (screenWidth * 0.05).clamp(16.0, 20.0);
    final iconSize = (screenWidth * 0.07).clamp(24.0, 28.0);
    final percentageSize = (screenWidth * 0.06).clamp(20.0, 24.0);

    return Container(
      padding: EdgeInsets.all(resultPadding),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: (isGood ? AppColors.success : AppColors.primary)
                .withOpacity(0.3),
            blurRadius: 10,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(
              isGood ? Icons.check_circle : Icons.info,
              color: AppColors.white,
              size: iconSize,
            ),
          ),
          SizedBox(width: resultPadding * 0.8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Resultado',
                style: TextStyle(
                  fontSize: (screenWidth * 0.035).clamp(12.0, 14.0),
                  color: const Color(
                      0xFFFFFFFF), // Branco puro para melhor contraste
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${percentage.toStringAsFixed(0)}% de acertos',
                style: TextStyle(
                  fontSize: percentageSize,
                  fontWeight: FontWeight.bold,
                  color: AppColors.white,
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 100.ms).scale();
  }

  /// Badges em scroll horizontal
  Widget _buildHorizontalBadges() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 12),
          child: Row(
            children: [
              const FaIcon(
                FontAwesomeIcons.trophy,
                size: 20,
                color: AppColors.gold,
              ),
              const SizedBox(width: 8),
              Text(
                'Badges Conquistados',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.white,
                ),
              ),
            ],
          ),
        ),
        SizedBox(
          height: 140,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: widget.rewardData.badgesEarned.length,
            separatorBuilder: (context, index) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final badge = widget.rewardData.badgesEarned[index];
              return BadgeUnlockCard(
                badge: badge,
                delay: Duration(milliseconds: 300 + (index * 150)),
                onTap: () => _showBadgeDetails(badge),
              );
            },
          ),
        ),
      ],
    ).animate().fadeIn(delay: 250.ms).slideX(begin: 0.2, end: 0.0);
  }

  /// Streak card compacto
  Widget _buildCompactStreakCard() {
    final days = widget.rewardData.streakDays;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Row(
        children: [
          FaIcon(
            FontAwesomeIcons.fire,
            size: 28,
            color: Colors.orange[700],
          )
              .animate(
                onPlay: (controller) => controller.repeat(
                  reverse: true,
                  period: const Duration(milliseconds: 800),
                  min: 0,
                  max: 2,
                ),
              )
              .scale(
                begin: const Offset(1.0, 1.0),
                end: const Offset(1.1, 1.1),
              ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$days dias consecutivos!',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[700],
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Continue assim! 🔥',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms).slideX(begin: -0.2, end: 0.0);
  }

  /// Botões de ação compactos
  Widget _buildCompactActionButtons() {
    return Row(
      children: [
        // Botão principal expandido
        Expanded(
          flex: 2,
          child: Container(
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(12),
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
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
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

        // Botões secundários como ícones
        if (widget.onViewProfile != null) ...[
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.primary.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: IconButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                Navigator.of(context).pop();
                widget.onViewProfile?.call();
              },
              icon: const FaIcon(FontAwesomeIcons.user, size: 20),
              color: AppColors.primary,
              tooltip: 'Ver Perfil',
            ),
          ),
        ],

        if (widget.onViewBadges != null &&
            widget.rewardData.badgesEarned.isNotEmpty) ...[
          const SizedBox(width: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.gold.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: IconButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                Navigator.of(context).pop();
                widget.onViewBadges?.call();
              },
              icon: const FaIcon(FontAwesomeIcons.trophy, size: 20),
              color: AppColors.gold,
              tooltip: 'Ver Badges',
            ),
          ),
        ],
      ],
    ).animate().fadeIn(delay: 350.ms).slideY(begin: 0.2, end: 0.0);
  }

  // Método antigo - não usado mais
  // ignore: unused_element
  Widget _buildLevelUpCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [
            Color(0xFF6A11CB),
            Color(0xFF2575FC),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2575FC).withOpacity(0.4),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.trending_up,
            size: 40,
            color: Colors.white,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'LEVEL UP!',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'Nível ${widget.rewardData.previousLevel} → ${widget.rewardData.currentLevel}',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(delay: 300.ms)
        .scale(curve: Curves.elasticOut)
        .then()
        .shimmer(
          duration: const Duration(milliseconds: 2000),
          color: Colors.white.withOpacity(0.5),
        );
  }

  // Método antigo - não usado mais
  // ignore: unused_element
  Widget _buildStreakCard() {
    final days = widget.rewardData.streakDays;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.orange.withOpacity(0.2),
            Colors.deepOrange.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.orange.withOpacity(0.5),
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.local_fire_department,
            size: 32,
            color: Colors.orange[700],
          )
              .animate(
                onPlay: (controller) => controller.repeat(
                  reverse: true,
                  period: const Duration(milliseconds: 800),
                  min: 0,
                  max: 4, // Limitar a 4 ciclos
                ),
              )
              .scale(
                begin: const Offset(1.0, 1.0),
                end: const Offset(1.15, 1.15), // Reduzir intensidade
              ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Sequência Ativa',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
                Text(
                  '$days dias consecutivos!',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[700],
                  ),
                ),
                const Text(
                  'Continue assim para desbloquear badges especiais',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppColors.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 400.ms).slideX(
          begin: -0.2,
          end: 0.0,
        );
  }

  // Método antigo - não usado mais
  // ignore: unused_element
  Widget _buildActionButtons() {
    return Column(
      children: [
        // Botão principal (Continuar)
        SizedBox(
          width: double.infinity,
          child: Container(
            decoration: BoxDecoration(
              gradient: AppColors.primaryGradient,
              borderRadius: BorderRadius.circular(16),
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
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: const Text(
                'Continuar',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Botões secundários
        Row(
          children: [
            if (widget.onViewProfile != null)
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: AppColors.primary.withOpacity(0.6),
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.2),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: OutlinedButton.icon(
                    onPressed: () {
                      HapticFeedback.selectionClick();
                      Navigator.of(context).pop();
                      widget.onViewProfile?.call();
                    },
                    icon: const Icon(Icons.person, size: 20),
                    label: const Text(
                      'Perfil',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.white,
                      backgroundColor: AppColors.primary.withOpacity(0.3),
                      side: BorderSide.none,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                  ),
                ),
              ),
            if (widget.onViewProfile != null && widget.onViewBadges != null)
              const SizedBox(width: 12),
            if (widget.onViewBadges != null &&
                widget.rewardData.badgesEarned.isNotEmpty)
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: const Color(0xFF8B6914).withOpacity(0.6),
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF8B6914).withOpacity(0.2),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: OutlinedButton.icon(
                    onPressed: () {
                      HapticFeedback.selectionClick();
                      Navigator.of(context).pop();
                      widget.onViewBadges?.call();
                    },
                    icon: const Icon(Icons.emoji_events, size: 20),
                    label: const Text(
                      'Badges',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.white,
                      backgroundColor: const Color(0xFF8B6914).withOpacity(0.3),
                      side: BorderSide.none,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ],
    ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.2, end: 0.0);
  }

  void _showBadgeDetails(BadgeData badge) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Text(
              badge.icon,
              style: const TextStyle(fontSize: 32),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                badge.name,
                style: const TextStyle(fontSize: 18),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              badge.description,
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 6,
              ),
              decoration: BoxDecoration(
                color: Color(
                  int.parse(badge.rarityColor.replaceFirst('#', '0xFF')),
                ).withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                'Raridade: ${badge.rarity.toUpperCase()}',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Color(
                    int.parse(badge.rarityColor.replaceFirst('#', '0xFF')),
                  ),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Fechar'),
          ),
        ],
      ),
    );
  }

  int _calculateXPForNextLevel() {
    // Sistema de níveis rebalanceado
    final currentLevel = widget.rewardData.currentLevel;
    final currentXP = widget.rewardData.currentXP;

    // Definir XP necessário para cada nível (baseado no backend)
    final levelRequirements = {
      1: 0, // Nível 1: 0 XP
      2: 500, // Nível 2: 500 XP total
      3: 1000, // Nível 3: 1000 XP total
      4: 1500, // Nível 4: 1500 XP total
      5: 2000, // Nível 5: 2000 XP total
      6: 2500, // Nível 6: 2500 XP total
      7: 3000, // Nível 7: 3000 XP total
      8: 3500, // Nível 8: 3500 XP total
      9: 4000, // Nível 9: 4000 XP total
      10: 4500, // Nível 10: 4500 XP total
      11: 5250, // Nível 11: 5250 XP total
      12: 6000, // Nível 12: 6000 XP total
      13: 6750, // Nível 13: 6750 XP total
      14: 7500, // Nível 14: 7500 XP total
      15: 8250, // Nível 15: 8250 XP total
      16: 9000, // Nível 16: 9000 XP total
      17: 9750, // Nível 17: 9750 XP total
      18: 10500, // Nível 18: 10500 XP total
      19: 11250, // Nível 19: 11250 XP total
      20: 12000, // Nível 20: 12000 XP total
      21: 13000, // Nível 21: 13000 XP total
      22: 14000, // Nível 22: 14000 XP total
      23: 15000, // Nível 23: 15000 XP total
      24: 16000, // Nível 24: 16000 XP total
      25: 17000, // Nível 25: 17000 XP total
    };

    // Encontrar o próximo nível
    int nextLevel = currentLevel + 1;
    while (nextLevel <= 25 && levelRequirements[nextLevel]! <= currentXP) {
      nextLevel++;
    }

    // Se chegou ao nível máximo, retorna o XP atual
    if (nextLevel > 25) {
      return currentXP;
    }

    return levelRequirements[nextLevel]!;
  }
}
