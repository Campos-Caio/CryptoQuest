import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:cryptoquest/shared/widgets/my_button.dart';
import 'package:cryptoquest/shared/widgets/my_text_field.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  // Controladores para os campos de texto
  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();

  final AuthNotifier authNotifier = AuthNotifier(); 

  @override
  void dispose() {
    // Descarte os controladores para liberar recursos quando o widget for removido
    nameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _signUp() async {
    if (passwordController.text != confirmPasswordController.text) {
      _showMessage("As senhas não coincidem!");
      return;
    }
    // Outras validações simples
    if (nameController.text.isEmpty ||
        emailController.text.isEmpty ||
        passwordController.text.isEmpty) {
      _showMessage("Por favor, preencha todos os campos.");
      return;
    }

    // 1. Pega o AuthNotifier
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);

    // 2. Chama o novo método de registro do notifier
    final success = await authNotifier.register(
      name: nameController.text.trim(),
      email: emailController.text.trim(),
      password: passwordController.text.trim(),
    );

    if (!mounted) return;

    // 3. Reage ao resultado
    if (success) {
      _showMessage('Cadastro realizado com sucesso!', isError: false);

      // 4. USA A MESMA LÓGICA INTELIGENTE DE REDIRECIONAMENTO
      final userProfile = authNotifier.userProfile;
      // Para um novo usuário, a condição `hasCompletedQuestionnaire` será sempre `false`
      if (userProfile != null && userProfile.hasCompletedQuestionnaire) {
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        // Redireciona corretamente para o questionário
        Navigator.pushReplacementNamed(context, '/questionnaire');
      }
    } else {
      // Mostra a mensagem de erro que o notifier guardou
      _showMessage(
          authNotifier.errorMessage ?? 'Ocorreu um erro desconhecido.');
    }
  }

  // Função auxiliar para exibir mensagens (SnackBar ou Texto na tela
  void _showMessage(String message, {bool isError = true}) {
    Fluttertoast.showToast(
      msg: message,
      toastLength: Toast.LENGTH_LONG,
      gravity: ToastGravity.BOTTOM,
      backgroundColor: isError ? Colors.redAccent : Colors.green,
      textColor: Colors.white,
      fontSize: 16.0,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthNotifier>(builder: (context, value, child) {
      return Scaffold(
        body: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 25.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 50),
                Image.asset(
                  'assets/images/cryptoquest_hero.jpg',
                  height: 150,
                ),
                const SizedBox(height: 30),
                Text(
                  "Cadastro!",
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  "Informe seus dados para se cadastrar!",
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 30),
                MyTextField(
                  controller: nameController,
                  hintText: "Informe seu nome",
                  obscureText: false,
                  icon: const Icon(Icons.person, color: Colors.deepPurple),
                ),
                const SizedBox(height: 15),
                MyTextField(
                  controller: emailController,
                  hintText: "Informe seu email",
                  obscureText: false,
                  icon: const Icon(Icons.email, color: Colors.deepPurple),
                ),
                const SizedBox(height: 15),
                MyTextField(
                  controller: passwordController,
                  hintText: "Informe sua senha",
                  obscureText: true,
                  icon: const Icon(Icons.lock, color: Colors.deepPurple),
                ),
                const SizedBox(height: 15),
                MyTextField(
                  controller: confirmPasswordController,
                  hintText: "Confirmar Senha",
                  obscureText: true,
                  icon: const Icon(Icons.lock_reset, color: Colors.deepPurple),
                ),
                // O botão agora mostra um loading com base no estado do notifier
                authNotifier.isLoading
                    ? const CircularProgressIndicator(color: Colors.deepPurple)
                    : MyButton(
                        onTap: _signUp, // Chama a nova função _signUp
                        buttonCollor: Colors.deepPurple,
                        text: "Cadastrar!",
                      ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      "Já possui conta?",
                      style: TextStyle(color: Colors.white70, fontSize: 14),
                    ),
                    const SizedBox(width: 4),
                    GestureDetector(
                      onTap: () {
                        Navigator.pushReplacementNamed(context, "/login");
                      },
                      child: const Text(
                        "Faça login",
                        style: TextStyle(
                          color: Colors
                              .blueAccent, // Uma cor de destaque para o link
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 30), // Espaçamento inferior
              ],
            ),
          ),
        ),
      );
    });
  }
}
