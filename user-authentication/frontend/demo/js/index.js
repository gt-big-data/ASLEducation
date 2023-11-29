const video = document.getElementById("myvideo");
const handimg = document.getElementById("handimage");
const canvas = document.getElementById("canvas");
const canvas2 = document.getElementById("canvas2");
const context = canvas.getContext("2d");
const context2 = canvas2.getContext("2d");
let trackButton = document.getElementById("trackbutton");
let nextImageButton = document.getElementById("nextimagebutton");
let updateNote = document.getElementById("updatenote");

let imgindex = 1;
let isVideo = false;
let model = null;

// video.width = 500
// video.height = 400

const modelParams = {
  flipHorizontal: true, // flip e.g for video
  maxNumBoxes: 20, // maximum number of boxes to detect
  iouThreshold: 0.5, // ioU threshold for non-max suppression
  scoreThreshold: 0.6, // confidence threshold for predictions.
};

function startVideo() {
  handTrack.startVideo(video).then(function (status) {
    console.log("video started", status);
    if (status) {
      updateNote.innerText = "Video started. Now tracking";
      isVideo = true;
      runDetection();
    } else {
      updateNote.innerText = "Please enable video";
    }
  });
}

function toggleVideo() {
  if (!isVideo) {
    updateNote.innerText = "Starting video";
    startVideo();
  } else {
    updateNote.innerText = "Stopping video";
    handTrack.stopVideo(video);
    isVideo = false;
    updateNote.innerText = "Video stopped";
  }
}

nextImageButton.addEventListener("click", function () {
  nextImage();
});

trackButton.addEventListener("click", function () {
  toggleVideo();
});

function nextImage() {
  imgindex++;
  handimg.src = "images/" + (imgindex % 9) + ".jpg";
  // alert(handimg.src)
  setTimeout(() => {
    runDetectionImage(handimg);
  }, 500);
}

function dataURItoBlob(dataURI) {
  // convert base64 to raw binary data held in a string
  // doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
  var byteString = atob(dataURI.split(',')[1]);

  // separate out the mime component
  var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]

  // write the bytes of the string to an ArrayBuffer
  var ab = new ArrayBuffer(byteString.length);

  // create a view into the buffer
  var ia = new Uint8Array(ab);

  // set the bytes of the buffer to the correct values
  for (var i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
  }

  // write the ArrayBuffer to a blob, and you're done
  var blob = new Blob([ab], {type: mimeString});
  return blob;

}

function dataURLtoBlob2(dataurl) {
  var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
      bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
  while(n--){
      u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], {type:mime});
}

function blobToDataURL(blob, callback) {
  var a = new FileReader();
  console.log("in blob to url");
  a.onload = function(e) {callback(e.target.result);}
  a.readAsDataURL(blob);
}

var ctr = 0;
//This function infinitely loops (calls itself)
function runDetection() {
  model.detect(video).then(async (predictions) => {
    //console.log("Predictions 1: ", predictions);
    var removeInd = -1;
    for (var i = 0; i < predictions.length; i++) {
      if (predictions[i].class == 5) {
        removeInd = i;
        break;
      }
    }
    if (removeInd > -1) {
      predictions.splice(removeInd, 1);
    }
    //console.log("Predictions: ", predictions);

    var predictedLetter = "";

    if (predictions.length > 0) {
      //Predictions are ordered by score (highest confidence to lowest)

      var pred = predictions[0];
      var boxCoords = pred.bbox;    //format: [left edge, top edge, width, height]
      //console.log(boxCoords)

      
      var dataURL = canvas.toDataURL('image/jpeg');
      //console.log(dataURL);
      
      
      context2.canvas.width = boxCoords[2];
      context2.canvas.height = boxCoords[3];
      context2.clearRect(0, 0, canvas2.width, canvas2.height);
      context2.scale(-1, 1);   //do if horizontal flip is in model params
      context2.translate(-boxCoords[2], 0);  //do if horizontal flip is in params
      context2.drawImage(video,
        video.width - boxCoords[2] - boxCoords[0], boxCoords[1],   // Start at N pixels from the left and the top of the image (crop),
        boxCoords[2], boxCoords[3],   // "Get" a (w * h) area from the source image (crop),
        0, 0,     // Place the result at 0, 0 in the canvas,
        boxCoords[2], boxCoords[3]); // With as width / height: 160 * 60 (scale)  
      // context.drawImage(video,
      //   boxCoords[0], boxCoords[1],   // Start at N pixels from the left and the top of the image (crop),
      //   boxCoords[2], boxCoords[3],   // "Get" a (w * h) area from the source image (crop),
      //   0, 0,     // Place the result at 0, 0 in the canvas,
      //   boxCoords[2], boxCoords[3]); // With as width / height: 160 * 60 (scale)  
      
      dataURL = canvas2.toDataURL('image/jpeg');
      //console.log(dataURL);

      var blob = dataURLtoBlob2(dataURL);
      // var urlCreator = window.URL || window.webkitURL; 
      // var imageUrl = urlCreator.createObjectURL(blob); 

      // blobToDataURL(blob, function(dataurl){
      //   console.log(dataurl);
      // });

      console.log(blob);

      async function sendBlob(blob) {
        const formData = new FormData();
        formData.append('file', blob);
        
        const response = await fetch('/', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        console.log(data.prediction);
        return data.prediction;
      } 

      predictedLetter = await sendBlob(blob);
    }
    
    //The following function sits in /src/index.js but any changes there do not reflect on the front end
    //It actually uses /demo/handtrack.min.js, which is contents off /src/index.js and a bunch of other files, compressed
    //So, when u want to change /src/index.js, actually change /demo/handtrack.min.js

    model.renderPredictions(predictions, canvas, context, video, predictedLetter); //draws prediction - bounding box and label

    setTimeout(function() { //wait 500ms - this is hacky, please remove later
      if (isVideo) {
        requestAnimationFrame(runDetection);    //some kind of recursive call
      }
    }, 1000);
  });
}

function runDetectionImage(img) {
  model.detect(img).then((predictions) => {
    console.log("Predictions: ", predictions);
    model.renderPredictions(predictions, canvas, context, img);
  });
}

// Load the model.
handTrack.load(modelParams).then((lmodel) => {
  // detect objects in the image.
  model = lmodel;
  console.log(model);
  updateNote.innerText = "Loaded Model!";
  runDetectionImage(handimg);
  trackButton.disabled = false;
  nextImageButton.disabled = false;
});
