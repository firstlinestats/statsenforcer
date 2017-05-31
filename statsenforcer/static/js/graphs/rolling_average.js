function rollingAverage(divId, containerId, value, data, raw_data, day_range, abbreviation, player_name) {
    $(divId).html("");
    var twidth = $(containerId).width(),
        theight = 650;
    var parseDate = d3.time.format("%Y-%m-%d").parse;

    for (d in data) {
        data[d].date = parseDate(data[d].dateString);
    }
    for (d in raw_data) {
        raw_data[d].date = parseDate(data[d].dateString);
    }

  var margin = {top: 20, right: 10, bottom: 10, left: 40},
      width = 1000 - margin.left - margin.right,
      height = 650 - margin.top - margin.bottom;
  twidth -= margin.left - margin.right;
  theight -= margin.top - margin.bottom;
  if (width < twidth)
      width = twidth - margin.left - margin.right;

  $(divId).width(twidth).height(theight);
  var x = d3.time.scale()
      .range([0, width - margin.right - margin.left]);

  var y = d3.scale.linear()
      .range([580, 0]);

  var color = d3.scale.category10();

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .tickFormat(d3.time.format("%b %d"))
      .ticks(5);

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(5);

  var line = d3.svg.line()
      .interpolate("basis")
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d[value]); });
  var aline = d3.svg.line()
      .interpolate("linear")
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d[value]); });

  // Define the div for the tooltip
  var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

  var svg = d3.select(divId).append("svg")
        .attr("width", twidth)
        .attr("height", theight)
        .attr("viewBox", "0 0 " + width + " " + height)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(-" + margin.left + ",-" + margin.top + ")")
        .attr("fill", "white");

  var minDate = maxDate = null;
  var minPoints = null;
  var maxPoints = null;
  for (d in raw_data) {
    if (minDate == null)
        minDate = raw_data[d]["date"];
    maxDate = raw_data[d]["date"];
    var point = parseFloat(raw_data[d][value]);
    if (maxPoints == null || point > maxPoints)
        maxPoints = point;
    if (minPoints == null || point < minPoints)
        minPoints = point;
  }

  x.domain([minDate, maxDate]);
  y.domain([minPoints - 2, maxPoints + 2]);

  // x-axis
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + 580 + ")")
      .attr("shape-rendering", "crispEdges")
      .style("fill", "none")
      .attr("stroke", "#000")
      .call(xAxis)
    .append("text")
      .attr("class", "label")
      .attr("x", width - margin.left - margin.right)
      .attr("y", -6)
      .style("fill", "black")
      .style("text-anchor", "end")
      .style("border-radius", "10px")
      .style("text-transform", "uppercase")
      .style("font-size", "10px")
      .style('stroke', 'none')
      .text("Date");

  // y-axis
  svg.append("g")
      .attr("class", "y axis")
      .style("fill", "none")
      .attr("shape-rendering", "crispEdges")
      .attr("stroke", "#000")
      .call(yAxis)
    .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("fill", "black")
      .style("text-anchor", "end")
      .style("border-radius", "10px")
      .style("text-transform", "uppercase")
      .style('stroke', 'none')
      .style("font-size", "10px")
      .text(value);

    svg.append("path")
        .datum(raw_data)
        .attr("class", "innerline")
        .attr("fill", "none")
        .attr("stroke-width", "3px")
        .attr("d", aline)
        .style("stroke", function(v) {
          return get_color(abbreviation, true);
        })
    // Add the scatterplot
    svg.selectAll("dot")
        .data(raw_data)
    .enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d[value]); })
        .style("fill", function(v) {
          return get_color(abbreviation, true);
        })
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div.html(d.dateString + "<br/>"  + parseFloat(d[value]).toFixed(1))
                .style("left", (d3.event.pageX - 50) + "px")
                .style("top", (d3.event.pageY - 50) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });
    svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke-width", "3px")
        .attr("d", line)
        .style("stroke", function(v) {
          return get_color(abbreviation, false);
        });
    // Add the scatterplot
    svg.selectAll("dot")
        .data(data)
    .enter().append("circle")
        .attr("r", 3)
        .attr("cx", function(d) { return x(d.date); })
        .attr("cy", function(d) { return y(d[value]); })
        .style("fill", function(v) {
          return get_color(abbreviation, false);
        })
        .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div .html(d.dateString + "<br/>"  + parseFloat(d[value]).toFixed(1))
                .style("left", (d3.event.pageX - 50) + "px")
                .style("top", (d3.event.pageY - 50) + "px");
            })
        .on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });


  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height - 80)
    .attr("text-anchor", "right")
    .style("font-size", "10px")
    .style("fill", "black")
    .style("border-radius", "10px")
    .style("text-transform", "uppercase")
    .style("font-weight", "bold")
    .text("firstlinestats.com");

  svg.append("text")
    .attr("x", (width / 2))
    .attr("y", 0 - (margin.top / 4))
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .style("fill", "black")
    .text(player_name + " " + day_range + " Day Rolling Average for " + value);

  d3.selectAll('g.tick text')
    .style('fill', "black")
    .style('stroke', 'none');
  d3.selectAll('g.tick')
    .style('fill', "black")
    .style('stroke', 'none');
};
