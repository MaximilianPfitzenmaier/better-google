  /*--------------------
    Vars
    --------------------*/
    let progress = 0
    let startX = 0
    let active = 0
    let isDown = false
    
    /*--------------------
    Contants
    --------------------*/
    const speedWheel = 0.02
    const speedDrag = -0.1
    
    /*--------------------
    Get Z
    --------------------*/
    const getZindex = (array, index) => (array.map((_, i) => (index === i) ? array.length : array.length - Math.abs(index - i)))
    
    /*--------------------
    Items
    --------------------*/
    const $items = document.querySelectorAll('.spinning_item')
    const $cursors = document.querySelectorAll('.cursor')
    
    const displayItems = (item, index, active) => {
      const zIndex = getZindex([...$items], active)[index]
      item.style.setProperty('--zIndex', zIndex)
      item.style.setProperty('--active', (index-active)/$items.length)
      if((index-active)/$items.length < 0 ){
        item.classList.add("spinning_item-upper");
      }else{
        item.classList.remove("spinning_item-upper");
      }

      if((index-active)/$items.length  == 0){
        item.classList.add("middle");
      }else{
        item.classList.remove("middle");
      }


    }
    
    /*counter*/
      // Get all the div elements with class "num"
      const divs = document.getElementsByClassName('num');

      // Iterate over each div and add a formatted number to it
      for (let i = 0; i < divs.length; i++) {
        const div = divs[i];
        const divNumber = (i + 1).toString().padStart(2, '0'); // Format the number
        div.textContent = divNumber; // Set the div's content with the formatted number
      }


    /* charts __ Donut */
    function updateDonutChart(chart, percentage) {
        let currentPercentage = parseInt(chart.dataset.percentage, 10);
        let targetPercentage = percentage;
        let animationFrameId;
      
        if (!isNaN(currentPercentage) && currentPercentage >= 0 && currentPercentage <= 100) {
          const radius = 80;
          const circumference = 2 * Math.PI * radius;
      
          let svgElement = chart.querySelector('svg');
          let circleFill = svgElement ? svgElement.querySelector('.circle-fill') : null;
          let percentageText = chart.querySelector('.percentage');
      
          if (!svgElement) {
            svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svgElement.setAttribute('width', '100%');
            svgElement.setAttribute('height', '100%');
            chart.appendChild(svgElement);
          }
          var spinningItem = document.querySelector('.spinning_item');

          
          if (!circleFill) {
            circleFill = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circleFill.classList.add('circle-fill');
            circleFill.setAttribute('cx', '50%');
            circleFill.setAttribute('cy', '50%');
            circleFill.setAttribute('r', radius);
            circleFill.setAttribute('fill', 'none');
            if (spinningItem) {
              circleFill.setAttribute('stroke', '#ff4d4d');
            }else{
              circleFill.setAttribute('stroke', '#C25425');
            }
            
            circleFill.setAttribute('stroke-width', '20');
            circleFill.setAttribute('stroke-dasharray', `${circumference} ${circumference}`);
            svgElement.appendChild(circleFill);
          }
      
          if (!percentageText) {
            percentageText = document.createElement('div');
            percentageText.classList.add('percentage');
            chart.appendChild(percentageText);
          }
      
          const updateChart = () => {
            const progress = (targetPercentage - currentPercentage) * 0.05;
      
            if (Math.abs(targetPercentage - currentPercentage) <= Math.abs(progress)) {
              currentPercentage = targetPercentage;
              circleFill.setAttribute('stroke-dashoffset', `${circumference - (circumference * currentPercentage / 100)}`);
              percentageText.textContent = currentPercentage;
              cancelAnimationFrame(animationFrameId);
            } else {
              currentPercentage += progress;
              circleFill.setAttribute('stroke-dashoffset', `${circumference - (circumference * currentPercentage / 100)}`);
              percentageText.textContent = Math.round(currentPercentage);
              animationFrameId = requestAnimationFrame(updateChart);
            }
          };
          circleFill.style.transition = 'stroke-dashoffset 0.3s ease-in-out';
          updateChart();
        }
      }
    

    /* Bars */
    var spinningItem = document.querySelector('.spinning_item');

    if (spinningItem) {
      console.log("The div with class 'spinning_item' exists.");
      // Perform additional actions here if needed

    document.addEventListener("DOMContentLoaded", function() {
        var div = document.querySelector('.bar-chart');
        var barData = {
          barone: parseInt(div.getAttribute('data-barone')),
          bartwo: parseInt(div.getAttribute('data-bartwo')),
          barthree: parseInt(div.getAttribute('data-barthree')),
          barfour: parseInt(div.getAttribute('data-barfour')),
          barfive: parseInt(div.getAttribute('data-barfive')),
          barsix: parseInt(div.getAttribute('data-barsix')),
          barseven: parseInt(div.getAttribute('data-barseven')),
          bareight: parseInt(div.getAttribute('data-bareight')),
        };
  
        // Function to update the bar chart
        function updateBarChart() {
          for (var key in barData) {
            if (barData.hasOwnProperty(key)) {
              var barHeight = barData[key];
              var barElement = div.querySelector('.' + key);
              barElement.style.height = barHeight + 'px';
            }
          }
        }
  
        // Initial bar chart creation
        for (var key in barData) {
          if (barData.hasOwnProperty(key)) {
            var barHeight = barData[key];
            var barElement = document.createElement('div');
            barElement.className = 'bar ' + key;
            barElement.style.height = barHeight + 'px';
            div.appendChild(barElement);
          }
        }
  
        // Update the bar chart when the data attributes change
        function observeChanges() {
          var observer = new MutationObserver(function(mutationsList) {
            mutationsList.forEach(function(mutation) {
              if (mutation.type === 'attributes' && mutation.target === div) {
                var attributeName = mutation.attributeName;
                if (attributeName.startsWith('data-bar')) {
                  var barKey = attributeName.replace('data-', '');
                  barData[barKey] = parseInt(div.getAttribute(attributeName));
                  updateBarChart();
                }
              }
            });
          });
  
          observer.observe(div, { attributes: true });
        }
  
        observeChanges();
      });

    } else {
      console.log("The div with class 'spinning_item' does not exist.");
    }
    /* Update Donut */
    // Select the target node(s) to observe
    const spinningItems = document.querySelectorAll('.spinning_item');


    // Callback function to execute when mutations are observed
    const mutationCallback = (mutationsList, observer) => {
    for (let mutation of mutationsList) {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
        const target = mutation.target;

        // Check if the "middle" class was added
        if (target.classList.contains('middle')) {
            const score = target.getAttribute('data-score');
            const barone = target.getAttribute('data-barone');
            const bartwo = target.getAttribute('data-bartwo');
            const barthree = target.getAttribute('data-barthree');
            const barfour = target.getAttribute('data-barfour');
            const barfive = target.getAttribute('data-barfive');
            const barsix = target.getAttribute('data-barsix');
            const barseven = target.getAttribute('data-barseven');
            const bareight = target.getAttribute('data-bareight');
            // Update the "data-percentage" attribute of the donut-chart div
            const donutChart = document.querySelector('.donut-chart');
            donutChart.setAttribute('data-percentage', score);
            updateDonutChart(donutChart, score);
            // Update the bar attributes
            const barChart = document.querySelector('.bar-chart');
            barChart.setAttribute('data-barone', barone);
            barChart.setAttribute('data-bartwo', bartwo);
            barChart.setAttribute('data-barthree', barthree);
            barChart.setAttribute('data-barfour', barfour);
            barChart.setAttribute('data-barfive', barfive);
            barChart.setAttribute('data-barsix', barsix);
            barChart.setAttribute('data-barseven', barseven);
            barChart.setAttribute('data-bareight', bareight);
            // Update the keywords and how many are found.
            const dataKey = target.getAttribute('data-key');
            const elements = dataKey.split(', ');
            appendLiElements(elements)
            
        }
        }
    }
    };

    // Create a new mutation observer
    const observer = new MutationObserver(mutationCallback);

    // Configure the observer to monitor attribute changes
    const observerConfig = { attributes: true };

    // Start observing the spinning items
    spinningItems.forEach(item => {
    observer.observe(item, observerConfig);
    });

    /* take keywords function */
    function appendLiElements(array) {
        var keywordsDiv = document.querySelector('.keywords');
      
        // Clear existing content
        keywordsDiv.innerHTML = '';
      
        array.forEach(function(item) {
          var li = document.createElement('li');
          var span = document.createElement('span');
          span.classList.add('count-up');
          span.textContent = '0'; // Start the number at 0
      
          li.textContent = item.split(' ')[0]; // Extract the keyword from the array element
          li.appendChild(span);
          keywordsDiv.appendChild(li);
      
          // Animation variables
          var delay = 500; // Delay in milliseconds before starting the counting animation
          var duration = 500; // Animation duration in milliseconds
          var start = 0;
          var end = parseInt(item.split(' ')[1], 10); // Extract the number from the array element
      
          // Count animation
          var startTime = null;
          function countAnimation(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = timestamp - startTime;
      
            if (progress < delay) {
              // Delay before starting the animation
              requestAnimationFrame(countAnimation);
              return;
            }
      
            var percentage = Math.min((progress - delay) / duration, 1);
      
            var currentNumber = Math.floor(percentage * (end - start) + start);
            span.textContent = currentNumber;
      
            if (percentage < 1) {
              requestAnimationFrame(countAnimation);
            }
          }
      
          requestAnimationFrame(countAnimation);
        });
      }

    /*--------------------
    Animate
    --------------------*/
    const animate = () => {
      progress = Math.max(0, Math.min(progress, 100))
      active = Math.floor(progress/100*($items.length-1))
      
      $items.forEach((item, index) => displayItems(item, index, active))
    }
    animate()
    
    /*--------------------
    Click on Items
    --------------------*/
    $items.forEach((item, i) => {
      item.addEventListener('click', () => {
        progress = (i/$items.length) * 100 + 10
        animate()
      })
    })
    
    /*--------------------
    Handlers
    --------------------*/
    const handleWheel = e => {
      const wheelProgress = e.deltaY * speedWheel
      progress = progress + wheelProgress
      animate()
    }
    
    const handleMouseMove = (e) => {
      if (e.type === 'mousemove') {
        $cursors.forEach(($cursor) => {
          $cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`
        })
      }
      if (!isDown) return
      const x = e.clientX || (e.touches && e.touches[0].clientX) || 0
      const mouseProgress = (x - startX) * speedDrag
      progress = progress + mouseProgress
      startX = x
      animate()
    }
    
    const handleMouseDown = e => {
      isDown = true
      startX = e.clientX || (e.touches && e.touches[0].clientX) || 0
    }
    
    const handleMouseUp = () => {
      isDown = false
    }
    
    /*--------------------
    Listeners
    --------------------*/
    document.addEventListener('mousewheel', handleWheel)
    document.addEventListener('mousedown', handleMouseDown)
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    document.addEventListener('touchstart', handleMouseDown)
    document.addEventListener('touchmove', handleMouseMove)
    document.addEventListener('touchend', handleMouseUp)