package taskstore

type Task struct {
	ID    int    `json:"id"`
	Title string `json:"title"`
	Done  bool   `json:"done"`
}

func Save(path string, tasks []Task) error {
	return nil
}

func Load(path string) ([]Task, error) {
	return nil, nil
}
