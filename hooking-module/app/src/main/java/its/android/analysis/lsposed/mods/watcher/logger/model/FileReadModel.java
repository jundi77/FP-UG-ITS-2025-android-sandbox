package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

public class FileReadModel {
    @SerializedName("path")
    private String path;

    public FileReadModel(String path) {
        this.path = path;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }
}
