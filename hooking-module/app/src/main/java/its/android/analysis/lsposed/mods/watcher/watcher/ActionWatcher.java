package its.android.analysis.lsposed.mods.watcher.watcher;

import its.android.analysis.lsposed.mods.watcher.ModuleMain;

public abstract class ActionWatcher {
    public static final String LOG_TYPE = "watcher";
    public static String LOG_ACTION = "watch";

    protected static void logHookError(ModuleMain module, Exception e) {
        module.sendLog("hook", "error", e.toString());
    }

    protected static void logHookSuccess(ModuleMain module, String className, String methodName) {
        module.sendLog(LOG_TYPE, LOG_ACTION, "loaded on " + className + " on method " + methodName);
    }

    protected static void logModuleHookError(ModuleMain module, Exception e) {
        module.sendLocalLog("hook", "error", e.toString());
    }

    protected static void logModuleHookSuccess(ModuleMain module, String className, String methodName) {
        module.sendLocalLog(LOG_TYPE, LOG_ACTION, "loaded on " + className + " on method " + methodName);
    }
}
