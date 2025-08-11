import 'package:cryptoquest/features/profile/models/user_profile_update.dart';
import 'package:cryptoquest/services/auth_notifier.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  late final TextEditingController _nameController;
  late final TextEditingController _bioController;

  @override
  void initState() {
    super.initState();
    // Inicializa os controlelr com os dados do usuario
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    _nameController =
        TextEditingController(text: authNotifier.userProfile?.name ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  // Lida com o salvamennto das alteracoes do perfil
  Future<void> _saveProfileChange() async {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final updateModel = UserProfileUpdate(
      name: _nameController.text,
    );

    final sucess = await authNotifier.updateUserProfile(updateModel);

    if (mounted) {
      if (sucess) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text("Perfil atualizado com sucessO!"),
          backgroundColor: Colors.green,
        ));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Erro: ${authNotifier.errorMessage}'),
          backgroundColor: Colors.red,
        ));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthNotifier>(
      builder: (context, authNotifier, child) {
        final userProfile = authNotifier.userProfile;

        if (userProfile == null) {
          return Scaffold(
            appBar: AppBar(title: const Text("Meu Perfil")),
            body: const Center(
              child: Text("Usuario nao encontrado!"),
            ),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: const Text("Meu Perfil"),
            actions: [
              IconButton(
                tooltip: 'Sair',
                onPressed: () {
                  authNotifier.logout();
                  Navigator.of(context)
                      .pushNamedAndRemoveUntil('/login', (route) => false);
                },
                icon: const Icon(Icons.logout),
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Campos de perfil
                Text(
                  'Nome de Exibição',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(
                  height: 8,
                ),
                TextField(
                  controller: _nameController,
                ),
                const SizedBox(
                  height: 24,
                ),

                // Botao de salvar
                ElevatedButton(
                  onPressed: authNotifier.isLoading ? null : _saveProfileChange,
                  child: authNotifier.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                          ))
                      : const Text("Salvar Alterações"),
                ),

                const Divider(height: 48,), 

                // Secao de seguranca 
                Text("Segurança", style: Theme.of(context).textTheme.headlineSmall,), 
                const SizedBox(height: 16,), 
                ListTile(
                  leading: const Icon(Icons.email),
                  title: const Text("Alterar e-mail!"),
                  subtitle: Text(userProfile.email),
                  onTap: () {
                    // TODO logica para mostra um dialogo e chamar o updateEmail()
                  },
                ), 
                ListTile(
                  leading: const Icon(Icons.lock),
                  title: const Text("Alterar Senha"),
                  onTap: (){
                    // TODO logica para mostra um dialogo e chamar o updatePassword()
                  },
                )
              ],
            ),
          ),
        );
      },
    );
  }
}
