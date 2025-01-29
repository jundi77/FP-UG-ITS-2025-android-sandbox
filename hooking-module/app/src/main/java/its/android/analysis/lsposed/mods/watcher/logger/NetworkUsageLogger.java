package its.android.analysis.lsposed.mods.watcher.logger;

import androidx.annotation.NonNull;

import java.net.URL;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.NetworkUrlModel;
import its.android.analysis.lsposed.mods.watcher.watcher.NetworkActionWatcher;

@XposedHooker
public class NetworkUsageLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "usage";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        java.net.URL.class.getDeclaredMethod("openConnection");
        URL url = (URL) callback.getThisObject();
        if (url == null) return;

        module.sendLog(
                NetworkActionWatcher.LOG_TYPE,
                LOG_ACTION,
                "app is doing networking on openConnection",
                new NetworkUrlModel(url.toString())
        );
    }
}
