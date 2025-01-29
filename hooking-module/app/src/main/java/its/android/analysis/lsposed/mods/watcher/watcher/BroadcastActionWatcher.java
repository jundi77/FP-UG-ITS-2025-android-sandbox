package its.android.analysis.lsposed.mods.watcher.watcher;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import androidx.annotation.NonNull;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.BroadcastActionLogger;

@XposedHooker
public class BroadcastActionWatcher extends ActionWatcher implements XposedInterface.Hooker {
    public static final String LOG_TYPE = "broadcast";
    public static final String HOOK_LOG_ACTION = "snatch";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // ModuleMain somehow isn't instantiated
        if (module == null) return;

        // any statement that runs Context.registerReceiver have BroadcastReceiver,
        // hook that BroadcastReceiver class
        BroadcastReceiver loadedBroadcastReceiverObject = (BroadcastReceiver) callback.getArgs()[0];
        if (loadedBroadcastReceiverObject == null) return;
        module.sendLog(LOG_TYPE, HOOK_LOG_ACTION, loadedBroadcastReceiverObject.toString());

        try {
            java.lang.reflect.Method onReceiveMethod =
                    loadedBroadcastReceiverObject.getClass().getDeclaredMethod("onReceive", Context.class, Intent.class);
//            BroadcastReceiver.class.getDeclaredMethod("onReceive", Context.class, Intent.class);

            module.hook(onReceiveMethod, BroadcastActionLogger.class);
            logHookSuccess(module, loadedBroadcastReceiverObject.getClass().getName(), onReceiveMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
