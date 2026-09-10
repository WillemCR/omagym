package challenge

type Bus struct{}

func NewBus() *Bus                                            { return &Bus{} }
func (b *Bus) Subscribe(topic string, fn func(string)) func() { return func() {} }
func (b *Bus) Publish(topic, message string)                  {}
