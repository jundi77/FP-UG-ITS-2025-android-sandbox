package its.android.analysis.lsposed.mods.watcher.watcher;

import android.app.Notification;
import android.app.NotificationManager;

import androidx.core.app.NotificationManagerCompat;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.NotificationCreateLogger;

public class NotificationActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "notification";

    public NotificationActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            java.lang.reflect.Method notifCreateWithTagMethod =
                    NotificationManager.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);
//                NotificationManager.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);

            module.hook(notifCreateWithTagMethod, NotificationCreateLogger.class);
            logHookSuccess(module, NotificationManager.class.getName(), notifCreateWithTagMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method notifCreateMethod =
                    NotificationManager.class.getDeclaredMethod("notify", int.class, Notification.class);
//                NotificationManager.class.getDeclaredMethod("notify", int.class, Notification.class);

            module.hook(notifCreateMethod, NotificationCreateLogger.class);
            logHookSuccess(module, NotificationManager.class.getName(), notifCreateMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method notifCompatCreateWithTagMethod =
                    NotificationManagerCompat.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);
//                NotificationManagerCompat.class.getDeclaredMethod("notify", String.class, int.class, Notification.class);

            module.hook(notifCompatCreateWithTagMethod, NotificationCreateLogger.class);
            logHookSuccess(module, NotificationManagerCompat.class.getName(), notifCompatCreateWithTagMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method notifCompatCreateMethod =
                    NotificationManagerCompat.class.getDeclaredMethod("notify", int.class, Notification.class);
//                NotificationManagerCompat.class.getDeclaredMethod("notify", int.class, Notification.class);

            module.hook(notifCompatCreateMethod, NotificationCreateLogger.class);
            logHookSuccess(module, NotificationManagerCompat.class.getName(), notifCompatCreateMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
