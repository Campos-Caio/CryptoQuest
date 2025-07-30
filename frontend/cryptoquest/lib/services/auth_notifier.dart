import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:flutter/material.dart';
import 'package:cryptoquest/services/auth_service.dart'; 
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
}