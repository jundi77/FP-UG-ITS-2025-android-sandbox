package its.android.analysis.lsposed.mods.watcher.logger;

import androidx.annotation.NonNull;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.SmsSendModel;
import its.android.analysis.lsposed.mods.watcher.watcher.SmsActionWatcher;

@XposedHooker
public class SmsCreateLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "send";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        SmsManager.class.getDeclaredMethod("sendTextMessage", String.class, String.class, String.class, PendingIntent.class, PendingIntent.class);
//        SmsManager.class.getDeclaredMethod("sendDataMessage", String.class, String.class, short.class, byte[].class, PendingIntent.class, PendingIntent.class);
        Object[] methodArgs = callback.getArgs();

        String destAddress = (String) methodArgs[0];
        Object msg = methodArgs.length == 6? (byte[]) methodArgs[3] : (String) methodArgs[2];
        String port =  methodArgs.length == 6? methodArgs[2].toString() : null;

        module.sendLog(
                SmsActionWatcher.LOG_TYPE,
                LOG_ACTION,
                "app is sending an sms",
                new SmsSendModel(
                        destAddress,
                        msg,
                        port
                )
        );
    }
}
