import 'dart:convert';
import 'api_client.dart';

class AuthService {
  static Future<bool> login(String email, String password, {String? mfaCode}) async {
    final res = await ApiClient.post('/auth/login', {
      'email': email,
      'password': password,
      if (mfaCode != null) 'mfa_code': mfaCode,
    });
    if (res.statusCode != 200) return false;
    final data = jsonDecode(res.body);
    if (data['mfa_required'] == true) return false;
    await ApiClient.saveTokens(data['access_token'], data['refresh_token']);
    return true;
  }

  static Future<Map<String, dynamic>?> me() async {
    final res = await ApiClient.get('/auth/me');
    if (res.statusCode != 200) return null;
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<void> logout() async {
    await ApiClient.clearTokens();
  }
}
