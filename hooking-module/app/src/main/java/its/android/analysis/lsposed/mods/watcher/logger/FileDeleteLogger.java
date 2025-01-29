package its.android.analysis.lsposed.mods.watcher.logger;

import android.annotation.SuppressLint;

import androidx.annotation.NonNull;

import java.io.File;
import java.lang.reflect.Field;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.FileDeleteModel;
import its.android.analysis.lsposed.mods.watcher.watcher.FileActionWatcher;

@SuppressLint("SoonBlockedPrivateApi")
@XposedHooker
public class FileDeleteLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "delete";

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

        // File.class.getDeclaredMethod("delete");
        File file = (File) callback.getThisObject();
        if (file == null) return;

        try {
//            Reflective access to path will throw an exception when targeting API 34 and above
            Field pathFile = file.getClass().getDeclaredField("path");
            boolean defaultAccessible = pathFile.isAccessible();

            pathFile.setAccessible(true);
            String path = (String) pathFile.get(file);
            pathFile.setAccessible(defaultAccessible);

            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "app is deleting a file",
                    new FileDeleteModel(path)
            );
        } catch (NoSuchFieldException | IllegalAccessException e) {
            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "a file is being deleted but watcher cannot get it's path: " + e
            );
        }
    }
}
