function get(value){
  var xmlHttp  = new XMLHttpRequest();
  xmlHttp.open( "GET", value, false );
  xmlHttp.send( null );
  return xmlHttp.responseText;
}

self.addEventListener('message', function(e) {
  console.log('Worker said: ', e.data);
  setTimeout(get(e.data), 100);
}, false);