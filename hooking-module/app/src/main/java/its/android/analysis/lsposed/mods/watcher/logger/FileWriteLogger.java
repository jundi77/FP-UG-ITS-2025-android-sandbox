package its.android.analysis.lsposed.mods.watcher.logger;

import android.annotation.SuppressLint;

import androidx.annotation.NonNull;

import java.io.FileOutputStream;
import java.lang.reflect.Field;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.FileWriteModel;
import its.android.analysis.lsposed.mods.watcher.watcher.FileActionWatcher;

@XposedHooker
public class FileWriteLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "write";

    @SuppressLint("SoonBlockedPrivateApi")
    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

//        FileOutputStream.class.getDeclaredMethod("write", int.class);
//        FileOutputStream.class.getDeclaredMethod("write", byte[].class);
//        FileOutputStream.class.getDeclaredMethod("write", byte[].class, int.class, int.class);
        FileOutputStream fileOutputStream = (FileOutputStream) callback.getThisObject();
        Object[] writeArgs = callback.getArgs();
        if (fileOutputStream == null) return;

        try {
//            Reflective access to path will throw an exception when targeting API 34 and above
            Field pathFile = fileOutputStream.getClass().getDeclaredField("path");
            boolean defaultAccessible = pathFile.isAccessible();

            pathFile.setAccessible(true);
            String path = (String) pathFile.get(fileOutputStream);
            pathFile.setAccessible(defaultAccessible);

            // write(new byte[] { (byte) b }, 0, 1); -> taken from FileOutputStream
            byte[] bytesToWrite =
                    writeArgs[0] instanceof byte[]? (byte[]) writeArgs[0] : new byte[] { (byte) writeArgs[0] };
            if (writeArgs.length == 1) {
                module.sendLog(
                        FileActionWatcher.LOG_TYPE,
                        LOG_ACTION,
                        "app is writing to a file",
                        new FileWriteModel(
                                path,
                                bytesToWrite
                        )
                );
                return;
            }

            int bytesToWriteOffset =
                    writeArgs.length == 3? 0 : (int) writeArgs[1];
            int bytesToWriteLength =
                    writeArgs.length == 3? bytesToWrite.length : (int) writeArgs[2];

            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "app is writing to a file",
                    new FileWriteModel(
                            path,
                            bytesToWrite,
                            bytesToWriteOffset,
                            bytesToWriteLength
                    )
            );
        } catch (NoSuchFieldException | IllegalAccessException e) {
            module.sendLog(
                    FileActionWatcher.LOG_TYPE,
                    LOG_ACTION,
                    "a file is being written but watcher cannot get it's path: " + e
            );
        }
    }
}
