import QtQuick
import Quickshell

QtObject {
    function test_idle(s, t) {
        t.equal(s.status,"idle"); t.equal(s.output,""); t.ok(!s.job.running); t.equal(t.find(s,"statusLabel").text,"idle");
    }
    function test_success_output(s, t) {
        s.refresh(); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"ready"); t.equal(t.find(s,"outputLabel").text,"ready"); t.equal(t.find(s,"statusLabel").text,"success");});
    }
    function test_literal_arguments(s, t) {
        s.command=["/usr/bin/printf","%s","spaces; $HOME stay literal"]; s.refresh(); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"spaces; $HOME stay literal");});
    }
    function test_nonzero_exit(s, t) {
        s.command=["/usr/bin/false"]; s.refresh(); t.waitFor(function(){return s.status==="error"},function(){t.equal(s.output,""); t.equal(t.find(s,"statusLabel").text,"error");});
    }
    function test_recovery(s, t) {
        s.command=["/usr/bin/false"]; s.refresh(); t.waitFor(function(){return s.status==="error"},function(){s.command=["/usr/bin/printf","%s","recovered"]; s.refresh(); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"recovered");});});
    }
    function test_running_refresh_is_ignored(s, t) {
        s.command=["/usr/bin/sleep","0.2"]; s.output="old"; s.refresh(); t.equal(s.status,"running"); t.equal(s.output,""); t.waitFor(function(){return s.job.processId !== null},function(){var pid=s.job.processId; s.refresh(); t.equal(s.job.processId,pid); t.waitFor(function(){return s.status==="success"},function(){t.equal(s.output,"");});});
    }
}
