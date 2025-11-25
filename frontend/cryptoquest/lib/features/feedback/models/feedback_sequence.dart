import 'package:cryptoquest/features/feedback/models/feedback_event.dart';

/// Representa uma sequência de eventos de feedback
///
/// Gerencia a ordem e timing de múltiplos eventos de feedback
/// que devem ser exibidos em sequência
class FeedbackSequence {
  final List<FeedbackEvent> events;
  final Duration totalDuration;
  final bool shouldShowProgress;
  final String? title;

  const FeedbackSequence({
    required this.events,
    required this.totalDuration,
    this.shouldShowProgress = false,
    this.title,
  });

  /// Cria sequência vazia
  factory FeedbackSequence.empty() {
    return const FeedbackSequence(
      events: [],
      totalDuration: Duration.zero,
    );
  }

  /// Cria sequência com um único evento
  factory FeedbackSequence.single(FeedbackEvent event) {
    return FeedbackSequence(
      events: [event],
      totalDuration: event.delay + event.type.animationDuration,
    );
  }

  /// Cria sequência de múltiplos eventos
  factory FeedbackSequence.multiple(List<FeedbackEvent> events) {
    Duration totalDuration = Duration.zero;

    for (final event in events) {
      final eventDuration = event.delay + event.type.animationDuration;
      totalDuration = Duration(
        milliseconds:
            totalDuration.inMilliseconds + eventDuration.inMilliseconds,
      );
    }

    return FeedbackSequence(
      events: events,
      totalDuration: totalDuration,
      shouldShowProgress: events.length > 1,
    );
  }

  /// Cria sequência de quiz com múltiplas conquistas
  factory FeedbackSequence.quizWithMultipleAchievements({
    required FeedbackEvent quizEvent,
    required List<FeedbackEvent> achievementEvents,
  }) {
    final allEvents = [quizEvent, ...achievementEvents];
    return FeedbackSequence.multiple(allEvents);
  }

  /// Cria sequência de falha
  factory FeedbackSequence.failure(FeedbackEvent failureEvent) {
    return FeedbackSequence.single(failureEvent);
  }

  /// Cria sequência de conquista lendária
  factory FeedbackSequence.legendary({
    required FeedbackEvent legendaryEvent,
    List<FeedbackEvent>? additionalEvents,
  }) {
    final events = [legendaryEvent];
    if (additionalEvents != null) {
      events.addAll(additionalEvents);
    }
    return FeedbackSequence.multiple(events);
  }

  /// Retorna se a sequência está vazia
  bool get isEmpty => events.isEmpty;

  /// Retorna se a sequência tem apenas um evento
  bool get isSingle => events.length == 1;

  /// Retorna se a sequência tem múltiplos eventos
  bool get isMultiple => events.length > 1;

  /// Retorna o primeiro evento
  FeedbackEvent? get firstEvent => events.isNotEmpty ? events.first : null;

  /// Retorna o último evento
  FeedbackEvent? get lastEvent => events.isNotEmpty ? events.last : null;

  /// Retorna se a sequência contém eventos de sucesso
  bool get hasSuccessEvents => events.any((event) => event.isSuccess);

  /// Retorna se a sequência contém eventos de falha
  bool get hasFailureEvents => events.any((event) => event.isFailure);

  /// Retorna se a sequência é apenas de sucesso
  bool get isAllSuccess =>
      events.isNotEmpty && events.every((event) => event.isSuccess);

  /// Retorna se a sequência é apenas de falha
  bool get isAllFailure =>
      events.isNotEmpty && events.every((event) => event.isFailure);

  /// Retorna se a sequência é mista (sucesso e falha)
  bool get isMixed => hasSuccessEvents && hasFailureEvents;

  /// Retorna o número de eventos
  int get eventCount => events.length;

  /// Retorna eventos de um tipo específico
  List<FeedbackEvent> getEventsOfType(FeedbackType type) {
    return events.where((event) => event.type == type).toList();
  }

  /// Retorna eventos de sucesso
  List<FeedbackEvent> get successEvents {
    return events.where((event) => event.isSuccess).toList();
  }

  /// Retorna eventos de falha
  List<FeedbackEvent> get failureEvents {
    return events.where((event) => event.isFailure).toList();
  }

  /// Retorna eventos que devem mostrar confetti
  List<FeedbackEvent> get confettiEvents {
    return events.where((event) => event.type.shouldShowConfetti).toList();
  }

  /// Adiciona um evento à sequência
  FeedbackSequence addEvent(FeedbackEvent event) {
    final newEvents = List<FeedbackEvent>.from(events)..add(event);
    return FeedbackSequence.multiple(newEvents);
  }

  /// Adiciona múltiplos eventos à sequência
  FeedbackSequence addEvents(List<FeedbackEvent> newEvents) {
    final allEvents = List<FeedbackEvent>.from(events)..addAll(newEvents);
    return FeedbackSequence.multiple(allEvents);
  }

  /// Remove eventos de um tipo específico
  FeedbackSequence removeEventsOfType(FeedbackType type) {
    final filteredEvents = events.where((event) => event.type != type).toList();
    return FeedbackSequence.multiple(filteredEvents);
  }

  /// Filtra eventos por condição
  FeedbackSequence where(bool Function(FeedbackEvent) test) {
    final filteredEvents = events.where(test).toList();
    return FeedbackSequence.multiple(filteredEvents);
  }

  /// Retorna uma cópia da sequência com título
  FeedbackSequence withTitle(String title) {
    return FeedbackSequence(
      events: events,
      totalDuration: totalDuration,
      shouldShowProgress: shouldShowProgress,
      title: title,
    );
  }

  /// Retorna uma cópia da sequência com progresso habilitado
  FeedbackSequence withProgress(bool showProgress) {
    return FeedbackSequence(
      events: events,
      totalDuration: totalDuration,
      shouldShowProgress: showProgress,
      title: title,
    );
  }

  /// Calcula o delay acumulado até um evento específico
  Duration getDelayUntilEvent(int eventIndex) {
    if (eventIndex < 0 || eventIndex >= events.length) {
      return Duration.zero;
    }

    Duration totalDelay = Duration.zero;
    for (int i = 0; i < eventIndex; i++) {
      final event = events[i];
      totalDelay = Duration(
        milliseconds: totalDelay.inMilliseconds +
            event.delay.inMilliseconds +
            event.type.animationDuration.inMilliseconds,
      );
    }

    return totalDelay;
  }

  /// Retorna informações sobre a sequência
  Map<String, dynamic> toMap() {
    return {
      'eventCount': eventCount,
      'totalDuration': totalDuration.inMilliseconds,
      'shouldShowProgress': shouldShowProgress,
      'title': title,
      'hasSuccessEvents': hasSuccessEvents,
      'hasFailureEvents': hasFailureEvents,
      'isAllSuccess': isAllSuccess,
      'isAllFailure': isAllFailure,
      'isMixed': isMixed,
      'events': events
          .map((e) => {
                'type': e.type.toString(),
                'delay': e.delay.inMilliseconds,
                'shouldWaitForPrevious': e.shouldWaitForPrevious,
                'actions': e.actions.map((a) => a.toString()).toList(),
              })
          .toList(),
    };
  }

  @override
  String toString() {
    return 'FeedbackSequence('
        'events: $eventCount, '
        'duration: ${totalDuration.inMilliseconds}ms, '
        'progress: $shouldShowProgress'
        '${title != null ? ', title: $title' : ''}'
        ')';
  }
}
