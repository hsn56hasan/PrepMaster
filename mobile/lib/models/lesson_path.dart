/// Konu Yolu API yanıtı: status 0 ise bağlantı kurulamadı, 200 ise [data] doludur.
class PathResponse {
  final int status;
  final Map<String, dynamic>? data;
  final String? error;
  const PathResponse(this.status, this.data, this.error);

  bool get ok => status == 200 && data != null;
}
