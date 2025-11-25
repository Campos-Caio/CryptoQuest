import 'package:cryptoquest/shared/widgets/my_button.dart';
import 'package:cryptoquest/shared/widgets/my_text_field.dart';
import 'package:cryptoquest/features/auth/widgets/square_tile.dart';
import 'package:cryptoquest/features/auth/services/auth_service.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:provider/provider.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';

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
      toastLength: Toast.LENGTH_LONG,
      gravity: ToastGravity.BOTTOM,
      timeInSecForIosWeb: 3,
      backgroundColor: isError ? Colors.redAccent : Colors.green,
      textColor: Colors.white,
      fontSize: 16.0,
    );
  }

  // Metodo de login principal refatorado para funcionar com provider
  Future<void> signIn() async {
    // Acessa o AuthProvider sem ouvir por mudanças (apenas para chamar a função)
    final authProvider = Provider.of<AuthNotifier>(context, listen: false);

    // Chama o método de login do provider
    final success = await authProvider.login(
      emailController.text.trim(),
      passwordController.text.trim(),
    );

    if (!mounted) return;

    if (success) {
      showMessage('Login efetuado com sucesso!', isError: false);
      final userProfile = authProvider.userProfile;

      // Lógica de redirecionamento
      if (userProfile != null && userProfile.hasCompletedQuestionnaire) {
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        Navigator.pushReplacementNamed(context, '/questionnaire');
      }
    } else {
      // Mostra a mensagem de erro que o provider armazenou
      showMessage(authProvider.errorMessage ?? 'Ocorreu um erro desconhecido.');
    }
  }

  Future<void> signInWithGoogle() async {
    setState(() {
      _isLoading = true;
    });

    // Acessa o AuthProvider sem ouvir por mudanças (apenas para chamar a função)
    final authProvider = Provider.of<AuthNotifier>(context, listen: false);

    try {
      // Usa o provider em vez de chamar o serviço diretamente
      final userProfile = await authProvider.signInWithGoogle();

      if (!mounted) return;

      if (userProfile != null) {
        showMessage('Login efetuado com sucesso!', isError: false);

        // Lógica de redirecionamento simplificada e robusta
        // Usa APENAS o perfil retornado diretamente (mais confiável)
        if (userProfile.hasCompletedQuestionnaire == true) {
          Navigator.pushReplacementNamed(context, '/home');
        } else {
          Navigator.pushReplacementNamed(context, '/questionnaire');
        }
      } else {
        // Mostra a mensagem de erro que o provider armazenou
        showMessage(
            authProvider.errorMessage ?? 'Ocorreu um erro desconhecido.');
      }
    } on FirebaseAuthException catch (e) {
      // Tratamento de erros específicos do FirebaseAuth
      String message = 'Erro de autenticação: ${e.message}';
      showMessage(message);
    } catch (e) {
      showMessage("Ocorreu um erro inesperado: $e");
    } finally {
      // Define o estado de carregamento de volta para false, independentemente do resultado
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return Consumer<AuthNotifier>(
      builder: (context, authProvider, child) {
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
                                color: Colors
                                    .deepPurple) // Indicador de carregamento
                            : MyButton(
                                onTap: signIn,
                                buttonCollor: Colors.deepPurple,
                                text: "Login"),
                        Column(
                          children: [
                            Padding(
                              padding:
                                  EdgeInsetsGeometry.symmetric(horizontal: 25),
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
                              style: TextStyle(
                                  color: Colors.white70, fontSize: 14),
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
      },
    );
  }
}
