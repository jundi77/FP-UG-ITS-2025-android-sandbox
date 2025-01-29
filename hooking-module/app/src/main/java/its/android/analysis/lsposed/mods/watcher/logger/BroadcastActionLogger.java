package its.android.analysis.lsposed.mods.watcher.logger;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.NonNull;

import java.util.HashMap;
import java.util.Map;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.BroadcastIntentModel;
import its.android.analysis.lsposed.mods.watcher.watcher.BroadcastActionWatcher;

@XposedHooker
public class BroadcastActionLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "receive_broadcast";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        BroadcastReceiver.class.getDeclaredMethod("onReceive", Context.class, Intent.class);

        Object[] methodArgs = callback.getArgs();
        Intent receivedIntent = (Intent) methodArgs[1];

        Bundle extras = receivedIntent.getExtras();
        if (extras != null) {
            Map<String, Object> extrasMaps = new HashMap<String, Object>();
            for (String key : extras.keySet()) {
                extrasMaps.put(key, extras.get(key));
            }
            module.sendLog(
                    BroadcastActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "app received a broadcast",
                    new BroadcastIntentModel(receivedIntent.getAction(), extrasMaps)
            );
        } else {
            module.sendLog(
                    BroadcastActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "app received a broadcast",
                    new BroadcastIntentModel(receivedIntent.getAction())
            );
        }
    }
}
