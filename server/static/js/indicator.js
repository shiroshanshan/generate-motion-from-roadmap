//State indicator
(function(){
  var script=document.createElement('script');
  script.onload=function(){
    var stats=new Stats();
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.top = '30px';
    stats.domElement.style.left = '87%';
    stats.domElement.style.zIndex = 100;
    document.body.appendChild(stats.dom);
    requestAnimationFrame(function loop(){
      stats.update();
      requestAnimationFrame(loop)
    });
  };
  script.src='//mrdoob.github.io/stats.js/build/stats.min.js';
  document.head.appendChild(script);
})()
