//trying to create a catch all bubble graph
//data should be an array with each entry having an x, y, featureId, and displayName properties
function bubbleCompare(divId, containerId, xLabel, yLabel, data) {
    $(divId).html("");

    var margin = {
            top: 20,
            right: 10,
            bottom: 30,
            left: 40
        },
        width = $(containerId).width() - margin.left - margin.right,
        height = 500;


    var minX = d3.min(data, function(d) {
            return d.x;
        }),
        maxX = d3.max(data, function(d) {
            return d.x;
        }),
        minY = d3.min(data, function(d) {
            return d.y;
        }),
        maxY = d3.max(data, function(d) {
            return d.y;
        }),
        minRadius = d3.min(data, function(d) {
            return d.size;
        }),
        maxRadius = d3.max(data, function(d) {
            return d.size;
        }),
        meanX = d3.mean(data, function(d) {
            return d.x;
        }),
        meanY = d3.mean(data, function(d) {
            return d.y;
        });

    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var xValue = function(d) {
        return d.x;
    }; // data -> value

    var xScale = d3.scale.linear().domain([minX - (meanX * .05), maxX + (meanX * .05)]).range([0, width]); // value -> display

    var xMap = function(d) {
        return xScale(xValue(d));
    }; // data -> display

    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    var yValue = function(d) {
        return d.y;
    }; // data -> value

    var yScale = d3.scale.linear().domain([minY - (meanY * .05), maxY]).range([height, 0]); // value -> display

    var yMap = function(d) {
        return yScale(yValue(d));
    }; // data -> display

    var yAxis = d3.svg.axis().scale(yScale).orient("left");



    x.domain([minX - Math.abs((meanX * .05)), maxX + Math.abs((meanX * .05))]);
    y.domain([minY - Math.abs((meanY * .05)), maxY]);

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
        .data(data)
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
            return "circle-" + d["featureId"];
        })
        .style("fill", function(d) {
            return d.fillColor;
        })
        .style("stroke", function(d) {
            return d.strokeColor;
        })
        .on('click', circleClicked)
        .on("mouseover", function(d) {
            var html = d.displayName + "<br /><b>" + xLabel + ":</b>" + d.x + "<br /><b>" + yLabel + ": </b>" + d.y;
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
        .data(data)
        .enter();

    texts.append("text")
        .html(function(d) {
            return d.displayName;
        })
        .attr("id", function(d) {
            return "name-" + d["featureId"];
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

    if (xLabel === 'Season') {
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickValues(season)
            .tickFormat(function(d) {
                return formatAxisText(d, xLabel);
            });
    } else {
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .ticks(10)
            .tickFormat(function(d) {
                return formatAxisText(d, xLabel);
            });
    };


    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10)
        .tickFormat(function(d) {
            return formatAxisText(d, yLabel);
        });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("x", width - 50)
        .attr("dy", "-.71em")
        .style("text-anchor", "end")
        .text(xLabel);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(yLabel);

    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .text(xLabel + " vs " + yLabel);

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
