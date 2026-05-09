import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class RegisterScreen extends StatefulWidget {
  @override
  _RegisterScreenState createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usnController = TextEditingController();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  List<File> facePhotos = [];
  bool isRegistering = false;

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        facePhotos.add(File(pickedFile.path));
      });
    }
  }

  Future<void> _submitRegistration() async {
    if (facePhotos.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Need 2-5 photos')));
      return;
    }
    setState(() { isRegistering = true; });

    try {
      // Simulate face encoding (real app would encode locally or send raw)
      List<Map<String, dynamic>> encodings = [];
      for (var photo in facePhotos) {
        var bytes = await photo.readAsBytes();
        encodings.add({'data': base64Encode(bytes), 'timestamp': DateTime.now().toIso8601String()});
      }

      final response = await http.post(
        Uri.parse('http://10.0.2.2:5000/register_pending'),  // Emulator localhost
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'usn': _usnController.text,
          'name': _nameController.text,
          'email': _emailController.text,
          'face_encodings': encodings,
        }),
      );

      if (response.statusCode == 200) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Submitted for approval')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${response.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Network error')));
    }

    setState(() { isRegistering = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Register (2-5 Photos)')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: SingleChildScrollView(
          child: Column(
            children: [
              TextField(controller: _usnController, decoration: InputDecoration(labelText: 'USN')),
              TextField(controller: _nameController, decoration: InputDecoration(labelText: 'Name')),
              TextField(controller: _emailController, decoration: InputDecoration(labelText: 'Email')),
              SizedBox(height: 20),
              Text('${facePhotos.length} photos captured (need 2-5)', style: Theme.of(context).textTheme.titleMedium),
              SizedBox(height: 10),
              GridView.builder(
                shrinkWrap: true,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3),
                itemCount: facePhotos.length,
                itemBuilder: (context, index) => Image.file(facePhotos[index], fit: BoxFit.cover),
              ),
              SizedBox(height: 20),
              Row(
                children: [
                  Expanded(child: FloatingActionButton(
                    heroTag: 'camera',
                    onPressed: () => _pickImage(ImageSource.camera),
                    child: Icon(Icons.camera),
                  )),
                  SizedBox(width: 10),
                  Expanded(child: FloatingActionButton(
                    heroTag: 'gallery',
                    onPressed: () => _pickImage(ImageSource.gallery),
                    child: Icon(Icons.photo_library),
                  )),
                ],
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: isRegistering ? null : _submitRegistration,
                child: isRegistering ? CircularProgressIndicator() : Text('Submit for Approval'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
