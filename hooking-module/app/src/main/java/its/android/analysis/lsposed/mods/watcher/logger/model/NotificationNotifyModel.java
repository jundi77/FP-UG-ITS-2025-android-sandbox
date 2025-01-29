package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

import java.util.Map;

public class NotificationNotifyModel {
    @SerializedName("tag")
    private String tag;
    @SerializedName("id")
    private int id;
    @SerializedName("notification")
    private String notification;
    @SerializedName("extras")
    private Map<String, Object> extras;

    public NotificationNotifyModel(String tag, int id, String notification) {
        this.tag = tag;
        this.id = id;
        this.notification = notification;
    }

    public NotificationNotifyModel(String tag, int id, String notification, Map<String, Object> extras) {
        this.tag = tag;
        this.id = id;
        this.notification = notification;
        this.extras = extras;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getNotification() {
        return notification;
    }

    public void setNotification(String notification) {
        this.notification = notification;
    }
}
