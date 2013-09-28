function start_spin() {
  var opts = {
    lines: 13, // The number of lines to draw
    length: 20, // The length of each line
    width: 10, // The line thickness
    radius: 30, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#000', // #rgb or #rrggbb
    speed: 1, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: 'auto', // Top position relative to parent in px
    left: 'auto' // Left position relative to parent in px
  };
  var target = document.getElementById('map_canvas');
  window.spinner = new Spinner(opts).spin(target);
}

function stop_spin() {
  if (window.spinner != null) {
    window.spinner.stop();
  }
}

$( document ).ajaxStart(function() {
  start_spin();
});

$( document ).ajaxStop(function() {
  stop_spin();
});

/**
 * The HomeControl adds a control to the map that simply
 * returns the user to Chicago. This constructor takes
 * the control DIV as an argument.
 */
function wrapWindowByMask(){
    //화면의 높이와 너비를 구한다.
    var maskHeight = $(document).height();  
    var maskWidth = $(window).width();

    //마스크의 높이와 너비를 화면 것으로 만들어 전체 화면을 채운다.
    $('#mask').css({'width':maskWidth,'height':maskHeight});  
    //애니메이션 효과 - 일단 0초동안 까맣게 됐다가 60% 불투명도로 간다.
    $('#mask').fadeIn(0);      
    $('#mask').fadeTo("slow",0.6);    
    $('.popup_div').show();
}

$(document).ready(function(){
    //검은 막 띄우기
    $('.openMask').click(function(e){
        e.preventDefault();
        wrapWindowByMask();
    });
    //닫기 버튼을 눌렀을 때
    $('.popup_div .close_btn').click(function (e) {  
        //링크 기본동작은 작동하지 않도록 한다.
        e.preventDefault();  
        $('#mask, .popup_div').hide();  
    });
});

function HomeControl(controlDiv, map) {

  // Set CSS styles for the DIV containing the control
  // Setting padding to 5 px will offset the control
  // from the edge of the map.
  controlDiv.style.padding = '7px';

  // Set CSS for the control border.
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = 'white';
  controlUI.style.borderStyle = 'solid';
  controlUI.style.borderWidth = '2px';
  controlUI.style.cursor = 'pointer';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click to set the map to Home';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  var controlText = document.createElement('div');
  controlText.style.fontFamily = 'Arial,sans-serif';
  controlText.style.fontSize = '12px';
  controlText.style.paddingLeft = '4px';
  controlText.style.paddingRight = '4px';
  controlText.innerHTML = '<strong>지역선택</strong>';
  controlUI.appendChild(controlText);

  //chicago = new google.maps.LatLng(37.5663176911162, 126.97782838162229)
  // Setup the click event listeners: simply set the map to Chicago.
  google.maps.event.addDomListener(controlUI, 'click', function() {
    //map.setCenter(chicago)
    wrapWindowByMask();
  });
}

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

$(document).ready(function() {
  var mapOptions = {
    center: new google.maps.LatLng(37.5663176911162, 126.97782838162229),
    zoom: 14,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  window.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

  // Create the DIV to hold the control and call the HomeControl() constructor
  // passing in this DIV.
  var homeControlDiv = document.createElement('div');
  var homeControl = new HomeControl(homeControlDiv, window.map);

  homeControlDiv.index = 1;
  window.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);

  //wrapWindowByMask();
});

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
});

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
    + entry['own'] + ' / ' + entry['auth']
    + '</td></tr>'
    + '<tr><td>'
    + '정원 : ' + entry['capacity'] + ' / ' + entry['phone']
    + '</td></tr>'
    + '<tr><td>'
    + entry['lat'] + ' / ' + entry['lng'] 
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
    
    cleanup_prev_spots();
    window.spot = {marker:[], infowindow:[] };

    var i = 0;
    var sumOfLat = 0;
    var sumOfLng = 0;
    var minLng = 1000000.0;
    var minLat = 1000000.0;
    var maxLng = 0.0;
    var maxLat = 0.0;

    $.each(data, function(entryIndex, entry) {
      //alert( entry['title']+'/' + entry['own'] +'/'+ showResult.toString() );
      if ( !displayableOwnType(entry['own']) ) {
        return true;
      }

      info_text = build_text_for_infowindow(entry);
      window.spot.infowindow[i] = new google.maps.InfoWindow({
        content: info_text
      });

      var icon_filename = get_icon_filename(entry['own']);

      var lng = parseFloat(entry['lng'])
      var lat = parseFloat(entry['lat'])
      window.spot.marker[i] = new google.maps.Marker({
        position: new google.maps.LatLng(lng, lat),
        map: window.map,
        title: entry['title'],
        icon: 'http://maps.google.com/mapfiles/ms/icons/' + icon_filename
      });

      minLng = Math.min(lng, minLng);
      minLat = Math.min(lat, minLat);
      maxLng = Math.max(lng, maxLng);
      maxLat = Math.max(lat, maxLat);

      window.spot.marker[i].index = i;

      google.maps.event.addListener(window.spot.marker[i], 'click', function() {
        for (var j=0; j<window.spot.infowindow.length; ++j) {
          window.spot.infowindow[j].close();
        }
        window.spot.infowindow[this.index].open(window.map, window.spot.marker[this.index]);
      });

      sumOfLng = sumOfLng + parseFloat(entry['lng']);
      sumOfLat = sumOfLat + parseFloat(entry['lat']);

      i = i + 1;
    });

    alert( 'Total : ' +
      //sumOfLng.toString() + '/' +
      //minLat.toString() + '/' +
      //maxLat.toString() + '/' +
      i.toString()
      );

    if (i > 0) {
      var centerLng = sumOfLng/i;
      var centerLat = sumOfLat/i;
      window.map.setCenter(new google.maps.LatLng(centerLng, centerLat));
      if ( i > 1 ) {
        var zoomLevel = calcZoomLevel(minLng, minLat, maxLng, maxLat);
        //alert("ZoomLevel : ".concat(zoomLevel.toString()));
        window.map.setZoom(zoomLevel);
      }
    } else {
      //alert('Nothing');
    }
    //alert(i);
  });
}

function do_search_bypos( lat, lng ) {

  $('#mask, .popup_div').hide();

  window.map.setCenter(new google.maps.LatLng(lat, lng));
  var zoomLevel = window.map.getZoom();
  request_url = 'data/querybox';
  $.getJSON(request_url,{'lat':lng.toString(), 'lng':lat.toString(), 'zoom':zoomLevel.toString()},function(data) {

    cleanup_prev_spots();
    window.spot = {marker:[], infowindow:[] };

    var i = 0;
    $.each(data, function(entryIndex, entry) {
      //alert( entry['title']+'/' + entry['own'] +'/'+ showResult.toString() );
      if ( !displayableOwnType(entry['own']) ) {
        return true;
      }

      info_text = build_text_for_infowindow(entry);
      window.spot.infowindow[i] = new google.maps.InfoWindow({
        content: info_text
      });

      var icon_filename = get_icon_filename(entry['own']);

      var lng = parseFloat(entry['lng'])
      var lat = parseFloat(entry['lat'])
      window.spot.marker[i] = new google.maps.Marker({
        position: new google.maps.LatLng(lng, lat),
        map: window.map,
        title: entry['title'],
        icon: 'http://maps.google.com/mapfiles/ms/icons/' + icon_filename
      });

      window.spot.marker[i].index = i;

      google.maps.event.addListener(window.spot.marker[i], 'click', function() {
        for (var j=0; j<window.spot.infowindow.length; ++j) {
          window.spot.infowindow[j].close();
        }
        window.spot.infowindow[this.index].open(window.map, window.spot.marker[this.index]);
      });

      i = i + 1;
    });
    //alert( 'Total : ' + i.toString());
  });
}

$(document).ready(function() {
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
    loc = e.latLng;
    //alert(loc.toString());
    do_search_bypos(loc.lat(), loc.lng());
  });

});