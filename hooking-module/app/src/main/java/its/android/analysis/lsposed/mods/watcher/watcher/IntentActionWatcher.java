package its.android.analysis.lsposed.mods.watcher.watcher;

import android.content.Intent;
import android.net.Uri;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.IntentLaunchLogger;

public class IntentActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "intent";

    public IntentActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            java.lang.reflect.Method intentLaunchMethod = Intent.class.getDeclaredMethod(
                    "setDataAndType",
                    Uri.class,
                    String.class
            );
//                Intent.class.getDeclaredMethod("setDataAndType", Uri.class, String.class);
            module.hook(intentLaunchMethod, IntentLaunchLogger.class);
            logHookSuccess(module, Intent.class.getName(), intentLaunchMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
