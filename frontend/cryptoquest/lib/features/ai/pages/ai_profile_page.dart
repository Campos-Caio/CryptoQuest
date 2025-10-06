import 'package:flutter/material.dart';
import 'package:cryptoquest/features/ai/theme/ai_colors.dart';
import 'package:cryptoquest/features/ai/widgets/ai_card.dart';

class AIProfilePage extends StatefulWidget {
  const AIProfilePage({Key? key}) : super(key: key);

  @override
  State<AIProfilePage> createState() => _AIProfilePageState();
}

class _AIProfilePageState extends State<AIProfilePage> {
  bool isLoading = true;
  Map<String, dynamic>? aiProfile;
  List<Map<String, dynamic>>? recommendations;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadAIProfile();
  }

  Future<void> _loadAIProfile() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      // Simular carregamento de dados (será substituído pela API real)
      await Future.delayed(const Duration(seconds: 2));

      // Dados mock para desenvolvimento
      setState(() {
        aiProfile = {
          'learning_pattern': {
            'type': 'visual',
            'strength': 0.85,
            'context': 'Prefere conteúdo visual e gráficos'
          },
          'performance_summary': {
            'bitcoin_proficiency': 0.87,
            'ethereum_proficiency': 0.45,
            'defi_proficiency': 0.32,
            'engagement_score': 0.88,
            'avg_response_time': 12.5,
            'consistency_score': 0.82
          },
          'data_points': 15,
          'ai_enabled': true
        };

        recommendations = [
          {
            'content_id': 'ethereum_basics_quiz',
            'content_type': 'Quiz',
            'relevance_score': 0.92,
            'difficulty_level': 'beginner',
            'estimated_time': 15,
            'reasoning':
                'Baseado no seu perfil visual, recomendamos este quiz interativo',
            'learning_objectives': [
              'Conceitos básicos do Ethereum',
              'Diferenças com Bitcoin'
            ]
          },
          {
            'content_id': 'defi_concepts_lesson',
            'content_type': 'Lição',
            'relevance_score': 0.78,
            'difficulty_level': 'intermediate',
            'estimated_time': 25,
            'reasoning': 'Para expandir seus conhecimentos em DeFi',
            'learning_objectives': [
              'Protocolos DeFi',
              'Yield Farming',
              'Liquidez'
            ]
          },
          {
            'content_id': 'trading_advanced_challenge',
            'content_type': 'Desafio',
            'relevance_score': 0.65,
            'difficulty_level': 'advanced',
            'estimated_time': 30,
            'reasoning': 'Desafio para testar seus conhecimentos avançados',
            'learning_objectives': [
              'Análise técnica',
              'Gestão de risco',
              'Estratégias'
            ]
          }
        ];
      });
    } catch (e) {
      setState(() {
        errorMessage = 'Erro ao carregar perfil de IA: $e';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AIColors.darkBackground,
      appBar: AppBar(
        title: const Text(
          '🤖 Meu Perfil de IA',
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
            onPressed: _loadAIProfile,
            tooltip: 'Atualizar perfil',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (isLoading) {
      return _buildLoadingState();
    }

    if (errorMessage != null) {
      return _buildErrorState();
    }

    if (aiProfile == null) {
      return _buildEmptyState();
    }

    return _buildProfileContent();
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
            '🤖 A IA está processando seus dados',
            style: TextStyle(
              color: AIColors.textTertiary,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
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
            errorMessage!,
            style: TextStyle(
              color: AIColors.textSecondary,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadAIProfile,
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

  Widget _buildProfileContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildProfileCard(),
          const SizedBox(height: 16),
          _buildRecommendationsCard(),
          const SizedBox(height: 16),
          _buildInsightsCard(),
          const SizedBox(height: 16),
          _buildStatsCard(),
        ],
      ),
    );
  }

  Widget _buildProfileCard() {
    final learningPattern = aiProfile!['learning_pattern'] ?? {};
    final performanceSummary = aiProfile!['performance_summary'] ?? {};

    return AICard(
      title: 'Seu Perfil de Aprendizado',
      titleIcon: Icons.psychology,
      titleIconColor: AIColors.aiPrimary,
      child: Column(
        children: [
          AIStatCard(
            label: 'Estilo de Aprendizado',
            value: _getLearningStyleText(learningPattern['type']),
            icon: _getLearningStyleIcon(learningPattern['type']),
            color:
                AIColors.getLearningStyleColor(learningPattern['type'] ?? ''),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Proficiência Bitcoin',
            value:
                '${(performanceSummary['bitcoin_proficiency'] * 100).toInt()}%',
            icon: Icons.currency_bitcoin,
            color: AIColors.getProficiencyColor(
                performanceSummary['bitcoin_proficiency'] ?? 0.0),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Engajamento',
            value: _getEngagementText(performanceSummary['engagement_score']),
            icon: Icons.local_fire_department,
            color: AIColors.getEngagementColor(
                performanceSummary['engagement_score'] ?? 0.0),
          ),
          const SizedBox(height: 12),
          AIStatCard(
            label: 'Sessões Completadas',
            value: '${aiProfile!['data_points']}',
            icon: Icons.check_circle,
            color: AIColors.aiSuccess,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationsCard() {
    return AICard(
      title: 'Suas Recomendações',
      titleIcon: Icons.recommend,
      titleIconColor: AIColors.aiSuccess,
      child: Column(
        children: [
          if (recommendations != null && recommendations!.isNotEmpty)
            ...recommendations!
                .take(3)
                .map((rec) => AIRecommendationCard(
                      title: rec['content_id'],
                      type: rec['content_type'],
                      relevanceScore: rec['relevance_score'],
                      reasoning: rec['reasoning'],
                      learningObjectives:
                          List<String>.from(rec['learning_objectives']),
                      onTap: () {
                        // TODO: Implementar navegação para o conteúdo recomendado
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content:
                                Text('Navegando para: ${rec['content_id']}'),
                            backgroundColor: AIColors.aiPrimary,
                          ),
                        );
                      },
                    ))
                .toList()
          else
            _buildPlaceholderItem('Carregando recomendações...'),
        ],
      ),
    );
  }

  Widget _buildInsightsCard() {
    return AICard(
      title: 'Insights da IA',
      titleIcon: Icons.lightbulb,
      titleIconColor: AIColors.aiWarning,
      child: Column(
        children: [
          _buildInsightItem(
            'Horário Ideal',
            'Você rende melhor às 19h',
            Icons.access_time,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Velocidade',
            'Tempo médio: 12s por pergunta',
            Icons.speed,
          ),
          const SizedBox(height: 12),
          _buildInsightItem(
            'Foco',
            'Área para melhorar: Ethereum',
            Icons.gps_fixed,
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCard() {
    final performanceSummary = aiProfile!['performance_summary'] ?? {};

    return AICard(
      title: 'Estatísticas Detalhadas',
      titleIcon: Icons.analytics,
      titleIconColor: AIColors.aiSecondary,
      child: Column(
        children: [
          AIProgressCard(
            label: 'Ethereum',
            value: performanceSummary['ethereum_proficiency'] ?? 0.0,
            color: AIColors.getProficiencyColor(
                performanceSummary['ethereum_proficiency'] ?? 0.0),
            description: 'Sua proficiência em conceitos Ethereum',
          ),
          const SizedBox(height: 12),
          AIProgressCard(
            label: 'DeFi',
            value: performanceSummary['defi_proficiency'] ?? 0.0,
            color: AIColors.getProficiencyColor(
                performanceSummary['defi_proficiency'] ?? 0.0),
            description: 'Conhecimento em finanças descentralizadas',
          ),
          const SizedBox(height: 12),
          AIProgressCard(
            label: 'Consistência',
            value: performanceSummary['consistency_score'] ?? 0.0,
            color: AIColors.getEngagementColor(
                performanceSummary['consistency_score'] ?? 0.0),
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
}
