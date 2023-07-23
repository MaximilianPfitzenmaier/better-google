const cardItems = document.querySelectorAll('.card-item');
const stickyLink = document.getElementById('sticky-link');
const stickyheader = document.getElementById('sticky-header');
const stickyimg = document.getElementById('sticky-img');
const donutChart = document.querySelector('.donut-chart');

/* Initial */
if(cardItems[0]){
  cardItems[0].querySelector('a');
  const href = cardItems[0].querySelector('href');
  header = cardItems[0].querySelector('h2').textContent;
  stickyimg.src= cardItems[0].getAttribute('data-img');

  stickyLink.href = href;
  stickyheader.textContent= header;
  

  donutChart.setAttribute('data-percentage', cardItems[0].getAttribute('data-score'));
  updateDonutChart(donutChart, cardItems[0].getAttribute('data-score'));

  const initdataKey = cardItems[0].getAttribute('data-key');
  const initelements = initdataKey.split(', ');
  appendLiElements(initelements)

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
}






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
  


  
    // Attach the event listener to the document
    document.addEventListener('DOMContentLoaded', function() {
        redirectOnClick();
      });


/*search popup function*/ 

function showPopup() {
    var tueLogo = document.getElementById('searchimage');
    var overlay1 = document.getElementById('overlay-search');
    var popup1 = document.getElementById('popup-search');
    var closePopup1 = document.getElementById('close-popup-search');
  
    tueLogo.addEventListener('click', function() {
      overlay1.style.display = 'block';
      popup1.style.display = 'block';
      console.log('asdasdas');
    });
  
    closePopup1.addEventListener('click', function() {
      overlay1.style.display = 'none';
      popup1.style.display = 'none';
    });
  
    overlay1.addEventListener('click', function() {
      overlay1.style.display = 'none';
      popup1.style.display = 'none';
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    showPopup();
  });