package challenge

import "time"

type Cache struct{}

func New(ttl time.Duration) (*Cache, error)                   { return &Cache{}, nil }
func (c *Cache) Set(key, value string, now time.Time)         {}
func (c *Cache) Get(key string, now time.Time) (string, bool) { return "", false }
