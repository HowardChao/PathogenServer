// function reply_click(clicked_id){
//   // Remove selected file
//   console.log("clicked_id: ", clicked_id);
//   var key_id = clicked_id.replace('button_file_', '');
//   console.log("remove element id: ", "file_" + key_id);
//   document.getElementById("file_" + key_id).remove();
//   console.log("Before deleting: ", selectedFiles);
//   delete selectedFiles[key_id];
//   console.log("After deleting: ", selectedFiles);
// }

$(function () {

  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });




  // $(function () {
  //     $('#fileupload').fileupload({
  //         dataType: 'json',
  //         add: function (e, data) {
  //             data.context = $('<button/>').text('Upload')
  //                 .appendTo(document.body)
  //                 .click(function () {
  //                     data.context = $('<p/>').text('Uploading...').replaceAll($(this));
  //                     data.submit();
  //                 });
  //         },
  //         done: function (e, data) {
  //             data.context.text('Upload finished.');
  //         }
  //     });
  // });


  $("#up_btn").on('click', function (e) {
      e.preventDefault();
      $("#up_btn").trigger( "customName_submit_all_file");
  });


  $("#fileupload").fileupload({
   dataType: 'json',
   sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */


       // data.context = $('press-to-upload').text('Upload')
       //     .appendTo(document.body)
       //     .click(function () {
       //         data.context = $('<p/>').text('Uploading...').replaceAll($(this));
       //         data.submit();
       //     });
   add: function (e, data) {
      console.log("datadata: ", data);
      $.each(data.files, function (index, file) {
        // var newFileDiv = $("<div class='uploadBox' id='fileDiv_" + file.name + "'><div class='leftEle'><a href='#' id='link_" + index + "' class='removeFile'>Remove</a></div><div class='midEle'>" + file.name + "</div></div>");
        var newFilepulgin = $('<tr id="file_'+ file.name +'"><td><button type="button" class="btn btn-outline-danger" id="button_file_'+ file.name +'">remove selected file</button>&nbsp&nbsp&nbsp&nbsp <b>Filename: </b><a href="#" id="link_' + index + '" class="removeFile"> '+ file.name + '</a> &nbsp&nbsp&nbsp&nbsp <b>File Size: </b>'+ file.size +' byte </td></tr>');
        $('#data_selected_body').append(newFilepulgin);
        newFilepulgin.find('button').on('click', { filename: file.name, files: data.files }, function (event) {
            console.log("Button clicked!");
            event.preventDefault();
            var uploadFilesBox = $("#data_selected_body");
            var remDiv = $(document.getElementById("file_" + event.data.filename));
            remDiv.remove();
            data.files.length = 0;    //zero out the files array

        });
        data.context = newFilepulgin;
      });

       $("#up_btn").click(function () {
           if (data.files.length > 0) {     //only submit if we have something to upload
               data.submit();
               console.log("$$$$$data.files.name: ", data.files[0].name);
               var myNode = document.getElementById("file_" + data.files[0].name);
               console.log("myNode: ", myNode);
               myNode.innerHTML = '';
           }
           // var myNode = $("#data_selected_body");
           // var myNode = document.getElementById("data_selected_body");
           // myNode.innerHTML = '';
       });
   },
   start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
     $("#modal-progress").modal("show");
   },
   stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
     $("#modal-progress").modal("hide");
     window.location.reload();
   },
   progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
     var progress = parseInt(data.loaded / data.total * 100, 10);
     var strProgress = progress + "%";
     $(".progress-bar").css({"width": strProgress});
     $(".progress-bar").text(strProgress);
   },
   done: function (e, data) {
     console.log("data.result.is_valid:", data)
     if (data.result.is_valid) {
       $("#gallery tbody").prepend(
         // "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
         '<tr id="upload_'+ data.result.name +'"><td><div class="row"><div class="col-6 col-md-4"><b>Filename: </b><a href="'+ data.result.url + '" id="link_' + data.result.name + '" class="removeFile"> '+ data.result.name + '</a>  </div><div class="col-6 col-md-4"><b>File Size: </b> byte &nbsp&nbsp&nbsp&nbsp </div><div class="col-6 col-md-4"><button id="button_file_'+ data.result.name +'">remove selected file</button> </div></div></td></tr>'
         // '<tr><td>111</td></tr>'
       )
     }
   }

 });

});


//
//
// var selectedFiles = {};
// function reply_click(clicked_id){
//   // Remove selected file
//   console.log("clicked_id: ", clicked_id);
//   var key_id = clicked_id.replace('button_file_', '');
//   console.log("remove element id: ", "file_" + key_id);
//   document.getElementById("file_" + key_id).remove();
//   console.log("Before deleting: ", selectedFiles);
//   delete selectedFiles[key_id];
//   console.log("After deleting: ", selectedFiles);
// }
// $('#fileupload').on('change',function(){
//     //get the file name
//     var fileList = document.getElementById("fileupload").files;
//     var myNode = document.getElementById("data_selected_body");
//     // myNode.innerHTML = '';
//     for (var i=0; i<fileList.length; i++) {
//       selectedFiles[i] = fileList[i]
//       // <tr>
//       //   <td><a href="{{ data.file.url }}">{{ data.file.name }}</a></td>
//       // </tr>
//       $('#data_selected_body').append('<tr id="file_'+i.toString() +'"><td><b>Filename: </b><a href=""> '+ fileList[i].name + '</a> &nbsp&nbsp&nbsp&nbsp <b>File Size: </b>'+ fileList[i].size +' byte &nbsp&nbsp&nbsp&nbsp <button id="button_file_'+i.toString() +'" onClick="reply_click(this.id)">remove selected file</button></td></tr>')
//       console.log(fileList[i]);
//       console.log(selectedFiles);
//     }
//
//     //
//     // var fileName = $(this).val();
//     // var cleanFileName = fileName.replace('C:\\fakepath\\', " ");
//     // //replace the "Choose a file" label
//     // $(this).next('.custom-file-label').html(cleanFileName);
//     // reg_exp_1 = /([a-zA-Z0-9\s_\\.\-\(\):])+(.R1.fastq.gz)$/i
//     // if (cleanFileName.match(reg_exp_1)) {
//     //     console.log("Change color to green");
//     //     $('#inputGroupFile01').css("background-color", "#97dbac");
//     // } else {
//     //     console.log("Change color to red");
//     //     $('#inputGroupFile01').css("background-color", "#db9797");
//     // }
// });
