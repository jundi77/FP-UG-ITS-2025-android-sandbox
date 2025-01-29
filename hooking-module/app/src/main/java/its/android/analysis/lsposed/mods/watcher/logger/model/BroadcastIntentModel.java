package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

import java.util.Map;

public class BroadcastIntentModel {
    @SerializedName("action")
    private String action;

    @SerializedName("extras")
    private Map<String, Object> extras;

    public BroadcastIntentModel(String action) {
        this.action = action;
    }

    public BroadcastIntentModel(String action, Map<String, Object> extras) {
        this.action = action;
        this.extras = extras;
    }

    public Map<String, Object> getExtras() {
        return extras;
    }

    public void setExtras(Map<String, Object> extras) {
        this.extras = extras;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }
}
