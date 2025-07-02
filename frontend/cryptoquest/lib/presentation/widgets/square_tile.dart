import 'package:flutter/material.dart';

class SquareTile extends StatelessWidget {
  final String imagePath;
  final Function()? auth;

  const SquareTile({super.key, required this.imagePath, required this.auth});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: auth,
      child: Container(
        padding: EdgeInsets.all(20),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.white),
          borderRadius: BorderRadius.circular(16),
          color: Colors.grey[200],
        ),
        child: Image.asset(imagePath, height: 40),
      ),
    );
  }
}
