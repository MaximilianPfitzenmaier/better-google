const cardItems = document.querySelectorAll('.card-item');
const stickyLink = document.getElementById('sticky-link');
const stickyheader = document.getElementById('sticky-header');
const stickyimg = document.getElementById('sticky-img');
const donutChart = document.querySelector('.donut-chart');

/* Initial */
cardItems[0].querySelector('a');
const href = cardItems[0].querySelector('href');
header = cardItems[0].querySelector('h2').textContent;
stickyimg.src= cardItems[0].getAttribute('data-img');
donutChart.setAttribute('data-percentage', cardItems[0].getAttribute('data-score'));
updateDonutChart(donutChart, cardItems[0].getAttribute('data-score'));


cardItems.forEach(card => {
  card.addEventListener('mouseover', function() {
    const link = card.querySelector('a');
    const href = link.getAttribute('href');
    header = card.querySelector('h2').textContent;
    
    stickyLink.href = href;
    stickyheader.textContent= header;
    stickyimg.src= card.getAttribute('data-img');
    const score = card.getAttribute('data-score');

    /* Donut */
    donutChart.setAttribute('data-percentage', score);
    updateDonutChart(donutChart, score);
    /* Keywords */
    const dataKey = card.getAttribute('data-key');
    const elements = dataKey.split(', ');
    appendLiElements(elements)
  });
});


/* moon button*/

var moonButton = document.getElementById("moon-button");
moonButton.addEventListener("click", function() {
  moonButton.classList.toggle("clicked");
});


/*link click*/
function redirectOnClick() {
    var cardItems = document.querySelectorAll('.card-item');
  
    cardItems.forEach(function(cardItem) {
      var headerTitle = cardItem.querySelector('h2.header-title');
      var link = cardItem.querySelector('a');
  
      headerTitle.addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = link.href;
      });
    });
  }
  

  function addDarkClassOnClick() {
    var moonButton = document.getElementById("moon-button");
    var body = document.body;
  
    moonButton.addEventListener("click", function() {
        body.classList.toggle("dark");
    });
  }
  
    // Attach the event listener to the document
    document.addEventListener('DOMContentLoaded', function() {
        redirectOnClick();
        addDarkClassOnClick();
      });


/*search popup function*/ 

function showPopup() {
    var tueLogo = document.querySelector('.tue-logo');
    var overlay = document.getElementById('overlay');
    var popup = document.getElementById('popup');
    var closePopup = document.getElementById('close-popup');
  
    tueLogo.addEventListener('click', function() {
      overlay.style.display = 'block';
      popup.style.display = 'block';
    });
  
    closePopup.addEventListener('click', function() {
      overlay.style.display = 'none';
      popup.style.display = 'none';
    });
  
    overlay.addEventListener('click', function() {
      overlay.style.display = 'none';
      popup.style.display = 'none';
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    showPopup();
  });