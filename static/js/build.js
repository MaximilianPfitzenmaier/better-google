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

let firstscore = 100 / databuildArray[0]["ranking_score"];
let score, keys;

for (var i = 0; i < databuildArray.length; i++) {
    var spinningItem = document.createElement("div"); // Create a new spinningItem element in each iteration
    spinningItem.classList.add("spinning_item"); // Add the "spinning_item" class to the spinningItem
    
    score = databuildArray[i]["ranking_score"] * firstscore;
    keys = databuildArray[i]["keywords"];
    spinningItem.setAttribute("data-key", keys);
    spinningItem.setAttribute("data-score", score);
    
    var spinningbox = document.createElement("div"); // Create a new spinningbox element in each iteration
    spinningbox.classList.add("spinning_box");
    
    var url = document.createElement("a"); // Create a new url element in each iteration
    url.setAttribute("href", databuildArray[i]["url"]);
    url.classList.add("title");
    url.textContent = databuildArray[i]["title"];
    
    var description = document.createElement("p"); // Create a new description element in each iteration
    description.classList.add("description");
    description.textContent = databuildArray[i]["description"];
    
    var numberbox = document.createElement("div"); // Create a new numberbox element in each iteration
    numberbox.classList.add("num");
    numberbox.textContent = i + 1;

    var imgcontainer = document.createElement("div") // create a new div element as Conatiner for img styling in each iteration
    imgcontainer.classList.add("img_container");

    var imgsource = databuildArray[i]["img"].slice(1,-1).split(', ');
    var pageimg = imgsource[0].slice(1,-1);
    var favicon = "/static/img/wow.png";
    var randomnumber = Math.floor(Math.random() * 3) + 1;
    if(imgsource[0] == ""){
        switch (randomnumber) {
            case 1:
              pageimg = "/static/img/kuschel-maus.jpg";
              break;
            case 2:
              pageimg = "/static/img/maus-erwartet-anfrage.jpg";
              break;
            case 3:
              pageimg = "/static/img/runde-png-maus.png";
              break;
            default:
              pageimg = "/static/img/forest.jpg";
          }
        
    }
    if(imgsource.length == 2){
        favicon = imgsource[1].slice(1,-1);
        if(favicon == 'empty'){
            favicon = "/static/img/wow.png";
        }
    }
    var img = document.createElement("img"); // Create a new img element in each iteration
    img.classList.add("page_img");
    img.setAttribute("src", pageimg);
    imgcontainer.appendChild(img);

    spinningbox.appendChild(url);
    spinningbox.appendChild(description);
    spinningbox.appendChild(numberbox);
    spinningbox.appendChild(imgcontainer);
    
    spinningItem.appendChild(spinningbox);
    fragment.appendChild(spinningItem); // Append the spinningItem to the fragment
}

document.getElementById("outer_spinner").appendChild(fragment); // Append the fragment to the outer_spinner element




console.log(databuildArray);


