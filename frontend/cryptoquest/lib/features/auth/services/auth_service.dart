import 'dart:convert';
import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:cryptoquest/features/profile/models/user_profile_update.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http;
import 'package:cryptoquest/core/config/app_config.dart';

class AuthService {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  /// Cadastra um novo usuário no backend e, em seguida, realiza o login
  /// para obter o perfil completo e o token de autenticação.
  Future<UserProfile> signUpWithEmailAndPassword({
    required String name,
    required String email,
    required String password,
  }) async {
    // 1. Faz a chamada para o endpoint de registro que criamos no backend.
    final response = await http.post(
      Uri.parse(
          '${AppConfig.baseUrl}/auth/register'), // Chama o endpoint de registro
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
      }),
    );

    // 2. Verifica se o backend criou o usuário com sucesso.
    if (response.statusCode == 201) {
      // 201 Created
      // 3. Se o cadastro deu certo, o usuário agora existe.
      //    A maneira mais robusta de obter o estado completo (token, perfil)
      //    é simplesmente realizar o login com as credenciais que acabamos de usar.
      return signInWithEmailAndPassword(email: email, password: password);
    } else {
      // Se o backend retornou um erro (ex: e-mail já existe), lança uma exceção.
      final errorData = jsonDecode(response.body);
      throw Exception(
          "Falha ao cadastrar: ${errorData['detail'] ?? 'Erro desconhecido'}");
    }
  }

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
    if (userCredential.user == null)
      throw Exception('Usuário não encontrado no Firebase');

    final idToken = await userCredential.user!.getIdToken();
    if (idToken == null) throw Exception("Não foi possível obter o Token!");

    return _authenticateWithBackend(idToken);
  }

  // Metodo com retorno do User profile
  Future<UserProfile> _authenticateWithBackend(String idToken) async {
    final response = await http.post(
      Uri.parse('${AppConfig.baseUrl}/auth/authenticate'),
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer $idToken'
      },
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);

      // O backend retorna um objeto AuthSuccess que contém o user_profile
      final userProfileData = responseData['user_profile'];

      return UserProfile.fromJson(userProfileData);
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(
          "Erro do servidor: ${errorData['detail'] ?? 'Erro desconhecido'}");
    }
  }

  Future<void> signOut() async {
    await _firebaseAuth.signOut();
    await _googleSignIn.signOut();
  }

  Future<UserProfile> updateUserProfile(

      /// Atualiza os dados do perfil do usuario no backend.
      ///
      /// Args:
      ///   token (string): O token de autenticacao do usuario.
      ///   updateModel(UserProfileUpdate): O objeto com novos dados do perfil.
      /// Returns:
      ///   UserProfile: O perfil de usuariop atualizado, retornado pelo backend.
      String token,
      UserProfileUpdate updateModel) async {
    final response = await http.put(
      Uri.parse('${AppConfig.baseUrl}/users/me'),
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer $token'
      },
      body: jsonEncode(updateModel.toJson()),
    );

    if (response.statusCode == 200) {
      return UserProfile.fromJson(jsonDecode(response.body));
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception('Falha ao autorizar o perfil: ${errorData['detail']}');
    }
  }

  /// Atualiza o email do usuario no FirebaseAuthentication
  /// Args:
  ///   newEmail: O novo email desejado
  /// Esta eh uma operacao sensivel e pode exigir reatenticacao
  Future<void> updateEmail(String newEmail) async {
    final user = _firebaseAuth.currentUser;
    if (user == null) throw Exception('Nenhm usuario logado!');

    // O Sdk do Firebase Lida com a logica de seguranca
    await user.verifyBeforeUpdateEmail(newEmail);
  }

  /// Atualiza a senha do usuario no Firebase Authentication
  /// Args:
  ///   newPassword(String): A nova desejada.
  /// Essa eh uma operacao sensivel e pode exigir reautenticacao.
  Future<void> updatePassword(String newPassword) async {
    final user = _firebaseAuth.currentUser;
    if (user == null) throw Exception("Nenhum usuario logado!");

    await user.updatePassword(newPassword);
  }

  /// Busca o perfil completo do usuário autenticado a partir do backend.
  ///
  /// Usa o endpoint GET /auth/me que já criamos e testamos.
  ///
  /// Args:
  ///   token (String): O token de autenticação do usuário.
  ///
  /// Returns:
  ///   UserProfile: O perfil do usuário.
  Future<UserProfile> fetchUserProfile(String token) async {
    final response = await http.get(
      Uri.parse(
          '${AppConfig.baseUrl}/auth/me'), // Endpoint para buscar o perfil
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return UserProfile.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Falha ao carregar o perfil do usuário.');
    }
  }

  /// Reautentica o usuário com sua senha atual.
  /// Necessário para operações sensíveis como mudar e-mail ou senha.
  Future<void> reauthenticateWithPassword(String password) async {
    final user = _firebaseAuth.currentUser;
    if (user == null) throw Exception("Nenhum usuário logado.");

    // Pega as credenciais atuais do usuário
    final cred =
        EmailAuthProvider.credential(email: user.email!, password: password);

    // Tenta reautenticar
    await user.reauthenticateWithCredential(cred);
  }
}
