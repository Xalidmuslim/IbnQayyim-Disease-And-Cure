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
        versionCode = 48
        versionName = "0.48.0"
    }

    buildTypes {
        getByName("debug") {
            // Preserve data in v44: GitHub Actions debug signing keys differ per run.
            applicationIdSuffix = ".preview48"
            versionNameSuffix = "-preview"
        }
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
