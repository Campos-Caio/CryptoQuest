import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';

class CryptoCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget? icon;
  final Widget? trailing;

  const CryptoCard(
      {Key? key,
      required this.title,
      required this.subtitle,
      this.icon,
      this.trailing})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF7F5AF0),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          if (icon != null) icon!,
          const SizedBox(
            width: 12,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF00FFC8),
                  ),
                ),
                const SizedBox(
                  height: 4,
                ),
                Text(
                  subtitle,
                  style: TextStyle(color: Colors.white),
                ),
              ],
            ),
          ),
          if(trailing != null) trailing!, 
        ],
      ),
    );
  }
}
