// Pour récupérer le csrf_token

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Pour renvoyer les informations de produit au serveur 

function ajaxPost(url, data, callback, event) {
    var csrftoken = getCookie('csrftoken');
    var request = new XMLHttpRequest()
    request.open("POST", url)
    
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    request.setRequestHeader("X-CSRFToken", csrftoken);
    
    request.addEventListener("load", function () { 
        if (request.status >= 200 && request.status < 400) { 
            callback(event, request.responseText);
        } else {
             console.error(request.status + " " + request.statusText); 
        }
    });
    
    request.addEventListener("error", function () { 
        console.error("Erreur réseau");
    });
    request.send(data);
    }	

// Pour déclencher l'envoi des infos de produit au serveur

var save_links = document.getElementsByClassName("save-link");

var confirmToUser = (event, responseText) => {
    
    if (responseText === "SaveOK") {
        event.target.innerText = "Sauvegardé"
    } else if (responseText === "UnsaveOK") {
        event.target.innerText = "Sauvegarder"
    } else if (responseText === "SaveError") {
        event.target.innerText = "Erreur"
    }
}

for (link of save_links) {

    link.addEventListener("click", (e) => {

        e.preventDefault()
        
        var substitute_name = e.target.parentNode.parentNode.querySelector("h3").innerText
        var button_text_value = e.target.innerText

        if (substitute_name.includes("&")) {
            substitute_name = substitute_name.replace("&", "%26")
        }

        if (button_text_value === "Sauvegarder") {

            ajaxPost(
                "/save", 
                `request=save&substitute=${substitute_name}`, 
                confirmToUser, 
                e)

        } else if (button_text_value === "Sauvegardé") {
            
            ajaxPost("/save", 
                `request=unsave&substitute=${substitute_name}`, 
                confirmToUser, 
                e)

        }    
    })
}

// Pour déclencher la fenetre qui suggère des requêtes de recherche

var search_form = document.querySelectorAll("form")[1]
var search_input = document.querySelectorAll("input[type=search]")[1]

// Un observateur d'évènements, qui après un input clavier, envoie une requête à la viewfunction, si la recherche est fructueuse, une fenetre s'affiche avec les suggestions

search_input.addEventListener("keyup", (e) => {
    
    // Envoyer la requête au serveur
    
    // Ajouter ou rafrachir la fenetre

    if (document.querySelectorAll(".autocomplete-items").length === 1) {
        search_form.removeChild(document.querySelector(".autocomplete-items"))
        search_form.insertAdjacentHTML("beforeend", "<div class='autocomplete-items'></div>")
    } else {
        search_form.insertAdjacentHTML("beforeend", "<div class='autocomplete-items'></div>")
    }

    // AJouter les suggestions à la fenetre

    ex_data = {"suggestions": ["Perrier fines bulles", "Eau de source gazéifiée", "La Salvetat", "Rozana", "Cristaline", "Pepsi max zero"]} // Ex de données envoyées par la view à chaque suggestion

    ex_data.suggestions.forEach(
        suggestion => document.querySelector(".autocomplete-items").insertAdjacentHTML("beforeend",
        `<div> ${suggestion} </div>`)
    )

    // Cache la fenêtre si la recherche est vide, la remettre dans le cas contraire
    
    if (e.target.value === "") {
        document.querySelector(".autocomplete-items").classList.add("d-none") 
    } else if (document.querySelector(".autocomplete-items").classList.contains("d-none")) {
        document.querySelector(".autocomplete-items").classList.remove("d-none")
    }
})

// Retrouver la fenetre quand on remet le focus sur l'input

search_input.addEventListener("focus", (e) => { 
    
    if (e.target.value !== "") {
        if (document.querySelector(".autocomplete-items").classList.contains("d-none")) {
            document.querySelector(".autocomplete-items").classList.remove("d-none")
        }
    }
})

// Masquer la fenetre quand on perd le focus...

search_input.addEventListener("blur", (e) => { 

    if (document.querySelectorAll(".autocomplete-items").length > 0) {
        document.querySelector(".autocomplete-items").classList.add("d-none")
    }

})