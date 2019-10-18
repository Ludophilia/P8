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

function ajaxCommunicate(method, url, callback, data, extra_par) {

    var request = new XMLHttpRequest()
    request.open(method, url)
    
    if (method === "POST") {
        var csrftoken = getCookie('csrftoken');
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        request.setRequestHeader("X-CSRFToken", csrftoken);
    }

    request.addEventListener("load", function () { 
        if (request.status >= 200 && request.status < 400) { 
            if (extra_par !== "undefined") {
                callback(request.responseText, extra_par);
            } else {
                callback(request.responseText);
            }
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

function confirmToUser(responseText, event) {
    
    if (responseText === "SaveOK") {
        event.target.innerText = "Sauvegardé"
    } else if (responseText === "UnsaveOK") {
        event.target.innerText = "Sauvegarder"
    } else if (responseText === "SaveError") {
        event.target.innerText = "Erreur"
    }
}

function urlEncodeString(string) {

    conversion_table = {
        "&":"%26",
        ";":"%3B"
    }

    Object.entries(conversion_table).forEach(([sym,eqv]) => {
        if (string.includes(sym)) {
            string = string.replace(new RegExp(`${sym}`, "gm"), `${eqv}`)
        }
    })
    
    return string
}

var save_links = document.getElementsByClassName("save-link");

for (link of save_links) {

    link.addEventListener("click", (event) => {

        event.preventDefault()
        
        var substitute_name = urlEncodeString(event.target.parentNode.parentNode.querySelector("h3").innerText)
        var button_text_value = event.target.innerText

        if (button_text_value === "Sauvegarder") {

            ajaxCommunicate(
                "POST",
                "/save", 
                confirmToUser,
                `request=save&substitute=${substitute_name}`,
                event)

        } else if (button_text_value === "Sauvegardé") {
            
            ajaxCommunicate(
                "POST",
                "/save",
                confirmToUser,
                `request=unsave&substitute=${substitute_name}`, 
                event)
        }    
    })
}

// Pour déclencher la fenetre qui suggère des requêtes de recherche

var search_input = document.querySelectorAll("input[type=search]")[1]

function displaySuggestions (search_suggestions_js, query) {

    var search_form = document.querySelectorAll("form")[1]
    var search_suggestions = JSON.parse(search_suggestions_js)

    // Ajouter ou rafrachir la fenetre

    if (document.querySelectorAll(".autocomplete-items").length >= 1) {
        search_form.removeChild(document.querySelector(".autocomplete-items"))
    }
    search_form.insertAdjacentHTML("beforeend", "<div class='autocomplete-items'></div>")
    
    // AJouter les suggestions à la fenetre.

    search_suggestions.suggestions.forEach(
        (suggestion) => {
            suggested = suggestion.slice(query.length) // Ou slice(0, query.length) si on veut mettre en valeur ce qu'à tapé l'utilisateur ou slice(query.length) si on veut mettre les suggestions en valeur
            suggestion_og = suggestion

            suggestion = suggestion.replace(suggested, `<b>${suggested}</b>`)
            document.querySelector(".autocomplete-items").insertAdjacentHTML("beforeend",
            `<div class="ac-item"> ${suggestion} </div>`)

            document.querySelector(".ac-item:last-child").addEventListener("click", (event) => {
                
                if (event.target.classList.length === 0) {
                    search_input.value = event.target.parentNode.textContent.trim()
                } else {
                    search_input.value = event.target.textContent.trim()
                }
                document.querySelector("#searchbar02").click()
            })
        })
}

// Un observateur d'évènements, qui après un input clavier, envoie une requête à la viewfunction, si la recherche est fructueuse, une fenetre s'affiche avec les suggestions


search_input.addEventListener("keyup", (e) => {
    
    // Envoyer la requête au serveur

    var query = urlEncodeString(e.target.value)

    if (query.length > 0) {
        ajaxCommunicate("GET", `/suggest?query=${query}`, displaySuggestions, null, query)
    } else {
        if (document.querySelectorAll(".autocomplete-items").length > 0) {
            document.querySelector(".autocomplete-items").style.display = "none"
        } // Cache la fenêtre si la recherche est vide, elle sera supprimée et reconstruite à la prochaine requête
    }
})

// Retrouver la fenetre quand on remet le focus sur l'input

search_input.addEventListener("focus", (e) => { 
    
    if (e.target.value !== "") {
        if (document.querySelector(".autocomplete-items").style.display === "none") {
            document.querySelector(".autocomplete-items").style.display = "block"
        }
    }
})

// Masquer la fenetre quand on perd le focus...

search_input.addEventListener("blur", (e) => {

    if (e.target.value !== "") {
        if (document.querySelectorAll(".autocomplete-items").length > 0) {

            setTimeout(() => {
                document.querySelector(".autocomplete-items").style.display = "none"
            }, 200) // Pour contrer le fait que Le blur se déclenche avant le clic sur la fenetre autocomplete.
        }
    }
})