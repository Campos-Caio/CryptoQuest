import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:cryptoquest/features/profile/models/user_profile_update.dart';
import 'package:flutter/material.dart';
import 'package:cryptoquest/features/auth/services/auth_service.dart';
import 'package:firebase_auth/firebase_auth.dart';

class AuthNotifier extends ChangeNotifier {
  final AuthService _authService = AuthService();

  // Variáveis de estado privadas
  UserProfile? _userProfile;
  bool _isLoading = false;
  String? _errorMessage;
  String? _token;

  // Getters públicos para a UI acessar o estado de forma segura
  UserProfile? get userProfile => _userProfile;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _userProfile != null;
  String? get token => _token;

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners(); // Avisa a UI que o carregamento começou

    try {
      // Chama o serviço para fazer a autenticação
      _userProfile = await _authService.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      // Pega o token para uso futuro em outras partes do app
      _token = await FirebaseAuth.instance.currentUser?.getIdToken();

      _isLoading = false;
      notifyListeners(); // Avisa a UI que o carregamento terminou
      return true; // Sucesso
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners(); // Avisa a UI que deu erro
      return false; // Falha
    }
  }

  Future<bool> signInWithGoogle() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _userProfile = await _authService.signInWithGoogle();
      _token = await FirebaseAuth.instance.currentUser?.getIdToken();
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.signOut();
    _userProfile = null;
    _token = null;
    notifyListeners();
  }

  /// Atualiza o perfil do usuario, chama o servico e atualiza o estado local
  /// Args:
  ///   updateModel(UserProfileUpdate): Os novos dados a serem salvos.
  /// Returns:
  ///   bool: true se a operacao foi bem sucedida, false caso contrario
  Future<bool> updateUserProfile(UserProfileUpdate updateModel) async {
    if (_token == null) {
      _errorMessage = 'Usuario nao autenticado.';
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final updateProfile =
          await _authService.updateUserProfile(_token!, updateModel);

      // Se foi bem sucedido, atualiza o peril local para que a UI mude instantaneamente
      _userProfile = updateProfile;

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (error) {
      _errorMessage = error.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Busca os dados mais recentes do perfil do usuário no backend e atualiza o estado.
  ///
  /// Essencial para ser chamado após operações como a mudança de e-mail,
  /// para que a UI reflita os dados atualizados.
  Future<void> refreshUserProfile() async {
    // Se não houver token, não há o que fazer.
    if (_token == null) return;

    // Embora a UI não precise mostrar um loading para esta ação de fundo,
    // é uma boa prática gerenciar o estado.
    _isLoading = true;
    notifyListeners();

    try {
      // Chama o novo método no serviço para buscar os dados atualizados
      final refreshedProfile = await _authService.fetchUserProfile(_token!);
      // Atualiza o perfil local com os novos dados
      _userProfile = refreshedProfile;
      _errorMessage = null;
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Recarrega os dados do usuário do Firebase e atualiza o backend.
  /// Essencial após mudanças no Firebase Auth (ex: email).
  Future<void> refreshFirebaseUser() async {
    await FirebaseAuth.instance.currentUser?.reload();
    _token = await FirebaseAuth.instance.currentUser?.getIdToken(true);
    if (_token != null) {
      await refreshUserProfile(); // Chama a função que já temos para buscar do nosso backend
    }
  }

  Future<bool> register({
    required String name,
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners(); // Avisa a UI que o processo começou

    try {
      // Chama o novo método do serviço. Ele já retorna o perfil completo.
      _userProfile = await _authService.signUpWithEmailAndPassword(
        name: name,
        email: email,
        password: password,
      );
      // Pega o token do usuário recém-logado
      _token = await FirebaseAuth.instance.currentUser?.getIdToken();

      _isLoading = false;
      notifyListeners(); // Avisa a UI que o processo terminou com sucesso
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners(); // Avisa a UI que deu erro
      return false;
    }
  }
}
