package challenge

type Config struct {
	Address string
	Workers int
	Debug   bool
}

func Parse(text string) (Config, error) { return Config{}, nil }
