
$(document).ready(function() {
  var mapOptions = {
    center: new google.maps.LatLng(37.5663176911162, 126.97782838162229),
    zoom: 14,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  window.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
});

function do_display() {

  request_url = 'data/rectall';
  $.getJSON(request_url,function(data) {
    
    $.each(data, function(entryIndex, entry) {
      //alert(entry['geopt']);
      /*
      var rectangle = new google.maps.Rectangle({
        strokeColor: '#FF0000',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#FF0000',
        fillOpacity: 0.35,
        map: map,
        bounds: new google.maps.LatLngBounds(
          new google.maps.LatLng(parseFloat(entry['minLng']), parseFloat(entry['minLat'])),
          new google.maps.LatLng(parseFloat(entry['maxLng']), parseFloat(entry['maxLat'])))
      });
*/
      var marker = new google.maps.Marker({
        position: new google.maps.LatLng(parseFloat(entry['lng']), parseFloat(entry['lat'])+90),
        map: window.map
      });

    });
  });
}

$(document).ready(function() {
  do_display();
});