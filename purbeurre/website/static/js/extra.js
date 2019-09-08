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

var capitalize = (name) => name.charAt(0).toUpperCase()+name.slice(1)

// Modifier la fonction callback de telle manière à ce qu'elle modifie le dom en fonction de la reponse de la vue: si c'est OK, vous modifiez et vous écrivez "enregistré", sinon, Opération impossible ou rien (ne compléxfiez pas trop non plus)

//Il faudra sans doute aussi prendre en compte l'objet event
var confirm = (event, responseText) => {
    if (responseText === "OK") {
        var button_text = event.target
        button_text.innerText = "Sauvegardé"
        console.log(button_text)
    }
}

var save_links = document.getElementsByClassName("save-link");
// Faire LA MEME (un observateur d'év) pour la suppression des produits enregistrés.

for (link of save_links) {
    link.addEventListener("click", (e)=>{
        e.preventDefault()

        var substitute_name = e.target.parentNode.parentNode.querySelector("h3").innerText
        var product_name = capitalize(document.getElementsByTagName("h1")[0].innerText.toLowerCase())

        ajaxPost("/save", `product=${product_name}&substitute=${substitute_name}`, confirm, e)
    })
}
