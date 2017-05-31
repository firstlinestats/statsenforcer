function create_shot_attempts(data, divid, valtype, formstate) {
    var hometeam = data["homeName"],
        awayteam = data["awayName"];
    // add the graph canvas to the body of the webpage
    var margin = {top: 20, right: 50, bottom: 20, left: 40},
        width = 900 - margin.left - margin.right,
        height = width * 0.425 + margin.left;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    $(divid).width(($("#gameTabContent").width())).height(Math.round($("#gameTabContent").width() * 0.425));
    // setup x
    var xValue = function(d) { return d[0]; }, // data -> value
        xScale = d3.scale.linear().range([0, width]), // value -> display
        xMap = function(d) { return xScale(xValue(d)); }, // data -> display
        xAxis = d3.svg.axis().scale(xScale).tickValues([20*60, 40*60, 60*60]).tickFormat(function(d) { return d/60; }).orient("bottom");
    // setup y
    var yValue = function(d) { return d[1]; }, // data -> value
        yScale = d3.scale.linear().range([height, 0]), // value -> display
        yMap = function(d) { return yScale(yValue(d)); }, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");
    // setup fill color
    var cValue = function(d) { return "black";},
        color = d3.scale.category10();
    // add the tooltip area to the webpage
    var tooltip = d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden")
        .style("border-radius", 3)
        .attr("class", "tooltip-inner")
        .text("a simple tooltip");

    var svg = d3.select(divid).append("svg")
      .attr("width", $(divid).width())
      .attr("height", $(divid).height())
      .attr("viewBox", "0 0 " + (width + margin.left + margin.right) + " " + (height + margin.top + margin.bottom))
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    svg.append("rect")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", "translate(-" + margin.left + ",-" + margin.top + ")")
        .attr("fill", "white");
    var homeMax = d3.max(data["home" + valtype], yValue) + 1;
    var awayMax = d3.max(data["away" + valtype], yValue) + 1;
    var yScaleMax = Math.max(homeMax, awayMax);
    var xSecondsMax = d3.max(data["home" + valtype], xValue);
    var secondsMax = 0;
    if (xSecondsMax < 60*20) {
        secondsMax = 60*20;
    } else if (xSecondsMax < 60*40) {
        secondsMax = 60*40;
    } else if (xSecondsMax < 60*60) {
        secondsMax = 60*60;
    } else {
        secondsMax = xSecondsMax + 5;
    }

    xScale.domain([0, secondsMax]);
    yScale.domain([0, yScaleMax]);

    function format_toi(t) {
        var minutes = Math.floor(t / 60);
        var seconds = t - minutes * 60;
        return minutes + ":" + seconds
    }
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text(header);
    var line = d3.svg.line()
        .interpolate("step-after")
        .x(xMap)
        .y(yMap);
    createPeriods(svg, data["periodEnds"]);
    svg.append("path")
        .datum(data["home" + valtype])
        .attr('stroke', get_color(hometeam, true))
        .attr('stroke-width', 2)
        .attr('fill', "none")
        .attr("d", line);

    svg.append("path")
        .datum(data["away" + valtype])
        .attr('stroke', get_color(awayteam, true))
        .attr('stroke-width', 2)
        .attr('fill', "none")
        .attr("d", line);

    createPP(svg, data["awayPenalties"], hometeam);
    createPP(svg, data["homePenalties"], awayteam);

    createGoals(svg, data["homeGoals"], hometeam);
    createGoals(svg, data["awayGoals"], awayteam);
    svg.append("rect")
        .attr("x", 115)
        .attr("y", 4)
        .attr("width", 105)
        .attr("height", 20)
        .style("fill", "white")
        .style("stroke", "none")
    svg.append("text")
        .attr("x", margin.left + 75)
        .attr("y", margin.top)
        .attr("text-anchor", "left")
        .style("font-size", "10px")
        .style("fill", "black")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-size", "10px")
        .style("font-weight", "bold")
        .text("firstlinestats.com")

    svg.append("g")
      .append("text")
        .attr("class", "label")
        .attr("x", width / 2)
        .attr("y", height - 12)
        .attr("dy", ".71em")
        .style("text-anchor", "middle")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-size", "10px")
        .text(formstate);
    createLegend(hometeam, awayteam);

    // x-axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
      .append("text")
        .attr("class", "label")
        .attr("x", width - margin.right)
        .attr("y", -6)
        .style("text-anchor", "end")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-size", "10px")
        .text("Time");
    // y-axis
    if (valtype == "Shots")
        var header = "Shot Attempts By Team";
    else
        var header = "Scoring Chances By Team";
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(header);

    svg.selectAll(".axis path")
      .style({"fill": 'none', 'stroke-width' : '1px', 'stroke' : 'Black'})

    function mouseover(p) {
        //tooltip.html(p["full_name"] + "<br />SF:" + p.SF + "<br />SA:" + p.SA + "<br />TOI:" + format_toi(p.TOI));
        tooltip.style("visibility", "visible")
    }
    function mouseout() {
        d3.selectAll("text").classed("active", false);
        tooltip.style("visibility", "hidden");
    }
    function createPP(svg, data, teamname) {
        for (var i=0; i<data.length; i++) {
            var penl = data[i];
            svg.append("rect")
                .attr("x", xMap(penl))
                .attr("y", 0)
                .attr("width", xScale(penl[1]))
                .attr("height", height)
                .attr("fill", get_color(teamname, true))
                .attr("stroke", "none")
                .attr("opacity", 0.5)
        }
    }
    function createPeriods(svg, periods) {
        for (var i=0; i<periods.length; i++) {
            var seconds = periods[i];
            svg.append("line")
                .attr("x1", xScale(seconds))
                .attr("y1", 0)
                .attr("x2", xScale(seconds))
                .attr("y2", height)
                .style("fill", "none")
                .style("stroke", "grey")
                .style("stroke-width", 2)
                .style("stroke-dasharray", ("3, 3"))
                .style("opacity", 1)
        }
    }
    function createGoals(svg, goals, teamname) {
        for (var i=0; i<goals.length; i++) {
            var seconds = goals[i];
            svg.append("line")
                .attr("x1", xScale(seconds))
                .attr("y1", 0)
                .attr("x2", xScale(seconds))
                .attr("y2", height)
                .style("fill", "none")
                .style("stroke", get_color(teamname, false))
                .style("stroke-width", 6)
                .style("opacity", 1);
            svg.append("line")
                .attr("x1", xScale(seconds))
                .attr("y1", 0)
                .attr("x2", xScale(seconds))
                .attr("y2", height)
                .style("fill", "none")
                .style("stroke", get_color(teamname, true))
                .style("stroke-width", 2)
                .style("opacity", 1);
        }
    }
    function createLegend(hometeam, awayteam) {
        var legendRectSize = 18;
        var legendSpacing = 4;
        var data = [];
        data.push({color: get_color(hometeam, true), title: hometeam + " PP", opacity: 0.5, teamname: hometeam},
            {color: get_color(awayteam, true), title: awayteam + " PP", opacity: 0.5, teamname: awayteam},
            {color: hexAverage(get_color(hometeam, true), get_color(awayteam, true)), title: "4v4", opacity: 0.75, teamname: hometeam},
            {color: get_color(hometeam, true), title: hometeam + " Goal", opacity: 1, teamname: hometeam},
            {color: get_color(awayteam, true), title: awayteam + " Goal", opacity: 1, teamname: awayteam})
        svg.append('rect')
            .attr('x', legendRectSize + margin.left + margin.right - legendRectSize - 10)
            .attr('y', margin.top + legendRectSize + 10)
            .attr('width', legendRectSize * 8)
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
        legend.append('rect')
            .attr('x', legendRectSize + margin.left + margin.right + 15)
            .attr('y', legendRectSize + margin.top)
            .attr('width', legendRectSize)
            .attr('height', legendRectSize)
            .style('fill', function(d) { return d.color; })
            .style('stroke', color)
            .style('opacity', function(d) { return d.opacity; })
            .style("stroke", function(d) { if (d.opacity == 0.5 || d.opacity == 0.75) return "none"; else return get_color(d.teamname);});
        legend.append('rect')
            .attr('x', legendRectSize + margin.left + margin.right + 15)
            .attr('y', legendRectSize + margin.top)
            .attr('width', legendRectSize)
            .attr('height', legendRectSize)
            .style('fill', "none")
            .style('stroke', color)
            .style("stroke", function(d) { if (d.opacity == 0.5 || d.opacity == 0.75) return "none"; else return get_color(d.teamname);});
        legend.append('text')
            .attr('x', legendRectSize * 2 + margin.left + margin.right + 20)
            .attr('y', legendRectSize + margin.top + legendRectSize / 1.5)
            .style("text-anchor", "start")
            .text(function(d) { return d.title; });
    }
    function padToTwo(numberString) {
        if (numberString.length < 2) {
            numberString = '0' + numberString;
        }
        return numberString;
    }

    function hexAverage() {
        var args = Array.prototype.slice.call(arguments);
        return args.reduce(function (previousValue, currentValue) {
            return currentValue
                .replace(/^#/, '')
                .match(/.{2}/g)
                .map(function (value, index) {
                    return previousValue[index] + parseInt(value, 16);
                });
        }, [0, 0, 0])
        .reduce(function (previousValue, currentValue) {
            return previousValue + padToTwo(Math.floor(currentValue / args.length).toString(16));
        }, '#');
    }
}
