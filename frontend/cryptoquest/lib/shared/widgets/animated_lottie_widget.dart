import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

/// Widget wrapper para animações Lottie com suporte a cores customizadas
/// e controle de reprodução
class AnimatedLottieWidget extends StatelessWidget {
  final String assetPath;
  final double? width;
  final double? height;
  final bool repeat;
  final AnimationController? controller;
  final VoidCallback? onComplete;
  final BoxFit fit;
  final bool enableColorReplacement;

  const AnimatedLottieWidget({
    super.key,
    required this.assetPath,
    this.width,
    this.height,
    this.repeat = true,
    this.controller,
    this.onComplete,
    this.fit = BoxFit.contain,
    this.enableColorReplacement = true,
  });

  @override
  Widget build(BuildContext context) {
    return Lottie.asset(
      assetPath,
      width: width,
      height: height,
      fit: fit,
      repeat: repeat,
      controller: controller,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: Colors.red.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.error_outline,
            size: (width ?? height ?? 120) * 0.6,
            color: Colors.red,
          ),
        );
      },
      onLoaded: (composition) {
        if (controller != null) {
          controller!.duration = composition.duration;
          if (repeat) {
            if (controller!.status == AnimationStatus.dismissed) {
              controller!.repeat();
            } else {
              controller!.reset();
              controller!.repeat();
            }
          } else {
            controller!.forward().whenComplete(() {
              if (onComplete != null) {
                onComplete!();
              }
            });
          }
        }
      },
      // Substituir cores da animação pelas cores do app (se habilitado)
      delegates: enableColorReplacement
          ? LottieDelegates(
              values: [
                // Substituir cores genéricas pelas cores do tema
                ValueDelegate.color(const [
                  '**',
                  'Fill 1',
                ], value: AppColors.primary),
                ValueDelegate.color(const [
                  '**',
                  'Stroke 1',
                ], value: AppColors.accent),
              ],
            )
          : null,
      frameBuilder: (context, child, frame) {
        if (frame == null) {
          // Se não há frame, mostrar um indicador de carregamento
          return Container(
            width: width,
            height: height,
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        return child;
      },
    );
  }
}

/// Presets de caminhos para animações Lottie
/// Mapeamento dos arquivos baixados pelo usuário
class LottieAssets {
  // Celebration
  static const String trophyWin = 'assets/animations/lottie/Trophy.json';
  static const String levelUp = 'assets/animations/lottie/level up.json';
  static const String confettiBurst =
      'assets/animations/lottie/confetti_burst.json'; // Não disponível

  // Feedback
  static const String successCheck = 'assets/animations/lottie/success.json';
  static const String errorCross =
      'assets/animations/lottie/Error Occurred!.json';
  static const String loadingCrypto =
      'assets/animations/lottie/loading_crypto.json'; // Não disponível

  // Rewards
  static const String coinsFalling = 'assets/animations/lottie/Money rain.json';
  static const String starsSparkle =
      'assets/animations/lottie/Star rating.json';
  static const String badgeUnlock = 'assets/animations/lottie/Rewards.json';

  // Streak
  static const String fireStreak = 'assets/animations/lottie/Streak Fire.json';
  static const String targetHit =
      'assets/animations/lottie/target_hit.json'; // Não disponível
}

/// Widgets pré-configurados para casos de uso comuns
class LottieAnimations {
  /// Animação de troféu para conquistas
  static Widget trophy({
    double size = 150,
    AnimationController? controller,
    VoidCallback? onComplete,
  }) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.trophyWin,
      width: size,
      height: size,
      repeat: false,
      controller: controller,
      onComplete: onComplete,
    );
  }

  /// Animação de moedas caindo (XP)
  static Widget coins({double size = 60, bool repeat = true}) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.coinsFalling,
      width: size,
      height: size,
      repeat: repeat,
    );
  }

  /// Animação de estrelas brilhando (Pontos)
  static Widget stars({double size = 60, bool repeat = true}) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.starsSparkle,
      width: size,
      height: size,
      repeat: repeat,
    );
  }

  /// Checkmark de sucesso
  static Widget successCheck({
    double size = 120,
    AnimationController? controller,
    VoidCallback? onComplete,
  }) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.successCheck,
      width: size,
      height: size,
      repeat: false,
      controller: controller,
      onComplete: onComplete,
    );
  }

  /// X de erro
  static Widget errorCross({
    double size = 120,
    AnimationController? controller,
    VoidCallback? onComplete,
    bool repeat = false,
  }) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.errorCross,
      width: size,
      height: size,
      repeat: repeat,
      controller: controller,
      onComplete: onComplete,
      enableColorReplacement: false,
    );
  }

  /// Level up épico
  static Widget levelUp({
    double size = 200,
    AnimationController? controller,
    VoidCallback? onComplete,
  }) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.levelUp,
      width: size,
      height: size,
      repeat: false,
      controller: controller,
      onComplete: onComplete,
    );
  }

  /// Badge sendo desbloqueado
  static Widget badgeUnlock({
    double size = 180,
    AnimationController? controller,
    VoidCallback? onComplete,
  }) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.badgeUnlock,
      width: size,
      height: size,
      repeat: false,
      controller: controller,
      onComplete: onComplete,
    );
  }

  /// Fogo de streak
  static Widget fireStreak({double size = 40, bool repeat = true}) {
    return AnimatedLottieWidget(
      assetPath: LottieAssets.fireStreak,
      width: size,
      height: size,
      repeat: repeat,
    );
  }
}
