import 'dart:math';
import 'package:flutter/material.dart';
import 'package:confetti/confetti.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

/// Gerenciador aprimorado de confetti com presets para diferentes tipos de conquistas
class EnhancedConfettiController {
  late ConfettiController _controller;

  EnhancedConfettiController() {
    _controller = ConfettiController(
      duration: const Duration(seconds: 3),
    );
  }

  /// Confete padrão para conquistas normais
  void showStandard() {
    _controller.play();
  }

  /// Confete intenso para level up
  void showLevelUp() {
    _controller.play();
  }

  /// Confete lendário (mais longo)
  void showLegendary() {
    _controller.duration = const Duration(seconds: 5);
    _controller.play();
  }

  void stop() {
    _controller.stop();
  }

  void dispose() {
    _controller.dispose();
  }

  ConfettiController get controller => _controller;
}

/// Widget de confetti com presets customizados
class EnhancedConfettiWidget extends StatelessWidget {
  final ConfettiController controller;
  final ConfettiType type;
  final List<Color>? colors;
  final int numberOfParticles;
  final double gravity;

  const EnhancedConfettiWidget({
    super.key,
    required this.controller,
    this.type = ConfettiType.standard,
    this.colors,
    this.numberOfParticles = 20,
    this.gravity = 0.3,
  });

  List<Color> get _effectiveColors {
    if (colors != null) return colors!;

    switch (type) {
      case ConfettiType.standard:
        return [
          AppColors.primary,
          AppColors.secondary,
          AppColors.accent,
        ];
      case ConfettiType.gold:
        return [
          AppColors.gold,
          AppColors.warning,
          Colors.amber,
          const Color(0xFFFFD700),
        ];
      case ConfettiType.levelUp:
        return [
          AppColors.primary,
          AppColors.accent,
          AppColors.gold,
          Colors.white,
        ];
      case ConfettiType.legendary:
        return [
          AppColors.gold,
          const Color(0xFFFFD700),
          Colors.amber,
          Colors.white,
        ];
    }
  }

  int get _effectiveParticles {
    switch (type) {
      case ConfettiType.standard:
        return numberOfParticles;
      case ConfettiType.gold:
        return numberOfParticles + 5;
      case ConfettiType.levelUp:
        return numberOfParticles + 10;
      case ConfettiType.legendary:
        return numberOfParticles + 15;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ConfettiWidget(
      confettiController: controller,
      blastDirection: pi / 2, // Para baixo
      blastDirectionality: BlastDirectionality.explosive,
      emissionFrequency: type == ConfettiType.legendary ? 0.05 : 0.06,
      numberOfParticles: _effectiveParticles,
      gravity: gravity,
      colors: _effectiveColors,
      maxBlastForce: type == ConfettiType.legendary ? 30 : 20,
      minBlastForce: type == ConfettiType.legendary ? 15 : 10,
    );
  }
}

/// Tipos de confetti com intensidades diferentes
enum ConfettiType {
  standard, // Conquista normal
  gold, // Badge raro
  levelUp, // Level up
  legendary, // Badge lendário
}

/// Widget wrapper que facilita o uso do confetti
class ConfettiOverlay extends StatefulWidget {
  final Widget child;
  final ConfettiType type;
  final bool autoPlay;
  final Duration delay;

  const ConfettiOverlay({
    super.key,
    required this.child,
    this.type = ConfettiType.standard,
    this.autoPlay = false,
    this.delay = const Duration(milliseconds: 500),
  });

  @override
  State<ConfettiOverlay> createState() => ConfettiOverlayState();
}

class ConfettiOverlayState extends State<ConfettiOverlay> {
  late EnhancedConfettiController _confettiController;

  @override
  void initState() {
    super.initState();
    _confettiController = EnhancedConfettiController();

    if (widget.autoPlay) {
      Future.delayed(widget.delay, () {
        if (mounted) {
          play();
        }
      });
    }
  }

  void play() {
    switch (widget.type) {
      case ConfettiType.standard:
        _confettiController.showStandard();
        break;
      case ConfettiType.gold:
        _confettiController.showStandard();
        break;
      case ConfettiType.levelUp:
        _confettiController.showLevelUp();
        break;
      case ConfettiType.legendary:
        _confettiController.showLegendary();
        break;
    }
  }

  @override
  void dispose() {
    _confettiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        widget.child,
        Align(
          alignment: Alignment.topCenter,
          child: EnhancedConfettiWidget(
            controller: _confettiController.controller,
            type: widget.type,
          ),
        ),
      ],
    );
  }
}
