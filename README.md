<h2> Hi, I'm moonD4rk!</h2>

```go
package main

type Me struct {
	Name  string
	Roles []string
	Bio   string
}

func main() {
	me := &Me{
		Name:  "moonD4rk",
		Roles: []string{"Cyber Security Engineer", "Backend Developer", "SRE"},
		Bio:   "Building systems by day, Breaking them by night.",
	}
	_ = me
}
```

