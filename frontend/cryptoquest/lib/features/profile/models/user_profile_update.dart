class UserProfileUpdate {
  final String? name;
  final String? bio;
  final String? avatarUrl;

  UserProfileUpdate({this.avatarUrl, this.bio, this.name});

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {};
    if (name != null) data['name'] = name;
    if (bio != null) data['bio'] = bio;
    if (avatarUrl != null) data['avatarUrl'] = avatarUrl;
    return data; 
  }
}
