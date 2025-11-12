// Top-level build file
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("com.android.library") version "8.1.0" apply false
    kotlin("android") version "1.9.10" apply false
    kotlin("jvm") version "1.9.10" apply false
}

tasks.register<Delete>("clean") {
    delete(rootProject.buildDir)
}
