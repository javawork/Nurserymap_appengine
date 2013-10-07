
function getBoundsZoomLevel(bounds, mapDim) {
  var WORLD_DIM = { height: 256, width: 256 };
  var ZOOM_MAX = 21;

  function latRad(lat) {
      var sin = Math.sin(lat * Math.PI / 180);
      var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
      return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
  }

  function zoom(mapPx, worldPx, fraction) {
      return Math.floor(Math.log(mapPx / worldPx / fraction) / Math.LN2);
  }

  var ne = bounds.getNorthEast();
  var sw = bounds.getSouthWest();

  var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;

  var lngDiff = ne.lng() - sw.lng();
  var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

  var latZoom = zoom(mapDim.height, WORLD_DIM.height, latFraction);
  var lngZoom = zoom(mapDim.width, WORLD_DIM.width, lngFraction);

  return Math.min(latZoom, lngZoom, ZOOM_MAX);
}

function calcZoomLevel(minLng, minLat, maxLng, maxLat) {
  var markerBounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(minLng, minLat),
            new google.maps.LatLng(maxLng, maxLat));

  var viewBounds = window.map.getBounds();

  var $mapDiv = $('#map_canvas');
  var mapDim = { height: $mapDiv.height(), width: $mapDiv.width() };

  return getBoundsZoomLevel(markerBounds, mapDim)
}

function cleanup_prev_spots() {
  if ( window.spot === null ) 
    return;

  if ( window.spot === undefined ) 
    return;

  for ( var j = 0; j < window.spot.marker.length; j++) {
      window.spot.infowindow[j].close();
      window.spot.marker[j].setMap(null);
  }
  window.spot = null;
}

function build_text_for_infowindow( entry ) {
  return '<table><tr><td height="12" style="background:#4d7dbe;font-family:돋움;color:white;font-size:14px;font-weight:bold;" align="CENTER">'+entry['title']+'</td></tr><tr><td style="padding-right:10px;padding-left:10px;font-family:돋움;font-size:12px;"></td></tr>'
    + '<tr><td>'
    + entry['address'] 
    + '</td></tr>'
    + '<tr><td>'
    + entry['phone'] + ' / ' + entry['own'] + ' / ' + entry['auth']
    + '</td></tr>'
    + '<tr><td>'
    + '정원 : ' + entry['capacity'] + '&nbsp; '
    + '<a href="http://m.childcare.go.kr/nursery/neighbored_foundSlPL.jsp?stcode='+entry['id']+'&flag=BISl" target="_blank">'
    + '<img src="img/detail_btn.gif" align="top">' + '</a>'
    + '</td></tr>'
    + '</table>';  
}

function get_icon_filename(own) {
  var own_iconfile_table = {
    '국공립' : 'green-dot.png',
    '민간' : 'blue-dot.png',
    '가정' : 'red-dot.png',
    '기타' : 'purple-dot.png'
  }

  var icon_filename = own_iconfile_table[own];
  if (icon_filename === undefined)
    return own_iconfile_table['기타']
  else 
    return icon_filename;
}

function displayableOwnType(own) {
  var show_own_table = {
    '국공립' : $('#national').is(':checked'),
    '민간' : $('#private').is(':checked'),
    '가정' : $('#home').is(':checked'),
    '기타' : $('#other').is(':checked')
  }

  var result = show_own_table[own];
  if (result === undefined)
    return show_own_table['기타'];
  else 
    return result;
}

function do_search( area1, area2 ) {

  $('#mask, .popup_div').hide();

  request_url = 'data/query';
  $.getJSON(request_url,{'area1':area1, 'area2':area2},function(data) {
    
    //cleanup_prev_spots();

    var index = window.spot.marker.length;
    var counter = 0;
    var sumOfLat = 0;
    var sumOfLng = 0;
    var minLng = 1000000.0;
    var minLat = 1000000.0;
    var maxLng = 0.0;
    var maxLat = 0.0;

    $.each(data, function(entryIndex, entry) {
      //alert( entry['title']+'/' + entry['own'] +'/'+ showResult.toString() );
      if ( !displayableOwnType(entry['own']) )
        return true;

      if ( entry['id'] in window.spot.idset )
        return true;

      window.spot.idset[entry['id']] = true;

      info_text = build_text_for_infowindow(entry);
      window.spot.infowindow[index] = new google.maps.InfoWindow({
        content: info_text
      });

      var icon_filename = get_icon_filename(entry['own']);

      var lng = parseFloat(entry['lng'])
      var lat = parseFloat(entry['lat'])
      window.spot.marker[index] = new google.maps.Marker({
        position: new google.maps.LatLng(lng, lat),
        map: window.map,
        title: entry['title'],
        icon: 'http://maps.google.com/mapfiles/ms/icons/' + icon_filename
      });

      window.mc.addMarker(window.spot.marker[index]);

      minLng = Math.min(lng, minLng);
      minLat = Math.min(lat, minLat);
      maxLng = Math.max(lng, maxLng);
      maxLat = Math.max(lat, maxLat);

      window.spot.marker[index].index = index;

      google.maps.event.addListener(window.spot.marker[index], 'click', function() {
        for (var j=0; j<window.spot.infowindow.length; ++j) {
          window.spot.infowindow[j].close();
        }
        window.spot.infowindow[this.index].open(window.map, window.spot.marker[this.index]);
      });

      sumOfLng = sumOfLng + parseFloat(entry['lng']);
      sumOfLat = sumOfLat + parseFloat(entry['lat']);

      index = index + 1;
      counter = counter + 1;
    });

    //alert( 'Total : ' + counter.toString() );

    if (counter > 0) {
      var centerLng = sumOfLng/counter;
      var centerLat = sumOfLat/counter;
      window.map.setCenter(new google.maps.LatLng(centerLng, centerLat));
      if ( counter > 1 ) {
        var zoomLevel = calcZoomLevel(minLng, minLat, maxLng, maxLat);
        //alert("ZoomLevel : ".concat(zoomLevel.toString()));
        window.map.setZoom(zoomLevel);
      }
    } else {
      alert('해당 지역에 어린이집이 없습니다.');
    }
    //alert(i);
  });
}

function complete_search_bypos( data ) {
  //cleanup_prev_spots();
  var index = window.spot.marker.length;
  $.each(data, function(entryIndex, entry) {
    if ( !displayableOwnType(entry['own']) )
      return true;
    
    if ( entry['id'] in window.spot.idset )
      return true;

    window.spot.idset[entry['id']] = true;

    info_text = build_text_for_infowindow(entry);
    window.spot.infowindow[index] = new google.maps.InfoWindow({
      content: info_text
    });

    var icon_filename = get_icon_filename(entry['own']);

    var lng = parseFloat(entry['lng'])
    var lat = parseFloat(entry['lat'])
    window.spot.marker[index] = new google.maps.Marker({
      position: new google.maps.LatLng(lng, lat),
      map: window.map,
      title: entry['title'],
      icon: 'http://maps.google.com/mapfiles/ms/icons/' + icon_filename
    });

    window.mc.addMarker(window.spot.marker[index]);

    window.spot.marker[index].index = index;

    google.maps.event.addListener(window.spot.marker[index], 'click', function() {
      for (var j=0; j<window.spot.infowindow.length; ++j) {
        window.spot.infowindow[j].close();
      }
      window.spot.infowindow[this.index].open(window.map, window.spot.marker[this.index]);
    });

    index = index + 1;
  });
  //alert( 'Total : ' + i.toString());
  window.waiting_response = false;
}

function get_delta(zoom) {
  if (zoom <= 10)
    return 0.05;
  else if (zoom <= 12)
    return 0.025;
  else if (zoom <= 14)
    return 0.01;
  else if (zoom <= 16)
    return 0.005;
  else if (zoom <= 18)
    return 0.0025;
  else 
    return 0.001; 
}

function do_search_bypos( lat, lng ) {

  //$.getJSON('data/test',{ 'lat':lat.toString(),'lng':lng.toString()},function(data) {
  //});
  //return;

  $('#mask, .popup_div').hide();
  //alert(lat.toString() + ' / ' + lng.toString());

  if (window.waiting_response) {
    //alert('ignored!');
    return;
  }

  window.waiting_response = true;

  window.map.setCenter(new google.maps.LatLng(lat, lng));
  var zoomLevel = window.map.getZoom();
  request_url = 'data/querybox';

  var delta = get_delta(zoomLevel);
  var north = lng + delta*0.8;
  var east = lat + delta*0.8;
  var south = lng - delta*0.8;
  var west = lat - delta*0.8;
  $.getJSON(request_url,{'result':'100', 'north':north.toString(),'east':east.toString(),'south':south.toString(),'west':west.toString()},function(data) {
    complete_search_bypos(data);
  });

  north = lng + delta*3;
  east = lat + delta*2;
  south = lng - delta*3;
  west = lat - delta*2;
/*
  var rectangle = new google.maps.Rectangle({
    strokeColor: '#FF0000',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#00FF00',
    fillOpacity: 0.1,
    map: window.map,
    bounds: new google.maps.LatLngBounds(
      new google.maps.LatLng( west, south), 
      new google.maps.LatLng( east, north)
    )
  });
*/

  $.getJSON(request_url,{'result':'1000', 'north':north.toString(),'east':east.toString(),'south':south.toString(),'west':west.toString()},function(data) {
    complete_search_bypos(data);
  });
}

function request_search_from_moveevent() {
  var center = window.map.getCenter();
  //alert('bounds_changed ' + center.toString() );
  //loc.lat(), loc.lng()
  do_search_bypos( center.lat(), center.lng() );
}

$(document).ready(function() {

  $("#area1").change(function() {
    var area1_val = $("#area1").val();
    var area2 = $('#area2');
    area2.empty();
    area2.append("<option value='선택'>선택</option>");
    for (var index in area_code[area1_val] ) {
      var city = $.map(area_code[area1_val][index], function(value, key) {
        return key;
      });
      var city_code = $.map(area_code[area1_val][index], function(value, key) {
        return value;
      });

      var append_str = "<option value='".concat(city_code).concat("'>").concat(city).concat("</option>");
      area2.append(append_str);
    }
  });

  $("#area2").change(function() {
    var area2_val = $("#area2").val();
    var area_array = area2_val.split(" ");
    do_search( area_array[0], area_array[1] );
  });

  $('.popup_div .submit_btn').click(function (e) {
    var area2_val = $("#area2").val();
    var area_array = area2_val.split(" ");  
    do_search( area_array[0], area_array[1] );
  });

  google.maps.event.addListener(window.map, 'rightclick', function(e) {
    var loc = e.latLng;
    do_search_bypos(loc.lat(), loc.lng());
  });

  window.waiting_response = false;

  /*  
  google.maps.event.addListener(window.map, 'dragend', function() {
    request_search_from_moveevent();
  });

  google.maps.event.addListener(window.map, 'bounds_changed', function() {
    request_search_from_moveevent();
  });
  */

});