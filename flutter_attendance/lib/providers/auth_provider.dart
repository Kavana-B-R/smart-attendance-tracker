import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthProvider with ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> login(String usn, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:5000/student/login'),  // Emulator
        body: {'student_id': usn, 'password': password},
      );
      if (response.statusCode == 200) {
        // Parse user data
        _user = User.fromJson(jsonDecode(response.body));
      } else {
        _error = 'Invalid credentials';
      }
    } catch (e) {
      _error = 'Network error';
    }
    
    _isLoading = false;
    notifyListeners();
  }

  void logout() {
    _user = null;
    notifyListeners();
  }
}

class User {
  final int id;
  final String username;
  final String name;
  final String role;

  User({required this.id, required this.username, required this.name, required this.role});

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    username: json['username'],
    name: json['name'],
    role: json['role'],
  );
}
