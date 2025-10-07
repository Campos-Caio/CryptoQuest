import 'package:flutter/material.dart';
import 'package:cryptoquest/core/config/theme/app_colors.dart';

/// Item do bottom navigation
class BottomNavItem {
  final String label;
  final IconData icon;
  final IconData? activeIcon;
  final String route;
  final int index;

  const BottomNavItem({
    required this.label,
    required this.icon,
    this.activeIcon,
    required this.route,
    required this.index,
  });
}

/// Bottom Navigation Bar customizado
class AppBottomNavigationBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<BottomNavItem> items;

  const AppBottomNavigationBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: const Border(
          top: BorderSide(color: AppColors.cardBorder, width: 1),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: items.map((item) {
              final isSelected = currentIndex == item.index;
              return Expanded(
                child: GestureDetector(
                  onTap: () => onTap(item.index),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeInOut,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.primary.withOpacity(0.1)
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          curve: Curves.easeInOut,
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? AppColors.primary
                                : Colors.transparent,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Icon(
                            isSelected
                                ? (item.activeIcon ?? item.icon)
                                : item.icon,
                            color: isSelected
                                ? AppColors.onPrimary
                                : AppColors.onSurfaceVariant,
                            size: 24,
                          ),
                        ),
                        const SizedBox(height: 4),
                        AnimatedDefaultTextStyle(
                          duration: const Duration(milliseconds: 200),
                          style: TextStyle(
                            color: isSelected
                                ? AppColors.primary
                                : AppColors.onSurfaceVariant,
                            fontSize: 12,
                            fontWeight: isSelected
                                ? FontWeight.w600
                                : FontWeight.normal,
                          ),
                          child: Text(item.label),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }
}

/// Widget para páginas com bottom navigation
class BottomNavigationWrapper extends StatefulWidget {
  final List<BottomNavItem> items;
  final List<Widget> pages;
  final int initialIndex;
  final String? title;

  const BottomNavigationWrapper({
    super.key,
    required this.items,
    required this.pages,
    this.initialIndex = 0,
    this.title,
  });

  @override
  State<BottomNavigationWrapper> createState() =>
      _BottomNavigationWrapperState();
}

class _BottomNavigationWrapperState extends State<BottomNavigationWrapper> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  void _onItemTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: widget.title != null
          ? AppBar(
              title: Text(widget.title!),
              backgroundColor: AppColors.primary,
              foregroundColor: AppColors.onPrimary,
              elevation: 0,
              centerTitle: true,
            )
          : null,
      body: IndexedStack(
        index: _currentIndex,
        children: widget.pages,
      ),
      bottomNavigationBar: AppBottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onItemTapped,
        items: widget.items,
      ),
    );
  }
}

/// Configuração padrão dos itens de navegação
class AppNavigationItems {
  static const List<BottomNavItem> mainItems = [
    BottomNavItem(
      label: 'Início',
      icon: Icons.home_outlined,
      activeIcon: Icons.home,
      route: '/home',
      index: 0,
    ),
    BottomNavItem(
      label: 'Missões',
      icon: Icons.assignment_outlined,
      activeIcon: Icons.assignment,
      route: '/missions',
      index: 1,
    ),
    BottomNavItem(
      label: 'Trilhas',
      icon: Icons.school_outlined,
      activeIcon: Icons.school,
      route: '/learning-paths',
      index: 2,
    ),
    BottomNavItem(
      label: 'Ranking',
      icon: Icons.leaderboard_outlined,
      activeIcon: Icons.leaderboard,
      route: '/ranking',
      index: 3,
    ),
    BottomNavItem(
      label: 'Recompensas',
      icon: Icons.card_giftcard_outlined,
      activeIcon: Icons.card_giftcard,
      route: '/rewards',
      index: 4,
    ),
  ];
}
