$(document).ready(function() {
	getOtherAlerts()
	$("#randomSearch").on("click", getRandomSearch);

	$(".dropdown-menu li a").click(function(){
		$(this).parents(".input-group-btn").find('.btn').text($(this).text());
		$(this).parents(".input-group-btn").find('.btn').val($(this).text());
	});
	
	$(".submitSearch").on("click", sendSearch);
});

function getRandomSearch() {
	$.get("/get-random-search", function(results){
		return results;
	});
}

function getOtherAlerts() {
	$.get("/get-other-alerts", function(results){
		insertOtherAlerts(results);
	});
}

function insertOtherAlerts(results) {

	var table = document.getElementById("otherAlerts");
	var row = table.insertRow(1);
	
	for (var i = 0; i < results['alerts'].length; i++) {
		var homeCell = row.insertCell(0);
		homeCell.innerHTML = setText(results['alerts'][i+0].Image_URL, results['alerts'][i+0].ASIN, 
									  results['alerts'][i+0].Title, results['alerts'][i+0].Price);
	};

	$('.triggerModal').on('click', setModal);	
}

function setModal(evt) {
	var data = $(this).data();
	saveAlert(data.asin, data.title, data.price, data.price_f, data.image);

	$('.modal-body').empty();

	$('.modal-body').html("<img src="+data.image+"> <br>"+ 
						  data.title+ "<br>" +
						  data.price_f+
						  "<form><label for='alert-price-field'>Enter maximum price:</label> <input type='number' min='0' max='100' name='alert-price' id='alert-price-field'><br><br><label for'alert-length-field'>Length of notification (days):</label> <input type='number' min='1' max='5' name='alert-length' id='alert-length-field'> </form> <button type='button' class='submit-item btn btn-default' data-title='"+data.title+"' data-price='"+data.price+"' data-asin='"+data.asin+"'>Submit</button>"+"<br><br><p>*You can manage alerts in My Account");
	
	$('#setNotification').modal('show');
	$('.submit-item').on("click", updateAlert);
}


function saveAlert(asin, title, price, price_f, image_url) {
	$.post("/set-alert",
		{asin: asin,
		 title: title,
		 price: price,
		 image_url: image_url},

		function (result) {
			return result;
		}); 
} 


function updateAlert(evt) {
	var data = $(this).data();
	var alert_length = parseFloat($('#alert-length-field').val());
	var alert_price = parseFloat($('#alert-price-field').val());

	$.post("/update-alert", 
		{asin: data.asin,
		 title: data.title,
		 alert_price: alert_price,
		 alert_length: alert_length}, 

		function (result) {
			$('#setNotification').modal('hide');
	});
}	

function setText(image_url, asin, title, price) {
	var text = "<div class='searchItem'><img src="+image_url+">"+"<br>"+
			   "<a href='#' class='triggerModal' data-target='#setNotification' data-asin='"+asin+
			   "' data-title='" +title +
			   "' data-image='" +image_url+
			   "'data-price='" +price +
			   "'>"+title+"</a>"+"<br>"+
			   "</div>";

	return text;
}


function sendSearch(evt) {

	var category = $(".dropdown-menu").parents(".input-group-btn").find(".btn").val();
	var userSearch = $("#userSearch").val();

	var form = document.createElement("form");
	var inputCategory = document.createElement("input");
	var inputSearch = document.createElement("input");

	$(form).attr("action", "/search-results");

	$(inputCategory).attr("value", category);
	$(inputCategory).attr("name", "category");

	$(inputSearch).attr("value", userSearch);
	$(inputSearch).attr("name", "user_input");

	form.appendChild(inputCategory);
	form.appendChild(inputSearch);

	form.submit();
	$(".loader").fadeIn("slow");
}