package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

public class NetworkUrlModel {
    @SerializedName("url")
    private String url;

    public NetworkUrlModel(String url) {
        this.url = url;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }
}
