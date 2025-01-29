package its.android.analysis.lsposed.mods.watcher.api;

import androidx.annotation.NonNull;

import its.android.analysis.lsposed.mods.watcher.api.request.WatcherLogRequest;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public final class WatcherLogAPIClient {
    private static WatcherLogAPIClient instance;
    private final WatcherLogAPI watcherLogAPI;

    public static void spawnIfNotExists() {
        if (instance == null) {
            instance = new WatcherLogAPIClient();
        }
    }

    public static WatcherLogAPIClient getInstance() {
        spawnIfNotExists();
        return instance;
    }

    public static void sendLog(long timestamp, String type, String action, String msg) {
        WatcherLogAPIClient client = getInstance();
        WatcherLogRequest request = new WatcherLogRequest(
                timestamp,
                type,
                action,
                msg
        );

        client.getWatcherLogAPI().sendLog(request).enqueue(new Callback<Object>() {
            @Override
            public void onResponse(@NonNull Call<Object> call, @NonNull Response<Object> response) {
//                ModuleMain.getInstance().log("[api_log] [send] [success] " + request);
            }

            @Override
            public void onFailure(@NonNull Call<Object> call, @NonNull Throwable t) {
//                ModuleMain.getInstance().log("[api_log] [send] [fail] [" + t.toString() + "] " + request);
            }
        });
    }

    public static void sendLog(long timestamp, String type, String action, String msg, Object data) {
        WatcherLogAPIClient client = getInstance();
        WatcherLogRequest request = new WatcherLogRequest(
                timestamp,
                type,
                action,
                msg,
                data
        );

        client.getWatcherLogAPI().sendLog(request).enqueue(new Callback<Object>() {
            @Override
            public void onResponse(@NonNull Call<Object> call, @NonNull Response<Object> response) {
//                ModuleMain.getInstance().log("[api_log] [send] [success] " + request);
            }

            @Override
            public void onFailure(@NonNull Call<Object> call, @NonNull Throwable t) {
//                ModuleMain.getInstance().log("[api_log] [send] [fail] [" + t.toString() + "] " + request);
            }
        });
    }

    public WatcherLogAPIClient() {
        // TODO Set to localhost/127.0.0.1 on app that is deployed via web ui
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(getLogServerUrl(WatcherLogAPI.LOCAL_IP_HOST))
//                .baseUrl(getLogServerUrl(WatcherLogAPI.LOCAL_NAME_HOST))
//                .baseUrl(getLogServerUrl(WatcherLogAPI.WLAN_HOST))
//                .baseUrl(getLogServerUrl(WatcherLogAPI.VM_HOST))
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        watcherLogAPI = retrofit.create(WatcherLogAPI.class);
    }

    private static String getLogServerUrl(String host) {
        return "http://" + host + ":" + WatcherLogAPI.SERVER_PORT;
    }

    public WatcherLogAPI getWatcherLogAPI() {
        return watcherLogAPI;
    }
}
