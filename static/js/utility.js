    /* check if description is "none"  and delete is*/ 
    function replaceNoneText() {
        const descriptionTags = document.querySelectorAll('p.description');

        descriptionTags.forEach(tag => {
            if (tag.textContent.trim() === "none" || tag.textContent.trim() === "None") {
                tag.textContent = "";
            }
        });
    }
    /* Handle images with wrong links example links with /en/ to certain images are non existent so the /en/ has to be replaced */
      function replaceImageSrc() {
        const images = document.querySelectorAll('img.page_img');

        images.forEach(image => {
            if (image.src.includes('/en/')) {
                image.src = image.src.replace('/en/', '/');
            }
        });
    }

    function replaceImageSrcCards() {
        const images = document.querySelectorAll('img.little-img');
        const imagesdatas = document.querySelectorAll('card-item');

        images.forEach(image => {
            if (image.src.includes('/en/')) {
                image.src = image.src.replace('/en/', '/');
            }
        });

        imagesdatas.forEach(imagesdata => {
            if (imagesdata.getAttribute('data-img').includes('/en/')) {
                imagesdata.getAttribute('data-img') = imagesdata.getAttribute('data-img').replace('/en/', '/');
            }
        });
    }

    /* moon button --> for dark mode */

    var moonButton = document.getElementById("moon-button");
    moonButton.addEventListener("click", function() {
    moonButton.classList.toggle("clicked");
    /* if darkmode activated save in localstorage */
    if(localStorage.getItem("dark") !== null){
        localStorage.removeItem("dark");
    }else{
        localStorage.setItem("dark", "active");
    }
    
    
    });

    /* if value for darkmode exists darkmode was turned on */
    if(localStorage.getItem("dark") !== null){
    document.body.classList.add("dark");
    moonButton.classList.add("clicked");
    }

    function addDarkClassOnClick() {
        var moonButton = document.getElementById("moon-button");
        var body = document.body;
      
        moonButton.addEventListener("click", function() {
            body.classList.toggle("dark");
        });
      }

/* Loading animation while processing search query*/
        function showProcessing() {
            const loadingText = document.getElementById("loading-text");
            loadingText.innerText = "Processing your search";

            const points = ["",".", "..", "..."];
            let index = 0;

            function animateDots() {
                loadingText.innerText = "Processing your search" + points[index];
                index = (index + 1) % points.length;
            }

            const intervalId = setInterval(animateDots, 500);

            // Simulate the processing for 3 seconds (3000ms)
            setTimeout(function () {
                clearInterval(intervalId); // Stop the animation
                loadingText.innerText = ""; // Clear the loading text
            }, 500000000);
        }


        /* if search query higher than 20 or keywords 10 or heigher warning that query is too long and it might affect the search results */
        var formSubmitted = false;
        var keywordcountconf = true;

        function keywordscount() {
            // Get the h2 element by its ID
            const h2Element = document.getElementById('searched_query');
          
            // Get the input element by its ID
            const inputElement = document.getElementById('query_input');
          
            // Set the input value to the content of the h2 element
            inputElement.value = h2Element.textContent;
          }
          
          // Call the function to fill the input when needed
        var keyworddiv = document.getElementById('you_sure'); 
        if(keyworddiv){
            var keywordcount = parseInt(document.getElementById('you_sure').textContent, 10);
            if (keywordcount > 9) {
                document.getElementById('overlay').style.display = 'block';
                document.getElementById('popup').style.display = 'block';
                keywordcountconf = false;
                keywordscount();
            }
        }


        function checkWordCount(inputElement) {
            var inputValue = inputElement.value.trim();
            var wordCount = inputValue.split(/\s+/).length;
            

            if (wordCount > 20 && !formSubmitted && keywordcountconf) {
                if(document.getElementById("overlay-search")){
                    document.getElementById("close-popup-search").click();
                }
                document.getElementById('submit_form').setAttribute('onsubmit', 'return false;');
                document.getElementById('overlay').style.display = 'block';
                document.getElementById('popup').style.display = 'block';
            } else {
                document.getElementById('submit_form').removeAttribute('onsubmit');
                document.getElementById('overlay').style.display = 'none';
                document.getElementById('popup').style.display = 'none';
            }
        }
        

        /* function to close warning and allow search with long query */
        function confirmPopup() {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('popup').style.display = 'none';
            document.getElementById('submit_form').removeAttribute('onsubmit');
            document.getElementById('confirmkey').value = 1;
            formSubmitted = true;
        }

        function deniePopup() {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('popup').style.display = 'none';
            formSubmitted = false;
        }


        /* if search result where empty*/ 
        function resultempty() {
            const outerSpinner = document.getElementById('outer_spinner');
            
            const infoCard = document.querySelector('.info-card');

            const card = document.getElementById('cards-container');
            const infocards = document.getElementById('sticky-container');

            if(!card && !outerSpinner){
                return;
            }

            if(!outerSpinner){
                if (card.childElementCount === 0) {
                // If the outer_spinner div is empty, delete the existing content inside info-card
                infocards.innerHTML = '';

                // Create a new <p> element and an <img> element
                const newParagraph = document.createElement('p');
                const newParagraph2 = document.createElement('p');
                const newParagraph3 = document.createElement('p');
                const newParagraph4 = document.createElement('p');
                const newImage = document.createElement('img');
                newParagraph4.textContent = "Search results for " + '"' + document.getElementById('searched_query').textContent+ '"';
                // Set some content for the new <p> element and a source for the new <img> element
                newParagraph.textContent = 'Wow';
                newParagraph2.textContent = 'Such Empty';
                newParagraph3.textContent = 'Try again';
                newImage.src = '/static/img/wow.png';
                newParagraph.classList.add("emptyp","emptyp1");
                newParagraph2.classList.add("emptyp","emptyp2");
                newParagraph3.classList.add("emptyp","emptyp3");
                newParagraph4.classList.add("emptyp","emptyp4");
                newImage.classList.add("wow_img");
                document.body.classList.add('dark-info-card-empty');
                document.getElementById('sticky-container').classList.add('info-card-empty');
                // Append the new elements inside the info-card div
                infocards.appendChild(newParagraph);
                infocards.appendChild(newParagraph2);
                infocards.appendChild(newParagraph3);
                infocards.appendChild(newParagraph4);
                infocards.appendChild(newImage);
                }
                return;
            }
            if (outerSpinner.childElementCount === 0) {
                // If the outer_spinner div is empty, delete the existing content inside info-card
                infoCard.innerHTML = '';

                // Create a new <p> element and an <img> element
                const newParagraph = document.createElement('p');
                const newParagraph2 = document.createElement('p');
                const newParagraph3 = document.createElement('p');
                const newParagraph4 = document.createElement('p');
                const newImage = document.createElement('img');
                newParagraph4.textContent = "Search results for " + '"' + document.getElementById('searched_query').textContent+ '"';
                // Set some content for the new <p> element and a source for the new <img> element
                newParagraph.textContent = 'Wow';
                newParagraph2.textContent = 'Such Empty';
                newParagraph3.textContent = 'Try again';
                newImage.src = '/static/img/wow.png';
                newParagraph.classList.add("emptyp","emptyp1");
                newParagraph2.classList.add("emptyp","emptyp2");
                newParagraph3.classList.add("emptyp","emptyp3");
                newParagraph4.classList.add("emptyp","emptyp4");
                newImage.classList.add("wow_img");

                document.querySelectorAll('.info-card')[0].classList.add('info-card-empty');
                document.body.classList.add('dark-info-card-empty');
                // Append the new elements inside the info-card div
                infoCard.appendChild(newParagraph);
                infoCard.appendChild(newParagraph2);
                infoCard.appendChild(newParagraph3);
                infoCard.appendChild(newParagraph4);
                infoCard.appendChild(newImage);
            }
        }


    /* BITV Zoom function */

    const zoomLIs = document.querySelectorAll('.dropdown-menu li');

    zoomLIs.forEach(li => {
      li.addEventListener('click', function(event) {
        const zoomClassMatch = this.id.match(/^zoom-(\d+)$/);
        if (zoomClassMatch) {
          const zoomClass = 'zoom_' + zoomClassMatch[1];
          // Remove existing zoom class from the body, if any
          document.body.classList.forEach(className => {
            if (className.startsWith('zoom_')) {
              document.body.classList.remove(className);
            }
          });
          // Add the new zoom class to the body
          document.body.classList.add(zoomClass);
          // save zoom inside local storage to saved selected option
          localStorage.setItem("zoomlvl", zoomClass);

          if (zoomClass == "zoom_3") {
            document.body.classList.remove("active-zoom");
          }else{
            document.body.classList.add("active-zoom");
          }
          
        }
      });
    });
    
    /* get saved zoom lvl */
    if(localStorage.getItem("zoomlvl") !== null){
        document.body.classList.add(localStorage.getItem("zoomlvl"));
    }
    

    /* call functions here if they should fire after page is fully loaded */

    document.addEventListener('DOMContentLoaded', function() {
        replaceNoneText();
        replaceImageSrc();
        resultempty();
        replaceImageSrcCards();
        addDarkClassOnClick();
    });