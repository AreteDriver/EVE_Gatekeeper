# Keep Compose classes
-keep class androidx.compose.** { *; }
-keep class androidx.navigation.** { *; }

# Keep Retrofit
-keepclasseswithmembernames class * {
    @retrofit2.http.* <methods>;
}

# Keep kotlinx.serialization
-keepclassmembers class * {
    *** Companion;
}
-keepclasseswithmembers class * {
    @kotlinx.serialization.Serializable <methods>;
}
-keep,includedescriptorclasses class com.evemap.**$$serializer { *; }
-keepclassmembers class com.evemap.** {
    *** Companion;
}

# Keep okhttp
-dontwarn okhttp3.**
-dontwarn okio.**

# Keep lifecycle
-keep class androidx.lifecycle.** { *; }
