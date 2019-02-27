//Video record and upload
// function startRecord(){
(function(){
  var player = document.getElementById('player');
  var snapshotCanvas = document.getElementById('snapshot');

  var handleSuccess = function(stream) {
    player.srcObject = stream;
  };
  function postImg(Img){
    var formData = new FormData();
    formData.append("fname",currentMotion);
    formData.append("data",Img);
    $.ajax({
      type: 'POST',
      url: '/openface',
      async: true,
      cache: false,
      data: formData,
      processData: false,
      contentType: false,
      success: function(res){
        setTimeout(function(){
          document.getElementById("gaze").innerHTML = 'Gaze: ' + JSON.parse(res)["gaze"];
          document.getElementById("emotion").innerHTML = 'Emotion: ' + JSON.parse(res)["emotion"];
          console.log(JSON.parse(res)["emotion"]);
          shot();
        },0)
      },
    });
  }
  function shot(){
    var context = snapshotCanvas.getContext('2d');
    context.drawImage(player, 0, 0, snapshotCanvas.width, snapshotCanvas.height);
    snapshotCanvas.toBlob(postImg, 'image/jpeg');
  }
  navigator.mediaDevices.getUserMedia({video: true})
      .then(handleSuccess);
  shot();
})()
