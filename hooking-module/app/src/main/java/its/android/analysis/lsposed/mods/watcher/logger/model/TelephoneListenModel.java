package its.android.analysis.lsposed.mods.watcher.logger.model;

import com.google.gson.annotations.SerializedName;

import java.util.List;

public class TelephoneListenModel {

    @SerializedName("events")
    private int events;
    @SerializedName("eventList")
    private List<String> eventList;

    public TelephoneListenModel(int events, List<String> eventList) {
        this.events = events;
        this.eventList = eventList;
    }

    public int getEvents() {
        return events;
    }

    public void setEvents(int events) {
        this.events = events;
    }

    public List<String> getEventList() {
        return eventList;
    }

    public void setEventList(List<String> eventList) {
        this.eventList = eventList;
    }
}
