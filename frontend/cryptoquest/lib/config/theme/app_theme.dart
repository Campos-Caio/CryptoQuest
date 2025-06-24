import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

abstract class AppTheme {
  static ThemeData appTheme = ThemeData.dark().copyWith(
    primaryColor:const Color(0xFF7F5AF0),
    scaffoldBackgroundColor: const Color(0xFF16161A),
    textTheme: GoogleFonts.poppinsTextTheme(
      ThemeData.dark().textTheme, 
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFF242629),
      suffixIconColor: Colors.deepPurple, // cor do ícone dentro do textfield
      enabledBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: Colors.white),
        borderRadius: BorderRadius.circular(12),
      ),
      focusedBorder: OutlineInputBorder(
        borderSide: const BorderSide(color: Colors.deepPurple),
        borderRadius: BorderRadius.circular(12),
      ),
      hintStyle: const TextStyle(color: Color(0xFF94A1B2)),
    ),
  );
}
