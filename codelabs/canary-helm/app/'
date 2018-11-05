package main

import (
	"fmt"
	"net/http"
	"text/template"
)

var env string = ""

func err(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Someone hit the error endpoint!")

	http.Error(w, fmt.Sprintf("Error!"), 500)
}

func index(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Handling %+v\n", r)

	t, terr := template.ParseFiles("/content/index.html")

	if terr != nil {
		http.Error(w, fmt.Sprintf("Error loading template: %v", terr), 500)
		return
	}

	config := map[string]string{
		"Env": env,
	}

	t.Execute(w, config)
}

func main() {
	http.HandleFunc("/", index)
	http.HandleFunc("/error", err)

	port := ":80"
	fmt.Printf("Starting to service on port %s\n", port)
	http.ListenAndServe(port, nil)
}
