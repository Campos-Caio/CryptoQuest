import 'package:cryptoquest/core/config/theme/app_theme.dart';
import 'package:cryptoquest/features/initial_questionnaire/pages/questionnaire_page.dart';
import 'package:cryptoquest/features/initial_questionnaire/state/questionnaire_provider.dart';
import 'package:cryptoquest/features/missions/state/mission_notifier.dart';
import 'package:cryptoquest/features/profile/pages/profile_page.dart';
import 'package:cryptoquest/features/home/pages/home_page.dart';
import 'package:cryptoquest/features/auth/pages/login_page.dart';
import 'package:cryptoquest/features/auth/pages/register_page.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/missions/pages/missions_pages.dart';
import 'package:cryptoquest/features/learning_paths/learning_paths.dart';
import 'package:cryptoquest/features/rewards/providers/reward_provider.dart';
import 'package:cryptoquest/features/ranking/providers/ranking_provider.dart';
import 'package:cryptoquest/features/rewards/pages/rewards_page.dart';
import 'package:cryptoquest/features/ranking/pages/ranking_page.dart';
import 'package:cryptoquest/features/ai/pages/ai_profile_page.dart';
import 'package:cryptoquest/features/ai/providers/ai_provider.dart';
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
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthNotifier()),
        ChangeNotifierProxyProvider<AuthNotifier, QuestionnaireProvider>(
          create: (context) => QuestionnaireProvider(
            authNotifier: Provider.of<AuthNotifier>(context, listen: false),
          ),
          update: (context, authNotifier, previousQuestionnaireProvider) =>
              QuestionnaireProvider(authNotifier: authNotifier),
        ),
        ChangeNotifierProvider(create: (_) => MissionNotifier()),
        ChangeNotifierProvider(create: (_) => LearningPathProvider()),
        ChangeNotifierProxyProvider<AuthNotifier, RewardProvider>(
          create: (context) => RewardProvider(
            authNotifier: Provider.of<AuthNotifier>(context, listen: false),
          ),
          update: (context, authNotifier, previousRewardProvider) =>
              RewardProvider(authNotifier: authNotifier),
        ),
        ChangeNotifierProxyProvider<AuthNotifier, RankingProvider>(
          create: (context) => RankingProvider(
            authNotifier: Provider.of<AuthNotifier>(context, listen: false),
          ),
          update: (context, authNotifier, previousRankingProvider) =>
              RankingProvider(authNotifier: authNotifier),
        ),
        ChangeNotifierProvider(create: (_) => AIProvider()),
      ],
      child: const MyApp(),
    ),
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
        '/profile': (context) => const ProfilePage(),
        '/missions': (context) => const MissionsPages(),
        '/learning-paths': (context) => const LearningPathsPage(),
        '/learning-path-details': (context) {
          final pathId = ModalRoute.of(context)!.settings.arguments as String;
          return LearningPathDetailsPage(pathId: pathId);
        },
        '/module-details': (context) {
          final args = ModalRoute.of(context)!.settings.arguments
              as Map<String, dynamic>;
          return ModulePage(
            pathId: args['pathId'],
            module: args['module'],
            progress: args['progress'],
          );
        },
        '/rewards': (context) => const RewardsPage(),
        '/ranking': (context) => const RankingPage(),
        '/ai-profile': (context) => const AIProfilePage(),
      },
    );
  }
}
