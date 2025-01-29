package its.android.analysis.lsposed.mods.watcher.watcher;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;

import io.github.libxposed.api.XposedModuleInterface;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.FileDeleteLogger;
import its.android.analysis.lsposed.mods.watcher.logger.FileReadLogger;
import its.android.analysis.lsposed.mods.watcher.logger.FileWriteLogger;

public class FileActionWatcher extends ActionWatcher {
    public static final String LOG_TYPE = "file";

    public FileActionWatcher(ModuleMain module, XposedModuleInterface.PackageLoadedParam param) {

        try {
            java.lang.reflect.Method fileReadMethod =
                    FileInputStream.class.getDeclaredMethod("read");

            module.hook(fileReadMethod, FileReadLogger.class);
            logHookSuccess(module, FileInputStream.class.getName(), fileReadMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileReadByteArrayMethod =
                    FileInputStream.class.getDeclaredMethod("read", byte[].class);

            module.hook(fileReadByteArrayMethod, FileReadLogger.class);
            logHookSuccess(module, FileInputStream.class.getName(), fileReadByteArrayMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileReadByteArraySlicedMethod =
                    FileInputStream.class.getDeclaredMethod("read", byte[].class, int.class, int.class);

            module.hook(fileReadByteArraySlicedMethod, FileReadLogger.class);
            logHookSuccess(module, FileInputStream.class.getName(), fileReadByteArraySlicedMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileWriteIntMethod =
                    FileOutputStream.class.getDeclaredMethod("write", int.class);

            module.hook(fileWriteIntMethod, FileWriteLogger.class);
            logHookSuccess(module, FileOutputStream.class.getName(), fileWriteIntMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileWriteByteArrayMethod =
                    FileOutputStream.class.getDeclaredMethod("write", byte[].class);
//                FileOutputStream.class.getDeclaredMethod("write", byte[].class);

            module.hook(fileWriteByteArrayMethod, FileWriteLogger.class);
            logHookSuccess(module, FileOutputStream.class.getName(), fileWriteByteArrayMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileWriteByteArraySlicedMethod =
                    FileOutputStream.class.getDeclaredMethod("write", byte[].class, int.class, int.class);
//                FileOutputStream.class.getDeclaredMethod("write", byte[].class, int.class, int.class);

            module.hook(fileWriteByteArraySlicedMethod, FileWriteLogger.class);
            logHookSuccess(module, FileOutputStream.class.getName(), fileWriteByteArraySlicedMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }

        try {
            java.lang.reflect.Method fileDeleteMethod =
                    File.class.getDeclaredMethod("delete");

            module.hook(fileDeleteMethod, FileDeleteLogger.class);
            logHookSuccess(module, File.class.getName(), fileDeleteMethod.toString());
        } catch (NoSuchMethodException e) {
            logHookError(module, e);
        }
    }
}
