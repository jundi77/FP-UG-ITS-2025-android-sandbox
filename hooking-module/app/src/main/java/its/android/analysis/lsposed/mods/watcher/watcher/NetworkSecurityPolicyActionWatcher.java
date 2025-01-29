package its.android.analysis.lsposed.mods.watcher.watcher;

import android.security.NetworkSecurityPolicy;

import androidx.annotation.NonNull;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.XposedModuleInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.api.WatcherLogAPI;

@XposedHooker
public class NetworkSecurityPolicyActionWatcher extends ActionWatcher implements XposedInterface.Hooker {
    public static final String LOG_TYPE = "network_security_policy";
    public static final String HOOK_LOG_ACTION = "set_log_server_cleartext";

    public NetworkSecurityPolicyActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {
        try {
            java.lang.reflect.Method networkIsCleartextPermitted =
                    NetworkSecurityPolicy.class.getDeclaredMethod("isCleartextTrafficPermitted", String.class);
            module.hook(networkIsCleartextPermitted, NetworkSecurityPolicyActionWatcher.class);
            // don't send log there as isCleartextTrafficPermitted may return false at this point
        } catch (NoSuchMethodException e) {
            throw new RuntimeException(e);
        }

        // fallback if the app does not care what hostname it request, but honors cleartext permission
        try {
            java.lang.reflect.Method networkIsCleartextPermitted =
                    NetworkSecurityPolicy.class.getDeclaredMethod("isCleartextTrafficPermitted");
            module.hook(networkIsCleartextPermitted, NetworkSecurityPolicyActionWatcher.class);
            // don't send log there as isCleartextTrafficPermitted may return false at this point
            // just log to xposed module
            logModuleHookSuccess(module, NetworkSecurityPolicy.class.getName(), networkIsCleartextPermitted.toString());
        } catch (NoSuchMethodException e) {
            logModuleHookError(module, e);
        }
    }

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // ModuleMain is somehow isn't instantiated
        if (module == null) return;

        Object[] args = callback.getArgs();

        // if the app does not care what hostname it request, allow cleartext permission
        if (args.length == 0) {
            callback.returnAndSkip(true);
//            module.sendLocalLog(LOG_TYPE, HOOK_LOG_ACTION, "set cleartext for all hostname");
        }

        switch ((String) args[0]) {
            case WatcherLogAPI.LOCAL_IP_HOST:
            case WatcherLogAPI.LOCAL_NAME_HOST:
            case WatcherLogAPI.WLAN_HOST:
            case WatcherLogAPI.VM_HOST:
                callback.returnAndSkip(true);
//                module.sendLocalLog(LOG_TYPE, HOOK_LOG_ACTION, "set cleartext for hostname " + args[0]);
                break;
            default:
                // don't modify for other hostname
                break;
        }
    }
}
