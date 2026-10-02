import 'package:flutter/material.dart';

class DashboardScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard'),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacementNamed(context, '/'),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.verified_user, size: 100, color: Colors.green),
            SizedBox(height: 20),
            Text(
              'Login Successful!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              'The camera feature requires mobile setup.',
              style: TextStyle(color: Colors.grey),
            ),
            SizedBox(height: 30),
            ElevatedButton(
              onPressed: () {
                // This would navigate to camera screen
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Camera requires Android/iOS setup')),
                );
              },
              child: Text('Go to Camera (Mobile Only)'),
            ),
          ],
        ),
      ),
    );
  }
}