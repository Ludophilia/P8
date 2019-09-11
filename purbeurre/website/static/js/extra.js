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
