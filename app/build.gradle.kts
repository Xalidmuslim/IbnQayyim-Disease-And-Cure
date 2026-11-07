plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.xalidmuslim.diseaseandcure"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.xalidmuslim.diseaseandcure"
        minSdk = 26
        targetSdk = 35
        versionCode = 45
        versionName = "0.45.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { buildConfig = true }
}
