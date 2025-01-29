package its.android.analysis.lsposed.mods.watcher.logger;

import android.app.Notification;
import android.os.Bundle;

import androidx.annotation.NonNull;

import java.util.HashMap;
import java.util.Map;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.BroadcastIntentModel;
import its.android.analysis.lsposed.mods.watcher.logger.model.NotificationNotifyModel;
import its.android.analysis.lsposed.mods.watcher.watcher.BroadcastActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.NotificationActionWatcher;

@XposedHooker
public class NotificationCreateLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "notify";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
//        if (module == null) return;
        if (module == null) throw new RuntimeException("");

//        NotificationManager.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);
//        NotificationManager.class.getDeclaredMethod("notify", int.class, Notification.class);
//        NotificationManagerCompat.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);
//        NotificationManagerCompat.class.getDeclaredMethod("notify", int.class, Notification.class);
        Object[] methodArgs = callback.getArgs();

        String tag =
                methodArgs.length == 3? (String) methodArgs[0] : null;
        int id =
                methodArgs.length == 3? (int) methodArgs[1] : (int) methodArgs[0];
        Notification notification =
                (Notification) methodArgs[methodArgs.length - 1];
        if (notification != null) {
            Bundle extras = notification.extras;

            if (extras != null) {
                Map<String, Object> extrasMaps = new HashMap<String, Object>();
                for (String key : extras.keySet()) {
                    extrasMaps.put(key, extras.get(key));
                }
                module.sendLog(
                        NotificationActionWatcher.LOG_TYPE,
                        LOG_ACTION,
                        "app is notifying user",
                        new NotificationNotifyModel(
                                tag,
                                id,
                                notification.toString(),
                                extrasMaps
                        )
                );
            } else {
                module.sendLog(
                        NotificationActionWatcher.LOG_TYPE,
                        LOG_ACTION,
                        "app is notifying user",
                        new NotificationNotifyModel(
                                tag,
                                id,
                                notification.toString()
                        )
                );
            }
        }

        module.sendLog(
                NotificationActionWatcher.LOG_TYPE,
                LOG_ACTION,
                "app is notifying user",
                new NotificationNotifyModel(
                        tag,
                        id,
                        ""
                )
        );
    }
}
