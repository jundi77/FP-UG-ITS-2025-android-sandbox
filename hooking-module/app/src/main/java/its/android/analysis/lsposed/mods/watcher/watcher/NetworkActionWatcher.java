package its.android.analysis.lsposed.mods.watcher.watcher;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.NetworkUsageLogger;

public class NetworkActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "network";

    public NetworkActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            java.lang.reflect.Method netUsageMethod =
                    java.net.URL.class.getDeclaredMethod("openConnection");

            module.hook(netUsageMethod, NetworkUsageLogger.class);
            logHookSuccess(module, java.net.URL.class.getName(), netUsageMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
