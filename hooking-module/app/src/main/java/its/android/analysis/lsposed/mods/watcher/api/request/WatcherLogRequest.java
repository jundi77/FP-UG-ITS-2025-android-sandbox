package its.android.analysis.lsposed.mods.watcher.api.request;

import com.google.gson.annotations.SerializedName;

public class WatcherLogRequest {

    // Timestamp in milliseconds
    @SerializedName("timestamp")
    private long timestamp;

    // Type of log
    @SerializedName("type")
    private String type;

    // Action that is done for the log's type
    @SerializedName("action")
    private String action;

    // Detailed, formatted log message
    @SerializedName("msg")
    private String msg;

    // Additional data, null unless wanting to send some binary in base64 or other use cases
    @SerializedName("data")
    private Object data;

    public WatcherLogRequest(long timestamp, String type, String action, String msg) {
        this.timestamp = timestamp;
        this.type = type;
        this.action = action;
        this.msg = msg;
    }

    public WatcherLogRequest(long timestamp, String type, String action, String msg, Object data) {
        this.timestamp = timestamp;
        this.type = type;
        this.action = action;
        this.msg = msg;
        this.data = data;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}
