package its.android.analysis.lsposed.mods.watcher.watcher;

import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.IntentFilter;
import android.os.Handler;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;

public class ContextImplActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "context_broadcast";

    public ContextImplActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        // https://medium.com/@aliahmedrohan/how-to-auto-read-otp-in-android-programmatically-3fcb312ebf6a
        // https://androidacademic.blogspot.com/2017/01/read-sms-automatically-to-verify-otp.html

        // https://kevinboone.me/java_inner.html
        // possibility of BroadcastReceiver as an anonymous inner class

        // https://developer.android.com/reference/android/content/BroadcastReceiver
        // let's find any statement that runs Context.registerReceiver
        // as Context is an abstract class and registerReceiver is an abstract method, it cannot be hooked
        // https://github.com/frida/frida-java-bridge/issues/67#issuecomment-430529084
        // https://stackoverflow.com/questions/39122846/why-use-contextimpl-to-implement-context-rather-than-contextwrapper-in-android
        // let's hook ContextImpl, get the BroadcastReceiver from the registerReceiver parameters,
        // and hook that BroadcastReceiver object with BroadcastActionWatcher
        try {
            @SuppressLint("PrivateApi")
            Class<?> loadedContextImplClass = param.getClassLoader().loadClass("android.app.ContextImpl");

            try {
//                Context.class.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class);
                java.lang.reflect.Method contextRegisterReceiverMethod =
                        loadedContextImplClass.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class);

                module.hook(contextRegisterReceiverMethod, BroadcastActionWatcher.class);
                logHookSuccess(module, loadedContextImplClass.getName(), contextRegisterReceiverMethod.toString());
            } catch (NoSuchMethodException e) {
                logHookError(module, e);
            }

            try {
//                Context.class.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, int.class);
                java.lang.reflect.Method contextRegisterReceiverFlagsMethod =
                        loadedContextImplClass.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, int.class);

                module.hook(contextRegisterReceiverFlagsMethod, BroadcastActionWatcher.class);
                logHookSuccess(module, loadedContextImplClass.getName(), contextRegisterReceiverFlagsMethod.toString());
            } catch (NoSuchMethodException e) {
                logHookError(module, e);
            }

            try {
//                Context.class.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, String.class, Handler.class);
                java.lang.reflect.Method contextRegisterReceiverPermMethod =
                        loadedContextImplClass.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, String.class, Handler.class);

                module.hook(contextRegisterReceiverPermMethod, BroadcastActionWatcher.class);
                logHookSuccess(module, loadedContextImplClass.getName(), contextRegisterReceiverPermMethod.toString());
            } catch (NoSuchMethodException e) {
                logHookError(module, e);
            }

            try {
//                Context.class.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, String.class, Handler.class, int.class);
                java.lang.reflect.Method contextRegisterReceiverPermFlagsMethod =
                        loadedContextImplClass.getDeclaredMethod("registerReceiver", BroadcastReceiver.class, IntentFilter.class, String.class, Handler.class, int.class);

                module.hook(contextRegisterReceiverPermFlagsMethod, BroadcastActionWatcher.class);
                logHookSuccess(module, loadedContextImplClass.getName(), contextRegisterReceiverPermFlagsMethod.toString());
            } catch (NoSuchMethodException e) {
                logHookError(module, e);
            }

        } catch (ClassNotFoundException e) {
            logHookError(module, e);
        }
    }
}
