package challenge

import (
	"strings"
	"testing"
)

func TestHTMLRendering(t *testing.T) {
	data := map[string]string{"Name": "<script>alert(1)</script>", "URL": "https://example.com/?a=1&b=2"}
	got, e := Render(`<a href="{{.URL}}">{{.Name}}</a>`, data)
	if e != nil || strings.Contains(got, "<script>") || !strings.Contains(got, "&lt;script&gt;") || !strings.Contains(got, "a=1&amp;b=2") {
		t.Fatal(got, e)
	}
	if data["Name"] != "<script>alert(1)</script>" {
		t.Fatal("mutated data")
	}
	got, e = Render(`<a href="{{.URL}}">open</a>`, map[string]string{"URL": "javascript:alert(1)"})
	if e != nil || strings.Contains(got, "javascript:") || !strings.Contains(got, "#ZgotmplZ") {
		t.Fatal("unsafe URL was not filtered", got, e)
	}
}
func TestTemplateLogic(t *testing.T) {
	s, e := Render(" Hi {{if .Name}}{{.Name}}{{else}}friend{{end}}! ", map[string]string{"Name": "Ada"})
	if e != nil || s != " Hi Ada! " {
		t.Fatal(s, e)
	}
	s, e = Render("", nil)
	if s != "" || e != nil {
		t.Fatal(s, e)
	}
}
func TestTemplateErrors(t *testing.T) {
	for _, source := range []string{"prefix {{.Missing}}", "{{if}}", "{{call .Name}}"} {
		s, e := Render(source, map[string]string{"Name": "Ada"})
		if e == nil || s != "" {
			t.Fatal(source, s, e)
		}
	}
}
