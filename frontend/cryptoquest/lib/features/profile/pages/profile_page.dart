
import 'package:cryptoquest/features/profile/models/user_profile_update.dart';
import 'package:cryptoquest/services/auth_notifier.dart';
import 'package:cryptoquest/services/auth_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> with WidgetsBindingObserver {
  late final TextEditingController _nameController;
  final AuthService _authService = AuthService();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    _nameController = TextEditingController(text: authNotifier.userProfile?.name ?? '');
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _nameController.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      Provider.of<AuthNotifier>(context, listen: false).refreshFirebaseUser();
    }
  }

  Future<String?> _showInputDialog({
    required String title,
    required String hint,
    bool isPassword = false,
  }) async {
    final textController = TextEditingController();
    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: textController,
          obscureText: isPassword,
          decoration: InputDecoration(hintText: hint),
        ),
        actions: [
          TextButton(
            child: const Text("Cancelar"),
            onPressed: () => Navigator.of(context).pop(),
          ),
          ElevatedButton(
            child: const Text("Confirmar"),
            onPressed: () => Navigator.of(context).pop(textController.text),
          ),
        ],
      ),
    );
  }

  void _showMessage(String message, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(message),
      backgroundColor: isError ? Colors.redAccent : Colors.green,
    ));
  }

  Future<void> _saveProfileChanges() async {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final updateModel = UserProfileUpdate(
      name: _nameController.text,

    );

    final success = await authNotifier.updateUserProfile(updateModel);
    if (success) {
      _showMessage("Perfil atualizado com sucesso!");
    } else {
      _showMessage(authNotifier.errorMessage ?? 'Ocorreu um erro desconhecido.', isError: true);
    }
  }

  Future<void> _updateEmail() async {
    final newEmail = await _showInputDialog(title: "Alterar E-mail", hint: "Digite o novo e-mail");
    if (newEmail == null || newEmail.isEmpty) return;

    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    try {
      await _authService.updateEmail(newEmail);
      _showMessage("Link de confirmação enviado para $newEmail. Por favor, verifique sua caixa de entrada.");
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login' && mounted) {
        _showMessage("Por segurança, confirme sua senha atual.", isError: true);
        final password = await _showInputDialog(title: "Confirme sua Identidade", hint: "Digite sua senha atual", isPassword: true);
        if (password == null || password.isEmpty) return;
        try {
          await _authService.reauthenticateWithPassword(password);
          await _authService.updateEmail(newEmail);
          _showMessage("Link de confirmação enviado para $newEmail. Por favor, verifique sua caixa de entrada.");
        } catch (error) {
          _showMessage("Erro: $error", isError: true);
        }
      } else {
        _showMessage("Erro do Firebase: ${e.message}", isError: true);
      }
    } catch (e) {
      _showMessage("Erro inesperado: $e", isError: true);
    }
  }

  Future<void> _updatePassword() async {
    final newPassword = await _showInputDialog(title: "Alterar Senha", hint: "Digite a nova senha", isPassword: true);
    if (newPassword == null || newPassword.isEmpty) return;

    try {
      await _authService.updatePassword(newPassword);
      _showMessage("Senha alterada com sucesso!");
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login' && mounted) {
        _showMessage("Por segurança, confirme sua senha atual.", isError: true);
        final password = await _showInputDialog(title: "Confirme sua Identidade", hint: "Digite sua senha atual", isPassword: true);
        if (password == null || password.isEmpty) return;
        try {
          await _authService.reauthenticateWithPassword(password);
          await _authService.updatePassword(newPassword);
          _showMessage("Senha alterada com sucesso!");
        } catch (error) {
          _showMessage("Erro: $error", isError: true);
        }
      } else {
        _showMessage("Erro do Firebase: ${e.message}", isError: true);
      }
    } catch (e) {
      _showMessage("Erro inesperado: $e", isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthNotifier>(
      builder: (context, authNotifier, child) {
        final userProfile = authNotifier.userProfile;
        if (userProfile == null) {
          return Scaffold(
            appBar: AppBar(title: const Text("Perfil")),
            body: const Center(child: Text("Usuário não encontrado.")),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: const Text("Meu Perfil"),
            actions: [
              IconButton(
                tooltip: "Sair",
                icon: const Icon(Icons.logout),
                onPressed: () {
                  authNotifier.logout();
                  Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
                },
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text("Nome de Exibição", style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                TextField(controller: _nameController),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: authNotifier.isLoading ? null : _saveProfileChanges,
                  child: authNotifier.isLoading 
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text("Salvar Alterações"),
                ),
                const Divider(height: 48),
                Text("Segurança", style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.email),
                  title: const Text("Alterar E-mail"),
                  subtitle: Text(userProfile.email),
                  onTap: _updateEmail,
                ),
                ListTile(
                  leading: const Icon(Icons.lock),
                  title: const Text("Alterar Senha"),
                  onTap: _updatePassword,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}