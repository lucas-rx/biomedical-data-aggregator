import "./jquery.js";

function loading(){
    document.querySelector(".modal").style.display = "flex";
    let circle_drugbank = document.querySelector(".circle-loader.drugbank");
    circle_drugbank.classList.add("active");
    $.ajax({
        url: `/load_drugbank`,
        dataType: 'json',
        success: function(data) {
            console.log("Success");
            circle_drugbank.classList.add('load-complete');
            circle_drugbank.querySelector(".draw").classList.add('active');
        },
        complete: function() {
            console.log("Complete");

            let circle_omim = document.querySelector(".circle-loader.omim");
            circle_omim.classList.add("active");
            $.ajax({
                url: `/load_omim`,
                dataType: 'json',
                success: function(data) {
                    console.log("Success");
                    circle_omim.classList.add('load-complete');
                    circle_omim.querySelector(".draw").classList.add('active');
                },
                complete: function() {
                    console.log("Complete");

                    let circle_meddra = document.querySelector(".circle-loader.meddra");
                    circle_meddra.classList.add("active");
                    $.ajax({
                        url: `/load_meddra`,
                        dataType: 'json',
                        success: function(data) {
                            console.log("Success");
                            circle_meddra.classList.add('load-complete');
                            circle_meddra.querySelector(".draw").classList.add('active');
                        },
                        complete: function() {
                            console.log("Complete");

                            let circle_stitch = document.querySelector(".circle-loader.stitch");
                            circle_stitch.classList.add("active");
                            $.ajax({
                                url: `/load_stitch`,
                                dataType: 'json',
                                success: function(data) {
                                    console.log("Success");
                                    circle_stitch.classList.add('load-complete');
                                    circle_stitch.querySelector(".draw").classList.add('active');
                                },
                                complete: function() {
                                    console.log("Complete");

                                    let circle_atc = document.querySelector(".circle-loader.atc");
                                    circle_atc.classList.add("active");
                                    $.ajax({
                                        url: `/load_atc`,
                                        dataType: 'json',
                                        success: function(data) {
                                            console.log("Success");
                                            circle_atc.classList.add('load-complete');
                                            circle_atc.querySelector(".draw").classList.add('active');
                                        },
                                        complete: function() {
                                            console.log("Complete");

                                            let circle_hpo = document.querySelector(".circle-loader.hpo");
                                            circle_hpo.classList.add("active");
                                            $.ajax({
                                                url: `/load_hpo`,
                                                dataType: 'json',
                                                success: function(data) {
                                                    console.log("Success");
                                                    circle_hpo.classList.add('load-complete');
                                                    circle_hpo.querySelector(".draw").classList.add('active');
                                                },
                                                complete: function() {
                                                    console.log("Complete");

                                                    document.querySelector(".modal").style.opacity = "0";
                                                    document.querySelector(".modal").style.pointerEvents = "none";

                                                }
                                            });


                                        }
                                    });


                                }
                            });


                        }
                    });


                }
            });


        }
    });
}

loading()



