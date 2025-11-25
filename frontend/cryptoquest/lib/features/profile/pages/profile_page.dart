import 'package:cryptoquest/features/profile/models/user_profile_update.dart';
import 'package:cryptoquest/features/auth/state/auth_notifier.dart';
import 'package:cryptoquest/features/auth/services/auth_service.dart';
import 'package:cryptoquest/features/auth/user_profile_model.dart';
import 'package:cryptoquest/features/rewards/providers/reward_provider.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';
import 'package:cryptoquest/features/learning_paths/widgets/glassmorphism_card.dart';
import 'package:cryptoquest/shared/widgets/feedback_widgets.dart';
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
  final _formKey = GlobalKey<FormState>();
  bool _isEditingName = false;
  bool _isSaving = false;
  String _originalName = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    _originalName = authNotifier.userProfile?.name ?? '';
    _nameController = TextEditingController(text: _originalName);
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

  Future<String?> _showCustomInputDialog({
    required String title,
    required String hint,
    String? initialValue,
    bool isPassword = false,
    bool isEmail = false,
    String? Function(String?)? validator,
  }) async {
    final textController = TextEditingController(text: initialValue);
    final formKey = GlobalKey<FormState>();

    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AppColors.cardBorder),
        ),
        title: Text(
          title,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: AppColors.onBackground,
                fontWeight: FontWeight.bold,
              ),
        ),
        content: Form(
          key: formKey,
          child: TextFormField(
            controller: textController,
            obscureText: isPassword,
            keyboardType: isEmail ? TextInputType.emailAddress : TextInputType.text,
            autofocus: true,
            style: const TextStyle(color: AppColors.onSurface),
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: const TextStyle(color: AppColors.onSurfaceVariant),
              filled: true,
              fillColor: AppColors.surfaceVariant,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.cardBorder),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.cardBorder),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.primary, width: 2),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.error),
              ),
            ),
            validator: validator ??
                (isPassword
                    ? (value) {
                        if (value == null || value.isEmpty) {
                          return 'Este campo é obrigatório';
                        }
                        if (value.length < 6) {
                          return 'A senha deve ter pelo menos 6 caracteres';
                        }
                        return null;
                      }
                    : isEmail
                        ? (value) {
                            if (value == null || value.isEmpty) {
                              return 'Este campo é obrigatório';
                            }
                            if (!value.contains('@') || !value.contains('.')) {
                              return 'Digite um e-mail válido';
                            }
                            return null;
                          }
                        : null),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              'Cancelar',
              style: TextStyle(color: AppColors.onSurfaceVariant),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              if (formKey.currentState!.validate()) {
                Navigator.of(context).pop(textController.text);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: AppColors.onPrimary,
            ),
            child: const Text('Confirmar'),
          ),
        ],
      ),
    );
  }

  void _startEditingName() {
    setState(() {
      _isEditingName = true;
    });
  }

  void _cancelEditingName() {
    setState(() {
      _isEditingName = false;
      _nameController.text = _originalName;
    });
  }

  Future<void> _saveProfileChanges() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final updateModel = UserProfileUpdate(
      name: _nameController.text.trim(),
    );

    final success = await authNotifier.updateUserProfile(updateModel);
    
    setState(() => _isSaving = false);

    if (success) {
      setState(() {
        _isEditingName = false;
        _originalName = _nameController.text.trim();
      });
      if (mounted) {
        FeedbackSnackBar.showSuccess(context, 'Perfil atualizado com sucesso!');
      }
    } else {
      if (mounted) {
        FeedbackSnackBar.showError(
          context,
          authNotifier.errorMessage ?? 'Ocorreu um erro desconhecido.',
        );
      }
    }
  }

  Future<void> _updateEmail() async {
    final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
    final currentEmail = authNotifier.userProfile?.email ?? '';

    final newEmail = await _showCustomInputDialog(
      title: 'Alterar E-mail',
      hint: 'Digite o novo e-mail',
      initialValue: currentEmail,
      isEmail: true,
    );

    if (newEmail == null || newEmail.isEmpty || newEmail == currentEmail) return;

    try {
      await _authService.updateEmail(newEmail);
      if (mounted) {
        FeedbackSnackBar.showSuccess(
          context,
          'Link de confirmação enviado para $newEmail. Verifique sua caixa de entrada.',
        );
      }
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login' && mounted) {
        FeedbackSnackBar.showWarning(
          context,
          'Por segurança, confirme sua senha atual.',
        );
        final password = await _showCustomInputDialog(
          title: 'Confirme sua Identidade',
          hint: 'Digite sua senha atual',
          isPassword: true,
        );
        if (password == null || password.isEmpty) return;
        try {
          await _authService.reauthenticateWithPassword(password);
          await _authService.updateEmail(newEmail);
          if (mounted) {
            FeedbackSnackBar.showSuccess(
              context,
              'Link de confirmação enviado para $newEmail. Verifique sua caixa de entrada.',
            );
          }
        } catch (error) {
          if (mounted) {
            FeedbackSnackBar.showError(context, 'Erro: $error');
          }
        }
      } else {
        if (mounted) {
          FeedbackSnackBar.showError(context, 'Erro do Firebase: ${e.message}');
        }
      }
    } catch (e) {
      if (mounted) {
        FeedbackSnackBar.showError(context, 'Erro inesperado: $e');
      }
    }
  }

  Future<void> _updatePassword() async {
    final newPassword = await _showCustomInputDialog(
      title: 'Alterar Senha',
      hint: 'Digite a nova senha',
      isPassword: true,
    );
    if (newPassword == null || newPassword.isEmpty) return;

    final confirmPassword = await _showCustomInputDialog(
      title: 'Confirmar Senha',
      hint: 'Digite a senha novamente',
      isPassword: true,
      validator: (value) {
        if (value != newPassword) {
          return 'As senhas não coincidem';
        }
        return null;
      },
    );
    if (confirmPassword == null || confirmPassword.isEmpty) return;

    try {
      await _authService.updatePassword(newPassword);
      if (mounted) {
        FeedbackSnackBar.showSuccess(context, 'Senha alterada com sucesso!');
      }
    } on FirebaseAuthException catch (e) {
      if (e.code == 'requires-recent-login' && mounted) {
        FeedbackSnackBar.showWarning(
          context,
          'Por segurança, confirme sua senha atual.',
        );
        final password = await _showCustomInputDialog(
          title: 'Confirme sua Identidade',
          hint: 'Digite sua senha atual',
          isPassword: true,
        );
        if (password == null || password.isEmpty) return;
        try {
          await _authService.reauthenticateWithPassword(password);
          await _authService.updatePassword(newPassword);
          if (mounted) {
            FeedbackSnackBar.showSuccess(context, 'Senha alterada com sucesso!');
          }
        } catch (error) {
          if (mounted) {
            FeedbackSnackBar.showError(context, 'Erro: $error');
          }
        }
      } else {
        if (mounted) {
          FeedbackSnackBar.showError(context, 'Erro do Firebase: ${e.message}');
        }
      }
    } catch (e) {
      if (mounted) {
        FeedbackSnackBar.showError(context, 'Erro inesperado: $e');
      }
    }
  }

  Future<void> _handleLogout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => ConfirmationDialog(
        title: 'Confirmar Saída',
        message: 'Tem certeza que deseja sair da sua conta?',
        confirmText: 'Sair',
        cancelText: 'Cancelar',
        confirmColor: AppColors.error,
        onConfirm: () => Navigator.of(context).pop(true),
        onCancel: () => Navigator.of(context).pop(false),
      ),
    );

    if (confirmed == true) {
      final authNotifier = Provider.of<AuthNotifier>(context, listen: false);
      authNotifier.logout();
      if (mounted) {
        Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
      }
    }
  }

  String _getInitials(String name) {
    if (name.isEmpty) return '?';
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name[0].toUpperCase();
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<AuthNotifier, RewardProvider>(
      builder: (context, authNotifier, rewardProvider, child) {
        final userProfile = authNotifier.userProfile;
        if (userProfile == null) {
          return Scaffold(
            backgroundColor: AppColors.background,
            appBar: AppBar(
              title: const Text('Meu Perfil'),
              backgroundColor: AppColors.primary,
            ),
            body: const Center(
              child: Text(
                'Usuário não encontrado.',
                style: TextStyle(color: AppColors.onSurface),
              ),
            ),
          );
        }

        // Carregar badges se necessário
        if (rewardProvider.userBadges.isEmpty && !rewardProvider.isLoading) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            rewardProvider.loadUserBadges();
          });
        }

        return Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(
            title: const Text('Meu Perfil'),
            centerTitle: true,
            backgroundColor: AppColors.primary,
            foregroundColor: AppColors.onPrimary,
            elevation: 0,
            actions: [
              IconButton(
                tooltip: 'Sair',
                icon: const Icon(Icons.logout),
                onPressed: _handleLogout,
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header do Perfil
                _buildProfileHeader(userProfile, rewardProvider),
                const SizedBox(height: 24),

                // Estatísticas Rápidas
                _buildQuickStats(userProfile, rewardProvider),
                const SizedBox(height: 24),

                // Nome de Exibição
                _buildDisplayNameSection(authNotifier),
                const SizedBox(height: 24),

                // Inteligência Artificial
                _buildAISection(),
                const SizedBox(height: 24),

                // Segurança
                _buildSecuritySection(userProfile),
                const SizedBox(height: 24),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildProfileHeader(UserProfile userProfile, RewardProvider rewardProvider) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          // Avatar
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.accent.withOpacity(0.2),
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.accent,
                width: 3,
              ),
            ),
            child: Center(
              child: Text(
                _getInitials(userProfile.name),
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: AppColors.accent,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Nome
          Text(
            userProfile.name,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppColors.onPrimary,
            ),
          ),
          const SizedBox(height: 8),
          // Email
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.email, size: 16, color: AppColors.onPrimary),
              const SizedBox(width: 8),
              Flexible(
                child: Text(
                  userProfile.email,
                  style: TextStyle(
                    fontSize: 14,
                    color: AppColors.onPrimary.withOpacity(0.9),
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Data de Cadastro
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.calendar_today, size: 14, color: AppColors.onPrimary),
              const SizedBox(width: 6),
              Text(
                'Membro desde ${_formatDate(userProfile.registerDate)}',
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.onPrimary.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(UserProfile userProfile, RewardProvider rewardProvider) {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.analytics, color: AppColors.accent, size: 20),
              const SizedBox(width: 8),
              Text(
                'Estatísticas',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.onBackground,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  'Nível',
                  '${userProfile.level}',
                  Icons.stars,
                  AppColors.accent,
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  'Pontos',
                  '${userProfile.points}',
                  Icons.emoji_events,
                  AppColors.warning,
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  'XP',
                  '${userProfile.xp}',
                  Icons.trending_up,
                  AppColors.success,
                ),
              ),
              Expanded(
                child: _buildStatItem(
                  'Badges',
                  '${rewardProvider.userBadges.length}',
                  Icons.workspace_premium,
                  AppColors.secondary,
                ),
              ),
            ],
          ),
          if (userProfile.currentStreak > 0) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.error.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(Icons.local_fire_department, color: AppColors.error, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Sequência: ${userProfile.currentStreak} dias',
                    style: TextStyle(
                      color: AppColors.onBackground,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.onBackground,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildDisplayNameSection(AuthNotifier authNotifier) {
    // Atualizar nome original se o perfil mudou
    if (!_isEditingName && authNotifier.userProfile?.name != null) {
      _originalName = authNotifier.userProfile!.name;
      if (_nameController.text != _originalName) {
        _nameController.text = _originalName;
      }
    }

    return GlassmorphismCard(
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.person, color: AppColors.primary, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Nome de Exibição',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.onBackground,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nameController,
              enabled: _isEditingName,
              readOnly: !_isEditingName,
              style: TextStyle(
                color: _isEditingName 
                    ? AppColors.onSurface 
                    : AppColors.onSurfaceVariant,
              ),
              decoration: InputDecoration(
                hintText: 'Digite seu nome',
                hintStyle: const TextStyle(color: AppColors.onSurfaceVariant),
                filled: true,
                fillColor: _isEditingName 
                    ? AppColors.surfaceVariant 
                    : AppColors.surfaceVariant.withOpacity(0.5),
                prefixIcon: Icon(
                  _isEditingName ? Icons.edit : Icons.person_outline,
                  color: _isEditingName 
                      ? AppColors.primary 
                      : AppColors.onSurfaceVariant,
                ),
                suffixIcon: !_isEditingName
                    ? null
                    : IconButton(
                        icon: const Icon(Icons.close, size: 20),
                        color: AppColors.onSurfaceVariant,
                        onPressed: _cancelEditingName,
                        tooltip: 'Cancelar',
                      ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: AppColors.cardBorder),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: _isEditingName 
                        ? AppColors.cardBorder 
                        : AppColors.cardBorder.withOpacity(0.5),
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: AppColors.primary, width: 2),
                ),
                disabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: AppColors.cardBorder.withOpacity(0.5),
                  ),
                ),
                errorBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: AppColors.error),
                ),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'O nome não pode estar vazio';
                }
                if (value.trim().length < 2) {
                  return 'O nome deve ter pelo menos 2 caracteres';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            if (!_isEditingName)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _startEditingName,
                  icon: const Icon(Icons.edit),
                  label: const Text('Alterar'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: AppColors.onPrimary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              )
            else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _isSaving ? null : _cancelEditingName,
                      icon: const Icon(Icons.close),
                      label: const Text('Cancelar'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.onSurfaceVariant,
                        side: const BorderSide(color: AppColors.cardBorder),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton.icon(
                      onPressed: _isSaving ? null : _saveProfileChanges,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: AppColors.onPrimary,
                              ),
                            )
                          : const Icon(Icons.save),
                      label: Text(_isSaving ? 'Salvando...' : 'Salvar'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: AppColors.onPrimary,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAISection() {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: AppColors.success, size: 20),
              const SizedBox(width: 8),
              Text(
                'Inteligência Artificial',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.onBackground,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          InkWell(
            onTap: () => Navigator.pushNamed(context, '/ai-profile'),
            borderRadius: BorderRadius.circular(12),
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.success.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.psychology, color: AppColors.success),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Meu Perfil de IA',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppColors.onBackground,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Veja como a IA analisa seu aprendizado',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.arrow_forward_ios,
                      color: AppColors.onSurfaceVariant, size: 16),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSecuritySection(UserProfile userProfile) {
    return GlassmorphismCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.security, color: AppColors.warning, size: 20),
              const SizedBox(width: 8),
              Text(
                'Segurança',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.onBackground,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildSecurityItem(
            icon: Icons.email,
            title: 'Alterar E-mail',
            subtitle: userProfile.email,
            onTap: _updateEmail,
            color: AppColors.info,
          ),
          const SizedBox(height: 12),
          _buildSecurityItem(
            icon: Icons.lock,
            title: 'Alterar Senha',
            subtitle: 'Atualize sua senha de acesso',
            onTap: _updatePassword,
            color: AppColors.warning,
          ),
        ],
      ),
    );
  }

  Widget _buildSecurityItem({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    required Color color,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: color.withOpacity(0.3),
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppColors.onBackground,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios,
                color: AppColors.onSurfaceVariant, size: 16),
          ],
        ),
      ),
    );
  }
}
