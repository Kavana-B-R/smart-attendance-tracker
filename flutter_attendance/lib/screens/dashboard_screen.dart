import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/attendance_provider.dart';
import 'attendance_history_screen.dart';
import 'register_screen.dart';

class DashboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard - ${auth.user?.name ?? ''}'),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => Provider.of<AuthProvider>(context, listen: false).logout(),
          ),
        ],
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(child: ListTile(title: Text('Today\'s Classes'), subtitle: Text('09:00 - Math'))),
            SizedBox(height: 20),
            Row(
              children: [
                Expanded(child: ElevatedButton(
                  onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => AttendanceHistoryScreen())),
                  child: Text('Attendance History'),
                )),
                SizedBox(width: 10),
                Expanded(child: ElevatedButton(
                  onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegisterScreen())),
                  child: Text('Register Face'),
                )),
              ],
            ),
            SizedBox(height: 20),
            Expanded(child: Consumer<AttendanceProvider>(
              builder: (context, att, child) => ListView(
                children: att.recent.map((a) => ListTile(
                  title: Text(a.subjectName),
                  subtitle: Text('${a.status} - ${a.date}'),
                  leading: Icon(a.status == 'present' ? Icons.check_circle : Icons.cancel, color: a.status == 'present' ? Colors.green : Colors.red),
                )).toList(),
              ),
            )),
          ],
        ),
      ),
    );
  }
}
