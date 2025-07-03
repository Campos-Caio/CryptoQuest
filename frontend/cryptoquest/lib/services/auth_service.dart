import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;

class AuthService {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  final String _backendUrl = 'http://10.0.2.2:8000/auth/authenticate';

  // Metodo de Login com email e senha
  Future<void> signInWithEmailAndPassword(
      {required String email, required String password}) async {
    final userCredential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email, password: password);

    if (userCredential.user == null) {
      throw Exception("Usuario nao encontrado!");
    }

    // 2. Obtem o ID Token
    final idToken = await userCredential.user!.getIdToken(true);
    if (idToken == null) {
      throw Exception("Nao foi possivel encontrar o Token!");
    }

    // 3. Autentica o ID Token no backend
    await _authenticateWithBackend(idToken);
  }

  // Metodo para Login com google
  Future<void> signInWithGoogle() async {
    // 1. Inicia o login com google
    final googleUser = await _googleSignIn.signIn();
    if (googleUser == null) {
      throw Exception("Login com google cancelado pelo usuario!");
    }

    // 2. Obtem as credenciais do usuario
    final googleAuth = await googleUser.authentication;
    final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken, idToken: googleAuth.idToken);

    // 3. Autentica no Firebase
    final userCredential = await _firebaseAuth.signInWithCredential(credential);
    if (userCredential.user == null) {
      throw Exception('Usuario nao encontrado no Firebase');
    }

    // 4. Obtem o token
    final idToken = await userCredential.user!.getIdToken(true);
    if (idToken == null) {
      throw Exception("Nao foi possivel encontrar o Token!");
    }

    // 5. Autentica no backend
    await _authenticateWithBackend(idToken);
  }

  // Metodo para autenticar o token no backend
  Future<void> _authenticateWithBackend(String idToken) async {
    final response =
        await http.post(Uri.parse(_backendUrl), headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
      'Authorization': 'Bearer $idToken'
    }); 

    if(response.statusCode != 200){
      final errorData = jsonDecode(response.body);
      // Lanca um erro com a mensagem do backend 
      throw Exception("Erro interno no servidor: ${errorData['detail'] ?? 'Erro desconhecido!'}"); 
    }
  }

  Future<void> signOut() async{
    await _firebaseAuth.signOut();
    await _googleSignIn.signOut();
  }
}
