import 'dart:convert';
import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;

class AuthService {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  final String _backendUrl = 'http://10.0.2.2:8000/auth'; // URL base da autenticação

  // Retorna o UserProfile após o login
  Future<UserProfile> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email, password: password);

    if (userCredential.user == null) throw Exception("Usuário não encontrado!");

    final idToken = await userCredential.user!.getIdToken();
    if (idToken == null) throw Exception("Não foi possível obter o Token!");

    return _authenticateWithBackend(idToken);
  }
  
  // Retorna o UserProfile após o login com Google
  Future<UserProfile> signInWithGoogle() async {
    final googleUser = await _googleSignIn.signIn();
    if (googleUser == null) throw Exception("Login com Google cancelado!");

    final googleAuth = await googleUser.authentication;
    final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken, idToken: googleAuth.idToken);

    final userCredential = await _firebaseAuth.signInWithCredential(credential);
    if (userCredential.user == null) throw Exception('Usuário não encontrado no Firebase');

    final idToken = await userCredential.user!.getIdToken();
    if (idToken == null) throw Exception("Não foi possível obter o Token!");

    return _authenticateWithBackend(idToken);
  }

  // Metodo com retorno do User profile
  Future<UserProfile> _authenticateWithBackend(String idToken) async {
    final response = await http.post(
      Uri.parse('$_backendUrl/authenticate'),
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer $idToken'
      },
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      // O backend retorna um objeto AuthSuccess que contém o user_profile
      return UserProfile.fromJson(responseData['user_profile']);
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception("Erro do servidor: ${errorData['detail'] ?? 'Erro desconhecido'}");
    }
  }

  Future<void> signOut() async {
    await _firebaseAuth.signOut();
    await _googleSignIn.signOut();
  }
}