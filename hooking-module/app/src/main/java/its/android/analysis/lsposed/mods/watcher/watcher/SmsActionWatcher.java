package its.android.analysis.lsposed.mods.watcher.watcher;

import android.app.PendingIntent;
import android.telephony.SmsManager;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.SmsCreateLogger;

public class SmsActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "sms";

    public SmsActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            java.lang.reflect.Method smsManagerSendTextMethod = SmsManager.class.getDeclaredMethod(
                    "sendTextMessage",
                    String.class,
                    String.class,
                    String.class,
                    PendingIntent.class,
                    PendingIntent.class
            );
//                SmsManager.class.getDeclaredMethod("sendTextMessage", String.class, String.class, String.class, PendingIntent.class, PendingIntent.class);

            module.hook(smsManagerSendTextMethod, SmsCreateLogger.class);
            logHookSuccess(module, SmsManager.class.getName(), smsManagerSendTextMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method smsManagerSendDataMethod = SmsManager.class.getDeclaredMethod(
                    "sendDataMessage",
                    String.class,
                    String.class,
                    short.class,
                    byte[].class,
                    PendingIntent.class,
                    PendingIntent.class
            );
    //                SmsManager.class.getDeclaredMethod("sendDataMessage", String.class, String.class, short.class, byte[].class, PendingIntent.class, PendingIntent.class);

            module.hook(smsManagerSendDataMethod, SmsCreateLogger.class);
            logHookSuccess(module, SmsManager.class.getName(), smsManagerSendDataMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
