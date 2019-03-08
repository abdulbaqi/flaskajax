Chart.defaults.global.legend.display = false;

var options = {
    responsive:true,
    maintainAspectRatio: true,
    // elements:{line:{tension:0.1}},
    scales: {
      xAxes: [{
        display:false
      }],
      yAxes: [{
        //ticks: {min: 2.5,max:3.2},
        display:false
      }],
    },
};


$(document).ready(function(){

	$('form').on('submit', function(e){
		$.ajax({
			data: {
				sdg:$('#sdg').val(),
				country:$('#country').val()
			},
			type: 'POST',
			url : '/process'
		})
		.done(function(data){
			
			if (data.error){
				$('#result').text(data.error).show();
			}
			else {
				
				$('#result').html(data.df).show();
			$('.sparkline').each(function() {
    //Get context with jQuery - using jQuery's .get() method.
    var ctx = $(this).get(0).getContext("2d");
    //This will get the first returned node in the jQuery collection.
    var myNewChart = new Chart(ctx);
    
    // Get the chart data and convert it to an array
    var chartData = JSON.parse($(this).attr('data-chart_values'));
    
    // Build the data object
    var data = {};
    var labels = ['1','2','3','4','5', '6', '7'];
    var datasets = {};
    
    // Create a null label for each value
    // for (var i = 0; i < chartData.length; i++) {
    //   labels.push('');
    // }
    
    // Create the dataset
    datasets['fill'] = false;
    datasets['pointRadius'] = 0;
    datasets['borderColor'] = 'rgba(191, 63, 63,0.7)';
    datasets['borderWidth'] = 3;
    datasets['data'] = chartData;
    
    // Add to data object
    data['labels'] = labels;
    data['datasets'] = Array(datasets);

    new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    })
  });
			}
		})

		e.preventDefault();
	});

var sdgs=[];
var countries=[];

function loadSDG(){
	$.getJSON('/sdgs', function(data, status, xhr){
		for (var i = 0; i < data.length; i++ ) {
        	sdgs.push(data[i].goal);
    	}
});
};

loadSDG();

function loadCountries(){
	$.getJSON('/countries', function(data, status, xhr){
		for (var i = 0; i < data.length; i++ ) {
        	countries.push(data[i].name);
    	}
});
};

loadCountries();

$('#sdg').autocomplete({
	source: sdgs, 
	});

$('#country').autocomplete({
	source: countries, 
	});


});

