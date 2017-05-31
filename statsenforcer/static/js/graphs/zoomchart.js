

function zoomchart(divId, containerId, data, xCat, yCat, rCat, xText, yText, rText, tText, dataId) {
    $(divId).html("");
    var margin = { top: 50, right: 20, bottom: 30, left: 30 },
        outerWidth = $(containerId).width(),
        outerHeight = $(containerId).width() * 0.65,
        width = outerWidth - margin.left - margin.right,
        height = outerHeight - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]).nice();

    var y = d3.scale.linear()
        .range([height, 0]).nice();

    function compare(a, b) {
      if (a[rCat] < b[rCat])
        return 1;
      if (a[rCat] > b[rCat])
        return -1;
      return 0;
    }
    data.sort(compare);

    var xMax = d3.max(data, function(d) { return d[xCat]; }) * 1.05,
        xMin = d3.min(data, function(d) { return d[xCat]; }),
        xMin = xMin > 0 ? 0 : xMin,
        yMax = d3.max(data, function(d) { return d[yCat]; }) * 1.05,
        yMin = d3.min(data, function(d) { return d[yCat]; }),
        yMin = yMin > 0 ? 0 : yMin;

    x.domain([xMin, xMax]);
    y.domain([yMin, yMax]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .tickSize(-height);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickSize(-width);

    var color = d3.scale.category10();

    var tip = d3.tip()
        .attr("class", "d3-tip")
        .offset([-10, 0])
        .html(function(d) {
            return d.fullName + " (" + d.team + ")" + "<br />" + xCat + ": " + d[xCat] + "<br />" + yCat + ": " + d[yCat] + "<br />" + rCat + ": " + d[rCat];
        });

    var zoomBeh = d3.behavior.zoom()
        .x(x)
        .y(y)
        .scaleExtent([0, 500])
        .on("zoom", zoom);

    var svg = d3.select(divId)
        .append("svg")
          .attr("width", outerWidth)
          .attr("height", outerHeight)
          .attr("fill", "white")
        .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
          .call(zoomBeh);

    svg.call(tip);

    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("shape-rendering", "crispEdges");

    svg.append("g")
        .classed("x axis", true)
        .attr("transform", "translate(0," + height + ")")
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("shape-rendering", "crispEdges")
        .call(xAxis)
        .append("text")
          .classed("label", true)
          .attr("fill", "black")
          .attr("x", width)
          .attr("y", margin.bottom - 10)
          .style("text-anchor", "end")
          .style("fill", "black")
          .style("font-weight", "normal")
          .text(xText);

    svg.append("g")
        .classed("y axis", true)
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("shape-rendering", "crispEdges")
        .call(yAxis)
      .append("text")
        .classed("label", true)
        .attr("fill", "black")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .style("fill", "black")
        .style("font-weight", "normal")
        .text(yText);

    var objects = svg.append("svg")
        .classed("objects", true)
        .attr("width", width)
        .attr("height", height);

    objects.append("svg:line")
        .classed("axisLine hAxisLine", true)
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", width)
        .attr("y2", 0)
        .attr("fill", "none")
        .attr("stroke", "rgba(0, 0, 0, 0.1)")
        .attr("shape-rendering", "crispEdges")
        .attr("stroke-width", "2px")
        .attr("transform", "translate(0," + height + ")");

    objects.append("svg:line")
        .classed("axisLine vAxisLine", true)
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", 0)
        .attr("fill", "none")
        .attr("stroke", "rgba(0, 0, 0, 0.1)")
        .attr("shape-rendering", "crispEdges")
        .attr("stroke-width", "2px")
        .attr("y2", height);

    objects.selectAll(".dot")
        .data(data)
      .enter().append("circle")
        .classed("dot", true)
        .attr("r", function (d) { return 6 * Math.sqrt(d[rCat] / Math.PI); })
        .attr("transform", transform)
        .style("fill", function(d) { return get_color(d.team, false); })
        .style("stroke", function(d) { return get_color(d.team, true); })
        .style("stroke-width", "2px")
        .style("fill-opacity", .5)
        .on('click', circleClicked)
        .on("mouseover", tip.show)
        .on("mouseout", tip.hide);

    objects.selectAll("text")
        .data(data)
      .enter().append("text")
        .html(function(d) {
            return d["fullName"];
        })
        .attr("id", function(d) {
            return "name-" + d[dataId];
        })
        .attr("class", "text")
        .attr("transform", transformText)
        .attr("font-family", "sans-serif")
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .style("fill", "black")
        .style("visibility", "hidden")
        .attr("active", false)
        .style("text-anchor", "middle");

    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("fill", "black")
        .text(tText + " Comparisons, sized by " + rText)

    svg.append("text")
        .attr("x", margin.left)
        .attr("y", height - margin.bottom)
        .attr("text-anchor", "left")
        .style("font-size", "10px")
        .style("fill", "black")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-weight", "bold")
        .text("firstlinestats.com")

    d3.selectAll('g.tick text')
      .style('fill', "black");
    d3.selectAll('g.tick')
        .style('fill', "black");

    function zoom() {
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").call(yAxis);

        svg.selectAll(".dot")
            .attr("transform", transform);
        svg.selectAll(".text")
            .attr("transform", transformText);
        d3.selectAll('g.tick text')
            .style('fill', "black");
        d3.selectAll('g.tick')
            .style('fill', "black");
    }

    function transform(d) {
        return "translate(" + x(d[xCat]) + "," + y(d[yCat]) + ")";
    }

    function transformText(d) {
        return "translate(" + x(d[xCat]) + "," + (y(d[yCat]) - 6 * Math.sqrt(d[rCat] / Math.PI) - 5) + ")";
    }

    function circleClicked(d) {
        var name = svg.select("#name-" + d[dataId]);
        var active = name.attr("active");
        if (active === "false") {
            name.style("visibility", "visible");
            name.attr("active", "true");
        } else {
            name.style("visibility", "hidden");
            name.attr("active", "false");
        };
    };
}
