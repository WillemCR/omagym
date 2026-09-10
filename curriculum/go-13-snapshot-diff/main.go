package challenge

type Change struct{ Key, Kind, Before, After string }

func Diff(before, after map[string]string) []Change { return nil }
