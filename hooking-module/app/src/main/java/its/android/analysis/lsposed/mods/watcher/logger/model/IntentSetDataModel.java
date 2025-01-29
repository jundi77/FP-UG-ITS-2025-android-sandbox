package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

public class IntentSetDataModel {

    @SerializedName("data")
    private String data;
    @SerializedName("type")
    private String type;

    public IntentSetDataModel(String data, String type) {
        this.data = data;
        this.type = type;
    }

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }
}
