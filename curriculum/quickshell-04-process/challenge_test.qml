import QtQuick
import Quickshell
import Quickshell.Io

QtObject {
    function test_idle(s, t) {
        t.equal(s.status,"idle"); t.equal(s.output,""); t.ok(!s.job.running); t.equal(t.find(s,"statusLabel").text,"idle");
        t.ok(s.job instanceof Process, "job must alias a Quickshell.Io Process");
    }
    function test_success_output(s, t) {
        s.refresh(); t.ok(s.job.stdout instanceof StdioCollector, "job.stdout must be a StdioCollector once the run starts");
        t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"ready"); t.equal(t.find(s,"outputLabel").text,"ready"); t.equal(t.find(s,"statusLabel").text,"success");
            s.command=["/usr/bin/printf","%s","second"]; s.refresh(); t.equal(s.status,"running","A completed success must permit refresh");
            t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"second");});});
    }
    function test_literal_arguments(s, t) {
        s.command=["/usr/bin/printf","%s|%d","spaces; $HOME stay literal","0x1F"]; s.refresh(); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"spaces; $HOME stay literal|31");});
    }
    function test_nonzero_exit(s, t) {
        s.command=["/usr/bin/false"]; s.refresh(); t.waitFor(function(){return s.status==="error"},function(){t.equal(s.output,""); t.equal(t.find(s,"statusLabel").text,"error");});
    }
    function test_recovery(s, t) {
        s.command=["/usr/bin/false"]; s.refresh(); t.waitFor(function(){return s.status==="error"},function(){s.command=["/usr/bin/printf","%s","recovered"]; s.refresh(); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"recovered");});});
    }
    function test_running_refresh_is_ignored(s, t) {
        // Refresh again from inside started: the run is guaranteed to be in progress there, whatever the scheduler does.
        var starts=0, during=null; s.job.started.connect(function(){starts++; if (starts===1) { s.refresh(); during=s.status; }});
        s.command=["/usr/bin/sleep","0.5"]; s.output="old"; s.refresh(); t.equal(s.status,"running"); t.equal(s.output,""); s.refresh(); t.equal(s.status,"running");
        t.waitFor(function(){return s.status==="success"},function(){t.equal(during,"running"); t.equal(s.output,""); t.equal(starts,1,"refresh while running must not start the command again");});
    }
}
