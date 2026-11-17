import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

/// Uygulama içinde bir web sayfası açar (KVKK, sözleşmeler, PayTR ödeme sayfası).
///
/// [stopWhenUrlContains] verilirse sayfa o adrese gittiğinde ekran kapanır ve `true` döner
/// (ör. PayTR ödeme bitince sitedeki /odeme-sonuc sayfasına yönlendirir).
class WebPageScreen extends StatefulWidget {
  final String title;
  final String url;
  final String? stopWhenUrlContains;

  const WebPageScreen({
    super.key,
    required this.title,
    required this.url,
    this.stopWhenUrlContains,
  });

  static Future<bool?> open(BuildContext context, {required String title, required String url, String? stopWhenUrlContains}) {
    return Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => WebPageScreen(title: title, url: url, stopWhenUrlContains: stopWhenUrlContains),
      ),
    );
  }

  @override
  State<WebPageScreen> createState() => _WebPageScreenState();
}

class _WebPageScreenState extends State<WebPageScreen> {
  late final WebViewController _controller;
  bool _loading = true;
  bool _finished = false;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) => setState(() => _loading = true),
          onPageFinished: (_) => setState(() => _loading = false),
          onNavigationRequest: (req) {
            final stop = widget.stopWhenUrlContains;
            if (stop != null && req.url.contains(stop) && !_finished) {
              _finished = true;
              Navigator.of(context).pop(true);
              return NavigationDecision.prevent;
            }
            // Yalnızca güvenli (https) sayfalar
            return req.url.startsWith('https://') ? NavigationDecision.navigate : NavigationDecision.prevent;
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        bottom: _loading
            ? const PreferredSize(preferredSize: Size.fromHeight(2), child: LinearProgressIndicator(minHeight: 2))
            : null,
      ),
      body: WebViewWidget(controller: _controller),
    );
  }
}
