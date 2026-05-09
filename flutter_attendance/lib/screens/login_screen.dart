import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import 'dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usnController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Consumer<AuthProvider>(
          builder: (context, auth, child) {
            if (auth.isLoading) return Center(child: CircularProgressIndicator());
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextField(
                  controller: _usnController,
                  decoration: InputDecoration(labelText: 'USN/Username'),
                ),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: InputDecoration(labelText: 'Password'),
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: auth.isLoading ? null : () => _login(context),
                  child: Text('Login'),
                ),
                TextButton(
                  onPressed: () => Navigator.pushNamed(context, '/register'),
                  child: Text('Register'),
                ),
                if (auth.error != null) Text(auth.error!, style: TextStyle(color: Colors.red)),
              ],
            );
          },
        ),
      ),
    );
  }

  void _login(BuildContext context) async {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    await auth.login(_usnController.text, _passwordController.text);
    if (auth.isLoggedIn) {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => DashboardScreen()));
    }
  }
}
