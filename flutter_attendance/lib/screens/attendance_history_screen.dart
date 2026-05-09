import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/attendance_provider.dart';

class AttendanceHistoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Attendance History')),
      body: Consumer<AttendanceProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) return Center(child: CircularProgressIndicator());
          return ListView.builder(
            itemCount: provider.history.length,
            itemBuilder: (context, index) {
              final att = provider.history[index];
              return Card(
                child: ListTile(
                  title: Text(att.subjectName ?? 'Subject'),
                  subtitle: Text('${att.date} | ${att.status}'),
                  leading: CircleAvatar(
                    backgroundColor: att.status == 'present' ? Colors.green : Colors.red,
                    child: Text(att.status![0].toUpperCase()),
                  ),
                  trailing: att.faceVerified 
                    ? Icon(Icons.verified, color: Colors.blue) 
                    : Icon(Icons.block),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Provider.of<AttendanceProvider>(context, listen: false).refresh(),
        child: Icon(Icons.refresh),
      ),
    );
  }
}
