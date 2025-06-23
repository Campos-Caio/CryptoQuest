import 'package:flutter/material.dart';

abstract class AppTheme {
  static ThemeData appTheme = ThemeData.dark().copyWith(
    primaryColor: Colors.deepPurple,
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.grey.shade200,
      suffixIconColor: Colors.deepPurple, // cor do ícone dentro do textfield
      enabledBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: Colors.white),
        borderRadius: BorderRadius.circular(12),
      ),
      focusedBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: Colors.deepPurple),
        borderRadius: BorderRadius.circular(12),
      ),
      hintStyle: const TextStyle(color: Colors.grey),
    ),
  );
}
