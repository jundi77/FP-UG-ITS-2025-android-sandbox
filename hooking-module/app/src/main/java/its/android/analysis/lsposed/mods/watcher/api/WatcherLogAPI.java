package its.android.analysis.lsposed.mods.watcher.api;

import its.android.analysis.lsposed.mods.watcher.api.request.WatcherLogRequest;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface WatcherLogAPI {
    public static final String LOCAL_NAME_HOST = "localhost";
    public static final String LOCAL_IP_HOST = "127.0.0.1";
    public static final String VM_HOST = "192.168.88.234";
    public static final String WLAN_HOST = "192.168.78.254";
    public static final String SERVER_PORT = "9999";

    @POST("/api/android_watcher_log")
    Call<Object> sendLog(@Body WatcherLogRequest request);
}
