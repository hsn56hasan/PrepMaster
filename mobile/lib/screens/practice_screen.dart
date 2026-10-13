import 'package:flutter/material.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class PracticeScreen extends StatefulWidget {
  final String currentLevel;

  const PracticeScreen({super.key, required this.currentLevel});

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  late String _selectedLevel;
  List<Question> _questions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _selectedLevel = widget.currentLevel;
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    setState(() => _isLoading = true);
    final list = await ApiService().getQuestions(level: _selectedLevel);
    if (mounted) {
      setState(() {
        _questions = list;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kur Alıştırmaları (A1 - C2)'),
      ),
      body: Column(
        children: [
          // Level selector
          Container(
            height: 48,
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'all'].map((lvl) {
                final isSel = _selectedLevel == lvl;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(lvl.toUpperCase()),
                    selected: isSel,
                    onSelected: (_) {
                      setState(() => _selectedLevel = lvl);
                      _loadQuestions();
                    },
                    selectedColor: AppTheme.brandBlue,
                    labelStyle: TextStyle(
                      color: isSel ? Colors.white : AppTheme.textMain,
                      fontWeight: FontWeight.w800,
                      fontSize: 12,
                    ),
                    backgroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                );
              }).toList(),
            ),
          ),

          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _questions.isEmpty
                    ? Center(
                        child: Text(
                          'Bu seviyede ($_selectedLevel) soru bulunamadı.',
                          style: const TextStyle(color: AppTheme.textMuted),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _questions.length,
                        itemBuilder: (context, i) {
                          final q = _questions[i];
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 16),
                            child: Container(
                              padding: const EdgeInsets.all(18),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(color: AppTheme.borderSubtle),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                            decoration: BoxDecoration(
                                              color: AppTheme.brandLightBlue,
                                              borderRadius: BorderRadius.circular(6),
                                            ),
                                            child: Text(
                                              q.category,
                                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppTheme.brandBlue),
                                            ),
                                          ),
                                          const SizedBox(width: 6),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                            decoration: BoxDecoration(
                                              color: Colors.grey.shade100,
                                              borderRadius: BorderRadius.circular(6),
                                            ),
                                            child: Text(
                                              q.level,
                                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textMuted),
                                            ),
                                          ),
                                        ],
                                      ),
                                      Text(
                                        q.universityId.toUpperCase(),
                                        style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: AppTheme.textMuted),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 12),

                                  if (q.passage != null && q.passage!.isNotEmpty) ...[
                                    Container(
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.grey.shade50,
                                        borderRadius: BorderRadius.circular(12),
                                        border: Border.all(color: Colors.grey.shade200),
                                      ),
                                      child: Text(
                                        q.passage!,
                                        style: const TextStyle(fontSize: 12, height: 1.5, color: Color(0xFF475569)),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                  ],

                                  Text(
                                    q.question,
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.textMain),
                                  ),
                                  const SizedBox(height: 12),

                                  ...q.options.map((opt) {
                                    return Padding(
                                      padding: const EdgeInsets.only(bottom: 6),
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                        decoration: BoxDecoration(
                                          color: Colors.grey.shade50,
                                          borderRadius: BorderRadius.circular(12),
                                          border: Border.all(color: AppTheme.borderSubtle),
                                        ),
                                        child: Row(
                                          children: [
                                            Text('${opt.key}) ', style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12)),
                                            Expanded(child: Text(opt.text, style: const TextStyle(fontSize: 12))),
                                          ],
                                        ),
                                      ),
                                    );
                                  }),
                                  const SizedBox(height: 8),

                                  Theme(
                                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                                    child: ExpansionTile(
                                      tilePadding: EdgeInsets.zero,
                                      title: Row(
                                        children: const [
                                          Icon(Icons.help_outline_rounded, size: 16, color: AppTheme.brandBlue),
                                          SizedBox(width: 6),
                                          Text(
                                            'Doğru Cevap ve Çözümü Gör',
                                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTheme.brandBlue),
                                          ),
                                        ],
                                      ),
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.all(12),
                                          decoration: BoxDecoration(
                                            color: Colors.green.shade50,
                                            borderRadius: BorderRadius.circular(12),
                                            border: Border.all(color: Colors.green.shade200),
                                          ),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                'Doğru Cevap: ${q.correctAnswer}',
                                                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: AppTheme.accentEmerald),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(
                                                q.explanationTr,
                                                style: const TextStyle(fontSize: 12, height: 1.4, color: Color(0xFF064E3B)),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
