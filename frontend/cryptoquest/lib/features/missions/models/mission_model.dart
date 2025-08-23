class Mission {
  final String id;
  final String title;
  final String description;
  final int rewardPoints;
  final String type;

  Mission(
      {required this.id,
      required this.title,
      required this.description,
      required this.rewardPoints,
      required this.type});
      
  /// Factory constructor para criar uma Mission a partir de um JSON.
  factory Mission.fromJson(Map<String, dynamic> json){
    return Mission(
      id: json['id'],
      title: json['title'], 
      description: json['description'], 
      rewardPoints: json['rewardPoints'], 
      type: json['type']
    ); 
  }
}
