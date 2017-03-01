function create_corsi_events(alldata, divid, teamname, situations) {
  var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = (900 - margin.left) / 2 - margin.left - margin.right,
    height = width;

  $(divid).width(($("#gameTabContent").width()) / 2).height(($("#gameTabContent").width()) / 2);
  if ($(divid).width() < 768 / 2) {
    width = (900 - margin.left) - margin.left - margin.right;
    height = width;
    $(divid).width($("#gameTabContent").width()).height($("#gameTabContent").width());
  }
  var data = [];
  var existing = {};
  for (key in alldata) {
    var cf = alldata[key]["cf"];
    var ca = alldata[key]["ca"];
    var name = alldata[key].name;
    var sf = alldata[key].sf;
    var sa = alldata[key].sa;
    var toi = alldata[key].toi;
    var dupe = false;
    var newindex = data.length;
    if (cf in existing) {
      if (ca in existing[cf]) {
        dupe = true;
      } else {
        existing[cf][ca] = newindex;
      }
    } else {
      existing[cf] = {};
      existing[cf][ca] = newindex;
    }
    if (dupe == true) {
      var prev = data[existing[cf][ca]];
      prev.sf += ", " + alldata[key]["sf"];
      prev.sa += ", " + alldata[key]["sa"];
      prev.toi += ", " + alldata[key]["toi"];
      prev.name += ", " + alldata[key]["name"];
    } else {
      var prev = {};
      prev.cf = alldata[key]["cf"];
      prev.ca = alldata[key]["ca"];
      prev.sf = alldata[key]["sf"];
      prev.sa = alldata[key]["sa"];
      prev.toi = alldata[key]["toi"];
      prev.name = alldata[key]["name"];
      data.push(prev);
    }
  }

  /*
   * value accessor - returns the value to encode for a given data object.
   * scale - maps value to a visual display encoding, such as a pixel position.
   * map function - maps from data value to display value
   * axis - sets up axis
   */
  // setup x
  var xValue = function(d) { return d.cf + d.ca;}, // data -> value
      xScale = d3.scale.linear().range([0, width]), // value -> display
      xMap = function(d) { return xScale(xValue(d));}, // data -> display
      xAxis = d3.svg.axis().scale(xScale).orient("bottom");
  // setup y
  var yValue = function(d) { return d.cf - d.ca;}, // data -> value
      yScale = d3.scale.linear().range([height, 0]), // value -> display
      yMap = function(d) { return yScale(yValue(d));}, // data -> display
      yAxis = d3.svg.axis().scale(yScale).orient("left");
  // setup fill color
  var cValue = function(d) { return "black";},
      color = d3.scale.category10();
  // add the tooltip area to the webpage
  for (var i=0; i<data.length; i++) {
    d3.select("body")
        .append("div")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden")
        .style("border-radius", 3)
        .attr("active", false)
        .attr("class", "tooltip-inner")
        .attr("id", teamname + "-" + data[i].cf + "-" + data[i].ca + "-tooltip")
        .text("a simple tooltip");
  }

  // add the graph canvas to the body of the webpage
  var svg = d3.select(divid).append("svg")
      .attr("width", $(divid).width())
      .attr("height", $(divid).width())
      .attr("viewBox", "0 0 " + (width + margin.left + margin.right) + " " + (height + margin.top + margin.bottom))
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  // don't want dots overlapping axis, so add in buffer to data domain
  xScale.domain([d3.min([0, d3.min(data, xValue)-1]), d3.max(data, xValue)+1]);
  yScale.domain([-d3.max(data, function(d) { return Math.abs(d.cf - d.ca) + 1; }), d3.max(data,  function(d) { return Math.abs(d.cf - d.ca); }) + 1]);
  svg.append("rect")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .attr("transform", "translate(-" + margin.left + ",-" + margin.top + ")")
      .attr("fill", "white");

   svg.selectAll(".axis path")
      .style({"fill": 'none', 'stroke-width' : '1px', 'stroke' : 'Black'})

    // Draw Lines
    svg.append("line")          // attach a line
        .style("stroke", "red")  // colour the line
        .attr("x1", xScale(d3.min([0, d3.min(data, xValue)-1])))     // x position of the first end of the line
        .attr("y1", yScale(0))      // y position of the first end of the line
        .attr("x2", xScale(d3.max(data, xValue)+1))     // x position of the second end of the line
        .attr("y2", yScale(0));    // y position of the second end of the line
    var guideLines = [0.5, 1, 2, 4];
    for (var i = 0; i<guideLines.length; i++) {
        svg.append("line")          // attach a line
            .style("stroke", "grey")  // colour the line
            .attr("x1", xScale(d3.min([0, d3.min(data, xValue)-1])))     // x position of the first end of the line
            .attr("y1", yScale(0))      // y position of the first end of the line
            .attr("x2", xScale(guideLines[i] * d3.max(data, function(d) { return Math.abs(d.cf - d.ca) + 1; })))     // x position of the second end of the line
            .attr("y2", yScale(-d3.max(data, function(d) { return Math.abs(d.cf - d.ca) + 1; })));    // y position of the second end of the line
        svg.append("line")          // attach a line
            .style("stroke", "grey")  // colour the line
            .attr("x1", xScale(d3.min([0, d3.min(data, xValue)-1])))     // x position of the first end of the line
            .attr("y1", yScale(0))      // y position of the first end of the line
            .attr("x2", xScale(guideLines[i] * d3.max(data, function(d) { return Math.abs(d.cf - d.ca) + 1; })))     // x position of the second end of the line
            .attr("y2", yScale(d3.max(data, function(d) { return Math.abs(d.cf - d.ca) + 1; })));    // y position of the second end of the line
    }

  svg.append("g")
    .append("text")
      .attr("class", "label")
      .attr("x", width / 2)
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "middle")
      .attr("font-size", "10px")
      .text(situations);
  function format_toi(t) {
    var minutes = Math.floor(t / 60);
    var seconds = t - minutes * 60;
    return minutes + ":" + seconds
  }
    svg.append("text")
        .attr("x", margin.left + 50)
        .attr("y", height - margin.bottom)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("fill", "black")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-weight", "bold")
        .text("waronice.com")
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("font-weight", "bold")
        .style("font-size", "10px")
        .style("fill", "black")
        .style("text-transform", "uppercase")
        .style("font-weight", "bold")
        .text(teamname + " On-Ice Shot Attempts For/Against");

    // x-axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
      .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .style("font-size", "5px")
        .style("fill", "black")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-size", "10px")
        .style("font-weight", "bold")
        .text("Corsi For Plus Corsi Against");
    // y-axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .style("font-size", "5px")
        .style("fill", "black")
        .style("border-radius", "10px")
        .style("text-transform", "uppercase")
        .style("font-size", "10px")
        .style("font-weight", "bold")
        .text("Corsi For Minus Corsi Against");

    svg.selectAll(".tick text").style("font-size", "8px").style("font-weight", "bold");

    svg.selectAll('.domain')
      .style("fill", "none")
      .style("stroke", "#000")
      .style("shape-rendering", "crispEdges")

    svg.selectAll('.tick').select('line')
      .style("fill", "none")
      .style("stroke", "#000")
      .style("shape-rendering", "crispEdges")

    // draw dots
    svg.selectAll(".dot")
        .data(data)
      .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 5)
        .attr("cx", xMap)
        .attr("cy", yMap)
        .style("fill", function(d) { return get_color(teamname, true); })
        .style("stroke", function(d) { return get_color(teamname, false); })
        .on("click", mouseover);

    for (d in data) {
      mouseover(data[d]);
    }

    function mouseover(p) {
        var nameid = p.name;
        var names = nameid.split(", ");
        for (i=0; i<nameid.length; i++) {
          nameid = nameid.replace(" ", "-").replace(",", "")
        }
        var existing = d3.select("#name-0-" + p.cf + "-" + p.ca);
        if (existing[0][0] == null) {
          for (name in names) {
            svg.append("text")
              .attr("id", "name-" + name + "-" + p.cf + "-" + p.ca)
              .attr("x", xMap(p))
              .attr("y", yMap(p) - 5)
              .attr("dy", "-" + name + "em")
              .attr("text-anchor", "middle")
              .attr("font-size", "6px")
              .html(names[name]);
          }
        } else {
          for (name in names) {
            svg.select("#name-" + name + "-" + p.cf + "-" + p.ca).remove()
          }
        }
    }
    function mouseoverName(p) {
        var tooltip = d3.select("#" + teamname + "-" + p.cf + "-" + p.ca + "-tooltip");
        var active = tooltip.attr("active"),
          newOpacity = active ? 0 : 1;
        tooltip.html(p["name"] + "<br />SF:" + p.cf + "<br />SA:" + p.ca + "<br />TOI:" + p.toi);
        tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
        console.log(active)
        if (active == "false") {
          tooltip.style("visibility", "visible")
          tooltip.attr("active", "true")
          svg.append("text")
            .attr("id", "#" + teamname + "-" + p.cf + "-" + p.ca + "-name")
            .attr("x", xMap(p))
            .attr("y", yMap(p) - 5)
            .attr("text-anchor", "middle")
            .style("font-size", "16px")
            .on("click", mouseoverName)
            .text(p.name);
        } else {
          $("#" + teamname + "-" + p.cf + "-" + p.ca + "-name").remove();
          tooltip.style("visibility", "hidden")
          tooltip.attr("active", "false")
        }
    }
    function mouseout() {
        d3.selectAll("text").classed("active", false);
        tooltip.style("visibility", "hidden");
    }
}
