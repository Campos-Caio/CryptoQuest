import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cryptoquest/presentation/widgets/my_button.dart';
import 'package:cryptoquest/presentation/widgets/my_text_field.dart';
import 'package:flutter/material.dart';

// Importe a tela de login se você já a tiver criada
// import 'package:cryptoquest/presentation/pages/login_page.dart';

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

  final String _baseUrl = 'http://127.0.0.1:8000';

  String _message = '';
  Color _messageColor = Colors.transparent;

  @override
  void dispose() {
    // Descarte os controladores para liberar recursos quando o widget for removido
    nameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  // TODO: Implementar a lógica de registro aqui
  Future<void> _handleRegister() async {
    final String name = nameController.text.trim();
    final String email = emailController.text.trim();
    final String password = passwordController.text;
    final String confirmPassword = confirmPasswordController.text;

    // Validacoes Cliente Side
    if (name.isEmpty) {
      _showMessage("O campo Nome deve ser preenchido!", Colors.red);
      print("Campo nome deve ser preenchido!"); 
      return;
    }
    if (email.isEmpty) {
      _showMessage("O campo email deve ser preenchido!",Colors.red);
      return;
    }
    if (password.isEmpty) {
      _showMessage("O campo senha deve ser preenchido!",Colors.red);
      return;
    }
    if (confirmPassword.isEmpty) {
      _showMessage("O campo confirmar senha deve ser preenchido!",Colors.red);
      return;
    }
    if (password != confirmPassword) {
      // Mostrar um Snackbar ou alerta para o usuário
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('As senhas não coincidem!'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _message = "Registrando...";
      _messageColor = Colors.transparent;
    });

    try {
      final response = await http.post(
        Uri.parse("$_baseUrl/auth/register"),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'name': name,
          'email': email,
          'password': password,
          'confirmPassword': confirmPassword,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final Map<String, dynamic> responseBody = json.decode(response.body);
        _showMessage(
            'Registro concluido com sucesso! Bem vindo(a) ${responseBody['name']}',
            Colors.green);

        // Limpar os campos do formulário após o sucesso
        nameController.clear();
        emailController.clear();
        passwordController.clear();
        confirmPasswordController.clear();

        print('Usuário registrado com sucesso: ${responseBody['name']}');
        // TODO: Navegar para a tela de Login ou Home após o registro
        // Navigator.pushReplacement(context, MaterialPageRoute(builder: (context
      } else {
        // Erro no backend (400, 422,500)
        final Map<String, dynamic> errorBody = json.decode(response.body);
        final String errorMessage =
            errorBody['detail'] ?? "Ocorreu um erro desconhecido!";
        _showMessage(
            "Erro no registro! $errorMessage (Status: ${response.statusCode}})",
            Colors.red);
        print('Erro do backend: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      // Erro de Conexão ou Outra Exceção
      _showMessage(
          'Erro de conexão: Verifique sua internet! ($e)',
          Colors.red);
      print('Erro na requisição HTTP: $e');
    }
  }

  // Função auxiliar para exibir mensagens (SnackBar ou Texto na tela
  void _showMessage(String message, Color color) {
    setState(() {
      _message = message;
      _messageColor = color;
    });
     // Você também pode usar um SnackBar para mensagens temporárias:
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 25.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 50),
              Image.asset(
                'assets/images/register_hero.png',
                height: 150,
              ),
              const SizedBox(height: 30),
              const Text(
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
              const SizedBox(height: 30),
              MyButton(
                onTap: _handleRegister,
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
                    onTap: _handleRegister,
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
  }
}
