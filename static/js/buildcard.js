var datadiv = document.querySelector('.data_build')
/*Observer to look if dynamic changes were made inside of an div*/
const keyArray = ["doc_id", "url", "title", "description","img", "ranking_score" ];
let databuildArray = [];


datadiv.querySelectorAll('.data_index').forEach((data) =>{
    let indexArray = [];

    indexArray = {
            doc_id: data.querySelectorAll('li')[0].textContent,
            url: data.querySelectorAll('li')[1].textContent,
            title: data.querySelectorAll('li')[2].textContent,
            description: data.querySelectorAll('li')[3].textContent,
            img: data.querySelectorAll('li')[4].textContent,
            keywords: data.querySelectorAll('li')[5].textContent,
            ranking_score: data.querySelectorAll('li')[6].textContent,
        }
    
    databuildArray.push(indexArray);
})

var spinner = document.createElement("div");
var fragment = document.createDocumentFragment();

spinner.classList.add("spinner");
if(databuildArray.length != 0){
    var firstscore = 100 / databuildArray[0]["ranking_score"];
}

let score, keys;

for (var i = 0; i < databuildArray.length; i++) {
    var carditem = document.createElement("div"); // Create a new cardItem element in each iteration
    carditem.classList.add("card-item"); // Add the "card_item" class to the cardItem
    
    /* add data attributes for donut bar and images*/
    score = databuildArray[i]["ranking_score"] * firstscore;
    keys = databuildArray[i]["keywords"];
    carditem.setAttribute("data-key", keys);
    carditem.setAttribute("data-score", score);
    carditem.setAttribute("data-img", databuildArray[i]["img"]);
    
    var cardbox = document.createElement("div"); // Create a new cardbox element in each iteration
    cardbox.classList.add("card_box");
    
    var imgcontainer = document.createElement("div") // create a new div element as Conatiner for img styling in each iteration
    imgcontainer.classList.add("card_img_container");

    var img = document.createElement("img"); // Create a new img element in each iteration
    img.classList.add("little-img");
    img.setAttribute("src", databuildArray[i]["img"]);
    imgcontainer.appendChild(img);

    var innercard = document.createElement("div") // create a new div element as Conatiner for img styling in each iteration
    innercard.classList.add("inner-card");

    var url = document.createElement("h2"); // Create a new url element in each iteration
    url.setAttribute("href", databuildArray[i]["url"]);
    url.classList.add("header-title");
    url.textContent = databuildArray[i]["title"];
    innercard.appendChild(url);

    var a = document.createElement("a") // Create a new url element in each iteration
    a.setAttribute("src", databuildArray[i]["url"]);
    a.textContent = databuildArray[i]["url"];
    innercard.appendChild(a);

    var description = document.createElement("p"); // Create a new description element in each iteration
    description.classList.add("description");
    description.textContent = databuildArray[i]["description"];
    
    var numberbox = document.createElement("div"); // Create a new numberbox element in each iteration
    numberbox.classList.add("num");
    numberbox.textContent = i + 1;

    cardbox.appendChild(numberbox);
    cardbox.appendChild(imgcontainer);
    cardbox.appendChild(innercard);
    cardbox.appendChild(description);
    
    carditem.appendChild(cardbox);
    fragment.appendChild(carditem); // Append the spinningItem to the fragment
}

document.getElementById("cards-container").appendChild(fragment); // Append the fragment to the outer_spinner element
