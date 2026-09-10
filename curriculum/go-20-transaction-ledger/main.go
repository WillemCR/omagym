package challenge

type Transfer struct {
	From, To string
	Cents    int64
}
type Ledger struct{}

func NewLedger(initial map[string]int64) (*Ledger, error) { return &Ledger{}, nil }
func (l *Ledger) Apply(batch []Transfer) error            { return nil }
func (l *Ledger) Snapshot() map[string]int64              { return map[string]int64{} }
