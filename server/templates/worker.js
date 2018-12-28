self.addEventListener('message', function(e) {
  var data = e.data;
  self.postMessage({'mesh': data.mesh, 'motionParams': data.motionParams});
}, false);
