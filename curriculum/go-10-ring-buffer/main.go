package challenge

type Ring[T any] struct{}

func New[T any](capacity int) (*Ring[T], error) { return &Ring[T]{}, nil }
func (r *Ring[T]) Push(value T) (T, bool)       { var zero T; return zero, false }
func (r *Ring[T]) Pop() (T, bool)               { var zero T; return zero, false }
func (r *Ring[T]) Len() int                     { return 0 }
