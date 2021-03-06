function shotChart(data, homeabbr, awayabbr, situations, formstate) {
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
        width = 900 - margin.left - margin.right,
        height = width * 0.425 + margin.left;

    $("#shotChart").width($("#gameTabContent").width()).height(Math.round($("#gameTabContent").width() * 0.425));
    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    x.domain([-100, 100]);
    y.domain([-42.5, 42.5]);

    var color = d3.scale.category10();

    var line = d3.svg.line()
        .interpolate("basis")
        .x(function(d) { return x(d.x); })
        .y(function(d) { return y(d.y); });

    // add the tooltip area to the webpage
    var tooltip = d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden")
        .style("border-radius", 3)
        .attr("class", "tooltip-inner")
        .text("a simple tooltip");

    var svg = d3.select("#shotChart").append("svg")
        .attr("width", $("#shotChart").width())
        .attr("height", $("#shotChart").height())
        .attr("viewBox", "0 0 " + width + " " + height)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    svg.append("rect")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", "translate(-" + margin.left + ",-" + margin.top + ")")
        .attr("fill", "white");

    svg.append("svg:image")
        .attr("xlink:href", "/rink/")
        .attr("width", width - margin.left)
        .attr("height", height - margin.top);

    // Add team logos
    svg.append("svg:image")
        .attr("xlink:href", "/team/" + homeabbr + ".png")
        .attr("width", (width / 3) - margin.left)
        .attr("height", (height / 3) - margin.top)
        .attr("opacity", 0.6)
        .attr("transform", "translate(" + (width - margin.left - width / 2.75) + "," + ((height - margin.top) / 3) + ")");
    svg.append("svg:image")
        .attr("xlink:href", "/team/" + awayabbr + ".png")
        .attr("width", (width / 3) - margin.left)
        .attr("height", (height / 3) - margin.top)
        .attr("opacity", 0.6)
        .attr("transform", "translate(" + (width / 20) + "," + ((height - margin.top) / 3) + ")");

    var dangerZoneHome = [{x: 89, y: -9},
        {x: 69, y: -22}, {x: 54, y: -22},
        {x: 54, y: -9}, {x: 44, y: -9},
        {x: 44, y: 9}, {x: 54, y: 9},
        {x: 54, y: 22}, {x: 69, y: 22},
        {x: 89, y: 9}, {x: 89, y: -9}];

    var highDangerZoneHome = [{x: 89, y: -9},
        {x: 69, y: -9}, {x: 69, y: 9},
        {x: 89, y: 9}, {x: 89, y: -9}];

    var dangerZone = [dangerZoneHome];
    dangerZone.push(highDangerZoneHome);
    var dangerZoneAway = [];
    for (var points in dangerZoneHome) {
        var p = dangerZoneHome[points];
        dangerZoneAway.push({x: -p.x, y: p.y});
    }
    var highDangerZoneAway = [];
    for (var points in highDangerZoneHome) {
        var p = highDangerZoneHome[points];
        highDangerZoneAway.push({x: -p.x, y: p.y});
    }
    dangerZone.push(dangerZoneAway);
    dangerZone.push(highDangerZoneAway);


    svg.selectAll("polygon")
        .data(dangerZone)
      .enter().append("polygon")
        .attr("points",function(d) {
            return d.map(function(d) {
                return [x(d.x), y(d.y)].join(",");
            }).join(" ");
        })
        .attr("stroke","black")
        .attr("fill", "none")
        .attr("stroke-width", 2)
        .attr("opacity", 0.1);

    svg.selectAll(".dot")
        .data(data["home"].concat(data["away"]))
      .enter().append("circle")
        .attr("class", "dot")
        .attr("r", function(d) {
            if (d.danger == "MEDIUM")
                return 6;
            else if (d.danger == "HIGH")
                return 8;
            else
                return 4;
        })
        .attr("cx", function(d) { return x(d.x); })
        .attr("cy", function(d) { return y(d.y); })
        .style("fill", function(d) {
            if (d.type == "GOAL") {
                return "#FF0000";
            } else if (d.type == "BLOCKED_SHOT") {
                return "#898989";
            } else if (d.type == "MISSED_SHOT") {
                return "#FFFFFF";
            } else {
                return "#000000";
            }
        })
        .style("stroke", function(d) {
            if (d.x > 0)
                return get_color(homeabbr, true);
            else
                return get_color(awayabbr, true);
        })
        .style("stroke-width", "2px")
        .on("mouseover", function(d) {
            var shotType = "Unknown";
            if (d.type == "MISSED_SHOT")
                shotType = "Missed Shot";
            else if (d.type == "BLOCKED_SHOT")
                shotType = "Blocked Shot";
            else if (d.type == "GOAL")
                shotType = "Goal";
            else if (d.type == "SHOT")
                shotType = "Shot";
            var html = d.description + "<br /><b>Shot Type:</b>" + shotType + "<br /><b>Period: </b>" + d.period + " | " + d.time + "<br />" + d.danger;
            tooltip.html(html);
            tooltip.style("visibility", "visible");
        })
        .on("mousemove", function(d){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
        .on("mouseout", function(d) {
            d3.selectAll("text").classed("active", false);
            tooltip.style("visibility", "hidden");
        });

    svg.append("g")
      .append("text")
        .attr("class", "label")
        .attr("x", width / 2)
        .attr("y", height - 12)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .text(formstate);

    createLegend();

    function createLegend() {
        var legendRectSize = 9;
        var legendSpacing = 4;

        var data = [{name: "Shot on Goal", color: "#000000"},
            {"name": "Missed Shot", color: "#FFFFFF"},
            {"name": "Blocked Shot", color: "#898989"},
            {"name": "Goal", "color": "#FF0000"}]
        svg.append('rect')
            .attr('x', width / 2 - (legendRectSize * 4))
            .attr('y', margin.top + legendRectSize)
            .attr('width', legendRectSize * 12)
            .attr('height', legendRectSize * 7)
            .style('fill', 'white')
            .style('stroke', 'black')
        var legend = svg.selectAll('.legend')
            .data(data)
          .enter()
            .append('g')
            .attr('class', 'legend')
            .attr('transform', function(d, i) {
                var height = legendRectSize + legendSpacing;
                var offset =  height;
                var horz = -2 * legendRectSize;
                var vert = i * height + offset;
                return 'translate(' + horz + ',' + vert + ')';
            });
        legend.append('circle')
            .attr("class", "dot")
            .attr('cx', width / 2 - legendRectSize * 1)
            .attr('cy', legendRectSize)
            .attr('r', legendRectSize / 2)
            .style('fill', function(d) { return d.color; })
            .style('stroke', color)
            .style('opacity', function(d) { return d.opacity; })
            .style("stroke", function(d) { return "black";});
        legend.append('text')
            .attr('x', width / 2)
            .attr('y', legendRectSize + 5)
            .style("text-anchor", "start")
            .style("text-size", "8px")
            .text(function(d) { return d.name; });
    }

}
