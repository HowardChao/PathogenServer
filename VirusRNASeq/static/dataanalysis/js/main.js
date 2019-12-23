
// $('#inputGroupFile01').on('change', function () {
//     //get the file name
//     var fileName = $(this).val();
//     var cleanFileName = fileName.replace('C:\\fakepath\\', " ");
//     //replace the "Choose a file" label
//     $(this).next('.custom-file-label').html(cleanFileName);
// })

// $('#inputGroupFile02').on('change', function () {
//     //get the file name
//     var fileName = $(this).val();
//     var cleanFileName = fileName.replace('C:\\fakepath\\', " ");
//     //replace the "Choose a file" label
//     $(this).next('.custom-file-label').html(cleanFileName);
// })

// $('#paired-end-button').click(function () {
//     if (document.getElementById("inputGroupFile01").files.length == 0 && document.getElementById("inputGroupFile02").files.length == 0) {
//         console.log("Both files have not selected");
//         alert("Both files have not selected");
//         return false;
//     } else if (document.getElementById("inputGroupFile01").files.length == 0) {
//         console.log("File 1 have not selected");
//         alert("File 1 have not selected");
//         return false;
//     } else if (document.getElementById("inputGroupFile02").files.length == 0) {
//         console.log("File 2 have not selected");
//         alert("File 2 have not selected");
//         return false;
//     } else if (document.getElementById("inputGroupFile01").files.length == 1 && document.getElementById("inputGroupFile02").files.length == 1) {
//         console.log("Both file are selected")
//     } else {
//         console.log("There are something wrong!!!")
//         return false;
//     }
// })