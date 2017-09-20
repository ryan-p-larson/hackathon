function build_lookup() {
	var course_lookup = {};
	d3.json('data/indexed-courses.json', function(err, data) {
		if (err) console.log(err);

		d3.values(data).forEach((d) => {
			var courseID = d['courseID'];
			course_lookup[courseID] = d;
		});

	});
	return course_lookup;
}

function build_one_class(courseID, courses) {
	var nodes = [];
	var links = [];

	var course = courses[courseID];
	nodes.push(course);

	course['prereqs'].forEach((d) => {
		var prereqID = d['source'];
		var prereq = courses[prereqID];

		nodes.push(prereq);
		links.push(d);
	});
	return {"nodes": nodes, "links": links};
}
function draw_one_class(courseID, courses) {
	var course_graph = build_one_class(courseID, courses);
	draw_chart(course_graph);
}
function draw_classes(course_list, courses) {
	function merge_class_graphs(list_of_graphs) {
		var merged = list_of_graphs.reduceRight((a, b) => {

			var nodes = a['nodes'].concat(b['nodes']),
					links = a['links'].concat(b['links']);

			var nodes_uniq = Array.from(new Set(nodes)),
					links_uniq = Array.from(new Set(links));

			return {"nodes": nodes_uniq,
							"links": links_uniq
						};
		});
		return merged;
	}

	var course_graphs = course_list.map((d) => { return build_one_class(d, courses); });
	var final_graph = merge_class_graphs(course_graphs);

	console.log(final_graph);

	draw_chart(final_graph);
}

function draw_chart(graph) {

	if (graph['links'].length === 0) {
		console.log('No links, skipping');
		return;
	}

	// Set color scales
	var departments = Array.from(new Set(graph['nodes'].map((d) => { return d['department']; })));
	color_scale.domain(departments);

	// set course numbering scale (y)
	//y_scale.range = d3.range(graph['nodes'], (d) => { return d.course_num; });

	// clear chart
	svg.selectAll('.node').remove();
	svg.selectAll('.link').remove();
	svg.selectAll('text').remove();

	var link = svg.append("g")
	    .attr("class", "links")
	    .attr("fill", "none")
	    .attr("stroke", "#000")
	    .attr("stroke-opacity", 0.2)
	  .selectAll("path");
	var node = svg.append("g")
	    .attr("class", "nodes")
	    .attr("font-family", "sans-serif")
	    .attr("font-size", 10)
	  .selectAll("g");


	// sankey that ish
	sankey(graph);


	link = link
	    .data(graph.links)
	    .enter().append("path")
	      .attr("d", d3.sankeyLinkHorizontal())
	      .attr('class', 'link')
	      .attr("stroke-width", function(d) { return Math.max(1, d.width); });
	link.append("title")
	  .text(function(d) { return d.source.name + " → " + d.target.name; });

	node = node
	  .data(graph.nodes)
	  .enter().append("g")
		.filter(function(d) { return (d['targetLinks'].length > 0) || (d['sourceLinks'].length > 0); })
	  .attr('class', 'node');
	node.append("rect")
	  .attr('class', 'node')
	  .attr("x", function(d) { return d.x0; })
	  .attr("y", function(d) { return d.y0; })
	  .attr("height", function(d) { return d.y1 - d.y0; })
	  .attr("width", function(d) { return d.x1 - d.x0; })
	  .attr("fill", function(d) { return color_scale(d.department); })
	  .attr("stroke", "#000");
	node.append("text")
	  .attr("x", function(d) { return d.x0 - 6; })
	  .attr("y", function(d) { return (d.y1 + d.y0) / 2; })
	  .attr("dy", "0.35em")
	  .attr('class', '')
	  .attr("text-anchor", "end")
	  .text(function(d) { return d.name; })
	.filter(function(d) { return d.x0 < width / 2; })
	  .attr("x", function(d) { return d.x1 + 6; })
	  .attr("text-anchor", "start");
	node.append("title")
	  .text(function(d) { return d.name + '\n' + d.department; });
}

// interaction
function create_dropdown(courses) {
	var select_div = d3.select('#departmentSelect');

	var departments = d3.nest()
		.key((d)=>{ return d['department']; })
		.sortKeys((a, b) => { return d3.ascending(a, b); })
		.entries(d3.values(courses));


	var options = select_div.selectAll('option')
		.data(departments)
		.enter().append('option')
		.attr('value', (d)=> { return d.key; })
		.text((d)=> { return d.key + " (" + d.values.length +")"; });

	select_div.on("change", (d) => {
		var value = d3.select('#departmentSelect').node().value;
		draw_department(courses, value);
	});

	return;
}


// variables
var finance_l = [
	'MATH:1380',
	'RHET:1030',
	'CSI:1600',

	'ECON:1100',
	'ENGL:1200',
	'MSCI:1500',
	'STAT:1030',

	'ACCT:2100',
	'ECON:1200',
	'ECON:2800',

	'ACCT:2200',
	'BUS:3000',
	'MGMT:2000',
	'MSCI:3005',

	'ACCT:3020',
	'FIN:3000',
	'FIN:3020',
	'MGMT:2100',

	'FIN:3100',
	'FIN:3200',
	'FIN:3300',

	'MKTG:3000',

	'MSCI:3000'
];
var cs_l = [
	// CORE
	'CS:1210',
	'CS:2210',
	'CS:2230',
	'CS:2820',
	'CS:3330',
	'CS:3820',

	'CS:2630',
	'CS:3630',
	'CS:3640',

	'MATH:1850',
	'MATH:1860',
	'MATH:2700'
];
var journal_l = [
	'JMC:1100',
	'JMC:1200',
	'JMC:1600',
	'JMC:2300',
	'JMC:2010',
	'JMC:2020',
	'JMC:3180',
	'JMC:3300',
	'JMC:3470',
	'JMC:3490'
];
var indust_l = [
	'CHEM:1110',
	'ENGR:1100',
	'ENGR:1000',
	'MATH:1550',
	'RHET:1030',

	'ENGR:1300',
	'MATH:2550',
	'PHYS:1611',

	'IE:2000',
	'ENGR:2110',
	'ENGR:2120',
	'ENGR:2130',
	'MATH:2560',
	'PHYS:1612',
	'PSY:1001',

	'IE:2500',
	'IE:3500',
	'ENGR:2720',
	'STAT:2020',

	'IE:3000',
	'IE:3400',
	'IE:3610',
	'IE:3700',
	'ENGR:2760',

	'IE:3300',
	'IE:3450',
	'IE:3750',

	'IE:3350',
	'IE:3600'
];

function draw_department(courses, department) {
	var just_dep = d3.values(courses).filter((d) => {
		return d['department'] === department;
		})
		.map((d)=> { return d.courseID; });

	// change curriculum notice
	d3.select('#currentSelect').text(department);

	// draw the classes
	draw_classes(just_dep, courses);
	return;
}


// Chart
var margin = {top: 20, right: 20, bottom: 20, left: 20},
		width = 960 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var color_scale = d3.scaleOrdinal(d3.schemeCategory10);
var y_scale = d3.scaleLinear().range([height, 0]);

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var sankey = d3.sankey()
	.nodeId(function(d) { return d.courseID; })
	.nodeAlign(d3.sankeyCenter)
	.nodeWidth(15)
	.nodePadding(5)
	.size([width, height]);
