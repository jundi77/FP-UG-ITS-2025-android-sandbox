package its.android.analysis.lsposed.mods.watcher.logger;

import android.net.Uri;

import androidx.annotation.NonNull;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.IntentSetDataModel;
import its.android.analysis.lsposed.mods.watcher.watcher.IntentActionWatcher;

@XposedHooker
public class IntentLaunchLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "set_data_and_type";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        Intent.class.getDeclaredMethod("setDataAndType", Uri.class, String.class);
        Object[] setDataAndTypeArgs = callback.getArgs();

        Uri data = (Uri) setDataAndTypeArgs[0];
        String type = (String) setDataAndTypeArgs[1];

        module.sendLog(
                IntentActionWatcher.LOG_TYPE,
                LOG_ACTION,
                "app is doing setDataAndType to an Intent",
                new IntentSetDataModel(
                        data.toString(),
                        type == null? "" : type
                )
        );
    }
}
