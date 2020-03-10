var Script = function () {


    var doughnutData = [
        {
            //value: 30,
			value: 13,
            color:"#F7464A",
			label:"Not Started"
        },
        {
            //value : 50,
			value : 28,
            //color : "#46BFBD"
			color : "#f8b760",
			label:"In Progress"
        },
        /*{
            value : 100,
            color : "#FDB45C"
        },
        {
            value : 40,
            color : "#949FB1"
        },*/
        {
            //value : 120,
			value : 57,
            //color : "#4D5360"
			color : "#0E9046",
			label:"Completed"
        }

    ];
	var doughnutData1 = [
       /* {
            value: 30,
            color:"#F7464A"
			color:"#610B0B"
        },
        {
            value : 50,
			color : "#949FB1"
            color : "#46BFBD"
			
        },
        {
            value : 100,
            color : "#FDB45C"
			color : "#9accef"
        },*/

        {
            value : 81,
            /*color : "#949FB1"*/
			label:"Open Items",
			color : "#F7464A"
        },
        {
            value : 155,
            /*color : "#4D5360"*/
			label: "Completed items",
			color : "#0E9046"
        }

    ];
		
    var lineChartData = {
        labels : ["","","","","","",""],
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : [65,59,90,81,56,55,40]
            },
            {
                fillColor : "rgba(151,187,205,0.5)",
                strokeColor : "rgba(151,187,205,1)",
                pointColor : "rgba(151,187,205,1)",
                pointStrokeColor : "#fff",
                data : [28,48,40,19,96,27,100]
            }
        ]

    };
    var pieData = [
        {
            value: 28,
			label:"Open Items",
            color:"#F38630"
        },
        
        {
            value : 72,
			label: "Completed Items",
            color : "#69D2E7"
        }

    ];
    var barChartData = {
        labels : ["CL","GL","AM","AR","CO","AP","SUSP","ISP","MM","PCA","BANK"],
        datasets : [
            {
                fillColor : "#0E9046",
                strokeColor : "#0E9046",
                data : [72,61,58,70,32,40,68,79,54,70,20]
            },
            {
                fillColor : "#f8b760",
                strokeColor : "#f8b760",
                data : [18,24,18,24,21,18,12,14,31,5,18]
            },
			{
                fillColor : "#F7464A",
                strokeColor : "#F7464A",
                data : [10,15,24,6,47,42,20,7,15,25,62]
            }
			
			
        ]

    };
	 
	 var barChartData1 = {
        labels : ["CL","GL","AM","AR","CO","AP","SUSP","ISP","MM","PCA","BANK"],
        datasets : [
            {
                fillColor : "#0E9046",
                strokeColor : "#0E9046",
				data : [21,18,11,16,21,16,6,8,6,11,21]
                
            },
            /*{ 
                fillColor : "#f8b760",
                strokeColor : "#f8b760",
                data : [18,24,18,24,21,18,12,14,31,5,18]
            },*/
			{
                fillColor : "#F7464A",
                strokeColor : "#F7464A",
                data : [16,11,9,4,8,7,3,3,4,4,14]
            }
			
			
        ]

    };
	 
	
    var chartData = [
        {
            value : Math.random(),
            color: "#D97041"
        },
        {
            value : Math.random(),
            color: "#C7604C"
        },
        {
            value : Math.random(),
            color: "#21323D"
        },
        {
            value : Math.random(),
            color: "#9D9B7F"
        },
        {
            value : Math.random(),
            color: "#7D4F6D"
        },
        {
            value : Math.random(),
            color: "#584A5E"
        }
    ];
    var radarChartData = {
        labels : ["","","","","","",""],
        datasets : [
            {
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : [65,59,90,81,56,55,40]
            },
            {
                fillColor : "rgba(151,187,205,0.5)",
                strokeColor : "rgba(151,187,205,1)",
                pointColor : "rgba(151,187,205,1)",
                pointStrokeColor : "#fff",
                data : [28,48,40,19,96,27,100]
            }
        ]

    };
	
		
    new Chart(document.getElementById("doughnut").getContext("2d")).Doughnut(doughnutData, {
                                        tooltipFillColor: "#9accef", 
					tooltipFontColor: "#FEF8F3",
					tooltipTitleFontStyle: "normal",
					tooltipFontSize: 9 ,
                                        tooltipTitleFontSize: 12,
                    





                                                     }  );
	new Chart(document.getElementById("doughnut1").getContext("2d")).Doughnut(doughnutData1, {
                                       tooltipFillColor: "#9accef", 
					tooltipFontColor: "#FEF8F3",
					tooltipTitleFontStyle: "normal",
					tooltipFontSize: 9 ,
                                        tooltipTitleFontSize: 12,
                                                   }  );
    /*new Chart(document.getElementById("line").getContext("2d")).Line(lineChartData);
    new Chart(document.getElementById("radar").getContext("2d")).Radar(radarChartData);
    new Chart(document.getElementById("polarArea").getContext("2d")).PolarArea(chartData);*/
    new Chart(document.getElementById("bar").getContext("2d")).StackedBar(barChartData,{
            scaleShowGridLines : false, scaleShowLabels:false,
            tooltipFillColor: "#9accef",
              tooltipFontColor: "#FEF8F3",
					tooltipTitleFontStyle: "normal",
					tooltipFontSize: 9 ,
                                        tooltipTitleFontSize: 12,
                     
                                  });
	 new Chart(document.getElementById("bar1").getContext("2d")).StackedBar(barChartData1,{scaleShowGridLines : false, scaleShowLabels:false,
                                       tooltipFillColor: "#9accef",


                                       tooltipFontColor: "#FEF8F3",
					tooltipTitleFontStyle: "normal",
					tooltipFontSize: 9 ,
                                        tooltipTitleFontSize: 12,





});
   /* new Chart(document.getElementById("pie").getContext("2d")).Pie(pieData);*/

				
			

}();