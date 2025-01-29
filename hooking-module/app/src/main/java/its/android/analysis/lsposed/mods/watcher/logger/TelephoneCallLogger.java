package its.android.analysis.lsposed.mods.watcher.logger;

import androidx.annotation.NonNull;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.annotations.BeforeInvocation;
import io.github.libxposed.api.annotations.XposedHooker;
import its.android.analysis.lsposed.mods.watcher.ModuleMain;
import its.android.analysis.lsposed.mods.watcher.logger.model.TelephoneListenModel;
import its.android.analysis.lsposed.mods.watcher.watcher.TelephoneActionWatcher;

@XposedHooker
public class TelephoneCallLogger implements XposedInterface.Hooker {
    private static final String LOG_ACTION = "listen";

    // Filled with map value based on PhoneStateListener LISTEN_* field
    public static final Map<Integer, String> PHONE_STATE_LISTENER_MAP = new HashMap<>();

    public static Map<Integer, String> getPhoneStateListenerMap() {
        if (PHONE_STATE_LISTENER_MAP.isEmpty()) {
            PHONE_STATE_LISTENER_MAP.put(0, "LISTEN_NONE");
            PHONE_STATE_LISTENER_MAP.put(0x00000001, "LISTEN_SERVICE_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00000002, "LISTEN_SIGNAL_STRENGTH");
            PHONE_STATE_LISTENER_MAP.put(0x00000004, "LISTEN_MESSAGE_WAITING_INDICATOR");
            PHONE_STATE_LISTENER_MAP.put(0x00000008, "LISTEN_CALL_FORWARDING_INDICATOR");
            PHONE_STATE_LISTENER_MAP.put(0x00000010, "LISTEN_CELL_LOCATION");
            PHONE_STATE_LISTENER_MAP.put(0x00000020, "LISTEN_CALL_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00000040, "LISTEN_DATA_CONNECTION_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00000080, "LISTEN_DATA_ACTIVITY");
            PHONE_STATE_LISTENER_MAP.put(0x00000100, "LISTEN_SIGNAL_STRENGTHS");
            PHONE_STATE_LISTENER_MAP.put(0x00000400, "LISTEN_CELL_INFO");
            PHONE_STATE_LISTENER_MAP.put(0x00000800, "LISTEN_PRECISE_CALL_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00001000, "LISTEN_PRECISE_DATA_CONNECTION_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00002000, "LISTEN_DATA_CONNECTION_REAL_TIME_INFO");
            PHONE_STATE_LISTENER_MAP.put(0x00004000, "LISTEN_SRVCC_STATE_CHANGED");
            PHONE_STATE_LISTENER_MAP.put(0x00008000, "LISTEN_OEM_HOOK_RAW_EVENT");
            PHONE_STATE_LISTENER_MAP.put(0x00010000, "LISTEN_CARRIER_NETWORK_CHANGE");
            PHONE_STATE_LISTENER_MAP.put(0x00020000, "LISTEN_VOICE_ACTIVATION_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00040000, "LISTEN_DATA_ACTIVATION_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00080000, "LISTEN_USER_MOBILE_DATA_STATE");
            PHONE_STATE_LISTENER_MAP.put(0x00100000, "LISTEN_DISPLAY_INFO_CHANGED");
            PHONE_STATE_LISTENER_MAP.put(0x00200000, "LISTEN_PHONE_CAPABILITY_CHANGE");
            PHONE_STATE_LISTENER_MAP.put(0x00400000, "LISTEN_ACTIVE_DATA_SUBSCRIPTION_ID_CHANGE");
            PHONE_STATE_LISTENER_MAP.put(0x00800000, "LISTEN_RADIO_POWER_STATE_CHANGED");
            PHONE_STATE_LISTENER_MAP.put(0x01000000, "LISTEN_EMERGENCY_NUMBER_LIST");
            PHONE_STATE_LISTENER_MAP.put(0x02000000, "LISTEN_CALL_DISCONNECT_CAUSES");
            PHONE_STATE_LISTENER_MAP.put(0x04000000, "LISTEN_CALL_ATTRIBUTES_CHANGED");
            PHONE_STATE_LISTENER_MAP.put(0x08000000, "LISTEN_IMS_CALL_DISCONNECT_CAUSES");
            PHONE_STATE_LISTENER_MAP.put(0x10000000, "LISTEN_OUTGOING_EMERGENCY_CALL");
            PHONE_STATE_LISTENER_MAP.put(0x20000000, "LISTEN_OUTGOING_EMERGENCY_SMS");
            PHONE_STATE_LISTENER_MAP.put(0x40000000, "LISTEN_REGISTRATION_FAILURE");
            PHONE_STATE_LISTENER_MAP.put(0x80000000, "LISTEN_BARRING_INFO");
        }

        return PHONE_STATE_LISTENER_MAP;
    }

    @BeforeInvocation
    public static void before(@NonNull XposedInterface.BeforeHookCallback callback) {
        ModuleMain module = ModuleMain.getInstance();

        // Hooker is not called via ModuleMain or it's just somehow isn't instantiated
        if (module == null) return;

        Object[] methodArgs = callback.getArgs();
        int events = (int) methodArgs[1];
        List<String> eventList = new ArrayList<>();
        Map<Integer, String> eventMap = getPhoneStateListenerMap();

        for (Integer key : eventMap.keySet()) {
            // because it can be made with OR bitwise, let's check what is being listened with AND bitwise
            if ((events & key) != 0) {
                // the related listen flag is set
                eventList.add(eventMap.get(key));
            }
        }

        module.sendLog(
                TelephoneActionWatcher.LOG_TYPE,
                LOG_ACTION,
                "app is listening for a telephone state",
                new TelephoneListenModel(
                        events,
                        eventList
                )
        );
    }
}
