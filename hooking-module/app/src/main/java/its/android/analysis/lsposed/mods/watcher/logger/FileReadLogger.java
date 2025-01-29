package its.android.analysis.lsposed.mods.watcher.logger;

import android.annotation.SuppressLint;

import androidx.annotation.NonNull;

import java.io.FileInputStream;
import java.lang.reflect.Field;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.FileReadModel;
import its.android.analysis.lsposed.mods.watcher.watcher.FileActionWatcher;

@XposedHooker
public class FileReadLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "read";

    @SuppressLint("SoonBlockedPrivateApi")
    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        FileInputStream.class.getDeclaredMethod("read");
//        FileInputStream.class.getDeclaredMethod("read", byte[].class);
//        FileInputStream.class.getDeclaredMethod("read", byte[].class, int.class, int.class);
        FileInputStream fileInputStream = (FileInputStream) callback.getThisObject();;
        if (fileInputStream == null) return;

        try {
//            Reflective access to path will throw an exception when targeting API 34 and above
            Field pathFile = fileInputStream.getClass().getDeclaredField("path");
            boolean defaultAccessible = pathFile.isAccessible();

            pathFile.setAccessible(true);
            String path = (String) pathFile.get(fileInputStream);
            pathFile.setAccessible(defaultAccessible);

            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "app is reading a file",
                    new FileReadModel(path)
            );
        } catch (NoSuchFieldException | IllegalAccessException e) {
            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "a file is being read but watcher cannot get it's path: " + e
            );
        }
    }
}
