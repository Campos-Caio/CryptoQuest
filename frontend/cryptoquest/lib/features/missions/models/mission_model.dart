class Mission {
  final String id;
  final String title;
  final String description;
  final int rewardPoints;
  final String type;
  final String contentId;

  Mission({
    required this.id,
    required this.title,
    required this.description,
    required this.rewardPoints,
    required this.type,
    required this.contentId,
  });

  factory Mission.fromJson(Map<String, dynamic> json) {
    return Mission(
      // Usamos o operador '??' para fornecer um valor padrão
      // caso o campo não exista ou seja nulo no JSON.
      id: json['id'] ?? 'id_desconhecido',
      title: json['title'] ?? 'Missão Sem Título',
      description: json['description'] ?? 'Sem descrição disponível.',
      rewardPoints: json['reward_points'] ?? 0, // <-- Isso já resolve o problema do +0XP
      type: json['type'] ?? 'INDEFINIDO',
      contentId: json['content_id'] ?? '',
    );
  }
}