$(document).ready(function() {
	getCurrentAlerts();
	getRecentlyViewed();
});


function getCurrentAlerts() {
	$.get("/get-current-alerts", function(results){
		$('#alertTable tbody').empty();
		insertAlerts(results);
	});
}


function getRecentlyViewed() {
	$.get("/get-recently-viewed", function(results){
		insertSearches(results);
	});
}


function insertAlerts(results) {
    var table = document.getElementById("alertsBody");
	for (var i = 0; i < results['alerts'].length; i++) {
		var row = table.insertRow(0);
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);	
		var cell3 = row.insertCell(2);
		var cell4 = row.insertCell(3);
		var cell5 = row.insertCell(4);

		cell1.innerHTML = "<button class='btn btn-default delItem' data-alert_id='"+results['alerts'][i].Alert_id+"'>Delete</button>";
		cell2.innerHTML = "<img src="+results['alerts'][i].Image_URL+" width='60px'>";
		cell3.innerHTML = "<p>"+results['alerts'][i].Title+"</p>";
		cell4.innerHTML = "<p>"+formatNumber(results['alerts'][i].Alert_price)+"</p>";
		cell5.innerHTML = "<p>"+results['alerts'][i].Expiration_date+"</p>";	

		assignDeleteAlert();
	};
}


function assignDeleteAlert() {
	$(".delItem").on("click", delAlert)
}


function delAlert(evt) {
	
	var data = $(this).data();
	
	$.post("/delete-alert",
		{alert_id: data.alert_id},

		function(result) {
			refreshAlerts();
	});
}	


function refreshAlerts() {
	getCurrentAlerts();
}


function formatNumber(num) {
	return "$" + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
}


function insertSearches(results) {
	var table = document.getElementById("userSearchesTable");
	for (var i = results["alerts"].length; i--;) {
		var row = table.insertRow(1);
		var cell1 = row.insertCell(0);
		cell1.innerHTML = "<p><img src='"+results["alerts"][i].Image_URL+"'</p>"+
						  "<p>"+results["alerts"][i].Title+"</p>";		
	};
}