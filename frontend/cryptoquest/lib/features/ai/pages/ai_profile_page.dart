import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cryptoquest/features/ai/theme/ai_colors.dart';
import 'package:cryptoquest/features/ai/widgets/ai_card.dart';
import 'package:cryptoquest/features/ai/providers/ai_provider.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/quiz/pages/quiz_page.dart';
import 'package:cryptoquest/features/learning_paths/learning_paths.dart';

class AIProfilePage extends StatefulWidget {
  const AIProfilePage({Key? key}) : super(key: key);

  @override
  State<AIProfilePage> createState() => _AIProfilePageState();
}

class _AIProfilePageState extends State<AIProfilePage> {
  @override
  void initState() {
    super.initState();
    _loadAIData();
  }

  Future<void> _loadAIData() async {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final aiProvider = Provider.of<AIProvider>(context, listen: false);

    if (authNotifier.token != null && authNotifier.userProfile != null) {
      await aiProvider.loadAllAIData(
        authNotifier.userProfile!.uid,
        authNotifier.token!,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AIColors.darkBackground,
      appBar: AppBar(
        title: const Text(
          'Meu Perfil de IA',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        backgroundColor: Colors.transparent,
        foregroundColor: AIColors.textPrimary,
        elevation: 0,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: AIColors.aiPrimaryGradient,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAIData,
            tooltip: 'Atualizar perfil',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    return Consumer2<AIProvider, AuthNotifier>(
      builder: (context, aiProvider, authNotifier, child) {
        // Verificar se está carregando
        if (aiProvider.isLoadingProfile ||
            aiProvider.isLoadingRecommendations ||
            aiProvider.isLoadingInsights) {
          return _buildLoadingState();
        }

        // Verificar se há erros
        if (aiProvider.hasErrors) {
          return _buildErrorState(aiProvider);
        }

        // Verificar se não há dados
        if (!aiProvider.hasData) {
          return _buildEmptyState();
        }

        return _buildProfileContent(aiProvider);
      },
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(
              AIColors.aiPrimary,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Analisando seu perfil de aprendizado...',
            style: TextStyle(
              color: AIColors.textSecondary,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'A IA está processando seus dados',
            style: TextStyle(
              color: AIColors.textTertiary,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(AIProvider aiProvider) {
    String errorMessage = 'Erro desconhecido';
    if (aiProvider.profileError != null) {
      errorMessage = aiProvider.profileError!;
    } else if (aiProvider.recommendationsError != null) {
      errorMessage = aiProvider.recommendationsError!;
    } else if (aiProvider.insightsError != null) {
      errorMessage = aiProvider.insightsError!;
    }

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: AIColors.aiError,
          ),
          const SizedBox(height: 16),
          Text(
            'Ops! Algo deu errado',
            style: TextStyle(
              color: AIColors.textPrimary,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            errorMessage,
            style: TextStyle(
              color: AIColors.textSecondary,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadAIData,
            icon: const Icon(Icons.refresh),
            label: const Text('Tentar Novamente'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AIColors.aiPrimary,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.psychology_outlined,
            size: 64,
            color: AIColors.textTertiary,
          ),
          const SizedBox(height: 16),
          Text(
            'Perfil de IA não encontrado',
            style: TextStyle(
              color: AIColors.textPrimary,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Complete algumas atividades para gerar seu perfil de IA',
            style: TextStyle(
              color: AIColors.textSecondary,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildProfileContent(AIProvider aiProvider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildProfileCard(aiProvider),
          const SizedBox(height: 16),
          _buildRecommendationsCard(aiProvider),
          const SizedBox(height: 16),
          _buildInsightsCard(aiProvider),
          const SizedBox(height: 16),
          _buildStatsCard(aiProvider),
        ],
      ),
    );
  }

  Widget _buildProfileCard(AIProvider aiProvider) {
    return AICard(
      title: 'Seu Perfil de Aprendizado',
      titleIcon: Icons.psychology,
      titleIconColor: AIColors.aiPrimary,
      child: Column(
        children: [
          AIStatCard(
            label: 'Estilo de Aprendizado',
            value: _getLearningStyleText(aiProvider.learningStyle),
            icon: _getLearningStyleIcon(aiProvider.learningStyle),
            color:
                AIColors.getLearningStyleColor(aiProvider.learningStyle ?? ''),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Proficiência Bitcoin',
            value: '${((aiProvider.bitcoinProficiency ?? 0.0) * 100).toInt()}%',
            icon: Icons.currency_bitcoin,
            color: AIColors.getProficiencyColor(
                aiProvider.bitcoinProficiency ?? 0.0),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Engajamento',
            value: _getEngagementText(aiProvider.engagementScore),
            icon: Icons.local_fire_department,
            color:
                AIColors.getEngagementColor(aiProvider.engagementScore ?? 0.0),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Sessões Completadas',
            value: '${aiProvider.dataPoints ?? 0}',
            icon: Icons.check_circle,
            color: AIColors.aiSuccess,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationsCard(AIProvider aiProvider) {
    return AICard(
      title: 'Suas Recomendações',
      titleIcon: Icons.recommend,
      titleIconColor: AIColors.aiSuccess,
      child: Column(
        children: [
          if (aiProvider.recommendations.isNotEmpty)
            ...aiProvider.recommendations
                .take(3)
                .map((rec) => _buildRecommendationItem(rec))
          else
            _buildPlaceholderItem('Nenhuma recomendação disponível'),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(Map<String, dynamic> rec) {
    final isLearningPath =
        rec.containsKey('path_id') || rec.containsKey('name');

    if (isLearningPath) {
      // Recomendação de Learning Path - buscar nome real
      return Consumer<LearningPathProvider>(
        builder: (context, learningPathProvider, child) {
          final pathId = rec['path_id'] as String?;
          String pathName = rec['name'] ?? 'Trilha de Aprendizado';
          
          // Buscar nome real da trilha se tiver path_id
          if (pathId != null && learningPathProvider.learningPaths.isNotEmpty) {
            final path = learningPathProvider.learningPaths
                .firstWhere((p) => p.id == pathId, orElse: () => learningPathProvider.learningPaths.first);
            pathName = path.name;
          }
          
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AIColors.aiSuccess.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AIColors.aiSuccess.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.school, color: AIColors.aiSuccess, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        pathName,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AIColors.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        rec['description'] ?? 'Descrição não disponível',
                        style: TextStyle(
                          color: AIColors.textSecondary,
                          fontSize: 12,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: AIColors.aiSuccess.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              '${((rec['relevance_score'] ?? 0.0) * 100).toInt()}%',
                              style: TextStyle(
                                color: AIColors.aiSuccess,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            rec['reasoning'] ?? 'Recomendação personalizada',
                            style: TextStyle(
                              color: AIColors.textTertiary,
                              fontSize: 10,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Icon(Icons.arrow_forward_ios,
                    color: AIColors.textTertiary, size: 16),
              ],
            ),
          );
        },
      );
    } else {
      // Recomendação de Quiz/Conteúdo - buscar título real
      final contentId = rec['content_id'] as String?;
      final title = rec['title'] as String? ?? _getQuizTitle(contentId) ?? contentId ?? 'Conteúdo';
      
      return AIRecommendationCard(
        title: title,
        type: rec['content_type'] ?? 'Quiz',
        relevanceScore: rec['relevance_score'] ?? 0.0,
        reasoning: rec['reasoning'] ?? 'Recomendação personalizada',
        learningObjectives: List<String>.from(rec['learning_objectives'] ?? []),
        onTap: () => _navigateToRecommendedContent(rec),
      );
    }
  }
  
  /// Mapeia content_id para título real do quiz
  String? _getQuizTitle(String? contentId) {
    if (contentId == null) return null;
    
    final quizTitleMap = {
      'btc_quiz_01': 'Fundamentos do Bitcoin',
      'blockchain_conceitos_questionnaire': 'A Blockchain e a Criptografia',
      'daily_crypto_security_quiz': 'Segurança em Cripto',
      'bitcoin_caracteristicas_questionnaire': 'Características do Bitcoin',
      'chaves_privadas_questionnaire': 'Chaves Privadas e Segurança',
      'autocustodia_multisig_questionnaire': 'Autocustódia e Multisig',
      'daily_backup_quiz': 'Backup e Recuperação',
      'btc_quiz_02': 'Bitcoin Avançado',
      'utxo_questionnaire': 'UTXO e Transações',
      'lightning_network_questionnaire': 'Lightning Network',
      'nft_marketplace_lesson': 'NFT Marketplace',
      'smart_contracts_101': 'Smart Contracts 101',
      'solidity_basics_lesson': 'Fundamentos de Solidity',
      'contract_security_quiz': 'Segurança de Contratos',
    };
    
    return quizTitleMap[contentId];
  }

  Widget _buildInsightsCard(AIProvider aiProvider) {
    return AICard(
      title: 'Insights da IA',
      titleIcon: Icons.lightbulb,
      titleIconColor: AIColors.aiWarning,
      child: Column(
        children: [
          _buildInsightItem(
            'Horário Ideal',
            aiProvider.idealTime ?? 'Analisando padrões...',
            Icons.access_time,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Velocidade',
            'Tempo médio: ${aiProvider.avgResponseTime?.toStringAsFixed(1) ?? 'Calculando...'}s por pergunta',
            Icons.speed,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Foco',
            'Área para melhorar: ${aiProvider.focusArea ?? 'Analisando...'}',
            Icons.gps_fixed,
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCard(AIProvider aiProvider) {
    return AICard(
      title: 'Estatísticas Detalhadas',
      titleIcon: Icons.analytics,
      titleIconColor: AIColors.aiSecondary,
      child: Column(
        children: [
          AIProgressCard(
            label: 'Ethereum',
            value: aiProvider.ethereumProficiency ?? 0.0,
            color: AIColors.getProficiencyColor(
                aiProvider.ethereumProficiency ?? 0.0),
            description: 'Sua proficiência em conceitos Ethereum',
          ),
          const SizedBox(height: 12),
          AIProgressCard(
            label: 'DeFi',
            value: aiProvider.defiProficiency ?? 0.0,
            color:
                AIColors.getProficiencyColor(aiProvider.defiProficiency ?? 0.0),
            description: 'Conhecimento em finanças descentralizadas',
          ),
          const SizedBox(height: 12),
          AIProgressCard(
            label: 'Consistência',
            value: aiProvider.consistencyScore ?? 0.0,
            color:
                AIColors.getEngagementColor(aiProvider.consistencyScore ?? 0.0),
            description: 'Regularidade no seu aprendizado',
          ),
        ],
      ),
    );
  }

  Widget _buildInsightItem(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: AIColors.aiWarning, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: AIColors.textSecondary,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  color: AIColors.textPrimary,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPlaceholderItem(String text) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Text(
        text,
        style: TextStyle(
          color: AIColors.textTertiary,
          fontStyle: FontStyle.italic,
        ),
      ),
    );
  }

  String _getLearningStyleText(String? style) {
    return AIColors.getLearningStyleText(style ?? '');
  }

  IconData _getLearningStyleIcon(String? style) {
    return AIColors.getLearningStyleIcon(style ?? '');
  }

  String _getEngagementText(double? score) {
    if (score == null) return 'Calculando...';
    return AIColors.getEngagementText(score);
  }

  /// Navega para o conteúdo recomendado pela IA
  void _navigateToRecommendedContent(Map<String, dynamic> recommendation) {
    final contentId = recommendation['content_id'] as String?;
    final contentType = recommendation['content_type'] as String?;

    if (contentId == null) {
      _showErrorSnackBar('ID do conteúdo não encontrado');
      return;
    }

    try {
      switch (contentType?.toLowerCase()) {
        case 'quiz':
          _navigateToQuiz(contentId, recommendation);
          break;
        case 'lesson':
          _navigateToLesson(contentId, recommendation);
          break;
        case 'learning_path':
          _navigateToLearningPath(contentId, recommendation);
          break;
        default:
          _navigateToQuiz(contentId, recommendation); // Fallback para quiz
      }
    } catch (e) {
      _showErrorSnackBar('Erro ao navegar para o conteúdo: $e');
    }
  }

  /// Navega para um quiz recomendado
  void _navigateToQuiz(String contentId, Map<String, dynamic> recommendation) {
    // Mapear content_id para quiz_id real
    final quizId = _mapContentIdToQuizId(contentId);

    if (quizId == null) {
      _showErrorSnackBar('Quiz não encontrado: $contentId');
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizPage(
          missionId: 'ai_recommendation_${contentId}',
          quizId: quizId,
          missionTitle:
              '${recommendation['content_id'] ?? 'Quiz Recomendado'}',
        ),
      ),
    ).then((result) {
      // Recarregar dados de IA após completar o quiz
      if (result != null) {
        _loadAIData();
        _showSuccessSnackBar('Quiz recomendado completado!');
      }
    });
  }

  /// Navega para uma lição recomendada
  void _navigateToLesson(
      String contentId, Map<String, dynamic> recommendation) {
    // Por enquanto, redireciona para a página de learning paths
    // TODO: Implementar página específica para lições
    _showInfoSnackBar(
        'Lição recomendada: $contentId\nRedirecionando para Learning Paths...');

    Future.delayed(const Duration(seconds: 1), () {
      Navigator.pushNamed(context, '/learning-paths');
    });
  }

  /// Navega para uma trilha de aprendizado recomendada
  void _navigateToLearningPath(
      String contentId, Map<String, dynamic> recommendation) {
    // Mapear content_id para path_id real
    final pathId = _mapContentIdToPathId(contentId);

    if (pathId == null) {
      _showErrorSnackBar('Trilha de aprendizado não encontrada: $contentId');
      return;
    }

    Navigator.pushNamed(
      context,
      '/learning-path-details',
      arguments: pathId,
    ).then((result) {
      // Recarregar dados de IA após interagir com a trilha
      if (result != null) {
        _loadAIData();
        _showSuccessSnackBar('Trilha recomendada acessada!');
      }
    });
  }

  /// Mapeia content_id da IA para quiz_id real do sistema
  String? _mapContentIdToQuizId(String contentId) {
    final contentMapping = {
      'btc_quiz_01': 'btc_quiz_01',
      'blockchain_conceitos_questionnaire':
          'blockchain_conceitos_questionnaire',
      'daily_crypto_security_quiz': 'daily_crypto_security_quiz',
      'bitcoin_caracteristicas_questionnaire':
          'bitcoin_caracteristicas_questionnaire',
      'chaves_privadas_questionnaire': 'chaves_privadas_questionnaire',
      'autocustodia_multisig_questionnaire':
          'autocustodia_multisig_questionnaire',
      'daily_backup_quiz': 'daily_backup_quiz',
      'btc_quiz_02': 'btc_quiz_02',
      'nft_marketplace_lesson': 'nft_marketplace_quiz',
      'smart_contracts_101': 'smart_contracts_quiz',
      'solidity_basics_lesson': 'solidity_basics_quiz',
      'contract_security_quiz': 'contract_security_quiz',
      'utxo_questionnaire': 'utxo_questionnaire',
      'lightning_network_questionnaire': 'lightning_network_questionnaire',
    };

    return contentMapping[contentId];
  }

  /// Mapeia content_id da IA para path_id real do sistema
  String? _mapContentIdToPathId(String contentId) {
    // Mapeamento para trilhas de aprendizado
    final pathMapping = {
      'bitcoin_learning_path': 'aprofundando_bitcoin_tecnologia',
      'blockchain_learning_path': 'bitcoin_ecossistema_financeiro',
      'defi_learning_path': 'defi_ecosystem',
      'trading_learning_path': 'crypto_trading_mastery',
      'security_learning_path': 'crypto_security_fundamentals',
    };

    return pathMapping[contentId];
  }

  /// Mostra snackbar de sucesso
  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AIColors.aiSuccess,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  /// Mostra snackbar de erro
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AIColors.aiError,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  /// Mostra snackbar informativa
  void _showInfoSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AIColors.aiWarning,
        duration: const Duration(seconds: 3),
      ),
    );
  }
}
