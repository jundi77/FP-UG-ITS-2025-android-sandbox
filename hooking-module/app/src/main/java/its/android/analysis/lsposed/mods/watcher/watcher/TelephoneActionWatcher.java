package its.android.analysis.lsposed.mods.watcher.watcher;

import android.telephony.PhoneStateListener;
import android.telephony.TelephonyManager;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.TelephoneCallLogger;

public class TelephoneActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "telephone";

    public TelephoneActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            // https://developer.android.com/reference/android/telephony/TelephonyManager#listen(android.telephony.PhoneStateListener,%20int)
            // deprecated in api level 31
            java.lang.reflect.Method teleListenMethod =
                    TelephonyManager.class.getDeclaredMethod("listen", PhoneStateListener.class, int.class);
//                 TelephonyManager.class.getDeclaredMethod("listen", PhoneStateListener.class, int.class);

            module.hook(teleListenMethod, TelephoneCallLogger.class);
            logHookSuccess(module, TelephonyManager.class.getName(), teleListenMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
