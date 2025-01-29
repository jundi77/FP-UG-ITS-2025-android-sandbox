package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

public class SmsSendModel {
    @SerializedName("destinationAddress")
    private String destAddress;
    @SerializedName("msg")
    private Object msg;
    @SerializedName("port")
    private String port;

    public SmsSendModel(String destAddress, Object msg, String port) {
        this.destAddress = destAddress;
        this.msg = msg;
        this.port = port;
    }

    public String getDestAddress() {
        return destAddress;
    }

    public void setDestAddress(String destAddress) {
        this.destAddress = destAddress;
    }

    public Object getMsg() {
        return msg;
    }

    public void setMsg(Object msg) {
        this.msg = msg;
    }

    public String getPort() {
        return port;
    }

    public void setPort(String port) {
        this.port = port;
    }
}
