import "./jquery.js";

let tabs = document.querySelectorAll('.tab-content');

document.querySelectorAll('nav li').forEach(e => e.addEventListener('click', function(e) {
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`#tab-${e.target.dataset.value}`).classList.add('active');
    document.querySelectorAll('nav li').forEach(link => {
        link.classList.remove('active');
    });
    e.target.classList.add('active');
}));

let button = document.querySelector("button");
button.addEventListener("click", function (e) {
    let circle_search = document.querySelector(".circle-loader.search");
    circle_search.classList.add("active");
    document.querySelector(".circle-loader-search-container").classList.add("active");
})
