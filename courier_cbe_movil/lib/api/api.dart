import 'dart:io';

String getBaseUrl() {
  const String localIp = "192.168.21.143"; // Tu IP local (sin / al final)
  const String fallbackIp = "127.0.0.1"; // IP de respaldo
  const String puerto = "8000";

  try {
    if (Platform.isAndroid) {
      // En Android, usa la IP local primero, si falla, usa la IP de respaldo
      return "http://$localIp:$puerto";  // Si no funciona, intenta fallbackIp
    } else {
      // En otros sistemas (como iOS o web), usa la IP de la máquina local
      return "http://$fallbackIp:$puerto";
    }
  } catch (e) {
    // Si algo falla, usa la IP de respaldo
    return "http://$fallbackIp:$puerto";
  }
}

final String API_URL = getBaseUrl();
final String LOGIN_URL = "$API_URL/usuarios/login/";
final String PERFIL_URL = "$API_URL/usuarios/perfil/";
