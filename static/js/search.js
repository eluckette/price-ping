$(document).ready(function() {
	$(".loader").fadeOut("slow");
	getResults(1);
	$("#itemNumOne").html("1");
	$("#itemNumTwo").html("20");

	$(".dropdown-menu li a").click(function(){
		$(this).parents(".input-group-btn").find('.btn').text($(this).text());
		$(this).parents(".input-group-btn").find('.btn').val($(this).text());
	});

	$(".submitSearch").on("click", sendSearch);

	$(".pagination").on("click", refresh);
});


function refresh(evt) {
	getResults(evt.currentTarget.id);
}


function getResults(page_number) { 
	$.get('/paginate-search/'+page_number, function(results){
		insertResults(results);
	});
	$('html,body').scrollTop(0)
	$("#itemNumOne").html(page_number*20 - 19);
	$("#itemNumTwo").html(page_number*20);
}


function insertResults(results) {
	for(var i=document.getElementById("searchTable").rows.length; i>1; i--) {
		document.getElementById("searchTable").deleteRow(i-1);
	};

	var table = document.getElementById("searchTable");
	for (item in results) {
		for (var i = 0; i < 20; i=i+4) {
			var row = table.insertRow(1);
			var cell0 = row.insertCell(0);
			var cell1 = row.insertCell(1);
			var cell2 = row.insertCell(2);
			var cell3 = row.insertCell(3);

			cell0.innerHTML = setText(results[item][i+0].Image_URL, results[item][i+0].ASIN, 
									  results[item][i+0].Title, results[item][i+0].Price, 
									  results[item][i+0].Price_f);
			
			cell1.innerHTML = setText(results[item][i+1].Image_URL, results[item][i+1].ASIN, 
									  results[item][i+1].Title, results[item][i+1].Price, 
									  results[item][i+1].Price_f);
			
			cell2.innerHTML = setText(results[item][i+2].Image_URL, results[item][i+2].ASIN, 
									  results[item][i+2].Title, results[item][i+2].Price, 
									  results[item][i+2].Price_f);
			
			cell3.innerHTML = setText(results[item][i+3].Image_URL, results[item][i+3].ASIN, 
									  results[item][i+3].Title, results[item][i+3].Price, 
									  results[item][i+3].Price_f);				
		};
	};
	$('.triggerModal').on('click', setModal);	
}


function setModal(evt) {
	var data = $(this).data();
	saveAlert(data.asin, data.title, data.price, data.price_f, data.image);

	$('.modal-body').empty();

	$('.modal-body').html("<img src="+data.image+"> <br>"+ 
						  data.title+ "<br>" +
						  data.price_f+"<br><br>"+
						  "<form><label for='alert-price-field'>Enter maximum price:</label><br> <input type='number' class='inputField' min='0' max='100' name='alert-price' id='alert-price-field'><br><br><label for'alert-length-field'>Length of notification (days):</label><br><input type='number' class='inputField' min='1' max='5' name='alert-length' id='alert-length-field'> </form><br><button type='button' class='submit-item btn btn-submit btn-block' data-title='"+data.title+"' data-price='"+data.price+"' data-asin='"+data.asin+"'>Submit</button>"+"<br><br><p class='note'>*You can manage alerts in My Account");
	
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


function setText(image_url, asin, title, price, price_f) {
	var text = "<div class='searchItem'><img src="+image_url+">"+"<br>"+
			   "<a href='#' class='triggerModal' data-target='#setNotification' data-asin='"+asin+
			   "' data-title='" +title +
			   "' data-image='" +image_url+
			   "'data-price='" +price +
			   "' data-price_f='" +price_f +
			   "'>"+title+"</a>"+"<br>"+
			   "<p>"+price_f+"</p></div>";

	return text;
};


function sendSearch(evt) {
	var category = $('.dropdown-menu').parents(".input-group-btn").find('.btn').val();
	var userSearch = $("#userSearch").val();

	var form = document.createElement("form");
	var inputCategory = document.createElement('input');
	var inputSearch = document.createElement('input');

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

