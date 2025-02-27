This is used as a hooking module of the sandbox in an AVD, utilizing [LSPosed_mod](https://github.com/mywalkb/LSPosed_mod) as a fork of [LSPosed](https://github.com/LSPosed/LSPosed), because it offers CLI's way to manage LSPosed module. [Magisk](https://github.com/topjohnwu/Magisk) is used as dependencies of LSPosed.

To compile, follow LSPosed's code to setup dependencies at [their GitHub Workflows file](https://github.com/LSPosed/LSPosed/blob/master/.github/workflows/core.yml#L74), specifically this line:

```
cd api
./gradlew publishToMavenLocal
cd ../service
./gradlew publishToMavenLocal
```

Beware of [libxposed/api issue for compiling](https://github.com/libxposed/api/issues/29). At the time this hooking module is created, it's needed to checkout old commit before [libxposed/api commit 7b67273](https://github.com/libxposed/api/commit/7b6727313cb4864618d3c5b9dcdfb9f4f9bb378a), as this commit introduce breaking internal changes related to `@XposedHooker`, `@BeforeInvocation`, and `@AfterInvocation` annotation previously required for hooker class.

Development follows LSPosed guide first, if it doesn't work then follow LSPosed_mod changes.

After compiling, copy the APK's to web `instance-setup` directory as `hooker.apk`.

If explanation on this readme doesn't suffice, please open an issue to discuss it publicly.
