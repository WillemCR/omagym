import QtQuick
import Quickshell

QtObject {
    function test_24_hour_padding(s, t) {
        s.overrideTime = new Date(2025, 0, 1, 9, 5, 7); t.equal(t.find(s,"clockLabel").text,"09:05");
    }
    function test_midnight_and_noon(s, t) {
        s.use24Hours = false; s.overrideTime = new Date(2025,0,1,0,0,0); t.equal(t.find(s,"clockLabel").text,"12:00 AM"); s.overrideTime = new Date(2025,0,1,12,0,0); t.equal(t.find(s,"clockLabel").text,"12:00 PM");
    }
    function test_seconds_and_pm(s, t) {
        s.overrideTime = new Date(2025,0,1,21,5,7); s.use24Hours = false; s.showSeconds = true; t.equal(t.find(s,"clockLabel").text,"9:05:07 PM"); s.use24Hours = true; t.equal(t.find(s,"clockLabel").text,"21:05:07");
    }
    function test_time_replacement(s, t) {
        s.overrideTime = new Date(2025,0,1,10,1,0); s.overrideTime = new Date(2025,0,1,11,59,0); t.equal(t.find(s,"clockLabel").text,"11:59");
    }
    function test_precision(s, t) {
        t.ok(s.clock.enabled,"Clock must be live"); t.equal(s.clock.precision,SystemClock.Minutes); s.showSeconds = true; t.equal(s.clock.precision,SystemClock.Seconds); s.showSeconds = false; t.equal(s.clock.precision,SystemClock.Minutes);
    }
    function test_live_clock_ticks(s, t) {
        t.ok(s.clock instanceof SystemClock, "clock must alias a real SystemClock");
        var label = t.find(s,"clockLabel");
        // Hour precision moves clock.date to the top of the hour; the default display must follow it.
        s.clock.precision = SystemClock.Hours; t.equal(s.clock.date.getMinutes(), 0); t.equal(label.text, Qt.formatDateTime(s.clock.date,"hh:mm"));
        s.clock.precision = SystemClock.Seconds; s.showSeconds = true; var first = label.text;
        t.waitFor(function(){return label.text !== first},function(){t.equal(label.text,Qt.formatDateTime(s.clock.date,"hh:mm:ss")); t.ok(Math.abs(s.clock.date.getTime() - Date.now()) < 2000, "Displayed time must follow the live clock");});
    }
    function test_return_to_live_time(s, t) {
        s.overrideTime = new Date(2000,0,1,0,0,0); s.overrideTime = null; t.equal(t.find(s,"clockLabel").text,Qt.formatDateTime(s.clock.date,"hh:mm"));
    }
}
