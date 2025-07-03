import 'dart:convert';

import 'package:cryptoquest/presentation/widgets/my_button.dart';
import 'package:cryptoquest/presentation/widgets/my_text_field.dart';
import 'package:cryptoquest/presentation/widgets/square_tile.dart';
import 'package:cryptoquest/services/auth_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // Controllers para os campos de text
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  final AuthService _authService = AuthService();

  bool _isLoading = false;

  @override
  void dispose() {
    // Dispose para liberar recursos
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  // Metodo para exibir imagens de erro ou sucesso ao usuario
  void showMessage(String message, {bool isError = true}) {
    Fluttertoast.showToast(
      msg: message,
      toastLength: Toast.LENGTH_LONG, // Mensagem longa
      gravity: ToastGravity.BOTTOM, // Posição inferior
      timeInSecForIosWeb: 3, // Duração para iOS/Web
      backgroundColor: isError
          ? Colors.redAccent
          : Colors.green, // Cores diferentes para erro/sucesso
      textColor: Colors.white,
      fontSize: 16.0,
    );
  }

  // Metodo de login principal
  Future<void> signIn() async {
    // Define o estado de carregamento para true e atualiza UI
    setState(() {
      _isLoading = true;
    });

    try {
      // Wrapper para o AuthService
      await _authService.signInWithEmailAndPassword(
        email: emailController.text.trim(),
        password: passwordController.text.trim(),
      ); 
      showMessage('Login efetuado com sucesso!', isError: false);
      Navigator.pushReplacementNamed(context, '/home');
    } on FirebaseAuthException catch (e) {
      // Tratamento de erros especificos do FirebaseAuth
      String message;

      if (e.code == 'user-not-found') {
        message = 'Nenhum Usuario foi encontrado com este email!';
      } else if (e.code == 'wrong-password') {
        message = 'Senha incorreta!';
      } else if (e.code == 'invalid-email') {
        message = 'O formato do email é inválido.';
      } else if (e.code == 'network-request-failed') {
        message = 'Erro de conexão: Verifique sua internet.';
      }
      if (e.code == 'invalid-email') {
        message = 'Email Invalido!';
      } else {
        message = 'Erro de autenticação: ${e.message}';
      }
      showMessage(message);
      print("FirebaseAuthException: ${e.code} - ${e.message}");
    } catch (e) {
      // Tratamento de outros erros gerais.
      showMessage("Ocorreu um erro inesperado: $e");
      print("Erro inesperado: $e"); // Para depuração
    } finally {
      //  Define o estado de carregamento de volta para false, independentemente do resultado.
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> signInWithGoogle() async {
    setState(() {
      _isLoading = true;
    });

    // Wrapper do Login com google 
    try{
      await _authService.signInWithGoogle();
      showMessage('Login efetuado com sucesso!', isError: false);
      Navigator.pushReplacementNamed(context, '/home');
    } on FirebaseAuthException catch (e) {
      // Tratamento de erros especificos do FirebaseAuth
      String message = 'Erro de autenticação: ${e.message}';
      showMessage(message);
      print("FirebaseAuthException: ${e.code} - ${e.message}");
    } catch (e) {
      // Tratamento de outros erros gerais.
      showMessage("Ocorreu um erro inesperado: $e");
      print("Erro inesperado: $e"); // Para depuração
    } finally {
      //  Define o estado de carregamento de volta para false, independentemente do resultado.
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                SizedBox(
                  height: screenHeight * 0.05,
                ),
                Image.asset(
                  'assets/images/btc_purple.png',
                  height: screenHeight * 0.15,
                ),
                Column(
                  children: [
                    Text(
                      "CryptoQuest",
                      style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    ),
                    Text(
                      "Uma jornada pelo mundo Cripto",
                      style: TextStyle(fontSize: 16, color: Colors.white70),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(
                      height: screenHeight * 0.025,
                    ),
                    MyTextField(
                      controller: emailController,
                      hintText: "Email ou nome de Usuario",
                      obscureText: false,
                      icon: Icon(Icons.email),
                    ),
                    MyTextField(
                      controller: passwordController,
                      hintText: "Senha",
                      obscureText: true,
                      icon: Icon(Icons.password),
                    ),
                    SizedBox(
                      height: screenHeight * 0.01,
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 25.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.start,
                        children: [
                          Text(
                            "Esqueceu a senha?",
                            style: TextStyle(color: Colors.white70),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(
                      height: screenHeight * 0.025,
                    ),
                    _isLoading
                        ? CircularProgressIndicator(
                            color:
                                Colors.deepPurple) // Indicador de carregamento
                        : MyButton(
                            onTap: signIn,
                            buttonCollor: Colors.deepPurple,
                            text: "Login"),
                    Column(
                      children: [
                        Padding(
                          padding: EdgeInsetsGeometry.symmetric(horizontal: 25),
                          child: Row(
                            children: [
                              Expanded(
                                child: Divider(
                                  thickness: 0.5,
                                  color: Colors.deepPurple[400],
                                ),
                              ),
                              Padding(
                                padding: EdgeInsetsGeometry.symmetric(
                                    horizontal: screenHeight * 0.01),
                                child: Text(
                                  "Ou entre com",
                                  style: TextStyle(
                                    color: Colors.white70,
                                  ),
                                ),
                              ),
                              Expanded(
                                child: Divider(
                                  thickness: 0.5,
                                  color: Colors.deepPurple[400],
                                ),
                              ),
                            ],
                          ),
                        ),
                        SizedBox(
                          height: screenHeight * 0.025,
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SquareTile(
                                imagePath: "assets/images/google.png",
                                auth: signInWithGoogle),
                          ],
                        )
                      ],
                    ),
                    SizedBox(
                      height: screenHeight * 0.025,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          'Ainda nao possui uma conta?',
                          style: TextStyle(color: Colors.white70, fontSize: 14),
                        ),
                        GestureDetector(
                          onTap: () {
                            Navigator.pushReplacementNamed(
                                context, "/register");
                          },
                          child: Text(
                            " Cadastre-se",
                            style: TextStyle(
                                color: Colors.deepPurple,
                                fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(
                      height: screenHeight * 0.02,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
