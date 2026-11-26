# ML Kit metin tanıma: yalnızca Latin alfabesi paketini kullanıyoruz. Eklenti diğer alfabelerin
# (Çince, Devanagari, Japonca, Korece) sınıflarına derleme anında başvurur; bunlar APK'ya eklenmez.
-dontwarn com.google.mlkit.vision.text.chinese.**
-dontwarn com.google.mlkit.vision.text.devanagari.**
-dontwarn com.google.mlkit.vision.text.japanese.**
-dontwarn com.google.mlkit.vision.text.korean.**
