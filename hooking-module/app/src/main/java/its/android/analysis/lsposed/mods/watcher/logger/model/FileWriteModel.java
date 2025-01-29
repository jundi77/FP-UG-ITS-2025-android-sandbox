package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

public class FileWriteModel {
    @SerializedName("path")
    private String path;

    @SerializedName("data")
    private byte[] data;

    @SerializedName("offset")
    private int offset;

    @SerializedName("length")
    private int length;

    public FileWriteModel(String path, byte[] data) {
        this.path = path;
        this.data = data;
    }

    public FileWriteModel(String path, byte[] data, int offset, int length) {
        this.path = path;
        this.data = data;
        this.offset = offset;
        this.length = length;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }

    public int getOffset() {
        return offset;
    }

    public void setOffset(int offset) {
        this.offset = offset;
    }

    public int getLength() {
        return length;
    }

    public void setLength(int length) {
        this.length = length;
    }
}
