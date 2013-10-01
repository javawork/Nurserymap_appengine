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

    $('.openMask').click(function(e){
        e.preventDefault();
        wrapWindowByMask();
    });

    $('.popup_div .close_btn').click(function (e) {  
        e.preventDefault();  
        $('#mask, .popup_div').hide();  
    });

    $('.notice_close_btn').click(function (e) {  

      $( "#notice_div" ).animate({
        height: "0px"
      }, 100 );

      $( "#map_canvas" ).animate({
          height: "100%"
      }, 100, function() {
          window.map.relayout();
      }); 
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

  google.maps.event.addDomListener(controlUI, 'click', function() {
    wrapWindowByMask();
  });
}

$(document).ready(function() {
  var mapOptions = {
    center: new google.maps.LatLng(37.5663176911162, 126.97782838162229),
    zoom: 14,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  window.map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
  //var mcOptions = {gridSize: 50, maxZoom: 13};
  var mcOptions = {gridSize: 70, maxZoom: 14};
  window.mc = new MarkerClusterer(window.map, [], mcOptions);

  window.spot = {marker:[], infowindow:[], idset:{} };

  // Create the DIV to hold the control and call the HomeControl() constructor
  // passing in this DIV.
  var homeControlDiv = document.createElement('div');
  var homeControl = new HomeControl(homeControlDiv, window.map);

  homeControlDiv.index = 1;
  window.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);

  //wrapWindowByMask();
});
