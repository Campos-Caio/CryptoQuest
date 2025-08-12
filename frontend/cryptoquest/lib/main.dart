import 'package:cryptoquest/config/theme/app_theme.dart';
import 'package:cryptoquest/features/initial_questionnaire/pages/questionnaire_page.dart';
import 'package:cryptoquest/features/initial_questionnaire/state/questionnaire_provider.dart';
import 'package:cryptoquest/features/profile/pages/profile_page.dart';
import 'package:cryptoquest/presentation/pages/home_page.dart';
import 'package:cryptoquest/presentation/pages/login_page.dart';
import 'package:cryptoquest/presentation/pages/register_page.dart';
import 'package:cryptoquest/services/auth_notifier.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'firebase_options.dart';
import 'package:firebase_core/firebase_core.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(
    (MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthNotifier()),
        ChangeNotifierProxyProvider<AuthNotifier, QuestionnaireProvider>(
          // O 'create' é chamado uma vez para criar a instância inicial.
          create: (context) => QuestionnaireProvider(
            authNotifier: Provider.of<AuthNotifier>(context, listen: false),
          ),
          // O 'update' é chamado sempre que o AuthNotifier muda.
          update: (context, authNotifier, previousQuestionnaireProvider) =>
              QuestionnaireProvider(authNotifier: authNotifier),
        ),
      ],
      child: const MyApp(),
    )),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: "CryptoQuest",
        debugShowCheckedModeBanner: false,
        theme: AppTheme.appTheme,
        initialRoute: '/login',
        routes: {
          '/register': (context) => const RegisterPage(),
          '/login': (context) => LoginPage(),
          '/home': (context) => HomePage(),
          '/questionnaire': (context) => const QuestionnairePage(),
          '/profile':(context) => const ProfilePage(), 
        });
  }
}
