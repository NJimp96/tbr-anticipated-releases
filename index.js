$.getJSON("https://raw.githubusercontent.com/NJimp96/tbr-anticipated-releases/main/data/tbr_past_month.json")
.done(function( data ) {
    document.getElementById("shelf_month").innerHTML = data.map(bookCard).join("")
});

$.getJSON("https://raw.githubusercontent.com/NJimp96/tbr-anticipated-releases/main/data/tbr_coming_week.json")
.done(function( data ) {
    document.getElementById("shelf_week").innerHTML = data.map(bookCard).join("")
});


function bookCard(bookData){
    return `<a href=${bookData.Link} target="_blank">
                <div class="covercontainers">
                    <img src=${bookData.Cover} class="bookcovers">

                    <p class="dates">
                        ${bookData.Date}
                    </p>

                </div>
            </a>`
}
