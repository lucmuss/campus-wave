

function secondsToHtmlString(seconds) {
    var date = new Date(null);
    date.setSeconds(seconds);
    var stringDate = date.toISOString().substr(11, 8);
    return " - " + stringDate;
}

function getDefaultValues() {
    var secondsFrom = $(".secondsFrom").val();
    var secondsTo = $(".secondsTo").val();

    if (secondsTo == "") {
        secondsTo = '3600'
    }

    if (secondsFrom == "") {
        secondsFrom = '0'
    }

    return [secondsFrom, secondsTo];
}

default_values = getDefaultValues();

$(function() {

    $(".datePickerFrom").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "dd.mm.yy"
    });

    $(".datePickerTo").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: "dd.mm.yy"
    });

    $(".secondSlider").slider({
        range: true,
        min: 0,
        max: 3600,
        values: default_values,
        change: function(a, dataArray) {
            $(".secondsFrom").val(dataArray.values[0]);
            $(".secondsTo").val(dataArray.values[1]);

            $(".secondsFromHelp").html(secondsToHtmlString(dataArray.values[0]));
            $(".secondsToHelp").html(secondsToHtmlString(dataArray.values[1]));
        }
    });

    $( ".displayHiddenOptionsButton" ).click(function() {
    $( ".hiddenOptionsContainer" ).toggle( "fast", function() {
    // Animation complete.
    });
    });


    $('.resetButton').click(function() {
        $(':input','#myform')
            .not(':button, :submit, :reset, :hidden')
            .val('')
            .removeAttr('checked')
            .removeAttr('selected');
            $(".secondSlider").slider({
        range: true,
        min: 0,
        max: 3600,
        values: default_values,
        change: function(a, dataArray) {
            $(".secondsFrom").val(dataArray.values[0]);
            $(".secondsTo").val(dataArray.values[1]);

            $(".secondsFromHelp").html(secondsToHtmlString(dataArray.values[0]));
            $(".secondsToHelp").html(secondsToHtmlString(dataArray.values[1]));
        }
    });
    });

    $('.booleanInsertButton').click(function() {
    var booleanOperator = $(this).html();
    var inputValue = $("#mainTextInput").val();
    $("#mainTextInput").val(inputValue + " " + booleanOperator + " ");
    });



});


if ($("#termChart").length) {

    var canvasElement = $("#termChart");
    var dataPoints = $("#termChartData").val().split(";");
    var backgroundColors = $("#termChartBackgroundColors").val().split(";");
    var dataLabels = $("#termChartDataLabels").val().split(";");


    var dataset = {
        labels: dataLabels,
        datasets: [{
            data: dataPoints,
            backgroundColor: backgroundColors
        }]
    };


    var myChart = new Chart(canvasElement, {
        type: "doughnut",
        data: dataset
    });

}

if ($("#downToResult").length) {
$('html, body').animate({ scrollTop: $("#downToResult").offset().top}, 0);
}

//plyr.setup({ iconUrl: "/static/javascript/lib/plyr/svg/plyr.svg", debug: True });
