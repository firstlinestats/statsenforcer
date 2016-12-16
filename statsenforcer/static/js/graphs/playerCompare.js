function playerCompare(divId, containerId, xvalue, yvalue, data) {
    $(divId).html("");
    var axisText = {
        'g': "Goals",
        'a1': "Primary Assists",
        'a2': "Secondary Assists",
        'p': "Points",
        'cf': "Corsi For Total",
        'ca': "Corsi Against Total",
        'ff': "Fenwick For Total",
        'fa': "Fenwick Against Total",
        'gf': "On-Ice Goals For",
        'ga': "On-Ice Goals Against",
        'iscf': "Individual Scoring Chances For",
        'ihscf': "Individual High Danger Scoring Chances For",
        'scf': "Scoring Chances For",
        'hscf': "High Danger Scoring Chances For",
        'sca': "Scoring Chances Against",
        'hsca': "High Danger Scoring Chances Against",
        'fo_w': "Faceoffs Won",
        'fo_l': "Faceoffs Lost",
        'zso': "Offensive Zone Starts",
        'zsn': "Neutral Zone Starts",
        'zsd': "Defensive Zone Starts",
        'hitplus': "Hits",
        'hitminus': "Hits Taken",
        'pnplus': "Penalties",
        'pnminus': "Penalties Taken",
        'toi': "Time On Ice"
    };

    var xText = axisText[xvalue];
    var yText = axisText[yvalue];

    var margin = {
            top: 20,
            right: 40,
            bottom: 30,
            left: 50
        },
        width = $(containerId).width() - margin.left - margin.right,
        height = 500;

    var dataset = [];
    for (team in data) {
        var teamData = data[team];
        for (player in teamData) {
            teamData[player].playerId = player;
            if (xvalue !== "season") {
                teamData[player].x = parseFloat(teamData[player][xvalue]);
            } else {
                teamData[player].x = parseInt(teamData[player][xvalue]);
            };
            teamData[player].y = parseFloat(teamData[player][yvalue]);
            dataset.push(teamData[player]);
        };
    };


    var minX = d3.min(dataset, function(d) {
            return d.x;
        }),
        maxX = d3.max(dataset, function(d) {
            return d.x;
        }),
        minY = d3.min(dataset, function(d) {
            return d.y;
        }),
        maxY = d3.max(dataset, function(d) {
            return d.y;
        }),
        minRadius = d3.min(dataset, function(d) {
            return d.size;
        }),
        maxRadius = d3.max(dataset, function(d) {
            return d.size;
        }),
        meanX = d3.mean(dataset, function(d) {
            return d.x;
        }),
        meanY = d3.mean(dataset, function(d) {
            return d.y;
        });
    var x = d3.scale.linear()
        .range([0, width]);
    var y = d3.scale.linear()
        .range([height, 0]);

    var xValue = function(d) {
            return d.x;
        }, // data -> value
        xScale = d3.scale.linear().domain([minX - (meanX * .05), maxX + (meanX * .05)]).range([0, width]), // value -> display
        xMap = function(d) {
            return xScale(xValue(d));
        }, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    var yValue = function(d) {
            return d.y;
        }, // data -> value
        yScale = d3.scale.linear().domain([minY - (meanY * .05), maxY + (meanY * .05)]).range([height, 0]), // value -> display
        yMap = function(d) {
            return yScale(yValue(d));
        }, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");



    x.domain([minX - Math.abs((meanX * .05)), maxX +  Math.abs((meanX * .05))]);
    y.domain([minY - Math.abs((meanY * .05)), maxY +  Math.abs((meanY * .05))]);

    var maxallowed = 35,
        minallowed = 2;

    // add the tooltip area to the webpage
    var tooltip = d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden")
        .style("border-radius", 3)
        .attr("class", "tooltip-inner")
        .text("a simple tooltip");

    var svg = d3.select(divId)
        .insert("svg", "svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("rect")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", "translate(-" + margin.left + ",-" + margin.top + ")")
        .attr("fill", "white");

    svg.selectAll("circle")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("class", "circle")
        .attr("cx", function(d) {
            return x(d.x);
        })
        .attr("cy", function(d) {
            return y(d.y);
        })
        .attr("r", 10)
        .attr("id", function(d) {
            return "circle-" + d["playerId"] + '-' + d["team"];
        })
        .style("fill", function(d) {
            return get_color(d.team, true);
        })
        .style("stroke", function(d) {
            return get_color(d.team, false);
        })
        .on('click', circleClicked)
        .on("mouseover", function(d) {
            var html = d.name + "<br /><b>" + xvalue + ":</b>" + d[xvalue] + "<br /><b>" + yvalue + ": </b>" + d[yvalue];
            tooltip.html(html);
            tooltip.style("visibility", "visible");
        })
        .on("mousemove", function(d) {
            return tooltip.style("top", (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function(d) {
            d3.selectAll("text").classed("active", false);
            tooltip.style("visibility", "hidden");
        });

    var texts = svg.selectAll("text")
        .data(dataset)
        .enter();

    texts.append("text")
        .html(function(d) {
            return d["name"];
        })
        .attr("id", function(d) {
            return "name-" + d["playerId"];
        })
        .attr("x", function(d) {
            return xMap(d)
        })
        .attr("y", function(d) {
            return yMap(d) - 15
        })
        .attr("font-family", "sans-serif")
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("visibility", "hidden")
        .attr("active", false)
        .style("text-anchor", "middle");

    if (xvalue === 'season') {
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickValues(seasons)
            .tickFormat(function(d) {
                return formatAxisText(d, xText);
            });
    } else {
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .ticks(10)
            .tickFormat(function(d) {
                return formatAxisText(d, xText);
            });
    };


    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10)
        .tickFormat(function(d) {
            return formatAxisText(d, yText);
        });




    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("x", width - 50)
        .attr("dy", "-.71em")
        .style("text-anchor", "end")
        .text(xText);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(yText);

    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .text(xText + " vs " + yText);

    svg.append("text")
        .attr("x", margin.left)
        .attr("y", height - margin.bottom)
        .attr("text-anchor", "left")
        .style("font-size", "12px")
        .text("firstlinestats.com")

    function circleClicked(d) {
        var name = svg.select("#name-" + d["playerId"]);
        var active = name.attr("active");
        if (active === "false") {
            name.style("visibility", "visible");
            name.attr("active", "true");
        } else {
            name.style("visibility", "hidden");
            name.attr("active", "false");
        };
    };
};

function formatAxisText(d, text) {
    if (text.indexOf("Fraction") >= 0 || text.indexOf("Percentage") >= 0) {
        return d + "%";
    } else {
        return d;
    };
};
