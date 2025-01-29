package its.android.analysis.lsposed.mods.watcher;

import androidx.annotation.NonNull;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.XposedModule;
import its.android.analysis.lsposed.mods.watcher.api.WatcherLogAPIClient;
import its.android.analysis.lsposed.mods.watcher.watcher.ContextImplActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.FileActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.IntentActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.NetworkActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.NetworkSecurityPolicyActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.NotificationActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.SmsActionWatcher;
import its.android.analysis.lsposed.mods.watcher.watcher.TelephoneActionWatcher;

public class ModuleMain extends XposedModule {

    private static ModuleMain instance;

    public static ModuleMain getInstance() {
        return instance;
    }

    /**
     * Instantiates a new Xposed module.<br/>
     * When the module is loaded into the target process, the constructor will be called.
     *
     * @param base  The implementation interface provided by the framework, should not be used by the module
     * @param param Information about the process in which the module is loaded
     */
    public ModuleMain(XposedInterface base, ModuleLoadedParam param) {
        super(base, param);

        log("Module test " + param.getProcessName());
        instance = this;
    }

    @Override
    public void onPackageLoaded(@NonNull PackageLoadedParam param) {
        super.onPackageLoaded(param);

        log("onPackageLoaded: " + param.getPackageName());
        log("param classloader: " + param.getClassLoader());
        log("module apk path: " + this.getApplicationInfo().sourceDir);
        log("---------------------");

        if (!param.isFirstPackage()) return;

        // Hook network security cleartext permission check so that log can be send to log server
        // with cleartext
        new NetworkSecurityPolicyActionWatcher(this, param);

        // BroadcastActionWatcher is called from ContextImplActionWatcher
        new ContextImplActionWatcher(this, param);
        new FileActionWatcher(this, param);
        new IntentActionWatcher(this, param);
        new NetworkActionWatcher(this, param);
        new NotificationActionWatcher(this, param);
        new SmsActionWatcher(this, param);
        new TelephoneActionWatcher(this, param);
    }

    public long getLogTimestamp() {
        return System.currentTimeMillis();
    }

    public void sendLocalLog(String type, String action, String msg) {
        log(String.format("[watcher] [%s] [%s] [%s] %s", getLogTimestamp(), type, action, msg));
    }

    public void sendLocalLog(String type, String action, String msg, Object data) {
        log(String.format("[watcher] [%s] [%s] [%s] %s [%s]", getLogTimestamp(), type, action, msg, data));
    }

    public void sendLocalLog(long timestamp, String type, String action, String msg) {
        log(String.format("[watcher] [%s] [%s] [%s] %s", timestamp, type, action, msg));
    }

    public void sendLocalLog(long timestamp, String type, String action, String msg, Object data) {
        log(String.format("[watcher] [%s] [%s] [%s] %s [%s]", timestamp, type, action, msg, data));
    }

    public void sendLog(String type, String action, String msg) {
        long timestamp = getLogTimestamp();

        sendLocalLog(timestamp, type, action, msg);
        WatcherLogAPIClient.sendLog(timestamp, type, action, msg);
    }

    public void sendLog(String type, String action, String msg, Object data) {
        long timestamp = getLogTimestamp();

        sendLocalLog(timestamp, type, action, msg, data);
        WatcherLogAPIClient.sendLog(timestamp, type, action, msg, data);
    }
}
