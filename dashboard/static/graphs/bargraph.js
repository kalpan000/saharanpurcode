function randomColor(count = 0, returnArray = false) {
    if (count == 0)
        return "#000000".replace(/0/g, function() { return (~~(Math.random() * 16)).toString(16); }) + "77";

    var colors = [];
    while (count != 0) {
        colors.push("#000000".replace(/0/g, function() { return (~~(Math.random() * 16)).toString(16); }) + "77")
        count--;
    }

    return colors;
}


// CHART JS 


function loadNewData(chart, label, inputs, removeFirstElement = false, maxDataSize = -1) {


    // data = {"labels" : [] , "barlabel" : [] ,  "y" : [ [] , [] ] , "bgcolor" : [] , "bordercolor" : []} // labels are used as X axis

    if (inputs["y"][0].constructor === Array) {
        if (label != "")
            chart.data.labels = label;
        chart.data.datasets.every((dataset, index) => {
            console.log("Index", index);
            dataset.data = inputs["y"][index];
            return true;
        });

        // for (var i = 0; i < inputs["y"].length; i++) {
        //     arr.push({
        //         data: inputs["y"][i],
        //         backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"][i] : randomColor()),
        //         borderColor: (inputs["bordercolor"] ? inputs["bordercolor"][i] : randomColor()),
        //         borderWidth: 1
        //     });
        // }

    } else {
        chart.data.datasets = []
    }
    chart.update();
}

// data = [ [] ] size [1][1]
function updateGauge(chart, label, data, removeFirstElement = false, maxDataSize = -1) {
    value = data[0][0];
    chart.data.datasets[0].data = [value, 100 - value];
    chart.data.datasets[0].value = value;
    chart.options.plugins.subtitle.text = value;
    chart.update();
}


// data = [ [] , [] ] size [n][1]
function updatePie(chart, label, data, removeFirstElement = false, maxDataSize = -1) {
    var i = 0;
    var isArray = Array.isArray(data);


    var converted = []
    try {
        if (data[0].constructor === Array) {
            for (var i in data) {
                converted.push(data[i][0]);
            }
        } else converted = data[0];
    } catch (ex) {
        converted = data[0];
    }

    chart.data.datasets[0].data = converted;


    chart.update();
}


// data = [ [] ]  size = [n][x]
function updateChart(chart, label, data, removeFirstElement = false, maxDataSize = -1) {
    var i = 0;
    var isArray = Array.isArray(data);
    var removeElement = (maxDataSize != -1 && chart.data.datasets[0].data.length >= maxDataSize) || removeFirstElement;

    if (!removeElement) chart.data.labels.push((chart.data.datasets[0].length + 1) + "");
    chart.data.datasets.every((dataset, index) => {

        if (removeElement)
            dataset.data.shift();

        if (isArray) {
            dataset.data.push(data[i++]);
            return true;
        } else {
            dataset.data.push(data);

            return false;
        }
    });

    chart.update();
}

function updateChartLine(chart, label, data, removeFirstElement = false, maxDataSize = -1) {
    var i = 0;
    var isArray = Array.isArray(data);
    var removeElement = (maxDataSize != -1 && chart.data.datasets[0].data.length >= maxDataSize) || removeFirstElement;

    if (!removeElement) chart.data.labels.push(label);
    chart.data.datasets.every((dataset, index) => {
        if (removeElement) {
            dataset.data.shift();
        }
        if (isArray) {
            dataset.data.push(data[i++]);
            return true;
        } else {
            dataset.data.push(data);

            return false;
        }
    });

    chart.update();
}
var maximumPoints = 20; // with this variable you can decide how many points are display on the chart
function addData(chart, label, data) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        var d = data[0];
        dataset.data.push(d);
        data.shift();
    });


    var canRemoveData = false;
    chart.data.datasets.forEach((dataset) => {
        if (dataset.data.length > maximumPoints) {

            if (!canRemoveData) {
                canRemoveData = true;
                chart.data.labels.shift();
            }

            dataset.data.shift();

        }

    });



    chart.update();
}
// data = {"labels" : [] , "barlabel" : "" ,  "y" : [] , "bgcolor" : [  ] , "bordercolor" : [  ]}  // labels are used as X axis
function bar(inputs) {

    return {
        type: 'bar',
        data: {
            labels: inputs["labels"],
            datasets: [{
                label: inputs["barlabel"],
                data: inputs["y"],
                backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"] : randomColor(inputs["y"].length, true)),
                borderColor: (inputs["bordercolor"] ? inputs["bordercolor"] : randomColor(inputs["y"].length, true)),
                borderWidth: 1
            }]
        },
        options: Object.assign({}, CHARTJS_CONFIG),
    };
}


// data = {"labels" : [] , "barlabel" : [] ,  "y" : [ [] , [] ] , "bgcolor" : [] , "bordercolor" : []} // labels are used as X axis
function histo(inputs) {
    var arr = []
    for (var i = 0; i < inputs["y"].length; i++) {
        arr.push({
            label: inputs["barlabel"][i],
            data: inputs["y"][i],
            backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"][i] : randomColor()),
            borderColor: (inputs["bordercolor"] ? inputs["bordercolor"][i] : randomColor()),
            borderWidth: 1
        });
    }

    return {
        type: 'bar',
        data: {
            labels: inputs["labels"],
            datasets: arr,
        },
        options: Object.assign({}, CHARTJS_CONFIG),

    };

}

// data = {"labels" : [] , "barlabel" : [] ,  "y" : [ [] , [] ] , "bgcolor" : [] , "bordercolor" : [], "responsive": []} // labels are used as X axis
function line(inputs) {
    console.log("RESPONSIVE", inputs["responsive"]);
    var arr = []
    console.log("LINE DATA ", inputs)
    if (inputs["y"][0].constructor === Array) {

        for (var i = 0; i < inputs["y"].length; i++) {
            arr.push({
                label: inputs["barlabel"][i],
                data: inputs["y"][i],
                backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"][i] : randomColor()),
                borderColor: (inputs["bordercolor"] ? inputs["bordercolor"][i] : randomColor()),
                borderWidth: 1
            });
        }

    }


    var obj = {
        type: 'line',
        data: {
            labels: inputs["labels"],
            datasets: arr,
        },
        options: Object.assign({}, CHARTJS_CONFIG, { maintainAspectRatio: true }),
    };
    obj["options"]["scales"]["x"]["ticks"] = { display: true }
    obj["options"]["scales"]["y"]["ticks"] = { display: true, stepSize: 5 }
    return obj;
}

function line2(inputs) {
    console.log("RESPONSIVE", inputs["responsive"]);
    var arr = []
    console.log("LINE DATA ", inputs)
    if (inputs["y"][0].constructor === Array) {

        for (var i = 0; i < inputs["y"].length; i++) {
            arr.push({
                label: inputs["barlabel"][i],
                data: inputs["y"][i],
                backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"][i] : randomColor()),
                borderColor: (inputs["bordercolor"] ? inputs["bordercolor"][i] : randomColor()),
                borderWidth: 2
            });
        }

    }


    var obj = {
        type: 'line',
        data: {
            labels: inputs["labels"],
            datasets: arr,
        },
        options: Object.assign({}, CHARTJS_CONFIG, { maintainAspectRatio: false }),
    };

    // obj["options"]["scales"]["y"] = {suggestedMin: 0,suggestedMax: 10,}
    obj["options"]["scales"]["x"]["ticks"] = { display: true, maxTicksLimit: 10 }
    obj["options"]["scales"]["y"]["ticks"] = { display: true, stepSize: 5 }
    return obj;
}


// data = {"labels" : [] , "barlabel" : "",  "values" : [] , "bgcolor" : [] , "bordercolor" : []} // labels are used as X axis
function donut(inputs) {
    var converted = []
    try {
        if (inputs["y"][0].constructor === Array) {
            for (var i in inputs["y"]) {
                converted.push(inputs["y"][i][0]);
            }
        } else converted = inputs["y"];
    } catch (ex) {
        converted = inputs["y"][0];
    }



    var obj = {
        type: 'doughnut',
        data: {
            labels: inputs["labels"],
            datasets: [

                {
                    label: inputs["barlabel"],
                    data: converted,
                    backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"] : randomColor(converted.length, true)),
                },
            ],


        },
        options: Object.assign({}, CHARTJS_CONFIG),

    };

    return obj;
}


function gauge(inputs) {
    console.log("GAUGE", inputs);
    value = inputs["y"][0][0];

    var obj = {
        type: 'doughnut',
        data: {
            datasets: [{
                value: value,
                minValue: inputs["min"],
                data: [value, 100 - value],
                backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"] : randomColor(4, true)),
            }]
        },
        options: Object.assign({}, CHARTJS_CONFIG)

    };

    obj["options"]["rotation"] = 270;
    obj["options"]["circumference"] = 180;

    obj["options"]["plugins"] = {
        subtitle: {
            display: true,
            text: value,
            position: "bottom",

        }
    }
    obj["options"]["scales"]["x"]["ticks"] = { display: false }
    obj["options"]["scales"]["y"]["ticks"] = { display: false }
    return obj;
}
// data = {"labels" : [] , "barlabel" : "",  "values" : [] , "bgcolor" : [] , "bordercolor" : []} // labels are used as X axis
function pie(inputs) {



    var converted = []
    try {
        if (inputs["y"][0].constructor === Array) {
            for (var i in inputs["y"]) {
                converted.push(inputs["y"][i][0]);
            }
        } else converted = inputs["y"];
    } catch (ex) {
        converted = inputs["y"][0];
    }



    obj = {
        type: 'pie',
        data: {
            labels: inputs["labels"],
            datasets: [

                {
                    label: inputs["barlabel"],
                    data: converted,
                    backgroundColor: (inputs["bgcolor"] ? inputs["bgcolor"] : randomColor(2, true)),
                },
            ],


        },
        options: Object.assign({}, CHARTJS_CONFIG),

    };

    obj["options"]["scales"]["x"]["ticks"] = { display: false }
    obj["options"]["scales"]["y"]["ticks"] = { display: false }

    return obj;
}













// PLOTLY

// data = {"x" : [] , "y" : [] , "color" : ""} 
// data = {"x" : [ [] , [] ] , "y" : [ [] , [] ] , "color" : []}
function BarGraph(data) {

    var trace = {}
    var graphData = [];
    trace = {
        type: 'bar',
        marker: {
            line: { width: 2.5 }
        }
    };

    if (data["x"].length != data["y"].length) {
        console.log("length of data['x'] != data['y']");
        return false;
    }

    var traceCopy = Object.assign({}, trace);
    if (data["x"][0].constructor === Array) {

        for (var i in data["x"]) {
            traceCopy["color"] = data["color"] ? data["color"][i] : randomColor();
            traceCopy["x"] = data["x"][i];
            traceCopy["y"] = data["y"][i];
            traceCopy["name"] = data["name"][i];
            graphData.push(traceCopy)
            var traceCopy = Object.assign({}, trace);
        }
    } else {
        traceCopy["color"] = data["color"] ? data["color"] : randomColor();
        traceCopy["x"] = data["x"];
        traceCopy["y"] = data["y"];
        traceCopy["name"] = data["name"];
        graphData.push(traceCopy)
    }

    return graphData
}

// data = {"x" : [] , "y" : [] ,"name" : [], "color" : ""} 
// data = {"x" : [ [] , [] ] , "y" : [ [] , [] ] ,"name" : [], "color" : []}
function LineGraph(data) {

    var trace = {}
    var graphData = [];
    trace = {
        type: 'line',
        marker: {
            line: { width: 2.5 }
        }
    };

    if (data["x"].length != data["y"].length) {
        console.log("length of data['x'] != data['y']");
        return false;
    }

    var traceCopy = Object.assign({}, trace);
    if (data["x"][0].constructor === Array) {
        for (var i in data["x"]) {
            traceCopy["color"] = data["color"] ? data["color"][i] : randomColor();
            traceCopy["x"] = data["x"][i];
            traceCopy["y"] = data["y"][i];
            traceCopy["name"] = data["name"][i];
            graphData.push(traceCopy)
            var traceCopy = Object.assign({}, trace);
        }
    } else {
        traceCopy["color"] = data["color"] ? data["color"] : randomColor();
        traceCopy["x"] = data["x"];
        traceCopy["y"] = data["y"];
        traceCopy["name"] = data["name"];
        graphData.push(traceCopy)
    }
    return graphData
}

// data = {"labels" : [] , "values" : [] , "hole" : 0} 
function piechart(data) {

    if (data["values"].length != data["labels"].length) {
        console.log("Number of values != labels");
        return false;
    }

    var graphData = [{
        values: data["values"],
        labels: data["labels"],
        hole: (data["hole"] ? data["hole"] : 0),
        type: 'pie'
    }];

    return graphData;
}

// data = { "value" : , "min" :  , "max" : , "suffix" : "%" , "color": ""  }
function gaugeGraph(data) {
    var graphData = [{
        value: data["value"],
        type: "indicator",
        mode: "gauge+number",
        delta: { reference: data["value"] },
        number: { suffix: (data["suffix"] ? data["suffix"] : "%") },
        gauge: {
            visible: false,
            axis: { range: [Math.floor(data["min"]), Math.ceil(data["max"])] },
            borderwidth: 0.2,
            bar: { color: (data["color"] ? data["color"] : randomColor()) },
        }
    }];
    return graphData;
}