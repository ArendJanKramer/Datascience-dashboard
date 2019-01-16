var lossChart;

// Helper function needed for converting the Objects to Arrays
function objectToArray(p) {
    var keys = Object.keys(p);
    keys.sort(function (a, b) {
        return a - b;
    });

    var arr = [], idx = [];
    for (var i = 0; i < keys.length; i++) {
        arr.push(p[keys[i]]);
        idx.push(keys[i]);
    }
    return [idx, arr];
}

// Functions to update data in page
var failures = 0;

function updateDatasets() {
    $.getJSON("api/get_datasets", function (data) {
        $('ul#dataset li').remove();

        for (var key in data) {
            // check if the property/key is defined in the object itself, not in parent
            if (data.hasOwnProperty(key)) {
                $('ul#dataset').append('<li><a data-maker="' + data[key] + '">' + data[key] + '</a></li>');
            }
        }

        $('ul#dataset li').click(function () {
            $.ajax({
                type: "POST",
                url: "api/set_dataset",
                data: $(this).text(),
                success: function () {
                    updateAll();
                }
            });
        });

    }).done(function () {
        // Reload graph after 10 minutes
        failures = 0;
        setTimeout(updateDatasets, 10000);
    }).fail(function () {
        failures++;
        if (failures < 5) {
            // Try again after 1 minute only if this has not failed more
            // than five times in a row
            setTimeout(updateDatasets, 10000);
        }
    });
}


function updateSummary() {
    $.getJSON("api/summary", function (data) {

        $("#summary_loss_function").text(String(data.loss_function));
        $("#summary_last_epoch").text(String(data.last_epoch));

        $("#dataset-button").text(String(data.dataset));

    }).done(function () {
        // Reload graph after 10 minutes
        failures = 0;
        setTimeout(updateSummary, 10000);
    }).fail(function () {
        failures++;
        if (failures < 5) {
            // Try again after 1 minute only if this has not failed more
            // than five times in a row
            setTimeout(updateSummary, 10000);
        }
    });
}

function updateQueriesOverTime() {
    $.getJSON("api/loss", function (data) {

        // convert received objects to arrays
        data.training_loss = objectToArray(data.training_loss);
        data.validation_loss = objectToArray(data.validation_loss);

        lossChart.data.labels = [];
        lossChart.data.datasets[0].data = [];
        lossChart.data.datasets[1].data = [];

        // Add data for each hour that is available
        for (var epoch in data.training_loss[0]) {
            if ({}.hasOwnProperty.call(data.training_loss[0], epoch)) {
                var e;
                e = parseInt(data.training_loss[0][epoch]);

                lossChart.data.labels.push(String(e));
                lossChart.data.datasets[0].data.push(data.training_loss[1][epoch]);
                lossChart.data.datasets[1].data.push(data.validation_loss[1][epoch]);
            }
        }

        $("#queries-over-time .overlay").hide();
        lossChart.update();
    }).done(function () {
        // Reload graph after 10 minutes
        failures = 0;
        setTimeout(updateQueriesOverTime, 10000);
    }).fail(function () {
        failures++;
        if (failures < 5) {
            // Try again after 1 minute only if this has not failed more
            // than five times in a row
            setTimeout(updateQueriesOverTime, 10000);
        }
    });
}

function updateAll() {
    updateDatasets();
    updateQueriesOverTime();
    updateSummary();
}

$(document).ready(function () {

    // Pull in data via AJAX
    var ctx = document.getElementById("lossChart").getContext("2d");
    lossChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Training",
                    fill: true,
                    backgroundColor: "rgba(110,220,110,0.1)",
                    borderColor: "rgba(0, 166, 90,.8)",
                    pointBorderColor: "rgba(0, 166, 90,.8)",
                    pointRadius: 1,
                    pointHoverRadius: 5,
                    data: [],
                    pointHitRadius: 5,
                    cubicInterpolationMode: "monotone"
                },
                {
                    label: "Validation",
                    fill: true,
                    backgroundColor: "rgba(0,192,239,0.1)",
                    borderColor: "rgba(0,192,239,1)",
                    pointBorderColor: "rgba(0,192,239,1)",
                    pointRadius: 1,
                    pointHoverRadius: 5,
                    data: [],
                    pointHitRadius: 5,
                    cubicInterpolationMode: "monotone"
                }
            ]
        },
        options: {
            tooltips: {
                enabled: true,
                mode: "x-axis",
                callbacks: {
                    title: function (tooltipItem, data) {
                        var label = tooltipItem[0].xLabel;
                        return "Epoch " + label;
                    },
                    label: function (tooltipItems, data) {
                        return data.datasets[tooltipItems.datasetIndex].label + ": " + tooltipItems.yLabel;

                    }
                }
            },
            legend: {
                display: false
            },
            scales: {
                xAxes: [{}],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            maintainAspectRatio: false
        }
    });

    // Pull in data via AJAX
    updateAll();

});
