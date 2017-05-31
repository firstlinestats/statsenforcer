//trying to create a catch all bubble graph
//data should be an array with each entry having an x, y, featureId, and displayName properties
function bubbleCompare(divId, containerId, xLabel, yLabel, data) {
    $(divId).html("");

    var margin = {
        top: 20,
        right: 40,
        bottom: 30,
        left: 60
    };

    var width = $(containerId).width() - margin.left - margin.right;
    var height = 500;

    var minX = d3.min(data, function(d) {
        return d.x;
    });

    var maxX = d3.max(data, function(d) {
        return d.x;
    });

    var minY = d3.min(data, function(d) {
        return d.y;
    });
    var maxY = d3.max(data, function(d) {
        return d.y;
    });

    var minRadius = d3.min(data, function(d) {
        return d.size;
    });
    var maxRadius = d3.max(data, function(d) {
        return d.size;
    });

    var meanX = d3.mean(data, function(d) {
        return d.x;
    });
    var meanY = d3.mean(data, function(d) {
        return d.y;
    });

    //Setting up x
    var xScale = d3.scale.linear().range([0, width]);
    var xMap = function(d) {
        return xScale(d.x);
    };
    if (xLabel === 'Season') {
        xScale.domain([minX - 1000, maxX])
        var seasons = data.map(function(d) {
            return parseInt(d.season);
        })
        var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .tickValues(seasons)
            .tickFormat(function(d) {
                return formatAxisText(d, xLabel);
            });
    } else if (xLabel === 'Average Time On Ice') {
        xScale.domain([minX, maxX])
        var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .ticks(0);
    } else {
        xScale.domain([minX - (meanX * .05), maxX + (meanX * .05)])
        var xAxis = d3.svg.axis().scale(xScale).orient("bottom").tickFormat(function(d) {
            return formatAxisText(d, xLabel);
        });;
    };



    //Setting up y
    var yScale = d3.scale.linear().range([height, 0]).domain([minY - (meanY * .05), maxY]);
    var yMap = function(d) {
        return yScale(d.y);
    };
    var yAxis = d3.svg.axis().scale(yScale).orient("left").tickFormat(function(d) {
        return formatAxisText(d, yLabel);
    });;




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
        .attr("cx", xMap)
        .attr("cy", yMap)
        .attr("r", 10)
        .attr("id", function(d) {
            return "circle-" + d["featureId"] + d["season"];
        })
        .style("fill", function(d) {
            return d.fillColor;
        })
        .style("stroke", function(d) {
            return d.strokeColor;
        })
        .on('click', circleClicked)
        .on("mouseover", function(d) {
            var html = d.displayName + "<br /><b>" + xLabel + ":</b>" + d.x + "<br /><b>" + yLabel + ": </b>" + d.y + "<br /><b>" + "Season" + ": </b>" + d.season;
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
            return "name-" + d["featureId"] + d["season"];
        })
        .attr("x", function(d) {
            return xScale(d.x);
        })
        .attr("y", function(d) {
            return yScale(d.y) - 15;
        })
        .attr("font-family", "sans-serif")
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("visibility", "hidden")
        .attr("active", false)
        .style("text-anchor", "middle");

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
        var name = svg.select("#name-" + d["playerId"] + d["season"]);
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
